import numpy as np
import csv
import os
import os.path
import pandas as pd

def main():

    folder=input("please enter the state directory name:")


folder = "G:/Shared drives/Grissom Lab UMN/Projects/Dana/Dana_EphysBehavior_2023/HMM_output"

dateList = [x for x in os.listdir(folder) if "bandit" in x]

exploreList = []
mouseList = []
dateIDList = []

for date in dateList:
    print(date)
    for file in os.listdir(os.path.join(folder,date)):
        df = pd.read_csv(os.path.join(folder,date,file))
        state = df['state'].tolist()
        explore = state.count(0)/len(state)
        exploreList.append(explore)
        mouseList.append(file.split('_')[0])
        dateIDList.append(date[0:len(date)-10])
        

datadict = {'mouseID': mouseList, 'dateID' : dateIDList,'Pexplore': exploreList}
df1 = pd.DataFrame(datadict)
df1.to_csv('Pexplore_output.csv',index=False)


main()
