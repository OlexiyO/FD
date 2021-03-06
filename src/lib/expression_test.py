import cStringIO as StringIO
from unittest import TestCase
import math

import pandas as pd
import numpy as np
from pandas.util.testing import assert_series_equal

from lib.expression import *
from lib.expression import EOperators as E


nan = np.nan


class ExpressionTest(TestCase):
  def testExpr(self):
    self.assertEqual('x', Leaf('x').Expr())
    self.assertEqual('(~x)', (~Leaf('x')).Expr())
    self.assertEqual('(x + y)', (Leaf('x') + Leaf('y')).Expr())
    self.assertEqual('(x & y)', (Leaf('x') & Leaf('y')).Expr())
    self.assertEqual('(x | 1.0)', (Leaf('x') | 1).Expr())
    self.assertEqual('log(x)', E.Log(Leaf('x')).Expr())
    self.assertEqual('log((x & y))', E.Log(Leaf('x') & Leaf('y')).Expr())
    self.assertEqual('min(x,y)', E.Min(Leaf('x'), Leaf('y')).Expr())
    self.assertEqual('max(x,y,y)', E.Max(Leaf('x'), Leaf('y'), Leaf('y')).Expr())

  def testEvalWithNan(self):
    df = pd.DataFrame({'x': [0., 1., np.nan, np.nan],
                       'y': [10., np.nan, 11., np.nan], })
    assert_series_equal(pd.Series([10., np.nan, np.nan, np.nan]),
                        (Leaf('x') + Leaf('y')).Eval(df))
    assert_series_equal(pd.Series([0., np.nan, np.nan, np.nan]),
                        (Leaf('x') * Leaf('y')).Eval(df))
    assert_series_equal(pd.Series([0., np.nan, np.nan, np.nan]),
                        (Leaf('x') / Leaf('y')).Eval(df))
    assert_series_equal(pd.Series([float('inf'), np.nan, np.nan, np.nan]),
                        (Leaf('y') / Leaf('x')).Eval(df))
    assert_series_equal(pd.Series([1., math.exp(1.), np.nan, np.nan]),
                        E.Exp(Leaf('x')).Eval(df))
    assert_series_equal(pd.Series([np.nan, 0., np.nan, np.nan]),
                        E.Log(Leaf('x')).Eval(df))

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
    assert_series_equal(df.trb, Leaf('trb').Eval(df))
    assert_series_equal(2. * df.trb, (2. * Leaf('trb')).Eval(df))
    assert_series_equal(2. * df.trb, (Leaf('trb') * 2.).Eval(df))
    assert_series_equal(df.trb / df.pts, (Leaf('trb') / Leaf('pts')).Eval(df))
    assert_series_equal(df.trb - 1., (Leaf('trb') - 1.).Eval(df))
    assert_series_equal(1. - df.trb, (1. - Leaf('trb')).Eval(df))
    assert_series_equal(-df.trb.astype(float), (-Leaf('trb')).Eval(df))
    assert_series_equal(2. / df.trb, (2. / Leaf('trb')).Eval(df))
    assert_series_equal(df.trb / 2., (Leaf('trb') / 2).Eval(df))

    assert_series_equal((df.trb ** 2.).astype(float), (Leaf('trb') ** 2.).Eval(df))

  def testAndOr(self):
    df = pd.DataFrame({'x': [0, 1, nan, 2, 3, nan],
                       'y': [1, nan, 2, nan, 4, nan],
                       'z': [1., 2., 3., 2., 5., 2.],
                       'empty': [nan] * 6})
    assert_series_equal(
      pd.Series([0, 1, 2, 2, 3, np.nan]),
      (Leaf('x') | Leaf('y')).Eval(df))
    assert_series_equal(
      pd.Series([1, nan, nan, nan, 7, nan]),
      (Leaf('x') + Leaf('y')).Eval(df))
    assert_series_equal(
      pd.Series([0, nan, nan, nan, 3, nan]),
      (Leaf('x') & Leaf('y')).Eval(df))
    assert_series_equal(
      pd.Series([nan, nan, 1, nan, nan, 1]),
      (~Leaf('x')).Eval(df))
    assert_series_equal(
      pd.Series([nan, nan, 1, nan, nan, 1]),
      (~Leaf('x')).Eval(df))
    assert_series_equal(
      pd.Series([nan, nan, nan, nan, nan, nan]),
      (~Leaf('z')).Eval(df))
    assert_series_equal(
      pd.Series([nan, nan, nan, nan, nan, nan]),
      (Leaf('x') & Leaf('empty')).Eval(df))
    assert_series_equal(
      pd.Series([1.] * 6),
      (~Leaf('empty')).Eval(df))
    assert_series_equal(
      pd.Series([0., 1., 1., 2., 3, 1.]),
      (Leaf('x') | (~Leaf('x'))).Eval(df))
    assert_series_equal(
      pd.Series([nan, nan, 2., nan, nan, nan]),
      (Leaf('y') & (~Leaf('x'))).Eval(df))
    assert_series_equal(
      pd.Series([0, 1, nan, 2, 3, nan]),
      (Leaf('x') & 1).Eval(df))
    assert_series_equal(
      pd.Series([1, 1, nan, 1, 1, nan]),
      (1 & Leaf('x')).Eval(df))

  def testComparisonOperators(self):
    df = pd.DataFrame({'x': [0, 1, nan, 2, 3, nan],
                       'y': [1, nan, 2, nan, 4, nan],
                       'z': [1., 2., 3., 2., 5., 2.],
                       'empty': [nan] * 6})
    assert_series_equal(
      pd.Series([1., nan, nan, nan, 1., nan]),
      (Leaf('x') < Leaf('y')).Eval(df))
    assert_series_equal(
      pd.Series([1., nan, nan, nan, 1., nan]),
      (Leaf('y') > Leaf('x')).Eval(df))
    assert_series_equal(
      pd.Series([1., 1., nan, nan, 1., nan]),
      (Leaf('z') > Leaf('x')).Eval(df))
    assert_series_equal(
      pd.Series([1., 1., nan, 1., 1., nan]),
      (Leaf('z') >= Leaf('x')).Eval(df))
    assert_series_equal(
      pd.Series([1., nan, nan, nan, nan, nan]),
      (Leaf('z') == 1.).Eval(df))
    assert_series_equal(
      pd.Series([1., nan, nan, nan, nan, nan]),
      (1 >= Leaf('z')).Eval(df))
    assert_series_equal(
      pd.Series([nan, 1., 1., 1., 1., 1.]),
      (1 < Leaf('z')).Eval(df))
    assert_series_equal(
      pd.Series([1., 1., 1., 1., 1., 1.]),
      (Leaf('z') >= 1.).Eval(df))
    assert_series_equal(
      pd.Series([nan, 1., 1., 1., 1., 1.]),
      (Leaf('z') >= 2.).Eval(df))
    assert_series_equal(
      pd.Series([nan, nan, 1., nan, 1., nan]),
      (Leaf('z') > 2.).Eval(df))
    assert_series_equal(
      pd.Series([nan, 1, nan, 1, nan, 1]),
      (Leaf('z') == 2.).Eval(df))
    assert_series_equal(
      pd.Series([nan, 1, nan, 1, nan, 1]),
      (2. == Leaf('z')).Eval(df))

  def testLogExp(self):
    df = pd.DataFrame({'x': [0, 1, nan, 2, 3, nan],
                       'y': [1, nan, 2, nan, 4, nan]})
    assert_series_equal(pd.Series([0.] * 6), E.Log(1.).Eval(df))
    assert_series_equal(
      pd.Series([-np.inf, 0, nan, np.log(2.), np.log(3.), nan]),
      E.Log(Leaf('x')).Eval(df))
    assert_series_equal(
      pd.Series([0., 1., nan, 2., 3., nan]),
      E.Exp(E.Log(Leaf('x'))).Eval(df))

  def testMinMax(self):
    x, y = Leaf('x'), Leaf('y')
    df = pd.DataFrame({'x': [0, 1, nan, 2, 3, nan],
                       'y': [1, nan, 2, nan, 4, nan]})
    assert_series_equal(pd.Series([0., 1, 2, 2, 3, np.nan]),
                        E.Min(x, y).Eval(df))
    assert_series_equal(pd.Series([2., 1, 4, 2, 8, np.nan]),
                        E.Max(x, y, 2 * y).Eval(df))