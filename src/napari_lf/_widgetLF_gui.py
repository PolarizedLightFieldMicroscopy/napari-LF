import os, sys, glob, ntpath, subprocess, traceback, json, time
from pathlib import Path
from qtpy import QtCore, QtGui
from qtpy.QtGui import QPixmap, QPainter
from qtpy.QtCore import Qt, QTimer, QSize
from qtpy.QtWidgets import *
from magicgui.widgets import *

try:
	from napari_lf import _widgetLF_vals as LFvals
except:
	import _widgetLF_vals as LFvals

try:	
	import pyopencl as cl
except Exception as e:
	print(e)
	print(traceback.format_exc())

class LFQWidgetGui():
		
	def __init__(self):
		super().__init__()
		self.currentdir = os.path.dirname(os.path.realpath(__file__))
		self.lf_vals = LFvals.PLUGIN_ARGS
		self.settings = {}
		self.gui_elms = {}
		
		# == MAIN ==
		self.gui_elms["main"] = {}
		_widget_main = []
		self.logo_label = Label(value=LFvals.PLUGIN_ARGS['main']['logo_label']['label'], tooltip=LFvals.PLUGIN_ARGS['main']['logo_label']['help'])
		self.logo_label.native.setOpenExternalLinks(True)
		self.logo_label.native.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		self.logo_label.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		# size is controlled via html label height value, set to 60px

		self.info_label = Label(label=f'<h2><center>napari-LF</a></center></h2>')
		dict = LFvals.PLUGIN_ARGS["main"]["img_folder"]
		self.gui_elms["main"]["img_folder"] = create_widget(dict)
		
		dict = LFvals.PLUGIN_ARGS["main"]["img_list"]
		self.gui_elms["main"]["img_list"] = create_widget(dict)
		
		self.btn_open_img = PushButton(label='Open image')
		self.btn_open_img.max_width = 80
		_cont_img_list_btn = Container(name='Image List Open', widgets=[self.gui_elms["main"]["img_list"], self.btn_open_img], layout='horizontal', labels=False)

		dict = LFvals.PLUGIN_ARGS["main"]["metadata_file"]
		self.gui_elms["main"]["metadata_file"] = create_widget(dict)
		
		dict = LFvals.PLUGIN_ARGS["main"]["comments"]
		self.gui_elms["main"]["comments"] = create_widget(dict)
		self.gui_elms["main"]["comments"].native.setPlaceholderText(LFvals.PLUGIN_ARGS['main']['comments']['help'])
		self.commentsArea = self.gui_elms["main"]["comments"].native
		self.commentsArea.setMaximumHeight(60)
		# self.commentsArea.verticalScrollBar().setDisabled(True)
		# self.commentsArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		
		# self.commentsArea = QScrollArea()
		# self.commentsArea.setMaximumHeight(60)
		# self.commentsArea.setWidget(self.gui_elms["main"]["comments"].native)
		# self.commentsArea.setWidgetResizable(True)
		
		dict = LFvals.PLUGIN_ARGS["main"]["presets"]
		self.gui_elms["main"]["presets"] = create_widget(dict)
		self.btn_preset_load = PushButton(label='Load')
		self.btn_preset_save = PushButton(label='Save as..')
		self.btn_preset_delete = PushButton(label='Delete')
		_cont_preset_list_btn = Container(name='Presets', widgets=[self.gui_elms["main"]["presets"], self.btn_preset_load, self.btn_preset_save, self.btn_preset_delete], layout='horizontal', labels=False)
		_cont_preset_list_btn.native.layout().setContentsMargins(0,0,0,0)
		_cont_preset_list_btn.native.layout().setSpacing(2)
				
		self.btn_cal = PushButton(label='Calibrate')
		self.btn_cal.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.btn_cal_prog = Label()
		# self.btn_cal_prog.native.setFixedSize(20,20)
		self.btn_cal_prog.native.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		self.btn_cal_prog.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

		self.btn_rec = PushButton(label='Rectify')
		self.btn_rec.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.btn_rec_prog = Label()
		# self.btn_rec_prog.native.setFixedSize(20,20)
		self.btn_rec_prog.native.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		self.btn_rec_prog.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		
		self.btn_dec = PushButton(label='Deconvolve')
		self.btn_dec.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.btn_dec_prog = Label()
		# self.btn_dec_prog.native.setFixedSize(20,20)
		self.btn_dec_prog.native.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		self.btn_dec_prog.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		
		_cont_btn_checks = Container(name='Btn_chks', widgets=[self.btn_cal_prog, self.btn_rec_prog, self.btn_dec_prog], labels=False, layout='horizontal')
		_cont_btn_btns = Container(name='Btn press', widgets=[self.btn_cal, self.btn_rec, self.btn_dec], labels=False, layout='horizontal')
		
		_cont_btn_QFormLayout = QFormLayout()
		_cont_btn_QFormLayout.setSpacing(0)
		_cont_btn_QFormLayout.setContentsMargins(0,0,0,0)
		_cont_btn_QFormLayout.addRow(_cont_btn_checks.native)
		_cont_btn_QFormLayout.addRow(_cont_btn_btns.native)
		
		_cont_btn_widget = QWidget()
		_cont_btn_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		_cont_btn_widget.setLayout(_cont_btn_QFormLayout)
		
		_cont_btn_left = Container(name='btn Left', widgets=(), labels=False)
		_cont_btn_left.native.layout().addWidget(_cont_btn_widget)
		
		self.btn_stop = PushButton(label='Stop')
		self.btn_stop.min_height = 60
		self.btn_stop.min_width = 60
		
		_cont_btn_right = Container(name='btn Right', widgets=[self.btn_stop], labels=False)
		self._cont_btn_processing = Container(widgets=[_cont_btn_left, _cont_btn_right], labels=False, layout='horizontal')
		self._cont_btn_processing.native.layout().setContentsMargins(0,0,0,0)
		self._cont_btn_processing.native.layout().setSpacing(0)
		
		
		self.btn_nn_proc = PushButton(label='Deconvolve')
		self.btn_nn_proc.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.btn_nn_proc_prog = Label()
		# self.btn_dec_prog.native.setFixedSize(20,20)
		self.btn_nn_proc_prog.native.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		self.btn_nn_proc_prog.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		
		_cont_btn_checks2 = Container(name='Btn_chks', widgets=[self.btn_nn_proc_prog], labels=False, layout='horizontal')
		_cont_btn_btns2 = Container(name='Btn press', widgets=[self.btn_nn_proc], labels=False, layout='horizontal')
		
		_cont_btn_QFormLayout2 = QFormLayout()
		_cont_btn_QFormLayout2.setSpacing(0)
		_cont_btn_QFormLayout2.setContentsMargins(0,0,0,0)
		_cont_btn_QFormLayout2.addRow(_cont_btn_checks2.native)
		_cont_btn_QFormLayout2.addRow(_cont_btn_btns2.native)
		
		_cont_btn_widget2 = QWidget()
		_cont_btn_widget2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		_cont_btn_widget2.setLayout(_cont_btn_QFormLayout2)
		
		_cont_btn_left2 = Container(name='btn Left', widgets=(), labels=False)
		_cont_btn_left2.native.layout().addWidget(_cont_btn_widget2)
		
		self.btn_stop2 = PushButton(label='Stop')
		self.btn_stop2.min_height = 60
		self.btn_stop2.min_width = 60
		
		_cont_btn_right2 = Container(name='btn Right', widgets=[self.btn_stop2], labels=False)
		self._cont_btn_processing2 = Container(widgets=[_cont_btn_left2, _cont_btn_right2], labels=False, layout='horizontal')
		self._cont_btn_processing2.native.layout().setContentsMargins(0,0,0,0)
		
		
		_QFormLayout = QFormLayout()
		_QFormLayout.setContentsMargins(0,0,0,0)
		_QFormLayout.setSpacing(0)
		self.cont_btn_top = QWidget()
		self.cont_btn_top.setLayout(_QFormLayout)
		#_QFormLayout.setContentsMargins(1,1,1,1)
		
		if LFvals.dev_true:
			_cont_btn_checks.native.setStyleSheet("border: 1px dashed white;")
			_cont_btn_btns.native.setStyleSheet("border: 1px dashed white;")
			_cont_btn_widget.setStyleSheet("border: 1px dashed white;")
			self._cont_btn_processing.native.setStyleSheet("border: 1px dashed white;")
			_cont_btn_checks2.native.setStyleSheet("border: 1px dashed white;")
			_cont_btn_btns2.native.setStyleSheet("border: 1px dashed white;")
			_cont_btn_widget2.setStyleSheet("border: 1px dashed white;")
			self._cont_btn_processing2.native.setStyleSheet("border: 1px dashed white;")
		
		_QFormLayout.addRow(self.logo_label.native)
		
		self.LFAnalyze_btn = PicButton(QPixmap(LFvals.LFAnalyze_logo_btn_img), QPixmap(LFvals.LFAnalyze_logo_btn_hov_img), QPixmap(LFvals.LFAnalyze_logo_btn_act_img))
		self.LFAnalyze_btn_cont = Container(name='LFAnalyze_btn', widgets=())
		self.LFAnalyze_btn_cont.native.layout().addWidget(self.LFAnalyze_btn)
		
		self.LFAnalyze_btn.setMaximumHeight(45)
		self.LFAnalyze_btn.setMaximumHeight(200)
		# self.LFAnalyze_btn.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		self.LFAnalyze_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		self.LFAnalyze_btn.clicked.connect(self.LFAnalyze_btn_call)
		
		self.NeuralNet_btn = PicButton(QPixmap(LFvals.NeuralNet_logo_btn_img),QPixmap(LFvals.NeuralNet_logo_btn_hov_img),QPixmap(LFvals.NeuralNet_logo_btn_act_img))
		self.NeuralNet_btn_cont = Container(name='NeuralNet_btn', widgets=())
		self.NeuralNet_btn_cont.native.layout().addWidget(self.NeuralNet_btn)
		
		self.NeuralNet_btn.setMaximumHeight(45)
		self.NeuralNet_btn.setMaximumHeight(200)
		# self.NeuralNet_btn.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		self.NeuralNet_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		self.NeuralNet_btn.clicked.connect(self.NeuralNet_btn_call)
		self.NeuralNet_btn_cont.hide()
		
		_processing_methods = QWidget()
		hBoxLayout = QHBoxLayout()
		hBoxLayout.addWidget(self.LFAnalyze_btn_cont.native)
		hBoxLayout.addWidget(self.NeuralNet_btn_cont.native)
		_processing_methods.setLayout(hBoxLayout)
		_processing_methods.layout().setAlignment(Qt.AlignCenter|Qt.AlignHCenter)
		_processing_methods.layout().setContentsMargins(0,0,0,0)
		_processing_methods.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		
		_QFormLayoutData = QFormLayout()
		_QFormLayoutData.setContentsMargins(0,0,0,0)
		_QFormLayoutData.setSpacing(0)
		_QFormLayoutData.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
		_widget_data = QWidget()
		_widget_data.setLayout(_QFormLayoutData)
		_QFormLayoutData.addRow(self.gui_elms["main"]["img_folder"].label, self.gui_elms["main"]["img_folder"].native)
		_QFormLayoutData.addRow(_cont_img_list_btn.native)
		_QFormLayoutData.addRow(_processing_methods)
		if self.gui_elms["main"]["metadata_file"].visible:
			_QFormLayoutData.addRow(self.gui_elms["main"]["metadata_file"].label, self.gui_elms["main"]["metadata_file"].native)
			
		self.container_data = Container(name='Data', widgets=())
		self.container_data.native.layout().addWidget(_widget_data)
		
		self.qtab_widget_top = QTabWidget()
		tabBar = TabBar()
		tabBar.setDrawBase(False)
		self.qtab_widget_top.setTabBar(tabBar)
		self.qtab_widget_top.setTabPosition(QTabWidget.West)
		self.qtab_widget_top.setTabShape(QTabWidget.Triangular)
		self.qtab_widget_top.setLayout(QFormLayout())
		self.qtab_widget_top.layout().setContentsMargins(0,0,0,0)
		self.qtab_widget_top.layout().setSpacing(0)
		
		self.data_tab = QWidget()
		_data_tab_layout = QVBoxLayout()
		_data_tab_layout.setAlignment(Qt.AlignTop)
		self.data_tab.setLayout(_data_tab_layout)
		self.data_tab.layout().addWidget(self.container_data.native)
		self.qtab_widget_top.addTab(self.data_tab, 'Processing')
		
		self.hardware_tab = QWidget()
		_hardware_tab_layout = QVBoxLayout()
		_hardware_tab_layout.setAlignment(Qt.AlignTop)
		self.hardware_tab.setLayout(_hardware_tab_layout)
		
		self.qtab_widget_top.addTab(self.hardware_tab, 'Hardware')
		
		self.lfa_lib_tab = QWidget()
		_lfa_lib_tab_layout = QVBoxLayout()
		_lfa_lib_tab_layout.setAlignment(Qt.AlignTop)
		self.lfa_lib_tab.setLayout(_lfa_lib_tab_layout)
		
		self.qtab_widget_top.addTab(self.lfa_lib_tab, 'Misc')
		
		self._about_tab = QWidget()
		_about_tab_layout = QFormLayout()
		_about_tab_layout.setAlignment(Qt.AlignTop)
		_about_tab_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
		self._about_tab.setLayout(_about_tab_layout)
		
		
		_line = QFrame()
		_line.setMinimumWidth(1)
		_line.setFixedHeight(2)
		_line.setFrameShape(QFrame.HLine)
		_line.setFrameShadow(QFrame.Sunken)
		_line.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
		_line.setStyleSheet("margin:1px; padding:2px; border:1px solid rgb(128,128,128); border-width: 1px;")
		
		_line2 = QFrame()
		_line2.setMinimumWidth(1)
		_line2.setFixedHeight(2)
		_line2.setFrameShape(QFrame.HLine)
		_line2.setFrameShadow(QFrame.Sunken)
		_line2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
		_line2.setStyleSheet("margin:1px; padding:2px; border:1px solid rgb(128,128,128); border-width: 1px;")
		
		try:
			from ._version import version as __version__
		except ImportError:
			__version__ = "unknown"
		
		self.NapariLF_ver_label = Label(value=LFvals.PLUGIN_ARGS['main']['NapariLF_ver_label']['label'], tooltip=LFvals.PLUGIN_ARGS['main']['NapariLF_ver_label']['help'])
		self.NapariLF_ver_label.native.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		self.NapariLF_ver_label.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		
		self.LFAnalyze_logo_label = Label(value=LFvals.PLUGIN_ARGS['main']['LFAnalyze_logo_label']['label'], tooltip=LFvals.PLUGIN_ARGS['main']['LFAnalyze_logo_label']['help'])
		self.LFAnalyze_logo_label.native.setOpenExternalLinks(True)
		self.LFAnalyze_logo_label.native.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		self.LFAnalyze_logo_label.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		
		self.LFMNet_logo_label = Label(value=LFvals.PLUGIN_ARGS['main']['LFMNet_logo_label']['label'], tooltip=LFvals.PLUGIN_ARGS['main']['LFMNet_logo_label']['help'])
		self.LFMNet_logo_label.native.setOpenExternalLinks(True)
		self.LFMNet_logo_label.native.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		self.LFMNet_logo_label.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		
		self.NapariLF_ver_label.native.setText(LFvals.PLUGIN_ARGS["main"]["NapariLF_ver_label"]["label"] + __version__)
		_about_tab_layout.addRow(self.NapariLF_ver_label.native)
		_about_tab_layout.addRow(_line)
		_about_tab_layout.addRow(self.LFAnalyze_logo_label.native)
		_about_tab_layout.addRow(self.LFMNet_logo_label.native)
		_about_tab_layout.addRow(_line2)
		self.qtab_widget_top.addTab(self._about_tab, 'About')
		
		_QFormLayout.addRow(self.qtab_widget_top)

		
			
		# _QFormLayout.addRow(self.gui_elms["main"]["presets"].label, _cont_preset_list_btn.native)
		# _QFormLayout.addRow(self.gui_elms["main"]["comments"].label, self.commentsArea)
		
		_cont_preset_list_btn.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		#_QFormLayout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
		self.cont_btn_top.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		
		_QFormLayout2 = QFormLayout()
		self.cont_btn_status = QWidget()
		self.cont_btn_status.setLayout(_QFormLayout2)
		_QFormLayout2.setContentsMargins(0,0,0,0)
		_QFormLayout2.setSpacing(0)
		
		self.cont_btn_status_label = Label()
		self.cont_btn_status_label.native.setStyleSheet("color: rgb(0, 128, 0)")
		self.cont_btn_status_label.value = ':STATUS: ' + LFvals.PLUGIN_ARGS['main']['status']['value_idle']
		
		_QFormLayout2.addRow(self.cont_btn_status_label.native)
		
		self.cont_btn_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self.cont_btn_status_label.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self.cont_btn_status_label.native.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)

		self.groupbox = {"calibrate":{"required":{},"optional":{},"inspect":{}},"rectify":{"required":{},"optional":{}},"deconvolve":{"required":{},"optional":{}}, "projections":{}, "lfmnet":{}}
		
		# == CALIBATE ==
		_widget_calibrate_req = []
		_widget_calibrate_opt = []
		_widget_calibrate_ins = []
		self.gui_elms["calibrate"] = {}
		
		# (not working) method to only create gui options for visible parameters
		visible_cal_keys = []
		for key in self.lf_vals["calibrate"]:
			dict = self.lf_vals["calibrate"][key]
			if "visible" in dict:
				if dict["visible"] == True:
					visible_cal_keys.append(key)
			else:
				visible_cal_keys.append(key)

		# for key in visible_cal_keys:
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
						if "group" in dict and dict["group"] not in self.groupbox["calibrate"]["required"]:
							self.groupbox["calibrate"]["required"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
							_widget_calibrate_req.append(self.groupbox["calibrate"]["required"][dict["group"]])
							self.groupbox["calibrate"]["required"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["required"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["required"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["calibrate"]["required"]) or "misc" in self.groupbox["calibrate"]["required"]:
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["required"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["required"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["calibrate"]["required"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
							_widget_calibrate_req.append(self.groupbox["calibrate"]["required"]["misc"])
							self.groupbox["calibrate"]["required"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["required"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["required"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
				elif "cat" in dict and dict["cat"] == "inspect":
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_calibrate_ins.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in self.groupbox["calibrate"]["inspect"]:
							self.groupbox["calibrate"]["inspect"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
							_widget_calibrate_ins.append(self.groupbox["calibrate"]["inspect"][dict["group"]])
							self.groupbox["calibrate"]["inspect"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["inspect"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["inspect"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["calibrate"]["inspect"]) or "misc" in self.groupbox["calibrate"]["inspect"]:
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["inspect"][dict["group"]].layout().addRow(wid_elm.native)
							elif "no_label_layout_style" in dict and dict["no_label_layout_style"] == True:
								self.groupbox["calibrate"]["inspect"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["inspect"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["calibrate"]["inspect"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
							_widget_calibrate_ins.append(self.groupbox["calibrate"]["inspect"]["misc"])
							self.groupbox["calibrate"]["inspect"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["inspect"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["inspect"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
				else:
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_calibrate_opt.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in self.groupbox["calibrate"]["optional"]:
							self.groupbox["calibrate"]["optional"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
							_widget_calibrate_opt.append(self.groupbox["calibrate"]["optional"][dict["group"]])
							self.groupbox["calibrate"]["optional"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["optional"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["optional"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["calibrate"]["optional"]) or "misc" in self.groupbox["calibrate"]["optional"]:
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["optional"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["optional"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["calibrate"]["optional"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
							_widget_calibrate_opt.append(self.groupbox["calibrate"]["optional"]["misc"])
							self.groupbox["calibrate"]["optional"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["calibrate"]["optional"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["calibrate"]["optional"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
								
		self.btn_cal_req_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_cal_req_def.changed.connect
		def btn_cal_req_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["calibrate"]:
					dict = self.lf_vals["calibrate"][key]
					if "cat" in dict and dict["cat"] == "required":
						wid_elm = self.gui_elms["calibrate"][key]
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()
		
		self.btn_cal_opt_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_cal_opt_def.changed.connect
		def btn_cal_opt_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["calibrate"]:
					dict = self.lf_vals["calibrate"][key]
					if "cat" in dict and dict["cat"] == "required":
						pass
					else:
						wid_elm = self.gui_elms["calibrate"][key]
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()
		
		if self.lf_vals["misc"]["group_params"]["value"] == False:
			_widget_calibrate_req.append(self.btn_cal_req_def)			
			_widget_calibrate_opt.append(self.btn_cal_opt_def)
			self.widget_calibrate_req = Container(name='Calibrate Req', widgets=_widget_calibrate_req)
			self.widget_calibrate_opt = Container(name='Calibrate Opt', widgets=_widget_calibrate_opt)
			self.widget_calibrate_ins = Container(name='Calibrate Opt', widgets=_widget_calibrate_ins)
		else:
			_widget_calibrate_req.append(self.btn_cal_req_def.native)			
			_widget_calibrate_opt.append(self.btn_cal_opt_def.native)
			
			self.widget_calibrate_req = Container(name='Calibrate Req', widgets=())
			for wid_elm in _widget_calibrate_req:
				self.widget_calibrate_req.native.layout().addWidget(wid_elm)
			self.widget_calibrate_opt = Container(name='Calibrate Opt', widgets=())
			for wid_elm in _widget_calibrate_opt:
				self.widget_calibrate_opt.native.layout().addWidget(wid_elm)
			self.widget_calibrate_ins = Container(name='Calibrate Ins', widgets=())
			for wid_elm in _widget_calibrate_ins:
				self.widget_calibrate_ins.native.layout().addWidget(wid_elm)
		
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
						if "group" in dict and dict["group"] not in self.groupbox["rectify"]["required"]:
							self.groupbox["rectify"]["required"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
							_widget_rectify_req.append(self.groupbox["rectify"]["required"][dict["group"]])
							self.groupbox["rectify"]["required"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["rectify"]["required"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["rectify"]["required"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["rectify"]["required"]) or "misc" in self.groupbox["rectify"]["required"]:
							group = "misc"
							if "group" in dict:
								group = dict["group"]
							if dict["type"] == "bool":
								self.groupbox["rectify"]["required"][group].layout().addRow(wid_elm.native)
							else:
								self.groupbox["rectify"]["required"][group].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["rectify"]["required"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
							_widget_rectify_req.append(self.groupbox["rectify"]["required"]["misc"])
							self.groupbox["rectify"]["required"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["rectify"]["required"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["rectify"]["required"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
				else:
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_rectify_opt.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in self.groupbox["rectify"]["optional"]:
							self.groupbox["rectify"]["optional"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
							_widget_rectify_opt.append(self.groupbox["rectify"]["optional"][dict["group"]])
							self.groupbox["rectify"]["optional"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["rectify"]["optional"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["rectify"]["optional"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["rectify"]["optional"]) or "misc" in self.groupbox["rectify"]["optional"]:
							group = "misc"
							if "group" in dict:
								group = dict["group"]
							if dict["type"] == "bool":
								self.groupbox["rectify"]["optional"][group].layout().addRow(wid_elm.native)
							else:
								self.groupbox["rectify"]["optional"][group].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["rectify"]["optional"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							_widget_rectify_opt.append(self.groupbox["rectify"]["optional"]["misc"])
							self.groupbox["rectify"]["optional"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["rectify"]["optional"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["rectify"]["optional"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
					
		self.btn_rec_req_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_rec_req_def.changed.connect
		def btn_rec_req_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["rectify"]:
					dict = self.lf_vals["rectify"][key]
					if "cat" in dict and dict["cat"] == "required":
						wid_elm = self.gui_elms["rectify"][key]
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()
		
		self.btn_rec_opt_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_rec_opt_def.changed.connect
		def btn_rec_opt_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["rectify"]:
					dict = self.lf_vals["rectify"][key]
					if "cat" in dict and dict["cat"] == "required":
						pass
					else:
						wid_elm = self.gui_elms["rectify"][key]
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()
						
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
						if "group" in dict and dict["group"] not in self.groupbox["deconvolve"]["required"]:
							self.groupbox["deconvolve"]["required"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
							_widget_deconvolve_req.append(self.groupbox["deconvolve"]["required"][dict["group"]])
							self.groupbox["deconvolve"]["required"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["deconvolve"]["required"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["deconvolve"]["required"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["deconvolve"]["required"]) or "misc" in self.groupbox["deconvolve"]["required"]:
							group = "misc"
							if "group" in dict:
								group = dict["group"]
							if dict["type"] == "bool":
								self.groupbox["deconvolve"]["required"][group].layout().addRow(wid_elm.native)
							else:
								self.groupbox["deconvolve"]["required"][group].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["deconvolve"]["required"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
							_widget_deconvolve_req.append(self.groupbox["deconvolve"]["required"]["misc"])
							self.groupbox["deconvolve"]["required"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["deconvolve"]["required"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["deconvolve"]["required"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
				else:
					if self.lf_vals["misc"]["group_params"]["value"] == False:
						_widget_deconvolve_opt.append(wid_elm)
					else:
						if "group" in dict and dict["group"] not in self.groupbox["deconvolve"]["optional"]:
							self.groupbox["deconvolve"]["optional"][dict["group"]] = QGroupBox(dict["group"])
							vbox = QFormLayout()
							vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
							_widget_deconvolve_opt.append(self.groupbox["deconvolve"]["optional"][dict["group"]])
							self.groupbox["deconvolve"]["optional"][dict["group"]].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["deconvolve"]["optional"][dict["group"]].layout().addRow(wid_elm.native)
							else:
								self.groupbox["deconvolve"]["optional"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
						elif ("group" in dict and dict["group"] in self.groupbox["deconvolve"]["optional"]) or "misc" in self.groupbox["deconvolve"]["optional"]:
							group = "misc"
							if "group" in dict:
								group = dict["group"]
							if dict["type"] == "bool":
								self.groupbox["deconvolve"]["optional"][group].layout().addRow(wid_elm.native)
							else:
								self.groupbox["deconvolve"]["optional"][group].layout().addRow(wid_elm.label, wid_elm.native)
						else:
							self.groupbox["deconvolve"]["optional"]["misc"] = QGroupBox("Misc")
							vbox = QFormLayout()
							vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
							_widget_deconvolve_opt.append(self.groupbox["deconvolve"]["optional"]["misc"])
							self.groupbox["deconvolve"]["optional"]["misc"].setLayout(vbox)
							if dict["type"] == "bool":
								self.groupbox["deconvolve"]["optional"]["misc"].layout().addRow(wid_elm.native)
							else:
								self.groupbox["deconvolve"]["optional"]["misc"].layout().addRow(wid_elm.label, wid_elm.native)
					
		self.btn_dec_req_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_dec_req_def.changed.connect
		def btn_dec_req_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["deconvolve"]:
					dict = self.lf_vals["deconvolve"][key]
					if "cat" in dict and dict["cat"] == "required":
						wid_elm = self.gui_elms["deconvolve"][key]
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()
			
		self.btn_dec_opt_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_dec_opt_def.changed.connect
		def btn_dec_opt_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["deconvolve"]:
					dict = self.lf_vals["deconvolve"][key]
					if "cat" in dict and dict["cat"] == "required":
						pass
					else:
						wid_elm = self.gui_elms["deconvolve"][key]
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()
					
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
		
		# == PROJECTIONS ==
		self.gui_elms["projections"] = {}
		self.groupbox["projections"] = {}
		_widget_projections = []
		for key in LFvals.PLUGIN_ARGS['projections']:
			dict = LFvals.PLUGIN_ARGS["projections"][key]
			if "group" in dict and dict["group"] not in self.groupbox["projections"] and self.lf_vals["misc"]["group_params"]["value"] == True:
				self.groupbox["projections"][dict["group"]] = QGroupBox(dict["group"])
				vbox = QFormLayout()
				vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
				_widget_projections.append(self.groupbox["projections"][dict["group"]])
				self.groupbox["projections"][dict["group"]].setLayout(vbox)
			if "label" not in dict:
				dict["label"] = dict["dest"]
			wid_elm = create_widget(dict)
			self.gui_elms["projections"][key] = wid_elm
			if "group" in dict:
				if self.lf_vals["misc"]["group_params"]["value"] == False:
					_widget_projections.append(wid_elm)
				else:
					if dict["type"] == "bool":
						self.groupbox["projections"][dict["group"]].layout().addRow(wid_elm.native)
					elif "no_label_layout_style" in dict and dict["no_label_layout_style"] == True:
						self.groupbox["projections"][dict["group"]].layout().addRow(wid_elm.native)
					elif "label_btn" in dict:
						self.groupbox["projections"][dict["group"]].layout().addRow(dict["label_btn"], wid_elm.native)
					else:
						self.groupbox["projections"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
			else:
				_widget_projections.append(wid_elm)
				
		if self.lf_vals["misc"]["group_params"]["value"] == False:	
			self.container_projections = Container(name='Projections', widgets=_widget_projections)
		else:		
			self.container_projections = Container(name='Projections', widgets=())
			for wid_elm in _widget_projections:
				self.container_projections.native.layout().addWidget(wid_elm)
		
		# == LFMNET ==
		self.gui_elms["lfmnet"] = {}
		self.groupbox["lfmnet"] = {}
		_widget_lfmnet = []
		for key in LFvals.PLUGIN_ARGS['lfmnet']:
			dict = LFvals.PLUGIN_ARGS["lfmnet"][key]
			if "group" in dict and dict["group"] not in self.groupbox["lfmnet"] and self.lf_vals["misc"]["group_params"]["value"] == True:
				self.groupbox["lfmnet"][dict["group"]] = QGroupBox(dict["group"])
				vbox = QFormLayout()
				vbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
				_widget_lfmnet.append(self.groupbox["lfmnet"][dict["group"]])
				self.groupbox["lfmnet"][dict["group"]].setLayout(vbox)
			if "label" not in dict:
				dict["label"] = dict["dest"]
			wid_elm = create_widget(dict)
			self.gui_elms["lfmnet"][key] = wid_elm
			if "group" in dict:
				if self.lf_vals["misc"]["group_params"]["value"] == False:
					_widget_lfmnet.append(wid_elm)
				else:
					if "visible" in dict and dict["visible"] == False:
						pass
					else:
						if dict["type"] == "bool":
							self.groupbox["lfmnet"][dict["group"]].layout().addRow(wid_elm.native)
						elif "no_label_layout_style" in dict and dict["no_label_layout_style"] == True:
							self.groupbox["lfmnet"][dict["group"]].layout().addRow(wid_elm.native)
						else:
							self.groupbox["lfmnet"][dict["group"]].layout().addRow(wid_elm.label, wid_elm.native)
			else:
				_widget_lfmnet.append(wid_elm)
				
		if self.lf_vals["misc"]["group_params"]["value"] == False:	
			self.container_lfmnet = Container(name='LFM-NET', widgets=_widget_lfmnet)
		else:		
			self.container_lfmnet = Container(name='LFM-NET', widgets=())
			for wid_elm in _widget_lfmnet:
				self.container_lfmnet.native.layout().addWidget(wid_elm)

		
		# == HARDWARE ==
		self.gui_elms["hw"] = {}
		_widget_hw = []
		self.gpu_choices = self.get_GPU()
		self.gui_elms["hw"]["gpu_id"] = ComboBox(name='Device', label='Device', tooltip=LFvals.PLUGIN_ARGS['hw']['gpu_id']['help'], choices=(self.gpu_choices))
		self.platforms_choices = self.get_PlatForms()
		self.gui_elms["hw"]["platform_id"] = ComboBox(name='Platform', label='Platform', tooltip=LFvals.PLUGIN_ARGS['hw']['platform_id']['help'], choices=(self.platforms_choices))
		# self.cpu_threads_combobox = ComboBox(label=LFvals.PLUGIN_ARGS['calibrate']['num_threads']['label'], tooltip=LFvals.PLUGIN_ARGS['calibrate']['num_threads']['help'], choices=(list(range(1,129))))
		self.gui_elms["hw"]["disable_gpu"] = CheckBox(label=LFvals.PLUGIN_ARGS['hw']['disable_gpu']['label'], value=LFvals.PLUGIN_ARGS['hw']['disable_gpu']['default'], tooltip=LFvals.PLUGIN_ARGS['hw']['disable_gpu']['help'])
		self.gui_elms["hw"]["use_single_prec"] = CheckBox(label=LFvals.PLUGIN_ARGS['hw']['use_single_prec']['label'], value=LFvals.PLUGIN_ARGS['hw']['use_single_prec']['default'], tooltip=LFvals.PLUGIN_ARGS['hw']['use_single_prec']['help'])
		
		for key in LFvals.PLUGIN_ARGS['hw']:
			wid_elm = self.gui_elms["hw"][key]
			_widget_hw.append(wid_elm)
			
		self.btn_hw_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_hw_def.changed.connect
		def btn_hw_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["hw"]:
					dict = self.lf_vals["hw"][key]
					wid_elm = self.gui_elms["hw"][key]
					if dict["type"] == "int" and type(wid_elm.value).__name__ == "str":
						try:
							wid_elm.value = wid_elm.choices[dict["default"]]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
					else:
						try:
							if wid_elm.widget_type == 'ComboBox':
								if dict["default"] in wid_elm.choices:
									wid_elm.value = dict["default"]
								elif len(wid_elm.choices) == 0:
									pass
								else:
									wid_elm.value = wid_elm.choices[0]
							else:
								wid_elm.value = dict["default"]
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				self.verify_preset_vals()

		_widget_hw.append(self.btn_hw_def)
			
		self.container_hw = Container(name='HW', widgets=_widget_hw)
		self.hardware_tab.layout().addWidget(self.container_hw.native)
		
			
		# == MISC ==
		self.gui_elms["misc"] = {}
		_widget_misc = []

		_misc_widget = QWidget()
		_layout_misc = QFormLayout(_misc_widget)
		_layout_misc.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
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
				
		self.btn_misc_cls = PushButton(name='CLS', label='Clear Terminal')
		@self.btn_misc_cls.changed.connect
		def btn_misc_cls():
			os.system('cls' if os.name == 'nt' else 'clear')
			
		_layout_misc.addRow(self.btn_misc_cls.native)
				
		self.btn_misc_def = PushButton(name='RTD', label='Reset to Defaults')
		@self.btn_misc_def.changed.connect
		def btn_misc_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				for key in self.lf_vals["misc"]:
					dict = self.lf_vals["misc"][key]
					wid_elm = self.gui_elms["misc"][key]
					if key != "lib_ver_label" or (key == "lib_ver_label" and str(self.gui_elms["misc"]["lib_folder"].value) != str(self.lf_vals["misc"]["lib_folder"]["default"])):
						if dict["type"] == "int" and type(wid_elm.value).__name__ == "str":
							try:
								wid_elm.value = wid_elm.choices[dict["default"]]
							except Exception as e:
								print(e)
								print(traceback.format_exc())
						else:
							try:
								if wid_elm.widget_type == 'ComboBox':
									if dict["default"] in wid_elm.choices:
										wid_elm.value = dict["default"]
									elif len(wid_elm.choices) == 0:
										pass
									else:
										wid_elm.value = wid_elm.choices[0]
								else:
									wid_elm.value = dict["default"]
							except Exception as e:
								print(e)
								print(traceback.format_exc())
				self.verify_preset_vals()
				
		_layout_misc.addRow(self.btn_misc_def.native)
		
		self.btn_all_def = PushButton(name='RTD', label='Reset ALL Settings to Defaults')
		@self.btn_all_def.changed.connect
		def btn_all_defaults():
			qm = QMessageBox
			ret = qm.question(QWidget(),'', "Reset ALL Values to Default ?", qm.Yes | qm.No)
			if ret == qm.Yes:
				btn_cal_req_defaults()
				btn_cal_opt_defaults()
				btn_rec_req_defaults()
				btn_rec_opt_defaults()
				btn_dec_req_defaults()
				btn_dec_opt_defaults()
				btn_hw_defaults()
				btn_misc_defaults()
				self.gui_elms["main"]["comments"].value = self.lf_vals["main"]["comments"]["default"]
				self.verify_preset_vals()
			
		_line = QFrame()
		_line.setMinimumWidth(1)
		_line.setFixedHeight(2)
		_line.setFrameShape(QFrame.HLine)
		_line.setFrameShadow(QFrame.Sunken)
		_line.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
		_line.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(128,128,128); border-width: 1px;")
		
		_layout_misc.addRow(_line)
		_layout_misc.addRow(self.btn_all_def.native)
		
		self.container_lfa = _misc_widget
		self.lfa_lib_tab.layout().addWidget(self.container_lfa)
		
		
		
		# bind values between props
		# @self.gui_elms["calibrate"]["ulens_focal_length"].changed.connect
		def copy_vals():
			self.gui_elms["calibrate"]["ulens_focal_distance"].value = self.gui_elms["calibrate"]["ulens_focal_length"].value
		
		@self.btn_preset_load.changed.connect
		def load_presets():
			preset_sel = self.gui_elms["main"]["presets"].value
			if preset_sel is not None and preset_sel != "":
				if "preset_choices" in self.settings:
					if preset_sel in self.settings["preset_choices"]:
						loaded_preset_vals = self.settings["preset_choices"][preset_sel]
						for section in loaded_preset_vals:
							for prop in loaded_preset_vals[section]:
								try:
									if self.gui_elms[section][prop].widget_type == 'ComboBox':
										if loaded_preset_vals[section][prop] in self.gui_elms[section][prop].choices:
											self.gui_elms[section][prop].value = loaded_preset_vals[section][prop]
										elif len(self.gui_elms[section][prop].choices) == 0:
											pass
										else:
											self.gui_elms[section][prop].value = self.gui_elms[section][prop].choices[0]
									else:
										self.gui_elms[section][prop].value = loaded_preset_vals[section][prop]
								except Exception as e:
									print(e)
									print(traceback.format_exc())
			
		@self.btn_preset_save.changed.connect
		def save_presets():
			name = self.get_preset_name()
			if name == None:
				return
			if "preset_choices" not in self.settings:
				self.settings["preset_choices"] = {}
			
			preset_vals = {}
			for section in ["calibrate", "rectify", "deconvolve"]:
				preset_vals[section] = {}
				for prop in LFvals.PLUGIN_ARGS[section]:
					if "exclude_from_settings" in LFvals.PLUGIN_ARGS[section][prop] and LFvals.PLUGIN_ARGS[section][prop]["exclude_from_settings"] == True:
						pass
					else:
						if LFvals.PLUGIN_ARGS[section][prop]["type"] in ["file","folder","str"]:
							preset_vals[section][prop] = str(self.gui_elms[section][prop].value)
						else:
							preset_vals[section][prop] = self.gui_elms[section][prop].value
			
			self.settings["preset_choices"][name] = preset_vals
			self.save_plugin_prefs()
			self.refresh_preset_choices()
			self.gui_elms["main"]["presets"].value = name
			
		@self.btn_preset_delete.changed.connect
		def delete_presets():
			preset_sel = self.gui_elms["main"]["presets"].value
			if preset_sel is not None and preset_sel != "":
				if "preset_choices" in self.settings:
					if preset_sel in self.settings["preset_choices"]:
						del(self.settings["preset_choices"][preset_sel])
						self.save_plugin_prefs()
						self.refresh_preset_choices()
		
		@self.gui_elms["calibrate"]["calibration_files"].changed.connect
		def cal_img_list_inspect():
			img_selected = str(self.gui_elms["calibrate"]["calibration_files"].value)
			img_folder = str(self.gui_elms["main"]["img_folder"].value)
			img_file_path = os.path.join(img_folder, img_selected)
			
			import h5py
			
			str_data = []
			with h5py.File(img_file_path, "r") as f:
				for data_key in f.attrs.keys():
						data = f.attrs[data_key]
						str_data.append(str(data_key) +' : '+ str(data))
						str_data.append("\n")
				# List all groups
				groups = f.keys()
				str_data.append("=== Groups: %s ===" % list(groups))
				str_data.append("\n")
				for group in groups:
					str_data.append("--- Group: %s ---" % group)
					str_data.append("\n")
					# Get the data
					data_grp = f[group]
					#str_data.append("-- %s --" % data_grp)
					#str_data.append("\n")
					for data_key in data_grp.attrs.keys():
						data = data_grp.attrs[data_key]
						str_data.append(str(data_key) +' : '+ str(data))
						str_data.append("\n")
				str_data.append("====================")
				
			self.gui_elms["calibrate"]["calibration_files_viewer"].value = ''.join(str_data)
			
		@self.gui_elms["main"]["img_folder"].changed.connect
		def img_folder_changes():
			self.verify_existing_files()
			bool = self.read_meta()
			if bool:
				self.refresh_vals()
		
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
		
		self.cal_tab3 = QWidget()
		_cal_tab_layout3 = QVBoxLayout()
		_cal_tab_layout3.setAlignment(Qt.AlignTop)
		self.cal_tab3.setLayout(_cal_tab_layout3)
		
		_scroll_cal_req = QScrollArea()
		_scroll_cal_req.setWidgetResizable(True)
		_scroll_cal_req.setWidget(self.widget_calibrate_req.native)
		_cal_tab_layout.addWidget(_scroll_cal_req)
		
		_scroll_cal_opt = QScrollArea()
		_scroll_cal_opt.setWidgetResizable(True)
		_scroll_cal_opt.setWidget(self.widget_calibrate_opt.native)
		_cal_tab_layout2.addWidget(_scroll_cal_opt)
		
		_scroll_cal_ins = QScrollArea()
		_scroll_cal_ins.setWidgetResizable(True)
		_scroll_cal_ins.setWidget(self.widget_calibrate_ins.native)
		_cal_tab_layout3.addWidget(_scroll_cal_ins)
		
		self.qtab_cal_tabWidget = QTabWidget()
		self.qtab_cal_tabWidget.setTabPosition(QTabWidget.South)
		self.qtab_cal_tabWidget.addTab(self.cal_tab, 'Required')
		self.qtab_cal_tabWidget.addTab(self.cal_tab2, 'Optional')
		self.qtab_cal_tabWidget.addTab(self.cal_tab3, 'Inspect')
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
		
		self.projections_tab = QWidget()
		_projections_tab_layout = QVBoxLayout()
		_projections_tab_layout.setAlignment(Qt.AlignTop)
		self.projections_tab.setLayout(_projections_tab_layout)
		self.projections_tab.layout().addWidget(self.container_projections.native)
		self.qtab_widget.addTab(self.projections_tab, 'Projections')
		
		self.lfmnet_tab = QWidget()
		_lfmnet_tab_layout = QVBoxLayout()
		_lfmnet_tab_layout.setAlignment(Qt.AlignTop)
		self.lfmnet_tab.setLayout(_lfmnet_tab_layout)
		self.lfmnet_tab.layout().addWidget(self.container_lfmnet.native)
		# self.qtab_widget.addTab(self.lfmnet_tab, 'Neural Net')
		
		
		
		# self.calib_tab = QWidget()
		# _calib_tab_layout = QVBoxLayout()
		# _calib_tab_layout.setAlignment(Qt.AlignTop)
		# self.calib_tab.setLayout(_calib_tab_layout)
		# self.qtab_widget.addTab(self.calib_tab, 'Calibrate Grid')
		# self.LFD_frame = QMainWindow()
		# self.LFD_frame.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(0, 0, 255); border-width: 1px;")
		# _calib_tab_layout.addWidget(self.LFD_frame)
		
		#APP
		self.widget_main_top_comps = Container(widgets=(), labels=True)
		self.widget_main_top_comps.native.layout().addWidget(self.cont_btn_top)
		self.widget_main_top_comps.native.layout().setContentsMargins(0,0,0,0)
		self.widget_main_top_comps.native.layout().setSpacing(0)
		if LFvals.dev_true:
			self.widget_main_top_comps.native.setStyleSheet("border : 1px dashed white;")
			
		#self.gui_elms["main"]["comments"].parent.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

		vlay = QVBoxLayout()		
		box = CollapsibleBox("Presets && Comments")
		vlay.addWidget(box)
		lay = QVBoxLayout()
		lay.addWidget(_cont_preset_list_btn.native)
		lay.addWidget(self.commentsArea)

		box.setContentLayout(lay)
		# vlay.addStretch()
		_preset_comments_expand = QWidget()
		_preset_comments_expand.setLayout(vlay)
		_preset_comments_expand.layout().setContentsMargins(0,0,0,0)
		_preset_comments_expand.layout().setSpacing(0)
		_preset_comments_expand.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		
		self.widget_main_bottom_comps0 = Container(widgets=(), labels=True)
		self.widget_main_bottom_comps0.native.layout().addWidget(_preset_comments_expand, Qt.AlignTop)
		self.widget_main_bottom_comps0.native.layout().setContentsMargins(0,0,0,0)
		self.widget_main_bottom_comps0.native.layout().setSpacing(0)
		self.widget_main_bottom_comps0.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
			
		self.container_data.native.layout().addWidget(self.widget_main_bottom_comps0.native, Qt.AlignTop)
		
		self.widget_main_bottom_comps1 = Container(widgets=(), labels=True)
		self.widget_main_bottom_comps1.native.layout().addWidget(self.qtab_widget)
		
		self.widget_main_bottom_comps2 = Container(widgets=(), labels=True)
		self.widget_main_bottom_comps2.native.layout().addWidget(self.lfmnet_tab)
		self.widget_main_bottom_comps2.visible = False
		self._cont_btn_processing2.visible = False
		
		self.widget_main_bottom_comps_scroll = Container(widgets=(), labels=True)
		self.widget_main_bottom_comps_scroll.native.layout().addWidget(self.widget_main_bottom_comps1.native)
		self.widget_main_bottom_comps_scroll.native.layout().addWidget(self.widget_main_bottom_comps2.native)
		
		self.scroll_bottom = QScrollArea()
		self.scroll_bottom.setWidgetResizable(True)
		self.scroll_bottom.setWidget(self.widget_main_bottom_comps_scroll.native)
		self.container_data.native.layout().addWidget(self.scroll_bottom, Qt.AlignTop)
		
		_QFormLayout_proc_btns = QFormLayout()
		_processing_btns = QWidget()
		_processing_btns.setLayout(_QFormLayout_proc_btns)
		_QFormLayout_proc_btns.setContentsMargins(0,0,0,0)
		_QFormLayout_proc_btns.setSpacing(0)
		_QFormLayout_proc_btns.addRow(self._cont_btn_processing2.native)
		_QFormLayout_proc_btns.addRow(self._cont_btn_processing.native)
		_QFormLayout_proc_btns.setAlignment(Qt.AlignBottom)
		_processing_btns.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		
		self.container_data.native.layout().addWidget(_processing_btns, Qt.AlignBottom)
		# self.scroll_bottom.setMinimumHeight(400)
		
		if LFvals.dev_true:
			self.widget_main_bottom_comps0.native.setStyleSheet("border: 1px dashed white;")
			self.widget_main_bottom_comps1.native.setStyleSheet("border: 1px dashed white;")
			self.widget_main_bottom_comps2.native.setStyleSheet("border: 1px dashed white;")
			self.widget_main_bottom_comps_scroll.native.setStyleSheet("border: 1px dashed white;")
			self.scroll_bottom.setStyleSheet("border: 1px dashed white;")
		
		self.widget_main_proc_btn_comps = Container(widgets=(), labels=True)
		self.widget_main_proc_btn_comps.native.layout().addWidget(self.cont_btn_status)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.verify_existing_files)
		self.timer.start(500)
		
	def LFAnalyze_btn_call(self):
		# print("LFAnalyze_btn_call")
		if self.LFAnalyze_btn.isChecked() == True:
			self.widget_main_bottom_comps0.visible = True
			self.widget_main_bottom_comps1.visible = True
			self.widget_main_bottom_comps2.visible = False
			self._cont_btn_processing.visible = True
			self._cont_btn_processing2.visible = False
			self.LFAnalyze_btn_cont.visible = True
			self.NeuralNet_btn_cont.visible = False
			self.settings["main"]["mode_choice"] = 'LFAnalyze'
		else:
			self.widget_main_bottom_comps0.visible = False
			self.widget_main_bottom_comps1.visible = False
			self.widget_main_bottom_comps2.visible = True
			self._cont_btn_processing.visible = False
			self._cont_btn_processing2.visible = True
			self.LFAnalyze_btn_cont.visible = False
			self.NeuralNet_btn_cont.visible = True
			self.settings["main"]["mode_choice"] = 'NeuralNet'
		self.NeuralNet_btn.toggle()
		self.save_plugin_prefs()
			
	def NeuralNet_btn_call(self):
		# print("NeuralNet_btn_call")
		if self.NeuralNet_btn.isChecked() == True:
			self.widget_main_bottom_comps0.visible = False
			self.widget_main_bottom_comps1.visible = False
			self.widget_main_bottom_comps2.visible = True
			self._cont_btn_processing.visible = False
			self._cont_btn_processing2.visible = True
			self.LFAnalyze_btn_cont.visible = False
			self.NeuralNet_btn_cont.visible = True
			self.settings["main"]["mode_choice"] = 'NeuralNet'
		else:
			self.widget_main_bottom_comps0.visible = True
			self.widget_main_bottom_comps1.visible = True
			self.widget_main_bottom_comps2.visible = False
			self._cont_btn_processing.visible = True
			self._cont_btn_processing2.visible = False
			self.LFAnalyze_btn_cont.visible = True
			self.NeuralNet_btn_cont.visible = False
			self.settings["main"]["mode_choice"] = 'LFAnalyze'
		self.LFAnalyze_btn.toggle()
		self.save_plugin_prefs()
		
	def verify_existing_files(self):
		
		try:
			# print('verify_existing_files thread running')
		
			_img_folder = str(self.gui_elms["main"]["img_folder"].value)
			path = Path(_img_folder)
			if path.is_dir():
			
				out_files = [
					{"section":"calibrate","out_file":"output_filename", "sub_section":"required", "group":LFvals.PLUGIN_ARGS['calibrate']['output_filename']['group']},
					{"section":"rectify","out_file":"output_filename", "sub_section":"required", "group":LFvals.PLUGIN_ARGS['rectify']['output_filename']['group']},
					{"section":"deconvolve","out_file":"output_filename", "sub_section":"required", "group":LFvals.PLUGIN_ARGS['deconvolve']['output_filename']['group']},
					{"section":"projections","out_file":"output_filename_lightfield", "group":LFvals.PLUGIN_ARGS['projections']['output_filename_lightfield']['group']},
					{"section":"projections","out_file":"output_filename_volume", "group":LFvals.PLUGIN_ARGS['projections']['output_filename_volume']['group']},
					{"section":"lfmnet","out_file":"output_filename", "group":LFvals.PLUGIN_ARGS['lfmnet']['output_filename']['group']}
				]
				
				_alert_symbol = ' ⚠'
				_space_char = '  '
				
				for out in out_files:
					_img_out = self.gui_elms[out["section"]][out["out_file"]].value
					
					_file_path = os.path.join(_img_folder, _img_out)		
					path = Path(_file_path)
					if path.is_file():
						self.gui_elms[out["section"]][out["out_file"]].native.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(255, 255, 0); border-width: 1px;")
						if self.lf_vals["misc"]["group_params"]["value"] == True:
							if "sub_section" in out:
								i, j = self.groupbox[out["section"]][out["sub_section"]][out["group"]].layout().getWidgetPosition(self.gui_elms[out["section"]][out["out_file"]].native)
								widget_item = self.groupbox[out["section"]][out["sub_section"]][out["group"]].layout().itemAt(i, j-1)
							else:
								i, j = self.groupbox[out["section"]][out["group"]].layout().getWidgetPosition(self.gui_elms[out["section"]][out["out_file"]].native)
								widget_item = self.groupbox[out["section"]][out["group"]].layout().itemAt(i, j-1)
							widget = widget_item.widget()
							widget.setText(self.gui_elms[out["section"]][out["out_file"]].label + _alert_symbol)
							widget.setToolTip("A filed named '{out_file}' already exists in this folder!\nYou can continue but it will overwrite the existing file.".format(out_file = self.gui_elms[out["section"]][out["out_file"]].value))			
					else:
						self.gui_elms[out["section"]][out["out_file"]].native.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(0, 0, 0); border-width: 1px;")
						if self.lf_vals["misc"]["group_params"]["value"] == True:
							if "sub_section" in out:
								i, j = self.groupbox[out["section"]][out["sub_section"]][out["group"]].layout().getWidgetPosition(self.gui_elms[out["section"]][out["out_file"]].native)
								widget_item = self.groupbox[out["section"]][out["sub_section"]][out["group"]].layout().itemAt(i, j-1)
							else:
								i, j = self.groupbox[out["section"]][out["group"]].layout().getWidgetPosition(self.gui_elms[out["section"]][out["out_file"]].native)
								widget_item = self.groupbox[out["section"]][out["group"]].layout().itemAt(i, j-1)
							widget = widget_item.widget()
							widget.setText(self.gui_elms[out["section"]][out["out_file"]].label + _space_char)
							widget.setToolTip("")
							
				self.image_folder_changes()
			
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			
	def verify_preset_vals(self):
		preset_sel = self.gui_elms["main"]["presets"].value
		if preset_sel is not None and preset_sel != "":
			if "preset_choices" in self.settings:
				if preset_sel in self.settings["preset_choices"]:
					loaded_preset_vals = self.settings["preset_choices"][preset_sel]
					for section in loaded_preset_vals:
						for prop in loaded_preset_vals[section]:
							try:
								if LFvals.PLUGIN_ARGS[section][prop]["type"] == "file" and (os.path.normpath(self.gui_elms[section][prop].value) in [os.path.normpath(loaded_preset_vals[section][prop])]):
									pass
								elif self.gui_elms[section][prop].value == loaded_preset_vals[section][prop]:
									pass
								else:
									#print(self.gui_elms[section][prop].value, loaded_preset_vals[section][prop])
									# self.gui_elms["main"]["presets"].native.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(255, 255, 0); border-width: 1px;")
									if "" not in self.gui_elms["main"]["presets"].choices:
										choices = self.gui_elms["main"]["presets"].choices = self.gui_elms["main"]["presets"].choices + ("",)
									self.gui_elms["main"]["presets"].value = ""
									break
							except Exception as e:
								print(e)
								print(traceback.format_exc())
		elif preset_sel == "":
			for preset_selx in self.settings["preset_choices"]:
				if preset_selx != "":
					loaded_preset_vals = self.settings["preset_choices"][preset_selx]
					for section in loaded_preset_vals:
						do_break = True
						do_exit = False
						for prop in loaded_preset_vals[section]:
							try:
								if LFvals.PLUGIN_ARGS[section][prop]["type"] == "file" and (os.path.normpath(self.gui_elms[section][prop].value) in [os.path.normpath(loaded_preset_vals[section][prop])]):
									pass
								elif self.gui_elms[section][prop].value == loaded_preset_vals[section][prop]:
									pass
								else:
									do_break = False
									do_exit = True
									break
							except Exception as e:
								print(e)
								print(traceback.format_exc())
						if do_exit:
							break
						if do_break:
							if "" in self.gui_elms["main"]["presets"].choices:
								tup_list = list(self.gui_elms["main"]["presets"].choices)
								tup_list.remove("")
								self.gui_elms["main"]["presets"].choices = tuple(tup_list)
								self.gui_elms["main"]["presets"].value = preset_selx
								# self.gui_elms["main"]["presets"].native.setStyleSheet("margin:1px; padding:1px; border:1px solid rgb(0, 0, 0); border-width: 1px;")
							break
		
	def refresh_preset_choices(self):
		preset_choices = []
		if "preset_choices" in self.settings:
			for preset in self.settings["preset_choices"]:
				preset_choices.append(preset)
		
		if len(preset_choices) > 0:
			preset_choices.sort()
		self.gui_elms["main"]["presets"].choices = preset_choices
		
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
		self.cont_btn_status_label.value = txt
		self.cont_btn_status_label.native.update()
		
	def set_btns_and_status(self, btn_enab_bool, status_txt):
		self.cont_btn_status_label.value = ':STATUS: ' + status_txt
		self.btn_cal.enabled = btn_enab_bool
		self.btn_rec.enabled = btn_enab_bool
		self.btn_dec.enabled = btn_enab_bool
		
		if status_txt == LFvals.PLUGIN_ARGS['main']['status']['value_error']:
			self.cont_btn_status_label.native.setStyleSheet("color: rgb(255, 0, 0)")
		elif status_txt == LFvals.PLUGIN_ARGS['main']['status']['value_busy']:
			self.cont_btn_status_label.native.setStyleSheet("color: rgb(255, 255, 0)")
		else:
			self.cont_btn_status_label.native.setStyleSheet("color: rgb(0, 128, 0)")
		self.cont_btn_status_label.native.update()

	# ToDo - implement as directory change listener event
	def image_folder_changes(self):
		img_folder = str(self.gui_elms["main"]["img_folder"].value)
		lfc_file = str(self.gui_elms["calibrate"]["output_filename"].value)
		lfc_file_path = os.path.join(img_folder, lfc_file)
		
		path = Path(lfc_file_path)
		if path.is_file():
			self.btn_cal_prog.native.setText('✔️')
			self.btn_cal_prog.native.setStyleSheet("font-size: 16px; color: green; vertical-align: baseline;")
		else:
			self.btn_cal_prog.native.setText('')
			
		rec_file = str(self.gui_elms["rectify"]["output_filename"].value)
		rec_file_path = os.path.join(img_folder, rec_file)
		path = Path(rec_file_path)
		if path.is_file():
			self.btn_rec_prog.native.setText('✔️')
			self.btn_rec_prog.native.setStyleSheet("font-size: 16px; color: green; vertical-align: baseline;")
		else:
			self.btn_rec_prog.native.setText('')
			
		dec_file = str(self.gui_elms["deconvolve"]["output_filename"].value)
		dec_file_path = os.path.join(img_folder, dec_file)
		path = Path(dec_file_path)
		if path.is_file():
			self.btn_dec_prog.native.setText('✔️')
			self.btn_dec_prog.native.setStyleSheet("font-size: 16px; color: green; vertical-align: baseline;")
		else:
			self.btn_dec_prog.native.setText('')
			
		dec_nn_file = str(self.gui_elms["lfmnet"]["output_filename"].value)
		dec_nn_file_path = os.path.join(img_folder, dec_nn_file)
		path = Path(dec_nn_file_path)
		if path.is_file():
			self.btn_nn_proc_prog.native.setText('✔️')
			self.btn_nn_proc_prog.native.setStyleSheet("font-size: 16px; color: green; vertical-align: baseline;")
		else:
			self.btn_nn_proc_prog.native.setText('')
		
		self.populate_img_list()
		self.populate_cal_img_list()
		self.populate_projections_file_list()
		self.populate_lfmnet_model_list()
		
	def populate_projections_file_list(self):
		img_folder = str(self.gui_elms["main"]["img_folder"].value)
		proj_files = []
		for ext in LFvals.PROJ_EXTS:
			files_search = "*.{file_ext}".format(file_ext=ext)
			files = glob.glob(os.path.join(img_folder, files_search))
			for file in files:
				proj_files.append(ntpath.basename(file))
				
		# if len(proj_files) == 0:
			# self.gui_elms["projections"]["input_file_volume"].value = ""
			# self.gui_elms["projections"]["input_file_lightfield"].value = ""
		
		self.gui_elms["projections"]["input_file_volume"].choices = proj_files
		self.gui_elms["projections"]["input_file_lightfield"].choices = proj_files

	def populate_lfmnet_model_list(self):
		img_folder = str(self.gui_elms["main"]["img_folder"].value)
		model_files = []
		for ext in LFvals.MODEL_EXTS:
			files_search = "*.{file_ext}".format(file_ext=ext)
			files = glob.glob(os.path.join(img_folder, files_search))
			for file in files:
				model_files.append(ntpath.basename(file))
				
		# if len(model_files) == 0:
			# self.gui_elms["lfmnet"]["input_model"].value = ""
		
		self.gui_elms["lfmnet"]["input_model"].choices = model_files
		if len(model_files) == 0:
			self.gui_elms["lfmnet"]["input_model_prop_viewer"].value = ""
			self.btn_nn_proc.enabled = False
		else:
			self.btn_nn_proc.enabled = True
		
	def populate_img_list(self):
		img_folder = str(self.gui_elms["main"]["img_folder"].value)
		img_files = []
		for ext in LFvals.IMAGE_EXTS:
			files_search = "*.{file_ext}".format(file_ext=ext)
			files = glob.glob(os.path.join(img_folder, files_search))
			for file in files:
				img_files.append(ntpath.basename(file))
				
		self.gui_elms["main"]["img_list"].choices = img_files
		self.gui_elms["calibrate"]["radiometry_frame_file"].choices = img_files
		self.gui_elms["calibrate"]["dark_frame_file"].choices = img_files
		self.gui_elms["rectify"]["input_file"].choices = img_files
		self.gui_elms["deconvolve"]["input_file"].choices = img_files
		self.gui_elms["lfmnet"]["input_file"].choices = img_files
		
	def populate_cal_img_list(self):
		img_folder = str(self.gui_elms["main"]["img_folder"].value)
		img_files = []
		for ext in LFvals.HDF5_EXTS:
			files_search = "*.{file_ext}".format(file_ext=ext)
			files = glob.glob(os.path.join(img_folder, files_search))
			for file in files:
				img_files.append(ntpath.basename(file))
				
		if len(img_files) == 0:
			self.gui_elms["calibrate"]["calibration_files_viewer"].value = ""
			self.btn_rec.enabled = False
			self.btn_dec.enabled = False
			# self.btn_nn_proc.enabled = False
		else:
			self.btn_rec.enabled = True
			self.btn_dec.enabled = True
			# self.btn_nn_proc.enabled = True
		
		self.gui_elms["calibrate"]["calibration_files"].choices = img_files
		self.gui_elms["rectify"]["calibration_file"].choices = img_files
		self.gui_elms["deconvolve"]["calibration_file"].choices = img_files
		self.gui_elms["projections"]["calibration_file"].choices = img_files
		# self.gui_elms["lfmnet"]["calibration_file"].choices = img_files
		
	def set_cal_img(self):
		cal_file = self.gui_elms["calibrate"]["output_filename"].value
		self.gui_elms["rectify"]["calibration_file"].value = cal_file
		self.gui_elms["deconvolve"]["calibration_file"].value = cal_file
		self.gui_elms["projections"]["calibration_file"].value = cal_file
		
	def openImage(self, path):
		imageViewerFromCommandLine = {'linux':'xdg-open','win32':'explorer','darwin':'open'}[sys.platform]
		subprocess.Popen([imageViewerFromCommandLine, path])
		
	def openImageExtViewer(self, path):
		imageViewerFromCommandLine = "{viewer} {cmd} {file_path}".format(viewer=self.gui_elms["misc"]["ext_viewer"].value, cmd="-file-name", file_path=path)
		subprocess.Popen(imageViewerFromCommandLine)
			
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
		
	def save_plugin_prefs(self):
		for section in LFvals.PLUGIN_ARGS:
			if section not in self.settings:
				self.settings[section] = {}
			for prop in LFvals.PLUGIN_ARGS[section]:
				if "exclude_from_settings" in LFvals.PLUGIN_ARGS[section][prop] and LFvals.PLUGIN_ARGS[section][prop]["exclude_from_settings"] == True:
					pass
				else:
					if LFvals.PLUGIN_ARGS[section][prop]["type"] in ["file","folder","str"]:
						self.settings[section][prop] = str(self.gui_elms[section][prop].value)
					else:
						self.settings[section][prop] = self.gui_elms[section][prop].value
		
		settings_file_path = Path(os.path.join(self.currentdir, LFvals.SETTINGS_FILENAME))
		with open(settings_file_path, "w") as f:
			json.dump(self.settings, f, indent=4)

	def load_plugin_prefs(self, pre_init=False):
		try:
			settings_file_path = Path(os.path.join(self.currentdir, LFvals.SETTINGS_FILENAME))
			if settings_file_path.is_file() is False:
				self.save_plugin_prefs()
			else:
				with open(settings_file_path, "r") as f:
					self.settings = json.load(f)
					
				for section in LFvals.PLUGIN_ARGS:
					for prop in LFvals.PLUGIN_ARGS[section]:
						try:
							if prop in LFvals.PLUGIN_ARGS[section] and (section in self.settings and prop in self.settings[section]):
								LFvals.PLUGIN_ARGS[section][prop]["value"] = self.settings[section][prop]
							if pre_init == False and prop in self.gui_elms[section] and prop in self.settings[section] and (section in self.settings and prop in self.settings[section]):
								try:
									if self.gui_elms[section][prop].widget_type == 'ComboBox':
										if self.settings[section][prop] in self.gui_elms[section][prop].choices:
											self.gui_elms[section][prop].value = self.settings[section][prop]
										elif len(self.gui_elms[section][prop].choices) == 0:
											#self.gui_elms[section][prop].value = ""
											pass
										else:
											self.gui_elms[section][prop].value = self.gui_elms[section][prop].choices[0]
									else:
										self.gui_elms[section][prop].value = self.settings[section][prop]
								except Exception as e:
									print(e)
									print(traceback.format_exc())
						except Exception as e:
							print(e)
							print(traceback.format_exc())
				if pre_init == False:
					bool = self.read_meta()
					if bool:
						self.refresh_vals()
					self.image_folder_changes()
					self.refresh_preset_choices()
			
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			self.settings = {}
			
	def write_meta(self):
		try:
			meta_data = {}
			section = "main"
			meta_data[section] = {}
			prop = "comments"
			meta_data[section][prop] = str(self.gui_elms[section][prop].value)
			
			for section in ['calibrate','rectify','deconvolve','hw']:
				meta_data[section] = {}
				for prop in LFvals.PLUGIN_ARGS[section]:
					if ("exclude_from_settings" in LFvals.PLUGIN_ARGS[section][prop] and LFvals.PLUGIN_ARGS[section][prop]["exclude_from_settings"] == True) or ("exclude_from_settings" in LFvals.PLUGIN_ARGS[section][prop] and LFvals.PLUGIN_ARGS[section][prop]["exclude_from_settings"] == True):
						pass
					else:
						if LFvals.PLUGIN_ARGS[section][prop]["type"] in ["file","folder","str"]:
							meta_data[section][prop] = str(self.gui_elms[section][prop].value)
						else:
							meta_data[section][prop] = self.gui_elms[section][prop].value
			
			metadata_file_path = Path(self.gui_elms["main"]["img_folder"].value, self.gui_elms["main"]["metadata_file"].value)
			with open(metadata_file_path, "w") as f:
				json.dump(meta_data, f, indent=4)
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			
	def read_meta(self):
		try:
			path = Path(os.path.join(self.gui_elms["main"]["img_folder"].value, self.gui_elms["main"]["metadata_file"].value))
			if path.is_file():
				with open(os.path.join(self.gui_elms["main"]["img_folder"].value, self.gui_elms["main"]["metadata_file"].value)) as json_file:
					meta_data = json.load(json_file)
					
				for section in meta_data:
					for prop in meta_data[section]:
						if prop in self.gui_elms[section] and prop in meta_data[section]:
							try:
								if self.gui_elms[section][prop].widget_type == "ComboBox":
									if meta_data[section][prop] in self.gui_elms[section][prop].choices:
										self.gui_elms[section][prop].value = meta_data[section][prop]
									elif len(self.gui_elms[section][prop].choices) == 0:
										#self.gui_elms[section][prop].value = ""
										pass
									else:
										self.gui_elms[section][prop].value = self.gui_elms[section][prop].choices[0]
								else:
									self.gui_elms[section][prop].value = meta_data[section][prop]
							except Exception as e:
								print(self.gui_elms[section][prop].widget_type)
								print(e)
								print(traceback.format_exc())
					
				return True
			else:
				return False
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			return False
			
	def get_preset_name(self):
		text, ok = QInputDialog.getText(QWidget(), 'Input Dialog', 'Enter preset name:')
		
		if ok:
			if "preset_choices" in self.settings:
				for preset in self.settings["preset_choices"]:
					if preset == text:
						qm = QMessageBox
						ret = qm.question(QWidget(),'', "Preset name already exists, overwirte ?", qm.Yes | qm.No)
						if ret == qm.Yes:
							return (str(text))
						else:
							return None
			return (str(text))
		return None
		
	def dump_errors(self, currentdir, err, traceback=False):
		t_stamp = time.strftime("%Y-%m-%d %H:%M:%S")
		contents = t_stamp + '\t' + str(err)
		err_file_name = time.strftime("%Y_%m_%d") + '.log'
		
		errorLogsDir = os.path.join(currentdir, 'errorLogs')
		if Path(errorLogsDir).is_dir() == False:
			os.mkdir(errorLogsDir)
		
		err_file_path = Path(os.path.join(errorLogsDir, err_file_name))
		if Path(err_file_path).is_file():
			with open(err_file_path, "r") as f:
				contents = f.read()
				if traceback:
					contents = t_stamp + '\t' + str(err) + contents
				else:
					contents = t_stamp + '\t' + str(err) + '\n' + contents
			
		with open(err_file_path, "w") as f:
			f.write(str(contents))

def create_widget(props):
	widget = None
	try:
		if "widget_type" in props:
			widget = create_widget(widget_type=props['widget_type'], tooltip=props['help'])
		elif props["type"] == "str":
			widget = LineEdit(label=props['label'], tooltip=props['help'])
		elif props["type"] == "text":
			widget = TextEdit(label=props['label'], tooltip=props['help'])
		elif props["type"] == "label":
			widget = Label(label=props['label'], tooltip=props['help'])
		elif props["type"] == "img_label":
			widget = Label(label=props['label'], tooltip=props['help'])
		elif props["type"] == "float":
			widget = FloatSpinBox(label=props['label'], tooltip=props['help'], step=0.01)
		elif props["type"] == "int":
			widget = SpinBox(label=props['label'], tooltip=props['help'], step=1)
		elif props["type"] == "sel":
			widget = ComboBox(label=props['label'], tooltip=props['help'], value=props["options"][0], choices=(props["options"]))
		elif props["type"] == "file":
			widget = FileEdit(label=props['label'], mode='r', tooltip=props['help'], nullable=True)
		elif props["type"] == "folder":
			widget = FileEdit(label=props['label'], mode='d', tooltip=props['help'], nullable=True)
		elif props["type"] == "bool":	
			widget = CheckBox(label=props['label'], tooltip=props['help'])
		elif props["type"] == "PushButton":	
			widget = PushButton(label=props['label'], tooltip=props['help'])
		else:
			pass
			
		if widget != None:
			# if "max" in props:
				# widget.max = props["max"]
			# if "step" in props:
				# widget.step = props["step"]
			
			if widget.widget_type == "LineEdit":
				widget.min_width = 100
				widget.native.setStyleSheet("background-color:black;")
				
			if widget.widget_type == "SpinBox":
				if "max" in props:
					widget.max = props["max"]
				if "min" in props:
					widget.min = props["min"]
				
			for prop in props:
				try:
					getattr(widget, prop)
					setattr(widget, prop, props[prop])
				except:
					pass
			
			if "default" in props:
				widget.value = props["default"]
			
	except Exception as e:
		print(props)
		print(e)
		print(traceback.format_exc())
	return widget
	
class CollapsibleBox(QWidget):
	def __init__(self, title="", parent=None):
		super(CollapsibleBox, self).__init__(parent)

		self.toggle_button = QToolButton(
			text=title, checkable=True, checked=False
		)
		self.toggle_button.setStyleSheet("QToolButton { border: none; }")
		self.toggle_button.setToolButtonStyle(
			QtCore.Qt.ToolButtonTextBesideIcon
		)
		self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
		self.toggle_button.pressed.connect(self.on_pressed)

		self.toggle_animation = QtCore.QParallelAnimationGroup(self)

		self.content_area = QScrollArea(maximumHeight=0, minimumHeight=0)
		self.content_area.setSizePolicy(
			QSizePolicy.Expanding, QSizePolicy.Fixed
		)
		self.content_area.setFrameShape(QFrame.NoFrame)

		lay = QVBoxLayout(self)
		lay.setSpacing(0)
		lay.setContentsMargins(0, 0, 0, 0)
		lay.addWidget(self.toggle_button)
		lay.addWidget(self.content_area)

		self.toggle_animation.addAnimation(
			QtCore.QPropertyAnimation(self, b"minimumHeight")
		)
		self.toggle_animation.addAnimation(
			QtCore.QPropertyAnimation(self, b"maximumHeight")
		)
		self.toggle_animation.addAnimation(
			QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
		)

	# @QtCore.pyqtSlot()
	def on_pressed(self):
		checked = self.toggle_button.isChecked()
		self.toggle_button.setArrowType(
			QtCore.Qt.DownArrow if not checked else QtCore.Qt.RightArrow
		)
		self.toggle_animation.setDirection(
			QtCore.QAbstractAnimation.Forward
			if not checked
			else QtCore.QAbstractAnimation.Backward
		)
		self.toggle_animation.start()

	def setContentLayout(self, layout):
		lay = self.content_area.layout()
		del lay
		self.content_area.setLayout(layout)
		collapsed_height = (
			self.sizeHint().height() - self.content_area.maximumHeight()
		)
		content_height = layout.sizeHint().height()
		for i in range(self.toggle_animation.animationCount()):
			animation = self.toggle_animation.animationAt(i)
			animation.setDuration(500)
			animation.setStartValue(collapsed_height)
			animation.setEndValue(collapsed_height + content_height)

		content_animation = self.toggle_animation.animationAt(
			self.toggle_animation.animationCount() - 1
		)
		content_animation.setDuration(500)
		content_animation.setStartValue(0)
		content_animation.setEndValue(content_height)
		
class PicButton(QAbstractButton):
	def __init__(self, pixmap, pixmap_hover, pixmap_pressed, parent=None):
		super(PicButton, self).__init__(parent)
		self.pixmap = pixmap
		self.pixmap_hover = pixmap_hover
		self.pixmap_pressed = pixmap_pressed
		self.setCheckable(True)
		self.setVisible(True)

	def paintEvent(self, event):
		pix = self.pixmap_hover if self.underMouse() else self.pixmap
		if self.isChecked():
			pix = self.pixmap_pressed
		painter = QPainter(self)
		painter.drawPixmap(event.rect(), pix)

	def enterEvent(self, event):
		self.update()

	def leaveEvent(self, event):
		self.update()

	def sizeHint(self):
		return self.pixmap.size()

# https://stackoverflow.com/questions/46007131/make-every-tab-the-same-width-and-also-expandable
class TabBar(QTabBar):
	def tabSizeHint(self, index):
		size = QTabBar.tabSizeHint(self, index)
		return QSize(size.width(), 100)