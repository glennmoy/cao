#!/bin/bash

for year in 01 02 03 04 05 06; do

    file=lc${year}pts.txt
    rm points.20$year.dat

    num=`cat  $file | grep "600 " | tail -1 | awk '{print $6}' | sed 's/,//g'`
    echo 600 $num >> points.20$year.dat
    
    for p in `seq 550 -50 100`; do
        num=`cat  $file | grep "from $p " | tail -1 | awk '{print $8}' | sed 's/,//g'`
        echo $p $num >> points.20$year.dat
    
    done

    num=`cat $file | grep "less than " | tail -1 | awk '{print $7}' | sed 's/,//g'`
    echo 0 $num >> points.20$year.dat
done


for year in 07 08 09 10 11 12 13 14 15; do

    file=lc${year}pts.txt
    rm points.20$year.dat

    num=`cat  $file | grep "600 " | tail -1 | awk '{print $6}' | sed 's/,//g'`
    echo 600 $num >> points.20$year.dat

    for p in `seq 590 -10 100`; do
        num=`cat  $file | tail -53 | grep "$p\/" | grep "$p" | awk '{print $6}' | sed 's/,//g'`
        echo $p $num >> points.20$year.dat
    
    done

    if [ "$year" = "08" ]; then

        tot=`grep "presenting" lc08pts.txt | awk '{print $6}' | sed 's/,//g'`
        subtot=`tail -2 lc08pts.txt | head -1 | awk '{print $9}' | sed 's/,//g'`
        num=`echo "$tot-$subtot" | bc`
    else
        num=`cat $file | tail -53 | grep "100" | tail -1 | awk '{print $7}' | sed 's/,//g'`
    fi
    
    echo 0 $num >> points.20$year.dat
done


