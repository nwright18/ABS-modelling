"""Fixed Rate Loan Class"""

from .loan import Loan

class FixedRateLoan(Loan):

    def __init__(self, notional, rate,startDate,endDate,asset):
        super(FixedRateLoan,self).__init__(notional,rate,startDate,endDate,asset)