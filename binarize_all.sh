#!/bin/bash
#binarize_all in
for entry in "$1"/*
do
    python3 binarize.py $entry $2
    # echo $entry
done
