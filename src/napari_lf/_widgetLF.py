import os, sys
import napari
from magicgui.widgets import Container, FileEdit, Label, LineEdit, FloatSpinBox, PushButton, CheckBox, SpinBox
from qtpy.QtWidgets import QWidget, QHBoxLayout

args_cal_std = [
	"radiometry_frame.png",
	"--radiometry-frame",
	"radiometry_frame.png",
	"--dark-frame",
	"dark_frame.tif",
	"--pixel-size",
	"4.55",
	"--pitch",
	"125",
	"--focal-length",
	"2433",
	"--magnification",
	"20",
	"--na",
	"0.5",
	"--tubelens-focal-length",
	"180.0",
	"--wavelength",
	"510",
	"--medium-index",
	"1.33",
	"--num-slices",
	"5",
	"--um-per-slice",
	"5.0",
	"--supersample",
	"4",
	"-o",
	"calibration.lfc",
	# "--use-single-precision"
]

args_decon_std = [
	"light_field.png",
	"-c",
	"calibration.lfc",
	"-o",
	"antleg_stack.tif",
	"--solver",
	"rl",
	# "--use-single-precision"
]

args_rec_std = [
	"light_field.png",
	"-c",
	"calibration.lfc",
	"-o",
	"rectified.png"
]

new_args_decon = args_decon_std
new_args_cal = args_cal_std
new_args_rec = args_rec_std
	
#LFANALYZE
currentdir = os.path.dirname(os.path.realpath(__file__))
folder_lfa = FileEdit(value=currentdir, label='LF Analyze Folder', mode='d')
widget_lfa = Container(name='LF Analyze', widgets=[folder_lfa])

#INPUTS
# label_input = Label(value='Inputs')
folder_path1 = FileEdit(value='', label='Input Image Folder', mode='d')
img_lf = LineEdit(value=args_decon_std[0], label='Light Field Image')
img_radio = LineEdit(value=args_cal_std[0], label='Radiometry Image')
img_dark_frame = LineEdit(value=args_cal_std[4], label='Dark Frame Image')
db_lfc = LineEdit(value=args_cal_std[28], label='LFC Database')
widget_inputs = Container(name='Inputs', widgets=[folder_path1, img_lf, img_radio, img_dark_frame, db_lfc])

#OUTPUTS
# label_output = Label(value='Outputs')
# folder_path2 = FileEdit(value='', label='Output Folder', mode='d')
img_stack = LineEdit(value=args_decon_std[4], label='Output stack')
img_rect = LineEdit(value=args_rec_std[4], label='Rectified Image')
widget_outputs = Container(name='Outputs', widgets=[img_stack, img_rect])

#PARAMETERS
# label_params = Label(value='Parameters')
pixel_size = FloatSpinBox(value=args_cal_std[6], label='Pixel Size', step=0.01)
pitch = SpinBox(value=args_cal_std[8], label='Pitch', step=1)
focal_length = SpinBox(value=args_cal_std[10], label='Focal Length', step=1, max=5000)
magnification = SpinBox(value=args_cal_std[12], label='Magnification', step=1)
num_aper = FloatSpinBox(value=args_cal_std[14], label='NA', step=1)
tfl = FloatSpinBox(value=args_cal_std[16], label='Tubelens Focal Length', step=1)
wavelength = SpinBox(value=args_cal_std[18], label='Wavelength', step=1)
medium_index = FloatSpinBox(value=args_cal_std[20], label='Medium Index', step=1)
num_slices = SpinBox(value=args_cal_std[22], label='Number of Slices', step=1)
um_per_slice = FloatSpinBox(value=args_cal_std[24], label='um per slice', step=1)
supersample = SpinBox(value=args_cal_std[26], label='Supersample', step=1)
use_single_prec = CheckBox(label='Use Single Precision')

widget_params = Container(name='Parameters', widgets=[pixel_size, pitch, focal_length, magnification, num_aper, tfl, wavelength, medium_index, num_slices, um_per_slice, supersample, use_single_prec])

#EXECUTE
btn_cal = PushButton(name='Calibrate', annotation=None, label='Calibrate')
btn_rec = PushButton(name='Rectify', annotation=None, label='Rectify')
btn_dec = PushButton(name='Deconvolve', annotation=None, label='Deconvolve')

