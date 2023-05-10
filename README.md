# napari-LF

[![License](https://img.shields.io/pypi/l/napari-LF.svg?color=green)](https://github.com/PolarizedLightFieldMicroscopy/napari-LF/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-LF.svg?color=green)](https://pypi.org/project/napari-LF)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-LF.svg?color=green)](https://python.org)
[![tests](https://github.com/PolarizedLightFieldMicroscopy/napari-LF/workflows/tests/badge.svg)](https://github.com/PolarizedLightFieldMicroscopy/napari-LF/actions)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-LF)](https://napari-hub.org/plugins/napari-LF)
[![Downloads](https://static.pepy.tech/badge/napari-lf)](https://pepy.tech/project/napari-lf)
<!-- [![codecov](https://codecov.io/gh/PolarizedLightFieldMicroscopy/napari-LF/branch/main/graph/badge.svg)](https://codecov.io/gh/PolarizedLightFieldMicroscopy/napari-LF) -->

Light field imaging plugin for napari

----------------------------------

Deconvolves a 4D light field image into a full 3D focus stack reconstruction

https://user-images.githubusercontent.com/23206511/236919283-d53ca97a-9bdd-4598-b553-34996f688237.mp4

napari-LF contains an analytic and neural net analysis methods for light field images.

### LF Analyze
**LF Analyze**, the analytic method, provides three basic processes to Calibrate, Rectify, and Deconvolve light field images:

The **Calibrate** process generates a calibration file that represents the optical setup that was used to record the light field images. The same calibration file can be used to rectify and deconvolve all light field images that were recorded with the same optical setup, usually the same microscope and light field camera. The Calibrate process requires as input the radiometry frame, dark frame, optical parameters, and volume parameters to generate the calibration file, which is subsequently used to rectify and deconvolve related light field images. The calibration file includes a point spread function (PSF) derived from the optical and volume parameters and is stored in HDF5 file format.

The **Rectify** process uses the calibration file for an affine transformation to scale and rotate experimental light field images that were recorded with a light field camera whose microlens array was (slightly) rotated with respect to the pixel array of the area detector and whose pixel pitch is not commensurate with the microlens pitch. After rectification, the rectified light field has the same integer number of pixels behind each microlens. When the Deconvolve process is called for an experimental light field image, rectifying the light field image is automatically applied before the iterative deconvolution does begin. However, the rectified light field image is not saved and is not available for viewing. Therefore, by pushing the Rectify button in the middle of the napari-LF widget, only the rectification step is invoked and the rectified light field image is saved to the project directory.

The **Deconvolve** process uses the PSF and a wave optics model to iteratively deconvolve a light field image into a stack of optical sections.

The **Parameter** panels, located in the lower half of the napari-LF widget, allows the user to specify settings for the reconstruction process. Once the appropriate parameters are selected, the Calibrate button followed by the Deconvolve button can be pushed to complete the reconstruction.

### Neural Net
**Neural Net** provides a method of applying a trained neural net model to deconvolve a light field image.

## Quickstart
1. Install the napari-LF plugin into your napari environment, as described below under **Installation**.
1. From the napari Plugins menu, select the napari-LF plugin to install its widget into the napari viewer.
### LF Analyze
1. Near the top of the widget, select your project folder containing the following images: light field, radiometry, and dark frame.
1. Calibration
    1. In the processing panel, navigate to **Calibrate, Required** (top tab **Calibrate**, bottom tab **Required**), which is the default selection.
    1. Select **radiometry** and **dark frame** images from pull down menus.
    1. Write the name of the **calibration file** you would like to produce, e.g. calibration.lfc.
    1. Enter the appropriate **optical parameters** according to your microscope and sample material.
    1. Enter the **volume parameters** you would like for your 3D reconstuction.
    1. Push the `Calibrate` button.
1. Deconvolution
    1. In the processing panel, navigate to **Deconvolve, Required**.
    1. Select **light field** image and **calibration file** from pull down menus.
    1. Write the name of the **output image stack** you would like to produce, e.g. output_stack.tif.
    1. Push the `Deconvolve` button.
The 3D focal stack reconstruction will display in the napari viewer and be saved in your original project folder.
### Neural Net
1. Click on the **LF Analyze** logo to toggle to the **Neural Net** mode.
1. Near the top of the widget, select your project folder containing the light field image and the trained neural net. If you do not already have a trained model, you can train a model using this [Jupyter notebook](https://github.com/PolarizedLightFieldMicroscopy/napari-LF/blob/main/src/napari_lf/lfa/main_train_neural_net.ipynb).
1. In the processing panel, select your **light field image** and **neural net model**.
1. Write the name of the **output image stack** you would like to produce, e.g. output_stack.tif.
1. Push the `Deconvolve` button.
The 3D focal stack reconstruction will display in the napari viewer and be saved in your original project folder.

## Getting Help
For details about each parameter, hover over each parameter textbox to read the tooltip description.
For additional information about the reconstruction process, see our [User Guide](docs/napari-LF_UserGuide_5July2022.docx).

## Installation

After you have [napari] installed, you can one of the methods below to install `napari-LF`.

Method 1: You can install `napari-LF` via [pip]:

    pip install napari-LF

Method 2: Use the napari plugin menu.

1. Open napari from the command line:

        napari

1. From the napari menu, select **Plugins > Install/uninstall Packages**.

1. Either (a) scroll through the list of available plugins to find `napari-LF`, or (b) drag and drop a downloaded `napari-LF` directory into the bottom bar.

1. Select **Install** to install the light field plugin.

Method 3: Install the latest development version from the command line.

    pip install git+https://github.com/PolarizedLightFieldMicroscopy/napari-LF.git

Lastly, to access the installed plugin, open napari from the command line:

    napari

From the napari menu, select **Plugins > Main Menu (napari-LF)**. Note that you may need to close and reopen napari for the `napari-LF` to appear.

### Installation for developers

Create a virtual environment from the command line for napari with the python libraries necessary for the light field plugin:

    conda create --name napari-lf python==3.9
    conda activate napari-lf

Clone the github repository:

    conda install git
    git clone https://github.com/PolarizedLightFieldMicroscopy/napari-LF.git
    cd napari-LF
    pip install -e .

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
"napari-LF" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/PolarizedLightFieldMicroscopy/napari-LF/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
