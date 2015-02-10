import unittest
from unittest import TestCase

from analysis.fanduel_analysis import PredictDay


global_DF_15 = None
global_prediction = None


class RealLifeTests(TestCase):
  def _TestIn(self, who, day):
    result = PredictDay(global_DF_15, global_prediction, day)
    self.assertTrue(who in [x.pid for x in result.team], msg=result)

  def _TestOut(self, who, day):
    result = PredictDay(global_DF_15, global_prediction, day)
    self.assertFalse(who in [x.pid for x in result.team], msg=result)

  def testDrasticChange(self):
    self._TestOut('jacksre01', '2014_12_16')
    self._TestIn('whiteha01', '2015_01_25')


def TestPrediction(DF_15, prediction):
  global global_prediction
  global global_DF_15
  global_prediction = prediction
  global_DF_15 = DF_15
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(RealLifeTests)
  unittest.TextTestRunner().run(suite)


__all__ = ['TestPrediction']