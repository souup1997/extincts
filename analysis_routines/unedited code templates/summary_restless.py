import numpy as np
import csv
import os
import os.path
import pandas as pd
"""
This file was originally written by Cathy Chen to analyze restless bandit data for mice in her pharmacology experiment. It was adapted to Madison's plant cohort (two-arm bandit with WT and 16pDEL mice) 03/16/22 with Erin Giglio, Madison, and Dana assisting.

Goals for this routine: take an input folder with pre-existing metrics and generate a data table containing summary bandit data for all mice running that day.

planned header format for the output file:

mouseID     date_run    totalTrial      meanRunLength      percentWinStay     percentLoseShift       percentStay     percentSwitch   percentReward   percentChance   pReward_Chance

to run with pasting the file thing in an input in response to the rest.

meanRunLength refers to the number of same choices in a row without switching--essentially the "stickiness" of the mouse in this run at this time.
"""

def main():
    folder="R:/cla_psyc_grissom_labshare/Projects/Anika/cryptids/bandit_processed/"
    outFolder = folder.split("bandit_processed")[0] + "bandit_output"
    if os.path.isdir(outFolder) is False:
        os.makedirs(outFolder)    

    for dateFolder in os.listdir(folder):
        print(dateFolder)
        thisDate = dateFolder.split('_')[0]
        dateList = []
        mouseList = []
        totalReward = []
        trialNum = []
        winstayList = []
        loseshiftList = []
        stayList = []
        shiftList = []
        percentRewardList = []
        percentChanceList = []
        switch_reward_list = []
        switch_NR_list = []
        runLengthList = []
        IDList = []
        for i in os.listdir(os.path.join(folder,dateFolder)):
            thisMouse = i.split('.')[0]
            print(thisMouse)
            mouseList.append(thisMouse)
            dateList.append(thisDate)
            df = pd.read_csv(os.path.join(folder,dateFolder,i))
            choiceList = df['choice_chosen'].tolist()
            rewardList = df['reward_outcome'].tolist()
            leftList = df['left_probability'].tolist()
            rightList =df['right_probability'].tolist()
            ## count the number of trial run
            trialNum.append(len(choiceList))
            ## calculate the percent reward-chance
            percentReward = rewardList.count(1)/len(rewardList)
            percentRewardList.append(percentReward)
            chanceList = []
            for h in range (len(leftList)):
                chance = (leftList[h]+rightList[h])/100/2
                chanceList.append(chance)
            percentChance = np.mean(chanceList)
            percentChanceList.append (percentChance)
            totalReward.append(percentReward-percentChance)
            ## calculate win stay lose shit
            winstay = 0
            win = 0
            loseshift = 0
            lose = 0
            for j in range (len(rewardList)-1):
                if rewardList[j] == 1:
                    win += 1
                    if choiceList[j] == choiceList [j+1]:
                        winstay +=1
                if rewardList[j] == 0:
                    lose +=1
                    if choiceList[j] != choiceList [j+1]:
                        loseshift += 1
            if win== 0:
                winstayList.append('na')
            else:
                winstayList.append(winstay/win)
            if lose == 0:
                loseshiftList.append ('na')
            else:
                loseshiftList.append(loseshift/lose)
            stay = 0
            ### stay vs. shift
            shift = 0
            for k in range (len(rewardList)-1):
                if choiceList[k] == choiceList [k+1]:
                    stay += 1
                else:
                    shift += 1
            stayList.append(stay/len(rewardList))
            shiftList.append(shift/len(rewardList))
            #### calculate run length
            runCount = 1
            runList = []
            for q in range (1,len(choiceList)):
                if choiceList[q] == choiceList[q-1]:
                    runCount += 1
                else:
                    runList.append (runCount)
                    runCount = 1
            runLength = np.mean(runList)
            runLengthList.append(runLength)
        dataDict = {"mouseID" : mouseList, "dateList": dateList, "totalTrial" : trialNum, "meanRunLength" : runLengthList, "percentWinStay" : winstayList, "percentLoseShift" : loseshiftList, "percentStay" : stayList, "percentSwitch" : shiftList, "percentReward" : percentRewardList, "percentChance" : percentChanceList, "pReward_Chance"  : totalReward}    
        rawDF = pd.DataFrame(dataDict)
        newDF = rawDF.sort_values(by="mouseID")
        newDF.to_csv(os.path.join(outFolder, thisDate + ".csv"),index=False)

if __name__ == "__main__":
    main()
