#!/usr/bin/env python3

import os
import sys
import numpy as np
import cv2


class ObjectFinder:
    def __init__(self, in_file, spath):
        self.name = os.path.basename(in_file)
        self.save_path = spath
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)
        self.pic = cv2.imread(in_file)

    def make_labels(self):
        res = cv2.connectedComponents(self.pic[:, :, 0], ltype=cv2.CV_32S)
        self.labels = np.zeros(self.pic.shape)
        self.objects_count = res[0] - 1
        h, w, _ = self.pic.shape
        for y in range(0, h):
            for x in range(0, w):
                self.labels[y, x] = 255 * res[1][y, x] // (res[0] - 1)

    def clusters(self):
        pass

    def run(self):
        self.make_labels()
        #  cv2.imwrite("lol.png", resa)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("""Usage: {} in_file out_dir""".format(sys.argv[0]))
    else:
        finder = ObjectFinder(sys.argv[1], sys.argv[2])
        finder.run()
