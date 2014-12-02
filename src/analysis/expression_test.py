import cStringIO as StringIO
from unittest import TestCase

import pandas as pd
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