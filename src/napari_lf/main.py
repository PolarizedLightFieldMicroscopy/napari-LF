import napari
from lfa import lfdeconvolve
import argparse
import os
# if __name__ == "__main__":
#     viewer = napari.Viewer()
#     napari.run()


def main():
    args = ["input_file C:\\Users\\OldenbourgLab2\\Code\\napari-LF-develop\\src\\napari_lf\\examples\\antleg\\light_field.png",]
    args = ['C:\\Users\\OldenbourgLab2\\Code\\napari-LF-develop\\src\\napari_lf\\examples\\antleg\\light_field.png', 
            '--calibration-file', 'C:\\Users\\OldenbourgLab2\\Code\\napari-LF-develop\\src\\napari_lf\\examples\\antleg\\calibration.lfc', 
            '--output-file', 'C:\\Users\\OldenbourgLab2\\Code\\napari-LF-develop\\src\\napari_lf\\examples\\antleg\\output_stack.tif',
            '--solver', 'vcdnet']
    
    args = ['C:\\Users\\OldenbourgLab2\\Code\\napari-LF-develop\\src\\napari_lf\\examples\\mousebrain\\input_img_0.tif', 
            '--calibration-file', 'C:\\Users\\OldenbourgLab2\\Code\\napari-LF-develop\\src\\napari_lf\\examples\\mousebrain\\calibration-sin.lfc', 
            '--output-file', 'C:\\Users\\OldenbourgLab2\\Code\\napari-LF-develop\\src\\napari_lf\\examples\\mousebrain\\output_stack_lfmnet.tif',
            '--solver', 'lfmnet']
    
    
    lfdeconvolve.main(args)


if __name__ == '__main__':
    main()
    