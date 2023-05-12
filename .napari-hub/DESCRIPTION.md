

<!-- This file is designed to provide you with a starting template for documenting
the functionality of your plugin. Its content will be rendered on your plugin's
napari hub page.

The sections below are given as a guide for the flow of information only, and
are in no way prescriptive. You should feel free to merge, remove, add and 
rename sections at will to make this document work best for your plugin. 

# Description

This should be a detailed description of the context of your plugin and its 
intended purpose.

If you have videos or screenshots of your plugin in action, you should include them
here as well, to make them front and center for new users. 

You should use absolute links to these assets, so that we can easily display them 
on the hub. The easiest way to include a video is to use a GIF, for example hosted
on imgur. You can then reference this GIF as an image.

![Example GIF hosted on Imgur](https://i.imgur.com/A5phCX4.gif)

Note that GIFs larger than 5MB won't be rendered by GitHub - we will however,
render them on the napari hub.

The other alternative, if you prefer to keep a video, is to use GitHub's video
embedding feature.

1. Push your `DESCRIPTION.md` to GitHub on your repository (this can also be done
as part of a Pull Request)
2. Edit `.napari/DESCRIPTION.md` **on GitHub**.
3. Drag and drop your video into its desired location. It will be uploaded and
hosted on GitHub for you, but will not be placed in your repository.
4. We will take the resolved link to the video and render it on the hub.

Here is an example of an mp4 video embedded this way.

https://user-images.githubusercontent.com/17995243/120088305-6c093380-c132-11eb-822d-620e81eb5f0e.mp4

# Intended Audience & Supported Data

This section should describe the target audience for this plugin (any knowledge,
skills and experience required), as well as a description of the types of data
supported by this plugin.

Try to make the data description as explicit as possible, so that users know the
format your plugin expects. This applies both to reader plugins reading file formats
and to function/dock widget plugins accepting layers and/or layer data.
For example, if you know your plugin only works with 3D integer data in "tyx" order,
make sure to mention this.

If you know of researchers, groups or labs using your plugin, or if it has been cited
anywhere, feel free to also include this information here.

# Quickstart

This section should go through step-by-step examples of how your plugin should be used.
Where your plugin provides multiple dock widgets or functions, you should split these
out into separate subsections for easy browsing. Include screenshots and videos
wherever possible to elucidate your descriptions. 

Ideally, this section should start with minimal examples for those who just want a
quick overview of the plugin's functionality, but you should definitely link out to
more complex and in-depth tutorials highlighting any intricacies of your plugin, and
more detailed documentation if you have it.

# Additional Install Steps (uncommon)
We will be providing installation instructions on the hub, which will be sufficient
for the majority of plugins. They will include instructions to pip install, and
to install via napari itself.

Most plugins can be installed out-of-the-box by just specifying the package requirements
over in `setup.cfg`. However, if your plugin has any more complex dependencies, or 
requires any additional preparation before (or after) installation, you should add 
this information here.

# Getting Help

This section should point users to your preferred support tools, whether this be raising
an issue on GitHub, asking a question on image.sc, or using some other method of contact.
If you distinguish between usage support and bug/feature support, you should state that
here.

# How to Cite

Many plugins may be used in the course of published (or publishable) research, as well as
during conference talks and other public facing events. If you'd like to be cited in
a particular format, or have a DOI you'd like used, you should provide that information here. -->


Deconvolves a 4D light field image into a full 3D focus stack reconstruction

https://user-images.githubusercontent.com/23206511/236919283-d53ca97a-9bdd-4598-b553-34996f688237.mp4

napari-LF contains an analytic and neural net analysis methods for light field images. To download example light field images, see our repository [napari-LF-docs-samples](https://github.com/PolarizedLightFieldMicroscopy/napari-LF-docs-samples).

### LF Analyze
**LF Analyze**, the analytic method, provides three basic processes to Calibrate, Rectify, and Deconvolve light field images:

The **Calibrate** process generates a calibration file that represents the optical setup that was used to record the light field images. The same calibration file can be used to rectify and deconvolve all light field images that were recorded with the same optical setup, usually the same microscope and light field camera. The Calibrate process requires as input the radiometry frame, dark frame, optical parameters, and volume parameters to generate the calibration file, which is subsequently used to rectify and deconvolve related light field images. The calibration file includes a point spread function (PSF) derived from the optical and volume parameters and is stored in HDF5 file format.

The **Rectify** process uses the calibration file for an affine transformation to scale and rotate experimental light field images that were recorded with a light field camera whose microlens array was (slightly) rotated with respect to the pixel array of the area detector and whose pixel pitch is not commensurate with the microlens pitch. After rectification, the rectified light field has the same integer number of pixels behind each microlens. When the Deconvolve process is called for an experimental light field image, rectifying the light field image is automatically applied before the iterative deconvolution does begin. However, the rectified light field image is not saved and is not available for viewing. Therefore, by pushing the Rectify button in the middle of the napari-LF widget, only the rectification step is invoked and the rectified light field image is saved to the project directory.

The **Deconvolve** process uses the PSF and a wave optics model to iteratively deconvolve a light field image into a stack of optical sections.

The **Parameter** panels, located in the lower half of the napari-LF widget, allows the user to specify settings for the reconstruction process. Once the appropriate parameters are selected, the Calibrate button followed by the Deconvolve button can be pushed to complete the reconstruction.

### Neural Net
**Neural Net** provides a method of applying a trained neural net model to deconvolve a light field image. Based on Pytorch Lightning and a provided [base class](https://github.com/PolarizedLightFieldMicroscopy/napari-LF/blob/main/src/napari_lf/lfa/neural_nets/LFNeuralNetworkProto.py), you can either create your own network, or use the pre-shipped networks (LFMNet, VCDNet, ...).

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
For additional information about the reconstruction process, see our [User Guide](docs/napari-LF_UserGuide_12May2023.pdf).

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


[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[file an issue]: https://github.com/PolarizedLightFieldMicroscopy/napari-LF/issues
[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
