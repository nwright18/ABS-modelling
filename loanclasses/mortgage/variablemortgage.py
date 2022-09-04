"""Variable mortgage Class"""

from .mortgagemixin import MortgageMixin
from ..variablerateloan import VariableRateLoan

class VariableMortgage(MortgageMixin,VariableRateLoan):

    def __init__(self,notional,rateDict,startDate,endDate,home):
        super(VariableMortgage,self).__init__(notional,rateDict,startDate,endDate,home)