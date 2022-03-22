import os
from qtpy.QtCore import Qt, QSize
from qtpy.QtGui import QMovie
from qtpy.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QScrollArea, QMessageBox, QTabWidget, QGridLayout, QSizePolicy, QLabel, QFrame, QGroupBox
from magicgui.widgets import Container, FileEdit, Label, LineEdit, FloatSpinBox, PushButton, CheckBox, SpinBox, Slider, ComboBox, TextEdit
try:
	from napari_lf import _widgetLF_vals as LFvals
except:
	import _widgetLF_vals as LFvals

try:	
	import pyopencl as cl
except Exception as e:
	print(e)
	
# self.lf_vals["misc"]["group_params"]["value"] = True

class LFQWidgetGui():
		
	def __init__(self):
		super().__init__()
		
		self.currentdir = os.path.dirname(os.path.realpath(__file__))
		self.lf_vals = LFvals.PLUGIN_ARGS
		self.gui_elms = {}
		
		# == MAIN ==
		self.gui_elms["main"] = {}
		_widget_main = []
		self.logo_label = Label(value=LFvals.PLUGIN_ARGS['main']['logo_label']['label'], tooltip=LFvals.PLUGIN_ARGS['main']['logo_label']['help'])
		self.logo_label.native.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		self.logo_label.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		
		self.info_label = Label(label=f'<h2><center>LF Analyze</a></center></h2>')
		self.gui_elms["main"]["img_folder"] = FileEdit(value=LFvals.PLUGIN_ARGS['main']['img_folder']['default'], label=LFvals.PLUGIN_ARGS['main']['img_folder']['label'], tooltip=LFvals.PLUGIN_ARGS['main']['img_folder']['help'], mode='d')
		self.gui_elms["main"]["metadata_file"] = LineEdit(value=LFvals.PLUGIN_ARGS['main']['metadata_file']['default'], label=LFvals.PLUGIN_ARGS['main']['metadata_file']['label'], tooltip=LFvals.PLUGIN_ARGS['main']['metadata_file']['help'])
		self.gui_elms["main"]["comments"] = TextEdit(value=LFvals.PLUGIN_ARGS['main']['comments']['default'], label=LFvals.PLUGIN_ARGS['main']['comments']['label'], tooltip=LFvals.PLUGIN_ARGS['main']['comments']['help'])
		self.gui_elms["main"]["comments"].native.setMaximumHeight(50)
		self.btn_cal = PushButton(name='Calibrate', label='Calibrate')
		self.btn_rec = PushButton(name='Rectify', label='Rectify')
		self.btn_dec = PushButton(name='Deconvolve', label='Deconvolve')
		_cont_btn_left = Container(name='btn Left', widgets=[self.btn_cal, self.btn_rec, self.btn_dec], labels=False)
		
		self.btn_stop = PushButton(name='Stop', label='Stop')
		self.btn_stop.height = 80
		self.btn_stop.min_height = 80
		
		_cont_btn_right = Container(name='btn Right', widgets=[self.btn_stop], labels=False)		
		_cont_btn_status = Container(widgets=[_cont_btn_left, _cont_btn_right], labels=False, layout='horizontal')
		
		_QFormLayout = QFormLayout()
		self.cont_btn_status = QWidget()
		self.cont_btn_status.setLayout(_QFormLayout)
		
		self.cont_btn_status_label = Label()
		self.cont_btn_status_label.native.setStyleSheet("border:1px solid rgb(0, 255, 0);")
		self.cont_btn_status_label.value = ':STATUS: '+LFvals.PLUGIN_ARGS['main']['status']['value_idle']
		
		_QFormLayout.addRow(self.logo_label.native)
		_QFormLayout.addRow(self.gui_elms["main"]["img_folder"].label, self.gui_elms["main"]["img_folder"].native)
		_QFormLayout.addRow(self.gui_elms["main"]["metadata_file"].label, self.gui_elms["main"]["metadata_file"].native)
		_QFormLayout.addRow(self.gui_elms["main"]["comments"].label, self.gui_elms["main"]["comments"].native)
		
		_QFormLayout.addRow(_cont_btn_status.native)
		_QFormLayout.addRow(self.cont_btn_status_label.native)
		
		self.cont_btn_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self.cont_btn_status_label.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.cont_btn_status_label.native.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		
		groupbox = {"calibrate":{"required":{},"optional":{}},"rectify":{"required":{},"optional":{}},"deconvolve":{"required":{},"optional":{}}}
		
		# == CALIBATE ==
		_widget_calibrate_req = []
		_widget_calibrate_opt = []
		self.gui_elms["calibrate"] = {}
		for key in self.lf_vals["calibrate"]:
			dict = self.lf_vals["calibrate"][key]
			if "label" not in dict:
				dict["label"] = dict["dest"]
			wid_elm = create_widget(dict)
			if wid_elm != None:
				self.gui_elms["calibrate"][key] = wid_elm
				
				if "cat" in dict and dict["cat"] == "required":
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_calibrate_req.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in groupbox["calibrate"]["required"]:
							groupbox["calibrate"]["required"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							_widget_calibrate_req.append(groupbox["calibrate"]["required"][dict["group"]])
							groupbox["calibrate"]["required"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								groupbox["calibrate"]["required"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								groupbox["calibrate"]["required"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in groupbox["calibrate"]["required"]) or "misc" in groupbox["calibrate"]["required"]:
							if dict["type"] == "bool":
								groupbox["calibrate"]["required"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								groupbox["calibrate"]["required"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							groupbox["calibrate"]["required"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_calibrate_req.append(groupbox["calibrate"]["required"]["misc"])
							groupbox["calibrate"]["required"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								groupbox["calibrate"]["required"]["misc"].layout().addRow(wid_elm.native)
							else:
								groupbox["calibrate"]["required"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
				else:
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_calibrate_opt.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in groupbox["calibrate"]["optional"]:
							groupbox["calibrate"]["optional"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							_widget_calibrate_opt.append(groupbox["calibrate"]["optional"][dict["group"]])
							groupbox["calibrate"]["optional"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								groupbox["calibrate"]["optional"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								groupbox["calibrate"]["optional"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in groupbox["calibrate"]["optional"]) or "misc" in groupbox["calibrate"]["optional"]:
							if dict["type"] == "bool":
								groupbox["calibrate"]["optional"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								groupbox["calibrate"]["optional"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							groupbox["calibrate"]["optional"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_calibrate_opt.append(groupbox["calibrate"]["optional"]["misc"])
							groupbox["calibrate"]["optional"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								groupbox["calibrate"]["optional"]["misc"].layout().addRow(wid_elm.native)
							else:
								groupbox["calibrate"]["optional"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
					
		self.btn_cal_req_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_cal_req_def.changed.connect
		def btn_cal_req_defaults():
			for key in self.lf_vals["calibrate"]:
				dict = self.lf_vals["calibrate"][key]
				if "cat" in dict and dict["cat"] == "required":
					wid_elm = self.gui_elms["calibrate"][key]
					wid_elm.value = dict["default"]
		
		self.btn_cal_opt_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_cal_opt_def.changed.connect
		def btn_cal_opt_defaults():
			for key in self.lf_vals["calibrate"]:
				dict = self.lf_vals["calibrate"][key]
				if "cat" in dict and dict["cat"] == "required":
					pass
				else:
					wid_elm = self.gui_elms["calibrate"][key]
					wid_elm.value = dict["default"]
		
		if self.lf_vals["misc"]["group_params"]["value"] == False:
			_widget_calibrate_req.append(self.btn_cal_req_def)			
			_widget_calibrate_opt.append(self.btn_cal_opt_def)
			self.widget_calibrate_req = Container(name='Calibrate Req', widgets=_widget_calibrate_req)
			self.widget_calibrate_opt = Container(name='Calibrate Opt', widgets=_widget_calibrate_opt)
		else:
			_widget_calibrate_req.append(self.btn_cal_req_def.native)			
			_widget_calibrate_opt.append(self.btn_cal_opt_def.native)
			
			self.widget_calibrate_req = Container(name='Calibrate Req', widgets=())
			for wid_elm in _widget_calibrate_req:
				self.widget_calibrate_req.native.layout().addWidget(wid_elm)
			self.widget_calibrate_opt = Container(name='Calibrate Opt', widgets=())
			for wid_elm in _widget_calibrate_opt:
				self.widget_calibrate_opt.native.layout().addWidget(wid_elm)
		
		# == RECTIFY ==
		_widget_rectify_req = []
		_widget_rectify_opt = []
		self.gui_elms["rectify"] = {}
		for key in self.lf_vals["rectify"]:
			dict = self.lf_vals["rectify"][key]
			if "label" not in dict:
				dict["label"] = dict["dest"]
			wid_elm = create_widget(dict)
			if wid_elm != None:
				self.gui_elms["rectify"][key] = wid_elm
				
				if "cat" in dict and dict["cat"] == "required":
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_rectify_req.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in groupbox["rectify"]["required"]:
							groupbox["rectify"]["required"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							_widget_rectify_req.append(groupbox["rectify"]["required"][dict["group"]])
							groupbox["rectify"]["required"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								groupbox["rectify"]["required"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								groupbox["rectify"]["required"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in groupbox["rectify"]["required"]) or "misc" in groupbox["rectify"]["required"]:
							group = "misc"
							if "group" in dict:
								group = dict["group"]
							if dict["type"] == "bool":
								groupbox["rectify"]["required"][group].layout().addRow(wid_elm.native)
							else:
								groupbox["rectify"]["required"][group].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							groupbox["rectify"]["required"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_rectify_req.append(groupbox["rectify"]["required"]["misc"])
							groupbox["rectify"]["required"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								groupbox["rectify"]["required"]["misc"].layout().addRow(wid_elm.native)
							else:
								groupbox["rectify"]["required"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
				else:
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_rectify_opt.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in groupbox["rectify"]["optional"]:
							groupbox["rectify"]["optional"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							_widget_rectify_opt.append(groupbox["rectify"]["optional"][dict["group"]])
							groupbox["rectify"]["optional"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								groupbox["rectify"]["optional"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								groupbox["rectify"]["optional"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in groupbox["rectify"]["optional"]) or "misc" in groupbox["rectify"]["optional"]:
							group = "misc"
							if "group" in dict:
								group = dict["group"]
							if dict["type"] == "bool":
								groupbox["rectify"]["optional"][group].layout().addRow(wid_elm.native)
							else:
								groupbox["rectify"]["optional"][group].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							groupbox["rectify"]["optional"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_rectify_opt.append(groupbox["rectify"]["optional"]["misc"])
							groupbox["rectify"]["optional"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								groupbox["rectify"]["optional"]["misc"].layout().addRow(wid_elm.native)
							else:
								groupbox["rectify"]["optional"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
					
		self.btn_rec_req_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_rec_req_def.changed.connect
		def btn_rec_req_defaults():
			for key in self.lf_vals["rectify"]:
				dict = self.lf_vals["rectify"][key]
				if "cat" in dict and dict["cat"] == "required":
					wid_elm = self.gui_elms["rectify"][key]
					wid_elm.value = dict["default"]
		
		self.btn_rec_opt_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_rec_opt_def.changed.connect
		def btn_rec_opt_defaults():
			for key in self.lf_vals["rectify"]:
				dict = self.lf_vals["rectify"][key]
				if "cat" in dict and dict["cat"] == "required":
					pass
				else:
					wid_elm = self.gui_elms["rectify"][key]
					wid_elm.value = dict["default"]
					
		if self.lf_vals["misc"]["group_params"]["value"] == False:
			_widget_rectify_req.append(self.btn_rec_req_def)			
			_widget_rectify_opt.append(self.btn_rec_opt_def)
			self.widget_rectify_req = Container(name='Rectify Req', widgets=_widget_rectify_req)
			self.widget_rectify_opt = Container(name='Rectify Opt', widgets=_widget_rectify_opt)
		else:
			_widget_rectify_req.append(self.btn_rec_req_def.native)			
			_widget_rectify_opt.append(self.btn_rec_opt_def.native)
			
			self.widget_rectify_req = Container(name='Rectify Req', widgets=())
			for wid_elm in _widget_rectify_req:
				self.widget_rectify_req.native.layout().addWidget(wid_elm)
			self.widget_rectify_opt = Container(name='Rectify Opt', widgets=())
			for wid_elm in _widget_rectify_opt:
				self.widget_rectify_opt.native.layout().addWidget(wid_elm)
		
		# == DECONVOLVE ==
		_widget_deconvolve_req = []
		_widget_deconvolve_opt = []
		self.gui_elms["deconvolve"] = {}
		for key in self.lf_vals["deconvolve"]:
			dict = self.lf_vals["deconvolve"][key]
			if "label" not in dict:
				dict["label"] = dict["dest"]
			wid_elm = create_widget(dict)
			if wid_elm != None:
				self.gui_elms["deconvolve"][key] = wid_elm
				
				if "cat" in dict and dict["cat"] == "required":
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_deconvolve_req.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in groupbox["deconvolve"]["required"]:
							groupbox["deconvolve"]["required"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							_widget_deconvolve_req.append(groupbox["deconvolve"]["required"][dict["group"]])
							groupbox["deconvolve"]["required"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								groupbox["deconvolve"]["required"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								groupbox["deconvolve"]["required"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in groupbox["deconvolve"]["required"]) or "misc" in groupbox["deconvolve"]["required"]:
							group = "misc"
							if "group" in dict:
								group = dict["group"]
							if dict["type"] == "bool":
								groupbox["deconvolve"]["required"][group].layout().addRow(wid_elm.native)
							else:
								groupbox["deconvolve"]["required"][group].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							groupbox["deconvolve"]["required"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_deconvolve_req.append(groupbox["deconvolve"]["required"]["misc"])
							groupbox["deconvolve"]["required"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								groupbox["deconvolve"]["required"]["misc"].layout().addRow(wid_elm.native)
							else:
								groupbox["deconvolve"]["required"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
				else:
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_deconvolve_opt.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in groupbox["deconvolve"]["optional"]:
							groupbox["deconvolve"]["optional"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							_widget_deconvolve_opt.append(groupbox["deconvolve"]["optional"][dict["group"]])
							groupbox["deconvolve"]["optional"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								groupbox["deconvolve"]["optional"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								groupbox["deconvolve"]["optional"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in groupbox["deconvolve"]["optional"]) or "misc" in groupbox["deconvolve"]["optional"]:
							group = "misc"
							if "group" in dict:
								group = dict["group"]
							if dict["type"] == "bool":
								groupbox["deconvolve"]["optional"][group].layout().addRow(wid_elm.native)
							else:
								groupbox["deconvolve"]["optional"][group].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							groupbox["deconvolve"]["optional"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_deconvolve_opt.append(groupbox["deconvolve"]["optional"]["misc"])
							groupbox["deconvolve"]["optional"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								groupbox["deconvolve"]["optional"]["misc"].layout().addRow(wid_elm.native)
							else:
								groupbox["deconvolve"]["optional"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
					
		self.btn_dec_req_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_dec_req_def.changed.connect
		def btn_dec_req_defaults():
			for key in self.lf_vals["deconvolve"]:
				dict = self.lf_vals["deconvolve"][key]
				if "cat" in dict and dict["cat"] == "required":
					wid_elm = self.gui_elms["deconvolve"][key]
					wid_elm.value = dict["default"]
			
		self.btn_dec_opt_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_dec_opt_def.changed.connect
		def btn_dec_opt_defaults():
			for key in self.lf_vals["deconvolve"]:
				dict = self.lf_vals["deconvolve"][key]
				if "cat" in dict and dict["cat"] == "required":
					pass
				else:
					wid_elm = self.gui_elms["deconvolve"][key]
					wid_elm.value = dict["default"]
					
		if self.lf_vals["misc"]["group_params"]["value"] == False:
			_widget_deconvolve_req.append(self.btn_dec_req_def)			
			_widget_deconvolve_opt.append(self.btn_dec_opt_def)
			self.widget_deconvolve_req = Container(name='Deconvolve Req', widgets=_widget_deconvolve_req)
			self.widget_deconvolve_opt = Container(name='Deconvolve Opt', widgets=_widget_deconvolve_opt)
		else:
			_widget_deconvolve_req.append(self.btn_dec_req_def.native)			
			_widget_deconvolve_opt.append(self.btn_dec_opt_def.native)
			
			self.widget_deconvolve_req = Container(name='Deconvolve Req', widgets=())
			for wid_elm in _widget_deconvolve_req:
				self.widget_deconvolve_req.native.layout().addWidget(wid_elm)
			self.widget_deconvolve_opt = Container(name='Deconvolve Opt', widgets=())
			for wid_elm in _widget_deconvolve_opt:
				self.widget_deconvolve_opt.native.layout().addWidget(wid_elm)
		
		# == HARDWARE ==
		self.gui_elms["hw"] = {}
		_widget_hw = []
		self.gpu_choices = self.get_GPU()
		self.gui_elms["hw"]["gpu_id"] = ComboBox(name='Select Device', label='Select Device', tooltip=LFvals.PLUGIN_ARGS['hw']['gpu_id']['help'], choices=(self.gpu_choices))
		self.platforms_choices = self.get_PlatForms()
		self.gui_elms["hw"]["platform_id"] = ComboBox(name='Select Platform', label='Select Platform', tooltip=LFvals.PLUGIN_ARGS['hw']['platform_id']['help'], choices=(self.platforms_choices))
		# self.cpu_threads_combobox = ComboBox(label=LFvals.PLUGIN_ARGS['calibrate']['num_threads']['label'], tooltip=LFvals.PLUGIN_ARGS['calibrate']['num_threads']['help'], choices=(list(range(1,129))))
		self.gui_elms["hw"]["disable_gpu"] = CheckBox(label=LFvals.PLUGIN_ARGS['hw']['disable_gpu']['label'], value=LFvals.PLUGIN_ARGS['hw']['disable_gpu']['default'])
		self.gui_elms["hw"]["use_single_prec"] = CheckBox(label=LFvals.PLUGIN_ARGS['hw']['use_single_prec']['label'], value=LFvals.PLUGIN_ARGS['hw']['use_single_prec']['default'])
		
		for key in LFvals.PLUGIN_ARGS['hw']:
			wid_elm = self.gui_elms["hw"][key]
			_widget_hw.append(wid_elm)
			
		self.btn_hw_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_hw_def.changed.connect
		def btn_hw_defaults():
			for key in self.lf_vals["hw"]:
				dict = self.lf_vals["hw"][key]
				wid_elm = self.gui_elms["hw"][key]
				if dict["type"] == "int" and type(wid_elm.value).__name__ == "str":
					wid_elm.value = wid_elm.choices[dict["default"]]
				else:
					wid_elm.value = dict["default"]

		_widget_hw.append(self.btn_hw_def)
			
		self.container_hw = Container(name='HW', widgets=_widget_hw)
			
		# == MISC ==
		self.gui_elms["misc"] = {}
		_widget_misc = []

		_misc_widget = QWidget()
		_layout_misc = QFormLayout(_misc_widget)
		_layout_misc.setLabelAlignment(Qt.AlignLeft)
		_layout_misc.setFormAlignment(Qt.AlignRight)
		
		for key in self.lf_vals["misc"]:
			dict = self.lf_vals["misc"][key]
			wid_elm = create_widget(dict)
			self.gui_elms["misc"][key] = wid_elm
			_widget_misc.append(wid_elm)
			if dict["type"] == "bool":
				_layout_misc.addRow(wid_elm.native)
			else:
				_layout_misc.addRow(wid_elm.label, wid_elm.native)
				
		self.btn_misc_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_misc_def.changed.connect
		def btn_misc_defaults():
			for key in self.lf_vals["misc"]:
				dict = self.lf_vals["misc"][key]
				wid_elm = self.gui_elms["misc"][key]
				if key != "lib_ver_label" or (key == "lib_ver_label" and str(self.gui_elms["misc"]["lib_folder"].value) != str(self.lf_vals["misc"]["lib_folder"]["default"])):
					if dict["type"] == "int" and type(wid_elm.value).__name__ == "str":
						wid_elm.value = wid_elm.choices[dict["default"]]
					else:
						wid_elm.value = dict["default"]
				
		_layout_misc.addRow(self.btn_misc_def.native)
		
		self.btn_all_def = PushButton(name='RTD', label='Reset ALL Settings to Defaults')
		@self.btn_all_def.changed.connect
		def btn_all_defaults():			
			btn_cal_req_defaults()
			btn_cal_opt_defaults()
			btn_rec_req_defaults()
			btn_rec_opt_defaults()
			btn_dec_req_defaults()
			btn_dec_opt_defaults()
			btn_hw_defaults()
			btn_misc_defaults()
			self.gui_elms["main"]["comments"].value = self.lf_vals["main"]["comments"]["default"]
			
		_line = QFrame()
		_line.setMinimumWidth(1)
		_line.setFixedHeight(2)
		_line.setFrameShape(QFrame.HLine)
		_line.setFrameShadow(QFrame.Sunken)
		_line.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
		_line.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(0, 255, 0); border-width: 1px;")
		
		_layout_misc.addRow(_line)
		_layout_misc.addRow(self.btn_all_def.native)
		
		self.container_lfa = _misc_widget
		
		# ==================================
		
		self.qtab_widget = QTabWidget()
		
		self.cal_tab = QWidget()
		_cal_tab_layout = QVBoxLayout()
		_cal_tab_layout.setAlignment(Qt.AlignTop)
		self.cal_tab.setLayout(_cal_tab_layout)
		_cal_tab_layout.addWidget(self.widget_calibrate_req.native)
		
		self.cal_tab2 = QWidget()
		_cal_tab_layout2 = QVBoxLayout()
		_cal_tab_layout2.setAlignment(Qt.AlignTop)
		self.cal_tab2.setLayout(_cal_tab_layout2)
		
		_scroll_cal_req = QScrollArea()
		_scroll_cal_req.setWidgetResizable(True)
		_scroll_cal_req.setWidget(self.widget_calibrate_req.native)
		_cal_tab_layout.addWidget(_scroll_cal_req)
		
		_scroll_cal_opt = QScrollArea()
		_scroll_cal_opt.setWidgetResizable(True)
		_scroll_cal_opt.setWidget(self.widget_calibrate_opt.native)
		_cal_tab_layout2.addWidget(_scroll_cal_opt)
		
		self.qtab_cal_tabWidget = QTabWidget()
		self.qtab_cal_tabWidget.setTabPosition(QTabWidget.South)
		self.qtab_cal_tabWidget.addTab(self.cal_tab, 'Required')
		self.qtab_cal_tabWidget.addTab(self.cal_tab2, 'Optional')
		self.qtab_widget.addTab(self.qtab_cal_tabWidget, 'Calibrate')
		
		self.rec_tab = QWidget()
		_rec_tab_layout = QVBoxLayout()
		_rec_tab_layout.setAlignment(Qt.AlignTop)
		self.rec_tab.setLayout(_rec_tab_layout)
		_rec_tab_layout.addWidget(self.widget_rectify_req.native)
		
		self.rec_tab2 = QWidget()
		_rec_tab_layout2 = QVBoxLayout()
		_rec_tab_layout2.setAlignment(Qt.AlignTop)
		self.rec_tab2.setLayout(_rec_tab_layout2)
		_rec_tab_layout2.addWidget(self.widget_rectify_opt.native)
		
		self.qtab_rec_tabWidget = QTabWidget()
		self.qtab_rec_tabWidget.setTabPosition(QTabWidget.South)
		self.qtab_rec_tabWidget.addTab(self.rec_tab, 'Required')
		self.qtab_rec_tabWidget.addTab(self.rec_tab2, 'Optional')
		self.qtab_widget.addTab(self.qtab_rec_tabWidget, 'Rectify')
		
		self.dec_tab = QWidget()
		_dec_tab_layout = QVBoxLayout()
		_dec_tab_layout.setAlignment(Qt.AlignTop)
		self.dec_tab.setLayout(_dec_tab_layout)
		_dec_tab_layout.addWidget(self.widget_deconvolve_req.native)
		
		self.dec_tab2 = QWidget()
		_dec_tab_layout2 = QVBoxLayout()
		_dec_tab_layout2.setAlignment(Qt.AlignTop)
		self.dec_tab2.setLayout(_dec_tab_layout2)
		
		_scroll_dec_opt = QScrollArea()
		_scroll_dec_opt.setWidgetResizable(True)
		_scroll_dec_opt.setWidget(self.widget_deconvolve_opt.native)
		_dec_tab_layout2.addWidget(_scroll_dec_opt)
		
		self.qtab_dec_tabWidget = QTabWidget()
		self.qtab_dec_tabWidget.setTabPosition(QTabWidget.South)
		self.qtab_dec_tabWidget.addTab(self.dec_tab, 'Required')
		self.qtab_dec_tabWidget.addTab(self.dec_tab2, 'Optional')
		self.qtab_widget.addTab(self.qtab_dec_tabWidget, 'Deconvolve')
		
		self.hardware_tab = QWidget()
		_hardware_tab_layout = QVBoxLayout()
		_hardware_tab_layout.setAlignment(Qt.AlignTop)
		self.hardware_tab.setLayout(_hardware_tab_layout)
		self.hardware_tab.layout().addWidget(self.container_hw.native)
		self.qtab_widget.addTab(self.hardware_tab, 'Hardware')
		
		self.lfa_lib_tab = QWidget()
		_lfa_lib_tab_layout = QVBoxLayout()
		_lfa_lib_tab_layout.setAlignment(Qt.AlignTop)
		self.lfa_lib_tab.setLayout(_lfa_lib_tab_layout)
		self.lfa_lib_tab.layout().addWidget(self.container_lfa)
		self.qtab_widget.addTab(self.lfa_lib_tab, 'Misc')
		
		# self.qtab_widget.setMaximumWidth(360)
		# self.qtab_widget.setMaximumHeight(375)
		
		#APP
		# self.widget_logo_info = Container(widgets=[self.logo_label], labels=True)
		self.widget_main_comps = Container(widgets=(), labels=True)
		self.widget_main_comps.native.layout().addWidget(self.cont_btn_status)
		
		self.gui_elms["main"]["comments"].parent.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
		
		self.widget_main = Container(widgets=(), labels=True)
		self.widget_main.native.layout().addWidget(self.qtab_widget)
		
	def refresh_vals(self):
		for section in LFvals.PLUGIN_ARGS:
			if section in self.lf_vals and section in self.gui_elms:
				for key in LFvals.PLUGIN_ARGS[section]:
					if key in self.lf_vals[section] and key in self.gui_elms[section]:
						dict = self.lf_vals[section][key]
						wid_elm = self.gui_elms[section][key]
						if dict["type"] in ["file","folder","str"]:
							dict["value"] = str(wid_elm.value)
						elif LFvals.PLUGIN_ARGS[section][key]["type"] == "int" and type(wid_elm.value).__name__ == "str":
							dict["value"] = self.gui_elms[section][key].native.currentIndex()
						else:
							dict["value"] = wid_elm.value
		
	def set_status_text(self, txt):
		# self.status.value = txt
		self.cont_btn_status_label.value = txt
		
	def set_btns_and_status(self, btn_enab_bool, status_txt):
		# self.status.value = LFvals.PLUGIN_ARGS['main']['status']['value_busy']
		self.cont_btn_status_label.value = status_txt
		self.btn_cal.enabled = btn_enab_bool
		self.btn_rec.enabled = btn_enab_bool
		self.btn_dec.enabled = btn_enab_bool
		
		# load_gif = LFvals.loading_img
		# mov = QMovie(load_gif)
		# mov.setScaledSize(QSize(14, 14))
		# self.status.native.setMovie(mov)
		# mov.start()
			
	def get_GPU(self):
		gpu_list = []
		try:
			for platform in cl.get_platforms():
				gpu_list.append(platform.name.strip('\r\n \x00\t'))
		except:
			pass
		return gpu_list
		
		
	def get_PlatForms(self):
		platforms_list = []
		try:
			for platform in cl.get_platforms():
				for device in platform.get_devices():
					platforms_list.append(device.name.strip('\r\n \x00\t'))
		except:
			pass
		return platforms_list

def create_widget(props):
	widget = None
	try:
		if "widget_type" in props:
			widget = create_widget(widget_type=props['widget_type'])
		elif props["type"] == "str":
			widget = LineEdit(label=props['label'], tooltip=props['help'])
		elif props["type"] == "label":
			widget = Label(label=props['label'], tooltip=props['help'])
		elif props["type"] == "img_label":
			widget = Label(label=props['label'], tooltip=props['help'])
		elif props["type"] == "float":
			widget = FloatSpinBox(label=props['label'], tooltip=props['help'], step=0.01)
		elif props["type"] == "int":
			widget = SpinBox(label=props['label'], tooltip=props['help'], step=1)
		elif props["type"] == "sel":
			widget = ComboBox(label=props['label'], tooltip=props['help'], choices=(props["options"]))
		elif props["type"] == "file":
			widget = FileEdit(label=props['label'], mode='r', tooltip=props['help'], nullable=True)
		elif props["type"] == "folder":
			widget = FileEdit(label=props['label'], mode='d', tooltip=props['help'], nullable=True)
		elif props["type"] == "bool":	
			widget = CheckBox(label=props['label'])
		else:
			pass
			
		if widget != None:
			# if "max" in props:
				# widget.max = props["max"]
			# if "step" in props:
				# widget.step = props["step"]
			for prop in props:
				try:
					getattr(widget, prop)
					setattr(widget, prop, props[prop])
				except:
					pass
				
			widget.value = props["default"]
	except Exception as e:
		print(props)
		print(e)
	return widget