# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
figure(figsize=(16, 12), dpi=160)
import datetime as dt


path=r"C:/Users/alex_/.spyder-py3/OntarioTrafficData/2006_commercial_vehicle_survey_-_traffic_volumes_at_survey_stations.csv"

df=pd.read_csv(path
             #, usecols= ("Station ID", "Station Name", "Direction", "Day of Week Number", "Hour", "Single",  "Multi", "Auto", "total_trucks", "Total vehicles")
              )

df.rename(columns={"total_trucks":"Total Trucks"}, inplace="True")

#To check where the high traffic volumes are
dfvolumes=df.groupby(["Station ID"],as_index=False).sum()
dfvolumes.sort_values(by = "Total Trucks", ascending = False, inplace = True)

#visualize just for fun/to see how much higher our selected areas are.

fig, ax = plt.subplots()
ax.bar(x=dfvolumes["Station ID"], height=dfvolumes["Total Trucks"],)
ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
ax.set_xlabel('Station IDs')  
ax.set_ylabel('Biweekly Truck Volumes')  
ax.set_title('Total Truck volumes over a two week period')

#print(dfvolumes.head()) 

#indicates ON0116, ON0115 have the highest traffic volumes. Where is ON0115,0116?

#print(df.loc[df["Station ID"]==("ON0116" or "ON0115")])
#ON0116 is Eastbound Downsview, ON0115 is Westbound.



#######Original method########

#Alternatively, knowing the 401 is the busiest highway in Canada, we could jump right to it.
df401=df.loc[df["Highway or Road"]=="Hwy 401"]

#We want to isolate the stretch with the highest average truck volume
df401stations=df401.groupby("Station ID").mean()

#again visualize to compare

fig, ax = plt.subplots(figsize=(5, 2.7))
ax.bar(x=df401["Station ID"], height=df401["Total Trucks"],)
ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
ax.set_xlabel('401 Station IDs')  
ax.set_ylabel('Hourly Truck Volumes')  
ax.set_title('Average Hourly Truck Volumes on the 401')

#print(df401stations.iloc[df401stations["Total Trucks"].argmax()])
#prints ON0116, we are likely interested in one way traffic so this is fine, but will grab
#the paired station to be safe. It's likely one number up or one down, let's check.

#df["Location Description"].loc[df["Station ID"]=="ON0116"].values is: 
#"On Highway 401, from Hwy 401 eastbound collectors west of Keele St to MTO Parking Lot north of Hwy 401 on west side of Keele St'
#df["Location Description"].loc[df["Station ID"]=="ON0115"].values is:
#On Highway 401, from Hwy 401 westbound collectors east of Keele St to MTO Parking Lot north of Hwy 401 on west side of Keele St'

 
#Now we drop some unnecessary columns. Most are related to location and now irrelevant. 
#We also drop multi and single because our data for power output does not specify truck size.
df=df.drop(columns=["Station Name", "Direction", "Location Description", "MTO Region", "Highway or Road", "Single", "Multi"])

dfeast=df.loc[df["Station ID"]=="ON0116"]
dfwest=df.loc[df["Station ID"]=="ON0115"]

#From Google maps, the 401 is 8 lanes total at this section.
#From the literature, about 40% of the trucks should be in the right lane and 5% in the left
#Otherwise we want to assume the lanes each have about the same volume, so we fill in the rest with cars.

    ####################Shoulder Turbine placement###################
    
#Eastbound

#We sum total traffic and divide by 4, subtract 2*(40% of truck volume) because one truck takes up the space of two cars
dfeast["Right East Auto"]=round(dfeast["Total vehicles"]/4-dfeast["Total Trucks"]*.8)
dfeast["Right East Trucks"]=round(dfeast["Total Trucks"]*.4)
dfeast=dfeast.drop(columns=["Station ID"])
#Check there are no negative values by mistake
#print(dfeast.min())
#A better approach would be:
#  for i in dfwest.index:
#    if dfwest["Right West Auto"].any()<0:
#        print(f"row {i} is negative")

#Westbound

#We sum total traffic and divide by 4, subtract 2*(40% of truck volume) because one truck takes up the space of two cars
dfwest["Right West Auto"]=round(dfwest["Total vehicles"]/4-dfwest["Total Trucks"]*.8)
dfwest["Right West Trucks"]=round(dfwest["Total Trucks"]*.4)
dfwest=dfwest.drop(columns=["Station ID"])
#Check there are no negative values by mistake
#print(dfwestr.min()) 


    ###################Meridian Turbine placement ###################
    
