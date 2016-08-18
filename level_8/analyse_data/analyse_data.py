import numpy as np
import pandas as pd
import pandasql as ps
import csv
import scipy.stats
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.text 

# I'm going to use seaborn palette
current_palette=sns.color_palette()

# Import data
# [code year points college audition]
cao_data=pd.read_csv('course_points_col.csv')
# [year points num]
cand_data=pd.read_csv('awarded_points_col.csv')

'''
0. CAO Data  
    - Focus on level 8 courses 2001-2015, old data harder to compile
    - First round offers only: not everyone gets a place; not everyone accepts a place
    - No mature or graduate students considered (except mature nursing)
    - Missing values: AQA, course no longer running need to be mentioned
    - Some courses may have changed name
    - TR001 needs to be averaged over all options
    
    - How to deal with non-normal points? ie based on maths bonus points and HPAT 2012+
    - Need to find out which courses criteria have changed - medicine will be most difficult
    - Can still be used in time series and predictions (as long as criteria are constant)
    - Should be omitted from histogram and overall averaging since they will skew results
'''

def do_regression(x_data,y_data,printyn):

    slope, intercept, r_value, p_value, std_err=scipy.stats.linregress(x_data,y_data)

    predicted_y=slope*x_data+intercept
    pred_error=y_data-predicted_y
    dof=len(x_data)-2
    res_std_err=np.sqrt(np.sum(pred_error**2)/dof)

    if printyn:
        print "\nslope\t=",slope
        print "intercept\t=",intercept
        print "r_value\t=",r_value
        print "p_value\t=",p_value
        print "std_err\t=",std_err

        f=plt.figure()
        ax=f.add_subplot(111)
        textstr = '$y=%.2f+%.2f*x$\n$r=%.2f$'%(intercept, slope, r_value)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top',backgroundcolor='1.0')    

        plt.scatter(x_data,y_data)
        plt.plot(x_data,predicted_y,'r-')
        plt.savefig('regression.pdf',bbox_inches='tight')
        plt.show()

    return slope,intercept,r_value,p_value,res_std_err


# Normalise the points post 2012 by subtracting 25 points
def normalise_points(factor,constant):
    for index,row in cao_data_norm.iterrows():
        if int(row['year'])>=2013 and not np.isnan(row['points']):
            p=cao_data_norm.iloc[index].points
            #cao_data_norm.set_value(index,'points',p-25)
            if p<=625:
                cao_data_norm.set_value(index,'points',(p-constant)/factor)
            else:    
                cao_data_norm.set_value(index,'points',p-25)
    return cao_data_norm 


#Do auto-regression of 2010 vs 2011
def auto_regress(df,year1,year2,printyn):

    old_points=[]
    new_points=[]

    for y in range(year1,year2):  
        old_points.extend(df[str(y)].values)
        new_points.extend(df[str(y+1)].values)

    old_points=np.array(old_points)
    new_points=np.array(new_points)

    slope, intercept,r_value,p_value,std_err=do_regression(old_points,new_points,printyn)

    return slope,intercept

#Plot of my idea behind normalising the data
q0=""" SELECT code,points,year FROM cao_data WHERE year>=2006 AND audition==0;"""
sample_data=ps.sqldf(q0,locals())
sample_data.columns=['code','points','year']
sample_data=sample_data.pivot(index='code',columns='year',values='points').dropna()
sample_data.columns=['2006','2007','2008','2009','2010','2011','2012','2013','2014','2015']
sample_data.index.name='code'

#auto_regress(sample_data,2012,2013,True)

factor,constant=auto_regress(sample_data,2012,2013,False)
cao_data_norm=cao_data.copy()
normalise_points(factor,constant)

q0=""" SELECT code,points,year FROM cao_data_norm WHERE year>=2010 AND audition==0;"""
sample_data_norm=ps.sqldf(q0,locals())
sample_data_norm.columns=['code','points','year']
sample_data_norm=sample_data_norm.pivot(index='code',columns='year',values='points').dropna()
sample_data_norm.columns=['2010','2011','2012','2013','2014','2015']
sample_data_norm.index.name='code'

