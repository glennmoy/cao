#########################################################################
#             Convert all downloaded PDFs to .txt files                 #
#               Written by Glenn Moynihan August 2016                   #
#########################################################################

#!/bin/bash
# Once the datapages have all been downloaded we want
# to convert the pdfs to text files so we can grep them.

for file in `find . -type f -iname '*.pdf'`
do
    echo $file
    pdftotext -layout $file
done
