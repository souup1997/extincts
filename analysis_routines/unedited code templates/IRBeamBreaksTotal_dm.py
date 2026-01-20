import os
import pandas as pd
import numpy as np
import csv

datafolder = "/Volumes/GoogleDrive/.shortcut-targets-by-id/1ViukzrRuj2_kokqRTVQ1Au9zl4ZUhK1B/Angelica/Angelica_chefs_2022_C9G/bandit_raw"

datafolder = "G:/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_StarWars_2022_Dups/bandit_raw/"

allDict = {}
for folder in os.listdir(datafolder):
    print(folder)
    daypath = os.path.join(datafolder, folder)
    dayDict = {}
    for filename in os.listdir(daypath):
        print(filename)
        if "UMN" in filename:
            #add here: if UMN is in the file name then...
            with open (os.path.join(daypath,filename), newline = '') as csvfile:
                csvReader = csv.reader(csvfile, delimiter = ',')
                lineCount = 0
                for line in csvReader:
                    lineCount += 1
                    if lineCount == 11:
                        name = line[1].lower()
            bandit = pd.read_csv(os.path.join(daypath,filename), header = 18)
            Item_Name = bandit['Item_Name']
            Evnt_Name = bandit['Evnt_Name']
            Evnt_Time = bandit['Evnt_Time']
            Arg1_Value = bandit['Arg1_Value']
            Arg3_Value = bandit['Arg3_Value']
            Arg4_Value = bandit['Arg4_Value']
        else:
            bandit = pd.read_csv(os.path.join(daypath,filename))
            print(os.path.join(daypath,filename))
            #This shows the contents of the .csv file in powershell.
            #print(bandit)
            name = filename.split('_')[0]
            #This shows the column names. The data that I need to access is in the column "Item_name".
            Item_Name = bandit['DEffectText']
            Evnt_Name = bandit['DEventText']
            Evnt_Time = bandit['DTime']
            Arg1_Value = bandit['DValue1']
            Arg3_Value = bandit['DValue3']
            Arg4_Value = bandit['DValue4']
        #Here I create an empty list. I will want this to be a column in my dataframe later on.
        sequence_movements = []
        #I created a for loop to run through the data file searching for the following strings:
        for n in range(len(Item_Name)):
            if Item_Name[n] == "Tray #1":
                sequence_movements.append(1) #When "Reward_value_L" is found in Item_Name column, add the corresponding value from Arg1_Value column to the left_probability list.
            if Item_Name[n] == "BIRBeam #1":
                sequence_movements.append(2) #When "Reward_value_C" is found in Item_Name column, add the corresponding value from Arg1_Value column to the center_probability list.
            if Item_Name[n] == "FIRBeam #1":
                sequence_movements.append(3) #When "Reward_value_R" is found in Item_Name column, add the corresponding value from Arg1_Value column to the right_probability list.
            if Evnt_Name[n] == "Touch Down Event":
                sequence_movements.append(4)
        #This deletes the first 11 occurances in sequence_movements, since when they appear in the .csv file, the trials have not begun yet. For reference, the trials begin on row 123 of the .csv file when the value in the Evnt_time column changes to 0.004.
        del sequence_movements[0:12]
        dayDict[name] = len(sequence_movements)
    allDict[folder] = dayDict

outputfile = 'G:/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_StarWars_2022_Dups/sequence_movements_all.csv'
df = pd.DataFrame(allDict)
df.to_csv(outputfile)
