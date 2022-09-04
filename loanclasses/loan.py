"""Loan Class"""
"""Added checkDefault method"""

import math
import logging
import datetime
from assetclasses.asset import Asset
from functools import wraps
import datetime


class Loan(object):

    def __init__ (self,notional,rate,startDate,endDate,asset):
        if isinstance(asset,Asset):
            self._asset = asset
        else:
            logging.error(('Error : Asset entered is not a valid Asset object'))
            raise TypeError('Error! Expected an Asset Object')
        self._notional = notional
        self._rate = rate
        self._startDate = startDate
        self._endDate = endDate
        self._term = self.getTerm()
        self._default = False


    #getters and setters
    @property
    def notional(self):
        return self._notional

    @notional.setter
    def notional(self,input_notional):
        self._notional = input_notional

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self,input_rate):
        self._rate = input_rate

    @property
    def startDate(self):
        return self._startDate

    @startDate.setter
    def startDate(self,input_date):
        self._startDate = input_date
        self._term = self.getTerm()

    @property
    def endDate(self):
        return self._endDate

    @endDate.setter
    def endDate(self,input_date):
        self._endDate = input_date
        self._term = self.getTerm()

    @property
    def asset(self):
        return self._asset

    @asset.setter
    def asset(self,input_asset):
        if isinstance(input_asset,Asset):
            self._asset = input_asset
        else:
            logging.error(('Error : Asset entered is not a valid Asset object'))
            raise TypeError('Error! Expected an Asset Object')

    @property
    def term(self):
        return self._term

    def getRate(self, period):
        return self._rate

    def getTerm(self):
        term = self._endDate - self._startDate
        return int(term.days/30)


    #Static Methods

    @staticmethod
    def monthlyRate(AnnualRate):
        return (AnnualRate/12)

    @staticmethod
    def annualRate(MonthlyRate):
        return (MonthlyRate*12)

    @staticmethod
    def getDate(date_str):
        return datetime.datetime.strptime(date_str,'%d/%m/%y').date()

    #Class Methods

    @classmethod
    def calcMonthlyPmt(cls,face,rate,term):
        pmt = (cls.monthlyRate(rate) * face) / (1 - (1 + cls.monthlyRate(rate))**(-term))
        logging.debug(f'Monthly payment = {pmt}')
        return pmt

    @classmethod
    def calcBalance(cls,face,rate,term,period):
        if period > term:
            logging.info(f'Period {period} exceeds tenor ({term})')
            return 0
        term1 = face*((1 + cls.monthlyRate(rate)) ** period)
        term2 = (cls.calcMonthlyPmt(face,rate,term) * ((((1 + cls.monthlyRate(rate)) ** period) - 1)) / cls.monthlyRate(rate))
        bal = term1 - term2
        logging.debug(f'Balance for period {period} = {bal}')
        return bal

    #Decorators

    def Memoize(func):
        memoize_dict = {}
        @wraps(func)
        def wrapper(*args):
            result = memoize_dict.get(tuple(args))
            if result:
                return result
            result = func(*args)
            memoize_dict[tuple(args)] = result
            return result
        return wrapper

    #loanclasses Methods

    def monthlyPayments(self, period = None): #monthly loan payments
        pmt = self.calcMonthlyPmt(self.notional,self.getRate(period),self.term)
        return pmt

    def totalPayments(self): #total payments made to maturity
        tot_payments = sum([self.monthlyPayments(period) for period in range(1,self._term+1)])
        logging.debug(f'Total payment = {tot_payments}')
        return tot_payments

    def totalInterest(self): #total interest paid until maturity
        logging.debug(f'Total payment = {self.totalPayments()}')
        totInterest = (self.totalPayments() - self._notional)
        logging.debug(f'Total interest = {totInterest}')
        return totInterest

    def balance(self , period): #remaining balance amount of the loan for a given period
        return self.calcBalance(self.notional,self.getRate(period),self.term, period)


    def interestDue(self,period): #interest to be paid in a given period
        if period > self._term:
            logging.info(f'Period {period} exceeds tenor ({self._term})')
            return 0
        intDue = (self.balance(period - 1)*self.monthlyRate(self.getRate(period)))
        logging.debug(f'Previous balance = {self.balance(period - 1)}')
        logging.debug(f'Monthly rate for period {period} = {self.monthlyRate(self.getRate(period))}')
        logging.debug(f'Interest Due for period {period} = {intDue}')
        return intDue

    def principalDue(self,period): #principal to be paid in a given period
        if period > self._term:
            logging.info(f'Period {period} exceeds tenor ({self._term})')
            return 0
        priDue = (self.monthlyPayments() - self.interestDue(period))
        logging.debug(f'Monthly payment for period {period} = {self.monthlyPayments}')
        logging.debug(f'Interest Due for period {period} = {self.interestDue(period)}')
        logging.debug(f'Principal Due for period {period} = {priDue}')
        return priDue

    @Memoize
    def interestDueRecursive(self,period): #same as interestDue method, but using a recursive structure
        if period > self._term:
            logging.info(f'Period {period} exceeds tenor ({self._term})')
            return 0
        elif period < 2 :
            logging.warning('Warning : Waterfall calculations expected to take longer. Explicit functions recommended')
            return (self.monthlyRate(self.getRate(period)) * self._notional)
        else :
            return self.balance(period - 1) * self.monthlyRate(self.getRate(period))

    @Memoize
    def principalDueRecursive(self,period): #same as principalDue method, but using a recursive structure
        if period > self._term:
            logging.info(f'Period {period} exceeds tenor ({self._term})')
            return 0
        return self.monthlyPayments() - self.interestDueRecursive(period)

    @Memoize
    def balanceRecursive(self,period): #same as balanceDue method, but using a recursive structure
        if period > self._term:
            logging.info(f'Period {period} exceeds tenor ({self._term})')
            return 0
        elif period < 1:
            logging.warning('Warning : Waterfall calculations expected to take longer. Explicit functions recommended')
            return self._notional
        else:
            return self.balanceRecursive(period - 1) - self.principalDue(period)

    def recoveryValue(self,period):
        logging.debug(f'Asset value for period {period} = {self._asset.value(period)}')
        recValue = 0.6 * self._asset.value(period)
        logging.debug(f'Recovery value for period {period} = {recValue}')
        return recValue

    def equity(self,period):
        equity = self._asset.value(period) - self.balance(period)
        logging.debug(f'Asset value for period {period} = {self._asset.value(period)}')
        logging.debug(f'Balance for period {period} = {self.balance(period)}')
        logging.debug(f'Equity for period {period} = {equity}')
        return equity

    def checkDefault(self,defaultCheck,period):
        if self._default is True:
            return 0
        if defaultCheck == True:
            self._default = True
            self._notional = 0
            return self.recoveryValue(period)
        else:
            return 0


#string representations for loanclasses class

    def __str__(self):
        return 'Loan Parameters : Notional = ' + str(self._notional) + ', rate = ' + str(self._rate) + ', term = ' + str(self._term)

    def __repr__(self):
        return self.__str__()

