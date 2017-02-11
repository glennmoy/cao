# cao

In this version: Updated Jan 2017

Statistical analysis of CAO data 2001-2016

In root directory:

/downloaded_pdfs contains the pdf files containing all the data I scraped from the CAO website. 
Here they are also converted to .txt files.

/level_6-7 contains Level 6 and 7 course data. This was left in raw format.

/level_8 contains Level 8 course data. This is the data I performed the analysis on.

/points_awarded contains points awarded to Leaving Cert candidates.


In sub-directories:

/clean_data is where I scraped the .txt files for the course points and write them to .dat files
which are then compiled into a single .csv DataFrame.

/analyse_data is where I perform the analysis on the .csv files.
 
Note the *col.csv files are human-readable
