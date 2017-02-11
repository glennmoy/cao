#!/bin/bash

for image in `ls *pdf`; do
    name=`echo $image | cut -d'.' -f1`
    echo $image $name
    sips -s format png $image --out $name.png
done
