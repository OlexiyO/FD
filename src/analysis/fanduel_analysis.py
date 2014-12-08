import os
import itertools

from analysis import knapsack
from analysis.player_info import Position, PlayerStatus
from crawl import fanduel_parser
from crawl.player_ids import FD_DIR


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


def CheckAllFDGames(predictions, df, only_healthy=True, print_selections=False,
                    only_positive_minutes=True):
  knapsack.T = 0
  pred_series = [p.Eval(df) for p in predictions]
  for fname in os.listdir(FD_DIR):
    if not fname.endswith('.html'):
      continue
    players_list = fanduel_parser.FDFromFile(os.path.join(FD_DIR, fname))
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


def CheckVirtualFDGames(expr_base, expr_test, df):
  ser_base, ser_test = expr_base.Eval(df), expr_test.Eval(df)
  for date_id in set(df['date_id']):
    flt = df['date_id'] == date_id
    pred_base = ser_base[flt]
    pred_test = ser_test[flt]
    pid = df['player_id'][flt]
    results_for_day = dict(itertools.izip(pid, df['fantasy_pts'][flt]))
    results = [Emulate(players_list, pd, results_for_day, print_selections=print_selections)
               for pd in pred_for_day]
    print fname[:-5].ljust(15), '\t', '\t'.join('%.1f' % r for r in results)
