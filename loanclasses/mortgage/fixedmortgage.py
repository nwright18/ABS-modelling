from ..fixedrateloan import FixedRateLoan
from .mortgagemixin import MortgageMixin

class FixedMortgage(MortgageMixin,FixedRateLoan):
    def __init__(self,notional,rate,startDate,endDate,home):
        super(FixedMortgage,self).__init__(notional,rate,startDate,endDate,home)
