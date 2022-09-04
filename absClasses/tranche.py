"""
Tranche Class
"""
import logging
from loanclasses.loanpool import LoanPool
from loanclasses.loan import Loan
import numpy_financial as npf
from functools import reduce


class Tranche(object): #base tranche class

    def __init__(self,notional,rate,subordinate_flag):
        if type(self) is not Tranche:
            self._notional = notional
            self._rate = rate
            self._subordinate_flag = subordinate_flag
        else: #subordination flag warning
            logging.error('Abstract Base Classes should not be instantiated as a standalone object.')
            raise NotImplementedError()

    @property
    def notional(self):
        return self._notional

    @notional.setter
    def notional(self,inotional):
        self._notional = inotional

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self,irate):
        self._rate = irate

    @property
    def subordinate_flag(self):
        return self._subordinate_flag

    @subordinate_flag.setter
    def subordinate_flag(self,iflag):
        self._subordinate_flag = iflag

class StandardTranche(Tranche):

    def __init__(self,notional,rate, subordinate_flag):
        super(StandardTranche,self).__init__(notional,rate,subordinate_flag)
        self._principalPaid = 0 #total principal paid till current period
        self._cashFlows = [-self.notional] #list of cashflows received by the Tranche in each period
        self._principalPayments = [] #list of principal payments made in each period
        self._current_period = 0
        self._interestShortfall = 0
        self._prevNotional = 0

        self._prin_period_check = [] #to check if payment already made for current period
        self._inter_period_check = []

    def increaseTimePeriod(self): #increases time period of the tranche
        self._prevNotional = self.notionalBalance()
        self._current_period += 1


    def makePrincipalPayment(self,principal_payment): #method to make principal payment to tranche

        if self.notionalBalance() <= 0:
            logging.error('Notional balance is zero.')
            raise Exception()

        if self._current_period not in self._prin_period_check:
            self._principalPaid += principal_payment
            self._cashFlows[-1] += principal_payment
            self._principalPayments.append(principal_payment)
            self._prin_period_check.append(self._current_period)
        else:
            logging.error(f'Principal payment already made for period {self._current_period}')
            raise ValueError()

    def makeInterestPayment(self,interest_payment): #method to make interest payment to tranche

        if self._current_period not in self._inter_period_check:
            if self.interestDue() > 0:
                self._cashFlows.append(interest_payment)
                self._interestShortfall = max(self.interestDue() - interest_payment,0)
            else:
                logging.error('Notional balance is zero, cannot accept interest payment')
            self._inter_period_check.append(self._current_period)
        else:
            logging.error(f'Principal payment already made for period {self._current_period}')
            raise ValueError()


    def interestDue(self): #interest due for the current period
        return (self._prevNotional * Loan.monthlyRate(self._rate)) + self._interestShortfall


    def notionalBalance(self): #remaining notional balance for the current period
        return self._notional - self._principalPaid

    def reset(self): #resets the tranche objects
        self._principalPaid = 0
        self._current_period = 0
        self._principalPayments.clear()
        self._interestShortfall = 0
        self._prevNotional = 0
        self._prin_period_check.clear()
        self._inter_period_check.clear()
        self._cashFlows.clear()

    def IRR(self): #IRR of the tranche (annual rate)
        return (npf.irr(self._cashFlows)*12)

    def DIRR(self): #reduced yield of the tranche (in bps)
        dirr_bps = (self._rate - self.IRR())*10000
        return dirr_bps

    def rating(self): #rating the tranche as per the reduced yield
        ratingTable= {0.06 : 'Aaa',0.67 : 'Aa1',1.3 : 'Aa2',2.7 : 'Aa3',5.2 : 'A1',8.9 : 'A2',13 : 'A3',19 : 'Baa1',27 : 'Baa2',46 : 'Baa3',72 : 'Ba1',106 : 'Ba2',143 : 'Ba3',183 : 'B1',231 : 'B2',311 : 'B3',2500 : 'Caa',10000: 'Ca'}
        dirr_bps = self.DIRR()
        dirr_diff = {(dirr_bps - bps) : bps for bps in ratingTable.keys() if (dirr_bps - bps) >= 0}
        rating = ratingTable.get(dirr_diff.get(min(dirr_diff.keys()))) if len(dirr_diff.items()) > 0 else 'Aaa'
        return rating

    def AL(self): #returns the average life of the tranche
        if self.notionalBalance() > 0: #if tranche principal not fully paid off
            return None
        else:
            averageLife = reduce(lambda total, payment: total + (payment[0]) * payment[1],
                                 enumerate(self._principalPayments,1), 0) / self.notional
            return averageLife







