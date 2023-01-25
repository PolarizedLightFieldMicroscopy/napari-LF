# major libraries
import numpy as np
import h5py
import os
import subprocess
import time
import tempfile
import socket
import argparse
import sys

# lflib imports
import lflib
from lflib.imageio import load_image, save_image
from lflib.lightfield import LightField
from lflib.calibration import LightFieldCalibration
from lflib.util import ensure_path
from lfdeconvolve import copy_file, retrieve_calibration_file
#----------------------------------------------------------------------------------

def do_project(args):

    filename = args.input_file
    projection_type = args.solver

    # Default calibration filename has a *.lfc suffix, and the same prefix
    if not args.calibration_file:
        fileName, fileExtension = os.path.splitext(filename)
        calibration_file = fileName + '.lfc'
    else:
        calibration_file = args.calibration_file

    # Default output filename has a -RECTIFIED suffix
    if not args.output_filename:
        fileName, fileExtension = os.path.splitext(filename)
        output_filename = fileName + '-STACK.tif'
    else:
        output_filename = args.output_filename

    print('\t--> hostname:{host}'.format(host=socket.gethostname()))
    print('\t--> specified gpu-id:{gpuid}'.format(gpuid=args.gpu_id))

    #check if output filename appears to be formatted as user@host:path.
    remote_output_fn = None
    if ':' in output_filename and '@' in output_filename:
        remote_output_fn = output_filename
        output_filename = tempfile.gettempdir() + os.sep + 'deconv_tmpout_' + str(hash(filename)) + os.path.splitext(output_filename)[1]
        print('\t--> output file location is on remote host. Output will temporarily appear at %s.'%output_filename)

    # Loadim the calibration data
    calibration_file = retrieve_calibration_file(calibration_file, id=str(args.gpu_id))
    lfcal = LightFieldCalibration.load(calibration_file)
    print('\t--> loaded calibration file.')

    # Load the raw input data
    if ':' in filename and '@' in filename:
        tmpname = tempfile.gettempdir() + os.sep + 'deconv_tmpin_' + str(hash(filename)) + os.path.splitext(filename)[1]
        print('\t--> input file is on remote host. Transferring temporarily to  %s.'%tmpname)
        copy_file(filename, tmpname)
        im = load_image(tmpname, dtype=np.float32, normalize=False)
        os.remove(tmpname)
    else:
        im = load_image(filename, dtype=np.float32, normalize = False)
    print('\t--> %s opened.  Pixel values range: [%d, %d]' % (filename, int(im.min()), int(im.max())))

    if projection_type=='proj_vol':
        # Perform dark frame subtraction
        from lflib.lfexceptions import ZeroImageException
        try:
            im = lfcal.subtract_dark_frame(im)
            print('\t    Dark frame subtracted.  Pixel values range: [%f, %f]' % (im.min(), im.max()))
            lf_zeros = False
        except ZeroImageException:
            print("\t    A frame with no light pixels was found, but it's no big deal")
            lf_zeros = True

        # Rectify the image
        lf = lfcal.rectify_lf(im)

    # Save a little bit of verboseness in the code below by extracting the appropriate 'db' object.
    if lfcal.psf_db is not None:
        print('\t    Using wave optic psf db.')
        db = lfcal.psf_db
    else:
        print('\t    Using rayspread db.')
        db = lfcal.rayspread_db

    # Initialize the volume as a plain focal stack.  We normalize by the weights as well.
    from lflib.volume import LightFieldProjection
    lfproj = LightFieldProjection(lfcal.rayspread_db, lfcal.psf_db,
                                  disable_gpu = args.disable_gpu, gpu_id = args.gpu_id, platform_id = args.platform_id, use_sing_prec=args.use_sing_prec)

    # Enable radiometry correction
    lfproj.set_premultiplier(lfcal.radiometric_correction)

    print('-------------------------------------------------------------------')
    print(f'{"Forward" if projection_type=="proj_lf" else "Backward"} projecting:', filename)

    from lflib.linear_operators import LightFieldOperator
    nrays = db.ns*db.nu*db.nt*db.nv
    nvoxels = db.nx*db.ny*db.nz
    A_lfop = LightFieldOperator(lfproj, db, args.use_sing_prec)
    A_operator = A_lfop.as_linear_operator(nrays, nvoxels)

    # What kind of projection to make?
    if projection_type=='proj_lf':
        if nvoxels != np.prod(im.shape):
            raise ValueError(f"Input volume doesn't have the expected size: Input: {im.shape}, expected: {db.ny},{db.nx},{db.nz}")
        elif im.shape[0] != db.ny: # Maybe this is a loaded volume with transposed coordinates
            im = np.transpose(im,(1,2,0))
        if im.shape[0] != db.ny:
            raise ValueError(f"Input volume doesn't have the expected size: Input: {im.shape}, expected: {db.ny},{db.nx},{db.nz}")
        
        print(f'Forward projecting [Vol ({db.ny},{db.nx},{db.nz})]  --->    [LF image ({db.nu*db.ns},{db.nv*db.nt})]')

        # Reshape volume to be a column
        x_vec = np.reshape(im, np.prod(im.shape))
        # Multiply with system matrix to get a lf 
        lf_vec = A_operator.matvec(x_vec) #np.random.rand(db.nu*db.ns, db.nv*db.nt)
        # Reshape 1D result into 2D
        output = np.reshape(lf_vec, (db.nu*db.ns, db.nv*db.nt))
        lf = LightField(output, db.nu, db.nv, db.ns, db.nt,
                          representation = LightField.TILED_SUBAPERTURE)
        output =  lf.asimage(representation = LightField.TILED_LENSLET)
        
    elif projection_type=='proj_vol':
        # Convert LF image to the correct format, as it comes as Subaperture images
        im_subaperture = lf.asimage(representation = LightField.TILED_SUBAPERTURE)
        print(f'Backward projecting [LF image ({im_subaperture.shape[0]},{im_subaperture.shape[1]})]    --->    [Vol  ({db.ny},{db.nx},{db.nz})]')
        # reshape to 1D row
        lf_vec = np.reshape(im_subaperture, np.prod(im_subaperture.shape))
        # Multiply by adjoint operator to get volume
        x_vec = A_operator.rmatvec(lf_vec)
        # Reshape into correct shape
        output = np.reshape(x_vec, (db.ny, db.nx, db.nz))
    else:
        raise ValueError("The projection type specified is not an option, " +
                         "available methods are: "
                         " Forward project a 3D volume ('proj_vol'), " +
                         " Backward project a 2D LF ('proj_lf')")


    # ================================= SAVE RESULTS ==================================

    # Create a new hdf5 file for the output
    if os.path.splitext(output_filename)[1].lower() == ".h5":
        f = h5py.File(output_filename,'w')
        f.create_dataset('timeseries_tensor', data=np.reshape(output, np.prod(output.shape), order='f'))
        output_shape = np.array(np.array(output.shape[::-1]))
        f.create_dataset('tensor_shape', data=output_shape)
        print('    Saving', f)
        f.close()

    # Or, if the file suffix is *.tif, then we save a tiff stack
    else:
        # Save volume/image
        save_image(output_filename, output)
        print(f'saved {output_filename}')

    # If necessary, transfer output file to remote host and delete local copy.
    if remote_output_fn:
        copy_file(output_filename, remote_output_fn)
        os.remove(output_filename)

