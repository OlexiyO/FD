import os
import itertools

import pandas as pd

from analysis import knapsack
from analysis.player_info import Position, PlayerStatus, PlayerInfo, NormalizeName
from crawl.fanduel_parser import ParseFDFile
from crawl.player_ids import FD_DIR, GetPlayerPosition, GetPlayerIdFromFDId


def Emulate(fd_data, player_predictions, player_results,
            requests=Position.FD_REQUEST, salary_cap=60000,
            print_selections=False):
  """

  Args:
    fd_data: [PlayerInfo]
    predictions: dict(player_id --> number)
    results: dict(player_id --> number)

  Returns:
    How many points would've been scored.
  """
  updated_data = [
    pi.Override(pts=player_predictions.get(pi.pid, 0))
    for pi in fd_data]
  best = knapsack.BestChoice(updated_data, requests, salary_cap)
  if best is None:
    return None
  if print_selections:
    for p in best:
      print p, player_results.get(p.pid, 0)
  return sum(player_results.get(pi.pid, 0) for pi in best)


def _SeriesToPlayerMap(series, date):
  res = {}
  for index, value in series.iteritems():
    pid, game_id = index.split(':')
    assert game_id.startswith(date)
    res[pid] = value
  return res


DF_15 = None


def FDFromFile(filepath):
  return [
    PlayerInfo(position=v[0], name=NormalizeName(v[1]), salary=int(v[5]), health=v[-3],
               status=v[-1], pts=None, pid=GetPlayerIdFromFDId(fd_id))
    for fd_id, v in ParseFDFile(filepath).iteritems()]


def CheckAllFDGames(predictions, df, only_healthy=True, print_selections=False,
                    only_positive_minutes=True):
  knapsack.T = 0
  pred_series = [p.Eval(df) for p in predictions]
  for fname in os.listdir(FD_DIR):
    if not fname.endswith('.html'):
      continue
    players_list = FDFromFile(os.path.join(FD_DIR, fname))
    if only_healthy:
      players_list = [p for p in players_list if p.status == PlayerStatus.OK]
    date_need = fname[:10].replace('_', '')
    flt = df['date_id'] == int(date_need)
    pid = df['player_id'][flt]
    pred_for_day = [dict(itertools.izip(pid, ps[flt])) for ps in pred_series]
    results_for_day = dict(itertools.izip(pid, df['fantasy_pts'][flt]))
    results = [Emulate(players_list, pd, results_for_day, print_selections=print_selections)
               for pd in pred_for_day]
    print fname[:-5].ljust(15), '\t', '\t'.join('%.1f' % r for r in results)

  print knapsack.T


def CheckVirtualFDGames(expr_base, expr_test, df, print_per_day=False):
  ser_base, ser_test = expr_base.Eval(df), expr_test.Eval(df)
  scores_base, scores_test = [], []
  gameday = 0
  for date_id in sorted(set(df['date_id'])):
    gameday += 1
    if gameday < 10:
      continue
    flt = df['date_id'] == date_id
    pids = df['player_id'][flt]
    pred_base = dict(itertools.izip(pids, ser_base[flt]))
    pred_test = dict(itertools.izip(pids, ser_test[flt]))
    salaries = ((2.5 * df['fantasy_pts_per_game'][flt]).astype(int) * 100).map(lambda x: max(x, 3500))

    results_for_day = dict(itertools.izip(pids, df['fantasy_pts'][flt]))
    players_list = [
      PlayerInfo(position=GetPlayerPosition(pid), name=pid,
                 salary=sal, health=PlayerStatus.OK,
                 status=PlayerStatus.OK, pts=None, pid=pid)
      for pid, sal in zip(pids, salaries)
      if GetPlayerPosition(pid) is not None]
    if not players_list:
      continue
    sb = Emulate(players_list, pred_base, results_for_day, print_selections=False)
    st = Emulate(players_list, pred_test, results_for_day, print_selections=False)
    scores_base.append(sb)
    scores_test.append(st)
    if print_per_day:
      print str(date_id).ljust(15), '\t', '\t'.join('%.1f' % r for r in [sb, st])

  wins = sum(1 for x, y in zip(scores_base, scores_test) if x > y + .10001)
  losses = sum(1 for x, y in zip(scores_base, scores_test) if x < y - .10001)
  print 'Base:', expr_base
  print 'Test:', expr_test
  print 'Base\t\tTest\t\tDraw'
  print '%d\t\t%d\t\t(%d):' % (wins, losses, len(scores_base) - wins - losses)
  res_base = pd.Series(scores_base)
  res_test = pd.Series(scores_test)
  print '%.1f\t\t%.1f        median' % (res_base.median(), res_test.median())
  print '%.1f\t\t%.1f        mean' % (res_base.mean(), res_test.mean())
