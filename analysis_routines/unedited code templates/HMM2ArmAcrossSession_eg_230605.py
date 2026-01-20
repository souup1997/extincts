"""
This code fit an HMM model to choice sequences (2-armed restless bandit) across sessions. One transition matrix is being optimized across all sessions. The HMM model is 1. parameter-tied 2. reseeded (random initial T matrix) 3. fixed emission matrix, 5. fixed initial distribution. 6. optimization based by observed log likelihood and side criteria is Tmatrix[0,0] and [1,1]> 0.5. This code is created by Cathy Chen. Date 01/2021.

Code has been modified slightly by Madison and Erin (07/2022) to retain animal identities and names throughout the analyses.
The lines that need to be edited for each cohort of animals are 14-16.

Note for Dana (12/20/22): because I'm running this for you, I ran a quick find-and-replace for my scratch folder from yours. Change it back when you can run on your own! 
"""
import numpy as np
import pandas as pd
import os
from datetime import datetime

#manually changing variables
folder = "/scratch.global/muel0720/ephys/bandit_processed/"
destinationFolder = "/scratch.global/muel0720/ephys/HMM_output/"

sessionList = os.listdir(folder)
nSessions = len(sessionList) #how many sessions down do you want to run these analyses? We are now assuming ALL OF THEM
#sessionList = ['bandit' + str(x) + '_processed' for x in range(1,nSessions+1)] #list comprehension right here!

missingDict = {'animalID' : []}

set1 = set([x.split('.')[0] for x in os.listdir(os.path.join(folder,'bandit01_processed'))])
bigSet = set1

for i in range(1,nSessions+1):
    if i < 10:
        thisSet = set([x.split('.')[0] for x in os.listdir(os.path.join(folder,'bandit0' + str(i) + '_processed'))])
    else:
        thisSet = set([x.split('.')[0] for x in os.listdir(os.path.join(folder,'bandit' + str(i) + '_processed'))])
    bigSet = thisSet | bigSet #this means "the big set equals any value in EITHER set". so if session1 has {anakin,bantha,organa} and session2 has {anakin,bantha,quigon}, bigSet should be {anakin,bantha,organa,quigon}. basically here I'm pausing to make sure I have EVERY. SINGLE. POSSIBLE. MOUSE. in my biggest set so I can't miss any if some get added only later in the sequence. 

#defining list of animals in the dataset 
animalList = list(bigSet) #you need to cull animalList here if you want to exclude some mice 
animalList.sort()

"""
Subroutines to be called elsewhere
"""
def forward (V, a, b, initial_distribution):
    alpha = np.zeros((V.shape[0],a.shape[0]))
    alpha[0, :] = initial_distribution * b[:, V[0]]
    for t in range(1, V.shape[0]):
        for j in range(a.shape[0]):
            alpha[t, j] = alpha[t - 1].dot(a[:, j]) * b[j, V[t]]
    return alpha

def backward (V, a, b):
    beta = np.zeros((V.shape[0], a.shape[0]))
    # setting beta(T) = 1
    beta[V.shape[0] - 1] = np.ones((a.shape[0]))
    # Loop in backward way from T-1 to
    # Due to python indexing the actual loop will be T-2 to 0
    for t in range(V.shape[0] - 2, -1, -1):
        for j in range(a.shape[0]):
            beta[t, j] = (beta[t + 1] * b[:, V[t + 1]]).dot(a[j, :])
    return beta

def baum_welch(V, a, b, initial_distribution, n_iter=100):
    M = a.shape[0]
    T = len(V)
    for n in range(n_iter):
        alpha = forward(V, a, b, initial_distribution)
        #print (alpha)
        beta = backward(V, a, b)
        xi = np.zeros((M, M, T - 1))
        for t in range(T - 1):
            denominator = np.dot(np.dot(alpha[t, :].T, a) * b[:, V[t + 1]].T, beta[t + 1, :])
            for i in range(M):
                numerator = alpha[t, i] * a[i, :] * b[:, V[t + 1]].T * beta[t + 1, :].T
                xi[i, :, t] = numerator / denominator
        ### xi is 3x3x299
        ## gamma is a 3x300 matrix
        gamma = np.sum(xi, axis=1)
        ## tmp is transition matrix (a) in log likelihood form
        #### parameter tying
        tmp = np.sum(xi,2)
        # Add additional T'th element in gamma
        #gamma = np.hstack((gamma, np.sum(xi[:, :, T - 2], axis=0).reshape((-1, 1))))
        #K = b.shape[1]
        #denominator = np.sum(gamma, axis=1)
        #for l in range(K):
         #   b[:, l] = np.sum(gamma[:, V == l], axis=1)
        #b = np.divide(b, denominator.reshape((-1, 1)))
        ### fix b, b stays the same
        #b = np.array([[1/2,1/2],[1,0],[0,1]])
    return tmp

