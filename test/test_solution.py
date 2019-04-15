import unittest
from magD.solution import Solution
from magD.scnl import Scnl


class TestSolution(unittest.TestCase):
    '''test solution class'''

    def test_obj_creation(self):
        '''test object creation'''
        scnl = Scnl("sta", "chan", "net", "loc")
        solution = Solution(scnl, 10)
        self.assertIsNotNone(solution)

if __name__ == '__main__':
    unittest.main()
