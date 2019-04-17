import unittest
# import sys
# import os
# sys.path.append(os.path.abspath('..'))
from magD.origin import Origin
from magD.scnl import Scnl
from magD.solution import Solution


class TestOrigin(unittest.TestCase):

    def test_sort_and_truncate_solutions(self):
        """Test sorting and trucation"""
        o = Origin(45, -122)
        scnl0 = Scnl("sta", "chan", "net", "loc")
        scnl0a = Scnl("sta", "chan", "net", "loc")
        scnl1 = Scnl("sta1", "chan", "net", "loc")
        scnl1a = Scnl("sta1", "chan", "net", "loc")
        scnl2 = Scnl("sta2", "chan", "net", "loc")
        scnl3 = Scnl("sta3", "chan", "net", "loc")
        scnl3a = Scnl("sta3", "chan", "net", "loc")

        o.solutions.append(Solution(scnl0a, 1))
        o.solutions.append(Solution(scnl0, 10))
        o.solutions.append(Solution(scnl1a, 10))
        o.solutions.append(Solution(scnl1, 1))
        o.solutions.append(Solution(scnl2, 10))
        o.solutions.append(Solution(scnl3, 200))
        o.solutions.append(Solution(scnl3a, 199))
        o.sort_and_truncate_solutions(4)
        self.assertEqual(len(o.solutions), 4)
        self.assertEqual(o.solutions[0].value, 1)
        self.assertEqual(o.solutions[1].value, 1)
        self.assertEqual(o.solutions[2].value, 10)
        self.assertEqual(o.solutions[3].value, 199)

        o1 = Origin(45, -121)
        o1.solutions.append(Solution(scnl0, 10))
        o1.solutions.append(Solution(scnl1, 1))
        o1.solutions.append(Solution(scnl2, 10))
        o1.solutions.append(Solution(scnl3, 200))

        o1.sort_and_truncate_solutions(2)
        self.assertEqual(len(o1.solutions), 2)
        self.assertEqual(o1.solutions[0].value, 1)
        self.assertEqual(o1.solutions[1].value, 10)


        # o.insertDetection((3,scnl0))
        # self.assertEqual(len(o.solutions),1)
        # '''should move to front'''
        # o.insertDetection((2,scnl1))
        # self.assertEqual(len(o.solutions),2)
        # self.assertEqual(o.solutions[0][1], scnl1)
        # '''should insert at end'''
        # o.insertDetection((5,scnl3))
        # print(o.solutions)
        # self.assertEqual(len(o.solutions),3)
        # self.assertEqual(o.solutions[2][1], scnl3)

if __name__ == '__main__':
    unittest.main()
