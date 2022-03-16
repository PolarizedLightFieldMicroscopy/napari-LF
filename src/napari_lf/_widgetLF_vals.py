import os
currentdir = os.path.dirname(os.path.realpath(__file__))
logo_img = os.path.join(currentdir, 'resources\\lfa_logo_napari.png')
loading_img = os.path.join(currentdir, 'resources\\loading.gif')
examples_folder = os.path.join(currentdir, 'examples\\antleg')

SOLVER_OPTIONS = {
	'Approximate Message Passing (with optional multiscale denoising':'amp', 'Alternating Direction Method of Multipliers with Huber loss':'admm_huber','Alternating Direction Method of Multipliers with TV penalty':'admm_tv','Conjugate Gradient':'cg','Direct method with Cholesky factorization':'direct','Least Squares QR':'lsqr','K-space deconvolution':'kspace','Simultaneous Iterative Reconstruction Technique':'sirt','MRNSD':'mrnsd','Richardson-Lucy':'rl'
}

PLUGIN_ARGS = {
	"general":{
		"lib_folder":{
			"label":"LF Analyze Folder","default":"","help":"Select you LF Analyze Library folder."
		},
		"lib_ver_label":{
			"label":"LF Analyze Ver:","default":"","help":"LF Analyze Library version."
		},
		"img_folder":{
			"label":"Input Image Folder","default":examples_folder,"help":"Select your dataset folder containing the raw light-field image(s)."
		},
		"metadata_file":{
			"default":"metadata.txt","label":"Metadata file","help":"Select the name of the metadata file that will be produced for the dataset."
		},
		"logo_label":{
			"label":f'<a href="https://chanzuckerberg.com/science/programs-resources/imaging/napari/light-field-imaging-plugin/"><img src="{logo_img}"></a>', "help":"LF Analyze About WebPage"
		},
		"status":{
			"label":"STATUS:", "value":"== IDLE ==", "value_busy":"== BUSY ==", "value_idle":"== IDLE ==", "value_error":"== ERROR =="
		}
	},
	"hw":{
		"gpu_id":{
			"prop":"--gpu-id","dest":"gpu_id","type":"int","default":int(os.environ.get('USE_GPU_ID', 0)),"help":"Force lfdeconvolve to use a specific GPU on your system. If not supplied this will default to $USE_GPU_ID or 0), if --gpu-id is not supplied it will default to the value of the USE_GPU_ID environment variable, if set, or 0 otherwise."
		},
		"platform_id":{
			"prop":"--platform-id","label":"Select Platform","dest":"platform_id","type":"int","default":0,"help":"Force lfdeconvolve to use a specific OpenCL Platform on your system."
		},
		"use_single_prec":{
			"prop":"--use-single-precision","label":"Use Single Precision","action":"store_true","dest":"use_sing_prec","default":False,"help":"Use single precision float instead of double."
		},
		"disable_gpu":{
			"prop":"--disable-gpu","action":"store_true","label":"Disable GPU","dest":"disable_gpu","type":"bool","default":False,"help":"Disable GPU deconvolution and use software implementation instead."
		}
	},
	"calibrate":{
	# ===============================
	# ======= Calibrate =============
	# ===============================
		"output_filename":{
			"prop_short":"-o","prop":"--output-filename","label":"Calibration File","default":"calibration.lfc","dest":"output_filename","help":"Specify the name of the calibration file.","type":"str","cat":"required","img_folder_file":True
		},
		"synthetic_lf":{
			"prop":"--synthetic","label":"Synthetic LF","action":"store_true","dest":"synthetic_lf","default":False,"help":"Use this option to create a synthetic light field (i.e. with no calibration image","type":"bool"
		},
		"use_ray_optics":{
			"prop":"--use-ray-optics","label":"Use Ray Optics","action":"store_true","dest":"use_ray_optics","default":False,"help":"Use the less accurate ray optics model rather than wave optics model.","type":"bool"
		},
		"voxels_as_points":{
			"prop":"--voxels-as-points","label":"Use Voxels As Points","action":"store_true","dest":"voxels_as_points","default":False,"help":"Treat each voxel as an ideal point source. This turns of numerical integration that gives the voxel spatial extent (which can be important for anti-aliasing).","type":"bool"
		},
		# Calibration routine parameters
		"dark_frame_file":{
			"prop":"--dark-frame","label":"Dark Frame Image","dest":"dark_frame_file","default":"dark_frame.tif","type":"str","help":"Specify a dark frame image to subtract from the input light-field before processing (This makes radiometric calibration more accurate).","cat":"required","img_folder_file":True
		},
		"radiometry_frame_file":{
			"prop":"--radiometry-frame","label":"Radiometry Image","dest":"radiometry_frame_file","type":"str","default":"radiometry_frame.png","help":"Specify a radiometry frame to use for radiometric correction. If no frame is specified, then no radiometric correction is carried out.","cat":"required","img_folder_file":True
		},
		"align_radiometry":{
			"prop":"--align-radiometry","label":"Align Radiometry","action":"store_true","dest":"align_radiometry","type":"bool","default":False,"help":"Align the radiometry image automatically to the geometric calibration image. (Use this option when the radiometry frame has been \"bumped\" before imaging begins)."
		},
		 # Optical parameters
		"ulens_pitch":{
			"prop":"--pitch","label":"Microlens Pitch (um)","dest":"ulens_pitch","type":"float","default":125,"help":"Specify the microlens pitch (in microns).","cat":"required"
		},
		"pixel_size":{
			"prop":"--pixel-size","label":"Pixel Size (um)","dest":"pixel_size","type":"float","default":4.55,"help":"Specify the size of a pixel on the sensor taking magnification due to relay optics into account (in microns).","cat":"required"
		},	
		"ulens_focal_length":{
			"prop":"--focal-length","label":"Microlens Focal Length (um)","dest":"ulens_focal_length","type":"float","default":2433,"help":"Specify the microlens focal length (in microns).","cat":"required","max":5000
		},
		"ulens_focal_distance":{
			"prop":"--ulens-focal-distance","label":"Microlens Focal Distance (um)","dest":"ulens_focal_distance","type":"float","default":2433,"help":"Specify the microlens focal distance (in microns). If you do not specify a value it is assumed that the focal distance is equal to the focal length.","max":5000
		},
		"objective_magnification":{
			"prop":"--magnification","label":"Objective Magnification","dest":"objective_magnification","type":"int","default":20,"help":"Specify the objective magnification.","cat":"required"
		},
		"objective_na":{
			"prop":"--na","label":"Objective NA","dest":"objective_na","type":"float","default":0.5,"help":"Specify the objective numerical aperture.","cat":"required"
		},
		"tubelens_focal_length":{
			"prop":"--tubelens-focal-length","label":"Tunelens Focal Length (mm)","dest":"tubelens_focal_length","type":"float","default":180.0,"help":"Tube lens focal length (in millimeters).","cat":"required"
		},
		"center_wavelength":{
			"prop":"--wavelength","label":"Center Wavelength (nm)","dest":"center_wavelength","type":"float","default":510,"help":"Center wavelength of emission spectrum of the sample (nm).","cat":"required"
		},
		"medium_index":{
			"prop":"--medium-index","label":"Medium Index","dest":"medium_index","type":"float","default":1.33,"help":"Set the index of refraction of the medium.","cat":"required"
		},
		"ulens_fill_factor":{
			"prop":"--ulens-fill-factor","label":"Microlens Fill Factor","dest":"ulens_fill_factor","type":"float","default":1.0,"help":"Specify the microlens fill factor (e.g. 1.0, 0.7, ...)."
		},
		"pixel_fill_factor":{
			"prop":"--pixel-fill-factor","label":"Pixel Fill Factor","dest":"pixel_fill_factor","type":"float","default":1.0,"help":"Specify the pixel fill factor (e.g. 1.0, 0.7, ...)."
		},
		"ulens_profile":{
			"prop":"--ulens-profile","label":"Microlens Profile","dest":"ulens_profile","default":'rect',"options":['rect','circ'],"type":"sel","help":"Specify the shape of the microlens apertures. Options include: ['rect', 'circ']"
		},
		# Geometric calibration Options
		"affine_alignment":{
			"prop":"--affine-alignment","action":"store_true","dest":"affine_alignment","type":"bool","default":False,"help":"Use affine warp for correcting geometric distortion (default is cubic)."
		},
		"isometry_alignment":{
			"prop":"--isometry-alignment","action":"store_true","dest":"isometry_alignment","type":"bool","default":False,"help":"Use isometry warp for correcting geometric distortion (default is cubic)."
		},
		"chief_ray_image":{
			"prop":"--chief-ray","action":"store_true","dest":"chief_ray_image","type":"bool","default":False,"help":"Use this flag to indicate that the calibration frame is a chief ray image."	
		},
		# Synthetic parameters
		"ns":{
			"prop":"--ns","dest":"ns","type":"int","default":50,"help":"Set the lenslets in s direction."
		},
		"nt":{
			"prop":"--nt","dest":"nt","type":"int","default":50,"help":"Set the lenslets in t direction."
		},
		# Other Options
		"crop_center_lenslets":{
			"prop":"--crop-center-lenslets","action":"store_true","dest":"crop_center_lenslets","type":"bool","default":False,"help":"For severe aperture vignetting (high NA objectives)	 use only center lenslets for calibration and extrapolate outwards."
		},
		"skip_alignment":{
			"prop":"--skip-alignment","action":"store_true","dest":"skip_alignment","type":"bool","default":False,"help":"Skip the alignment step during geometric calibration (useful if you are working with an already-rectified light field or a synthetic light field."
		},
		"skip_subpixel_alignment":{
			"prop":"--skip-subpixel-alignment","action":"store_true","dest":"skip_subpixel_alignment","type":"bool","default":False,"help":"Skip subpixel alignment for determining lenslet centers."
		},
		"num_threads":{
			"prop":"--num-threads","label":"Number of CPU threads","dest":"num_threads","type":"int","default":10,"help":"Set the number of CPU threads to use when generating the raydb."
		},
		"pinhole_filename":{
			"prop":"--pinhole","dest":"pinhole_filename","type":"str","default":"","help":"After calibrating save the rectified light field as a rectified sub-aperture image."
		},
		"lenslet_filename":{
			"prop":"--lenslet","dest":"lenslet_filename","type":"str","default":"","help":"After calibrating save the rectified light field as a rectified lenslet image."
		},
		"debug":{
			"prop_short":"-d","prop":"--debug","action":"store_true","dest":"debug","type":"bool","default":False,"help":"Save debug images."
		}
	},
	"rectify":{
	# ===============================
	# ========== Rectify ============
	# ===============================
		"output_pixels_per_lenslet":{
			"prop_short":"-p","prop":"--output-pixels-per-lenslet","dest":"output_pixels_per_lenslet","type":"str","default":"","help":"Specify the number of pixels per lenslet in the output image."
		},
		"output_filename":{
			"prop_short":"-o","prop":"--output-file","label":"Rectified Image","dest":"output_filename","type":"str","default":"rectified.png","help":"Specify the output filename.","cat":"required","img_folder_file":True
		},
		"calibration_file":{
			"prop_short":"-c","prop":"--calibration-file","label":"Calibration File","dest":"calibration_file","type":"str","default":"calibration.lfc","help":"Specify the calibration file to use for rectification.","cat":"required","img_folder_file":True
		},
		"subaperture":{
			"prop_short":"-s","prop":"--subaperture","action":"store_true","dest":"subaperture","type":"bool","default":False,"help":"Save out the light field image as tiled subapertures."
		}
	},
	"deconvolve":{
	# ===============================
	# ======= Deconvolve ============
	# ===============================
		"input_file":{
			"prop":"input_file","label":"Light Field Image","dest":"input_file","type":"str","default":"light_field.png","help":"You must supply at least one light field image to deconvolve.","cat":"required","img_folder_file":True,"exclude_from_args":True
		},
		"output_filename":{
			"prop_short":"-o","prop":"--output-file","label":"Output Image Stack","dest":"output_filename","type":"str","default":"output_stack.tif","help":"Specify the output filename.","cat":"required","img_folder_file":True
		},
		"calibration_file":{
			"prop_short":"-c","prop":"--calibration-file","label":"Calibration File","dest":"calibration_file","type":"str","default":"calibration.lfc","help":"Specify the calibration file to use for rectification.","cat":"required","img_folder_file":True
		},
		"private_fn":{
			"prop":"--private-key","dest":"private_fn","type":"file","default":os.path.join(os.path.dirname(os.path.abspath(__file__)), 'enlightenment_c3'),"help":"Specify the private key file for remote transfers."
		},
		"cov_directory":{			
			"prop":"--cov-directory","dest":"cov_directory","type":"str","default":"","help":"Specify the directory where ADMM covariance matrices are saved."	
		},
		# Volume parameters
		"num_slices":{
			"prop":"--num-slices","label":"Number of Slices","dest":"num_slices","type":"int","default":5,"help":"Set the number of slices to produce in the output stacks.","cat":"required","exclude_from_args":True
		},
		"um_per_slice":{
			"prop":"--um-per-slice","label":"um per Slice","dest":"um_per_slice","type":"float","default":5.0,"help":"Set the thickness of each slice (in um).","cat":"required","exclude_from_args":True
		},
		"z_center":{
			"prop":"--z-center","label":"Central z-slice Offset (um)","dest":"z_center","type":"float","default":0.0,"help":"Set the offset for the central z slice (in um)."
		},
		"supersample":{
			"prop":"--supersample","label":"Supersample","dest":"supersample","type":"int","default":4,"help":"Supersample the light field volume. This results in a higher resolution reconstruction up to a point and interpolation after that point.","cat":"required","exclude_from_args":True
		},
		# Algorithm selection	
		"solver":{
			"prop":"--solver","dest":"solver","type":"sel","default":"rl",
			"options":[SOLVER_OPTIONS[key] for key in SOLVER_OPTIONS],
			"help":"Available reconstruction methods are: \nApproximate Message Passing (with optional multiscale denoising (\'amp\')\nAlternating Direction Method of Multipliers with Huber loss (\'admm_huber\')\nAlternating Direction Method of Multipliers with TV penalty (\'admm_tv\')\nConjugate Gradient (\'cg\')\nDirect method with Cholesky factorization (\'direct\')\nLeast Squares QR (\'lsqr\')\nK-space deconvolution (\'kspace\')\nSimultaneous Iterative Reconstruction Technique (\'sirt\')\nMRNSD (\'mrnsd\')\nand Richardson-Lucy (\'rl\'). Default is currently \'rl\'."
		},
		# Algorithm-specific parameters							
		"alpha":{
			"prop":"--alpha","dest":"alpha","type":"float","default":1.6,"help":"Relaxation parameter for SIRT-based iterative reconstruction."
		},
		"multiscale_smoothing":{				
			"prop":"--multiscale-smoothing","dest":"multiscale_smoothing","action":"store_true","type":"bool","default":False,"help":"Multiscale regularization option for AMP reconstruction."
		},
		"save_multiscale":{
			"prop":"--save-multiscale","dest":"save_multiscale","action":"store_true","type":"bool","default":False,"help":"Save multilevel decomposition of data."
		},
		# Generic parameters for iterative reconstruction routines"							
		"regularization_lambda":{
			"prop":"--lambda","dest":"regularization_lambda","type":"float","default":0.0,"help":"Regularization coefficient (behavior varies by reconstruction algorithm)"
		},
		"regularization_lambda2":{
			"prop":"--lambda2","dest":"regularization_lambda2","type":"float","default":0.0,"help":"Additional regularization coefficient. (Behavior varies by algorithm	 and not all algorithms use two regularization coefficients.)"
		},
		"max_iter":{
			"prop":"--max-iter","dest":"max_iter","type":"int","default":15,"help":"Maximum number of iterations for SIRT-based reconstruction."
		},
		"conv_thresh":{
			"prop":"--convergence-threshold","dest":"conv_thresh","type":"float","default":0.0,"help":"Convergence criteria threshold, d/dt (MSE). Try 5e-5 for SIRT, 1e-2 for TV."
		},
		# Noise model parameters							
		"readnoise_variance":{
			"prop":"--readnoise-variance","dest":"readnoise_variance","type":"float","default":0.0,"help":"Set the variance of the (measured) camera read noise."
		},
		"background_level":{					
			"prop":"--background-level","dest":"background_level","type":"float","default":1.0,"help":"Set the (measured) background level of the image."
		},
		# Assorted other parameters							
		"focalstack":{
			"prop":"--focalstack","action":"store_true","dest":"focalstack","type":"bool","default":False,"help":"Turn off deconvolution and simply save a focal stack to disk."
		},
		"remove_grid":{
			"prop":"--remove-grid","action":"store_true","dest":"remove_grid","type":"bool","default":False,"help":"Remove grid artifacts in light field image using spectral median filter."
		},
		"pinhole_filename":{
			"prop":"--pinhole-file","dest":"pinhole_filename","default":"","type":"str","help":"After deconvolution  save out a deconvolved light field sub-aperture image.","img_folder_file":True
		},
		"decon_type":{
			"prop":"--deconvolution-type","dest":"decon_type","default":'algebraic',"options":['algebraic','direct','admm'],"type":"sel","help":"Choose deconvolution method. One of [algebraic, direct, admm]."
		},
		"reg_factor":{
			"prop":"--reg-factor","dest":"reg_factor","type":"float","default":100,"help":"Regularization parameter used in ADMM."
		},
		"h5py_cov_filename":{
			"prop":"--h5py-cov-filename","dest":"h5py_cov_filename","default":'tests/covariance_blocks.h5',"type":"str","help":"Specify the HDF5 covariance filename."
		},
		"direct_type":{
			"prop":"--direct-type","dest":"direct_type","default":"covariance","type":"str","help":"If --direct flag is set to True specifies whether the covariance or projection matrix method is used."
		},
		"benchmark":{
			"prop":"--benchmark","action":"store_true","dest":"benchmark","type":"bool","default":False,"help":"Compare the CPU and GPU speeds for forward & back porjection operations."
		},
		"test":{
			"prop":"--test","dest":"test","type":"int","default":1,"help":"Select a unit test (1-4)."
		},
		"log_convergence":{
			"prop":"--log-convergence","action":"store_true","dest":"log_convergence","type":"bool","default":False,"help":"For logging convergence details."
		}
	}
}