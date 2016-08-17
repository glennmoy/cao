#!/bin/bash

for file in `ls *pdf`; do
    echo $file
    outfile="${file%%.*}"

     sips -s format png $file --out $outfile.png


done
