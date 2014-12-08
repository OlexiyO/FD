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