#auto_regress(sample_data_norm,2012,2013,True)
#auto_regress(sample_data_norm,2010,2015,True)


def convert_new_points(points):
        return points*factor+constant


'''
1. How do number of courses compare to number of LC students?
    - Include error bars of std
    - Is there some correlation or trend? - yes, r=0.7
'''
#number of candidates per year
q1=""" SELECT year,SUM(num) FROM cand_data GROUP BY year;"""
num_cands_per_year=ps.sqldf(q1,locals())
num_cands_per_year.columns=['year','num']

#number of courses per year
q2=""" SELECT year,COUNT(code) FROM cao_data_norm GROUP BY year;"""
num_courses_per_year=ps.sqldf(q2,locals())
num_courses_per_year.columns=['year','num']

def num_cands_vs_num_courses():
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax2=ax1.twinx()
    ax1.set_ylim([50000,57000])
    ax1.set_xticklabels(['2001','2003','2005','2007','2009','2011','2013','2015'])
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Number of LC Students')
    ax1=num_cands_per_year.num.plot(ax=ax1,marker='s',color=current_palette[1],label='Number of LC Candidates')
    ax2=num_courses_per_year.num.plot(ax=ax2,marker='o',color=current_palette[0],label='Number of L8 Courses',secondary_y=True)
    ax2.set_ylim([300,1000])
    ax2.set_ylabel('Number of Courses')
    ax=plt.gca()
    lines = ax1.get_lines() + ax2.get_lines()
    ax.legend(lines, [l.get_label() for l in lines],loc='upper center')
    plt.savefig('num_cands_vs_num_courses.pdf',bbox_inches='tight')


    # Do a regression on analysis here
    slope,intercept,r_value,p_value,std_err=do_regression(num_cands_per_year.num,num_courses_per_year.num,True)

    return
#num_cands_vs_num_courses()


'''
2. How do the course points compare to number of LC students?
    - Include error bars of std
    - Is there some correlation or trend?

'''
#average points over all courses per year
q4=""" SELECT year,AVG(points) FROM cao_data GROUP BY year;"""
av_points_per_year=ps.sqldf(q4,locals())
av_points_per_year.columns=['year','points']

def num_cands_vs_av_points():
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax2=ax1.twinx()
    ax1.set_ylim([50000,59000])
    ax1.set_xticklabels(['2001','2003','2005','2007','2009','2011','2013','2015'])
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Number of LC Students')

    ax1=num_cands_per_year.num.plot(ax=ax1,marker='s',color=current_palette[1],label='Number of LC Candidates')
    ax2=av_points_per_year.points.plot(ax=ax2,marker='^',color=current_palette[2],label='Average Course Points',secondary_y=True)
    ax2.set_ylabel('Average Cut-off Points')
    ax=plt.gca()
    lines = ax1.get_lines() + ax2.get_lines()
    ax.legend(lines, [l.get_label() for l in lines],loc='upper center')
    plt.savefig('num_cands_vs_av_points.pdf',bbox_inches='tight')
    
    slope, intercept,r_value,p_value,std_err=do_regression(num_cands_per_year.num,av_points_per_year.points,True)

    return

#num_cands_vs_av_points()

#For the hell, plot num_courses vs average_points
#plt.scatter(y=av_points_per_year.points,x=num_courses_per_year.num)
#plt.show()


