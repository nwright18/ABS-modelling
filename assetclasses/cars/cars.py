"""Car Asset Class"""

from ..asset import Asset

class Car(Asset):

    def __init__(self,initialValue):
        super(Car,self).__init__(initialValue)

class Civic(Car):

    def __init__(self,initialValue):
        super(Civic,self).__init__(initialValue)

    def annualDeprRate(self,period = None):
        return 0.10

class Ferrari(Car):
    def __init__(self,initialValue):
        super(Ferrari,self).__init__(initialValue)

    def annualDeprRate(self,period = None):
        return 0.05


class Lamborghini(Car):
    def __init__(self, initialValue):
        super(Lamborghini, self).__init__(initialValue)

    def annualDeprRate(self,period = None):
        return 0.12


class AlfaRomeo(Car):
    def __init__(self, initialValue):
        super(AlfaRomeo, self).__init__(initialValue)

    def annualDeprRate(self,period = None):
        return 0.25


class Mercedes(Car):
    def __init__(self, initialValue):
        super(Mercedes, self).__init__(initialValue)

    def annualDeprRate(self,period = None):
        return 0.15