@btn_cal.changed.connect
def btn_cal_call():
	combine_args()
	print(new_args_cal)
	run_lfcalibrate(new_args_cal)
	print('==Done==')
	
@btn_rec.changed.connect
def btn_rec_call():
	combine_args()
	print(new_args_rec)
	run_lfrectify(new_args_rec)
	print('==Done==')
	
@btn_dec.changed.connect
def btn_dec_call():
	combine_args()
	print(new_args_decon)
	run_lfdeconvolve(new_args_decon)
	print('==Done==')
	
def combine_args():
	new_args_decon = args_decon_std
	new_args_cal = args_cal_std
	new_args_rec = args_rec_std
	
	new_args_decon[0] = os.path.join(folder_path1.value, img_lf.value)
	new_args_decon[2] = os.path.join(folder_path1.value, db_lfc.value)
	new_args_decon[4] = os.path.join(folder_path1.value, img_stack.value)
	
	new_args_rec[0] = os.path.join(folder_path1.value, img_lf.value)
	new_args_rec[2] = os.path.join(folder_path1.value, db_lfc.value)
	new_args_rec[4] = os.path.join(folder_path1.value, img_rect.value)
	
	new_args_cal[0] = os.path.join(folder_path1.value, img_radio.value)
	new_args_cal[2] = os.path.join(folder_path1.value, img_radio.value)
	new_args_cal[4] = os.path.join(folder_path1.value, img_dark_frame.value)
	
	new_args_cal[6] = str(pixel_size.value)
	new_args_cal[8] = str(pitch.value)
	new_args_cal[10] = str(focal_length.value)
	new_args_cal[12] = str(magnification.value)
	new_args_cal[14] = str(num_aper.value)
	new_args_cal[16] = str(tfl.value)
	new_args_cal[18] = str(wavelength.value)
	new_args_cal[20] = str(medium_index.value)
	new_args_cal[22] = str(num_slices.value)
	new_args_cal[24] = str(um_per_slice.value)
	new_args_cal[26] = str(supersample.value)
	new_args_cal[28] = os.path.join(folder_path1.value, db_lfc.value)
	if use_single_prec.value == True:
		new_args_cal.append('--use-single-precision')
		new_args_decon.append('--use-single-precision')
		
def run_lfcalibrate(args):
	# currentdir = os.path.dirname(os.path.realpath(__file__))
	# grandparentdir = os.path.dirname(os.path.dirname(currentdir))
	sys.path.append(folder_lfa.value)
	from lfcalibrate import main
	main(args)
	
def run_lfrectify(args):
	# currentdir = os.path.dirname(os.path.realpath(__file__))
	# grandparentdir = os.path.dirname(os.path.dirname(currentdir))
	sys.path.append(folder_lfa.value)
	from lfrectify import main
	main(args)
	
def run_lfdeconvolve(args):
	# currentdir = os.path.dirname(os.path.realpath(__file__))
	# grandparentdir = os.path.dirname(os.path.dirname(currentdir))
	sys.path.append(folder_lfa.value)
	from lfdeconvolve import main
	main(args)
	viewer.open(new_args_decon[4], stack=True)

#APP
widget_main = Container(name='LFAnalyze', annotation=None, label='LFAnalyze', tooltip=None, visible=None, enabled=True, gui_only=False, backend_kwargs={}, layout='vertical', widgets=(widget_lfa, widget_inputs, widget_outputs, widget_params, btn_cal, btn_rec, btn_dec), labels=True)

# Method 1: As Napari plugin
class LFQWidget:
	def __init__(self, napari_viewer):
		super().__init__()
		self.viewer = napari_viewer
		self.viewer.window.add_dock_widget(widget_main)
		
# class LFQWidget(QWidget):
	# your QWidget.__init__ can optionally request the napari viewer instance
	# in one of two ways:
	# 1. use a parameter called `napari_viewer`, as done here
	# 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
	# def __init__(self, napari_viewer):
		# super().__init__()
		# self.viewer = napari_viewer
		# self.setLayout(QHBoxLayout())
		# self.layout().addWidget(widget_main)

# Method 2: As stand-alone application
# widget_main.show(run=True)

# Method 3: As Napari viewer
# viewer = napari.Viewer()
# viewer.window.add_dock_widget(widget_main)
# napari.run()