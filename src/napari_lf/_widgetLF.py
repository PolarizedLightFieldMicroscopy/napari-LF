import os, sys, traceback
from pathlib import Path
import napari
from napari.qt.threading import thread_worker
from qtpy import QtCore, QtGui
from qtpy.QtCore import Qt
from qtpy.QtWidgets import *
from magicgui.widgets import *

# Fix for the QPixMap error
# https://github.com/PolarizedLightFieldMicroscopy/napari-LF/issues/29
app = QApplication([])

try:
	from napari_lf import _widgetLF_gui as LFgui
	from napari_lf import _widgetLF_vals as LFvals
except:
	import _widgetLF_gui as LFgui
	import _widgetLF_vals as LFvals
	
try:
	from napari_lf.lfa import lfcalibrate, lfdeconvolve, lfrectify, lfproject
	from napari_lf.lfa import lflib
except:
	from lfa import lfcalibrate, lfdeconvolve, lfrectify, lfproject
	from lfa import lflib
	

# from lfd.settings import Settings
# from lfd import display

METHOD = LFvals.METHODS[0]

# Method 1: As Napari plugin
class LFQWidget(QWidget):
		
	def __init__(self, napari_viewer):
		super().__init__()
		self.lfa_args = {}
		self.viewer = napari_viewer
		self.method = METHOD
		self.lfcalibrate = None
		self.lfdeconvolve = None
		self.lfrectify = None
		self.lfproject = None
		self.lflib = None
		self.lflib_ver = ''
		self.lflib_ext = False
		self.currentdir = os.path.dirname(os.path.realpath(__file__))
		self.gui = None
		#Get and Set Prefs
		self.gui = LFgui.LFQWidgetGui()
		self.gui.load_plugin_prefs(pre_init=True)
		self.gui.method = self.method
		self.thread_worker = None
		
		# load up settings
		# qt_settings = QtCore.QSettings(QtCore.QSettings.IniFormat,
									   # QtCore.QSettings.UserScope,
									   # 'Stanford University',
									   # 'LFDisplay')
		# self.lfd_settings = Settings(qt_settings)

		@self.gui.btn_open_img.changed.connect
		def img_list_open():
			img_selected = str(self.gui.gui_elms["main"]["img_list"].value)
			img_folder = str(self.gui.gui_elms["main"]["img_folder"].value)
			img_file_path = os.path.join(img_folder, img_selected)
			
			# self.lfd_settings.setValue('input/file/default_path',img_file_path)
			
			if self.gui.gui_elms["misc"]["use_ext_viewer"].value == True:
				if self.gui.gui_elms["misc"]["ext_viewer_sel"].value == "System":
					self.openImage(img_file_path)
				else:
					self.openImageExtViewer(img_file_path)
			else:
				if self.method == LFvals.METHODS[0]:
					self.viewer.open(img_file_path, stack=True)
				elif self.method == LFvals.METHODS[1]:
					self.viewer.open(img_file_path, stack=True)
				else:
					if self.gui.gui_elms["misc"]["ext_viewer_sel"].value == "System":
						self.openImage(img_file_path)
					else:
						self.openImageExtViewer(img_file_path)
		
		# @self.gui.gui_elms["misc"]["lib_folder"].changed.connect
		# @self.gui.gui_elms.get("misc", {}).get("lib_folder").changed.connect
		def folder_lfa_call():
			vals = load_lf(self.gui.gui_elms["misc"]["lib_folder"].value)
			if vals[0]:
				self.lflib_ext = True
				self.lfcalibrate = vals[1]['lfcalibrate']
				self.lfdeconvolve = vals[1]['lfdeconvolve']
				self.lfrectify = vals[1]['lfrectify']
				self.lfproject = vals[1]['lfproject']
				self.lflib = vals[1]['lflib']
				self.lflib_ver = self.lflib.version
				self.gui.gui_elms["misc"]["lib_ver_label"].value = self.lflib_ver
				# print('LFA loaded from:', self.gui.gui_elms["misc"]["lib_folder"].value, '| LF LIB Ver:', self.lflib_ver)
			else:
				# print('LFA could not be loaded from:', self.gui.gui_elms["misc"]["lib_folder"].value)
				self.gui.gui_elms["misc"]["lib_ver_label"].value = 'Error!'
				
		# @self.gui.gui_elms["main"]["img_folder"].changed.connect
		def img_folder_call():
			bool = self.gui.read_meta()
			if bool:
				self.refresh_vals()
			self.gui.image_folder_changes()
				
		def set_status(vals):
			self.gui.set_btns_and_status(True, vals[0])
			
			if vals[1] == 'cal' and vals[2] == '':
				self.gui.populate_cal_img_list() #refresh calib lfc choice in drop-down
				self.gui.set_cal_img() # set the new calib lfc file as default choice for rectify/deconvolve
				
			if vals[1] == 'rec' and vals[2] == '':
				self.display_rec_image()
				
			if vals[1] == 'dec' and vals[2] == '':
				self.display_proc_image('dec')
				
			if vals[1] == 'lfmnet' and vals[2] == '':
				self.display_proc_image(operation_type=vals[1])
    
			if 'proj_' in vals[1] and vals[2] == '':
				self.display_proc_image(operation_type=vals[1])
				
			if vals[2] != '':
				err = vals[2]
				# print(repr(err))
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Critical)
				msg.setText("Error")
				msg.setInformativeText(repr(err))
				msg.setWindowTitle("Error")
				msg.exec_()
				
			self.gui.image_folder_changes()
			
		@self.gui.btn_cal.changed.connect
		def btn_cal_call():
			self.gui.set_btns_and_status(False, LFvals.PLUGIN_ARGS['main']['status']['value_busy'])
			self.combine_args()
			# https://napari.org/api/napari.qt.threading.html
			self.thread_worker = self.run_lfcalibrate(self.new_args_cal)  # create "worker" object
			self.thread_worker.returned.connect(set_status)  # connect callback functions
			self.thread_worker.start()
			
		@self.gui.btn_rec.changed.connect
		def btn_rec_call():
			self.gui.set_btns_and_status(False, LFvals.PLUGIN_ARGS['main']['status']['value_busy'])
			self.combine_args()
			self.thread_worker = self.run_lfrectify(self.new_args_rec)
			self.thread_worker.returned.connect(set_status)
			self.thread_worker.start()
			
		@self.gui.btn_dec.changed.connect
		def btn_dec_call():
			self.gui.set_btns_and_status(False, LFvals.PLUGIN_ARGS['main']['status']['value_busy'])
			self.combine_args()
			self.thread_worker = self.run_lfdeconvolve(self.new_args_decon)
			self.thread_worker.returned.connect(set_status)
			self.thread_worker.start()
			
		@self.gui.btn_stop.changed.connect
		def btn_stop_call():
			self.thread_worker.quit()
			self.gui.set_btns_and_status(True, LFvals.PLUGIN_ARGS['main']['status']['value_idle'])
			
		@self.gui.btn_stop2.changed.connect
		def btn_stop_call():
			self.thread_worker.quit()
			self.gui.set_btns_and_status(True, LFvals.PLUGIN_ARGS['main']['status']['value_idle'])
			
		@self.gui.gui_elms["projections"]["input_file_volume_btn"].changed.connect
		def input_file_volume_btn_fnc():
			#print("Button for Forward Projections Volume Processing")
			self.gui.set_btns_and_status(False, LFvals.PLUGIN_ARGS['main']['status']['value_busy'])
			self.combine_args()
			self.thread_worker = self.run_lf_proj_lfs(self.new_args_proj)
			self.thread_worker.returned.connect(set_status)
			self.thread_worker.start()
			
		@self.gui.gui_elms["projections"]["input_file_lightfield_btn"].changed.connect
		def input_file_lightfield_btn_fnc():
			#print("Button for Backward Projections Lightfield Processing")
			self.gui.set_btns_and_status(False, LFvals.PLUGIN_ARGS['main']['status']['value_busy'])
			self.combine_args()
			self.thread_worker = self.run_lf_proj_vol(self.new_args_proj)
			self.thread_worker.returned.connect(set_status)
			self.thread_worker.start()
			
		@self.gui.gui_elms["lfmnet"]["input_model_btn"].changed.connect
		@self.gui.btn_nn_proc.changed.connect
		def input_model_btn_fnc():
			#print("Button for LFMNet Model Processing")
			self.gui.set_btns_and_status(False, LFvals.PLUGIN_ARGS['main']['status']['value_busy'])
			self.combine_args()
			self.thread_worker = self.run_lf_net(self.new_args_lfmnet)
			self.thread_worker.returned.connect(set_status)
			self.thread_worker.start()
			
		@self.gui.gui_elms["lfmnet"]["input_model"].changed.connect
		def input_model_change_call():
			#print("Button for LFMNet Model Change")
			try:
				try:
					import torch
				except Exception as e:
					print("torch could not be imported")
					print(e)
					print(traceback.format_exc())
					return

				try:
					from napari_lf.lfa.neural_nets.LFNeuralNetworkProto import LFNeuralNetworkProto
				except:
					from lfa.neural_nets.LFNeuralNetworkProto import LFNeuralNetworkProto
				
				# Define input shape, and extract it either from a calib file or the stored checkpoint
				LFshape = None
				# Load calib file
				if self.gui.gui_elms["lfmnet"]["calibration_file"].value == None:
					pass
				else:
					calibFile_path = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), self.gui.gui_elms["lfmnet"]["calibration_file"].value))
					path = Path(calibFile_path)
					if path.is_file():
						import h5py
						with h5py.File(calibFile_path, "r") as f:
							lf = f['geometry']
							LFshape = [lf.attrs['nu'], lf.attrs['nv'], lf.attrs['ns'], lf.attrs['nt']]
					
				if self.gui.gui_elms["lfmnet"]["input_model"].value == None:
					return
				checkpoint_path = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), self.gui.gui_elms["lfmnet"]["input_model"].value))

				# Load Network
				net = LFNeuralNetworkProto.load_network_from_file(checkpoint_path, LFshape)
				
				# Set network into evaluation mode (faster ode)
				net.eval()
				data_str = ""
				for i in net.network_settings_dict:
					data_str += i + ' : ' + str(net.network_settings_dict[i]) + '\n'
				for i in net.training_settings_dict:
					data_str += i + ' : ' + str(net.training_settings_dict[i]) + '\n'
				self.gui.gui_elms["lfmnet"]["input_model_prop_viewer"].value = data_str
			except Exception as e:
				print(e)
				print(traceback.format_exc())
			
		for section in ['calibrate','rectify','deconvolve','hw','misc','main']:
			for prop in LFvals.PLUGIN_ARGS[section]:
				if LFvals.PLUGIN_ARGS[section][prop]['type'] in ['int', 'float', 'sel']:
					self.gui.gui_elms[section][prop].native.installEventFilter(self)
			
		#Get and Set Prefs
		self.gui.populate_img_list()
		self.gui.populate_cal_img_list()
		self.gui.load_plugin_prefs()
		
		if "mode_choice" in self.gui.settings["main"] and self.gui.settings["main"]["mode_choice"] == 'NeuralNet':
			self.gui.LFAnalyze_btn_cont.hide()
			self.gui.NeuralNet_btn_cont.show()
			self.gui.widget_main_bottom_comps0.hide()
			self.gui.widget_main_bottom_comps1.hide()
			self.gui.widget_main_bottom_comps2.show()
			self.gui._cont_btn_processing.hide()
			self.gui._cont_btn_processing2.show()
			self.gui.NeuralNet_btn.toggle()
		else:
			self.gui.LFAnalyze_btn.toggle()
		
		#Layout
		layout = QVBoxLayout()
		self.setLayout(layout)
		
		self.setMinimumWidth(480)
		self.layout().addWidget(self.gui.widget_main_top_comps.native)
		self.layout().addWidget(self.gui.qtab_widget_top)
		self.layout().addWidget(self.gui.widget_main_proc_btn_comps.native)
		self.layout().setAlignment(Qt.AlignTop)
		self.layout().setContentsMargins(0,0,0,0)
		self.layout().setSpacing(0)
		
		self.set_lfa_libs()
		if LFvals.dev_true:
			self.setStyleSheet("border : 1px dashed white;")
		
		# create the display widget
		# set defaults
		# if not self.lfd_settings.contains('output/default_path'):
			# self.lfd_settings.setValue('output/default_path',os.getcwd())
		# if not self.lfd_settings.contains('input/default_path'):
			# self.lfd_settings.setValue('input/default_path',os.getcwd())
		# if not self.lfd_settings.contains('app/resource_path') or not os.path.exists(os.path.join(self.lfd_settings.getString('app/resource_path'), 'splash.png')):
			# load resource location
			# cwd = os.getcwd()
			# if not sys.argv[0]:
				# resource_path = cwd
			# else:
				# resource_path = os.path.dirname(os.path.abspath(sys.argv[0]))
			# self.lfd_settings.setValue('app/resource_path',resource_path)
			
		# img_selected = str(self.gui.gui_elms["main"]["img_list"].value)
		# img_folder = str(self.gui.gui_elms["main"]["img_folder"].value)
		# img_file_path = os.path.join(img_folder, img_selected)
		# self.lfd_settings.setValue('input/file/default_path',img_file_path)
		# self.dispWidget = display.ImagingDisplay(self.lfd_settings, self.gui.LFD_frame)
		# self.gui.LFD_frame.setCentralWidget(self.dispWidget)
		
	def set_lfa_libs(self):
		if self.method == LFvals.METHODS[0]:
			try:
				self.lfcalibrate = lfcalibrate
				self.lfdeconvolve = lfdeconvolve
				self.lfrectify = lfrectify
				self.lfproject = lfproject
				self.lflib = lflib
				self.lflib_ver = lflib.version
				self.gui.gui_elms["misc"]["lib_ver_label"].value = self.lflib_ver
				# print('LFA loaded from:', self.gui.gui_elms["misc"]["lib_folder"].value, '| LF LIB Ver:', self.lflib_ver)
			except Exception as e:
				print(e)
				print('LFA could not be loaded from:', self.gui.gui_elms["misc"]["lib_folder"].value)
				self.gui.gui_elms["misc"]["lib_ver_label"].value = 'Error!'
				print(traceback.format_exc())
	
	def closeEvent(self, event):
		self.gui.save_plugin_prefs()
		if self.gui.timer is not None:
			self.gui.timer.stop()
		# print('closeEvent')
			
	def hideEvent(self, event):
		self.gui.save_plugin_prefs()
		if self.gui.timer is not None:
			self.gui.timer.stop()
		# print('hideEvent')
		
	def showEvent(self, event):
		if self.gui.timer is not None:
			self.gui.timer.start(500)
		# print('showEvent')
		
	#Event Filter
	def eventFilter(self, source, event):
		if (event.type() == QtCore.QEvent.MouseButtonRelease):
			self.gui.verify_preset_vals()
		if (event.type() == QtCore.QEvent.Wheel and self.gui.gui_elms['misc']['disable_mousewheel'].value == True):
			return True
		return super(LFQWidget, self).eventFilter(source, event)

	def display_rec_image(self):
		rec_img = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), self.gui.lf_vals["rectify"]["output_filename"]["value"]))
		
		if self.gui.gui_elms["misc"]["use_ext_viewer"].value == True:
			if self.gui.gui_elms["misc"]["ext_viewer_sel"].value == "System":
				self.openImage(rec_img)
			else:
				self.openImageExtViewer(rec_img)
		else:
			if self.method == LFvals.METHODS[0]:
				self.viewer.open(rec_img, stack=True)
			elif self.method == LFvals.METHODS[1]:
				self.viewer.open(rec_img, stack=True)
			else:
				if self.gui.gui_elms["misc"]["ext_viewer_sel"].value == "System":
					self.openImage(rec_img)
				else:
					self.openImageExtViewer(proc_img)
	
	def display_proc_image(self, operation_type='dec'):
		if operation_type=='dec':
			proc_img = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), self.gui.lf_vals["deconvolve"]["output_filename"]["value"]))
		elif operation_type=='proj_lf':
			proc_img = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), self.gui.lf_vals["projections"]["output_filename_lightfield"]["value"]))
		elif operation_type=='proj_vol':
			proc_img = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), self.gui.lf_vals["projections"]["output_filename_volume"]["value"]))
		elif operation_type=='lfmnet':
			proc_img = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), self.gui.lf_vals["lfmnet"]["output_filename"]["value"]))
   
		layer = None
		if self.gui.gui_elms["misc"]["use_ext_viewer"].value == True:
			if self.gui.gui_elms["misc"]["ext_viewer_sel"].value == "System":
				self.openImage(proc_img)
			else:
				self.openImageExtViewer(proc_img)
		else:
			if self.method == LFvals.METHODS[0]:
				layer = self.viewer.open(proc_img, stack=True)
			elif self.method == LFvals.METHODS[1]:
				layer = self.viewer.open(proc_img, stack=True)
			else:
				if self.gui.gui_elms["misc"]["ext_viewer_sel"].value == "System":
					self.openImage(proc_img)
				else:
					self.openImageExtViewer(proc_img)
		# Disable scaling of the output if its an image
		if layer is not None and 'proj' not in operation_type:
			volume_voxel_scale = [	self.gui.gui_elms['calibrate']['um_per_slice'].value,
                         			self.gui.gui_elms['calibrate']['pixel_size'].value / self.gui.gui_elms['calibrate']['objective_magnification'].value,
                         			self.gui.gui_elms['calibrate']['pixel_size'].value / self.gui.gui_elms['calibrate']['objective_magnification'].value]
			layer[-1].scale = tuple(volume_voxel_scale)

	def openImage(self, path):
		self.gui.openImage(path)
		
	def openImageExtViewer(self, path):
		self.gui.openImageExtViewer(path)
		
	def combine_args(self):		
		self.new_args_cal = []
		self.new_args_rec = []
		self.new_args_decon = []
		self.new_args_proj = []
		self.new_args_lfmnet = []
		
		self.gui.refresh_vals()
		
		try:			
			for section in ["calibrate", "hw"]:
				for key in self.gui.lf_vals[section]:
					dict = self.gui.lf_vals[section][key]
					if "exclude_from_args" in dict and dict["exclude_from_args"] == True:
						pass
					elif "bind" in dict and dict["bind"] in self.gui.lf_vals[section] and dict["value"] == self.gui.lf_vals[section][dict["bind"]]["value"]:
						pass
					else:
						prop = dict["prop"]
						if ("cat" in dict and dict["cat"] == "required") or (dict["value"] != dict["default"]):
							current_val = dict["value"]
						else:
							current_val = None
							
						if dict["type"] == "bool":
							if dict["default"] == True or current_val == True:
								self.new_args_cal.append(prop)
						else:
							if current_val != None:								
								if dict["type"] != "bool":
									if "img_folder_file" in dict and dict["img_folder_file"] == True:
										current_val = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), current_val))
									else:
										current_val = str(current_val)
								self.new_args_cal.append(prop)
								self.new_args_cal.append(current_val)
								
			self.new_args_cal.append(LFvals.PLUGIN_ARGS["main"]["comments"]["prop"])
			self.new_args_cal.append(self.gui.gui_elms["main"]["comments"].value)

			key = "input_file"
			dict = self.gui.lf_vals["rectify"][key]
			current_val = dict["value"]
			if "img_folder_file" in dict and dict["img_folder_file"] == True:
				current_val = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), current_val))
			else:
				current_val = str(current_val)
			self.new_args_rec.append(current_val)
			
			for key in self.gui.lf_vals["rectify"]:
				dict = self.gui.lf_vals["rectify"][key]
				if "exclude_from_args" in dict and dict["exclude_from_args"] == True:
					pass
				elif "bind" in dict and dict["bind"] in self.gui.lf_vals["rectify"] and dict["value"] == self.gui.lf_vals["rectify"][dict["bind"]]["value"]:
					pass
				else:
					prop = dict["prop"]
					if ("cat" in dict and dict["cat"] == "required") or (dict["value"] != dict["default"]):
						current_val = dict["value"]
					else:
						current_val = None
						
					if dict["type"] == "bool":
						if dict["default"] == True or current_val == True:
							self.new_args_rec.append(prop)
					else:
						if current_val != None:
							if dict["type"] != "bool":
								if "img_folder_file" in dict and dict["img_folder_file"] == True:
									current_val = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), current_val))
								else:
									current_val = str(current_val)
							self.new_args_rec.append(prop)
							self.new_args_rec.append(current_val)
					
			key = "input_file"
			dict = self.gui.lf_vals["deconvolve"][key]
			current_val = dict["value"]
			if "img_folder_file" in dict and dict["img_folder_file"] == True:
				current_val = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), current_val))
			else:
				current_val = str(current_val)
			self.new_args_decon.append(current_val)
			
			for section in ["deconvolve", "hw"]:
				for key in self.gui.lf_vals[section]:
					dict = self.gui.lf_vals[section][key]
					if "exclude_from_args" in dict and dict["exclude_from_args"] == True:
						pass
					elif "bind" in dict and dict["bind"] in self.gui.lf_vals[section] and dict["value"] == self.gui.lf_vals[section][dict["bind"]]["value"]:
						pass
					else:
						prop = dict["prop"]
						if ("cat" in dict and dict["cat"] == "required") or (dict["value"] != dict["default"]):
							current_val = dict["value"]
						else:
							current_val = None
							
						if current_val == None:
							pass
						elif dict["type"] == "bool":
							if dict["default"] == True or current_val == True:
								self.new_args_decon.append(prop)
						else:
							if "img_folder_file" in dict and dict["img_folder_file"] == True:
								current_val = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), current_val))
							else:
								current_val = str(current_val)
							self.new_args_decon.append(prop)
							self.new_args_decon.append(current_val)
							
			key = "input_file"
			dict = self.gui.lf_vals["lfmnet"][key]
			current_val = dict["value"]
			if "img_folder_file" in dict and dict["img_folder_file"] == True:
				current_val = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), current_val))
			else:
				current_val = str(current_val)
			self.new_args_lfmnet.append(current_val)
			
			for section in ["lfmnet", "hw"]:
				for key in self.gui.lf_vals[section]:
					dict = self.gui.lf_vals[section][key]
					if "exclude_from_args" in dict and dict["exclude_from_args"] == True:
						pass
					elif "bind" in dict and dict["bind"] in self.gui.lf_vals[section] and dict["value"] == self.gui.lf_vals[section][dict["bind"]]["value"]:
						pass
					else:
						prop = dict["prop"]
						if ("cat" in dict and dict["cat"] == "required") or (dict["value"] != dict["default"]):
							current_val = dict["value"]
						else:
							current_val = None
							
						if current_val == None:
							pass
						elif dict["type"] == "bool":
							if dict["default"] == True or current_val == True:
								self.new_args_lfmnet.append(prop)
						else:
							if "img_folder_file" in dict and dict["img_folder_file"] == True:
								current_val = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), current_val))
							else:
								current_val = str(current_val)
							self.new_args_lfmnet.append(prop)
							self.new_args_lfmnet.append(current_val)
       		
			key = "input_file_volume"
			dict = self.gui.lf_vals["projections"][key]
			current_val = dict["value"]
			if "img_folder_file" in dict and dict["img_folder_file"] == True:
				current_val = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), current_val))
			else:
				current_val = str(current_val)
			self.new_args_proj.append(current_val)
			key = "input_file_lightfield"
			dict = self.gui.lf_vals["projections"][key]
			current_val = dict["value"]
			if "img_folder_file" in dict and dict["img_folder_file"] == True:
				current_val = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), current_val))
			else:
				current_val = str(current_val)
			self.new_args_proj.append(current_val)
   
			for section in ["projections", "hw"]:
				for key in self.gui.lf_vals[section]:
					dict = self.gui.lf_vals[section][key]
					if "exclude_from_args" in dict and dict["exclude_from_args"] == True:
						pass
					elif "bind" in dict and dict["bind"] in self.gui.lf_vals[section] and dict["value"] == self.gui.lf_vals[section][dict["bind"]]["value"]:
						pass
					else:
						prop = dict["prop"]
						if ("cat" in dict and dict["cat"] == "required") or (dict["value"] != dict["default"]):
							current_val = dict["value"]
						else:
							current_val = None
							
						if current_val == None:
							pass
						elif dict["type"] == "bool":
							if dict["default"] == True or current_val == True:
								self.new_args_proj.append(prop)
						else:
							if "img_folder_file" in dict and dict["img_folder_file"] == True:
								current_val = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), current_val))
							else:
								current_val = str(current_val)
							self.new_args_proj.append(prop)
							self.new_args_proj.append(current_val)

		except Exception as e:
			print(key)
			print(traceback.format_exc())
			raise(e)
			
		self.gui.write_meta()

	@thread_worker(progress={'total': 0})
	def run_lfcalibrate(self, args):
		# currentdir = os.path.dirname(os.path.realpath(__file__))
		# grandparentdir = os.path.dirname(os.path.dirname(currentdir))
		# sys.path.append(gui_elms["misc"]["lib_folder"].value)
		# from lfcalibrate import main
		try:
			print(args)
			self.lfcalibrate.main(args)
			return (LFvals.PLUGIN_ARGS['main']['status']['value_idle'], 'cal', '')
		except Exception as err:
			print(traceback.format_exc())
			self.gui.dump_errors(self.currentdir, str(traceback.format_exc()), traceback=True)
			return (LFvals.PLUGIN_ARGS['main']['status']['value_error'], 'cal', err)
			
	@thread_worker(progress={'total': 0})
	def run_lfrectify(self, args):
		# currentdir = os.path.dirname(os.path.realpath(__file__))
		# grandparentdir = os.path.dirname(os.path.dirname(currentdir))
		# sys.path.append(gui_elms["misc"]["lib_folder"].value)
		# from lfrectify import main
		try:
			print(args)
			self.lfrectify.main(args)
			return (LFvals.PLUGIN_ARGS['main']['status']['value_idle'], 'rec', '')
		except Exception as err:
			print(traceback.format_exc())
			self.gui.dump_errors(self.currentdir, str(traceback.format_exc()), traceback=True)
			return (LFvals.PLUGIN_ARGS['main']['status']['value_error'], 'rec', err)
		
	@thread_worker(progress={'total': 0})
	def run_lfdeconvolve(self, args):
		# currentdir = os.path.dirname(os.path.realpath(__file__))
		# grandparentdir = os.path.dirname(os.path.dirname(currentdir))
		# sys.path.append(gui_elms["misc"]["lib_folder"].value)
		# from lfdeconvolve import main
		try:
			print(args)
			self.lfdeconvolve.main(args)		
			return (LFvals.PLUGIN_ARGS['main']['status']['value_idle'], 'dec', '')
		except Exception as err:
			print(traceback.format_exc())
			self.gui.dump_errors(self.currentdir, str(traceback.format_exc()), traceback=True)
			return (LFvals.PLUGIN_ARGS['main']['status']['value_error'], 'dec', err)
			
	@thread_worker(progress={'total': 0})
	def run_lf_proj_lfs(self, args):
		try:
			args += ['--solver','proj_lf']
			print(args)
			print("Projections LFs process")	
			self.lfproject.main(args)
			return (LFvals.PLUGIN_ARGS['main']['status']['value_idle'], 'proj_lf', '')
		except Exception as err:
			print(traceback.format_exc())
			self.gui.dump_errors(self.currentdir, str(traceback.format_exc()), traceback=True)
			return (LFvals.PLUGIN_ARGS['main']['status']['value_error'], 'proj_lf', err)
			
	@thread_worker(progress={'total': 0})
	def run_lf_proj_vol(self, args):
		try:
			args += ['--solver','proj_vol']
			print(args)
			print("Projections Vols process")	
			self.lfproject.main(args)	
			return (LFvals.PLUGIN_ARGS['main']['status']['value_idle'], 'proj_vol', '')
		except Exception as err:
			print(traceback.format_exc())
			self.gui.dump_errors(self.currentdir, str(traceback.format_exc()), traceback=True)
			return (LFvals.PLUGIN_ARGS['main']['status']['value_error'], 'proj_vol', err)
			
	@thread_worker(progress={'total': 0})
	def run_lf_net(self, args):
		try:
			args += ['--solver','net']
			# torch_device = torch.device("cuda:1")
			# torch_device = torch.device("cpu:1")
			gpu_id = 1 #It seems that even when no GPU is selected, devices should be >=1 (Josué Page Vizcaíno)
			try:
				gpu_id = max(self.gui.gpu_choices.index(self.gui.gui_elms["hw"]["gpu_id"].value)+1,1)
			except Exception as err:
				pass

			print(args)
			print("Neural Net process")
			
			print('\t--> hostname:{host}'.format(host=lfdeconvolve.socket.gethostname()))
			
			if '--disable-gpu' not in args:
				print('\t--> specified gpu-id:{gpuid}'.format(gpuid=gpu_id))
			
			import torch
			if '--disable-gpu' not in args:
				print('\t--> cuda available:{gpu}'.format(gpu=torch.cuda.is_available()))
			print("\t--> device: ","cuda:"+str(gpu_id) if torch.cuda.is_available() and not '--disable-gpu' in args else "cpu")
			
			try:
				from napari_lf.lfa.neural_nets.LFNeuralNetworkProto import LFNeuralNetworkProto
				from napari_lf.lfa.lflib.lightfield import LightField
			except:
				from lfa.neural_nets.LFNeuralNetworkProto import LFNeuralNetworkProto
				from lfa.lflib.lightfield import LightField


			cal_present = False
			# # Load calib file
			# if self.gui.gui_elms["lfmnet"]["calibration_file"].value != None:
			# 	calibFile_path = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), self.gui.gui_elms["lfmnet"]["calibration_file"].value))
			# 	path = Path(calibFile_path)
			# 	if path.is_file() != False:
			# 		# Loadim the calibration data
			# 		calibration_file = lfdeconvolve.retrieve_calibration_file(calibFile_path, id=str(gpu_id))
			# 		lfcal = lfdeconvolve.LightFieldCalibration.load(calibration_file)
			# 		print('\t--> loaded calibration file: %s' % (calibFile_path))

			# 	cal_present = True
			
			# Check if input file selected
			if self.gui.gui_elms["lfmnet"]["input_file"].value == None:
				return
			LF_File_path = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), self.gui.gui_elms["lfmnet"]["input_file"].value))

			#Import LF image
			im = lfdeconvolve.load_image(LF_File_path, dtype=lfdeconvolve.np.float32, normalize = False)
			print('\t--> loaded LF file: %s.  Pixel values range: [%d, %d]' % (LF_File_path, int(im.min()), int(im.max())))
			
			
			LFshape = None
			# if cal_present:
			# 	# Rectify the image
			# 	# skip-alignment parameter is set by calib file
			# 	print('\t--> skip_alignment: %s' % (lfcal.skip_alignment))
			# 	lf = lfcal.rectify_lf(im)
			# 	LFshape = [lf.nu, lf.nv, lf.ns, lf.nt]

			# Network path present?
			if self.gui.gui_elms["lfmnet"]["input_model"].value == None:
				return
			checkpoint_path = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), self.gui.gui_elms["lfmnet"]["input_model"].value))


			# Load network based on checkpoint
			net = LFNeuralNetworkProto.load_network_from_file(checkpoint_path, LFshape)
			print('\t--> loaded model-checkpoint file: %s' % (checkpoint_path))
			
			# Set network into evaluation mode (faster ode)
			net.eval()
			
			# If there was no calibration file, extract info about lightfield from network

			if not cal_present: # Load LFshape from model
				LFshape = net.LF_in_shape
				print(LFshape)
				lf = LightField(im, LFshape[0], LFshape[1], LFshape[2], LFshape[3],
                                      representation = LightField.TILED_LENSLET)
			## Process image:
			with torch.no_grad():
				# Move network to device (GPU/CPU)
				torch_device = torch.device("cuda:"+str(gpu_id) if torch.cuda.is_available() and not '--disable-gpu' in args else "cpu")
				net = net.to(torch_device)   
				# Prepare input to network
				im_lenslet = lf.asimage(representation = lfdeconvolve.LightField.TILED_LENSLET)
				# Compute 3D reconstruction
				prediction = net(im_lenslet)
				# Normalize for output
				prediction /= prediction.max()
				# Copy to from GPU to CPU numpy
				x_vec = prediction[0,0,...].detach().cpu().numpy()

			# Save volume
			output_filename = str(os.path.join(str(self.gui.gui_elms["main"]["img_folder"].value), self.gui.gui_elms["lfmnet"]["output_filename"].value))
			lfdeconvolve.save_image(output_filename, x_vec)
			print('\t--> Saved', output_filename)
			
			return (LFvals.PLUGIN_ARGS['main']['status']['value_idle'], 'lfmnet', '')
		except Exception as err:
			print(traceback.format_exc())
			self.gui.dump_errors(self.currentdir, str(traceback.format_exc()), traceback=True)
			return (LFvals.PLUGIN_ARGS['main']['status']['value_error'], 'lfmnet', err)

	def refresh_vals(self):
		self.gui.refresh_vals()

	def set_method(self, method):
		self.method = method
		
	def set_viewer(self, viewer):
		self.viewer = viewer

