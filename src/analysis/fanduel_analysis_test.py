import cStringIO as StringIO
from unittest import TestCase

import pandas as pd

from analysis import fanduel_analysis
from analysis.player_info import PlayerInfo, PlayerStatus
from lib.expression import Leaf


class FDAnalysisTest(TestCase):
  def _CheckPlayersList(self, players, expected):
    self.assertEqual(len(players), len(expected))
    for pinfo in players:
      self.assertIn(pinfo.pid, expected)
      position, salary = expected[pinfo.pid]
      self.assertEqual(pinfo,
                       PlayerInfo(position=position, name=pinfo.pid, salary=salary,
                                  health=PlayerStatus.OK, status=PlayerStatus.OK, pts=None, pid=pinfo.pid))

  def testVirtualGamesGenerator(self):
    sio = StringIO.StringIO('\n'.join([
      ',fantasy_pts_per_game,date_id,player_id',
      '0,16,20141212,barbole01',
      '1,24.4,20141212,duncati01',
      '2,20.3,20141212,greenda02',
      '3,25.3,20141213,greenda02',
      '4,10,20141213,ibakase01',
      '5,35,20141213,rosede01',
    ]))
    df = pd.DataFrame.from_csv(sio)
    output = list(fanduel_analysis._VirtualGamesGenerator(df, Leaf('fantasy_pts_per_game'), gameday_cutoff=0))
    self.assertEqual(2, len(output))
    date1, players1 = output[0]
    date2, players2 = output[1]
    self.assertEqual(date1, 20141212)
    self._CheckPlayersList(players1,
                           {'barbole01': ('SG', 4000),
                            'duncati01': ('PF', 6100),
                            'greenda02': ('SG', 5000)})
    self.assertEqual(date2, 20141213)
    self._CheckPlayersList(players2,
                           {'greenda02': ('SG', 6300),
                            'ibakase01': ('PF', 3500),  # min salary
                            'rosede01': ('PG', 8700)})

    # Now with 1 game cutoff
    output = list(fanduel_analysis._VirtualGamesGenerator(df, Leaf('fantasy_pts_per_game'), gameday_cutoff=2))
    self.assertEqual(1, len(output))
    date, players = output[0]
    self.assertEqual(date, 20141213)
    self._CheckPlayersList(players,
                           {'greenda02': ('SG', 6300),
                            'ibakase01': ('PF', 3500),  # min salary
                            'rosede01': ('PG', 8700)})

  def testVirtualGamesGeneratorWithDiffSalary(self):
    sio = StringIO.StringIO('\n'.join([
      ',fantasy_pts_per_game,date_id,player_id,pts_per_game',
      '0,16,20141212,barbole01,10',
      '1,24.4,20141212,duncati01,10',
      '2,20.3,20141212,greenda02,8.5',
      '3,25.3,20141213,greenda02,10.5',
      '4,10,20141213,ibakase01,4.0',
      '5,35,20141213,rosede01,24',
    ]))
    # Average pts per game: 11.16
    # fantasy pts: 21.83
    # multiplier: 1.95522
    df = pd.DataFrame.from_csv(sio)
    output = list(fanduel_analysis._VirtualGamesGenerator(df, Leaf('pts_per_game'), gameday_cutoff=2))
    self.assertEqual(1, len(output))
    date, players = output[0]
    self.assertEqual(date, 20141213)
    self._CheckPlayersList(players,
                           {'greenda02': ('SG', 5100),
                            'ibakase01': ('PF', 3500),  # min salary
                            'rosede01': ('PG', 11700)})