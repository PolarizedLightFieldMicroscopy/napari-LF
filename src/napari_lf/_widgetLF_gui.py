import os
from qtpy.QtCore import Qt, QSize
from qtpy.QtGui import QMovie
from qtpy.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QMessageBox, QTabWidget
from magicgui.widgets import Container, FileEdit, Label, LineEdit, FloatSpinBox, PushButton, CheckBox, SpinBox, Slider, ComboBox
try:
	from napari_lf import _widgetLF_vals as LFvals
except:
	import _widgetLF_vals as LFvals

try:	
	import pyopencl as cl
except Exception as e:
	print(e)

class LFQWidgetGui():
		
	def __init__(self):
		super().__init__()
		
		self.currentdir = os.path.dirname(os.path.realpath(__file__))
		self.lf_vals = LFvals.PLUGIN_ARGS
		
		# == MAIN ==
		self.logo_label = Label(label=LFvals.PLUGIN_ARGS['general']['logo_label']['label'], tooltip=LFvals.PLUGIN_ARGS['general']['logo_label']['help'])
		self.info_label = Label(label=f'<h2><center>LF Analyze</a></center></h2>')
		self.img_folder = FileEdit(value=LFvals.PLUGIN_ARGS['general']['img_folder']['default'], label=LFvals.PLUGIN_ARGS['general']['img_folder']['label'], tooltip=LFvals.PLUGIN_ARGS['general']['img_folder']['help'], mode='d')
		self.meta_txt = LineEdit(value=LFvals.PLUGIN_ARGS['general']['metadata_file']['default'], label=LFvals.PLUGIN_ARGS['general']['metadata_file']['label'], tooltip=LFvals.PLUGIN_ARGS['general']['metadata_file']['help'])
		self.btn_cal = PushButton(name='Calibrate', label='Calibrate')
		self.btn_rec = PushButton(name='Rectify', label='Rectify')
		self.btn_dec = PushButton(name='Deconvolve', label='Deconvolve')
		self.status = Label(value=LFvals.PLUGIN_ARGS['general']['status']['value'], label=LFvals.PLUGIN_ARGS['general']['status']['label'])
		sp = self.status.native.sizePolicy()
		sp.setRetainSizeWhenHidden(True)
		self.status.native.setSizePolicy(sp)
		self.status.native.setAlignment(Qt.AlignCenter)
		
		self.gui_elms = {}
		
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
					_widget_calibrate_req.append(wid_elm)
				else:
					_widget_calibrate_opt.append(wid_elm)
		
		self.widget_calibrate_req = Container(name='Calibrate Req', widgets=_widget_calibrate_req)
		self.widget_calibrate_opt = Container(name='Calibrate Opt', widgets=_widget_calibrate_opt)
		
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
					_widget_rectify_req.append(wid_elm)
				else:
					_widget_rectify_opt.append(wid_elm)
		
		self.widget_rectify_req = Container(name='Rectify Req', widgets=_widget_rectify_req)
		self.widget_rectify_opt = Container(name='Rectify Opt', widgets=_widget_rectify_opt)
		
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
					_widget_deconvolve_req.append(wid_elm)
				else:
					_widget_deconvolve_opt.append(wid_elm)
		
		self.widget_deconvolve_req = Container(name='Deconvolve Req', widgets=_widget_deconvolve_req)
		self.widget_deconvolve_opt = Container(name='Deconvolve Opt', widgets=_widget_deconvolve_opt)
		
		# == HARDWARE ==
		self.gpu_choices = self.get_GPU()
		self.gpu_combobox = ComboBox(name='Select Device', label='Select Device', tooltip=LFvals.PLUGIN_ARGS['hw']['gpu_id']['help'], choices=(self.gpu_choices))
		self.platforms_choices = self.get_PlatForms(self.gpu_combobox.native.currentIndex())
		self.platform_combobox = ComboBox(name='Select Platform', label='Select Platform', tooltip=LFvals.PLUGIN_ARGS['hw']['platform_id']['help'], choices=(self.platforms_choices))
		# self.cpu_threads_combobox = ComboBox(label=LFvals.PLUGIN_ARGS['calibrate']['num_threads']['label'], tooltip=LFvals.PLUGIN_ARGS['calibrate']['num_threads']['help'], choices=(list(range(1,129))))
		self.use_disable_gpu = CheckBox(label=LFvals.PLUGIN_ARGS['hw']['disable_gpu']['label'], value=LFvals.PLUGIN_ARGS['hw']['disable_gpu']['default'])
		self.use_single_prec = CheckBox(label=LFvals.PLUGIN_ARGS['hw']['use_single_prec']['label'], value=LFvals.PLUGIN_ARGS['hw']['use_single_prec']['default'])
		self.container_hw = Container(widgets=[self.gpu_combobox, self.platform_combobox, self.use_disable_gpu, self.use_single_prec])
		
		@self.gpu_combobox.changed.connect
		def gpu_sel_call():
			self.platforms_choices = self.get_PlatForms(self.gpu_combobox.native.currentIndex())
			self.platform_combobox.choices = self.platforms_choices
			
		# == LFANALYZE LIB ==
		self.folder_lfa_label = Label(label=LFvals.PLUGIN_ARGS['general']['lib_ver_label']['label'], value=LFvals.PLUGIN_ARGS['general']['lib_ver_label']['default'], tooltip=LFvals.PLUGIN_ARGS['general']['lib_ver_label']['help'])
		self.folder_lfa = FileEdit(value=self.currentdir, label=LFvals.PLUGIN_ARGS['general']['lib_folder']['label'], mode='d', tooltip=LFvals.PLUGIN_ARGS['general']['lib_folder']['help'])
		self.container_lfa = Container(widgets=[self.folder_lfa, self.folder_lfa_label])
		
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
		self.lfa_lib_tab.layout().addWidget(self.container_lfa.native)
		self.qtab_widget.addTab(self.lfa_lib_tab, 'LFAnalyze Library')
		
		self.qtab_widget.setMaximumWidth(360)
		# self.qtab_widget.setMaximumHeight(375)
		
		#APP
		self.widget_logo_info = Container(name='', annotation=None, label='', tooltip=None, visible=None, enabled=True, gui_only=False, backend_kwargs={}, layout='vertical', widgets=(Label(),self.logo_label), labels=True)
		self.widget_main_comps = Container(name='', annotation=None, label='', tooltip=None, visible=None, enabled=True, gui_only=False, backend_kwargs={}, layout='vertical', widgets=(self.img_folder, self.meta_txt, self.btn_cal, self.btn_rec, self.btn_dec, self.status), labels=True)
		self.widget_main = Container(name='LFAnalyze', annotation=None, label='LFAnalyze', tooltip=None, visible=None, enabled=True, gui_only=False, backend_kwargs={}, layout='vertical', widgets=(), labels=True)
		self.widget_main.native.layout().addWidget(self.qtab_widget)
		
	def refresh_vals(self):
		for section in ["calibrate","rectify","deconvolve"]:
			for key in self.lf_vals[section]:
				dict = self.lf_vals[section][key]
				wid_elm = self.gui_elms[section][key]
				if dict["type"] == "file" or dict["type"] == "folder":
					dict["value"] = str(wid_elm.value)
				else:
					dict["value"] = wid_elm.value
		
	def set_status_busy(self):
		self.status.value = LFvals.PLUGIN_ARGS['general']['status']['value_busy']
		load_gif = LFvals.loading_img
		mov = QMovie(load_gif)
		mov.setScaledSize(QSize(14, 14))
		self.status.native.setMovie(mov)
		mov.start()
		
	def get_GPU(self):
		gpu_list = []
		for platform in cl.get_platforms():
			gpu_list.append(platform.name.strip('\r\n \x00\t'))
		return gpu_list
		
	def get_PlatForms(self, idx):
		platforms_list = []
		try:
			platforms = cl.get_platforms()
			for device in platforms[idx].get_devices():
				platforms_list.append(device.name.strip('\r\n \x00\t'))
			return platforms_list
		except:
			return []

def create_widget(props):
	widget = None
	try:
		if props["type"] == "str":
			widget = LineEdit(label=props['label'], tooltip=props['help'])
		elif props["type"] == "float":
			widget = FloatSpinBox(label=props['label'], tooltip=props['help'], step=0.001)
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
			if "max" in props:
				widget.max = props["max"]
			if "step" in props:
				widget.max = props["step"]
				
			widget.value = props["default"]
	except Exception as e:
		print(props)
		print(e)
	return widget