#!/usr/bin/env python3

import sys
from subprocess import call
import cv2
import os


class Binarizator:
    def __init__(self, in_image, spath):
        self.name = os.path.basename(in_image).replace(".jpg", "")
        self.save_path = spath
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)
        call(["./simple_bin.sh", in_image])
        self.pic = cv2.imread("tmp.png")

    def morfology(self):
        self.res = cv2.morphologyEx(self.pic, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4)))

    def show(self):
        self.morfology()
        cv2.imwrite(self.save_path + "/" + self.name + ".png", self.res)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("""Usage: {} in_file out_dir""".format(sys.argv[0]))
    else:
        binarizator = Binarizator(sys.argv[1], sys.argv[2])
        binarizator.show()