def show_Error(err):
	print(repr(err))
	msg = QMessageBox()
	msg.setIcon(QMessageBox.Critical)
	msg.setText("Error")
	msg.setInformativeText(repr(err))
	msg.setWindowTitle("Error")
	msg.exec_()
	
def load_lf(folder_path):
	try:
		sys.path.insert(1, str(folder_path))

		import lfcalibrate, lfdeconvolve, lfrectify, lfproject
		import lflib
		
		return (True, {'lfcalibrate':lfcalibrate, 'lfdeconvolve':lfdeconvolve, 'lfrectify':lfrectify, 'lfproject':lfproject, 'lflib':lflib})			
	except Exception as e:
		print(e)
		print(traceback.format_exc())
		return (False, {})

def main(method):
	METHOD = method
	if method == LFvals.METHODS[1]: # Method 2: As napari viewer	
		viewer = napari.Viewer()
		widget = LFQWidget(QWidget())
		widget.set_method(method)
		widget.set_viewer(viewer)
		viewer.window.add_dock_widget(widget)
		napari.run()
	elif method == LFvals.METHODS[2]: # Method 3: As stand-alone application
		app = QApplication(sys.argv)
		widget = LFQWidget(QWidget())
		widget.setWindowTitle('napari-LF')
		widget.setWindowIcon(LFvals.q_icon_img)
		widget.resize(500, 750)
		widget.set_method(method)
		widget.show()
		sys.exit(app.exec_())

if __name__ == "__main__":
	main(LFvals.METHODS[1])