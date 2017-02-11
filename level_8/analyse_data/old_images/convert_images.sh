#########################################################################
#           Convert all PDFs to png images for us with Jekyll.          #
#               Written by Glenn Moynihan August 2016                   #
#########################################################################

#!/bin/bash

for file in `ls *pdf`; do
    echo $file
    outfile="${file%%.*}"

     sips -s format png $file --out $outfile.png


done
