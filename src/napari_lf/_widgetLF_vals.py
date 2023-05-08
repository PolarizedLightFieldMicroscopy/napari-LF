import os, sys, multiprocessing
from qtpy.QtGui import QIcon

currentdir = os.path.dirname(os.path.realpath(__file__))
icon_img = os.path.join(currentdir, 'resources/icon.ico')
logo_img = os.path.join(currentdir, 'resources/logos/napari-LF_logo.png')

# Image processing logos
# TODO: Only the active ("act") logos have had their font updated. The other logos
# 	should be updated. They should also be in used or removed.
# LF Analyze
LFAnalyze_logo_img = os.path.join(currentdir, 'resources/LFAnalyze_logo_201_45px.png')
LFAnalyze_logo_btn_img = os.path.join(currentdir, 'resources/lfa_logo/buttons/half_res/LFA_logo_3D_inact_201_45px.png')
LFAnalyze_logo_btn_hov_img = os.path.join(currentdir, 'resources/lfa_logo/buttons/half_res/LFA_logo_3D_hov_201_45px.png')
LFAnalyze_logo_btn_act_img = os.path.join(currentdir, 'resources/logos/lfa_logo_3d_act.png')
# Neural Net
NeuralNet_logo_img = os.path.join(currentdir, 'resources/NeuralNet_logo_201_45px.png')
NeuralNet_logo_btn_img = os.path.join(currentdir, 'resources/nn_logo/buttons/half_res/NN_logo_3D_inact_201_45px.png')
NeuralNet_logo_btn_hov_img = os.path.join(currentdir, 'resources/nn_logo/buttons/half_res/NN_logo_3D_hov_201_45px.png')
NeuralNet_logo_btn_act_img = os.path.join(currentdir, 'resources/logos/nn_logo_3d_act.png')

loading_img = os.path.join(currentdir, 'resources/loading.gif')
examples_folder = os.path.join(currentdir, 'examples/antleg')
lfa_folder = os.path.join(currentdir, 'lfa')

q_icon_img = QIcon(icon_img)

SOLVER_OPTIONS = {
	'Approximate Message Passing (with optional multiscale denoising':'amp', 'Alternating Direction Method of Multipliers with Huber loss':'admm_huber','Alternating Direction Method of Multipliers with TV penalty':'admm_tv','Conjugate Gradient':'cg','Direct method with Cholesky factorization':'direct','Least Squares QR':'lsqr','K-space deconvolution':'kspace','Simultaneous Iterative Reconstruction Technique':'sirt','MRNSD':'mrnsd','Richardson-Lucy':'rl'
}

IMAGE_EXTS = ["tif","png","jpg","bmp"]
HDF5_EXTS = ["hdf", "h4", "hdf4", "h5", "hdf5", "he2", "he5", "lfc"]
PROJ_EXTS = IMAGE_EXTS
MODEL_EXTS = ["ckpt"]

METHODS = ['PLUGIN','NAPARI','APP']
SETTINGS_FILENAME = "settings.ini"

# https://napari.org/magicgui/usage/widget_overview.html
# https://napari.org/magicgui/api/_autosummary/magicgui.widgets.create_widget.html#magicgui.widgets.create_widget
# PLUGIN_ARGS also creates GUI elements
# Required properties are "type","label","default","help"
# A type == sel must include "options" property
# Based on "type" appropriate widgets will be created
# Define additional widget attributes (eg. enabled, visible etc.) for further customization (refer widget overview link above)
# For calibrate, rectify, deconvolve add property "cat":"required" to be included under Required tab, otherwise gui element will be under Optional tab
# GUI elements will be laid vertically as per sequence here for each main tab (Calibrate, Rectify, Deconvolve, Hardware, Misc)

develop_mode = False # change to True if developing
dev_true = False
dev_false = True
if develop_mode:
	dev_true = True
	dev_false = False

