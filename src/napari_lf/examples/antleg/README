This is a light field of an ant leg, taken using a water immersion 20x
0.5NA objective and a 125um pitch, f/20 microlens array (focal length
2433um).  The image was collected on an Andor Neo sCMOS imager (6.5um 
pixel pitch).  The image was magnified slightly using a 50:35 relay lens 
that makes for an effective pixel size of 4.55um.

This directory also contains a radiometry image collected by placing a
fluorescent flat field test slide under the microscope.  This serves
to calibrate both the radiometry and position of the lenslets.

The dark frame was taken with no light falling on the sensor.
This gives the bias level for the camera, which is taken into
account when reconstructing the image.  


SUMMARY OF OPTICAL PARAMETERS
-----------------------------

pixel-size 4.55 um
pitch 125 um
focal-length 2433 um 
magnification 20 x
na 0.5 
tubelens-focal-length 180.0 
wavelength 510 
medium-index 1.33 


EXAMPLE USE CASE
----------------
First navigate to the directory <path to LFAnalyze>/examples/ant_leg/.

STEP 1: calibrate and the data and prepare it for a reconstruction
with 50 z-slices with 5um spacing, and with 4x sampling over the
"native" lenslet resolution.

Run one of the following options in the terminal:
1. python calibrate.py
2. python /../../lfcalibrate.py raidometry_20x-000000.png --radiometry-frame raidometry_20x-000000.png --dark-frame dark_frame-000000.tif --pixel-size 4.55 --pitch 125 --focal-length 2433 --magnification 20 --na 0.5 --tubelens-focal-length 180.0 --wavelength 510 --medium-index 1.33 --num-slices 50 --um-per-slice 5.0 --supersample 4 -o antleg_calibration.lfc

STEP 2: perform light field deconvolution, producing a deconvolved volume stored in a tiff stack.

Run one of the following options in the terminal:
1. python deconvolve.py
2. python ../../lfdeconvolve.py light_field-000000.png -c antleg_calibration.lfc -o antleg_stack.tif

Recfifying instructions below are to be updated.
---------
(optional) Step 3: using the geometric calibration, 'rectify' a raw light field image for
further processing using your own algorithms.

As a lenslet image:
   python2.7 <path to LFAanalyze>/lfrectify.py -c antleg_calibration.lfc light_field-000000.png -o rectified_lenslet.tif

As a subaperture image:
    python2.7 <path to LFAanalyze>/lfrectify.py -c antleg_calibration.lfc light_field-000000.png --subaperture -o rectified_subaperture.tif

DEBUGGING
---------

The calibration file calibration_std.lfc was used to generate
the output file antleg_stack_std.tif. These files are to be
used a reference standard for comparison. Deconvolution was
performed with the solver "rl".
