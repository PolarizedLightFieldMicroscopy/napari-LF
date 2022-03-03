import numpy as np
import os
import cv2

def load_image(filename, dtype = None, normalize = False):
    """
    Load the image supplied by the user using OpenCV, and then
    immediately convert it to a numpy array.  The user may request
    that it be cast into a specific data type, or (in the case of
    floating point data) normalized to the range [0, 1.0].
    """
    if not os.path.exists(filename):
        raise IOError("File \"" + filename + "\" does not exist.")
    
    filetype = filename.split('.')[-1]
    if filetype.lower() == 'tif':
        import tifffile
        # Does not account for tif images with multiple directories/slices.
        im = tifffile.imread(filename)
        # Squeeze may be necessary.
        # im = np.squeeze(im)
    elif filetype.lower() == 'jpg':
        # convert RGB to monochromatic
        im = np.asarray(cv2.imread(filename, cv2.CV_LOAD_IMAGE_GRAYSCALE))
    else:
        try:
            im = np.asarray(cv2.imread(filename, -1))
        except:
            im = np.asarray(cv2.LoadImage(filename, -1))
            im = np.asarray(im.ravel()[0][:]) # hack
            print("You are using an old version of openCV. Loading image using cv2.LoadImage.")

    if not im.shape:
        raise IOError("An error occurred while reading \"" + filename + "\"")

    # The user may specify that the data be returned as a specific
    # type.  Otherwise, it is returned in whatever format it was
    # stored in on disk.
    if dtype:
        im = im.astype(dtype)

    # Normalize the image if requested to do so.  This is only
    # supported for floating point images.
    if normalize :
        if (im.dtype == np.float32 or im.dtype == np.float64):
            return im / im.max()
        else:
            raise NotImplementedError
    else:
        return im


def save_image(filename, image, dtype = None):
    import tifffile
    """
    Save the image to disk using OpenCV or libtiff.  The file format
    to use is inferred from the suffix of the filename.  OpenCV is
    used to write all file types except for tiff images.

    When saving tiffs, you may a 2D or 3D image into save_image().  A
    3D image will be saved as a tif stack automatically.
    """
    filetype = filename.split('.')[-1]

    # Test if there is no filetype
    if filename == filetype or len(filetype) > 3:
        raise IOError('Could not write file \'%s\'.  You must specify a file suffix.' % (filename))

    if os.path.dirname(filename) and not os.path.exists(os.path.dirname(filename)):
        raise IOError("Directory \"" + os.path.dirname(filename) +
                      "\" does not exist.  Could not save file \"" + filename + "\"")

    # If the user has specified a data type, we convert it here.
    if dtype is not None:
        image = image.astype(dtype)

    # For now we transpose the data since it is stored in y,x,z order.
    # We can remove this later when we switch to z,y,x.
    if len(image.shape) >2:
        image = np.moveaxis(image,2,0)
    tifffile.imsave(filename,image)

