from collections import namedtuple

from analysis.player_info import PlayerInfo, NormalizeName
from crawl.player_ids import GetPlayerIdFromFDId


GameInfo = namedtuple('GameInfo', ['is_home', 'team', 'opponent'])


def _GamesFDDictFromFile(filepath):
  with open(filepath) as fin:
    for line in fin:
      if 'FD.playerpicker.teamIdToFixtureCompactString' in line:
        clean_line = line.replace('FD.playerpicker.teamIdToFixtureCompactString = ', '')
        clean_line = clean_line.strip()
        clean_line = clean_line[:-1]  # drop trailing semicolon
        return eval(clean_line)


def FDPlayersDictFromFile(filepath):
  """Returns {fd_id: list of strings}, as found in FD html file."""
  with open(filepath) as fin:
    for line in fin:
      if 'FD.playerpicker.allPlayersFullData' in line:
        clean_line = line.replace('FD.playerpicker.allPlayersFullData = ', '')
        clean_line = clean_line.strip()
        clean_line = clean_line[:-1]  # drop trailing semicolon
        clean_line = clean_line.replace('false', 'False')
        clean_line = clean_line.replace('\\/', '/')
        return eval(clean_line)
  assert False, filepath


def ParseTeam(team_str):
  """team_str is either 'TEA' or '<b>TEA</b>'; team code is FD code.
  Returns standard 3-letter code.
  """
  fd_team_code = team_str[3:-4] if '<b>' in team_str else team_str
  return {
    'SA': 'SAS',
    'NO': 'NOP',
    'GS': 'GSW',
    'NY': 'NYK',
    'BKN': 'BRK',
    'CHA': 'CHO',
  }.get(fd_team_code, fd_team_code)


def ParseGameInfo(str_info):
  away, home = str_info.split('@')
  is_home = '<b>' in home
  team = ParseTeam(home if is_home else away)
  opponent = ParseTeam(away if is_home else home)
  return GameInfo(is_home=is_home, team=team, opponent=opponent)


def GamesInfoFromFile(filepath):
  games_fd_dict = _GamesFDDictFromFile(filepath)
  return {game_id: ParseGameInfo(value) for game_id, value in games_fd_dict.iteritems()}


def ParseFDFile(filepath):
  fd_players_data = FDPlayersDictFromFile(filepath)
  fd_games_dict = GamesInfoFromFile(filepath)
  players_infos = [
    PlayerInfo(position=v[0], name=NormalizeName(v[1]), salary=int(v[5]), health=v[-3],
               status=v[-1], pts=None, pid=GetPlayerIdFromFDId(fd_id))
    for fd_id, v in fd_players_data.iteritems()
    if GetPlayerIdFromFDId(fd_id) is not None]
  player_to_game = {GetPlayerIdFromFDId(fd_id): fd_games_dict[v[3]]
                    for fd_id, v in fd_players_data.iteritems()
                    if GetPlayerIdFromFDId(fd_id) is not None}
  return players_infos, player_to_game