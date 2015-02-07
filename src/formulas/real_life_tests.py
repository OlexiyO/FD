import unittest
from unittest import TestCase

from analysis.fanduel_analysis import PredictDay


global_DF_15 = None
global_prediction = None


class RealLifeTests(TestCase):
  def testDrasticChange(self):
    result = PredictDay(global_DF_15, global_prediction, '2014_12_16')
    print result
    self.assertFalse('jacksre01' in [x.pid for x in result.team])


def TestPrediction(DF_15, prediction):
  global global_prediction
  global global_DF_15
  global_prediction = prediction
  global_DF_15 = DF_15
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(RealLifeTests)
  unittest.TextTestRunner().run(suite)


__all__ = ['TestPrediction']