'''
3. Histograms of points
    - Course points over all years
    - Points awarded over all years
'''
def histograms_of_points():
    
    #All courses over all years
    mean_points=cao_data_norm.points.mean()
    std_points=cao_data_norm.points.std()

    fig=plt.figure()
    ax=fig.add_subplot(111)
    binlist=np.arange(0,1000,50)
    plt.hist(cao_data_norm.points.dropna(),binlist,color=current_palette[1])
    textstr = '$\mu=%.2f$\n$\sigma=%.2f$'%(mean_points, std_points)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top',backgroundcolor='1.0')    
    plt.xlabel('Cutoff Points')
    plt.ylabel('Number of Courses')
    plt.savefig('course_points_hist.pdf',bbox_inches='tight')
    plt.show()

 
    #Courses not requiring audition over all years
    mean_points_no_aud=cao_data_norm[cao_data_norm.audition==False].points.mean()
    std_points_no_aud=cao_data_norm[cao_data_norm.audition==False].points.std()

    binlist=np.arange(0,650,50)
    fig=plt.figure()
    ax=fig.add_subplot(111)
    textstr = '$\mu=%.2f$\n$\sigma=%.2f$'%(mean_points_no_aud, std_points_no_aud)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top',backgroundcolor='1.0')    
    plt.hist(cao_data_norm[cao_data_norm.audition==False].points.dropna(),binlist,color=current_palette[3])
    plt.xlabel('Cutoff Points')
    plt.ylabel('Number of Courses')
    plt.savefig('course_points_hist_600.pdf',bbox_inches='tight')
    plt.show()
    
    
    #Candidates points over all years
    mean_cands=cao_data.points.mean()
    std_cands=cand_data.points.std()

    fig=plt.figure()
    ax=fig.add_subplot(111)
    binlist=np.arange(0,700,50)
    textstr = '$\mu=%.2f$\n$\sigma=%.2f$'%(mean_cands, std_cands)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top',backgroundcolor='1.0')    
    plt.hist(cand_data.points.dropna(),binlist,weights=cand_data.num,color=current_palette[2])
    plt.xlabel('Points Awarded')
    plt.ylabel('Number of Candidates')
    plt.savefig('points_awarded_hist.pdf',bbox_inches='tight')
    plt.show()



    print "All points mean: ",mean_points,"\tSTD: ",std_points
    print "No Aud points mean: ",mean_points_no_aud, "\tSTD: ",std_points_no_aud
    print "Mean Candidates:", mean_cands, "\tSTD: ",std_cands

    return

#histograms_of_points()

'''
4. Ranking the Colleges
    - Rankings with/without auditions
    - Most diverse college (one with highest std)
    - Biggest jump/fall in one year
    - Faculty rankings? EMS, Health, Arts? Hard to do...
'''

'''
# Average points for all courses
q5=""" SELECT college,ROUND(AVG(points),0) FROM cao_data_norm GROUP BY college ORDER BY AVG(points) DESC;"""
av_points_per_college=ps.sqldf(q5,locals())
av_points_per_college.columns=['college','points']

# Average points for courses with no audition
q6=""" SELECT college,audition,ROUND(AVG(points),0) FROM cao_data_norm WHERE audition=0 GROUP BY college ORDER BY AVG(points) DESC;"""
av_points_per_college_no_aud=ps.sqldf(q6,locals())
av_points_per_college_no_aud.columns=['college','audition','points']

# Average points for courses with auditions
q7=""" SELECT college,audition,ROUND(AVG(points),0) FROM cao_data_norm WHERE audition=1 GROUP BY college ORDER BY AVG(points) DESC;"""
av_points_per_college_only_aud=ps.sqldf(q7,locals())
av_points_per_college_only_aud.columns=['college','audition','points']
'''

def get_college_rankings(audition,year):
    college_name=[];mean=[];std=[]

    if audition:
        if year>2000:
            for college in cao_data_norm['college'][(cao_data_norm['year']==year)].dropna().unique():
                m=cao_data_norm.dropna().points[(cao_data_norm.college==college) & (cao_data_norm.year==year)].mean()
                s=0
                college_name.append(college); mean.append(m); std.append(s)
    
        else:    
            for college in cao_data_norm['college'].dropna().unique():
                m=cao_data_norm.dropna().points[(cao_data_norm.college==college)].mean()
                s=cao_data_norm.dropna().points[(cao_data_norm.college==college)].std()
                college_name.append(college); mean.append(m); std.append(s)
        
    else:
        if year>2000:
            for college in cao_data_norm['college'][(cao_data_norm['audition']==False) & (cao_data_norm['year']==year)].dropna().unique():
                m=cao_data_norm.dropna()['points'][(cao_data_norm['college']==college) & (cao_data_norm['audition']==False) & (cao_data_norm['year']==year)].mean()
                s=0
                college_name.append(college); mean.append(m); std.append(s)
    
        else:    
            for college in cao_data_norm['college'][(cao_data_norm['audition']==False)].dropna().unique():
                m=cao_data_norm.dropna().points[(cao_data_norm.college==college) & (cao_data_norm.audition==False)].mean()
                s=cao_data_norm.dropna().points[(cao_data_norm.college==college) & (cao_data_norm.audition==False)].std()
                college_name.append(college); mean.append(m); std.append(s)
    
    rankings_df=pd.DataFrame({'college':college_name,'mean':mean,'std':std})
    rankings_df.columes=['college','mean','std']
        

    q="""SELECT college,mean,std FROM rankings_df ORDER BY mean DESC"""
    sorted_rankings=ps.sqldf(q,locals())
    sorted_rankings.columns=['college','mean','std']

    print sorted_rankings

    plot_college_rankings(sorted_rankings)
        

