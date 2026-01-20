import os
import pandas as pd
import numpy as np
import csv
from scipy import stats

datafolder = "G:/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_StarWars_2022_Dups/bandit_raw"
outputfolder = datafolder + '_rewardRT/'

for sessionFolder in os.listdir(datafolder):
    #to get list of all the files in your input folder...
    thisSession = os.path.join(datafolder,sessionFolder)
    sessionOutputDir = os.path.join(outputfolder,sessionFolder)
    if os.path.isdir(sessionOutputDir) is False:
        os.makedirs(sessionOutputDir)
    fileList = os.listdir(thisSession)
    for filename in fileList:
        if "UMN" in filename:
            #add here: if UMN is in the file name then...
            with open(os.path.join(thisSession,filename), newline = '') as csvfile:
                csvReader = csv.reader(csvfile, delimiter = ',')
                lineCount = 0
                for line in csvReader:
                    lineCount += 1
                    if lineCount == 11:
                        name = line[1].lower()
            bandit_raw = pd.read_csv(os.path.join(thisSession,filename), header = 18)
            bandit = bandit_raw[bandit_raw.DTime > 0]
            bandit = bandit.sort_values(by='Evnt_ID')
            Item_Name = bandit['Item_Name']
            Evnt_Name = bandit['Evnt_Name']
            Evnt_Time = bandit['Evnt_Time']
            Arg1_Value = bandit['Arg1_Value']
            Arg3_Value = bandit['Arg3_Value']
            Arg4_Value = bandit['Arg4_Value']
        else:
            bandit_raw = pd.read_csv(os.path.join(thisSession,filename))
            bandit_raw = bandit_raw.sort_values('DAuto')
            print(os.path.join(thisSession,filename))
            #This shows the contents of the .csv file in powershell.
            #print(bandit)
            name = filename.split('_')[0]
            bandit = bandit_raw[bandit_raw.DTime > 0]
            bandit = bandit.sort_values(by='DAuto')
            #This shows the column names. The data that I need to access is in the column "Item_name".
            Item_Name = bandit['DEffectText']
            Evnt_Name = bandit['DEventText']
            Evnt_Time = bandit['DTime']
            Arg1_Value = bandit['DValue1']
            Arg3_Value = bandit['DValue3']
            Arg4_Value = bandit['DValue4']
    #Here I create an empty list. I will want this to be a column in my dataframe later on.
        pokes_time = []
        collected = []

    #I created a for loop to run through the data file searching for the following strings:
        for n in Item_Name.index:
            if Item_Name[n] == "Reward Collected Start ITI":
                collected.append(Evnt_Time[n])
            elif Item_Name[n] == "L side touched, reward" or Item_Name[n] == "C side touched, reward" or Item_Name[n] == "C touched, reward" or Item_Name[n] == "R side touched, reward":
                pokes_time.append(Evnt_Time[n])
        
        print(len(pokes_time))
        print(len(collected))
        if len(pokes_time) != len(collected):
            pokes_time.pop(len(collected))
        #subtracting the two lists from one another to get retrieval reaction time list.
        rt_list2 = np.array(collected) - np.array(pokes_time)
        rt_zscore = stats.zscore(rt_list2)
        #Here I made a matrix (with only one column) and used it to create a dataframe. A data frame was necessary to export as a .csv file.
        bandit_output = {'pokes timestamp': pokes_time, 'reward collected timestamp': collected, 'reward retrieval reaction time': rt_list2, "zscore": rt_zscore}
        df = pd.DataFrame(bandit_output)
        #Exported as a CSV file:
        df.to_csv(os.path.join(sessionOutputDir, str(name) + ".csv"),index=False)
        print("The output file can now be found in the folder.")
        print(" ")