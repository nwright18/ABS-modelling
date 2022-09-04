"""Auto Loan CLass"""
"""Added exception handling"""


from .fixedrateloan import FixedRateLoan
from assetclasses.cars.cars import Car
import logging

class AutoLoan(FixedRateLoan):

    def __init__(self,notional,rate,startDate,endDate,asset):
        if isinstance(asset,Car):
            super(AutoLoan,self).__init__(notional,rate,startDate,endDate,asset)
        else:
            raise TypeError('Error! Expected a Car object')