#parameter tying averages the ore to oitL and oitR in the 3x3 matrix, and line 85 also divides by the number of trials to get a transition matrix that is probabilistic (rather than numbers of trials, which is what baum welch is doing)
def parameterTying(tmp):
    tmp[0,1] = (tmp[0,1] + tmp[0,2])/2
    tmp[0,2] = tmp[0,1]
    tmp[1,1] = (tmp[1,1]+tmp[2,2])/2
    tmp[2,2] = tmp[1,1]
    tmp[1,0] = (tmp[1,0]+tmp[2,0])/2
    tmp[2,0] = tmp[1,0]
    a = tmp/np.sum(tmp,1).reshape((-1, 1))
    return a

def optimizeLog (V, a, b, initial_distribution):
    T = V.shape[0] ## 300 - time.trial
    M = a.shape[0] ## number of states - 3
    ## p (state)
    omega = np.zeros((T, M))
    omega[0, :] = (initial_distribution) #inital state distribution
    for i in range (1,T):
        for j in range (0,M):
            omega[i,j] = np.dot((a[:,j]),(omega[(i-1)]))
    #print (omega)
    ## p (choice) =sum( p(choice|state) *p(state))
    probList = []
    for k in range (0,T):
        pchoice = np.dot(b[:,V[k]],omega[k])
        probList.append(pchoice)
    logLike = (np.sum(np.log(probList)))*(-1)
    ### this is the observed log likelihood
    return logLike

def viterbi(V, a, b, initial_distribution):
    T = V.shape[0] ## 300 - time.trial
    M = a.shape[0] ## number of states - 3
    omega = np.zeros((T, M))
    #omega[0, :] = np.log(initial_distribution * b[:, V[0]]) # prior
    omega[0, :] = (initial_distribution * b[:, V[0]]) # prior
    prev = np.zeros((T - 1, M))
    for t in range(1, T):
        for j in range(M):
            # Same as Forward Probability
            probability = omega[t - 1] + np.log(a[:, j]) + np.log(b[j, V[t]])
            # This is our most probable state given previous state at time t (1)
            prev[t - 1, j] = np.argmax(probability)
            # This is the probability of the most probable state (2)
            omega[t, j] = np.max(probability)
    ## shape of omega is 300x3
    # Path Array
    S = np.zeros(T)
    # Find the most probable last hidden state
    last_state = np.argmax(omega[T - 1, :])
    S[0] = last_state
    backtrack_index = 1
    for i in range(T - 2, -1, -1):
        S[backtrack_index] = prev[i, int(last_state)]
        last_state = prev[i, int(last_state)]
        backtrack_index += 1
    # Flip the path array since we were backtracking
    result = np.flip(S, axis=0)
    return result

