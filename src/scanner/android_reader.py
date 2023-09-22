import os
import tempfile

import cv2
import numpy as np

from src.common.constants import Constants


class AndroidReader:
    """
    Reads the image from the connected devices
    """
    def __init__(self, debug_mode: bool) -> None:
        self.debug_mode = debug_mode

    def read_level_image(self):
        temp_filename = tempfile.mktemp() + ".png"
        if self.debug_mode:
            print(f"Reading image in {temp_filename}")
        os.system(f"{Constants.ADB_PATH} exec-out screencap -p > {temp_filename}")
        image: np.ndarray = cv2.imread(temp_filename)
        os.system(f"rm {temp_filename}")
        return image
