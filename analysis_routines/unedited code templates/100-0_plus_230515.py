import os
import os.path
import csv
import pandas as pd
#This code takes ABET output files and spits out a csv with the mouse name, number of trials, and percent correct. it now also reports number of reversals. it slices, it dices, it chops and it preps!

def main():
    """Reads a file of raw data and analyze side bias"""
    print ("This program analyzes correct percent, percent rewarded, and reversals for probabilistic training schedules")
    #folder=os.path.join(os.getcwd(),'Raw data','2022','01-12-22')
    folder=input("please enter the directory name:")
    #destinationFolder=input("Please enter the destination folder name: ")
    outFolder = "G:/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_EphysBehavior_2023/processed_data/"

    filenameList=[]
    totalNumTrialList=[]
    CorrectRateList=[]
    scheduleList = []
    nameList=[]
    dateList = []
    reversalList = []
    percentRewardList = []
    timeList=[]

    for file in os.listdir(folder):
        if "summary" in file:
            continue
        filename = os.path.join(folder, file)
        thisMouse = pd.read_csv(filename)
        name = file.partition('_')[0] #pulls everything before the "_" part of the file name and applies that to the mouse name
        date = file.partition('_')[2].partition('_')[2].partition('.')[0] #pulls everything after "_" but before "."
        numCorrect = len(thisMouse[(thisMouse.DEffectText == "High_prob_chosen")]) -1
        numIncorrect = len(thisMouse[(thisMouse.DEffectText == "Low_prob_chosen")]) -1
        numReversals = len(thisMouse[thisMouse.DEffectText == "Reversal"]) -1
        if '100-0' in thisMouse.scheduleID.unique()[0]: #"if it's 100-0..."
            numReversals = 0
        try: #had a problem when mouse did no trials so now the code tries to do math first
            CorrectRateList.append((numCorrect/(numCorrect+numIncorrect))*100)
            PercentReward = 100*((len(thisMouse[thisMouse.DEffectText == "High_prob_payoff"]) + len(thisMouse[thisMouse.DEffectText == "Low_prob_payoff"]) - 2) / (numIncorrect + numCorrect)) #ABET WHY
        except: #when math don't work, just say the mouse did 0
            CorrectRateList.append(0)
            PercentReward=0
        totalNumTrialList.append(numCorrect+numIncorrect)
        nameList.append(name)
        dateList.append(date)
        timeList.append(thisMouse.DTime.max())
        reversalList.append(numReversals)
        percentRewardList.append(PercentReward)
        scheduleList.append(thisMouse.scheduleID.unique()[0])

    rawDF = pd.DataFrame ({"animal ID": nameList, "date run": dateList, "timeTaken": timeList, "schedule": scheduleList, 'total trial': totalNumTrialList, 'percentCorrect':CorrectRateList, 'percentReward' : percentRewardList, 'numReversals' : reversalList})
    df = rawDF.sort_values(by="animal ID")
    outfile=outFolder+date+'_output.csv'
    df.to_csv(outfile,index=False)

if __name__ == "__main__":
    main()
