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
        self.pic = cv2.imread(in_file, 0)

    def find_objects(self):
        self.objects = []
        contours, hierarchy, something = cv2.findContours(self.pic, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for el in hierarchy:
            area = cv2.contourArea(el)
            M = cv2.moments(el)
            perimeter = cv2.arcLength(el, True)
            c = (perimeter ** 2) / area
            elongation = (M['m20'] + M['m02'] + np.sqrt((M['m20'] - M['m02']) ** 2 + 4 * (M['m11'] ** 2))) /\
                (M['m20'] + M['m02'] - np.sqrt((M['m20'] - M['m02']) ** 2 + 4 * (M['m11'] ** 2)))
            theta = 1 / 2 * np.arctan(2 * M['m11'] / (M['m20'] - M['m02']))
            self.objects.append({"area": area, "perimeter": perimeter, "compactness": c,
                                "elongation": elongation, "theta": theta})

    def normalize(self):
        max_area = max(item['area'] for item in self.objects)
        max_perimeter = max(item['perimeter'] for item in self.objects)
        max_compactness = max(item['compactness'] for item in self.objects)
        max_elongation = max(item['elongation'] for item in self.objects)
        max_theta = max(item['theta'] for item in self.objects) + 1
        for i in range(0, len(self.objects)):
            self.objects[i]['area'] = self.objects[i]['area'] / max_area
            self.objects[i]['perimeter'] = self.objects[i]['perimeter'] / max_perimeter
            self.objects[i]['compactness'] = self.objects[i]['compactness'] / max_compactness
            self.objects[i]['elongation'] = self.objects[i]['elongation'] / max_elongation
            self.objects[i]['theta'] = (self.objects[i]['theta'] + 1) / max_theta
        print(self.objects)

    def clusters(self):
        pass

    def run(self):
        self.find_objects()
        self.normalize()
        #  cv2.imwrite("lol.png", resa)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("""Usage: {} in_file out_dir""".format(sys.argv[0]))
    else:
        finder = ObjectFinder(sys.argv[1], sys.argv[2])
        finder.run()
