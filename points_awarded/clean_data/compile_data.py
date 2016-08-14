import pandas as pd
import numpy as np
import csv

'''
Convert the .dat files into a csv
'''
def compile_points():

    my_dict={}

    for year in reversed(range(2001,2016)):

        points_dict={}
        filename="points."+str(year)+".dat"
        f=open(filename,"r")
        for line in f:
    
            points,num=line.split(" ")

            points_dict[str(points)]={'num':int(num)}
     
        f.close()
        my_dict[str(year)]=points_dict

    #print my_dict['2009']['490']

    #Convert dictionary to dataframe using year as index and print to .csv file
    points_df=pd.DataFrame(my_dict)
    points_df=points_df.fillna(np.nan)
    points_df=points_df.sort_index(axis=1,ascending=False)
    points_df.index.name='points'
    points_df.to_csv("awarded_points.csv",sep='\t')
    points_df.to_json("awarded_points.json")

    points_df_trans=points_df.transpose()
    points_df_trans.index.names=['year']
    points_df_trans.to_csv("awarded_points_trans.csv",sep='\t')

    #Convert dataframe to column format
    f = csv.writer(open("awarded_points_col.csv", "wb+"))
    f.writerow(["year", "points", "num"])

    for year in my_dict:
        for points in my_dict[year]:
            f.writerow([year,points,my_dict[year][points]['num']])

    return

compile_points()
