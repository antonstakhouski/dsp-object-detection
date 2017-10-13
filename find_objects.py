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
        self.res = np.zeros(self.pic.shape)

    def find_objects(self):
        self.objects = []
        contours, self.hierarchy, something = cv2.findContours(self.pic, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
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

    def clusterization(self):
        n = 2
        self.find_centers(n)
        self.clusterize()

    def show(self):
        for i in range(0, len(self.objects)):
            for j in range(0, len(self.clusters)):
                for element in self.clusters[j]:
                    if i == element["num"]:
                        color = ((j + 1) * 255) / len(self.clusters)
                        self.fill(i, color)

    def fill(self, num, color):
        for pixel in self.hierarchy[num]:
            self.res[pixel[0, 1], pixel[0, 0]] = color

    def clusterize(self):
        min_cluster = 0
        min_metric = 1
        for i in self.objects:
            for j in range(0, len(self.centroids)):
                if self.metric(i, self.centroids[j]) <= min_metric:
                    min_metric = self.metric(i, self.centroids[j])
                    min_cluster = j
            self.clusters[min_cluster].append(i)
            self.recalc_centroid(j)
            min_metric = 1

    def recalc_centroid(self, num):
        sum_area = sum(item['area'] for item in self.clusters[num])
        sum_perimeter = sum(item['perimeter'] for item in self.clusters[num])
        sum_compactness = sum(item['compactness'] for item in self.clusters[num])
        sum_elongation = sum(item['elongation'] for item in self.clusters[num])
        sum_theta = sum(item['theta'] for item in self.clusters[num])
        self.centroids[num]['area'] = sum_area / len(self.clusters[num])
        self.centroids[num]['perimeter'] = sum_perimeter / len(self.clusters[num])
        self.centroids[num]['compactness'] = sum_compactness / len(self.clusters[num])
        self.centroids[num]['elongation'] = sum_elongation / len(self.clusters[num])
        self.centroids[num]['theta'] = sum_theta / len(self.clusters[num])

    def metric(self, obj1, obj2):
        return np.sqrt((obj1['area'] - obj2['area']) ** 2 +
                       (obj1['perimeter'] - obj2['perimeter']) ** 2 +
                       (obj1['compactness'] - obj2['compactness']) ** 2 +
                       (obj1['elongation'] - obj2['elongation']) ** 2 +
                       (obj1['theta'] - obj2['theta']) ** 2)

    def find_centers(self, n):
        max_metric = 0
        jj = 0
        ii = 0
        for i in self.objects:
            for j in self.objects:
                if self.metric(i, j) >= max_metric:
                    max_metric = self.metric(i, j)
                    ii = i
                    jj = j
        self.clusters = []
        self.centroids = []
        self.centroids.append(ii.copy())
        self.centroids.append(jj.copy())
        self.clusters.append([ii.copy()])
        self.clusters.append([jj.copy()])
        self.objects.remove(ii)
        self.objects.remove(jj)
        #
        #  max_metric = 0
        #  ii = 0
        #  for z in range(2, n):
        #      for i in self.objects:
        #          sum_metric = 0
        #          for j in self.centroids:
        #              sum_metric += self.metric(i, j)
        #          if sum_metric >= max_metric:
        #              max_metric = sum_metric
        #              ii = i
        #      self.clusters.append([ii])
        #      self.centroids.append(ii)
        #      self.objects.remove(ii)

    def run(self):
        self.find_objects()
        self.normalize()
        self.clusterization()
        self.show()
        print(len(self.clusters[0]))
        print(len(self.clusters[1]))
        #  print(len(self.clusters[2]))
        #  print(len(self.clusters[3]))
        cv2.imwrite(self.save_path + "/" + self.name, self.res)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("""Usage: {} in_file out_dir""".format(sys.argv[0]))
    else:
        finder = ObjectFinder(sys.argv[1], sys.argv[2])
        finder.run()
