"""
AP 20260212
So this code just makes a big summary of the data and what happens for every day there is data for my mice
Notes can be hand written into the data sum file
An empty row is inserted after every day for my own visualization prefrences
Currently, it has to be run in order
- we could add a line that sorts by date... but currently I'm just moving stuff if I have to re-run days
- I'll make a new script and/or edit this one if I want a different functionality in the future
"""

import os
import pandas as pd

rawDir = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__name__)), 'raw_data'))
pathCSV = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__name__)), 'data_sum_2026.csv'))
old_df = pd.read_csv(pathCSV, index_col=False)

yearDir = '2026'
dateList = ['02-09-26','02-10-26']

new_dfs = []
for date in dateList:
    dateDir = os.path.join(rawDir,yearDir,date)
    for file in os.listdir(dateDir):
        if '_summary.csv' in file:
            print(file)

            sum = pd.read_csv(os.path.join(dateDir,file))
            sum = sum.sort_values(by='mouseID')

            filename = file
            mouse = sum['mouseID']
            sex = sum['dbID'].astype(str).str[0]
            sum['dateID'] = pd.to_datetime(sum['date_run'])
            day = sum['dateID'].dt.dayofweek
            dateID = sum['dateID'].dt.date
            schedule = sum['scheduleName']
            trials = sum['numTrialsCompleted']
            
            sum_output = {
                'mouseID' : mouse,
                'sex' : sex,
                'date' : dateID,
                'weekday' : day,
                'schedule' : schedule,
                'trials' : trials
                }
            
            new_df = pd.DataFrame(sum_output)
            new_df.loc[len(new_df)] = None
            new_dfs.append(new_df)

        else:
            continue

new_df = pd.concat(new_dfs, ignore_index=True)
full_df = pd.concat([old_df, new_df], ignore_index=True)

full_df.to_csv(pathCSV, index=False)

