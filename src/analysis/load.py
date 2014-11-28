from collections import defaultdict
import itertools
import datetime
import os

import pandas as pd


def AllDataForSeason(year):
  DATA_DIR = 'C:/Coding/FanDuel/data/crawl/%d/csv/regular/' % year
  dfs = [pd.DataFrame.from_csv(os.path.join(DATA_DIR, fname))
         for fname in os.listdir(DATA_DIR)]
  return pd.concat(dfs), dfs


def PrintData(*args, **kwargs):
  topn = kwargs.pop('topn', 20)
  assert not kwargs
  if len(args) < 1:
    for v in args[0][:topn]:
      print v
  else:
    data = [[] for _ in args]
    for i, val in enumerate(itertools.izip(*args)):
      if i >= topn:
        break
      for j, x in enumerate(val):
        data[j].append(str(x))
    for i, col in enumerate(data):
      maxw = max(len(s) for s in col)
      data[i] = [s.ljust(maxw) for s in col]
    for vals in itertools.izip(*data):
      print '\t'.join('%s' % s for s in vals)


def AddSecondaryFeatures(df):
  df['fantasy_pts'] = (df.pts + 1.2 * df.trb + 1.5 * df.ast +
                       2 * df.blk + 2 * df.stl - df.tov)


def AddPerGameFeatures(df, fields=None):
  if fields is None:
    fields = [
      'fantasy_pts', 'pts', 'drb', 'orb', 'trb', 'ast', 'blk', 'stl',
      'tov', 'mp', 'fg', 'fga', 'fg3', 'fg3a', 'ft', 'fta', 'pf']

  agg_data = {}

  df_sorted = df.sort(['game_id'])
  extra_df = pd.DataFrame(index=df.index,
                          data={s: 0 for s in fields + ['games_played']})
  games_played = defaultdict(int)
  for index, series in df_sorted.iterrows():
    player_id, game_id = index.split(':')
    player_data = agg_data.get(player_id)
    if player_data is None:
      player_data = {x: 0 for x in fields}
    games_count = float(games_played[player_id])
    extra_df['games_played'][index] = games_count
    for fname in fields:
      extra_df[fname][index] = player_data[fname] / games_count if games_count else 0
      player_data[fname] += series[fname]
    games_played[player_id] += 1
    agg_data[player_id] = player_data

  df['games_played'] = extra_df['games_played']
  for fname in fields:
    df['%s_per_game' % fname] = extra_df[fname]


def GameDate(game_id):
  year, month, day = int(game_id[:4]), int(game_id[4:6]), int(game_id[6:8])
  return datetime.date(year, month, day)


def FirstGameEarlier(game_id1, game_id2):
  return GameDate(game_id1) < GameDate(game_id2)