# Plot college rankings
def plot_college_rankings(rankings_df):
    # Careful of where min/max applies to 2+ colleges!!

    #Find min and max course points for colleges with min/max mean/std
    max_mean_college=rankings_df.head(1)
    min_mean_college=rankings_df.tail(1)

    #histogram colors will change depending on range    
    mask1=rankings_df['mean'] < 500
    mask2=rankings_df['mean'] < 400
    mask3=rankings_df['mean'] < 300
    mask4=rankings_df['mean'] < 200
    
    colors = np.array([current_palette[0]]*len(rankings_df))
    colors[np.where(mask1)] = current_palette[1]
    colors[np.where(mask2)] = current_palette[2]
    colors[np.where(mask3)] = current_palette[3]
    colors[np.where(mask4)] = current_palette[4]
    
    ax1 = rankings_df.dropna().plot(x='college',y='mean',kind='barh',figsize=(9,9.5),legend=False,fontsize=12,grid=True,color=colors)
    ax1.set_title("Average Course Points per University",fontsize=16,family='Helvetica') # x-label
    ax1.set_xlabel("Mean Points",fontsize=12) # x-label
    ax1.set_ylabel("",fontsize=12)       # y-label
    ax1.tick_params(axis='y', pad=10)    # add padding bw y-tics and y-axis
    plt.gca().invert_yaxis()            # sort by descending order
   
    # Put the points on the right hand side 
    for idx,line in rankings_df.iterrows():
           
        for p in ax1.patches:
            mean=p.get_width()
            ax1.annotate(str(int(mean)),(600,p.get_y()+1.2*p.get_height()),fontsize=12)
    
    fig=plt.gcf()
    fig.subplots_adjust(left=0.5,right=0.85,top=0.95,bottom=0.08)    # give more space to college names
    plt.savefig("college_rankings_all.pdf")
    plt.show()
    #print ggplot(av_points_per_college, aes(x='college', weight='points')) + geom_bar(stat='identity')+coord_flip()
    return

# Get college rankings and make sorted graph
# can specify if auditions or not or by year
#get_college_rankings(True,205)


