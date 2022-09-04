"""reading data from Loans.csv"""


import logging
from loanclasses.loanpool import LoanPool
from loanclasses.loan import Loan
from loanclasses.autoloan import AutoLoan
from loanclasses.mortgage.fixedmortgage import FixedMortgage,FixedRateLoan
from assetclasses.houses.houses import PrimaryHome
from assetclasses.houses.houses import VacationHome
from assetclasses.cars.cars import Ferrari
from assetclasses.cars.cars import AlfaRomeo
from assetclasses.cars.cars import Mercedes
from assetclasses.cars.cars import Civic
from assetclasses.cars.cars import Lamborghini



def createLoan(loantype,assetname,assetvalue,face,rate,startDate,endDate): #converting loans read from csv to a loan object

    if loantype ==  'House':
        if assetname in ['PrimaryHome', 'VacationHome']:
            home_class = globals()[assetname]
            home_obj = home_class(float(assetvalue)) #creating a house object using a string name of class
            loan = FixedMortgage(float(face),float(rate),startDate,endDate,home_obj)

        else:
            raise TypeError(f'{assetname} entered is not a valid House asset')

    elif loantype == 'Car':

        if assetname in ['Civic', 'Lamborghini', 'Ferrari', 'AlfaRomeo', 'Mercedes']:
            car_class = globals()[assetname]
            car_obj = car_class(float(assetvalue)) #creating a car object using a string name of class
            loan = AutoLoan(float(face),float(rate),startDate,endDate,car_obj)

        else:
            raise TypeError(f'{assetname} entered is not a valid Car asset')

    else:
        raise TypeError(f'{loantype} is not a valid loan type')
    return loan


def readLoans(filePath): #reading data from loans.csv
    loanPool = LoanPool([])
    loanList = []
    path = filePath
    with open(path, 'r') as file:
        for line in list(file.readlines())[1:]:
            loanList.append(line.rstrip(',,,,\n').split(',')[1:])
    for loantype, assetname, face, rate, startDate, endDate, assetvalue in loanList:
        loanPool.loans.append(createLoan(loantype, assetname, assetvalue, face, rate,
                                         Loan.getDate(startDate), Loan.getDate(endDate)))  # Creates a new loan and saves it in a loanpool object
    logging.info('File loaded successfully')
    return loanPool
