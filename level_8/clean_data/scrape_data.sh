#########################################################################
#  Scrape the .txt files for the points data and write to .dat files.   #
#               Written by Glenn Moynihan August 2016                   #
#########################################################################

#!/bin/bash
LANG=C
for file in gen01.htm gen02.htm men01.htm men02.htm psy01.htm psy02.htm deg01.htm deg02.htm deg03.htm deg04.htm; do
    year=`echo $file | grep -o '0[1-4]'`
   #gets rid of ^L character causing blank lines
     grep '[A-Z][A-Z][0-9][0-9][0-9]' $file | grep -v "TR001" | tr -dc 'A-Za-z0-9*# \r\n\t' > course_data.20$year.dat
done

for year in 05 06 07 08 09 10 11 12 13 14 15 16; do
    file=lvl8_$year.txt
     grep '[A-Z][A-Z][0-9][0-9][0-9]' $file | grep -v "TR001" | tr -dc 'A-Za-z0-9*# \r\n\t' > course_data.20$year.dat
done

#OLD CODE
#2001-2004 are .htm files 
#for file in gen01.htm gen02.htm men01.htm men02.htm psy01.htm psy02.htm deg01.htm deg02.htm deg03.htm deg04.htm; do
#
#    y=`echo $file | grep -o '0[1-4]'`
#    #grep for CAO codes
#    grep '[A-Z][A-Z][0-9][0-9][0-9]' $file | awk '{print $1}'> codes
#    #grep for course descriptions in form _course_description_
#    grep '[A-Z][A-Z][0-9][0-9][0-9]' $file | sed 's/ [0-9][0-9][0-9]//g' | awk '{$1="";print}' | sed 's/#//g' | sed 's/*//g' | sed 's/ /_/g' > desc
#    #grep course points removing *, # characters
#    grep '[A-Z][A-Z][0-9][0-9][0-9]' $file | awk '{print $(NF-1)}'  | sed "s/#//g"|sed "s/*//g" > points
#
#    #paste into files
#    paste codes desc >> course_codes.20$y.dat
#    paste codes points >> course_points.20$y.dat
#
#    #These are courses that are also interview based
#    grep "#" $file | grep -o "[A-Z][A-Z][0-9][0-9][0-9]" > courses_over600.20$y.dat
#
#done
#
#
##These are single column files, 2006-2007 are double column, need to be ammended first
#for year in 05 06 07 08 09 10 11 12 13 14 15; do
#
#    file=lvl8_$year.txt
#    #grep for CAO codes
#    grep -o '[A-Z][A-Z][0-9][0-9][0-9]' $file | awk '{print $1}'> codes
#    #grep for course descriptions in form _course_description_
#    grep '[A-Z][A-Z][0-9][0-9][0-9]' $file | sed 's/ [0-9][0-9][0-9]//g' | awk '{$1="";print}' | sed 's/#//g' | sed 's/*//g' | sed 's/ /_/g' > desc
#    #grep course points removing *, # characters
#    grep '[A-Z][A-Z][0-9][0-9][0-9]' $file | awk '{print $(NF-1)}'  | sed "s/#//g"|sed "s/*//g" > points_final
#    grep '[A-Z][A-Z][0-9][0-9][0-9]' $file | awk '{print $(NF-1)}'  | sed "s/#//g"|sed "s/*//g" > points_med
#
#    #paste into files
#    paste codes desc > course_codes.20$year.dat
#    paste codes points_final points_med > course_points.20$year.dat
#
#    #These are courses that are also interview based
#    grep "#" $file | grep -o "[A-Z][A-Z][0-9][0-9][0-9]" > courses_over600.20$year.dat
#
#done
#
#    #concatenate all courses and descriptions into list
#    cat course_codes.*.dat | uniq > cc; mv cc course_desc.all.dat
#
#    rm codes points desc course_codes* points_final points_med
