"""Variable Rate loanclasses Class"""
"""Added exception handling"""

from .loan import Loan
import logging


class VariableRateLoan(Loan):
    def __init__(self,notional,rateDict,startDate,endDate,asset):
        if isinstance(rateDict,dict):
            super(VariableRateLoan,self).__init__(notional,rateDict,startDate,endDate,asset)
        else:
            raise TypeError('Error! Expected a rate dictionary')


    def getRate(self,period):
        period_diff = {(period - startPeriod) : startPeriod for startPeriod in self._rate.keys() if (period - startPeriod) >= 0}
        return self._rate[period_diff[min(period_diff.keys())]]

