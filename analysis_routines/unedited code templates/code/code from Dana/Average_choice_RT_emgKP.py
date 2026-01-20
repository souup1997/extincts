import os
import pandas as pd
import numpy as np
import csv
from scipy import stats

datafolder = "/Volumes/GoogleDrive/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_StarWars_2022_Dups/bandit_raw_choiceRT"
#"G:/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_StarWars_2022_Dups/bandit_raw_choiceRT/"
outputfolder = "/Volumes/GoogleDrive/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_StarWars_2022_Dups/average_choiceRT2/"
#'G:/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_StarWars_2022_Dups/average_choiceRT/'

sessionList = os.listdir(datafolder)
#list comprehension: filter out the Excel file from our list of session folders
sessionList = [x for x in sessionList if x!= 'ChoiceReactionTimeAverages_dmkp.xlsx']
sessionList.sort()


fileList = ['anakin1.csv', 'anakin3.csv', 'bantha1.csv', 'bantha2.csv', 'chewbacca1.csv', 'chewbacca2.csv', 'chewbacca3.csv', 'dooku1.csv', 'dooku2.csv', 'dooku3.csv', 'dooku4.csv', 'erso1.csv', 'erso2.csv', 'erso3.csv', 'erso4.csv', 'fett1.csv', 'fett2.csv', 'grogu1.csv', 'grogu2.csv', 'grogu3.csv', 'grogu4.csv', 'nahdar1.csv', 'nahdar2.csv', 'nahdar3.csv', 'nahdar4.csv', 'organa1.csv', 'organa2.csv', 'organa3.csv', 'organa4.csv', 'padme1.csv', 'padme2.csv', 'quigon1.csv', 'quigon2.csv', 'quigon3.csv', 'quigon4.csv', 'quigon5.csv', 'rey1.csv', 'rey2.csv', 'rey3.csv', 'rey4.csv', 'rey5.csv']

outputDict = dict(mouseID = [], bandit1 = [], bandit2 = [], bandit3 = [], bandit4 = [], bandit5 = [], bandit6 = [], bandit7 = [], bandit8 = [], bandit9 = [], bandit10 = [], bandit11 = [], bandit12 = [], bandit13 = [], bandit14 = [], bandit15 = [], bandit16 = [], bandit17 = [], bandit18 = [], bandit19 = [], bandit20 = [])

sessionList= [x for x in os.listdr(datafolder) if x != '.DS_Store']

for sessionFolder in sessionList: #for every folder in our list
    #to get list of all the files in your input folder...
    thisSession = os.path.join(datafolder,sessionFolder) #the full path to that input folder
    print(sessionFolder)
    for filename in fileList:
        if os.path.isfile(os.path.join(thisSession,filename)) == True:
            print(os.path.join(thisSession,filename))
            choiceDF = pd.read_csv(os.path.join(thisSession,filename))
            choiceDF = choiceDF[(choiceDF.zscore < 2)&(choiceDF.zscore > -2)] #filter to: everything with zscore that is less than 3 AND more than -3
            outputDict[sessionFolder].append(choiceDF['choice reaction time'].mean())
        else:
            outputDict[sessionFolder].append("MISSING")
        if sessionFolder == 'bandit1':
            outputDict['mouseID'].append(filename.split('.')[0])

outFile = pd.DataFrame(outputDict)
outFile.to_csv('/Volumes/GoogleDrive/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_StarWars_2022_Dups/average_choiceRT2/',index=False)