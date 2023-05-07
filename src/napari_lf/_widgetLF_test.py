from qtpy.QtWidgets import *

# Fix for the QPixMap error
# https://github.com/PolarizedLightFieldMicroscopy/napari-LF/issues/29
app = QApplication([])

try:
	from napari_lf import _widgetLF as napariLF
except:
	import _widgetLF as napariLF
	
METHODS = ['PLUGIN','NAPARI','APP']
METHOD = METHODS[0]

if __name__ == "__main__":
	napariLF.main(METHODS[1])