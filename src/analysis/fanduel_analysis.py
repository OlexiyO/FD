from collections import namedtuple
import os
import itertools

import pandas as pd

from lib import expression
from analysis import knapsack
from analysis.player_info import Position, PlayerStatus, PlayerInfo
from crawl.fanduel_parser import ParseFDFile
from crawl.player_ids import FD_DIR, GetPlayerPosition
from lib.misc_functions import PrintRows
from lib.plotting import HistogramPlot


EmulationResult = namedtuple('EmulationResult', ['score', 'team'])

def Emulate(fd_data, player_predictions, player_results,
            requests=Position.FD_REQUEST, salary_cap=60000):
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
  return EmulationResult(score=sum(player_results.get(pi.pid, 0) for pi in best),
                         team=best)


def _SeriesToPlayerMap(series, date):
  res = {}
  for index, value in series.iteritems():
    pid, game_id = index.split(':')
    assert game_id.startswith(date)
    res[pid] = value
  return res


def FDFromFile(filepath):
  return ParseFDFile(filepath)[0]


ENOUGH_DATA = (
  (expression.Leaf('minutes') >= 10) &
  (expression.Leaf('minutes_per_game') >= 10) &
  (expression.Leaf('games_played') >= 10))


def _CheckFDGames(fd_games_generator, predictions, df, requests,
                  print_selections=False, df_filter=ENOUGH_DATA, only_healthy=True,
                  expr_real_result=expression.Leaf('fantasy_pts')):
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
    results = [Emulate(players_list, pred, results_for_day,
                       requests=requests).score
               for pred in pred_for_day]
    if all(r < 30 for r in results):
      continue
    for r, allr in zip(results, all_results):
      allr.append(r)
    print str(date_need).ljust(15), '\t', '\t'.join('%.1f' % r for r in results)

  PrintComparison(all_results)
  PrintRRTable(all_results)
  HistogramPlot(*all_results)


def _FDGamesGenerator(fd_dir):
  for fname in os.listdir(fd_dir):
    if fname.endswith('late.html') or not fname.endswith('.html'):
      continue
    players_list = FDFromFile(os.path.join(FD_DIR, fname))
    date_need = fname[:10].replace('_', '')
    yield date_need, players_list


def PredictDay(df, prediction, fd_date,
               requests=Position.FD_REQUEST,
               only_healthy=True,
               banned_players=None,
               included_players=None,
               expr_real_result=expression.Leaf('fantasy_pts')):
  banned_players = banned_players or []
  included_players = included_players or []
  prediction = expression.LeafOrExpr(prediction)
  filepath = os.path.join(FD_DIR, '%s.html' % fd_date)
  assert os.path.exists(filepath), filepath
  date_need = fd_date.replace('_', '')
  small_df = df[df['date_id'] == int(date_need)]
  pid = small_df['player_id']

  players_list = FDFromFile(filepath)
  if only_healthy:
    players_list = [p for p in players_list
                    if p.status == PlayerStatus.OK]
  pred_for_day = dict(itertools.izip(pid, prediction.Eval(small_df)))
  results_for_day = dict(itertools.izip(pid, expr_real_result.Eval(small_df)))
  requests_adjusted = dict(requests)
  salary_cap = 60000
  preselected = []
  for p in players_list:
    if p.pid in included_players:
      requests_adjusted[p.position] -= 1
      salary_cap -= p.salary
      preselected.append(p.Override(pts=-1))

  players_list = [p for p in players_list
                  if p.pid not in included_players and p.pid not in banned_players]
  result = Emulate(players_list, pred_for_day, results_for_day,
                   requests=requests_adjusted, salary_cap=salary_cap)
  print requests_adjusted
  result = EmulationResult(score=result.score, team=result.team + preselected)
  for b in result.team:
    print 'Scored:', '{:4.1f}'.format(results_for_day.get(b.pid, 0)), b
  return result


def CheckAllFDGames(predictions, df, requests=Position.FD_REQUEST,
                    print_selections=False,
                    df_filter=ENOUGH_DATA, only_healthy=True,
                    expr_real_result=expression.Leaf('fantasy_pts')):
  _CheckFDGames(_FDGamesGenerator(FD_DIR), predictions, df, requests,
                print_selections=print_selections,
                df_filter=df_filter, only_healthy=only_healthy, expr_real_result=expr_real_result)


def _VirtualGamesGenerator(df, expr_salaries_from):
  min_salary = 3500
  salaries_eval = expr_salaries_from.Eval(df)
  salary_mult = df['fantasy_pts_per_game'].mean() / salaries_eval.mean()
  for date_id in sorted(set(df['date_id'])):
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


def CheckVirtualFDGames(predictions, df, requests=Position.FD_REQUEST,
                        print_selections=False,
                        df_filter=ENOUGH_DATA, only_healthy=True,
                        expr_real_result=expression.Leaf('fantasy_pts'),
                        expr_salaries_from=expression.Leaf('fantasy_pts_per_game')):
  _CheckFDGames(_VirtualGamesGenerator(df, expr_salaries_from),
                predictions, df, requests,
                print_selections=print_selections,
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
  print '\t\t'.join('%.1f' % x.quantile(.25) for x in series_infos) + '\t\t25%'
  print '\t\t'.join('%.1f' % x.median() for x in series_infos) + '\t\tmedian'
  print '\t\t'.join('%.1f' % x.quantile(.75) for x in series_infos) + '\t\t75%'
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
    print 'Predicted:', '{:4.1f}'.format(player_predictions[b.pid]), b
