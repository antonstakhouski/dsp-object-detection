#!/usr/bin/env python3

import os
import sys
import numpy as np
import cv2


class ObjectFinder:
    def __init__(self, in_file, spath):
        self.colors = [[237, 74, 232], [49, 53, 176], [27, 191, 194], [156, 39, 3], [202, 237, 76], [138, 68, 156]]
        self.name = os.path.basename(in_file)
        self.save_path = spath
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)
        self.pic = cv2.imread(in_file, 0)
        self.res = np.zeros((self.pic.shape[0], self.pic.shape[1], 3))

    def find_objects(self):
        self.objects = []
        contours, self.hierarchy, something = cv2.findContours(self.pic, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        num = 0
        for el in self.hierarchy:
            area = cv2.contourArea(el)
            M = cv2.moments(el)
            perimeter = cv2.arcLength(el, True)
            c = (perimeter ** 2) / area
            elongation = (M['m20'] + M['m02'] + np.sqrt((M['m20'] - M['m02']) ** 2 + 4 * (M['m11'] ** 2))) /\
                (M['m20'] + M['m02'] - np.sqrt((M['m20'] - M['m02']) ** 2 + 4 * (M['m11'] ** 2)))
            theta = 1 / 2 * np.arctan(2 * M['m11'] / (M['m20'] - M['m02']))
            self.objects.append({"area": area, "perimeter": perimeter, "compactness": c,
                                "elongation": elongation, "theta": theta, "num": num})
            num += 1

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

    def show(self):
        for i in range(0, len(self.hierarchy)):
            for j in range(0, len(self.clusters)):
                for element in self.clusters[j]:
                    if i == element["num"]:
                        self.fill(i, j)
                        break

    def fill(self, num, color):
        for pixel in self.hierarchy[num]:
            self.res[pixel[0, 1], pixel[0, 0]][0] = self.colors[color][0]
            self.res[pixel[0, 1], pixel[0, 0]][1] = self.colors[color][1]
            self.res[pixel[0, 1], pixel[0, 0]][2] = self.colors[color][2]

    def run(self):
        self.n = 2
        self.find_objects()
        self.normalize()

        elements = []
        for el in self.objects:
            lst = []
            [lst.append(x[1]) for x in el.items()]
            elements.append(lst[:][:-1])
        elements = np.float32(elements)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.01)
        ret, label, center = cv2.kmeans(elements, self.n, None, criteria, 100, cv2.KMEANS_RANDOM_CENTERS)

        # Now separate the data, Note the flatten()
        self.clusters = []
        self.true_clusters = []
        for i in range(0, self.n):
            self.clusters.append(elements[label.ravel() == i].tolist())
            for i in self.clusters:
                tmpcl = []
                for j in i:
                    tmpcl.append({"area": j[0], "perimeter": j[1], "compactness": j[2], "elongation": j[3],
                                  "theta": j[4]})
            self.true_clusters.append(tmpcl)

        for i in range(0, len(self.clusters)):
            for j in range(0, len(self.clusters[i])):
                for el in self.objects:
                    if abs(self.true_clusters[i][j]['area'] - el['area']) <= 0.01 and\
                       abs(self.true_clusters[i][j]['perimeter'] - el['perimeter']) <= 0.01 and\
                       abs(self.true_clusters[i][j]['compactness'] - el['compactness']) <= 0.01 and\
                       abs(self.true_clusters[i][j]['elongation'] - el['elongation']) <= 0.01 and\
                       abs(self.true_clusters[i][j]['theta'] - el['theta']) <= 0.01:
                        self.true_clusters[i][j]['num'] = el['num']
        self.clusters = self.true_clusters
        for i in range(0, len(self.clusters)):
            print(len(self.clusters[i]))
        self.show()
        cv2.imwrite(self.save_path + "/" + self.name, self.res)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("""Usage: {} in_file out_dir""".format(sys.argv[0]))
    else:
        finder = ObjectFinder(sys.argv[1], sys.argv[2])
        finder.run()
