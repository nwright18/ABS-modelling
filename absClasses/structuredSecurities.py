"""
Structured Securities Class
"""
import logging

from absClasses.tranche import StandardTranche

class StructuredSecurities(object):

    def __init__(self, total_notional, mode = 0):
        self._totalNotional = total_notional
        self._pshortfall = {}
        self._tranches =[]
        self._reserve = 0
        self._period = 0
        self._waterfallPayments =[]
        self._paymentDetails = {}
        if mode in (0,1):
            self._mode = mode #0 for sequential, 1 for pro rate
        else:
            logging.exception(f'{mode} is not a valid mode. Please select 0 for sequential or 1 for pro rate payment modes.')
            raise ValueError()

    @property
    def total_notional(self):
        return self._totalNotional

    @total_notional.setter
    def total_notional(self,inotional):
        self._totalNotional = inotional

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self,imode):
        if imode in (0, 1):
            self._mode = imode  # 0 for sequential, 1 for pro rate
        else:
            logging.exception(
                f'{imode} is not a valid mode. Please select 0 for sequential or 1 for pro rate payment modes.')
            raise ValueError()

    def addTranche(self, notionalPercent, rate, subordinate_flag): #adds a tranche
        tranche = StandardTranche(notionalPercent * self._totalNotional,rate,subordinate_flag)
        self._tranches.append(tranche)

    def increaseTimePeriod(self): #increases the time period of all tranches in the security by 1
        if self._period > 0:
            self._paymentDetails[self._period] = self._waterfallPayments[:]
        self._waterfallPayments.clear()
        self._period += 1

        for tranche in self._tranches:
            tranche.increaseTimePeriod()

    def makePayments(self, cashAmount, principalAmount): #make payments to the tranches in each period
        flaggedTranches = sorted(self._tranches, key = lambda tranche: tranche._subordinate_flag) #sorting the tranches as per seniority using subordinate_flag
        availableFunds = cashAmount + self._reserve

        for tranche in flaggedTranches: #making interest payments first
            interestDue = tranche.interestDue()
            interest_payment = min(availableFunds, interestDue)
            if interestDue > 0:
                tranche.makeInterestPayment(interest_payment)
                availableFunds = max(availableFunds - interest_payment,0)
            self._waterfallPayments.append([interestDue, interest_payment, tranche._interestShortfall])


        remainingPrincipalAmount = min(max(availableFunds,0),principalAmount) #amount remaining after interest has been paid
        for index,tranche in enumerate(flaggedTranches):
            fraction = (tranche.notional / self._totalNotional)
            principalDue = (min(remainingPrincipalAmount + self._pshortfall.get(index,0), tranche.notionalBalance()) if self._mode == 0 else min((principalAmount * fraction) + self._pshortfall.get(index,0), tranche.notionalBalance()))
            principalPayment = min(principalDue,availableFunds)
            if principalDue > 0:
                tranche.makePrincipalPayment(principalPayment)
                self._pshortfall[index] = max((principalDue - principalPayment),0)
                remainingPrincipalAmount = max(remainingPrincipalAmount - principalPayment,0)
                availableFunds = max(availableFunds - principalPayment,0)
            self._waterfallPayments[index].extend([principalDue,principalPayment, tranche.notionalBalance()])

        self._reserve = max(availableFunds,0)
        self._waterfallPayments.append(self._reserve)

    def getWaterfall(self): #retuns the payment details after all the waterfall payments are completed
        return self._paymentDetails

def doWaterfall(loanpool, structuredSecurity):
    period = 0
    recValues = []
    while(loanpool.activeLoanCount(period) > 0):
        period += 1
        defaults = loanpool.checkDefaults((period))
        structuredSecurity.increaseTimePeriod()
        total_payment = loanpool.paymentDue(period) + defaults
        principal_payment = loanpool.principalDue(period) + defaults
        structuredSecurity.makePayments(total_payment,principal_payment)
        recValues.append(defaults)
        #add cpr to this code (potentially)

    loanPayments = loanpool.getWaterfall()
    ABSPayments = structuredSecurity.getWaterfall()
    metrics = {'IRR' : [], 'DIRR' : [], 'AverageLife' : [], 'Rating' : []}
    for tranche in structuredSecurity._tranches:
        metrics['IRR'].append(tranche.IRR())
        metrics['DIRR'].append(tranche.DIRR())
        metrics['AverageLife'].append(tranche.AL())
        metrics['Rating'].append(tranche.rating())

    return (loanPayments,ABSPayments,metrics,recValues)

def writeToCSV(loanPayments, ABSPayments):
    with open('ABSPayments.csv','w+') as file:
        file.write('Period,interestDue A,interestPaid A,interestShortfall A,principalDueA,principalPaid A,notionalBalance A,interestDue B,interestPaid B,interestShortfall B,principalDueB,principalPaid B,notionalBalance B,Reserve\n')
        for period,tranchePayments in ABSPayments.items():
            file.write(f'{period},')
            for interestDue, interestPaid, interestShortfall, principalDue,principalPaid, notionalBalance in tranchePayments[:2]:
                file.write(f'{interestDue},{interestPaid},{interestShortfall},{principalDue},{principalPaid},{notionalBalance},')
            file.write(f'{tranchePayments[-1]}\n')

    with open('loanPayments.csv', 'w+') as file:
        file.write('Period,TotalPayments,InterestPayments,PrincipalPayments\n')
        for period,(totalPayments, totalInterests, principalPayments) in enumerate(loanPayments):
            file.write(f'{period + 1},{totalPayments},{totalInterests},{principalPayments}\n')

    logging.info('Export to CSV successful')