#----------------------------------------------------------------------------------
#                                        MAIN
#----------------------------------------------------------------------------------
# if __name__ == "__main__":
def main(args=None):
    print('LFProject v%s' % (lflib.version))

    parser = argparse.ArgumentParser()
    parser.add_argument('input_filename_volume',
                        help="You must supply at least one volume "
                        "to project.")
    parser.add_argument('input_filename_lightfield',
                        help="You must supply at least one light field image "
                        "to project.")
    parser.add_argument("--output-filename-volume", dest="output_filename_volume",
                        help="Specify the output filename.")
    parser.add_argument("--output-filename-lightfield", dest="output_filename_lightfield",
                        help="Specify the output filename.")
    parser.add_argument("-c", "--calibration-file", dest="calibration_file",
                        help="Specify the calibration file to use for rectification.")
    key_def = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'enlightenment_c3')
    parser.add_argument("--private-key", dest="private_fn", type=str,
                        default=key_def,
                        help="Specify the private key file for remote transfers.")

    # Algorithm selection
    # Note: some solvers may not work
    parser.add_argument("--solver", dest="solver", default='proj_vol',
                      help= "Available projection types are: " +
                         " Forward project a 3D volume ('proj_vol'), " +
                         " Backward project a 2D LF ('proj_lf'), ")

    # Misc Options
    parser.add_argument("--use-single-precision",
                      action="store_true", dest="use_sing_prec", default=False,
                      help="Use single precision float instead of double.")
    parser.add_argument("--platform-id", dest="platform_id", type=int, default=0,
                      help="Force lfdeconvolve to use a specific OpenCL Platform on your system.")

    # Assorted other parameters
    parser.add_argument("--disable-gpu",
                      action="store_true", dest="disable_gpu", default=False,
                      help="Disable GPU deconvolution, and use software implementation instead.")

    # if --gpu-id is not supplied it will default to the value of the USE_GPU_ID environment
    # variable, if set, or 1 otherwise.
    parser.add_argument("--gpu-id", dest="gpu_id", type=int, default=int(os.environ.get('USE_GPU_ID', 0)),
                      help="Force lfdeconvolve to use a specific GPU on your system. If not supplied this will default to $USE_GPU_ID or 0")
   
    args = parser.parse_args(args)

    args.output_filename = None
    if args.solver=='proj_lf':
        args.output_filename = args.output_filename_lightfield
        args.input_file = args.input_filename_volume
    elif args.solver=='proj_vol':
        args.output_filename = args.output_filename_volume
        args.input_file = args.input_filename_lightfield
    if args.output_filename is not None:
        ensure_path(args.output_filename)

    # Run the deconvolution algorithm
    do_project(args)

if __name__ == "__main__":
    main()