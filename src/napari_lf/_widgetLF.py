import os, sys, json
from pathlib import Path
import napari
from napari.qt.threading import thread_worker
from qtpy.QtWidgets import QWidget, QHBoxLayout, QScrollArea
from magicgui.widgets import Container, FileEdit, Label, LineEdit, FloatSpinBox, PushButton, CheckBox, SpinBox, Slider
from napari_lf.lfa import lfcalibrate, lfdeconvolve, lfrectify

# Method 1: As Napari plugin
class LFQWidget(QWidget):
		
	def __init__(self, napari_viewer):
		super().__init__()
		self.viewer = napari_viewer
		self.args_cal_std = [
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

		self.args_decon_std = [
			"light_field.png",
			"-c",
			"calibration.lfc",
			"-o",
			"antleg_stack.tif",
			"--solver",
			"rl",
			# "--use-single-precision"
		]

		self.args_rec_std = [
			"light_field.png",
			"-c",
			"calibration.lfc",
			"-o",
			"rectified.png"
		]

		self.new_args_decon = self.args_decon_std
		self.new_args_cal = self.args_cal_std
		self.new_args_rec = self.args_rec_std
			
		#LFANALYZE
		self.currentdir = os.path.dirname(os.path.realpath(__file__))
		self.folder_lfa = FileEdit(value=self.currentdir, label='LF Analyze Folder', mode='d', enabled=False)
		self.widget_lfa = Container(name='LF Analyze', widgets=[self.folder_lfa])
		
		#INPUTS
		# label_input = Label(value='Inputs')
		self.folder_path1 = FileEdit(value='', label='Input Image Folder', mode='d')
		self.img_lf = LineEdit(value=self.args_decon_std[0], label='Light Field Image')
		self.img_radio = LineEdit(value=self.args_cal_std[0], label='Radiometry Image')
		self.img_dark_frame = LineEdit(value=self.args_cal_std[4], label='Dark Frame Image')
		self.db_lfc = LineEdit(value=self.args_cal_std[28], label='LFC Database')
		self.widget_inputs = Container(name='Inputs', widgets=[self.folder_path1, self.img_lf, self.img_radio, self.img_dark_frame, self.db_lfc])

		#OUTPUTS
		# label_output = Label(value='Outputs')
		# folder_path2 = FileEdit(value='', label='Output Folder', mode='d')
		self.img_stack = LineEdit(value=self.args_decon_std[4], label='Output stack')
		self.img_rect = LineEdit(value=self.args_rec_std[4], label='Rectified Image')
		self.meta_txt = LineEdit(value='metadata.txt', label='Metadata file')
		self.widget_outputs = Container(name='Outputs', widgets=[self.img_stack, self.img_rect, self.meta_txt])

		#PARAMETERS
		# label_params = Label(value='Parameters')
		self.pixel_size = FloatSpinBox(value=self.args_cal_std[6], label='Pixel Size', step=0.01)
		self.pitch = SpinBox(value=self.args_cal_std[8], label='Pitch', step=1)
		self.focal_length = SpinBox(value=self.args_cal_std[10], label='Focal Length', step=1, max=5000)
		self.magnification = SpinBox(value=self.args_cal_std[12], label='Magnification', step=1)
		self.num_aper = FloatSpinBox(value=self.args_cal_std[14], label='NA', step=0.1)
		self.tfl = FloatSpinBox(value=self.args_cal_std[16], label='Tubelens Focal Length', step=1)
		self.wavelength = FloatSpinBox(value=self.args_cal_std[18], label='Wavelength', step=1)
		self.medium_index = FloatSpinBox(value=self.args_cal_std[20], label='Medium Index', step=0.01)
		self.num_slices = SpinBox(value=self.args_cal_std[22], label='Number of Slices', step=1)
		self.um_per_slice = FloatSpinBox(value=self.args_cal_std[24], label='um per slice', step=0.1)
		self.supersample = SpinBox(value=self.args_cal_std[26], label='Supersample', step=1)
		self.use_single_prec = CheckBox(label='Use Single Precision')
		self.status = Label(value='== IDLE ==', label='STATUS:')

		self.widget_params = Container(name='Parameters', widgets=[self.pixel_size, self.pitch, self.focal_length, self.magnification, self.num_aper, self.tfl, self.wavelength, self.medium_index, self.num_slices, self.um_per_slice, self.supersample, self.use_single_prec])

		#EXECUTE
		self.btn_cal = PushButton(name='Calibrate', annotation=None, label='Calibrate')
		self.btn_rec = PushButton(name='Rectify', annotation=None, label='Rectify')
		self.btn_dec = PushButton(name='Deconvolve', annotation=None, label='Deconvolve')
		
		self.widget_btns = Container(name='Execute', widgets=[self.btn_cal, self.btn_rec, self.btn_dec, self.status])

		#APP
		self.widget_main = Container(name='LFAnalyze', annotation=None, label='LFAnalyze', tooltip=None, visible=None, enabled=True, gui_only=False, backend_kwargs={}, layout='vertical', widgets=(self.widget_inputs, self.widget_outputs, self.widget_params, self.widget_btns), labels=True)
		
		@self.folder_path1.changed.connect
		def folder_path1_call():
			bool = self.read_meta()
			if bool:
				self.refresh_fields()
				
		def set_status(vals):
			self.status.value = vals[0]
			
			if vals[1] == 'dec':
				self.display_proc_image()
			
		@self.btn_cal.changed.connect
		def btn_cal_call():
			self.status.value = '== BUSY =='
			self.combine_args()
			# print(self.new_args_cal)
			worker = self.run_lfcalibrate(self.new_args_cal)  # create "worker" object
			worker.returned.connect(set_status)  # connect callback functions
			worker.start()
			
		@self.btn_rec.changed.connect
		def btn_rec_call():
			self.status.value = '== BUSY =='
			self.combine_args()
			# print(self.new_args_rec)
			worker = self.run_lfrectify(self.new_args_rec)
			worker.returned.connect(set_status)
			worker.start()
			
		@self.btn_dec.changed.connect
		def btn_dec_call():
			self.status.value = '== BUSY =='
			self.combine_args()
			# print(self.new_args_decon)
			worker = self.run_lfdeconvolve(self.new_args_decon)
			worker.returned.connect(set_status)
			worker.start()
		
		#Layout
		layout = QHBoxLayout()
		self.setLayout(layout)
		
		self.scroll = QScrollArea()
		 #Scroll Area Properties
		self.scroll.setWidgetResizable(True)
		self.scroll.setWidget(self.widget_main.native)
		self.layout().addWidget(self.scroll)
		
		# self.layout().addWidget(self.widget_main.native)
			
	def display_proc_image(self):
		self.viewer.open(self.new_args_decon[4], stack=True)
		
	def combine_args(self):
		self.new_args_decon = self.args_decon_std[0:7]
		self.new_args_cal = self.args_cal_std[0:29]
		self.new_args_rec = self.args_rec_std[0:5]
		
		self.new_args_decon[0] = os.path.join(self.folder_path1.value, self.img_lf.value)
		self.new_args_decon[2] = os.path.join(self.folder_path1.value, self.db_lfc.value)
		self.new_args_decon[4] = os.path.join(self.folder_path1.value, self.img_stack.value)
		
		self.new_args_rec[0] = os.path.join(self.folder_path1.value, self.img_lf.value)
		self.new_args_rec[2] = os.path.join(self.folder_path1.value, self.db_lfc.value)
		self.new_args_rec[4] = os.path.join(self.folder_path1.value, self.img_rect.value)
		
		self.new_args_cal[0] = os.path.join(self.folder_path1.value, self.img_radio.value)
		self.new_args_cal[2] = os.path.join(self.folder_path1.value, self.img_radio.value)
		self.new_args_cal[4] = os.path.join(self.folder_path1.value, self.img_dark_frame.value)
		
		self.new_args_cal[6] = str(self.pixel_size.value)
		self.new_args_cal[8] = str(self.pitch.value)
		self.new_args_cal[10] = str(self.focal_length.value)
		self.new_args_cal[12] = str(self.magnification.value)
		self.new_args_cal[14] = str(self.num_aper.value)
		self.new_args_cal[16] = str(self.tfl.value)
		self.new_args_cal[18] = str(self.wavelength.value)
		self.new_args_cal[20] = str(self.medium_index.value)
		self.new_args_cal[22] = str(self.num_slices.value)
		self.new_args_cal[24] = str(self.um_per_slice.value)
		self.new_args_cal[26] = str(self.supersample.value)
		self.new_args_cal[28] = os.path.join(self.folder_path1.value, self.db_lfc.value)
		if self.use_single_prec.value == True:
			self.new_args_cal.append('--use-single-precision')
			self.new_args_decon.append('--use-single-precision')
			
		# self.load_lf()
		self.write_meta()
			
	def load_lf(self):
		print('LFA Folder', self.folder_lfa.value)
		# sys.path.append(folder_lfa.value)
		# sys.path.append(os.path.join(folder_lfa.value, 'lflib'))
		sys.path.insert(0, self.folder_lfa.value)
		sys.path.insert(0, os.path.join(self.folder_lfa.value, 'lflib'))
		# from napari_lf.lfa import lfcalibrate, lfdeconvolve, lfrectify
		
	@thread_worker
	def run_lfcalibrate(self, args):
		# currentdir = os.path.dirname(os.path.realpath(__file__))
		# grandparentdir = os.path.dirname(os.path.dirname(currentdir))
		# sys.path.append(folder_lfa.value)
		# from lfcalibrate import main
		lfcalibrate.main(args)
		return ('== IDLE ==','cal')
		
	@thread_worker
	def run_lfrectify(self, args):
		# currentdir = os.path.dirname(os.path.realpath(__file__))
		# grandparentdir = os.path.dirname(os.path.dirname(currentdir))
		# sys.path.append(folder_lfa.value)
		# from lfrectify import main
		lfrectify.main(args)
		return ('== IDLE ==','rec')
		
	@thread_worker
	def run_lfdeconvolve(self, args):
		# currentdir = os.path.dirname(os.path.realpath(__file__))
		# grandparentdir = os.path.dirname(os.path.dirname(currentdir))
		# sys.path.append(folder_lfa.value)
		# from lfdeconvolve import main
		lfdeconvolve.main(args)		
		return ('== IDLE ==', 'dec')
				
	def write_meta(self):
		data = {'new_args_cal':self.new_args_cal, 'new_args_decon':self.new_args_decon, 'new_args_rec':self.new_args_rec}
		with open(os.path.join(self.folder_path1.value, self.meta_txt.value), 'w') as outfile:
			json.dump(data, outfile)
			
	def read_meta(self):
		path = Path(os.path.join(self.folder_path1.value, self.meta_txt.value))
		if path.is_file():
			with open(os.path.join(self.folder_path1.value, self.meta_txt.value)) as json_file:
				data = json.load(json_file)
				self.new_args_cal = (data['new_args_cal'])
				# print(self.new_args_cal)
				self.new_args_decon = (data['new_args_decon'])
				# print(self.new_args_decon)
				self.new_args_rec = (data['new_args_rec'])
				# print(self.new_args_rec)
			return True
		else:
			return False

	def refresh_fields(self):
		self.img_lf.value = os.path.basename(self.new_args_decon[0])
		self.db_lfc.value = os.path.basename(self.new_args_decon[2])
		self.img_stack.value = os.path.basename(self.new_args_decon[4])
		self.img_rect.value = os.path.basename(self.new_args_rec[4])
		self.img_radio.value = os.path.basename(self.new_args_cal[2])
		self.img_dark_frame.value = os.path.basename(self.new_args_cal[4])
		
		self.pixel_size.value = float(self.new_args_cal[6])
		self.pitch.value = int(self.new_args_cal[8])
		self.focal_length.value = int(self.new_args_cal[10])
		self.magnification.value = int(self.new_args_cal[12])
		self.num_aper.value = float(self.new_args_cal[14])
		self.tfl.value = float(self.new_args_cal[16])
		self.wavelength.value = float(self.new_args_cal[18])
		self.medium_index.value = float(self.new_args_cal[20])
		self.num_slices.value = int(self.new_args_cal[22])
		self.um_per_slice.value = float(self.new_args_cal[24])
		self.supersample.value = int(self.new_args_cal[26])
		
		self.use_single_prec.value = False
		if (len(self.new_args_cal) >= 30 and self.new_args_cal[29] == '--use-single-precision') or (len(self.new_args_decon) >= 8 and self.new_args_decon[7] == '--use-single-precision'):
			self.use_single_prec.value = True

# Method 2: As stand-alone application
# widget_main.show(run=True)

# Method 3: As Napari viewer
# viewer = napari.Viewer()
# viewer.window.add_dock_widget(widget_main)
# napari.run()
	