import unittest
import magD.iris as iris


class TestIris(unittest.TestCase):

    def test_get_available_channels(self):
        sta_string = "UMAT"
        chan_string = "HHZ,BHZ"
        net_string = "UW,UO,CC,NC"
        resp = iris.get_fdsn(sta_string, chan_string, net_string)
        scnls = resp['data']
        self.assertEqual(resp['code'], 200)

        print(scnls)
        self.assertEqual(scnls[0][0], "UMAT")
        self.assertEqual(scnls[0][1], "HHZ")
        self.assertEqual(scnls[0][2], "UW")
        self.assertEqual(float(round(scnls[0][4], 4)), 45.2904)
        self.assertEqual(float(round(scnls[0][5], 4)), -118.9595)

    # FIXME, should use a mock here!
    # def test_get_noise_pdf(self):
    #     resp = iris.get_noise_pdf("sta", "chan", "net", "loc", "2017-01-01",
    #                               "2017-02-01")
    #     self.assertEqual(resp['code'], 200)
    #     self.assertTrue(len(resp['data']) > 0)


if __name__ == '__main__':
    unittest.main()
