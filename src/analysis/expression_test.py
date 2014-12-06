import cStringIO as StringIO
from unittest import TestCase

import pandas as pd
import numpy as np


nan = np.nan
from pandas.util import testing as pd_test

from expression import *


class ExpressionTest(TestCase):
  def testEval(self):
    sio = StringIO.StringIO('\n'.join([
      ',pts,trb,team_ast,game_id,team',
      'ole:20141003sas,12,5,3,20141003sas,sas',
      'gru:20141006pho,12,5,3,20141006pho,pho',
      'ole:20141006pho,1,4,0,20141006pho,sas',
      'val:20141001sas,7,5,2,20141001sas,sas',
      'ole:20141001sas,7,5,13,20141001sas,sas',
      'gru:20141004pho,4,4,4,20141004pho,pho',
    ]))
    df = pd.DataFrame.from_csv(sio)
    pd_test.assert_series_equal(df.trb, Leaf('trb').Eval(df))
    pd_test.assert_series_equal(2. * df.trb, (2. * Leaf('trb')).Eval(df))
    pd_test.assert_series_equal(2. * df.trb, (Leaf('trb') * 2.).Eval(df))
    pd_test.assert_series_equal(df.trb / df.pts, (Leaf('trb') / Leaf('pts')).Eval(df))
    pd_test.assert_series_equal(df.trb - 1., (Leaf('trb') - 1.).Eval(df))
    pd_test.assert_series_equal(1. - df.trb, (1. - Leaf('trb')).Eval(df))
    pd_test.assert_series_equal(-df.trb.astype(float), (-Leaf('trb')).Eval(df))
    pd_test.assert_series_equal(2. / df.trb, (2. / Leaf('trb')).Eval(df))
    pd_test.assert_series_equal(df.trb / 2., (Leaf('trb') / 2).Eval(df))

  def testAndOr(self):
    df = pd.DataFrame({'x': [0, 1, nan, 2, 3, nan],
                       'y': [1, nan, 2, nan, 4, nan],
                       'z': [1., 2., 3., 2., 5., 2.],
                       'empty': [nan] * 6})
    pd_test.assert_series_equal(
      pd.Series([0, 1, 2, 2, 3, np.nan]),
      (Leaf('x') | Leaf('y')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([1, nan, nan, nan, 7, nan]),
      (Leaf('x') + Leaf('y')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([0, nan, nan, nan, 3, nan]),
      (Leaf('x') & Leaf('y')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([nan, nan, 1, nan, nan, 1]),
      (~Leaf('x')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([nan, nan, 1, nan, nan, 1]),
      (~Leaf('x')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([nan, nan, nan, nan, nan, nan]),
      (~Leaf('z')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([nan, nan, nan, nan, nan, nan]),
      (Leaf('x') & Leaf('empty')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([1.] * 6),
      (~Leaf('empty')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([0., 1., 1., 2., 3, 1.]),
      (Leaf('x') | (~Leaf('x'))).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([nan, nan, 2., nan, nan, nan]),
      (Leaf('y') & (~Leaf('x'))).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([0, 1, nan, 2, 3, nan]),
      (Leaf('x') & 1).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([1, 1, nan, 1, 1, nan]),
      (1 & Leaf('x')).Eval(df))

  def testComparisonOperators(self):
    df = pd.DataFrame({'x': [0, 1, nan, 2, 3, nan],
                       'y': [1, nan, 2, nan, 4, nan],
                       'z': [1., 2., 3., 2., 5., 2.],
                       'empty': [nan] * 6})
    pd_test.assert_series_equal(
      pd.Series([1., nan, nan, nan, 1., nan]),
      (Leaf('x') < Leaf('y')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([1., nan, nan, nan, 1., nan]),
      (Leaf('y') > Leaf('x')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([1., 1., nan, nan, 1., nan]),
      (Leaf('z') > Leaf('x')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([1., 1., nan, 1., 1., nan]),
      (Leaf('z') >= Leaf('x')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([1., nan, nan, nan, nan, nan]),
      (Leaf('z') == 1.).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([1., nan, nan, nan, nan, nan]),
      (1 >= Leaf('z')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([nan, 1., 1., 1., 1., 1.]),
      (1 < Leaf('z')).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([1., 1., 1., 1., 1., 1.]),
      (Leaf('z') >= 1.).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([nan, 1., 1., 1., 1., 1.]),
      (Leaf('z') >= 2.).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([nan, nan, 1., nan, 1., nan]),
      (Leaf('z') > 2.).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([nan, 1, nan, 1, nan, 1]),
      (Leaf('z') == 2.).Eval(df))
    pd_test.assert_series_equal(
      pd.Series([nan, 1, nan, 1, nan, 1]),
      (2. == Leaf('z')).Eval(df))