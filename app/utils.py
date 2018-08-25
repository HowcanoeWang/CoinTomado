import os
import shutil
import zipfile

temp_extractzip = ''


def extractzip(path):
    """Extract zip file.

    Arguments:
        path {str} -- zip directory path.
    """

    with zipfile.ZipFile(path) as fzip:
        fzip.extractall(temp_extractzip)
