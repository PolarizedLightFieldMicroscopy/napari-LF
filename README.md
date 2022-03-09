# napari-LF

[![License](https://img.shields.io/pypi/l/napari-LF.svg?color=green)](https://github.com/PolarizedLightFieldMicroscopy/napari-LF/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-LF.svg?color=green)](https://pypi.org/project/napari-LF)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-LF.svg?color=green)](https://python.org)
[![tests](https://github.com/PolarizedLightFieldMicroscopy/napari-LF/workflows/tests/badge.svg)](https://github.com/PolarizedLightFieldMicroscopy/napari-LF/actions)
[![codecov](https://codecov.io/gh/PolarizedLightFieldMicroscopy/napari-LF/branch/main/graph/badge.svg)](https://codecov.io/gh/PolarizedLightFieldMicroscopy/napari-LF)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-LF)](https://napari-hub.org/plugins/napari-LF)

A plugin to use with napari in the process of developing a light field imaging plugin

----------------------------------

This [napari] plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/cookiecutter-napari-plugin#getting-started

and review the napari docs for plugin developers:
https://napari.org/plugins/stable/index.html
-->

## Installation

Create a virtual environment from the command line for napari with the python libraries necessary for the light field plugin.

    conda create --name napari-lf python==3.9
    conda activate napari-lf
    conda install h5py
    conda install -c conda-forge pyopencl
    pip install opencv-contrib-python
    pip install "napari[all]"

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