'''
5. Ranking the Courses
    - Highest points to lowest (should also do since 2012 with raw points)
    - Most volative course (highest std)
    - Biggest jump/fall in one year
'''
def get_course_rankings(audition,year):
    course_name=[];mean=[];std=[];desc=[]

    if audition:
        
        if year>2000:
            for code in cao_data_norm['code'][(cao_data_norm['year']==year)].dropna().unique():
                m=cao_data_norm['points'][(cao_data_norm['code']==code) & (cao_data_norm['year']==year)].item()
                d=cao_data_norm['desc'][(cao_data_norm['code']==code) & (cao_data_norm['year']==year)].item()
                s=0 
                course_name.append(code); mean.append(m); std.append(s); desc.append(d)
        else:    
            for code in cao_data_norm['code'].dropna().unique():
                m=cao_data_norm['points'][(cao_data_norm['code']==code)].mean()
                s=cao_data_norm['points'][(cao_data_norm['code']==code)].std()
                d=cao_data_norm['desc'][(cao_data_norm['code']==code)].head(1).item()
                course_name.append(code); mean.append(m); std.append(s); desc.append(d)
    
    else:
        
        if year>2000:
            for code in cao_data_norm['code'][(cao_data_norm['audition']==False) & (cao_data_norm['year']==year)].dropna().unique():
                m=cao_data_norm['points'][(cao_data_norm['code']==code) & (cao_data_norm['year']==year)].item()
                d=cao_data_norm['desc'][(cao_data_norm['code']==code) & (cao_data_norm['year']==year)].item()
                s=0
                course_name.append(code); mean.append(m); std.append(s); desc.append(d)
        else:    
            for code in cao_data_norm['code'][(cao_data_norm['audition']==False)].dropna().unique():
                m=cao_data_norm['points'][(cao_data_norm['code']==code) & (cao_data_norm['audition']==False)].mean()
                s=cao_data_norm['points'][(cao_data_norm['code']==code) & (cao_data_norm['audition']==False)].std()
                d=cao_data_norm['desc'][(cao_data_norm['code']==code) & (cao_data_norm['audition']==False)].head(1).item()
                course_name.append(code); mean.append(m); std.append(s); desc.append(d)
        

    rankings_df=pd.DataFrame({'code':course_name,'desc':desc,'mean':mean,'std':std})
    rankings_df.columes=['code','desc','mean','std']

    q="""SELECT * FROM rankings_df ORDER BY std DESC LIMIT 10"""
    sorted_rankings=ps.sqldf(q,locals())
    sorted_rankings.columns=['code','desc','mean','std']

    print sorted_rankings.dropna()
    #plot_course_rankings(sorted_rankings)

#get_course_rankings(False,201)
'''
# Plot course rankings 
def plot_course_rankings(rankings_df):

    max_mean_course=rankings_df.dropna()['code'].head(1).item()
    min_mean_course=rankings_df.dropna()['code'].tail(1).item()
    max_mean_course_min=cao_data_norm.dropna().points[cao_data_norm.code==max_mean_course].min()
    max_mean_course_max=cao_data_norm.dropna().points[cao_data_norm.code==max_mean_course].max()
    min_mean_course_min=cao_data_norm.dropna().points[cao_data_norm.code==min_mean_course].min()
    min_mean_course_max=cao_data_norm.dropna().points[cao_data_norm.code==min_mean_course].max()

    print "\nMax/Min Mean College Points"
    print max_mean_course,"[",max_mean_course_min,",",max_mean_course_max,"]"
    print min_mean_course,"[",min_mean_course_min,",",min_mean_course_max,"]\n"


    max_std_course=rankings_df[rankings_df['std']==rankings_df.dropna().max()[2]].code.item()
    min_std_course=rankings_df[rankings_df['std']==rankings_df.dropna().min()[2]].code.item()

    max_std_course_min=cao_data_norm.dropna().points[cao_data_norm.code==max_std_course].min()
    max_std_course_max=cao_data_norm.dropna().points[cao_data_norm.code==max_std_course].max()
    min_std_course_min=cao_data_norm.dropna().points[cao_data_norm.code==min_std_course].min()
    min_std_course_max=cao_data_norm.dropna().points[cao_data_norm.code==min_std_course].max()
    
    print "\nMax/Min STD College Points"
    print max_std_course,"[",max_std_course_min,",",max_std_course_max,"]"
    print min_std_course,"[",min_std_course_min,",",min_std_course_max,"]\n"

    #histogram colors will change depending on range    
    mask1=rankings_df['mean'] < 500
    mask2=rankings_df['mean'] < 400
    mask3=rankings_df['mean'] < 300
    mask4=rankings_df['mean'] < 200
    
    colors = np.array([current_palette[0]]*len(rankings_df))
    colors[np.where(mask1)] = current_palette[1]
    colors[np.where(mask2)] = current_palette[2]
    colors[np.where(mask3)] = current_palette[3]
    colors[np.where(mask4)] = current_palette[4]
    
    ax1 = rankings_df.dropna().plot(x='code',y='mean',kind='barh',figsize=(9,9.5),legend=False,fontsize=12,grid=True,color=colors)
    ax1.set_title("Average Course Points per University",fontsize=16,family='Helvetica') # x-label
    ax1.set_xlabel("Mean Points",fontsize=12) # x-label
    ax1.set_ylabel("",fontsize=12)       # y-label
    ax1.tick_params(axis='y', pad=10)    # add padding bw y-tics and y-axis
    plt.gca().invert_yaxis()            # sort by descending order
   
    # Put the points on the right hand side 
    for idx, label in enumerate(list(rankings_df)): 
            for p in ax1.patches:
                mean=p.get_width()
                std=round(float(rankings_df['std'][rankings_df['mean']==mean].item()),2)
                ax1.annotate(str(int(mean))+", ("+str(std)+")", (600,p.get_y()+1.2*p.get_height()),fontsize=12)
    
    fig=plt.gcf()
    fig.subplots_adjust(left=0.5,right=0.85,top=0.95,bottom=0.08)    # give more space to code names
    plt.show()
    return
'''

