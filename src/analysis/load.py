from collections import Counter
import datetime
import os
import time

import numpy as np
import pandas as pd

from crawl.fanduel_parser import ParseFDFile


GAMES_PLAYED_FEATURE = 'games_played'
BASIC_FIELDS = [
  'pts', 'drb', 'orb', 'trb', 'ast', 'blk', 'stl',
  'tov', 'minutes', 'fg', 'fga', 'fg3', 'fg3a', 'ft', 'fta', 'fouls']

"""
Field names:
  trb: rebounds player got in game N.
  trb_per_game: rebounds per game player had BEFORE game N.
  team_trb: rebounds team got in game N
  team_trb_per_game: rebounds team had BEFORE game N.
  opp_trb: rebounds opponent got in game N
  opp_trb_per_game: rebounds different opponents of my team had BEFORE game N
      (averaging over my games)
  other_trb_per_game: rebounds my current opponent had BEFORE game N
      (averaging over their games)
"""


def DFForPrediction(extra_fd_file):
  fname = os.path.basename(extra_fd_file)
  date_id = fname[:10].replace('_', '')
  player_infos, game_infos = ParseFDFile(extra_fd_file)
  date, game_id, is_home, opponent, player, player_id, team = {}, {}, {}, {}, {}, {}, {}
  for pinfo in player_infos:
    pid = pinfo.pid
    game_info = game_infos[pid]
    host_team_id = game_info.team if game_info.is_home else game_info.opponent
    cur_game_id = date_id + '0' + host_team_id
    index = '%s:%s' % (pid, cur_game_id)
    is_home[index] = game_info.is_home
    team[index] = game_info.team
    opponent[index] = game_info.opponent
    game_id[index] = cur_game_id
    date[index] = float(date_id)
    player_id[index] = pid
    player[index] = pinfo.name
  return pd.DataFrame({
    'date': date,
    'game_id': game_id,
    'is_home': is_home,
    'opponent': opponent,
    'team': team,
    'player': player,
    'player_id': player_id})


def LoadDataForSeason(year, extra_fd_file=None):
  t0 = time.clock()
  DATA_DIR = 'C:/Coding/FanDuel/data/crawl/%d/csv/regular/' % year
  dfs = [pd.DataFrame.from_csv(os.path.join(DATA_DIR, fname))
         for fname in os.listdir(DATA_DIR)]
  if extra_fd_file:
    fd_df = DFForPrediction(extra_fd_file)
    for cname in dfs[0].columns:
      if cname not in fd_df.columns:
        fd_df[cname] = 0
    dfs.append(fd_df)

  print 'Loaded from disk:', time.clock() - t0
  DF = pd.concat(dfs)

  DF['date_id'] = DF['game_id'].map(lambda x: x[:8]).astype(int)
  AggregatePlayerPerGameFeatures(DF)
  AddRestFeaturesForPlayer(DF)
  AddOpponentFeatures(DF)
  AggregateTeamPerGameFeatures(DF)
  AddOtherFeatures(DF)
  AddSecondaryFeatures(DF)
  if 'is_home' in DF.columns:
    # TODO: Fix this during parsing.
    DF['is_home'] = DF['is_home'][DF['is_home']]
  print 'Processed:', time.clock() - t0
  return DF


def PrepareDF(df):
  for name in df.columns:
    if np.issubdtype(df[name].dtype, int):
      df[name] = df[name].astype(float)

  if 'date_id' in df.columns:
    df.sort(['date_id', 'game_id'], inplace=True)
  else:
    # Test
    df.sort(['game_id'], inplace=True)


def AddSecondaryFeatures(df):
  df['fantasy_pts'] = (df.pts + 1.2 * df.trb + 1.5 * df.ast +
                       2 * df.blk + 2 * df.stl - df.tov)
  df['fantasy_pts_per_game'] = (df.pts_per_game + 1.2 * df.trb_per_game + 1.5 * df.ast_per_game +
                                2 * df.blk_per_game + 2 * df.stl_per_game - df.tov_per_game)
  # ((Tm FGA + 0.4 * Tm FTA - 1.07 * (Tm ORB / (Tm ORB + Opp DRB)) * (Tm FGA - Tm FG) + Tm TOV)
  df['team_off_poss'] = (
    df.team_fga + 0.4 * df.team_fta + df.team_tov +
    -1.07 * (df.team_orb / (df.team_orb + df.opp_drb)) * (df.team_fga - df.team_fg))
  df['team_off_poss'].fillna(0., inplace=True)
  df['team_def_poss'] = (
    df.opp_fga + 0.4 * df.opp_fta + df.opp_tov +
    -1.07 * (df.opp_orb / (df.opp_orb + df.team_drb)) * (df.opp_fga - df.opp_fg))
  df['team_def_poss'].fillna(0., inplace=True)
  df['team_poss'] = .5 * (df['team_def_poss'] + df['team_off_poss'])

  df['team_def_poss_per_game'] = AggregatePerGameForTeam(df, df['team_def_poss'])
  df['team_off_poss_per_game'] = AggregatePerGameForTeam(df, df['team_off_poss'])
  df['team_poss_per_game'] = .5 * (df['team_def_poss_per_game'] + df['team_off_poss_per_game'])
  df['other_poss_per_game'] = MirrorFeatureForOpponent(df, 'team_poss_per_game')

  df['off_rating_per_game'] = df.team_pts_per_game / df.team_poss_per_game
  df['other_off_rating_per_game'] = MirrorFeatureForOpponent(df, 'off_rating_per_game')
  df['def_rating_per_game'] = df.opp_pts_per_game / df.team_poss_per_game
  df['other_def_rating_per_game'] = MirrorFeatureForOpponent(df, 'def_rating_per_game')


