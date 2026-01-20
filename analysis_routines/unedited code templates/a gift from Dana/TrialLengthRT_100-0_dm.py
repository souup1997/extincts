"""
This code is a modification of bandit code intended to help us understand learning data from our mice. here we want: 

For 100-0: 
-length of each total trial
-choice reaction time (defined as latency from display time to poke time)
-reward retrieval time (defined as latency from reward release/pump to collection)
-trial initiation reaction time (defind as latency from traylight to nosepoke/initiation) -NEW

I want to see: outputs for all individuals (i.e. RT per trial), but also easy summaries... since we are only looking at the first five days of each schedule in this pass, I'm going to say we get one spreadsheet per day for all animals, not one for each mouse per day. 

We also want a summary file for all mice with means. 
"""

import os
import pandas as pd
import numpy as np
import csv
from scipy import stats
import shutil
import itertools

datafolder = "R:/Projects/Dana/Dana_StarWars_2023_Dups/training_data/100_0/"
#"G:/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_StarWars_2023_Dups/training_data/100_0/"

dayList = [x for x in os.listdir(datafolder) if '.csv' not in x]
for day in dayList:
    dayDir = os.path.join(datafolder,day)
    #to get list of all the files in your input folder...
    fileList = [x for x in os.listdir(dayDir) if '~' not in x and '#' not in x]
    display_time = [] 
    trial_rewarded = []
    pokes_time = []
    reward_pump = []
    trial_counter = []
    reward_collection = []
    next_trial = [] 
    choiceRT_list = []
    rewardRT_list = []
    initiationRT_list = [] # DANA ADDED THIS
    mouseList = []
    last_size = 0
    fileList.sort()
    for filename in fileList:
        train_raw = pd.read_csv(os.path.join(dayDir,filename))
        mouseID = filename.split('_')[0]
        print(day + "_"+mouseID+": " + train_raw.scheduleID.unique()[0])
        dropCols = [x for x in train_raw.columns if 'Unnamed' in x]
        train = train_raw[train_raw.DTime > 0].drop(columns=dropCols)
        print(os.path.join(dayDir,filename))
        #This shows the contents of the .csv file in powershell.
        train = train.sort_values(by='DAuto')
        #This shows the column names. The data that I need to access is in the column "Item_name".
        Item_Name = train['DEffectText']
        Evnt_Name = train['DEventText']
        Evnt_Time = train['DTime']
        Arg1_Value = train['DValue1']
        Arg3_Value = train['DValue3']
        Arg4_Value = train['DValue4']
        for n in Item_Name.index:
            if Item_Name[n] == "Display Images": # Pulling "Display Image" in timestamp from raw csv column DEffectText and adding it to display times
                display_time.append(Evnt_Time[n])
            if Item_Name[n] == "Correct": 
                pokes_time.append(Evnt_Time[n])
                trial_rewarded.append('yes')
            if Item_Name[n] == "Incorrect": 
                pokes_time.append(Evnt_Time[n])
                trial_rewarded.append('no')
                reward_pump.append('na')
            if Item_Name[n] == "Feeder #1":
                if int(Evnt_Time[n]) == 0:
                    continue
                else: 
                    reward_pump.append(Evnt_Time[n])
            if Item_Name[n] == "Reward Collected Start ITI":
                reward_collection.append(Evnt_Time[n])
            if Item_Name[n] == "_Trial_Counter": #instead of "Next Trial" this output seems to say "First_Trial" throughout the code. Is this the same thing? 
                trial_counter.append(Evnt_Time[n])
            if Item_Name[n] == "Next trial": #instead of "Next Trial" this output seems to say "First_Trial" throughout the code. Is this the same thing? 
                next_trial.append(Evnt_Time[n])
        for var in [display_time,pokes_time,reward_pump,reward_collection,next_trial]:
            if var != reward_collection and len(var) != len(reward_collection) and var!=next_trial:
                var.pop()
            print("us " + str(len(var)))
        last_size = len(reward_collection) - len(mouseList)
        print(last_size)
        mouseList = mouseList + list(itertools.repeat(mouseID,last_size))
        print("mouseList: " + str(len(mouseList)))
        if len(trial_counter) != len(reward_collection):
            trial_counter.append('na')
        if len(next_trial) != len(reward_collection):
            next_trial.append('na')
        print("us " + str(len(trial_counter)))
    for t in range(len(next_trial)): #Change this to initiation for later training schedules
        if next_trial[t] == 'na':
            initiationRT_list.append('na')
        else:
            initiationRT_list.append(next_trial[t]-display_time[t])         
    #Here I made a matrix and used it to create a dataframe. A data frame was necessary to export as a csv file.
    for j in range(len(reward_collection)):
        if reward_pump[j] != 'na':
            rewardRT_list.append(reward_collection[j]-reward_pump[j])
        else:
            rewardRT_list.append('na')
    for j in range(len(pokes_time)):
        if pokes_time[j] != 'na':
            choiceRT_list.append(pokes_time[j]-display_time[j])
        else:
            choiceRT_list.append('na')
    trial_dur = []
    for j in range(len(display_time)):
        if trial_counter[j] == 'na' or display_time[j] == 'na':
            trial_dur.append('na')
        else:
            trial_dur.append(trial_counter[j]-display_time[j])
    training_output = {'mouseID': mouseList, 'display timestamp': display_time, 'pokes timestamp': pokes_time, 'pump timestamp': reward_pump, 'reward collection timestamp': reward_collection, 'trial counter' : trial_counter, 'next trial timestamp': next_trial, 'initiation reaction time': initiationRT_list, 'choice reaction time': choiceRT_list, 'retrieval reaction time': rewardRT_list,'trial_dur' : trial_dur}
    df = pd.DataFrame(training_output)
    unrewarded_idx = df[df['pump timestamp'] == 'na'].index
    df.loc[unrewarded_idx,['reward collection timestamp']] = 'na'
    #Check that the dataframe was created.
    #Exported as a CSV file:
    df.to_csv(os.path.join(datafolder,day  + "_allAnimals_100_0.csv"),index=False)

