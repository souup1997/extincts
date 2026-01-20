import os
import os.path
import csv
import pandas as pd
from scipy import stats
import numpy as np


def main():
    folder=input("please enter the directory name:")
    
    oreRTList = []
    oitRTList = []
    for i in range (1,33):
        oreRT = []
        oitRT = []
        
        df = pd.read_csv(os.path.join((str(folder) +'\\' + str(i) +'.csv')), index_col = None, header = 0)
        
        RT = df['RT']
        state = df['RL label'].tolist()

        zList = (RT - RT.mean())/RT.std(ddof=0)

        for j in range (len (RT)):
            if zList[j] <= 3 and zList[j] >= -3:
                if state[j] == 0:
                    oreRT.append(round (RT[j],2))
                else:
                    oitRT.append(round (RT[j],2))

        oreRT = [m for m in oreRT if m != 0]
        oitRT = [n for n in oitRT if n != 0]
        
        
        exploreRT = np.mean (oreRT)
        exploitRT = np.mean (oitRT)
    
        oreRTList.append(exploreRT)
        oitRTList.append(exploitRT)
                    
    dataDict1 = { 'explore RT': oreRTList, 'exploit RT': oitRTList}
    df1 = pd.DataFrame(dataDict1)
    df1.to_csv( 'output.csv')

    
        
    

                        
if __name__ == "__main__":
    main()