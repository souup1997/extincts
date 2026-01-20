import os
import pandas as pd
import datetime
import matplotlib.pyplot as plt

##############################################################################################################################################
#                                                                 Functions                                                                  #
##############################################################################################################################################

# Make one big pandas dataframe from all csvs in the csvDir while keeping index
def concatDataFrames(csvDir):
    csvFiles = [x for x in os.listdir(csvDir) if ".CSV" in x and "walkLog" not in x] # Create a big list that will be concatendated
    csvFiles = sorted(csvFiles, key = lambda x: x.split("_")[1])
    dates = [datetime.datetime.strptime(i.split("_")[1],"%m%d%y") for i in csvFiles] # Parse dates
    print("Oldest file: " + datetime.datetime.strftime(min(dates).date(), "%m-%d-%Y") + " | " + "Most recent file: " + datetime.datetime.strftime(max(dates).date(), "%m-%d-%Y")) # Print out the oldest file and most recent file
    toConcat = []
    ignoreFile = [f[:16] + ".CSV" for f in csvFiles if "fixed" in f] # Create list of files that were fixed
    for file in csvFiles:
        if file in ignoreFile: continue # Skip the files that were fixed but keep using the "_fixed.CSV" versions
        toConcat.append(pd.read_csv(os.path.join(csvDir,file), header=0, parse_dates=['MM:DD:YYYY hh:mm:ss'], date_format='%m/%d/%Y %H:%M:%S', index_col=['MM:DD:YYYY hh:mm:ss']))
    df = pd.concat(toConcat, axis=0, ignore_index=False).sort_index() # Creates dataframe and sorts it by timestamps
    darkCycle = df[(df.index.hour>=8) & (df.index.hour<20)] # Only the data during the dark cycles (hours: 08:00 to 20:00)
    lightCycle = df[(df.index.hour<8) | (df.index.hour>=20)] # Only the data during the light cycles (hours: 20:00 to 08:00)
    return df, darkCycle, lightCycle

######################################################### Calculations #########################################################
# 'data' is pd.dataframe() you want to analyze
# 'walkSize' is the maxsize of the walk generated, currently the arduino code creates a 500 trial walk
def banditRewardMinusChance(data,walkDir,walkSize = 500):
    data = data.drop(data[(data.Trial_CounterL>=walkSize) | (data.Trial_CounterR>=walkSize)].index) #Removing rows where Trial Counters are >= 500 cuz we don't need them for this
    rewarded = data[data.Event=='Pellet'].Event #All rewarded trials only
    allChoices = data[(data.Event=='Left') | (data.Event=='Right')].Event #All choices (i.e. left or right) -- this excludes any choice made during timeout or when there's a pellet waiting
    rewardPercent = len(rewarded)/len(allChoices)*100
    AvgList = []
    #Get walk values from specific walk files by iterating through the walk files
    for walkFile in data.walkFilename.unique():
        dfWalk = data[data.walkFilename==walkFile]
        walkEvent = dfWalk[(dfWalk.Event=='Left') | (dfWalk.Event=='Right')] #Values only when decision was made (i.e. no pellet events or choice during ITI)
        trialsL = walkEvent['Trial_CounterL'].astype(int).to_list() #All the Trial_CounterL values converted out of pandas format
        trialsR = walkEvent['Trial_CounterR'].astype(int).to_list() #All the Trial_CounterR values converted out of pandas format
        walkValues = pd.read_csv(os.path.join(walkDir,walkFile),header=0)
        walkValuesL = walkValues.leftArm
        walkValuesR = walkValues.rightArm
        #Create list of chances for the trials completed
        for trial in range(len(trialsL)): # trialL and trialR are the same length
            AvgList.append(int((walkValuesL.iloc[trialsL[trial]].astype(int) + walkValuesR.iloc[trialsR[trial]].astype(int))/2))
    chance = sum(AvgList)/len(AvgList)
    return rewardPercent-chance #Returns percent reward minus chance