#We repeat the same idea to figure out the left lane traffic volumes and composition.
    
#Eastbound

#We sum total traffic and divide by 4, subtract 2*(5% of truck volume) because one truck takes up the space of two cars
dfeast["Left East Auto"]=round(dfeast["Total vehicles"]/4-dfeast["Total Trucks"]*.1)
dfeast["Left East Trucks"]=round(dfeast["Total Trucks"]*.05)
#Check there are no negative values by mistake
#print(dfeastr.min())

#Westbound

#We sum total traffic and divide by 4, subtract 2*(10% of truck volume) because one truck takes up the space of two cars
dfwest["Left West Auto"]=round(dfwest["Total vehicles"]/4-dfwest["Total Trucks"]*.1)
dfwest["Left West Trucks"]=round(dfwest["Total Trucks"]*.05)
#Check there are no negative values by mistake
#print(dfwestr.min())

#We need to combine our east and west data into one dataframe

#Reindex
dfwest.index = range(len(dfwest.index))
dfeast.index = range(len(dfeast.index))

#Rename some columns
dfeast=dfeast.rename(columns={"Day of Week Number": "Day of week number east", "Hour": "Hour east", "Auto": "auto east", "Total Trucks": "Total Trucks east", "Total vehicles": "Total vehicles east"})
dfwest=dfwest.rename(columns={"Total vehicles": "Total vehicles west"})

#Combine into one dataframe, drop redundant columns
dftotal=pd.concat([dfwest, dfeast], axis=1)
dftotal=dftotal.drop(columns=["Hour east", "Day of week number east", "Auto", "Total Trucks", "auto east", "Total Trucks east"], axis=1)

#Repeating the data to have a full year.
dftotal=pd.concat([dftotal]*52,axis=0)
dftotal=dftotal.append(dftotal.iloc[0:24])

#Adding dates Jan 1 2006-Dec 31 2006 and dropping redundant columns. 
#Note, the df starts on a sunday and Jan 1 2006 was a sunday!
dftotal.index = pd.date_range(start='1/1/2006', periods=len(dftotal), freq='H')
dftotal=dftotal.drop(columns=["Day of Week Number", "Hour", "Total vehicles west", "Total vehicles east"])

#Defining the seasons
winterstart = dt.datetime.strptime('2006-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
winterend = dt.datetime.strptime('2006-03-10 23:59:59', '%Y-%m-%d %H:%M:%S')

summerstart = dt.datetime.strptime('2006-06-10 00:00:00', '%Y-%m-%d %H:%M:%S')
summerend = dt.datetime.strptime('2006-09-10 23:59:59', '%Y-%m-%d %H:%M:%S')

#increasing car traffic in the summer by 10%

dftotal.loc[(dftotal.index > summerstart) & (dftotal.index < summerend), 'Right West Auto'] = round(dftotal["Right West Auto"]*1.1)
dftotal.loc[(dftotal.index > summerstart) & (dftotal.index < summerend), 'Right East Auto'] = round(dftotal["Right East Auto"]*1.1)
dftotal.loc[(dftotal.index > summerstart) & (dftotal.index < summerend), 'Left West Auto'] = round(dftotal["Left West Auto"]*1.1)
dftotal.loc[(dftotal.index > summerstart) & (dftotal.index < summerend), 'Left East Auto'] = round(dftotal["Left East Auto"]*1.1)

#decreasing car traffic in the winter by 10%
dftotal.loc[(dftotal.index > winterstart) & (dftotal.index < winterend), 'Right West Auto'] = round(dftotal["Right West Auto"]*.9)
dftotal.loc[(dftotal.index > winterstart) & (dftotal.index < winterend), 'Right East Auto'] = round(dftotal["Right East Auto"]*.9)
dftotal.loc[(dftotal.index > winterstart) & (dftotal.index < winterend), 'Left West Auto'] = round(dftotal["Left West Auto"]*.9)
dftotal.loc[(dftotal.index > winterstart) & (dftotal.index < winterend), 'Left East Auto'] = round(dftotal["Left East Auto"]*.9)


dftotal.to_csv(r'D:\Spydercodes\401SeasonalTrafficVolumes.csv', index=True)
print(dftotal)