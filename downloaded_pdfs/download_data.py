#########################################################################
#  Mine all points related .pdf, .htm and .php files from cao website.  #
#               Written by Glenn Moynihan August 2016                   #
#                       Updated February 2017                           #
#########################################################################

import urllib
import re

# My data base is the CAO website
database="http://www.cao.ie/index.php?page=points&bb=mediastats"

# I want to find all the links related to points
website=urllib.urlopen(database)
html=website.read()
year_links = re.findall('"(.*points*?)"', html)

# Now for each link I want to go to that page and find all pdfs, htm and php
for link in year_links:

    # remove 'amp;' string
    link=link.replace("amp;","")
    # append to cao handle
    link="http://www.cao.ie/"+link

    # open each one and find all pdfs
    page=urllib.urlopen(link)
    html=page.read()
    pdfdataset=re.findall('"(.*pdf?)"', html)
    htmdataset=re.findall('"(.*htm)"', html)
    phpdataset=re.findall('"(.*points.*php)"', html)

    # list datapages and download to directory
    for datapage in htmdataset:
        print '     ',datapage
        pagename=datapage.rsplit('/',1)[1]
        urllib.urlretrieve(datapage,"./"+pagename)

    for datapage in pdfdataset:
        print '     ',datapage
        pagename=datapage.rsplit('/',1)[1]
        urllib.urlretrieve(datapage,"./"+pagename)

    for datapage in phpdataset:
        print '     ',datapage
        pagename=datapage.rsplit('/',1)[1]
        urllib.urlretrieve(datapage,"./"+pagename)