def pokePerDay(data):
    eventChoice = data.loc[(data.Event=='Left') | (data.Event=='Right')]
    ##### Per Day #####
    TPD = eventChoice.Event.resample('d').count() #Trial per hour
    avgTPD = TPD.mean()
    avgLine = [avgTPD] * len(TPD)
    ###### Graph for POKES PER DAY ######
    plt.plot(TPD.index,avgLine, linestyle='--')
    plt.plot(TPD.index,TPD)
    #plt.fill_between(TPD.index,0,max(TPD)+5,where=(TPD.index.hour>=8) & (TPD.index.hour<=20),alpha=0.5,color='.5') #Adds gray shading to lights off period (08:00 to 20:00)
    plt.ylabel('Pokes per Day')
    plt.xlabel('Date')
    #plt.title('Pokes per Hour')
    plt.show()

def pokePerCycle(data):
    dates = sorted(list(set(data.index.date))) #Get all dates (without duplicates)
    avgHour = []
    #Average number of pokes across all days per hour
    for hour in range(24):
        eventPerHour = []
        for date in dates:
            dfDate = data[data.index.date==date]
            dfHour = dfDate[dfDate.index.hour==hour]
            hourEvent = dfHour[(dfHour.Event=='Left') | (dfHour.Event=='Right')] # All choices (excluding choices during ITI or choices while pellet was in well)
            eventPerHour.append(len(hourEvent))
        avgHour.append(sum(eventPerHour)/len(eventPerHour))
    rearrangedAvg=avgHour[8:20] + avgHour[20:] + avgHour[:8] #Rearrange so it starts at 08:00 (dark cycle) and ends at 7:00 (light cycle)
    xstart = datetime.timedelta(hours=8)
    xticks = pd.Series(pd.timedelta_range(start = xstart, freq='h', periods=24))
    #Create x tickmarks for graph
    xticks = list(range(8,20)) + list(range(20,24)) + list(range(0,8))
    xticks = ["{}:00".format(str(i).zfill(2)) for i in xticks]
    #Create lines for averages for cycles
    darkAvg = sum(rearrangedAvg[:12])/len(rearrangedAvg[:12])
    lightAvg = sum(rearrangedAvg[12:])/len(rearrangedAvg[12:])
    darkAvgLine = [darkAvg] * 12
    lightAvgLine = [lightAvg] * 12
    ###### Graph for POKES PER HOUR ######
    plt.plot(xticks[:12],rearrangedAvg[:12],'o-', label="dark", color='b')
    plt.plot(xticks[12:],rearrangedAvg[12:],'o-', label="light", color='r')
    plt.plot(xticks[:12],darkAvgLine,'--',label={"avg = %4.2f" % darkAvg}, color='b')
    plt.plot(xticks[12:],lightAvgLine,'--',label={"avg = %4.2f" % lightAvg}, color='r')
    plt.fill_between(xticks[0:13],max(rearrangedAvg)+1,alpha=0.5,color='.5') #Adds gray shading to lights off period (08:00 to 20:00)
    plt.ylim([int(min(rearrangedAvg)),int(max(rearrangedAvg))+1])
    plt.legend()
    plt.ylabel('Trials per Hour')
    plt.xlabel('Time of day (24hr clock)')
    plt.title('Reward and Unrewarded trials by Dark and Light Cycles')
    plt.show()

def winStay(data):
    dfEvents = data[(data.Event=='Left') | (data.Event=='Right') | (data.Event=='Pellet')].Event
    rewardedIndex = []
    #Find indicies of pellet retrevial (as indicator of rewarded)
    for i in range(len(dfEvents)):
        if dfEvents.iloc[i] == 'Pellet':
            rewardedIndex.append(i)
    winStay=[]
    for j in rewardedIndex:
        if j+1 == len(dfEvents): #if last event is pellet retreival (i.e. no choice made after)
            break
        winStay.append(dfEvents.iloc[j-1] == dfEvents.iloc[j+1])
    return sum(winStay)/len(winStay)

