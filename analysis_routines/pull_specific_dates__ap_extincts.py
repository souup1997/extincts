"""
AP -- 20260114
Okay so I should document what I did I guess. I took the script Dana sent me to pull files from ABET and made some edits... It feels illegal to edit it... But I'm big and strong now. I know things. I can do it.
What I wanted was multifold:
I made it os independent -- I hope. It should work. I fixed some issues I was having with creating paths for my linux os.
I also added some edits to the summary file. So now the file is read as a df, filtered so only my mice are included, and sorted by mouseID, so I don't have to do that by hand. Amazing. I'm so proud.
"""


import shutil
import os
import pandas as pd

rawDir = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__name__)), 'raw_data')) # where the data's going (in the experiment folder, see pipeline)
CSVfolder = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__name__)), '..', '..', '..', '..', 'ABETdata', 'CSV')) # where the data's coming from (if your script is organized like mine, see pipeline)

mouseList = ['dodo', 'quagga'] # my cage names (and any misspellings)
yearDir = '2026' 
dateList = ['02-10-26'] # list of dates I need to pull data for


for dateDir in dateList: #for each date I've listed
    newDir = os.path.join(rawDir,yearDir,dateDir) # new location for files, a folder named by date, within a folder year, within raw_data
    if os.path.isdir(newDir) == False: # create folder if it doesn't exist
        os.makedirs(newDir)
    for file in os.listdir(os.path.join(CSVfolder,yearDir,dateDir)): # go through files in the day you're interested in 
        if '_summary' not in file: # for non-summary files
            for mouse in mouseList: # for each of your mice
                if mouse in file: # if their name is in the file name
                    newFile = os.path.join(newDir,file) # create new location
                    oldFile = os.path.join(CSVfolder,yearDir,dateDir,file) # identify files current location
                    shutil.copy(oldFile,newFile) # make a copy saved to new locaation
                    print(file) # keep track of progress
        if '_summary' in file: # if it's a summary file
            sumRoot = os.path.join(dateDir+'_summary.csv') # get the path
            oldSummary = os.path.join(CSVfolder,yearDir,dateDir,sumRoot) # identify location of current file
            newSummary = os.path.join(rawDir,yearDir,dateDir,sumRoot) # identify location you want it
            shutil.copy(oldSummary,newSummary) # make a copy in your new location
            print(sumRoot) # track progress
            sum_df = pd.read_csv(newSummary) # read file in new location
            sum_dfs = [] # create an empty list
            for mouse in mouseList: # for every mouse
                mousedf = sum_df[(sum_df['mouseID'].str.contains(mouse))] # filter the df so it only contains that mouse
                sum_dfs.append(mousedf) # append that df to your list
            summaryfile = pd.concat(sum_dfs, ignore_index=True).sort_values('mouseID') # concat them so you have one summary file with just your mice -- there's probably a simpler way to do this
            summaryfile.to_csv(newSummary, index=False) # save this new summary file over the copy of the original