PLUGIN_ARGS = {
	"main":{
		"logo_label":{
			"label":f'<a href="https://chanzuckerberg.com/science/programs-resources/imaging/napari/light-field-imaging-plugin/"><img src="{logo_img}" height="60"></a>',"help":"napari-LF About WebPage","type":"img_label","default":"","exclude_from_settings":True
		},
		"img_folder":{
			"label":"Project folder","default":examples_folder,"help":"Select your dataset folder containing the raw light field image(s).","type":"folder"
		},
		"img_list":{
			"label":"Available images","default":"","help":"List of available Images to view in the selected Project folder.","type":"sel","options":[""]
		},
		"metadata_file":{
			"default":"metadata.txt","label":"Metadata file","help":"Select the name of the metadata file that will be produced for the dataset.","type":"str","enabled":True,"visible":False
		},
		"comments":{
			"default":"","prop":"--comments","label":"Comments","help":"Comments from Acquisition and Processing","type":"str","type":"text"
		},
		"presets":{
			"default":"","label":"Presets","help":"Save/Load parameters from presets.","type":"sel","options":[""]
		},
		"status":{
			"label":"STATUS:","value":"== IDLE ==","value_busy":"== BUSY ==","value_idle":"== IDLE ==","value_error":"== ERROR ==","type":"label","default":"== IDLE ==","exclude_from_settings":True
		},
		"NapariLF_ver_label":{
			"label":"napari-LF Plugin Ver:","default":"","help":"napari-LF Plugin version.","type":"label","exclude_from_settings":True
		},
		"LFAnalyze_logo_label":{
			"label":f'<a href="https://graphics.stanford.edu/projects/lfmicroscope/"><img src="{LFAnalyze_logo_img}" height="50"></a>',"help":"LF Analyze About WebPage","type":"img_label","default":"","exclude_from_settings":True
		},
		"LFMNet_logo_label":{
			"label":f'<a href="https://github.com/pvjosue/LFMNet"><img src="{NeuralNet_logo_img}" height="50"></a>',"help":"LFMNet About WebPage","type":"img_label","default":"","exclude_from_settings":True
		},
	},
	"misc":{
		"lib_ver_label":{
			"label":"LF Analyze Ver:","default":"","help":"LF Analyze Library version.","type":"label"
		},
		"lib_folder":{
			"label":"LF Analyze folder","default":lfa_folder,"help":"Select your LF Analyze Library folder.","type":"folder"
		},
		"group_params":{
			"label":"Group parameters","default":True,"help":"Group parameters into sections (requires restart).","type":"bool","enabled":dev_true,"visible":dev_true
		},
		"use_ext_viewer":{
			"label":"Use system/external viewer","type":"bool","default":False,"help":"Use system/external viewer for displaying images instead."
		},
		"ext_viewer_sel":{
			"label":"Viewer","type":"sel","default":"System","options":["System","External"],"help":"Chose your viewer (System: OS default, External: User selects path below)."
		},
		"ext_viewer":{
			"label":"External viewer","type":"file","default":{'linux':'','win32':'','darwin':''}[sys.platform],"help":"Chose your external viewer (executable file)."
		},
		"disable_mousewheel":{
			"label":"Disable mousewheel on combobox and spinner widgets","type":"bool","default":True,"help":"Disable mousewheel on combobox and spinner widgets to avoid accidentally changing values."
		}
	},
	"hw":{
		"gpu_id":{
			"prop":"--gpu-id","dest":"gpu_id","type":"int","default":int(os.environ.get('USE_GPU_ID', 0)),"help":"Force lfdeconvolve to use a specific GPU on your system. If not supplied this will default to $USE_GPU_ID or 0), if --gpu-id is not supplied it will default to the value of the USE_GPU_ID environment variable, if set, or 0 otherwise.","exclude_from_args":True
		},
		"platform_id":{
			"prop":"--platform-id","label":"Select platform","dest":"platform_id","type":"int","default":0,"help":"Force lfdeconvolve to use a specific OpenCL Platform on your system."
		},
		"use_single_prec":{
			"prop":"--use-single-precision","label":"Use single precision","action":"store_true","dest":"use_sing_prec","type":"bool","default":False,"help":"Use single precision float instead of double."
		},
		"disable_gpu":{
			"prop":"--disable-gpu","action":"store_true","label":"Disable GPU","dest":"disable_gpu","type":"bool","default":False,"help":"Disable GPU deconvolution and use software implementation instead."
		}
	},
	"calibrate":{
	# ===============================
	# ======= Calibrate =============
	# ===============================
		# Input/Output Files
		"radiometry_frame_file":{
			"prop":"--radiometry-frame","label":"Radiometry image","dest":"radiometry_frame_file","type":"sel","default":"radiometry_frame.png","options":["radiometry_frame.png"],"help":"Specify a radiometry frame to use for radiometric correction. If no frame is specified, then no radiometric correction is carried out.","cat":"required","img_folder_file":True,"group":"Files"
		},
		"dark_frame_file":{
			"prop":"--dark-frame","label":"Dark frame image","dest":"dark_frame_file","default":"dark_frame.tif","options":["dark_frame.tif"],"type":"sel","help":"Specify a dark frame image to subtract from the input light-field before processing (This makes radiometric calibration more accurate).","cat":"required","img_folder_file":True,"group":"Files"
		},		
		"output_filename":{
			"prop_short":"-o","prop":"--output-filename","label":"Calibration file","default":"calibration.lfc","dest":"output_filename","help":"Specify the name of the calibration file.","type":"str","cat":"required","img_folder_file":True,"group":"Files"
		},
		"calibration_files":{
			"label":"Calibration file","default":"","dest":"calibration_files","help":"Inspect the selected calibration file.","type":"sel","options":[""],"cat":"inspect","group":"Inspector","exclude_from_settings":True,"exclude_from_args":True
		},
		"calibration_files_viewer":{
			"label":"Calibration file viewer","default":"","dest":"calibration_files_viewer","help":"Inspect the selected calibration file data in viewer. (Placeholder for a future HDF5 Viewer)","type":"text","cat":"inspect","group":"Inspector","exclude_from_settings":True,"exclude_from_args":True,"read_only":True,"no_label_layout_style":True
		},
		# Calibration routine parameters
		"synthetic_lf":{
			"prop":"--synthetic","label":"Synthetic LF","action":"store_true","dest":"synthetic_lf","default":False,"help":"Use this option to create a synthetic light field (i.e. with no calibration image","type":"bool","group":"Calibration routine parameters","enabled":dev_true,"visible":dev_true
		},
		"use_ray_optics":{
			"prop":"--use-ray-optics","label":"Use ray optics","action":"store_true","dest":"use_ray_optics","default":False,"help":"Use the less accurate ray optics model rather than wave optics model.","type":"bool","group":"Calibration routine parameters","enabled":dev_true,"visible":dev_true
		},
		"voxels_as_points":{
			"prop":"--voxels-as-points","label":"Use voxels as points","action":"store_true","dest":"voxels_as_points","default":False,"help":"Treat each voxel as an ideal point source. This turns of numerical integration that gives the voxel spatial extent (which can be important for anti-aliasing).","type":"bool","group":"Calibration routine parameters"
		},
		"align_radiometry":{
			"prop":"--align-radiometry","label":"Align radiometry","action":"store_true","dest":"align_radiometry","type":"bool","default":False,"help":"Align the radiometry image automatically to the geometric calibration image. (Use this option when the radiometry frame has been \"bumped\" before imaging begins).","group":"Calibration routine parameters"
		},
		 # Optical parameters
		"ulens_pitch":{
			"prop":"--pitch","label":"Microlens pitch (um)","dest":"ulens_pitch","type":"float","default":125,"help":"Specify the microlens pitch (in microns).","cat":"required","group":"Optical parameters"
		},
		"pixel_size":{
			"prop":"--pixel-size","label":"Pixel size (um)","dest":"pixel_size","type":"float","default":4.55,"help":"Specify the size of a pixel on the sensor taking magnification due to relay optics into account (in microns).","cat":"required","step":0.001,"group":"Optical parameters"
		},	
		"ulens_focal_length":{
			"prop":"--focal-length","label":"Microlens focal length (um)","dest":"ulens_focal_length","type":"float","default":2433,"step":1,"help":"Specify the microlens focal length (in microns).","cat":"required","max":5000,"group":"Optical parameters"
		},
		"ulens_focal_distance":{
			"prop":"--ulens-focal-distance","label":"Microlens focal distance (um)","dest":"ulens_focal_distance","type":"float","default":2433,"step":1,"help":"Specify the microlens focal distance (in microns). If you do not specify a value it is assumed that the focal distance is equal to the focal length.","max":5000,"group":"Optical parameters","bind":"ulens_focal_length"
		},
		"objective_magnification":{
			"prop":"--magnification","label":"Objective magnification","dest":"objective_magnification","type":"int","default":20,"help":"Specify the objective magnification.","cat":"required","group":"Optical parameters"
		},
		"objective_na":{
			"prop":"--na","label":"Objective NA","dest":"objective_na","type":"float","default":0.5,"help":"Specify the objective numerical aperture.","cat":"required","group":"Optical parameters"
		},
		"tubelens_focal_length":{
			"prop":"--tubelens-focal-length","label":"Tubelens focal length (mm)","dest":"tubelens_focal_length","type":"float","default":180.0,"step":1,"help":"Tube lens focal length (in millimeters).","cat":"required","group":"Optical parameters"
		},
		"center_wavelength":{
			"prop":"--wavelength","label":"Center wavelength (nm)","dest":"center_wavelength","type":"float","default":510,"step":1,"help":"Center wavelength of emission spectrum of the sample (nm).","cat":"required","group":"Optical parameters"
		},
		"medium_index":{
			"prop":"--medium-index","label":"Medium index","dest":"medium_index","type":"float","default":1.33,"help":"Set the index of refraction of the medium.","cat":"required","group":"Optical parameters"
		},
		"ulens_fill_factor":{
			"prop":"--ulens-fill-factor","label":"Microlens fill factor","dest":"ulens_fill_factor","type":"float","default":1.0,"help":"Specify the microlens fill factor (e.g. 1.0, 0.7, ...).","group":"Optical parameters"
		},
		"pixel_fill_factor":{
			"prop":"--pixel-fill-factor","label":"Pixel fill factor","dest":"pixel_fill_factor","type":"float","default":1.0,"help":"Specify the pixel fill factor (e.g. 1.0, 0.7, ...).","group":"Optical parameters"
		},
		"ulens_profile":{
			"prop":"--ulens-profile","label":"Microlens profile","dest":"ulens_profile","default":'rect',"options":['rect','circ'],"type":"sel","help":"Specify the shape of the microlens apertures. Options include: ['rect', 'circ']","group":"Optical parameters"
		},
		# Volume parameters
		"num_slices":{
			"prop":"--num-slices","label":"Number of slices","dest":"num_slices","type":"int","default":5,"help":"Set the number of slices to produce in the output stacks.","cat":"required","exclude_from_args":False,"group":"Volume parameters"
		},
		"um_per_slice":{
			"prop":"--um-per-slice","label":"um per slice","dest":"um_per_slice","type":"float","default":5.0,"step":0.1,"help":"Set the thickness of each slice (in um).","cat":"required","exclude_from_args":False,"group":"Volume parameters"
		},
		"supersample":{
			"prop":"--supersample","label":"Supersample","dest":"supersample","type":"int","default":4,"help":"Supersample the light field volume. This results in a higher resolution reconstruction up to a point and interpolation after that point.","cat":"required","exclude_from_args":False,"group":"Volume parameters"
		},
		"z_center":{
			"prop":"--z-center","label":"Central z-slice offset (um)","dest":"z_center","type":"float","default":0.0,"help":"Set the offset for the central z slice (in um).","group":"Volume parameters"
		},
		# Geometric calibration Options
		"affine_alignment":{
			"prop":"--affine-alignment","action":"store_true","label":"Affine alignment","dest":"affine_alignment","type":"bool","default":False,"help":"Use affine warp for correcting geometric distortion (default is cubic).","group":"Geometric calibration Options"
		},
		"isometry_alignment":{
			"prop":"--isometry-alignment","action":"store_true","label":"Isometry alignment","dest":"isometry_alignment","type":"bool","default":False,"help":"Use isometry warp for correcting geometric distortion (default is cubic).","group":"Geometric calibration Options"
		},
		"chief_ray_image":{
			"prop":"--chief-ray","action":"store_true","label":"Chief ray image","dest":"chief_ray_image","type":"bool","default":False,"help":"Use this flag to indicate that the calibration frame is a chief ray image.","group":"Geometric calibration Options"
		},
		# Commented out to avoid being shown in plugin even with visible is False
		# # Synthetic parameters
		# "ns":{
		# 	"prop":"--ns","label":"Lenslet s-direction","dest":"ns","type":"int","default":50,"help":"Set the lenslets in s direction.","group":"Synthetic parameters","enabled":dev_true,"visible":dev_true
		# },
		# "nt":{
		# 	"prop":"--nt","label":"Lenslet t-direction","dest":"nt","type":"int","default":50,"help":"Set the lenslets in t direction.","group":"Synthetic parameters","enabled":dev_true,"visible":dev_true
		# },
		# Other Options
		"crop_center_lenslets":{
			"prop":"--crop-center-lenslets","action":"store_true","label":"Crop center lenslets","dest":"crop_center_lenslets","type":"bool","default":False,"help":"For severe aperture vignetting (high NA objectives)	 use only center lenslets for calibration and extrapolate outwards.","group":"Other Options"
		},
		"skip_alignment":{
			"prop":"--skip-alignment","action":"store_true","label":"Skip alignment","dest":"skip_alignment","type":"bool","default":False,"help":"Skip the alignment step during geometric calibration (useful if you are working with an already-rectified light field or a synthetic light field.","group":"Other Options"
		},
		"skip_subpixel_alignment":{
			"prop":"--skip-subpixel-alignment","action":"store_true","label":"Skip subpixel alignment","dest":"skip_subpixel_alignment","type":"bool","default":False,"help":"Skip subpixel alignment for determining lenslet centers.","group":"Other Options"
		},
		"num_threads":{
			"prop":"--num-threads","label":"Number of CPU threads","dest":"num_threads","type":"int","default":min(10,multiprocessing.cpu_count()),"help":"Set the number of CPU threads to use when generating the raydb.","group":"Other Options","max":multiprocessing.cpu_count(), "min":1
		},
		"pinhole_filename":{
			"prop":"--pinhole","label":"Pinhole filename","dest":"pinhole_filename","type":"str","default":"","help":"After calibrating save the rectified light field as a rectified sub-aperture image.","group":"Other Options"
		},
		"lenslet_filename":{
			"prop":"--lenslet","label":"Lenslet filename","dest":"lenslet_filename","type":"str","default":"","help":"After calibrating save the rectified light field as a rectified lenslet image.","group":"Other Options"
		},
		"debug":{
			"prop_short":"-d","prop":"--debug","label":"Debug","action":"store_true","dest":"debug","type":"bool","default":False,"help":"Save debug images.","group":"Other Options","enabled":dev_true,"visible":dev_true
		}
	},
	"rectify":{
	# ===============================
	# ========== Rectify ============
	# ===============================		
		"input_file":{
			"prop_short":"-i","prop":"--input_file","label":"Light field image","dest":"input_file","type":"sel","default":"light_field.png","options":["light_field.png"],"help":"Supply at least one light field image to rectify.","cat":"required","img_folder_file":True,"exclude_from_args":True,"group":"Files"
		},
		"calibration_file":{
			"prop_short":"-c","prop":"--calibration-file","label":"Calibration file","dest":"calibration_file","type":"sel","default":"calibration.lfc","options":["calibration.lfc"],"help":"Specify the calibration file to use for rectification.","cat":"required","img_folder_file":True,"group":"Files"
		},
		"output_filename":{
			"prop_short":"-o","prop":"--output-file","label":"Rectified image","dest":"output_filename","type":"str","default":"rectified.png","help":"Specify the output filename.","cat":"required","img_folder_file":True,"group":"Files"
		},
		"subaperture":{
			"prop_short":"-s","prop":"--subaperture","action":"store_true","label":"Subaperture","dest":"subaperture","type":"bool","default":False,"help":"Save out the light field image as tiled subapertures."
		},
		"output_pixels_per_lenslet":{
			"prop_short":"-p","prop":"--output-pixels-per-lenslet","label":"Output pixels per lenslet","dest":"output_pixels_per_lenslet","type":"str","default":"","help":"Specify the number of pixels per lenslet in the output image."
		}
	},
	"deconvolve":{
	# ===============================
	# ======= Deconvolve ============
	# ===============================
		"input_file":{
			"prop":"input_file","label":"Light field image","dest":"input_file","type":"sel","default":"light_field.png","options":["light_field.png"],"help":"You must supply at least one light field image to deconvolve.","cat":"required","img_folder_file":True,"exclude_from_args":True,"group":"Files"
		},
		"calibration_file":{
			"prop_short":"-c","prop":"--calibration-file","label":"Calibration file","dest":"calibration_file","type":"sel","default":"calibration.lfc","options":["calibration.lfc"],"help":"Specify the calibration file to use for rectification.","cat":"required","img_folder_file":True,"group":"Files"
		},
		"output_filename":{
			"prop_short":"-o","prop":"--output-file","label":"Output image stack","dest":"output_filename","type":"str","default":"output_stack.tif","help":"Specify the output filename.","cat":"required","img_folder_file":True,"group":"Files"
		},
		# Commented out to avoid being shown in plugin even with visible is False
		# "private_fn":{
		# 	"prop":"--private-key","label":"Private fn","dest":"private_fn","type":"file","default":os.path.join(os.path.dirname(os.path.abspath(__file__)), 'enlightenment_c3'),"help":"Specify the private key file for remote transfers.","enabled":dev_true,"visible":dev_true
		# },
		# "cov_directory":{			
		# 	"prop":"--cov-directory","label":"Cov directory","dest":"cov_directory","type":"str","default":"","help":"Specify the directory where ADMM covariance matrices are saved.","enabled":dev_true,"visible":dev_true
		# },
		# Algorithm selection
		"solver":{
			"prop":"--solver","label":"Solver","dest":"solver","type":"sel","default":"rl",
			"options":[SOLVER_OPTIONS[key] for key in SOLVER_OPTIONS],
			"help":"Available reconstruction methods are: \nApproximate Message Passing (with optional multiscale denoising (\'amp\')\nAlternating Direction Method of Multipliers with Huber loss (\'admm_huber\')\nAlternating Direction Method of Multipliers with TV penalty (\'admm_tv\')\nConjugate Gradient (\'cg\')\nDirect method with Cholesky factorization (\'direct\')\nLeast Squares QR (\'lsqr\')\nK-space deconvolution (\'kspace\')\nSimultaneous Iterative Reconstruction Technique (\'sirt\')\nMRNSD (\'mrnsd\')\nand Richardson-Lucy (\'rl\'). Default is currently \'rl\'.","group":"Algorithm selection"
		},
		# Algorithm-specific parameters							
		"alpha":{
			"prop":"--alpha","label":"Alpha","dest":"alpha","type":"float","default":1.6,"help":"Relaxation parameter for SIRT-based iterative reconstruction.","group":"Algorithm selection"
		},
		"multiscale_smoothing":{				
			"prop":"--multiscale-smoothing","label":"Multiscale smoothing","dest":"multiscale_smoothing","action":"store_true","type":"bool","default":False,"help":"Multiscale regularization option for AMP reconstruction.","group":"Algorithm selection"
		},
		"save_multiscale":{
			"prop":"--save-multiscale","label":"Save multiscale","dest":"save_multiscale","action":"store_true","type":"bool","default":False,"help":"Save multilevel decomposition of data.","group":"Algorithm selection"
		},
		# Generic parameters for iterative reconstruction routines						
		"regularization_lambda":{
			"prop":"--lambda","label":"Regularization lambda","dest":"regularization_lambda","type":"float","default":0.0,"help":"Regularization coefficient (behavior varies by reconstruction algorithm)","group":"Generic parameters for iterative reconstruction routines"
		},
		"regularization_lambda2":{
			"prop":"--lambda2","label":"Regularization lambda2","dest":"regularization_lambda2","type":"float","default":0.0,"help":"Additional regularization coefficient. (Behavior varies by algorithm and not all algorithms use two regularization coefficients.)","group":"Generic parameters for iterative reconstruction routines"
		},
		"max_iter":{
			"prop":"--max-iter","label":"Max iterations","dest":"max_iter","type":"int","default":15,"help":"Maximum number of iterations for SIRT-based reconstruction.","group":"Generic parameters for iterative reconstruction routines"
		},
		"conv_thresh":{
			"prop":"--convergence-threshold","label":"Convergence threshold","dest":"conv_thresh","type":"float","default":0.0,"help":"Convergence criteria threshold, d/dt (MSE). Try 5e-5 for SIRT, 1e-2 for TV.","group":"Generic parameters for iterative reconstruction routines"
		},
		# Noise model parameters					
		"readnoise_variance":{
			"prop":"--readnoise-variance","label":"Readnoise variance","dest":"readnoise_variance","type":"float","default":0.0,"help":"Set the variance of the (measured) camera read noise.","group":"Noise model parameters"
		},
		"background_level":{					
			"prop":"--background-level","label":"Background level","dest":"background_level","type":"float","default":1.0,"help":"Set the (measured) background level of the image.","group":"Noise model parameters"
		},
		# Assorted other parameters	
		"focalstack":{
			"prop":"--focalstack","action":"store_true","label":"Focal stack","dest":"focalstack","type":"bool","default":False,"help":"Turn off deconvolution and simply save a focal stack to disk.","group":"Assorted other parameters"
		},
		"remove_grid":{
			"prop":"--remove-grid","action":"store_true","label":"Remove grid","dest":"remove_grid","type":"bool","default":False,"help":"Remove grid artifacts in light field image using spectral median filter.","group":"Assorted other parameters"
		},
		"pinhole_filename":{
			"prop":"--pinhole-file","label":"Pinhole filename","dest":"pinhole_filename","default":"","type":"str","help":"After deconvolution  save out a deconvolved light field sub-aperture image.","img_folder_file":True,"group":"Assorted other parameters"
		},
		"decon_type":{
			"prop":"--deconvolution-type","label":"Deconvolution type","dest":"decon_type","default":'algebraic',"options":['algebraic','direct','admm'],"type":"sel","help":"Choose deconvolution method. One of [algebraic, direct, admm].","group":"Assorted other parameters"
		},
		"reg_factor":{
			"prop":"--reg-factor","label":"Registration factor","dest":"reg_factor","type":"float","default":100,"help":"Regularization parameter used in ADMM.","group":"Assorted other parameters"
		},
		"h5py_cov_filename":{
			"prop":"--h5py-cov-filename","label":"HDF5 covariance filename","dest":"h5py_cov_filename","default":'tests/covariance_blocks.h5',"type":"str","help":"Specify the HDF5 covariance filename.","group":"Assorted other parameters"
		},
		# Commented out to avoid being shown in plugin even with visible is False
		# "direct_type":{ #ToDo: ensure ' projection matrix method' prop name is correct
		# 	"prop":"--direct-type","label":"Direct type","dest":"direct_type","default":"covariance","type":"sel","options":["covariance","projection matrix"],"help":"If --direct flag is set to True specifies whether the covariance or projection matrix method is used.","group":"Assorted other parameters","enabled":dev_true,"visible":dev_true
		# },
		"benchmark":{
			"prop":"--benchmark","action":"store_true","label":"Benchmark","dest":"benchmark","type":"bool","default":False,"help":"Compare the CPU and GPU speeds for forward & back porjection operations.","group":"Assorted other parameters","enabled":dev_true,"visible":dev_true
		},
		# Commented out to avoid being shown in plugin even with visible is False
		# "test":{
		# 	"prop":"--test","label":"Unit test","dest":"test","type":"sel","default":1,"options":[1,2,3,4],"help":"Select a unit test (1-4).","group":"Assorted other parameters","enabled":dev_true,"visible":dev_true
		# },
		"log_convergence":{
			"prop":"--log-convergence","action":"store_true","label":"Log convergence","dest":"log_convergence","type":"bool","default":False,"help":"For logging convergence details.","group":"Assorted other parameters"
		}
	},
	"projections":{
	# ===============================
	# ======= Projections ============
	# ===============================
 		"calibration_file":{
			"prop_short":"-c","prop":"--calibration-file","label":"Calibration file","dest":"calibration_file","type":"sel","default":"calibration.lfc","options":["calibration.lfc"],"help":"Specify the calibration file to use for rectification.","cat":"required","img_folder_file":True,"group":"Calibrations"
		},
		"input_file_volume":{
			"prop":"input_file_volume","label":"Forward (volumes)","dest":"input_file_volume","type":"sel","default":"","options":[""],"help":"","exclude_from_args":True,"exclude_from_settings":True,"img_folder_file":True,"group":"Forward Projections"
		},
		"output_filename_lightfield":{
			"prop":"--output-filename-lightfield","label":"Output LF image","dest":"output_filename","type":"str","default":"output_proj_lf_img.tif","help":"Specify the output filename.","cat":"required","img_folder_file":True,"group":"Forward Projections"
		},
		"input_file_volume_btn":{
			"prop":"input_file_volume_btn","label_btn":"Process", "label":"Project Volume", "dest":"input_file_volume_btn","type":"PushButton","help":"","exclude_from_args":True,"exclude_from_settings":True,"group":"Forward Projections", "height":45, "width":200
		},
		"input_file_lightfield":{
			"prop":"input_file_lightfield","label":"Backward (lightfields)","dest":"input_file_lightfield","type":"sel","default":"","options":[""],"help":"","exclude_from_args":True,"exclude_from_settings":True,"img_folder_file":True,"group":"Backward Projections"
		},
		"output_filename_volume":{
			"prop":"--output-filename-volume","label":"Output volume stack","dest":"output_filename","type":"str","default":"output_proj_vol_stack.tif","help":"Specify the output filename.","cat":"required","img_folder_file":True,"group":"Backward Projections"
		},
		"input_file_lightfield_btn":{
			"prop":"input_file_lightfield_btn","label_btn":"Process", "label":"Project Lightfield","dest":"input_file_lightfield_btn","type":"PushButton","help":"","exclude_from_args":True,"exclude_from_settings":True,"group":"Backward Projections", "height":45, "width":200
		}
	},
	"lfmnet":{
	# ===============================
	# ======= LFMNet ============
	# ===============================
		"input_file":{
			"prop":"input_file","label":"Light field image","dest":"input_file","type":"sel","default":"","options":[""],"help":"Supply at least one light field image to rectify.","cat":"required","img_folder_file":True,"group":"Files"
		},
		# "calibration_file":{
		# 	"prop":"calibration_file","label":"Calibration file","dest":"calibration_file","type":"sel","default":"","options":[""],"help":"Specify the calibration file to use for rectification.","cat":"required","img_folder_file":True,"group":"Files"
		# },
		"input_model":{
			"prop":"input_model","label":"Neural net model","dest":"input_model","type":"sel","default":"","options":[""],"help":"","exclude_from_args":True,"exclude_from_settings":True,"group":"Files"
		},
		"input_model_prop_viewer":{
			"prop":"input_model_prop_viewer","label":"Model Prop Viewer","dest":"input_model_prop_viewer","default":"","options":[""],"help":"","exclude_from_args":True,"exclude_from_settings":True,"group":"Files", "type":"text","group":"Network Model Inspector","exclude_from_settings":True,"exclude_from_args":True,"read_only":True,"no_label_layout_style":True
		},
		"output_filename":{
			"prop":"output_file","label":"Output image stack","dest":"output_filename","type":"str","default":"output_network_stack.tif","help":"Specify the output filename.","cat":"required","img_folder_file":True,"group":"Files"
		},
		"input_model_btn":{
			"prop":"input_model_btn","label":"Deconvolve","dest":"input_model_btn","type":"PushButton","help":"","exclude_from_args":True,"exclude_from_settings":True,"group":"Files","visible":dev_true
		}
	}
}

def set_default_vals():
	for section in PLUGIN_ARGS:
		for key in PLUGIN_ARGS[section]:
			dict = PLUGIN_ARGS[section][key]
			if "default" in dict:
				dict["value"] = dict["default"]
				
set_default_vals()
