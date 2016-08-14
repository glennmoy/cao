import urllib
import re

# My data base is the CAO website
database="http://www.cao.ie/index.php?page=points&bb=mediastats"

# I want to find all the links to the various years
website=urllib.urlopen(database)
html=website.read()
year_links = re.findall('"(.*points*?)"', html)

# Now for each year I want to go to that page and find all pdfs
for link in year_links:

    # remove 'amp;' string
    link=link.replace("amp;","")
    # append to cao handle
    link="http://www.cao.ie/"+link
    print link

    # open each one and find all pdfs
    page=urllib.urlopen(link)
    html=page.read()
    pdfdataset=re.findall('"(.*pdf?)"', html)
    htmdataset=re.findall('"(.*htm)"', html)

    # list datapages and download
    for datapage in htmdataset:
        print '     ',datapage
        pagename=datapage.rsplit('/',1)[1]
        urllib.urlretrieve(datapage,"./"+pagename)

    for datapage in pdfdataset:
        print '     ',datapage
        pagename=datapage.rsplit('/',1)[1]
        urllib.urlretrieve(datapage,"./"+pagename)
