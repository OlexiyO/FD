import cStringIO as StringIO
from unittest import TestCase

import pandas as pd

from analysis import load


class LoadTest(TestCase):
  def testGameBefore(self):
    self.assertTrue(load.FirstGameEarlier('201312310MIN', '201401010MIN'))
    self.assertFalse(load.FirstGameEarlier('201401010MIN', '201312310MIN'))
    self.assertTrue(load.FirstGameEarlier('201411300MIN', '201412010HOU'))

  def testAddPerGameFeatures(self):
    sio = StringIO.StringIO('\n'.join([
      ',pts,trb,ast,game_id',
      'ole:3,12,5,3,3',
      'gru:6,12,5,3,6',
      'ole:6,1,4,0,6',
      'val:1,7,5,2,1',
      'ole:1,24,15,13,1',
      'gru:4,4,4,4,4',
    ]))
    test_df = pd.DataFrame.from_csv(sio)
    load.AddPerGameFeatures(test_df, ['pts', 'trb'])
    expected_sio = StringIO.StringIO('\n'.join([
      ',pts,trb,ast,game_id,games_played,pts_per_game,trb_per_game',
      'ole:3,12,5,3,3,1,24,15',
      'gru:6,12,5,3,6,1,4,4',
      'ole:6,1,4,0,6,2,18,10',
      'val:1,7,5,2,1,0,0,0',
      'ole:1,24,15,13,1,0,0,0',
      'gru:4,4,4,4,4,0,0,0',
    ]))
    expected = pd.DataFrame.from_csv(expected_sio)
    print expected
    print
    print test_df
    self.assertTrue((test_df == expected).all().all())