#for debugging--does not need to run
for key in training_output.keys():
    print(key + ": " + str(len(training_output[key])))

#now we have them all, let's do our summary sheet...
sumDict = dict(mouseID=[], day=[], initiationRT =[], choiceRT=[], retrievalRT=[], avg_trialLength=[], initiationRT_filt=[], choiceRT_filt=[], retrievalRT_filt=[], avg_trialLength_filt=[])
for day in dayList: 
    dayDF = pd.read_csv(os.path.join(datafolder,day  + "_allAnimals_100_0.csv"))
    for val in ['initiation reaction time', 'choice reaction time', 'retrieval reaction time', 'trial_dur']:
        new_val = val.replace(' ','_')+"_zScore"
        dayDF[new_val] = ''
        dayDF[new_val] = stats.zscore(pd.to_numeric(dayDF[dayDF[val]!='na'][val]))
        dayDF.to_csv(os.path.join(datafolder,day  + "_allAnimals_100_0.csv"),index=False)
    for mouse in dayDF.mouseID.unique():
        thisMouse = dayDF[dayDF.mouseID==mouse]
        choiceMean = pd.to_numeric(thisMouse[thisMouse['choice reaction time'] != 'na']['choice reaction time']).mean()
        choiceMean_filt = pd.to_numeric(thisMouse[abs(thisMouse.choice_reaction_time_zScore) < 3][thisMouse['choice reaction time'] != 'na']['choice reaction time']).mean()
        retrieveMean = pd.to_numeric(thisMouse[thisMouse['retrieval reaction time'] != 'na']['retrieval reaction time']).mean()
        retrieveMean_filt = pd.to_numeric(thisMouse[abs(thisMouse.retrieval_reaction_time_zScore) < 3][thisMouse['retrieval reaction time'] != 'na']['retrieval reaction time']).mean()
        initiationMean = pd.to_numeric(thisMouse[thisMouse['initiation reaction time'] != 'na']['initiation reaction time']).mean()
        initiationMean_filt = pd.to_numeric(thisMouse[abs(thisMouse.initiation_reaction_time_zScore) < 3][thisMouse['initiation reaction time'] != 'na']['initiation reaction time']).mean() #DANA ADDED THIS SECTION (THIS AND THE TWO LINES ABOVE IT)
        sumDict['mouseID'].append(mouse)
        sumDict['day'].append(day)
        sumDict['choiceRT'].append(choiceMean)
        sumDict['retrievalRT'].append(retrieveMean)
        sumDict['initiationRT'].append(initiationMean) #DANA ADDED THIS.
        sumDict['avg_trialLength'].append(pd.to_numeric(thisMouse.trial_dur[thisMouse.trial_dur!='na']).mean())
        sumDict['choiceRT_filt'].append(choiceMean_filt)
        sumDict['retrievalRT_filt'].append(retrieveMean_filt)
        sumDict['initiationRT_filt'].append(initiationMean_filt) #DANA ADDED THIS.
        sumDict['avg_trialLength_filt'].append(pd.to_numeric(thisMouse.trial_dur[thisMouse.trial_dur!='na'][abs(thisMouse.trial_dur_zScore) < 3]).mean())

sumDF = pd.DataFrame(sumDict)
sumDF = sumDF.sort_values(['day','mouseID'])

sumDF.to_csv(os.path.join(datafolder,"100-0_summaryDF.csv"), index=False)

