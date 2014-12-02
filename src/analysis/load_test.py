import cStringIO as StringIO
from unittest import TestCase

import pandas as pd

from analysis import load


class LoadTest(TestCase):
  def testGameBefore(self):
    self.assertTrue(load.FirstGameEarlier('201312310MIN', '201401010MIN'))
    self.assertFalse(load.FirstGameEarlier('201401010MIN', '201312310MIN'))
    self.assertTrue(load.FirstGameEarlier('201411300MIN', '201412010HOU'))

  def testAddOpponentFeatures(self):
    sio = StringIO.StringIO('\n'.join([
      ',team,opponent,team_pts,team_trb,team_ast,game_id',
      'ole:20141003sas,sas,gsw,13,5,3,20141003sas',
      'curry:20141003sas,gsw,sas,18,15,1,20141003sas',
      'gru:20141006pho,pho,sas,12,5,3,20141006pho',
      'val:20141001sas,nyk,sas,7,5,2,20141001sas',
      'ole:20141001sas,sas,nyk,24,15,13,20141001sas',
      'ole:20141006pho,sas,pho,1,4,0,20141006pho',
    ]))
    test_df = pd.DataFrame.from_csv(sio)
    load.AddOpponentFeatures(test_df, ['pts', 'trb'])
    expected_sio = StringIO.StringIO('\n'.join([
      ',team,opponent,team_pts,team_trb,team_ast,game_id,opp_pts,opp_trb',
      'ole:20141003sas,sas,gsw,13,5,3,20141003sas,18,15',
      'curry:20141003sas,gsw,sas,18,15,1,20141003sas,13,5',
      'gru:20141006pho,pho,sas,12,5,3,20141006pho,1,4',
      'val:20141001sas,nyk,sas,7,5,2,20141001sas,24,15',
      'ole:20141001sas,sas,nyk,24,15,13,20141001sas,7,5',
      'ole:20141006pho,sas,pho,1,4,0,20141006pho,12,5',
    ]))
    expected = pd.DataFrame.from_csv(expected_sio)
    load.PrepareDF(expected)
    print expected
    print
    print test_df
    pd.util.testing.assert_frame_equal(test_df, expected, check_index_type=True)

  def testAddPlayerPerGameFeatures(self):
    sio = StringIO.StringIO('\n'.join([
      ',pts,trb,ast,game_id,team',
      'ole:20141003sas,13,5,3,20141003sas,sas',
      'gru:20141006pho,12,5,3,20141006pho,pho',
      'ole:20141006pho,1,4,0,20141006pho,sas',
      'val:20141001sas,7,5,2,20141001sas,sas',
      'ole:20141001sas,24,15,13,20141001sas,sas',
      'gru:20141004pho,4,4,4,20141004pho,pho',
    ]))
    test_df = pd.DataFrame.from_csv(sio)
    load.AggreatePlayerPerGameFeatures(test_df, ['pts', 'trb'])
    expected_sio = StringIO.StringIO('\n'.join([
      ',pts,trb,ast,game_id,team,games_played,pts_per_game,trb_per_game',
      'ole:20141003sas,13,5,3,20141003sas,sas,1,24,15',
      'gru:20141006pho,12,5,3,20141006pho,pho,1,4,4',
      'ole:20141006pho,1,4,0,20141006pho,sas,2,18.5,10',
      'val:20141001sas,7,5,2,20141001sas,sas,0,0,0',
      'ole:20141001sas,24,15,13,20141001sas,sas,0,0,0',
      'gru:20141004pho,4,4,4,20141004pho,pho,0,0,0',
    ]))
    expected = pd.DataFrame.from_csv(expected_sio)
    load.PrepareDF(expected)
    print expected
    print
    print test_df
    pd.util.testing.assert_frame_equal(test_df, expected, check_index_type=True)

  def testAddTeamPerGameFeatures(self):
    sio = StringIO.StringIO('\n'.join([
      ',team_pts,team_trb,team_ast,game_id,team',
      'ole:20141003sas,12,5,3,20141003sas,sas',
      'gru:20141006pho,12,5,3,20141006pho,pho',
      'ole:20141006pho,1,4,0,20141006pho,sas',
      'val:20141001sas,7,5,2,20141001sas,sas',
      'ole:20141001sas,7,5,13,20141001sas,sas',
      'gru:20141004pho,4,4,4,20141004pho,pho',
    ]))
    test_df = pd.DataFrame.from_csv(sio)
    load.AggregateTeamPerGameFeatures(test_df, ['team_pts', 'team_trb'])
    expected_sio = StringIO.StringIO('\n'.join([
      ',team_pts,team_trb,team_ast,game_id,team,team_games_played,team_pts_per_game,team_trb_per_game',
      'ole:20141003sas,12,5,3,20141003sas,sas,1,7,5',
      'gru:20141006pho,12,5,3,20141006pho,pho,1,4,4',
      'ole:20141006pho,1,4,0,20141006pho,sas,2,9.5,5',
      'val:20141001sas,7,5,2,20141001sas,sas,0,0,0',
      'ole:20141001sas,7,5,13,20141001sas,sas,0,0,0',
      'gru:20141004pho,4,4,4,20141004pho,pho,0,0,0',
    ]))
    expected = pd.DataFrame.from_csv(expected_sio)
    load.PrepareDF(expected)
    print expected
    print
    print test_df
    pd.util.testing.assert_frame_equal(test_df, expected, check_index_type=True)