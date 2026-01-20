
import os
import os.path
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    folder=input("please enter the directory name:")
    outDir = "G:/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_EphysBehavior_2023/win_stay/"

    animalList = []
    result1List = []
    result2List = []
    fileList = os.listdir(folder)

    for i in fileList:
        df = pd.read_csv(os.path.join(folder,i), index_col = None, header = 0)

        choice = df['choice_chosen'].tolist()
        reward = df['reward_outcome'].tolist()
        state = df['state'].tolist()

        currentChoice = choice[0]

        #### switch = 1. stay = 0
        staySwitch = []

        for n in range (1,len(choice)):
            if choice[n] != currentChoice:
                staySwitch.append(1)
                currentChoice = choice[n]
            else:
                staySwitch.append(0)
                currentChoice = choice[n]

        reward = reward[:-1]
        state = state[:-1]

        winOre = 0
        winOit = 0
        WSore = 0 # win stay
        WSoit = 0

        for h in range (len(staySwitch)):
            if state[h]==0 and reward[h]==1:
                winOre += 1
                if staySwitch[h] == 0:
                    WSore +=1
            if state[h]==1 or state[h]==2  and reward[h]==1:
                winOit += 1
                if staySwitch[h] == 0:
                    WSoit +=1

        if WSore == 0:
            probWSore = 0
        else:
            probWSore = WSore/winOre

        if WSoit ==0:
            probWSoit = 0
        else:
            probWSoit = WSoit/winOit

        animalList.append(i.split('_')[0])
        result1List.append(probWSore)
        result2List.append(probWSoit)


    dataDict = {'mouseID':animalList, 'p win stay explore':result1List,'p win stay exploit':result2List}
    df = pd.DataFrame(dataDict)
    df = df.sort_values('mouseID')

    folder_pieces = os.path.split(folder)
    if folder_pieces[len(folder_pieces)-1] == '':
        newName = folder_pieces[len(folder_pieces)-2].split('_')[0]
    else:
        newName = folder_pieces[len(folder_pieces)-1].split('_')[0]

    df.to_csv(os.path.join(outDir,newName + '_p win stay by state.csv'),index=False)





if __name__ == "__main__":
    main()
