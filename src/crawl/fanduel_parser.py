from analysis.player_info import PlayerInfo


def FDFromFile(filepath):
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
  data = eval(clean_line)
  return [
    PlayerInfo(position=v[0], name=v[1], salary=v[5], health=v[-3], status=v[-1], pts=None)
    for v in data.itervalues()]