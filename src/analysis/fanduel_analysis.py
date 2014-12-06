import os

from analysis import knapsack
from analysis.player_info import Position, PlayerStatus
from analysis import load
from crawl import fanduel_parser
from crawl.player_ids import FD_DIR


def Emulate(fd_data, player_predictions, player_results,
            requests=Position.FD_REQUEST, salary_cap=60000,
            print_results=False):
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
  if print_results:
    for p in best:
      print p, player_results.get(p.pid, 0)
  return sum(player_results.get(pi.pid, 0) for pi in best)


def _SeriesToPlayerMap(series, date):
  res = {}
  for index, value in series.iteritems():
    pid, game_id = index.split(':')
    if game_id.startswith(date):
      res[pid] = value
  return res


DF_15 = None


def CheckAllFDGames(prediction_expr, df=None, only_healthy=True, print_results=False):
  if df is None:
    global DF_15
    if DF_15 is None:
      DF_15 = load.LoadDataForSeason(2015)
    df = DF_15

  prediction_series = prediction_expr.Eval(df)
  for fname in os.listdir(FD_DIR):
    if not fname.endswith('.html'):
      continue
    players_list = fanduel_parser.FDFromFile(os.path.join(FD_DIR, fname))
    if only_healthy:
      players_list = [p for p in players_list if p.status == PlayerStatus.OK]
    date_need = fname[:10].replace('_', '')
    prediction_for_day = _SeriesToPlayerMap(prediction_series, date_need)
    results_for_day = _SeriesToPlayerMap(df['fantasy_pts'], date_need)
    print Emulate(players_list, prediction_for_day, results_for_day, print_results=print_results)