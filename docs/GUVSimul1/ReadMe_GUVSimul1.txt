Simulated light field image of Giant Unilamellar Vesicle (GUV) 
stained with fluorescent membrane stain radiating isotropically

Simulation Software: RaytracingFluorIsotropicJuly2022.nb

voxPitch µLensPitch/3 = 0.5778µm,
magnObj = 60;  (*magnification of objective lens*)
naObj = 1.2;  (*naObj is NA of objective lens; ArcSine[1.2/1.33]=64°, tilt angle of ray passing through edge of aperture*)
nMedium = 1.35;  (*nMedium is the refractive index of the medium in object space*)
nrCamPix = 16;  (*nrCamPix is the number of camera pixels behind a lenslet in the horizontal and vertical direction*)
camPixPitch = 6.5;  (*size of camera pixels in micron*)
µLensCtr = {8, 8};  (*microLens center position in camera pixels*)
µLensPitch = 1.7333 (*= 104/60 µm in object space*)
rNA = 7.5;  (*rNA is the radius of the edge of the objective lens aperture in camera pixels*)

SUMMARY OF OPTICAL PARAMETERS
-----------------------------
pixel-size 6.5 um  (*camera pixel size*)
pitch 104 um  (*microlens pitch*)
focal-length 2500 um   (*microlens focal length*)
magnification 60x  (*magnification of microscope objective lens*)
na 1.2   (*numerical aperture of microscope objective lens*)
tubelens-focal-length 200.0 
wavelength 593 
medium-index ~1.35 

FILES
-----------------------------
LightField_GUVSimul1.tif: Simulated light field image, using simulateLF[guv[22, 1], {0, 0, 0}, {{-14, 14}, {-14, 14}}, True], 
GUV radius = 22.5 0.5778 = 13.0µm
Radiometry_GUVSimul1.tif: Radiometry image for generating calibration file
DarkFrame_GUVSimul1.tif: Dark frame
VolumeGroundTruth_GUVSimul1.tif: Volume stack used for simulating light field image, considered ground truth
Direct_GUVSimul1.tif: Simulated direct image projected onto µLens array, using simulateDirect[guv[22, 1], {0, 0, 0}, {{-14, 14}, {-14, 14}}, True]

Calibration_GUVSimul1-104.lfc: Number of Slices 104, um per Slice 0.43, Supersample 4 
	This calibration file is about 250MB and too big for Github storage. The file was deleted from this Repository
-> output_stack-104.tif

