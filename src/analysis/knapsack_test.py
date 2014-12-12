import math
import itertools
import random
from unittest import TestCase
import time

from analysis.fanduel_analysis import CheckVirtualFDGames
from analysis.knapsack import BestChoice
from analysis.player_info import Position, PlayerInfo


class KnapsackTest(TestCase):
  def testAlgoSimple(self):
    players = [
      PlayerInfo(name='A', salary=10000, pts=40, position=Position.C),
      PlayerInfo(name='B', salary=5000, pts=20, position=Position.C),
      PlayerInfo(name='C', salary=1000, pts=25, position=Position.C),
      PlayerInfo(name='D', salary=900, pts=5, position=Position.C),
      PlayerInfo(name='E', salary=100, pts=100, position=Position.PG)
    ]
    res = BestChoice(players, {Position.C: 1}, 10000)
    self.assertEqual([players[0]], res)

    res = BestChoice(players, {Position.C: 1}, 9999)
    self.assertEqual([players[2]], res)

    res = BestChoice(players, {Position.C: 1}, 900)
    self.assertEqual([players[3]], res)

    res = BestChoice(players, {Position.C: 2}, 9900)
    self.assertEqual([players[1], players[2]], res)

    res = BestChoice(players, {Position.C: 2}, 5900)
    self.assertEqual([players[2], players[3]], res)

    res = BestChoice(players, {Position.PG: 1}, 10000)
    self.assertEqual([players[4]], res)

    res = BestChoice(players, {Position.PG: 1, Position.C: 1}, 10100)
    self.assertEqual([players[0], players[4]], res)

    res = BestChoice(players, {Position.PG: 1, Position.C: 1}, 10000)
    self.assertEqual([players[2], players[4]], res)

  def testAlgoComplex(self):
    for n in range(100):
      request = Position.FD_REQUEST
      players = []
      seed = int(time.time() * 1000000) % 1000000
      print 'Seed:', seed
      random.seed(seed)
      D = {p: [] for p in Position.ALL}
      for p, count in request.iteritems():
        for _ in range(2 * count):
          pts = random.gauss(20, 7)
          salary = max(3500., math.floor(.5 + pts * 2.5) * 100.)
          p1 = PlayerInfo(position=p, name='', salary=salary, pts=pts)
          players.append(p1)
          D[p].append(p1)
      salary_cap = 40000 + random.gauss(5000, 2500)
      res = BestChoice(players, request, salary_cap)
      best, bval = [], 0
      per_position = [itertools.combinations(D[p], request[p]) for p in Position.ALL]
      for option in itertools.product(*per_position):
        ddd = list(itertools.chain(*option))
        if sum(x.salary for x in ddd) <= salary_cap:
          tpts = sum(x.pts for x in ddd)
          if tpts > bval:
            best, bval = ddd, tpts
      if bval <= 0:
        print 'Impossibru!'
        self.assertIsNone(res)
        continue
      else:
        print
        print sorted(res)
        print sorted(best)
        self.assertEqual(sorted(res), sorted(best))


  def testXXX(self):
    from analysis import load
    from lib import expression

    expr1 = expression.Leaf('fantasy_pts_per_game')
    golden = expression.Leaf('fantasy_pts')
    DF_15 = load.LoadDataForSeason(2015)
    CheckVirtualFDGames(expr1, golden, DF_15)