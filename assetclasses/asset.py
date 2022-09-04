"""Asset Class"""

import logging

class Asset(object):

    def __init__(self, initialValue):
        self._initialValue = initialValue

    @property
    def initialValue(self):
        return self._initialValue

    @initialValue.setter
    def initialValue(self,input_initialValue):
        self._initialValue = input_initialValue

    def annualDeprRate(self,period = None): #returns a static annualized depreciation value
        raise NotImplementedError()

    def monthlyDeprRate(self,period = None):
        return self.annualDeprRate(period)/12

    def value(self,period): #returns the value of the asset after the number of periods entered
        currentValue = self._initialValue * ((1 - self.monthlyDeprRate()) ** period)
        if currentValue >= 0:
            return currentValue
        else:
            return 0


    #string representations

    def __str__(self):
        return 'Initial Value = ' + str(self._initialValue) + ', annual depreciation = ' + str(self.annualDeprRate())

    def __repr__(self):
        return 'Initial Value = ' + str(self._initialValue) + ', annual depreciation = ' + str(self.annualDeprRate())
