# f all that and this and everything. Imma make a new way. I am god. No one can tell me what to do.

"""
AP -- 20260114
Okay so I should document what I did I guess. I took the script Dana sent me to pull files from ABET and made some edits... I was told not to do so, or rather, admonished by Dana for trying to do so early on... But I'm big and strong now. I know things. I can do it.
What I wanted was multifold:
I made it os independent -- I hope. It should work. I fixed some issues I was having with creating paths for my linux os.
I also added some edits to the summary file. So now the file is read as a df, filtered so only my mice are included, and sorted by mouseID, so I don't have to do that by hand. Amazing. I'm so proud.
"""


import shutil
import os
import pandas as pd

DMdir = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__name__)), 'raw_data'))
CSVfolder = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__name__)), '..', '..', '..', '..', 'ABETdata', 'CSV'))

mouseList = ['dodo', 'quagga']
yearDir = '2026'
dateList = ['01-16-26']


for dateDir in dateList:
    newDir = os.path.join(DMdir,yearDir,dateDir)
    if os.path.isdir(newDir) == False:
        os.makedirs(newDir)
    for file in os.listdir(os.path.join(CSVfolder,yearDir,dateDir)):
        if '_summary' not in file:
            for mouse in mouseList:
                if mouse in file:
                    newFile = os.path.join(newDir,file)
                    oldFile = os.path.join(CSVfolder,yearDir,dateDir,file)
                    shutil.copy(oldFile,newFile)
                    print(file)
        if '_summary' in file:
            sumRoot = os.path.join(dateDir+'_summary.csv')
            oldSummary = os.path.join(CSVfolder,yearDir,dateDir,sumRoot)
            newSummary = os.path.join(DMdir,yearDir,dateDir,sumRoot)
            shutil.copy(oldSummary,newSummary)
            print(sumRoot)
            sum_df = pd.read_csv(newSummary)
            sum_dfs = []
            for mouse in mouseList:
                mousedf = sum_df[(sum_df['mouseID'].str.contains(mouse))]
                sum_dfs.append(mousedf)
            summaryfile = pd.concat(sum_dfs, ignore_index=True).sort_values('mouseID') 
            summaryfile.to_csv(newSummary, index=False)


