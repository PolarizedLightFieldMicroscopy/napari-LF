# rectify.py
#
# Usage: rectify.py <lightfield_image.{tif,png,etc}> [--pixels-per-lenslet <ppl>]
#
# This script simply applies a rectification from a
# campixel_to_camlens.warp file to a single light field image.  The
# resulting rectified image should have the lenslets aligned with the
# horizontal and vertical dimensions of the image.  You can optionally
# specify the number of pixels per lenlet you would like in the output
# image, otherwise this value is computed for you based on the input
# imagery and the warp file.

from lflib.imageio import load_image, save_image
import sys, os
import numpy as np

def main(args=None, values=None):
    # Parse command line options
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('input_file', 
                        help="Supply at least one light field image to recfity.")
    parser.add_argument("-p", "--output-pixels-per-lenslet", dest="output_pixels_per_lenslet",
                      help="Specify the number of pixels per lenslet in the output image.")
    parser.add_argument("-o", "--output-file", dest="output_filename",
                      help="Specify the output filename.")
    parser.add_argument("-c", "--calibration-file", dest="calibration_file",
                      help="Specify the calibration file to use for rectification.")
    parser.add_argument('-s', "--subaperture",
                      action="store_true", dest="subaperture", default=False,
                      help="Save out the light field image as tiled subapertures.")
                      
    args = parser.parse_args(args)

    print(f"Rectifying {args.input_file}")

    # for filename in args:
    filename = args.input_file

    # Default calibration filename has a *.lfc suffix, and the same prefix
    if not args.calibration_file:
        fileName, fileExtension = os.path.splitext(filename)
        calibration_file = f"{fileName}.lfc"
    else:
        calibration_file = args.calibration_file

    # Default output filename has a -RECTIFIED suffix
    if not args.output_filename:
        fileName, fileExtension = os.path.splitext(filename)
        output_filename = f"{fileName}-RECTIFIED{fileExtension}"
    else:
        output_filename = args.output_filename

    # Load the calibration data
    from lflib.calibration import LightFieldCalibration
    lfcal = LightFieldCalibration.load(calibration_file)

    # Rectify the image
    im = load_image(filename, normalize = False)
    input_dtype = im.dtype

    # Perform dark frame subtraction
    im = lfcal.subtract_dark_frame(im)

    # Rectify the image
    rectified_lf = lfcal.rectify_lf(im)


    # Optionally reformat the image so that sub-aperturs are tiled, rather than lenslet images.
    from lflib.lightfield import LightField
    if (args.subaperture):
        im = rectified_lf.asimage(LightField.TILED_SUBAPERTURE)
        print('\t--> Saving', output_filename, 'as tiled sub-aperture image.')
    else:
        im = rectified_lf.asimage(LightField.TILED_LENSLET)
        print('\t--> Saving', output_filename, 'as tiled lenslet image.')

    print(f"Maximum:{im.max()}, Minimum:{im.min()}")

    save_image(output_filename, im, dtype=np.uint16)

if __name__ == "__main__":
    main()