import os
import itertools

import pandas as pd

from analysis import knapsack
from analysis.player_info import Position, PlayerStatus, PlayerInfo
from crawl.fanduel_parser import ParseFDFile
from crawl.player_ids import FD_DIR, GetPlayerPosition
from lib import expression
from lib.misc_functions import PrintRows


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
  return ParseFDFile(filepath)[0]


ENOUGH_DATA = (expression.Leaf('minutes') >= 10) & (expression.Leaf('minutes_per_game') >= 10)


def _CheckFDGames(fd_games_generator, predictions, df, print_selections=False,
                  df_filter=ENOUGH_DATA, only_healthy=True,
                  expr_real_result=expression.Leaf('fantasy_pts'),
):
  df = df_filter.Filter(df)
  for i, p in enumerate(predictions):
    print i + 1, p
  pred_series = [expression.LeafOrExpr(p).Eval(df) for p in predictions]
  all_results = [[] for _ in predictions]
  for date_need, players_list in fd_games_generator:
    if only_healthy:
      players_list = [p for p in players_list if p.status == PlayerStatus.OK]
    flt = df['date_id'] == int(date_need)
    pid = df['player_id'][flt]
    pred_for_day = [dict(itertools.izip(pid, ps[flt])) for ps in pred_series]
    results_for_day = dict(itertools.izip(pid, expr_real_result.Eval(df)[flt]))
    results = [Emulate(players_list, pred, results_for_day, print_selections=print_selections)
               for pred in pred_for_day]
    for r, allr in zip(results, all_results):
      allr.append(r)
      # print fname[:-5].ljust(15), '\t', '\t'.join('%.1f' % r for r in results)

  PrintComparison(all_results)
  PrintRRTable(all_results)


def _FDGamesGenerator(fd_dir):
  for fname in os.listdir(fd_dir):
    if not fname.endswith('.html'):
      continue
    players_list = FDFromFile(os.path.join(FD_DIR, fname))
    date_need = fname[:10].replace('_', '')
    yield date_need, players_list


def CheckAllFDGames(predictions, df, print_selections=False,
                    df_filter=ENOUGH_DATA, only_healthy=True,
                    expr_real_result=expression.Leaf('fantasy_pts')):
  _CheckFDGames(_FDGamesGenerator(FD_DIR), predictions, df, print_selections=print_selections,
                df_filter=df_filter, only_healthy=only_healthy, expr_real_result=expr_real_result)


def _VirtualGamesGenerator(df, expr_salaries_from, gameday_cutoff=10):
  gameday = 0
  min_salary = 3500
  salaries_eval = expr_salaries_from.Eval(df)
  salary_mult = df['fantasy_pts_per_game'].mean() / salaries_eval.mean()
  for date_id in sorted(set(df['date_id'])):
    gameday += 1
    if gameday < gameday_cutoff:
      continue
    flt = df['date_id'] == date_id
    pids = df['player_id'][flt]
    salaries = ((2.5 * salaries_eval[flt] * salary_mult).astype(int) * 100).map(lambda x: max(x, min_salary))
    players_list = [
      PlayerInfo(position=GetPlayerPosition(pid), name=pid,
                 salary=sal, health=PlayerStatus.OK,
                 status=PlayerStatus.OK, pts=None, pid=pid)
      for pid, sal in zip(pids, salaries)
      if GetPlayerPosition(pid) is not None]
    if players_list:
      yield date_id, players_list


def CheckVirtualFDGames(predictions, df, print_selections=False,
                        df_filter=ENOUGH_DATA, only_healthy=True,
                        expr_real_result=expression.Leaf('fantasy_pts'),
                        expr_salaries_from=expression.Leaf('fantasy_pts_per_game')):
  _CheckFDGames(_VirtualGamesGenerator(df, expr_salaries_from),
                predictions, df, print_selections=print_selections,
                df_filter=df_filter, only_healthy=only_healthy, expr_real_result=expr_real_result)


def PrintRRTable(all_results):
  def CreateTable():
    yield [''] + ['%d' % (i + 1) for i, _ in enumerate(all_results)]
    for n, res in enumerate(all_results):
      scores = ['%d : %d (%d)' % Score(res, rk) if k != n else '    XXX'
                for k, rk in enumerate(all_results)]
      yield ['%d' % (n + 1)] + scores

  PrintRows(CreateTable())


def Score(scores_base, scores_test):
  assert len(scores_base) == len(scores_test)
  wins = sum(1 for x, y in zip(scores_base, scores_test) if x > y + .10001)
  losses = sum(1 for x, y in zip(scores_base, scores_test) if x < y - .10001)
  return wins, losses, len(scores_base) - wins - losses


def PrintComparison(infos):
  """Each element of infos is a list of results for one prediction."""
  series_infos = [pd.Series(i) for i in infos]
  print '\t\t'.join('%.1f' % x.median() for x in series_infos) + '\t\tmedian'
  print '\t\t'.join('%.1f' % x.mean() for x in series_infos) + '\t\tmean'


def PredictTomorrow(df, fname, expr):
  date_need = fname[:10].replace('_', '')
  flt = (df['date_id'] == float(date_need))
  df = df[flt]
  players_list = FDFromFile(os.path.join(FD_DIR, fname))

  pid = df['player_id']
  prediction = expr.Eval(df)
  player_predictions = dict(itertools.izip(pid, prediction[flt]))

  players_out = ['jacksre01',  # not good enough after Durant is back
                 'wroteto01'  # too risky to be injured
  ]
  updated_data = [
    pi.Override(pts=player_predictions.get(pi.pid, 0))
    for pi in players_list
    if pi.status != PlayerStatus.OUT and pi.pid not in players_out]
  best = knapsack.BestChoice(updated_data, Position.FD_REQUEST, 60000)
  for b in best:
    print b, player_predictions[b.pid]
