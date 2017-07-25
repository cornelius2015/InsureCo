import unittest
import InsureCo
import pandas as pd
from pandas.util.testing import assert_frame_equal
import json


class InsureCoTestCase(unittest.TestCase):
    def setUp(self):
        self.insureCo = InsureCo.InsureCo('contract.json')

    def test_CheckIfDealIsOk(self):
        DealId = '1'
        Company ='WestCoast'
        Peril ='Earthquake'
        Location = 'USA'
        Coverage = [{u'Attribute': u'Location', u'Include': [u'USA', u'Canada']},
                    {u'Attribute': u'Peril', u'Exclude': [u'Tornado']}]
        IsOk = self.insureCo.CheckIfDealIsOk(DealId, Company, Location,Peril,Coverage)
        self.assertEqual(True, IsOk)
        IsNotOk=self.insureCo.CheckIfDealIsOk(DealId, Company, Location,'Tornado',Coverage)
        self.assertEqual(False, IsNotOk)

    def test_GetIncludesOrExcludes(self):
        Coverage = [{u'Attribute': u'Location', u'Include': [u'USA', u'Canada']},
                    {u'Attribute': u'Peril', u'Exclude': [u'Tornado']}]
        LocationIncludes = []
        PerilIncludes=[]

        for element in Coverage:
            if 'Attribute' in element:
                Attribute = element['Attribute']
                LocationIncludes.extend(self.insureCo.GetIncludesOrExcludes(Attribute,'Location',element,'Include'))
                PerilIncludes.extend(self.insureCo.GetIncludesOrExcludes(Attribute, 'Peril', element, 'Exclude'))
        self.assertEqual([u'USA', u'Canada'],LocationIncludes)
        self.assertEqual([u'Tornado'], PerilIncludes)

    def test_CalculateLosses(self):
        MaxAmount, OkDeals = self.insureCo.FindDealsCovered('deals.csv')
        CalculatedLosses=self.insureCo.CalculateLosses(OkDeals, 'losses.csv', MaxAmount)
        #perilsAndLosses=[('Earthquake',  '3500'),('Hurricane'  , '3000')]
        perilsAndLosses = [('Earthquake', 3500), ('Hurricane', 3000)]
        Headers = ['Peril', 'Loss']
        df = pd.DataFrame.from_records(perilsAndLosses, columns=Headers)
        #dfg=df.groupby()
        assert_frame_equal(CalculatedLosses,df)#check_dtype=False,check_frame_type=False)

    def test_FindDealsCovered(self):
        MaxAmount = 3000
        OkDeals = [('1', 'WestCoast', 'Earthquake', 'USA'), ('2', 'WestCoast', 'Hailstone', 'Canada'),
                   ('5', 'GeorgiaInsurance', 'Hurricane', 'USA')]

        self.assertEqual((MaxAmount, OkDeals ),self.insureCo.FindDealsCovered('deals.csv'))





if __name__ == '__main__':
    unittest.main()
