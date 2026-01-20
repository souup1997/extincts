import os
import pandas as pd
import subprocess
import shutil

"""
goal here is to nab all the Ephys Behavioral data and send them up Dana's way...
"""

mouseList = ["pyramid"]

CSVfolder = "R:/ABETdata/CSV/"
DMdir = "G:/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_EphysBehavior_2023/raw_data/"
#"R:/Projects/Dana/Dana_EphysBehavior_2023/raw_data/"

yearDir = '2023'
dateList = ["11-17-23", "11-20-23", "11-21-23"]


for dateDir in dateList:
    newDir = DMdir+yearDir+'/'+dateDir
    for file in os.listdir(os.path.join(CSVfolder,yearDir,dateDir)):
        mouseFlag = 0 #bc I want to only copy the summary file for a day if there are any goddamn hps in it but not copy it a billion times, now I have a little flag to tell me whether there were hps in THIS dir
        for mouse in mouseList:
            if mouse in file:
                if os.path.isdir(newDir) == False:
                    os.makedirs(newDir)
                newFile = newDir+"/"+file
                oldFile = CSVfolder+yearDir+'/'+dateDir+"/"+file
                shutil.copy(oldFile,newFile)
                mouseFlag = 1
                print(file)
        if mouseFlag == 1:
            sumRoot = dateDir + "_summary.csv"
            oldSummary = CSVfolder+yearDir+"/"+dateDir+"/"+sumRoot
            newSummary = DMdir+yearDir+"/"+dateDir+"/"+sumRoot
            shutil.copy(oldSummary,newSummary)
            mouseFlag = 0
