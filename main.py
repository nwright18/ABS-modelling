"""
Case Study
"""

from absClasses.structuredSecurities import StructuredSecurities,writeToCSV,doWaterfall
from monteCarlo import runMonte
from monteCarlo import simulateWaterfall
import getdata
import logging

def main():
    logging.disable(logging.INFO)

    loanPool = getdata.readLoans('C:\\Users\\user\\Desktop\\Quantnet Python\\Homework\\Level 7\\Case Study\\Loans.csv')

    structSec = StructuredSecurities(loanPool.totalPrinicipal(),0)
    structSec.addTranche(0.80,0.05,0)
    structSec.addTranche(0.20,0.08,1)

###Testing doWaterfall functions

    #loanPayments, ABSPayments,metrics,recValues = doWaterfall(loanPool, structSec)

    #writeToCSV(loanPayments, ABSPayments)
    #print(metrics)
    #print(recValues)

###simulate waterfall function

    #dirr, al = simulateWaterfall(loanPool, structSec,5)
    #print(f'{dirr} {al}')


    #For some rates, the notional for all tranches does not get paid down to 0.
    #There were also instances where the tranches get paid to 0 earlier than the final terms of the loanpool, and there is a non zero balance in the reserve account at the maturitty


    simDIRR, simAL, finalyields = runMonte(loanPool,structSec,0.005,20)


    print('ABS metrics')
    for index,tranche in enumerate(structSec._tranches):
        seniority = 'Senior' if tranche._subordinate_flag == 0 else 'Equity'
        print(f'{seniority} Tranche')
        print(f'Reduction in yield : {simDIRR[index]} bps')
        print(f'Average Life : {simAL[index]} periods')
        print(f'Yield calculated using Monte Carlo Sims : {finalyields[index]}')
        print(f'Tranche rating : {tranche.rating()}')
        print(f'Tranche rate : {tranche._rate}')

if __name__ == '__main__':
    main()
