from ..asset import Asset

class HouseBase(Asset):

    def __init__(self,initialValue):
        super(HouseBase,self).__init__(initialValue)


class PrimaryHome(HouseBase):

    def __init__(self,initialValue):
        super(PrimaryHome,self).__init__(initialValue)

    def annualDeprRate(self,period = None):
        return 0.05

class VacationHome(HouseBase):

    def __init__(self,initialValue):
        super(VacationHome,self).__init__(initialValue)

    def annualDeprRate(self,period = None):
        return 0.025