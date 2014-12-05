import os

from bs4 import BeautifulSoup
import pandas as pd

from analysis.player_info import NormalizeName


DATA_DIR = 'C:/Coding/FanDuel/data/crawl'


def PlayerIdFromPlayerLink(player_link):
  if (player_link.startswith('/players/') and
        player_link.endswith('.html')):
    res = os.path.basename(player_link)[:-5]  # drop .html
    assert player_link == '/players/%s/%s.html' % (res[0], res), player_link
    return res
  else:
    return None


def IsStatName(tag):
  return (tag.name == 'th' and
          tag.has_attr('data-stat') and
          'tooltip' in tag.get('class'))


def ProcessCellValueForTeam(field, value):
  if field in {'fg3_pct', 'fg_pct', 'ft_pct', 'ts_pct', 'efg_pct'}:
    return None
  elif field == 'player':
    return None
  elif field == 'pf':
    return 'team_fouls', value
  elif field == 'mp':
    return 'num_overtimes', (int(value) - 48 * 5) / (5 * 5)
  else:
    return ('team_%s' % field), value


def ProcessCellValueForPlayer(field, value):
  if field in {'fg3_pct', 'fg_pct', 'ft_pct', 'ts_pct', 'efg_pct'}:
    return None
  elif field == 'player':
    # return None
    return field, NormalizeName(value)
  elif field == 'pf':
    return 'fouls', value
  elif field == 'mp':
    assert value[-3] == ':', value
    mins = int(value[:-3])
    secs = int(value[-2:])
    assert 0 <= secs <= 59, value
    assert 0 <= mins < 70, value
    return 'minutes', (mins + (secs / 60.))
  else:
    return field, value


def FindTeams(soup):
  """Returns set of teams which played in this game."""
  team_href = lambda s: s.startswith('/teams/') and s.endswith('html')
  team_links = soup.findAll('a', href=team_href)
  return set(a.get('href')[7:10] for a in team_links)


def GetFieldNames(row):
  table = row.findParent(name='table')
  return [th.get('data-stat') for th in table.thead.findAll(IsStatName)]


def GetCellValues(row):
  return [cell.text.strip() for cell in row.findAll('td')]


def GetPlayerStats(row):
  field_names = GetFieldNames(row)
  values = GetCellValues(row)
  if len(values) == 2:
    if 'Did Not Play' in values[1] or 'Player Suspended' in values[1]:
      values = values[:1] + ['0:00'] + [0. for _ in field_names[2:]]
    else:
      raise AssertionError('Something wrong while parsing row:\n%s' % row)
  assert len(values) == len(field_names), (values, field_names)
  res = {}
  for field, value in zip(field_names, values):
    v1 = ProcessCellValueForPlayer(field, value)
    if v1 is not None:
      res[v1[0]] = v1[1]
  return res


def GetTeamStats(player_row):
  table = player_row.findParent(name='table')
  rows = table.findAll(class_='stat_total')
  assert len(rows) == 1, rows
  row = rows[0]
  field_names = GetFieldNames(row)
  values = GetCellValues(row)
  assert len(values) == len(field_names), (values, field_names)
  res = {}
  for field, value in zip(field_names, values):
    v1 = ProcessCellValueForTeam(field, value)
    if v1 is not None:
      res[v1[0]] = v1[1]
  return res


def HtmlToCsv(in_dir, out_dir, fname, with_advanced_stats=False):
  print fname
  filepath = os.path.join(in_dir, fname)
  game_id = fname[:-5]  # Drop .html
  home_team = game_id[-3:].upper()
  ymd = game_id[:8]
  with open(filepath) as fin:
    soup = BeautifulSoup(fin)
  player_href = lambda s: s.startswith('/players/') and s.endswith('html')
  stats_as = soup.findAll(name='a', href=player_href)
  active_rows = [a.parent.parent for a in stats_as]
  data = {}

  teams = FindTeams(soup)
  team_stats = {}

  for row in active_rows:
    try:
      player_id = PlayerIdFromPlayerLink(row.td.a.get('href'))
    except AttributeError:
      if 'Inactive' not in row.td.text.strip():
        raise
      else:
        continue

    if not player_id:
      continue

    record_id = player_id + ':' + game_id
    table = row.findParent(name='table')
    if table.get('id').endswith('advanced') and not with_advanced_stats:
      continue

    try:
      team_id = table.get('id')[:3].upper()
    except Exception:
      print 'RRR', row
      raise
    assert team_id in teams, (team_id, teams)

    d = data.get(record_id, {})
    d['player_id'] = player_id
    d['team'] = team_id
    d['opponent'] = teams.difference({team_id}).pop()
    d['is_home'] = team_id == home_team
    d['game_id'] = game_id
    d['date'] = ymd
    d.update(GetPlayerStats(row))
    if team_id not in team_stats:
      team_stats[team_id] = GetTeamStats(row)
    d.update(team_stats[team_id])

    data[record_id] = d
  df = pd.DataFrame.from_dict(data).transpose()
  csv_fname = fname[:-5] + '.csv'
  df.to_csv(os.path.join(out_dir, csv_fname))
  return df


def ParseRegSeasonAndOverwrite(year):
  base_dir = os.path.join(DATA_DIR, '%d' % year)
  raw_dir = os.path.join(base_dir, 'raw', 'regular')
  csv_dir = os.path.join(base_dir, 'csv', 'regular')
  for fname in os.listdir(raw_dir):
    if fname.endswith('.html'):
      HtmlToCsv(raw_dir, csv_dir, fname)


def ParseRegSeason(year):
  base_dir = os.path.join(DATA_DIR, '%d' % year)
  raw_dir = os.path.join(base_dir, 'raw', 'regular')
  csv_dir = os.path.join(base_dir, 'csv', 'regular')
  for fname in os.listdir(raw_dir):
    if fname.endswith('.html'):
      output_file = os.path.join(csv_dir, fname.replace('.html', '.csv'))
      if not os.path.exists(output_file):
        HtmlToCsv(raw_dir, csv_dir, fname)