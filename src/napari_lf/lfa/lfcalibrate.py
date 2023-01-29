# calibrate.py
#
# Usage: calibrate.py <calibration_dir>
#
# This script re-runs the calibration from a set of calibration images
# captured by the uScope GUI.  This script is mostly useful for
# debugging the calibration routines offline (i.e. away from the
# microscope), but can be used to update old calibration files from
# early experiments as well.
import sys
import os
import glob
import numpy as np
from lflib.imageio import load_image, save_image

from lflib.lfexceptions import (
    ParameterError,
    ParameterExistsError,
    ZeroImageException
    )

def avg_images(image_files):
    """
    Averages a set of images passed.
    Numerical error will become an issue with large number of files.
    """
    if len(image_files) == 0:
        return None
    im = load_image(image_files[0])
    im_type = im.dtype
    im = im.astype('float32')
    # numerical error will become a problem with large numbers of files
    for ifile in image_files[1:]:
        im = im + load_image(ifile, dtype='float32')
    return np.round(im/len(image_files)).astype(im_type)

def main(args=None, values=None):
    """Main calibration function that expects the user to provide parameters.
    """
    import lflib
    print(f'LFcalibrate v{lflib.version}')

    # Parse command line options
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output-filename", dest="output_filename",
            help="Specify the name of the calibration file.")
    parser.add_argument("--synthetic",
            action="store_true", dest="synthetic_lf", default=False,
            help="Use this option to create a synthetic light field (i.e. with no calibration image")

    parser.add_argument("--voxels-as-points",
            action="store_true", dest="voxels_as_points", default=False,
            help="Treat each voxel as an ideal point source.  This turns of numerical integration that gives the voxel spatial extent (which can be important for anti-aliasing.")

    # Calibration routine parameters
    parser.add_argument("--dark-frame", dest="dark_frame_file", default=None,
            help="Specify the a dark frame image to subtract from the input light-field before processing.  (This makes radiometric calibration more accurate.)")
    parser.add_argument("--radiometry-frame", dest="radiometry_frame_file", default=None,
            help="Specify the a radiometry frame to use for radiometric correction.  If no frame is specified, then no radiometric correction is carried out.")
    parser.add_argument("--align-radiometry", action="store_true", dest="align_radiometry", default=False,
            help="Align the radiometry image automatically to the geometric calibration image.  (use this option when the radiometry frame has been \"bumped\" before imaging begins.")

    # Optical parameters
    parser.add_argument("--pitch", dest="ulens_pitch", type=float, default=None,
            help="Specify the microlens pitch (in microns).")
    parser.add_argument("--pixel-size", dest="pixel_size", type=float, default=None,
            help="Specify the size of a pixel on the sensor, taking magnification due to relay optics into account (in microns).")
    parser.add_argument("--focal-length", dest="ulens_focal_length", type=float, default=2432.72,
            help="Specify the microlens focal length (in microns).")
    parser.add_argument("--ulens-focal-distance", dest="ulens_focal_distance", type=float, default=None,
            help="Specify the microlens focal distance (in microns).  If you do not specify a value, it is assumed that the focal distance is equal to the focal length.")
    parser.add_argument("--magnification", dest="objective_magnification", type=int, default=20,
            help="Specify the objective magnification.")
    parser.add_argument("--na", dest="objective_na", type=float, default = 0.5,
            help="Specify the objective numerical aperture.")
    parser.add_argument("--tubelens-focal-length", dest="tubelens_focal_length", type=float, default = 200.0,
            help="Tube lens focal length (in millimeters).")
    parser.add_argument("--wavelength", dest="center_wavelength", type=float, default = 509,
            help="Center wavelength of emission spectrum of the sample (nm).")
    parser.add_argument("--medium-index", dest="medium_index", type=float, default = 1.33,
            help="Set the index of refraction of the medium.")
    parser.add_argument("--ulens-fill-factor", dest="ulens_fill_factor", type=float, default=1.0,
            help="Specify the microlens fill factor (e.g. 1.0, 0.7, ...).")
    parser.add_argument("--pixel-fill-factor", dest="pixel_fill_factor", type=float, default=1.0,
            help="Specify the pixel fill factor (e.g. 1.0, 0.7, ...).")
    parser.add_argument("--ulens-profile", dest="ulens_profile", default='rect',
            help="Specify the shape of the microlens apertures.  Options include: ['rect', 'circ']")


    # Volume parameters
    parser.add_argument("--num-slices", dest="num_slices", type=int, default=30,
            help="Set the number of slices to produce in the output stacks.")
    parser.add_argument("--um-per-slice", dest="um_per_slice", type=float, default=10.0,
            help="Set the thickness of each slice (in um).")
    parser.add_argument("--z-center", dest="z_center", type=float, default=0.0,
            help="Set the offset for the central z slice (in um).")
    parser.add_argument("--supersample", dest="supersample", type=int, default= 1,
            help="Supersample the light field volume.  This results in a higher resolution reconstruction up to a point, and interpolation after that point.")

    # Geometric calibration Options
    parser.add_argument("--affine-alignment", action="store_true", dest="affine_alignment", default=False,
            help="Use affine warp for correcting geometric distortion (default is cubic).")
    parser.add_argument("--isometry-alignment", action="store_true", dest="isometry_alignment", default=False,
            help="Use isometry warp for correcting geometric distortion (default is cubic).")
    parser.add_argument("--chief-ray", action="store_true", dest="chief_ray_image", default=False,
            help="Use this flag to indicate that the calibration frame is a chief ray image.")

    # Synthetic parameters
    parser.add_argument("--ns", dest="ns", type=int, default=50,
            help="Set the lenslets in s direction.")
    parser.add_argument("--nt", dest="nt", type=int, default=50,
            help="Set the lenslets in t direction.")

    # Misc Options
    parser.add_argument("--use-single-precision",
            action="store_true", dest="use_sing_prec", default=False,
            help="Use single precision float instead of double.")
    parser.add_argument("--platform-id", dest="platform_id", type=int, default=0,
            help="Force lfcalibrate to use a specific OpenCL Platform on your system.")
    parser.add_argument("--gpu-id", dest="gpu_id", type=int, default=0,
            help="Force lfcalibrate to use a specific GPU on your system.")
    parser.add_argument("--disable-gpu",
                      action="store_true", dest="disable_gpu", default=False,
                      help="Disable GPU deconvolution, and use software implementation instead.")
    parser.add_argument("--comments", dest="comments", default="",
                      help="User comments.")

    # Other Options
    parser.add_argument("--crop-center-lenslets",
            action="store_true", dest="crop_center_lenslets", default=False,
            help="For severe aperture vignetting (high NA objectives), use only center lenslets for calibration, and extrapolate outwards.")
    parser.add_argument("--skip-alignment",
            action="store_true", dest="skip_alignment", default=False,
            help="Skip the alignment step during geometric calibration (useful if you are working with an already-rectified light field or a synthetic light field.")
    parser.add_argument("--skip-subpixel-alignment", action="store_true", dest="skip_subpixel_alignment", default=False,
            help="Skip subpixel alignment for determining lenslet centers.")
    parser.add_argument("--num-threads", dest="num_threads", type=int, default=10,
            help="Set the number of CPU threads to use when generating the raydb.")
    parser.add_argument("--pinhole", dest="pinhole_filename", default=None,
            help="After calibrating, save the rectified light field as a rectified sub-aperture image.")
    parser.add_argument("--lenslet", dest="lenslet_filename", default=None,
            help="After calibrating, save the rectified light field as a rectified lenslet image.")
                      
    args = parser.parse_args(args)

    # Use single precision if runing on a Mac OS
    if sys.platform == "darwin":
        print(f"Identified system platform as {sys.platform}, so using single precision.")
        args.use_sing_prec = True

    # If no focal distance is supplied, then set it (by default) to be equal to the ulens focal length.
    if args.ulens_focal_distance is None:
        args.ulens_focal_distance = args.ulens_focal_length

    # Check if the input paremeters are valid.
    print("args.synthetic_lf: ", not args.synthetic_lf)
    if not args.synthetic_lf and not args.radiometry_frame_file:
        raise ParameterError("Please supply exactly one calibration image.")

    calibration_filename = args.radiometry_frame_file

    # Check if necessary pixel per lenslet information is supplied.
    if args.pixel_size is None:
        raise ParameterExistsError(args.pixel_size, "Please supply the pixel size.")
    
    if args.ulens_pitch is None:
        raise ParameterExistsError(args.ulens_pitch, "Please supply the microlens pitch.")

    if args.synthetic_lf:
        ns = args.ns
        nt = args.nt
        nu = nv = int(np.ceil(float(args.ulens_pitch) / args.pixel_size))
        synthetic_lf = 65535 * np.ones((nt*nv, ns*nu), dtype=np.uint16)

        save_image(calibration_filename, synthetic_lf, dtype=np.uint16)
        args.skip_alignment = True

    # Default output filename has a -RECTIFIED suffix
    if not args.output_filename:
        calib_filename, _ = os.path.splitext(calibration_filename)
        output_filename = calib_filename + '.lfc'
    else:
        output_filename = args.output_filename

    # Check if dark-frame or radiometry-frame are regular expressions referring to multiple files.
    # If so, save an average image as the dark/radiometry frame
    if args.dark_frame_file is not None and len(glob.glob(args.dark_frame_file)) > 1:
        dark_frame_files = glob.glob(args.dark_frame_file)
        avg_dark_frame = avg_images(dark_frame_files)
        args.dark_frame_file = os.path.dirname(output_filename) + os.sep + 'darkframe_avg' + os.path.splitext(dark_frame_files[0])[1]
        save_image(args.dark_frame_file, avg_dark_frame)

    if args.radiometry_frame_file is not None and len(glob.glob(args.radiometry_frame_file)) > 1:
        radiometry_frame_files = glob.glob(args.radiometry_frame_file)
        avg_radiometry_frame = avg_images(radiometry_frame_files)
        args.radiometry_frame_file = os.path.dirname(output_filename) + os.sep + 'radiometryframe_avg' + os.path.splitext(radiometry_frame_files[0])[1]
        save_image(args.radiometry_frame_file, avg_radiometry_frame)

    # Create a new calibration object
    from lflib.calibration import LightFieldCalibration


    # FOR DEBUGGING: Load a previous calibration
    #lfcal = LightFieldCalibration.load(output_filename)

    from lflib.calibration.imaging import CalibrationAlignmentMethods
    if args.affine_alignment:
        calibration_method = CalibrationAlignmentMethods.CALIBRATION_AFFINE_ALIGNMENT
    elif args.isometry_alignment:
        calibration_method = CalibrationAlignmentMethods.CALIBRATION_ISOMETRY_ALIGNMENT
    else:
        calibration_method = CalibrationAlignmentMethods.CALIBRATION_CUBIC_ALIGNMENT

    lfcal = LightFieldCalibration(args, args.ulens_focal_length, args.ulens_focal_distance,
                                  args.ulens_pitch, args.pixel_size,
                                  args.objective_magnification, args.objective_na, args.medium_index,
                                  args.tubelens_focal_length,
                                  args.ulens_fill_factor, args.pixel_fill_factor,
                                  args.ulens_profile, args.center_wavelength,
                                  calibration_method)

    # STEP 1 : MEASURE THE GEOMETRIC DISTORTION
    #
    # This routine computes an affine transform that squares the
    # lenslet array to a nice, regularly space grid.
    lfcal.calibrate_geometry(calibration_filename,
                             skip_alignment = args.skip_alignment,
                             skip_subpixel_alignment = args.skip_subpixel_alignment,
                             chief_ray_image = args.chief_ray_image,
                             radiometry_file = args.radiometry_frame_file,
                             align_radiometry = args.align_radiometry,
                             crop_center_lenslets = args.crop_center_lenslets)
    print(('   Calibrated light field has [ %d x %d ] ray samples and [ %d x %d ] spatial samples.' %
           (lfcal.nu, lfcal.nv, lfcal.ns, lfcal.nt)))

    # Optionally, create a rectified sub-aperture image
    if args.pinhole_filename:
        from lflib.lightfield import LightField
        im = load_image(calibration_filename, dtype=np.float32, normalize = False)
        lf = lfcal.rectify_lf(im).asimage(LightField.TILED_SUBAPERTURE)
        save_image(args.pinhole_filename, lf/lf.max() * 65535, dtype=np.uint16)

    # Optionally, create a rectified lenslet image
    if args.lenslet_filename:
        from lflib.lightfield import LightField
        im = load_image(calibration_filename, dtype=np.float32, normalize = False)
        lf = lfcal.rectify_lf(im).asimage(LightField.TILED_LENSLET)
        save_image(args.lenslet_filename, lf/lf.max() * 65535, dtype=np.uint16)

    # STEP 2 : Compute rayspread database
    #
    # The rayspread database is a look-up table that serves as the
    # optical model of forward and back-projection of the light field.
    print('-> Generating light field psf database.  (This may take a little while...)')
    lfcal.generate_raydb(args.num_slices, args.um_per_slice,
                         args.supersample, args.z_center, args.num_threads,
                         voxels_as_points = args.voxels_as_points)

    # STEP 3 : MEASURE THE APERTURE PLANE VIGNETTING FOR THIS LENSLET IMAGE
    #
    # The vignetting function can be used for deconvolution.

    # First we determine a reasonable number of pixels per lenslet to
    # use.  This must be the same scheme used in lfstack.py and
    # elsewhere.  It's a little dangerous here to be accessing
    # coefficient directly... we should veil this in some layer of
    # abstraction soon!
    print('-> Calibrating radiometry using ', args.radiometry_frame_file)
    try:
        lfcal.calibrate_radiometry(calibration_filename,
                radiometry_frame_file = args.radiometry_frame_file,
                dark_frame_file = args.dark_frame_file)
        # Save the result
        lfcal.save(output_filename, args.comments)
        lfcal.print_summary()

    except ZeroImageException:
        print("ERROR: calibrating against a blank radiometric image")

if __name__ == "__main__":
    main()
