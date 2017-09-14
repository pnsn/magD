import unittest
import sys
import os
sys.path.append(os.path.abspath('..'))
from magD.origin import Origin
from magD.scnl import Scnl

# from pprint import pprint
# import numpy as np
# import json




class TestOrigin(unittest.TestCase):
    
  """Test obj creation"""
  def test_obj_creation(self):
    Origin.collection=[]
    for lat in range(10):
      Origin(lat, -122)
    self.assertEqual(len(Origin.collection), 10)
  
  """Test insert order"""
  def test_insert_order(self):
    Origin.collection=[]
    
    o=Origin(45, -122)
    scnl0=Scnl("sta", "chan", "net")
    scnl1=Scnl("sta1", "chan", "net")
    scnl2=Scnl("sta2", "chan", "net")
    scnl3=Scnl("sta3", "chan", "net")

    
    o.insertDetection((3,scnl0))
    self.assertEqual(len(o.detections),1)
    '''should move to front'''
    o.insertDetection((2,scnl1))
    self.assertEqual(len(o.detections),2)
    self.assertEqual(o.detections[0][1], scnl1)
    '''should insert at end'''
    o.insertDetection((5,scnl3))
    print(o.detections)
    self.assertEqual(len(o.detections),3)
    self.assertEqual(o.detections[2][1], scnl3)
    
  '''test num_stas indexing'''   
    
  # def test_number_stas_index(self):
  #   o=Origin(45, -122)
  #   scnl=Scnl("sta", "chan", "net")
  #   for mag in range(4,0,-1):
  #     o.insertDetection(mag,scnl)
  #   # self.assertEqual(o.min_detection(3), 3)
          

        
   
if __name__ == '__main__':
    unittest.main()