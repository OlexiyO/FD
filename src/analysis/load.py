from collections import Counter
import itertools
import datetime
import os

import numpy as np

import pandas as pd


GAMES_PLAYED_FEATURE = 'games_played'
BASIC_FIELDS = [
  'pts', 'drb', 'orb', 'trb', 'ast', 'blk', 'stl',
  'tov', 'minutes', 'fg', 'fga', 'fg3', 'fg3a', 'ft', 'fta', 'fouls']


def LoadDataForSeason(year):
  DATA_DIR = 'C:/Coding/FanDuel/data/crawl/%d/csv/regular/' % year
  dfs = [pd.DataFrame.from_csv(os.path.join(DATA_DIR, fname))
         for fname in os.listdir(DATA_DIR)]
  DF = pd.concat(dfs)
  AddTeamPerGameFeatures(DF)
  AddPlayerPerGameFeatures(DF)
  AddSecondaryFeatures(DF)
  return DF


def DFToFloat(df):
  for name in df.columns:
    if np.issubdtype(df[name].dtype, int):
      df[name] = df[name].astype(float)


def PrintData(*args, **kwargs):
  topn = kwargs.pop('topn', 20)
  assert not kwargs
  if topn > 0:
    a = 0
    b = topn
  else:
    a = len(args[0]) + topn  # topn is negative
    b = None
  if len(args) < 1:
    for v in itertools.islice(args[0], a, b):
      print v
  else:
    data = [[] for _ in args]

    for i, val in enumerate(itertools.islice(itertools.izip(*args), a, b)):
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
  df['fantasy_pts_per_game'] = (df.pts_per_game + 1.2 * df.trb_per_game + 1.5 * df.ast_per_game +
                                2 * df.blk_per_game + 2 * df.stl_per_game - df.tov_per_game)


def AddTeamPerGameFeatures(df, fields=None):
  DFToFloat(df)
  if fields is None:
    fields = list(set(BASIC_FIELDS) - {'minutes', 'plus_minus'})
  fields = ['team_%s' % name for name in fields]
  gp_fname = 'team_%s' % GAMES_PLAYED_FEATURE
  df_sorted = df.sort(['game_id'])
  extra_df = pd.DataFrame(index=df.index,
                          data={s: 0. for s in fields + [gp_fname]})

  agg_data = {}
  games_for_team = {}
  for index, series in df_sorted.iterrows():
    player_id, game_id = index.split(':')
    team_id = series['team']
    previous_games = games_for_team.setdefault(team_id, set())
    if game_id in previous_games:
      games_count = float(len(previous_games) - 1)
      data_after_game = agg_data.get(team_id)
      extra_df[gp_fname][index] = games_count
      for fname in fields:
        extra_df[fname][index] = (data_after_game[fname] - series[fname]) / games_count if games_count else 0
    else:
      games_count = float(len(previous_games))
      previous_games.add(game_id)
      if team_id not in agg_data:
        agg_data[team_id] = {x: 0. for x in fields}

      data_before_game = agg_data.get(team_id)
      extra_df[gp_fname][index] = games_count
      for fname in fields:
        extra_df[fname][index] = (data_before_game[fname] / games_count) if games_count else 0
        agg_data[team_id][fname] += series[fname]

  df[gp_fname] = extra_df[gp_fname]
  for fname in fields:
    df['%s_per_game' % fname] = extra_df[fname]


def AddPlayerPerGameFeatures(df, fields=None):
  DFToFloat(df)
  if fields is None:
    fields = BASIC_FIELDS

  agg_data = {}
  df_sorted = df.sort(['game_id'])
  extra_df = pd.DataFrame(index=df.index,
                          data={s: 0. for s in fields + ['games_played']})
  games_played = Counter()
  for index, series in df_sorted.iterrows():
    player_id, game_id = index.split(':')
    player_data = agg_data.get(player_id)
    if player_data is None:
      player_data = {x: 0. for x in fields}
    games_count = float(games_played[player_id])
    extra_df[GAMES_PLAYED_FEATURE][index] = games_count
    for fname in fields:
      extra_df[fname][index] = player_data[fname] / games_count if games_count else 0
      player_data[fname] += series[fname]
    games_played[player_id] += 1
    agg_data[player_id] = player_data

  df[GAMES_PLAYED_FEATURE] = extra_df[GAMES_PLAYED_FEATURE]
  for fname in fields:
    df['%s_per_game' % fname] = extra_df[fname]


def GameDate(game_id):
  year, month, day = int(game_id[:4]), int(game_id[4:6]), int(game_id[6:8])
  return datetime.date(year, month, day)


def FirstGameEarlier(game_id1, game_id2):
  return GameDate(game_id1) < GameDate(game_id2)
