#apps/utils/checker_helper.py
import os


def af_image_exists(image_path="static/images/employees/afwan.png"):
    # Check if the file exists and is a file (not a directory)
    return os.path.isfile(image_path)