# This file contains functions of general utility used throughout LFAnalyze.

def ensure_path(path):
    """ Check if a path exists. If not, create the necessary directories, 
    but if the path includes a file, don't create the file"""
    import os, errno
    dir_path = os.path.dirname(path)
    if len(dir_path) > 0:  # Only run makedirs if there is a directory to create!
        try:
            os.makedirs(dir_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
    return path

if __name__ == "__main__":
    pass
