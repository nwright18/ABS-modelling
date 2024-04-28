"""Loan Pool Class"""
"""added getWaterfall and checkDefaults methods"""


import copy
import random
from functools import reduce

class LoanPool(object):

    def __init__(self, loans):
        self._loans = copy.copy(list(loans))

    @property
    def loans(self):
        return self._loans

    @loans.setter
    def loans(self,loansList):
        self._loans = copy.copy(list(loansList))

    def totalPrinicipal(self):
        principal = reduce(lambda total, loan: total + loan.notional, self._loans,0)
        return principal

    def totalInterest(self):
        totalInterest = reduce(lambda total, loan: total + loan.totalInterest(),self._loans,0)
        return totalInterest

    def totalPayments(self):
        totalPayments = reduce(lambda total, loan:total + loan.totalPayments(),self._loans,0)
        return totalPayments

    def balance(self,period):
        poolBalance = reduce(lambda total, loan: total + loan.balance(period), self._loans,0)
        return poolBalance

    def principalDue(self,period):
        amount = reduce(lambda total, loan: total + loan.principalDue(period), self._loans,0)
        return amount

    def interestDue(self,period):
        totalInterest = reduce(lambda total, loan: total + loan.interestDue(period), self._loans,0)
        return totalInterest

    def paymentDue(self,period):
        return (self.principalDue(period) + self.interestDue(period))

    def activeLoanCount(self,period):
        counter = sum([1 for loan in self._loans if loan.balance(period) > 0])
        return counter

    def WAM(self):
        weightedMaturity = reduce(lambda total, loan: total + (loan.notional * loan.term),self._loans,0)
        return (weightedMaturity/self.totalPrinicipal())

    def WAR(self):
        weightedRate = reduce(lambda total, loan: total + (loan.notional * loan.rate), self._loans,0)
        return(weightedRate/self.totalPrinicipal())

    def getWaterfall(self):
        paymentDetails = []
        period = 0
        while(self.activeLoanCount(period) > 0):
            period += 1
            paymentDetails.append([self.paymentDue(period),self.interestDue(period),self.principalDue(period)])
        return paymentDetails

    def checkDefaults(self,period):
        recValues = []
        seedIndex = -1
        periods = [list(range(1,11)), list(range(11,60)), list(range(60,121)), list(range(121,181)), list(range(181,211)), list(range(211,360))]

        for index,timePeriod in enumerate(periods):
            if period in timePeriod:
                seedIndex = index
                break

        defaultProbabilities ={
            0 : random.choice([True if i < 5 else False for i in range(10000)]),
            1 : random.choice([True if i < 1 else False for i in range(1000)]),
            2 : random.choice([True if i < 2 else False for i in range(1000)]),
            3 : random.choice([True if i < 4 else False for i in range(1000)]),
            4 : random.choice([True if i < 2 else False for i in range(1000)]),
            5 : random.choice([True if i < 1 else False for i in range(1000)])
        }
        seed = defaultProbabilities.get(seedIndex,False)
        for loan in self._loans:
            if loan._default:
                continue
            else:
                recValues.append(loan.checkDefault(seed,period))
        return reduce(lambda total, recovery : total + recovery,recValues,0)







