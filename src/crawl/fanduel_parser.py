from analysis.player_info import PlayerInfo, NormalizeName
from player_ids import GetPlayerId


def ParseFDFile(filepath):
  data_line = ''
  with open(filepath) as fin:
    for line in fin:
      if 'FD.playerpicker.allPlayersFullData' in line:
        data_line = line
        break
  clean_line = data_line.replace('FD.playerpicker.allPlayersFullData = ', '')
  clean_line = clean_line.strip()
  clean_line = clean_line[:-1]  # drop trailing semicolon
  clean_line = clean_line.replace('false', 'False')
  clean_line = clean_line.replace('\\/', '/')
  return eval(clean_line)


def FDFromFile(filepath):
  return [
    PlayerInfo(position=v[0], name=NormalizeName(v[1]), salary=v[5], health=v[-3],
               status=v[-1], pts=None, pid=GetPlayerId(fd_id))
    for fd_id, v in ParseFDFile(filepath).iteritems()]