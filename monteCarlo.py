"""Functions to perform monte carlo simulations"""

import math
from absClasses.structuredSecurities import doWaterfall
import multiprocessing as MP
import logging
from functools import reduce


def simulateWaterfall(loanpool,structuredSecurity,NSIM): #returns the average dirr and al values after NSIM iterations
    simDIRR = []
    simAL = []
    finalDIRR = []
    finalAL = []
    for sim in range(NSIM):
        _,_,metrics,_ = doWaterfall(loanpool,structuredSecurity)
        simDIRR.append(metrics['DIRR'])
        simAL.append(metrics['AverageLife'])
    return (simDIRR,simAL) #

def runMonte(loanpool,structuredSecurity,tolerance,NSIM): #starts a monte carlo simulation and updates the yield values at each iteration
    maxIter = 10 #max number of iterations of runMonte function for convergence
    count = 1
    dirr,al = 0, 0

    yields = []

    yieldCalc = lambda al, dirr: 0.01*((7/1 + (0.08 * math.exp(-1.9*al/12))) + (0.19*math.sqrt(abs(al*dirr/12))))

    while (count <= maxIter):
        yields.clear()
        print(count)
        count += 1
        dirr, al = runSimulationParallel(loanpool,structuredSecurity,NSIM,20)
        diff = 0
        for index,tranche in enumerate(structuredSecurity._tranches):
            a, d = al[index], dirr[index]
            coeff = 1.2 if tranche._subordinate_flag == 0 else 0.8
            oldTrancheRate = tranche._rate
            newTrancheRate = oldTrancheRate + coeff * (yieldCalc(a,d) - oldTrancheRate)
            tranche._rate = newTrancheRate
            yields.append(newTrancheRate)
            diff += (tranche.notional * abs((oldTrancheRate - newTrancheRate)/oldTrancheRate))/structuredSecurity._totalNotional
        if (diff <= tolerance):
            break
    if count > maxIter:
        logging.warning(f'Failed to converge within maxIter ({maxIter}) iterations')
    else:
        print('Sim completed')
    return (dirr,al,yields)

def doWork(input,output):
    while(True):
        try:
            func, args = input.get(timeout = 1)
            output.put(func(*args))
        except:
            break
    return output

def runSimulationParallel(loanpool,structuredSecurity,NSIM, numProcesses): #performing waterfall calculations using multiprocessing

    res = []
    batchsize = int(NSIM/numProcesses)
    input_queue,output_queue = MP.Queue(), MP.Queue()

    for i in range(numProcesses):
        input_queue.put((simulateWaterfall, (loanpool,structuredSecurity,batchsize)))

    processes = [MP.Process(target = doWork, args = (input_queue,output_queue)) for i in range(numProcesses)]

    for process in processes:
        process.start()


    while(len(res) < NSIM):
        res.append(output_queue.get())

    for process in processes:
        process.terminate()

    dirrList = [dirr for dirr,_ in res]
    alList = [al for _,al in res]

    dirrListUnpacked = [dirr for process in dirrList for dirr in process]
    alListUnpacked = [al for process in alList for al in process]

    finalDIRR = []
    finalAL = []

    for index,_ in enumerate(structuredSecurity._tranches):
        finalDIRR.append(reduce(lambda total, dirr: total + dirr[index],dirrListUnpacked,0)/NSIM)
        finalAL.append(reduce(lambda total, al : total + al[index] if al[index] else total + 0,alListUnpacked,0)/NSIM)

    return (finalDIRR,finalAL)