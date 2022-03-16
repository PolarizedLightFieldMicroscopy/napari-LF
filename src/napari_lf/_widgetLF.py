import os, sys, json
from pathlib import Path
import napari
from napari.qt.threading import thread_worker
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QMessageBox, QTabWidget
from magicgui.widgets import Container, FileEdit, Label, LineEdit, FloatSpinBox, PushButton, CheckBox, SpinBox, Slider, ComboBox

try:
	from napari_lf import _widgetLF_gui as LFgui
	from napari_lf.lfa import lfcalibrate, lfdeconvolve, lfrectify
	from napari_lf.lfa import lflib
	from napari_lf import _widgetLF_gui as LFgui
except:
	import _widgetLF_gui as LFgui
	# from lfa import lfcalibrate, lfdeconvolve, lfrectify
	# from lfa import lflib

METHODS = ['PLUGIN','NAPARI','APP']
METHOD = METHODS[0]

# Method 1: As Napari plugin
class LFQWidget(QWidget):
		
	def __init__(self, napari_viewer):
		super().__init__()
		self.settings = {}
		self.lfa_args = {}
		self.viewer = napari_viewer
		self.method = METHOD
		self.lfcalibrate = None
		self.lfdeconvolve = None
		self.lfrectify = None
		self.lflib = None
		self.lflib_ver = ''
		self.lflib_ext = False
		self.currentdir = os.path.dirname(os.path.realpath(__file__))
		self.gui = LFgui.LFQWidgetGui()
		
		@self.gui.folder_lfa.changed.connect
		def folder_lfa_call():
			vals = load_lf(self.gui.folder_lfa.value)
			if vals[0]:
				self.lflib_ext = True
				self.lfcalibrate = vals[1]['lfcalibrate']
				self.lfdeconvolve = vals[1]['lfdeconvolve']
				self.lfrectify = vals[1]['lfrectify']
				self.lflib = vals[1]['lflib']
				self.lflib_ver = self.lflib.version
				self.gui.folder_lfa_label.value = self.lflib_ver
				print('LFA loaded from:', self.gui.folder_lfa.value, '| LF LIB Ver:', self.lflib_ver)
			else:
				print('LFA could not be loaded from:', self.gui.folder_lfa.value)
				self.gui.folder_lfa_label.value = 'Error!'
				
		@self.gui.img_folder.changed.connect
		def folder_path1_call():
			bool = self.read_meta()
			if bool:
				self.refresh_fields()
				
		def set_status(vals):
			self.gui.status.value = vals[0]
			
			if vals[1] == 'dec':
				self.display_proc_image()
				
			if vals[2] != '':
				err = vals[2]
				print(repr(err))
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Critical)
				msg.setText("Error")
				msg.setInformativeText(repr(err))
				msg.setWindowTitle("Error")
				msg.exec_()
			
		@self.gui.btn_cal.changed.connect
		def btn_cal_call():
			self.gui.set_status_busy()
			self.combine_args()
			worker = self.run_lfcalibrate(self.new_args_cal)  # create "worker" object
			worker.returned.connect(set_status)  # connect callback functions
			worker.start()
			
		@self.gui.btn_rec.changed.connect
		def btn_rec_call():
			self.gui.set_status_busy()
			self.combine_args()
			worker = self.run_lfrectify(self.new_args_rec)
			worker.returned.connect(set_status)
			worker.start()
			
		@self.gui.btn_dec.changed.connect
		def btn_dec_call():
			self.gui.set_status_busy()
			self.combine_args()
			worker = self.run_lfdeconvolve(self.new_args_decon)
			worker.returned.connect(set_status)
			worker.start()
			
		#Get and Set Prefs
		self.load_plugin_prefs()
		
		#Layout
		layout = QVBoxLayout()
		self.setLayout(layout)
		
		self.scroll = QScrollArea()
		 #Scroll Area Properties
		self.scroll.setWidgetResizable(True)
		self.scroll.setWidget(self.gui.widget_main.native)
		self.layout().addWidget(self.gui.widget_logo_info.native)
		self.layout().addWidget(self.gui.widget_main_comps.native)
		self.layout().addWidget(self.scroll)
		self.setMinimumSize(400,600)
		self.set_lfa_libs()
		
	def set_lfa_libs(self):
		if self.method == METHODS[0]:
			try:
				self.lfcalibrate = lfcalibrate
				self.lfdeconvolve = lfdeconvolve
				self.lfrectify = lfrectify
				self.lflib = lflib
				self.lflib_ver = lflib.version
				self.gui.folder_lfa_label.value = self.lflib_ver
				print('LFA loaded from:', self.gui.folder_lfa.value, '| LF LIB Ver:', self.lflib_ver)
			except:
				print('LFA could not be loaded from:', self.gui.folder_lfa.value)
				self.gui.folder_lfa_label.value = 'Error!'
		
	def closeEvent(self, event):
		self.save_plugin_prefs()
			
	def hideEvent(self, event):
		self.save_plugin_prefs()

	def display_proc_image(self):
		proc_img = str(os.path.join(str(self.gui.img_folder.value), self.gui.lf_vals["deconvolve"]["output_filename"]["value"]))
		if self.method == METHODS[0]:
			self.viewer.open(proc_img, stack=True)
		elif self.method == METHODS[1]:
			self.viewer.open(proc_img, stack=True)
		else:
			self.openImage(proc_img)

	def openImage(self, path):
		import subprocess
		imageViewerFromCommandLine = {'linux':'xdg-open','win32':'explorer','darwin':'open'}[sys.platform]
		subprocess.Popen([imageViewerFromCommandLine, path])
		
	def combine_args(self):		
		self.new_args_cal = []
		self.new_args_rec = []
		self.new_args_decon = []
		
		self.gui.refresh_vals()
		
		try:
			key = "radiometry_frame_file"
			dict = self.gui.lf_vals["calibrate"][key]
			current_val = dict["value"]
			if "img_folder_file" in dict and dict["img_folder_file"] == True:
				current_val = str(os.path.join(str(self.gui.img_folder.value), current_val))
			else:
				current_val = str(current_val)
			self.new_args_cal.append(current_val)
			
			for key in self.gui.lf_vals["calibrate"]:
				dict = self.gui.lf_vals["calibrate"][key]
				if "exclude_from_args" in dict and dict["exclude_from_args"] == True:
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
							self.new_args_cal.append(prop)
							if dict["type"] != "bool":
								if "img_folder_file" in dict and dict["img_folder_file"] == True:
									current_val = str(os.path.join(str(self.gui.img_folder.value), current_val))
								else:
									current_val = str(current_val)
							self.new_args_cal.append(current_val)

			key = "input_file"
			dict = self.gui.lf_vals["deconvolve"][key]
			current_val = dict["value"]
			if "img_folder_file" in dict and dict["img_folder_file"] == True:
				current_val = str(os.path.join(str(self.gui.img_folder.value), current_val))
			else:
				current_val = str(current_val)
			self.new_args_rec.append(current_val)
			for key in self.gui.lf_vals["rectify"]:
				dict = self.gui.lf_vals["rectify"][key]
				if "exclude_from_args" in dict and dict["exclude_from_args"] == True:
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
							self.new_args_rec.append(prop)
							if dict["type"] != "bool":
								if "img_folder_file" in dict and dict["img_folder_file"] == True:
									current_val = str(os.path.join(str(self.gui.img_folder.value), current_val))
								else:
									current_val = str(current_val)
							self.new_args_rec.append(current_val)
					
			key = "input_file"
			dict = self.gui.lf_vals["deconvolve"][key]
			current_val = dict["value"]
			if "img_folder_file" in dict and dict["img_folder_file"] == True:
				current_val = str(os.path.join(str(self.gui.img_folder.value), current_val))
			else:
				current_val = str(current_val)
			self.new_args_decon.append(current_val)
			for key in self.gui.lf_vals["deconvolve"]:
				dict = self.gui.lf_vals["deconvolve"][key]
				if "exclude_from_args" in dict and dict["exclude_from_args"] == True:
					pass
				else:
					prop = dict["prop"]
					if ("cat" in dict and dict["cat"] == "required") or (dict["value"] != dict["default"]):
						current_val = dict["value"]
					else:
						current_val = None
						
					if dict["type"] == "bool":
						if dict["default"] == True or current_val == True:
							self.new_args_decon.append(prop)
					else:
						if current_val != None:
							self.new_args_decon.append(prop)
							if dict["type"] != "bool":
								if "img_folder_file" in dict and dict["img_folder_file"] == True:
									current_val = str(os.path.join(str(self.gui.img_folder.value), current_val))
								else:
									current_val = str(current_val)
							self.new_args_decon.append(current_val)
					
		except Exception as e:
			print(key)
			raise(e)
			
		self.write_meta()

	@thread_worker
	def run_lfcalibrate(self, args):
		# currentdir = os.path.dirname(os.path.realpath(__file__))
		# grandparentdir = os.path.dirname(os.path.dirname(currentdir))
		# sys.path.append(folder_lfa.value)
		# from lfcalibrate import main
		try:
			print(args)
			self.lfcalibrate.main(args)
			return ('== IDLE ==', 'cal', '')
		except Exception as err:
			return ('== ERROR ==', 'cal', err)
			
	@thread_worker
	def run_lfrectify(self, args):
		# currentdir = os.path.dirname(os.path.realpath(__file__))
		# grandparentdir = os.path.dirname(os.path.dirname(currentdir))
		# sys.path.append(folder_lfa.value)
		# from lfrectify import main
		try:
			print(args)
			self.lfrectify.main(args)
			return ('== IDLE ==', 'rec', '')
		except Exception as err:
			return ('== ERROR ==', 'rec', err)
		
	@thread_worker
	def run_lfdeconvolve(self, args):
		# currentdir = os.path.dirname(os.path.realpath(__file__))
		# grandparentdir = os.path.dirname(os.path.dirname(currentdir))
		# sys.path.append(folder_lfa.value)
		# from lfdeconvolve import main
		try:
			print(args)
			self.lfdeconvolve.main(args)		
			return ('== IDLE ==', 'dec', '')
		except Exception as err:
			return ('== ERROR ==', 'dec', err)
				
	def write_meta(self):
		data = {'new_args_cal':self.new_args_cal, 'new_args_decon':self.new_args_decon, 'new_args_rec':self.new_args_rec}
		with open(os.path.join(self.gui.img_folder.value, self.gui.meta_txt.value), 'w') as outfile:
			json.dump(data, outfile)
			
	def read_meta(self):
		path = Path(os.path.join(self.gui.img_folder.value, self.gui.meta_txt.value))
		if path.is_file():
			with open(os.path.join(self.gui.img_folder.value, self.gui.meta_txt.value)) as json_file:
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
		pass

	def set_method(self, method):
		self.method = method
		
	def set_viewer(self, viewer):
		self.viewer = viewer
		
	def save_plugin_prefs(self):
		self.settings['gpu_id'] = self.gui.gpu_combobox.native.currentIndex()
		self.settings['use_single_prec'] = self.gui.use_single_prec.value
		self.settings['lib_folder'] = str(self.gui.folder_lfa.value)
		self.settings['img_folder'] = str(self.gui.img_folder.value)
		
		settings_file_path = Path(os.path.join(self.currentdir, 'settings.json'))
		with open(settings_file_path, "w") as f:
			json.dump(self.settings, f, indent=4)

	def load_plugin_prefs(self):
		settings_file_path = Path(os.path.join(self.currentdir, 'settings.json'))
		if settings_file_path.is_file() is False:
			self.save_plugin_prefs()
		else:
			with open(settings_file_path, "r") as f:
				self.settings = json.load(f)
				
			self.gui.gpu_combobox.native.setCurrentIndex(self.settings['gpu_id'])
			self.gui.use_single_prec.value = self.settings['use_single_prec']
			self.gui.folder_lfa.value = str(self.settings['lib_folder'])
			self.gui.img_folder.value = str(self.settings['img_folder'])
	
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

		import lfcalibrate, lfdeconvolve, lfrectify
		import lflib
		
		return (True, {'lfcalibrate':lfcalibrate, 'lfdeconvolve':lfdeconvolve, 'lfrectify':lfrectify, 'lflib':lflib})			
	except Exception as e:
		print(e)
		return (False, {})

def main(method):
	METHOD = method
	if method == METHODS[1]: # Method 2: As Napari viewer	
		viewer = napari.Viewer()
		widget = LFQWidget(QWidget())
		widget.set_method(method)
		widget.set_viewer(viewer)
		viewer.window.add_dock_widget(widget)
		napari.run()
	elif method == METHODS[2]: # Method 3: As stand-alone application
		app = QApplication(sys.argv)
		widget = LFQWidget(QWidget())
		widget.setWindowTitle('LF Analyze')
		widget.resize(500, 750)
		widget.set_method(method)
		widget.show()
		sys.exit(app.exec_())

if __name__ == "__main__":
	main(METHODS[1])