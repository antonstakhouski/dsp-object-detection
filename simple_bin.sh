#!/bin/bash
out=$(echo $1 | cut -f 1 -d '.')
java -jar "cos-1.8.jar" $1 $out
mv $out\\binary_.png tmp.png
