import os
import pandas as pd
import numpy as np
import csv

datafolder = "G:/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_EphysBehavior_2023/bandit_raw/bandit15"
outputfolder = datafolder[0:len(datafolder)] + '_processed//'

if os.path.isdir(outputfolder) is False:
    os.makedirs(outputfolder)

#to get list of all the files in your input folder...
fileList = os.listdir(datafolder)
for filename in fileList:
    if "UMN" in filename:
        #add here: if UMN is in the file name then...
        with open (os.path.join(datafolder,filename), newline = '') as csvfile:
            csvReader = csv.reader(csvfile, delimiter = ',')
            lineCount = 0
            for line in csvReader:
                lineCount += 1
                if lineCount == 11:
                    name = line[1].lower()
        bandit_raw = pd.read_csv(os.path.join(datafolder,filename), header = 18)
        bandit = bandit_raw[bandit_raw.DTime > 0]
        bandit = bandit.sort_values(by='Evnt_ID')
        Item_Name = bandit['Item_Name']
        Evnt_Name = bandit['Evnt_Name']
        Evnt_Time = bandit['Evnt_Time']
        Arg1_Value = bandit['Arg1_Value']
        Arg3_Value = bandit['Arg3_Value']
        Arg4_Value = bandit['Arg4_Value']
    else:
        bandit_raw = pd.read_csv(os.path.join(datafolder,filename))
        print(os.path.join(datafolder,filename))
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
        #Here I create empty lists. I will want these to be the columns in my dataframe later on.
    left_probability = []
    right_probability = []
    choice_chosen = []
    reward_outcome = []
    #Empty lists for reaction time
    display_time = []
    pokes_time = []
    next_trial = []
    rt_list = []
    rt_list1 = []
    #I created a for loop to run through the data file searching for the following strings:
    for n in Item_Name.index:
        if Item_Name[n] == "Reward_value_R":
            right_probability.append(Arg1_Value[n]) #When "Reward_value_R" is found in Item_Name column, add the corresponding value from Arg1_Value column to the right_probability list.
        if Item_Name[n] == "Reward_value_L":
            left_probability.append(Arg1_Value[n]) #When "Reward_value_L" is found in Item_Name column, add the corresponding value from Arg1_Value column to the left_probability list.
        if Item_Name[n] == "L side touched, reward":
            choice_chosen.append(1) #When the mouse chooses the left side this will be indicated by the integer 1 in the choice_chosen list.
            reward_outcome.append(1) #When the mouse chose correctly and/or recieved reward this will be indicated by the integer 1 in the reward_outcome list.
        if Item_Name[n] == "R side touched, reward":
            choice_chosen.append(2) #When the mouse chooses the right side this will be indicated by the integer 3 in the choice_chosen list.
            reward_outcome.append(1) #When the mouse chose correctly and/or recieved reward this will be indicated by the integer 1 in the reward_outcome list.
        if Item_Name[n] == "L side touched, no reward":
            choice_chosen.append(1) #When the mouse chooses the left side this will be indicated by the integer 1 in the choice_chosen list.
            reward_outcome.append(0) #When the mouse chose incorrectly and/or didn't recieved reward this will be indicated by the 0 in the reward_outcome list.
        if Item_Name[n] == "R side touched, no reward":
            choice_chosen.append(2) #When the mouse chooses the right side this will be indicated by the integer 3 in the choice_chosen list.
            reward_outcome.append(0) #When the mouse chose incorrectly and/or didn't recieved reward this will be indicated by the 0 in the reward_outcome list.
        if Item_Name[n] == "Display Images":
            display_time.append(Evnt_Time[n])
        elif Item_Name[n] == "L side touched, reward" or Item_Name[n] == "R side touched, reward" or Item_Name[n] == "L side touched, no reward" or Item_Name[n] == "R side touched, no reward":
            pokes_time.append(Evnt_Time[n])
        if Item_Name[n] == "Next trial":
            next_trial.append(Evnt_Time[n])
    #This deletes the first occurance of each of these items, since when they appear in the .csv file, the trials have not begun yet. For reference, the trials begin on row 123 of the .csv file when the value in the Evnt_time column changes to 0.004.
        #I used the below code to check the lengths of each future column. They should all be the same length since probabilities, choice chosen, and reward outcome apply to every trial.
        # print(len(left_probability))
        # print(len(right_probability))
        # print(len(choice_chosen))
        # print(len(reward_outcome))
    if len(left_probability) != len(choice_chosen):
        left_probability.pop()
    if len(right_probability) != len(choice_chosen):
        right_probability.pop()        #print(len(left_probability))
        #print(len(right_probability))
        #print(len(choice_chosen))
        #print(len(reward_outcome))
        ####Choice Reaction Time
        #print(len(pokes_time))
        #print (len(display_time))
    if len(pokes_time) != len(display_time):
        #display_time.pop()
        print(len(pokes_time))
        print (len(display_time))
    for j in range(len(pokes_time)):
        rt_list.append(pokes_time[j]-display_time[j])
    ####Trial Initiation Reaction Time
        #print(len(next_trial))
        #print (len(display_time))
    if len(next_trial) != len(display_time):
        del display_time[-1]
        print(len(next_trial))
        print (len(display_time))
    for t in range(len(next_trial)):
        rt_list1.append(next_trial[t]-display_time[t])
        #print(len(left_probability))
        #print(len(right_probability))
        #print(len(choice_chosen))
        #print(len(reward_outcome))
        #print(len(next_trial))
        #print(len(display_time))
        #print(len(pokes_time))
        #print(len(rt_list))
        #print(len(rt_list1))
        #Here I made a matrix and used it to create a dataframe. A data frame was necessary to export as a csv file.
    bandit_output = {'left_probability': left_probability, 'right_probability': right_probability, 'choice_chosen': choice_chosen, 'reward_outcome': reward_outcome, 'display timestamp': display_time, 'pokes timestamp': pokes_time, 'next trial timestamp': next_trial, 'choice reaction time': rt_list, 'trial initiation time': rt_list1}
    bd_lenCheck = {}
    for key in bandit_output.keys():
        bd_lenCheck[key] = len(bandit_output[key])
    df_lenCheck = pd.DataFrame(bd_lenCheck,index=['counts']).T
    if len(df_lenCheck.counts.unique()) > 1:
        trim_keys = list(df_lenCheck[df_lenCheck.counts == df_lenCheck.counts.max()].index)
        realLimit = df_lenCheck.counts.min()
        for key in trim_keys:
            bandit_output[key] = bandit_output[key][0:realLimit]
    df = pd.DataFrame(bandit_output)
    #Check that the dataframe was created.
    #print(df)
    #Exported as a CSV file:
    df.to_csv(outputfolder+ '//'+ str(name) + ".csv",index=False)
    print("The output file can now be found in the folder.")
    print(" ")