def optimTM(folder,nSessions,animalList):
    reseed = 10 #you're trying to find the optimal values for the transition matrix, so this is telling you how many times the model pauses and looks around to see what the best version it can get is. 
    optimAList = []
    #optimAList = [[0]]
    for mouse in animalList: ###animal ID
        print(mouse)
        count = 1
        while count <= reseed:
            count +=1
            obsLogList = []
            matrixAList = []
            for h in range(reseed):
                acrossSessTmp = np.array([[0,0,0],[0,0,0],[0,0,0]])
                #### randomly reseed transition matrix A
                rand1 = np.random.random()
                rand2 = np.random.random()
                a = np.array([[(1-rand1),rand1/2,rand1/2],[1-rand2,rand2,0],[1-rand2,0,rand2]])
                ## emission probs (p(choice|state)), fixed
                matrixB = np.array([[1/2,1/2],[1,0],[0,1]])
                initial_distribution = np.array((1,0,0))
                for sessionNum in range(1,nSessions+1):  ### session
                    ##### retrieve choice sequence data
                    if sessionNum < 10:
                        thisDir = os.path.join(folder, 'bandit0' + str(sessionNum)+"_processed")
                    else:
                        thisDir = os.path.join(folder, 'bandit' + str(sessionNum)+"_processed")
                    sessionFiles = os.listdir(thisDir)
                    try:
                        fileName = [i for i in sessionFiles if mouse in i][0]
                        df = pd.read_csv(os.path.join(thisDir,fileName), skiprows = 0)
                        choice = df['choice_chosen'].tolist()
                        newChoice = np.asarray([int(choice[i]) -1 for i in range(len(choice))]) #choice chosen comes out as 1 and 2, code needs it to be new list of 0s and 1s instead
                        ### fit baum welch algorithm
                        hmm=baum_welch(newChoice,a,matrixB,initial_distribution, n_iter =100)
                        ### add up log likelihood T matric across session
                        for col in range (0,3):
                            for row in range (0,3):
                                acrossSessTmp[col][row] += hmm[col][row]
                    except:
                        print(sessionNum)
                        print(mouse)
                        print(count)
                ### parameter tying
                matrixA = parameterTying(acrossSessTmp)
                matrixAList.append(matrixA)
                ### calculate observed log likelihood for that matrix A
                obsLog = optimizeLog(newChoice, matrixA, matrixB, initial_distribution)
                obsLogList.append(obsLog)
            optimA = matrixAList[obsLogList.index(min(obsLogList))]
            print(optimA)
            if count >= 10 or optimA[1,1] > 0.5 and optimA[0,0] > 0.5:
                optimAList.append(optimA)
                break
            ### find the optimA across all the reseeding
    print('optimized matrix A is %s' % optimAList)
    print(optimAList)
    return(optimAList)

"""
n.b. Erin: this is where Cathy's code initially started initializing its "main" distribution. Instead of inputting our folders at the start, we're going to spell out the paths
"""
#Let's see. How many sessions are there? How many animals? Let's write a routine to check the input folder for all the days that can be session folders.
#### get optimized transition matrix A for each animal
optimAList = optimTM(folder,nSessions,animalList)

transitionMatrixA = []
transitionMatrixB = []

if len(animalList) != len(optimAList):
    error("lengths of animal list and optimAlist do not agree")

for i in range(len(optimAList)): #for all the mice in the optimAList
    transitionMatrixA.append(optimAList[i][0,0])
    transitionMatrixB.append(optimAList[i][1,1])

# now we put the state labels on the mouses actual choices
for mouse in animalList: ###animal ID
    for sessionNum in range(1,nSessions+1):  ### session
        if sessionNum < 10:
            sessionName = 'bandit0' + str(sessionNum)+"_processed"
            numName = '0' + str(sessionNum) #for naming down there to make everything tidy--see line 56
        else:
            sessionName = 'bandit' + str(sessionNum)+"_processed"
            numName = str(sessionNum)
        in_sessDir = os.path.join(folder, sessionName) #defining inputs and outputs 
        out_sessDir = os.path.join(destinationFolder, sessionName)
        if os.path.isdir(out_sessDir) == False:
            os.makedirs(out_sessDir)
        ##### retrieve choice sequence data
        sessionFiles = os.listdir(in_sessDir)
        try:
            fileName = [i for i in sessionFiles if mouse in i][0]
            df = pd.read_csv(os.path.join(in_sessDir, fileName), skiprows=0)
            choice1 = df['choice_chosen'].tolist()
            # choice chosen comes out as 1 and 2, code needs it to be 0 and 1 instead
            newChoice1 = np.asarray([int(choice1[i]) - 1 for i in range(len(choice1))])
            ### initialize fixed matrix B and initial dist
            matrixB = np.array([[1/2, 1/2], [1, 0], [0, 1]])
            initial_distribution2 = np.array((1, 0, 0))
            ### label each trial using viterbi algorithm
            #stateLabel = viterbi(newChoice1,optimAList[p-1],matrixB,initial_distribution2)
            stateLabel = viterbi(newChoice1, optimAList[0], matrixB, initial_distribution2)
            labelList = stateLabel.tolist()
            df['state'] = labelList
            #Dict = {'state': labelList}
            #df = pd.DataFrame(Dict)
            outName = os.path.join(out_sessDir, mouse+'_session' + numName + "_withStates.csv")
            print(outName)
            df.to_csv(outName, index=False)
        except:
            print(mouse)
            print(sessionNum)

Dict2 = {'transition matrix [0,0]': transitionMatrixA, 'transition matrix [1,1]': transitionMatrixB }
df2 = pd.DataFrame(Dict2)
df2['mouseID'] = animalList
df2.to_csv(os.path.join(destinationFolder,'transition_matrix_' + datetime.now().strftime("%m-%d-%Y") + '.csv'),index=False)
