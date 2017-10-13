#!/bin/bash

for entry in binarized/*
do
    python3 find_objects.py $entry founded
    # echo $entry
done
