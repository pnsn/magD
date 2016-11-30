import unittest
import sys
import os
sys.path.append(os.path.abspath('..'))
# from MagD.core import parse_json_file
import MagD.iris as iris
from MagD.scnl import Scnl

from pprint import pprint
# import numpy as np
# import json



class TestIris(unittest.TestCase):
    
    
    def test_get_available_channels(self):
        sta_string="UMAT"
        chan_string="HHZ,BHZ"
        net_string="UW,UO,CC,NC"
        scnls=iris.get_available_scnls(sta_string,chan_string,net_string)
        self.assertTrue(scnls[0].chan=="HHZ")
        self.assertIsInstance(scnls[0].lat, float)
        self.assertIsInstance(scnls[0].lon, float)
        self.assertIsInstance(scnls[0].samprate, float)
        
        chan_string="BHZ,HHZ"
        scnls=iris.get_available_scnls(sta_string,chan_string,net_string)
        self.assertTrue(scnls[0].chan=="BHZ")

        chan_string="ZZZ,HHZ"
        scnls=iris.get_available_scnls(sta_string,chan_string,net_string)
        self.assertTrue(scnls[0].chan=="HHZ")

        #vcr has tirggered HHZ but not continuous. This is bad
        sta_string="VCR"
        scnls=iris.get_available_scnls(sta_string,chan_string,net_string)
        self.assertTrue(scnls==[]);
        

    
    def test_get_noise_pdf(self):
        scnl=Scnl("BABR","BHZ","UW")
        noise=iris.get_noise_pdf(scnl)
        self.assertIsInstance(noise[0].attrib["hits"], str)
        
    def test_create_scnl_pdf_modes(self):
        scnls=[Scnl("BABR","BHZ","UW")]
        iris.create_scnl_pdf_modes(scnls)
        self.assertTrue(len(scnls[0].powers) >0)
        self.assertTrue(scnls[0].base !=None)
        self.assertTrue(scnls[0].freq0 !=None)
        
        
        
if __name__ == '__main__':
    unittest.main()
        
        