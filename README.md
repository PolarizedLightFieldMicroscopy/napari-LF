# napari-LF

[![License](https://img.shields.io/pypi/l/napari-LF.svg?color=green)](https://github.com/PolarizedLightFieldMicroscopy/napari-LF/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-LF.svg?color=green)](https://pypi.org/project/napari-LF)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-LF.svg?color=green)](https://python.org)
<!-- [![tests](https://github.com/PolarizedLightFieldMicroscopy/napari-LF/workflows/tests/badge.svg)](https://github.com/PolarizedLightFieldMicroscopy/napari-LF/actions) -->
[![codecov](https://codecov.io/gh/PolarizedLightFieldMicroscopy/napari-LF/branch/main/graph/badge.svg)](https://codecov.io/gh/PolarizedLightFieldMicroscopy/napari-LF)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-LF)](https://napari-hub.org/plugins/napari-LF)

Light field imaging plugin for napari

----------------------------------

Deconvolves a 4D light field image into a full 3D focal stack reconstruction

![Example GIF hosted on Imgur](https://i.imgur.com/A5phCX4.gif)

Through the calibration process followed by the deconvolution process, 
**Calibration** process uses the radiometry frame, dark frame, optical parameters, and volume 
parameters to rectify the image and generated a point spread function (PSF). **Deconvolution** 
process uses the PSF and wave optics to deconvolve the light field image into a focal stack.

**Calibration** process uses the calibration (radiometry, dark) images along with optical and 
volume parameters to rectify the image and generate the point spread function (PSF) of the 
optical system. **Deconvolution** process uses the PSF and wave optics to deconvolve the light 
field image into a focal stack.

**Parameter panel**, located at the bottom of the plugin window, allows the user to specify 
settings of the reconstuction process. Once the appropriate parameters are selected, the 
`Calibrate` button followed by the `Deconvolve` button can be pushed to complete the 
reconstruction. 

## Quickstart
1. Select your **Project folder** containing the following images: light field, radiometry, and dark frame.
1. Write the name of the metadata file you want for recording your reconstruction settings, e.g. metadata.txt.
1. Calibration
    - In the parameters panel, navigate to **Calibrate, Required** (top tab **Calibrate**, bottom tab **Required**), which is the default selection.
    - Select **radiometry** and **dark frame** images from pull down menus.
    - Write the name of the **calibration file** you would like to produce, e.g. calibration.lfc.
    - Enter the appropriate **optical parameters** according to your microscope and sample material.
    - Enter the **volume parameters** you would like for your 3D reconstuction.
    - Push the `Calibrate` button.
1. Deconvolution
    - In the parameters panel, navigate to **Deconvolve, Required**.
    - Select **light field** image and **calibration file** from pull down menus.
    - Write the name of the **output image stack** you would like to produce, e.g. output_stack.tif.
    - Push the `Deconvolve` button.
3D focal stack reconstruction will display in the napari viewer and be saved in your original Project folder.

## Getting Help
For details about each parameter, hover over each parameter textbox to read the tooltip description.
For additional information about the reconstruction process, see our documentation on [GitHub](https://github.com/PolarizedLightFieldMicroscopy/napari-LF).

## Installation

Create a virtual environment from the command line for napari with the python libraries necessary for the light field plugin.

    conda create --name napari-lf python==3.9 h5py pyopencl napari git -c conda-forge
    conda activate napari-lf

Then, install the light field plugin. Below are two methods of installing:

Method 1: Install the latest development version from the command line.

    pip install git+https://github.com/PolarizedLightFieldMicroscopy/napari-LF.git

Method 2: Install a downloaded version.

1. Open napari from the command line.

        napari

2. From the menu, select **Plugins > Install/uninstall Packages**.

3. Drag and drop the downloaded `napari-LF` directory into the bottom bar.

4. Select **Install** to install the light field plugin.

5. Close napari.

Lastly, to access the plugin, open napari from the command line.

    napari

From the menu, select **Plugins > napari-LF > LF-Analyze**.

------
At a future time, you can install `napari-LF` via [pip]:

    pip install napari-LF
------

## Installation for developers

Clone the github repository:

```
conda install git

git clone https://github.com/PolarizedLightFieldMicroscopy/napari-LF.git

cd napari-LF

pip install -e .
```

## Deployment to pypi

For deploying the plugin to the python package index (pypi), one needs a [pypi user account](https://pypi.org/account/register/) 
first. For deploying the plugin to pypi, one needs to install some tools:

```
python -m pip install --user --upgrade setuptools wheel
python -m pip install --user --upgrade twine
```

The following command allows us to package the source code as a python wheel. 
Make sure that the 'dist' and 'build' folders are deleted before doing this:

```
python setup.py sdist bdist_wheel
```

This command ships the just generated to pypi:

```
python -m twine upload --repository pypi dist/*
```

[Read more about distributing your python package via pypi](https://realpython.com/pypi-publish-python-package/#publishing-to-pypi).


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