def MirrorFeatureForOpponent(df, fname_from):
  """For example, before SAS vs MIA game:
     A = 20 for SAS, 10 for MIA.
     MirrorFeatureForOpponent(df, 'A', 'B')
     would return series where opp_X will be 10 for SAS, 10 for MIA
  """
  key = df['game_id'].map(str) + ':' + df['team'].map(str)
  # (team_name:game_id) --> value
  data = dict(zip(key, df[fname_from]))
  opp_key = df['game_id'].map(str) + ':' + df['opponent'].map(str)
  return opp_key.map(data)


def AddOpponentFeatures(df, fields=None):
  PrepareDF(df)
  if fields is None:
    fields = list(set(BASIC_FIELDS) - {'minutes', 'plus_minus'})
  fields_from = ['team_%s' % fname for fname in fields]
  fields_to = ['opp_%s' % fname for fname in fields]
  for fname_from, fname_to in zip(fields_from, fields_to):
    df[fname_to] = MirrorFeatureForOpponent(df, fname_from)


def AddOtherFeatures(df, fields_from=None, fields_to=None):
  """Adds 'other' features."""
  PrepareDF(df)
  if fields_from is None:
    assert fields_to is None, fields_to
    fields = list(set(BASIC_FIELDS) - {'minutes', 'plus_minus'})
    fields_from = ['team_%s_per_game' % name for name in fields]
    fields_to = ['other_%s_per_game' % name for name in fields]
  else:
    assert len(fields_from) == len(fields_to)

  for fname_from, fname_to in zip(fields_from, fields_to):
    df[fname_to] = MirrorFeatureForOpponent(df, fname_from)


def AggregateTeamPerGameFeatures(df, fields=None):
  PrepareDF(df)
  if fields is None:
    fields = list(set(BASIC_FIELDS) - {'minutes', 'plus_minus'})
    fields = ['team_%s' % name for name in fields] + ['opp_%s' % name for name in fields]

  df['team_%s' % GAMES_PLAYED_FEATURE] = AggregatePerGameForTeam(
    df, pd.Series(1., index=df.index),
    per_game_feature=pd.Series(1., index=df.index))
  for fname in fields:
    df['%s_per_game' % fname] = AggregatePerGameForTeam(df, df[fname])


def AggregatePerGameForTeam(df, orig_feature, per_game_feature=None):
  """Returns "per_game" feature from orig_feature."""
  if per_game_feature is None:
    per_game_feature = df['team_%s' % GAMES_PLAYED_FEATURE]

  agg_data = Counter()
  games_for_team = {}
  res = pd.Series(0., index=df.index)
  for index, series in df.iterrows():
    player_id, game_id = index.split(':')
    team_id = series['team']
    previous_games = games_for_team.setdefault(team_id, set())
    if game_id not in previous_games:
      previous_games.add(game_id)
      agg_data[team_id] += orig_feature[index]

    games_count = per_game_feature[index]
    res[index] = (agg_data[team_id] - orig_feature[index]) / games_count if games_count else 0
  return res


def AddRestFeaturesForPlayer(df):
  # TODO(olexiy): Add features:
  # *) "when team played last time".
  # *) Whether there was travel since last game.
  # *) Games before the last.
  last_game = {}
  rest = pd.Series(None, df.index)
  prev_game_mp = pd.Series(None, df.index)
  for index, row in df.iterrows():
    pid = row['player_id']
    when_str = row['game_id'][:8]
    minutes = row['minutes']
    when = datetime.date(int(when_str[:4]), int(when_str[4:6]), int(when_str[6:8]))
    last_tup = last_game.get(pid)
    if last_tup:
      last, mp = last_tup
      assert last < when, index
      rest[index] = min(7, (when - last).days)
      prev_game_mp[index] = mp
    else:
      rest[index] = 7
      prev_game_mp[index] = 30
    last_game[pid] = when, minutes

  df['player_rest'] = rest
  df['player_previous_minutes'] = prev_game_mp


def AggregatePlayerPerGameFeatures(df, fields=None):
  PrepareDF(df)
  if fields is None:
    fields = BASIC_FIELDS

  agg_data = {}
  extra_df = pd.DataFrame(index=df.index,
                          data={s: 0. for s in fields + ['games_played']})
  games_played = Counter()
  for index, series in df.iterrows():
    player_id, game_id = index.split(':')
    player_data = agg_data.get(player_id)
    if player_data is None:
      player_data = {x: 0. for x in fields}
    games_count = float(games_played[player_id])
    extra_df[GAMES_PLAYED_FEATURE][index] = games_count
    for fname in fields:
      extra_df[fname][index] = player_data[fname] / games_count if games_count else 0
      player_data[fname] += series[fname]
    if series['minutes'] >= .1:
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