def loseShift(data):
    dfEvents = data[(data.Event=='Left') | (data.Event=='Right') | (data.Event=='Pellet')].Event
    loseShift = []
    for i in range(len(dfEvents)):
        if i+1 >= len(dfEvents): #if choice is the last (i.e. no choice made after)
            break
        if (dfEvents.iloc[i+1]=='Pellet') | (dfEvents.iloc[i]=='Pellet'): #if the next entry or current entry is rewarded trial (i.e. if this is win) skip
            continue
        else:
            loseShift.append(dfEvents.iloc[i] != dfEvents.iloc[i+1])
    return sum(loseShift)/len(loseShift)

# Calculates median of a list
def median(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2
    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0
    
# example dfs:
# dfs = [dfAll,darkCycle,lightCycle]
def banditOverDays(dfs): # Cumulative reward minus chance. Spits out a graph
    dates = dfAll.index.date.tolist()
    uniqueDates = sorted(list(set(dates)))
    lineStyles = ["ko--","xb-","^r-"]
    lineNames = ["dfAll","darkCycle","lightCycle"]
    plt.axhline(0,color='lightgrey')
    for i in range(len(dfs)):
        df = dfs[i]
        cumulativeRMC = []
        days = pd.DataFrame()
        for d in uniqueDates:
            day = df[df.index.date==d]
            days = pd.concat([days,day])
            cumulativeRMC.append(banditRewardMinusChance(days,csvDir))
        #avgLine = sum(cumulativeRMC)/len(cumulativeRMC)
        #medLine = median(cumulativeRMC)
        plt.plot(uniqueDates,cumulativeRMC,lineStyles[i], label = lineNames[i])
        #plt.plot(uniqueDates, [avgLine] * len(cumulativeRMC), "r--", label={"average = %4.2f" % avgLine})
        #plt.plot(uniqueDates, [medLine] * len(cumulativeRMC), "b--", label={"median = %4.2f" % medLine})
    plt.legend()
    plt.ylabel("(%) reward-chance")
    plt.title('Cumulative reward minus chance')
    plt.show()

######################################################### Return data sets #########################################################

# Returns dataframe of hours where number of choices/trials within that hour is > 2x the average for that hour
def doubleAvgHour(data):
    dfEvents = dfEvents = data[(data.Event=='Left') | (data.Event=='Right')].Event
    eventsPerHour = dfEvents.resample('h').count()
    avgPerHour = eventsPerHour.mean()
    highPokeCount = eventsPerHour[eventsPerHour >= 2 * avgPerHour]
    # Create dataframe that includes datapoints where 
    Info = pd.DataFrame()
    for timestamp in highPokeCount.index:
        Info = pd.concat([Info,data[(data.index.date==timestamp.date()) & (data.index.hour==timestamp.hour)]])
    return Info

# Returns list of bouts of reward defining trials made within 1 minute
# Includes, current trial, if the trial was rewarded or not, and the following trial
# Also prints out WinStay and LoseShift binned by bout
def WinStayLoseShiftBouts(data): 
    # Reorganize the data
    dfChoices = data[(data.Event=='Left') | (data.Event=='Right')] # Reward defining trials
    dfPellet = data[(data.Event=='Pellet')] # All instances of reward
    # Bin by bout where bout = are periods where trials are made under 1 minute
    boutBins, winStayList, loseShiftList = [], [], []
    i = 0
    # Calculate the bouts - goes cohort by cohort
    while i < len(dfChoices)-1:
        bout = []
        while i < len(dfChoices)-1:
            currentdf = dfChoices.index[i]
            nextdf = dfChoices.index[i+1]
            i += 1
            if nextdf - currentdf <= datetime.timedelta(minutes=1):
                bout.append(currentdf)
                bout.append(nextdf)
            else:
                break
        if bout == []: continue
        # Calculate winShift and loseStay per bout
        boutMin, boutMax = min(bout), max(bout)
        boutPellet = dfPellet[(dfPellet.index>=boutMin) & (dfPellet.index<=boutMax)].index.to_list() # Add any event of Pellet if it's within bout
        bout = bout + boutPellet
        dfBout = data.loc[bout].sort_index().drop_duplicates()
        ####### LoseShift and WinStay per bout #######
        boutEvent = dfBout[(dfBout.Event=='Left') | (dfBout.Event=='Right') | (dfBout.Event=='Pellet')].Event
        if boutEvent.iloc[-1] == 'Pellet': boutEvent = boutEvent[:-1] # Drop last entry if it's 'Pellet' event as it's useless in this case and causes issues
        j = 0
        while j < len(boutEvent):
            if j+1 == len(boutEvent): break
            if boutEvent.iloc[j] == 'Pellet': 
                j+=1
            elif boutEvent.iloc[j+1] == 'Pellet': # if current trial rewarded
                winStayList = winStayList + [boutEvent.iloc[j] == boutEvent.iloc[j+2]]
                j+=2
            elif boutEvent.iloc[j+1] in ['Left','Right']:
                loseShiftList = loseShiftList + [boutEvent.iloc[j] == boutEvent.iloc[j+1]]
                j+=1
            else:
                raise Exception("Something went wrong...\ni = " + str(i) + "\nj = " + str(j))
        ##############################################
        boutBins.append(bout)
    winStay = sum(winStayList)/len(winStayList)
    loseShift = sum(loseShiftList)/len(loseShiftList)
    print("WinStay = " + str(winStay))
    print("LoseShift = " + str(loseShift))
    #boutData = pd.concat([dfAll.loc[x] for x in boutBins]).sort_index().drop_duplicates() # This the dataframe of all the bouts ****NOT BINNED****
    return  boutBins #boutBins is a list of bouts where bouts are lists of the Timestamps

##############################################################################################################################################
#                                                          Concat all files                                                                  #
##############################################################################################################################################
csvDir = "R:\\cla_psyc_grissom_labshare\\Projects\\Anika\\data\\FED3\\pyramid\\pyramid2_data\\bandit_data\\30-90_limits"
print(os.listdir(csvDir))

if os.path.exists(csvDir):
    print("✅ Path exists!")
else:
    print("❌ Path does NOT exist. Check your path.")

dfAll, darkCycle, lightCycle = concatDataFrames(csvDir) # This gets you a pandas data frame of all the files included in the csvDir
print(darkCycle.head())


###############################################################
###############################################################

##################### TESTING STUFF BELOW #####################

###############################################################
###############################################################

# Returns which side was the higher probability
# On a scale of -1 is left, 0 is trial, 1 is right
# Returns the average probability of the higher side
# Returns the average difference betwen probability of high-side minus low-side
def banditSideProbability(data,walkDir,walkSize = 500):
    data = data.drop(data[(data.Trial_CounterL>=walkSize) | (data.Trial_CounterR>=walkSize)].index) #Removing rows where Trial Counters are >= 500 cuz we don't need them for this
    allChoices = data[(data.Event=='Left') | (data.Event=='Right')] #All choices (i.e. left or right) -- this excludes any choice made during timeout or when there's a pellet waiting
    highsideList = []
    highProbList = []
    probDiffList = []
    #Get walk values from specific walk files by iterating through the walk files
    for walkFile in allChoices.walkFilename.unique():
        print(walkFile)
        dfWalk = allChoices[allChoices.walkFilename==walkFile]
        walkEvent = dfWalk[(dfWalk.Event=='Left') | (dfWalk.Event=='Right')] #Values only when decision was made (i.e. no pellet events or choice during ITI)
        trialsL = walkEvent['Trial_CounterL'].astype(int).to_list() #All the Trial_CounterL values converted out of pandas format
        trialsR = walkEvent['Trial_CounterR'].astype(int).to_list() #All the Trial_CounterR values converted out of pandas format
        walkValues = pd.read_csv(os.path.join(walkDir,walkFile),header=0)
        walkValuesL = walkValues.leftArm
        walkValuesR = walkValues.rightArm
        #Create list of chances for the trials completed
        for trial in range(len(trialsL)): # trialL and trialR are the same length
            currentTrialLProb = walkValuesL[trialsL[trial]]
            currentTrialRProb = walkValuesR[trialsR[trial]]
            if currentTrialLProb > currentTrialRProb:
                highsideList.append(-1)
            elif currentTrialLProb == currentTrialRProb:
                highsideList.append(0)
            elif currentTrialLProb < currentTrialRProb:
                highsideList.append(1)
            highProbList.append(max(currentTrialLProb, currentTrialRProb))
            probDiffList.append(max(currentTrialLProb, currentTrialRProb)-min(currentTrialLProb, currentTrialRProb))
    highsideProb = sum(highsideList)/len(highsideList)
    highProb = sum(highProbList)/len(highProbList)
    probDiffAvg = sum(probDiffList)/len(probDiffList)
    return highsideProb,highProb,probDiffAvg

# Returns average and median of time between rewarded and unrewarded trials (i.e. excludes)
#########
# NEED TO CHECK IF BREAKS IN DATA CAUSES PROBLEMS
# LIKE WINTER BREAK
#########
def choiceDelta(data):
    dfEvents = data[(data.Event=='Left') | (data.Event=='Right')]
    timeBetweenPokes = []
    for i in range(len(dfEvents.index)):
        if i+1 == len(dfEvents): break
        delta = dfEvents.index[i+1] - dfEvents.index[i]
        if delta < datetime.timedelta(seconds=0): 
            print(dfEvents.index[i])
            raise Exception("Hold up, there's a negative time-delta --> " + str(dfEvents.index[i]))
        ################
        if delta > datetime.timedelta(days=1): continue #Skip entry if the next entry is greater than 1 day (assuming it encapsulates a break)
        ################
        timeBetweenPokes.append(delta)
    #len([i for i in timeBetweenPokes if i > datetime.timedelta(seconds=60)])
    timeSum = datetime.timedelta()
    for j in range(len(timeBetweenPokes)):
        timeSum = timeSum + timeBetweenPokes[j]
    choiceAvg = datetime.timedelta(seconds=int(timeSum.total_seconds()/len(timeBetweenPokes))) #Average seconds between trials
    choiceMedn = median(timeBetweenPokes) #Median seconds between trials
    return choiceAvg, choiceMedn

def graphWalks(csvDir):
    csvFiles = [x for x in os.listdir(csvDir) if ".CSV" in x and "walkLog" in x] # Create a big list that will be concatendated
    csvFiles = sorted(csvFiles, key = lambda x: x.split("_")[1])
    walksDict = {}
    for file in csvFiles:
        date = file.split('_')[2] + "-" + file.split('_')[3][:-4]
        date = datetime.datetime.strptime(date,'%m%d%y-%H%M%S')
        walksDict[date] = pd.read_csv(os.path.join(csvDir,file), header=0)
    for i in range(len(walksDict.keys())):
        print(str(i) + ": " + str(date) + " | (Year-Month-Day Hour:Minute:Seconds)")
    print("Please select date by entering number...")
    num = int(input())
    walk = list(walksDict.keys())[num]
    plt.plot(range(1,501), walksDict[walk].leftArm, "bo-", label='leftArm')
    plt.plot(range(1,501), walksDict[walk].rightArm, "ro-", label='rightArm')
    plt.legend()
    plt.ylabel('Probability (%)')
    plt.xlabel(str(date) + "\n(Year-Month-Day Hour:Minute:Seconds)")
    plt.show()

graphWalks(csvDir)