'''
6. Time series on individual courses
    - Choose most interesting/popular ones for display
    - How can I predict 2016? ARIMA? Regression? Depends on data I suppose

    - Anything interesting about newer courses (<3 years) compared to more established ones (10+ years)
        maybe higher average points, IT related?

    - Anything interesting about finished courses (<2012)?
        did they decrease in points toward the end? Are the outdated? 
'''

#Time series for individual courses
def course_time_series(course,printyn):

    time_series=cao_data[['year','points']][cao_data['code']==course]    

    #Prediction through Linear Regression or ARIMA
    if len(time_series)>8:

        #Linear Regression on Time
        slope,intercept,r_value,p_valued,std_err=do_regression(time_series.year,time_series.points,printyn)
        lin_reg_pred=2016*slope+intercept

        #AR(1)
        slope,intercept,r_value,p_value,std_err_auto=do_regression(time_series.points.values[0:-1],time_series.points.values[1:],printyn)
        auto_reg_pred=time_series.points.values[-1]*slope+intercept
        
        #ARIMA(1,1,0)
        x2=time_series.points.values[0:-2]
        x1=time_series.points.values[1:-1]
        y=time_series.points.values[2:]
        slope, intercept,r_value,p_value,std_err_ari=do_regression((x1-x2),(y-x1),printyn)
        ari_pred=(time_series.points.values[-1]-time_series.points.values[-2])*slope+intercept+time_series.points.values[-1]

#        print course,"\t",round(lin_reg_pred,0),round(2*std_err,0),"\t",round(auto_reg_pred,0),round(2*std_err_auto,0),"\t",round(ari_pred,0),round(2*std_err_ari,0)

        return round(lin_reg_pred,0),round(2*std_err,0),round(auto_reg_pred,0),round(2*std_err_auto,0),round(ari_pred,0),round(2*std_err_ari,0)

    else:
        return 0,0,0,0,0,0


print "#Course\tLin_Reg,Err\tAR(1),Err\tARIMA(1,1,0),Err"
f = csv.writer(open("predictions_2016.csv", "wb+"))
for course in cao_data['code'][(cao_data['year']==2015)].dropna():

    lin_reg=0
    lin_reg,lr_err,ar,ar_err,arima,arima_err=course_time_series(course,False)

    if lin_reg!=0:
        f.writerow([course,lin_reg,lr_err,ar,ar_err,arima,arima_err])
    
    
f.close() 

#course='TR071'
#course_time_series(course,True)


'''
7. Time series on different sectors based on key word in description
'''
'''
#Time series for Sectors
q12="""SELECT year,AVG(points) FROM cao_data 
        WHERE desc LIKE '%Information%' OR '%Comput%' OR '%Software%' OR '%Digital%'
        GROUP BY year ORDER BY year ASC"""
time_series_norm=ps.sqldf(q12,globals())
time_series_norm.columns=['year','points']

fig=plt.figure()
ax=fig.add_subplot(111)
plt.plot(time_series_norm.year,time_series_norm.points)
plt.scatter(time_series_norm.year,time_series_norm.points,color=current_palette[2])
ax.set_xlabel('Year')
ax.set_ylabel('Average Points')
plt.savefig('industry.pdf',bbox_inches='tight')
plt.show()
'''
