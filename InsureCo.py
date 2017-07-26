import json
import csv
import linecache
import sys
import numpy as np
import pandas as pd


class InsureCo:
    '''
    Constructor for the InsureCo Class. This method takes a
    '''
    def __init__(self,Contract):
        try:
            with open(Contract) as data_file:
                self.data = json.load(data_file)
        except IOError as e:
            self.PrintException()
    '''Function to check if deal satisfies the contract i.e if the deal is covered under the insurance policy'''
    def CheckIfDealIsOk(self,DealId="",Company="",Location="",Peril="",Coverage=[]):
        LocationIncludes=[]
        LocationExcludes = []
        PerilExcludes=[]
        PerilIncludes=[]
        for element in Coverage:
            if 'Attribute' in element:
                Attribute = element['Attribute']
                LocationIncludes.extend(self.GetIncludesOrExcludes(Attribute,'Location', element,'Include'))
                #LocationExcludes.extend(GetIncludesOrExcludes(Attribute, 'Location', element, 'Exclude'))
                PerilExcludes.extend(self.GetIncludesOrExcludes(Attribute, 'Peril', element, 'Exclude'))
                #PerilIncludes.extend(GetIncludesOrExcludes(Attribute, 'Peril', element, 'Include'))
        if (Location in LocationIncludes) and (Peril not in PerilExcludes):
            return True
        else:
            return False
            #return DealId, Company, Peril, Location

    '''Find out what attribute is be included or excluded'''
    def GetIncludesOrExcludes(self,Attribute,AttributeName, element,IncludeOrExclude):
        IncludesOrExcludes=""
        if (Attribute == AttributeName):
            if IncludeOrExclude in element:
                IncludesOrExcludes = element[IncludeOrExclude]
        return IncludesOrExcludes
    '''Gives a summary of the losses grouped by Perils'''
    def CalculateLosses(self,OkDeals,LossFileName,MaxAmount):
        perilsAndLosses=[]
        try:
            with open(LossFileName) as LossesFile:
                Losses = csv.reader(LossesFile)
                next(Losses,None)
                for row in Losses:
                    LossEventId = row[0]
                    LossDealId = row[1]
                    LossAmount = int(row[2])
                    if LossAmount > MaxAmount:
                        LossAmount = MaxAmount
                    for deal in OkDeals:
                        if deal[0]==LossDealId:
                            perilsAndLosses.append((deal[2],LossAmount))
        except IOError as e:
            self.PrintException()

        Headers=['Peril','Loss']
        dataFrame = pd.DataFrame.from_records(perilsAndLosses,columns=Headers)
        dataFrameGroupedBy=dataFrame.groupby(['Peril'],as_index=False).sum()
        return dataFrameGroupedBy


    def FindDealsCovered(self,DealsFileName):
        Coverage = self.data['Coverage']
        MaxAmount = self.data['MaxAmount']
        OkDeals = []
        try:
            with open(DealsFileName) as dealsFile:
                deals = csv.reader(dealsFile)
                next(deals, None)
                for row in deals:
                    DealId = row[0]
                    Company = row[1]
                    Peril = row[2]
                    Location = row[3]
                    if (self.CheckIfDealIsOk(DealId, Company, Location, Peril, Coverage)==True):
                        OkDeals.append((DealId, Company, Peril, Location))

        except IOError as e:
            self.PrintException()

        return MaxAmount,OkDeals

    def PrintException(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print 'Exception In ({}, Line {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

if __name__ == '__main__':

    insureCo = InsureCo('contract.json')
    print "Deals Covered:\n"
    MaxAmount, OkDeals=insureCo.FindDealsCovered('deals.csv')
    print  "DealId     Company       Peril    Location"
    for deal in OkDeals:
        print deal[0] + '        ' + deal[1] + '     ' + deal[2] + '     ' + deal[3]
    print '\n\nLoss Summary:\n'
    print insureCo.CalculateLosses(OkDeals, 'losses.csv', MaxAmount)

'''
 3. Discuss how your solution will scale. How does the performance of your
solution vary with the size of the problem? Could you have used a different
algorithm to get better performance for large input files?

Answer:
Regarding how the solution will scale, the only upper bounds on the input and output of the data depends on the memory
of the computer as there are no other restrictions.
The Time Complexity for finding which deal is covered is O(M*N) i.e looping through the deals and for each deal looping
through the coverage conditions as can be seen  from functions "FindDealsCovered" and "CheckIfDealIsOk".
The Time Complexity for the Calculate Losses function is also O(m*n) i.e a nested loop. As the Losses.csv file and deals.csv
files the solution takes longer to excute because of the greater number of deals and losses to work with.
There are a number of ways that one could improve the performance in order to check which deal is covered:

1) Introduce Multithreading programming where one would test if a group of deals satisfied the conditions for coverage
and in parallel with that thread another group of deals would be tested for the conditions being satisfied and so forth.
So if you had 4 thereads running the task would be completed 4 times faster. We can do something similar for the CalculateLosses function.

2)Another way to increase the performance is to store all the data from the  deals.csv in a database table and index
the relevant columns, we can then do a query to find the relevant deals i.e "Select DealId, Company, Peril, Location from Deals
where Location in ('USA','Canada') and Peril != 'Tornando'".
For the Losses problem we would load the data from the Losses.csv file index the relevant columns to improve perfromance
and execute a query something like the follwoing: "Select Peril, Sum(Loss) Case Loss > MaxAmount Then MaxAmount End from Losses join
Deals on Losses.DealId=Deals.DealId where Deals.Location in ('USA','Canada') and Deals.Peril != 'Tornando' Group By Peril"

3) Another way to improve performance would be to unroll the loops  for the Deals and the losses functions.
4) Another way to improve performance would be to do the program in C++.
5) If we were using numerical calculations e.g matrix multiplications or Monte Carlo Simulations etc. then we would use numpy
and take advantage of SIMD (Single Instruction Multiple Data) which would greatly improve performance.

'''

