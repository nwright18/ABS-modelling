"""mortgage Mixin class"""

"""Added exception handling"""

from assetclasses.houses.houses import HouseBase

class MortgageMixin(object):

    def __init__(self,notional,rate,startDate,endDate,home):
        if isinstance(home,HouseBase):
            super(MortgageMixin,self).__init__(notional,rate,startDate,endDate,home)
        else:
            raise TypeError('Error! Expected a House object as asset')

    def PMI(self,period): #checks if LTV > 80% and returns PMI value if True, else PMI = 0
        initialAssetValue = self.asset.initialValue
        currentBalance = self.balance(period)
        if (currentBalance/initialAssetValue) >= 0.8:
            return (0.000075)*initialAssetValue
        else:
            return 0

    def monthlyPayment(self,period):
        monthly_payment = super(MortgageMixin,self).monthlyPayments()
        return monthly_payment + self.PMI(period)

    def principalDue(self,period):
        principal_due = super(MortgageMixin,self).principalDue(period)
        return principal_due - self.PMI(period)