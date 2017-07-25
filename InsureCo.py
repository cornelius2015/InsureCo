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


    def GetIncludesOrExcludes(self,Attribute,AttributeName, element,IncludeOrExclude):
        IncludesOrExcludes=""
        if (Attribute == AttributeName):
            if IncludeOrExclude in element:
                IncludesOrExcludes = element[IncludeOrExclude]
        return IncludesOrExcludes

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

