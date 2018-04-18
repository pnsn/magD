import unittest
import sys
import os
sys.path.append(os.path.abspath('..'))
# from MagD.core import parse_json_file
import magD.iris as iris
from magD.scnl import Scnl

from pprint import pprint
# import numpy as np
# import json



class TestIris(unittest.TestCase):
    
    def test_get_available_channels(self):
        sta_string="UMAT"
        chan_string="HHZ,BHZ"
        net_string="UW,UO,CC,NC"
        resp=iris.get_fdsn(sta_string,chan_string,net_string)
        scnls=resp['data']
        self.assertTrue(resp['code']==200)

        print(scnls)
        self.assertTrue(scnls[0][0]=="UMAT")
        self.assertTrue(scnls[0][1]=="HHZ")
        self.assertTrue(scnls[0][2]=="UW")
        self.assertTrue(float(scnls[0][5])==45.2904)
        self.assertTrue(float(scnls[0][6])==-118.9595)


    def test_get_noise_pdf(self):
        scnl=Scnl("BABR","BHZ","UW")
        resp=iris.get_noise_pdf(scnl, "2017-01-01", "2017-02-01")
        self.assertTrue(resp['code']==200)
        self.assertTrue(len(resp['data']) > 0)

    def test_make_df(self):
      scnl=Scnl("BABR","BHZ","UW")
      resp=iris.get_noise_pdf(scnl, "2017-01-01", "2017-02-01")
      data =resp['data']
      df= iris.make_df




if __name__ == '__main__':
    unittest.main()
