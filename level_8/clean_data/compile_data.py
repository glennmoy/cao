import pandas as pd
import numpy as np
from ggplot import *
import csv
import json
   
def read_course_data():
    '''
    Create nested dictionary of year:code:points:interview
    '''
    course_dict={}
    college_dict={}
    
    #First load in College codes and names to dictionary
    f=open("college_codes.dat","r")
    for line in f:
        words=line.split(" ")
        #Want to remove the \n sybol from college name
        college_dict[words[0]]=' '.join(words[1:len(words)]).rstrip('\n')

    #Now load in Course codes, descriptions and points 
    #Loop over all years    
    for year in range(2001,2016):
        courses={}

        #Open file and loop over all courses
        filename="course_data."+str(year)+".dat"
        f=open(filename,"r")
        for line in f:
            break_clause=False
            
            #Split line up into parts
            words=line.split(" ")
        
            #Course code is always first element
            code=words[0]

    
            #Look up college name in dictionary using course code
            try:
                college=college_dict[code[:2]]
            except KeyError:
                college=""

            #initialize remaining parameters
            desc=""; audition=False;  n=1

            while n<(len(words)): 

                if "Graduate" in words[n] or "graduate" in words[n] or "Mature" in words[n] or "mature" in words[n]:
                    n+=1
                    break_clause=True
                    break

                if "Portfolio" in words[n] or "portfolio" in words[n]\
                or "Audition" in words[n] or "audition" in words[n]\
                or "Interview" in words[n] or "interview" in words[n]:
                    n+=1
                    audition=True
                    continue

                #If word is a number then its the points
                try:
                    p=int(words[n].replace("*","").replace("#",""))

                    # For some reason courses are listed as 999
                    if p==999:
                        points=np.nan
                    elif  p>10 and p<=1200:
                        points=p
 
                        #if # appears in points then audition is required
                        if "#" in words[n] or "**" in words[n] or "***" in words[n]:
                            audition=True
                        break
                    else:
                        n+=1
                        continue
        
                # If word is not blank and not 'No' and not 
                # a #-symbol then add word to description
                except ValueError:
                    if words[n] and not words[n]=="No" and not words[n]=="#":
                        desc+=" "+words[n]
                n+=1

                #If no 3 digit points can be found assign nan
                points=np.nan
            
            if break_clause:
                continue

            courses[code]={'description':desc,'college':college,'points':points,'audition':audition}
            #print code,"\t",desc,"\t",points,"\t",audition
            
        f.close()

        #Nest this dictionary into the full dictionary
        course_dict[str(year)]=courses
    
    #Sample call
#    print course_dict['2004']['CK101']['description']
#    print course_dict['2015']['TR035']['points']


    #Convert dictionary to dataframe using year as index and print to .csv file
    points_df=pd.DataFrame(course_dict).transpose()
    points_df.index.name='YEAR'
    points_df.to_csv("course_points.csv",sep='\t')
    points_df.to_json("course_points.json")
    
    #Convert dataframe to column format
    f = csv.writer(open("course_points_col.csv", "wb+"))
    f.writerow(["code", "year", "points", "college", "audition","desc"])

    for year in course_dict:
        for code in course_dict[year]:
            f.writerow([code,year,course_dict[year][code]['points'],\
                        course_dict[year][code]['college'],\
                        course_dict[year][code]['audition'],\
                        course_dict[year][code]['description']])


    return 
                
points_df=read_course_data()
