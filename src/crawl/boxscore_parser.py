import os
import string

from bs4 import BeautifulSoup
import pandas as pd


GOOD_CHARS = string.letters + ' '


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


def ProcessFieldValue(field, value):
  if field in {'fg3_pct', 'fg_pct', 'ft_pct', 'ts_pct', 'efg_pct'}:
    return None
  elif field == 'player':
    # return None
    return ''.join(c for c in value if c in GOOD_CHARS)
  elif field == 'mp':
    assert value[-3] == ':', value
    mins = int(value[:-3])
    secs = int(value[-2:])
    assert 0 <= secs <= 59, value
    assert 0 <= mins < 70, value
    return mins + (secs / 60.)
  else:
    return value


def FindTeams(soup):
  """Returns set of teams which played in this game."""
  team_href = lambda s: s.startswith('/teams/') and s.endswith('html')
  team_links = soup.findAll('a', href=team_href)
  return set(a.get('href')[7:10] for a in team_links)


def HtmlToCsv(in_dir, out_dir, fname):
  filepath = os.path.join(in_dir, fname)
  game_id = fname[:-5]
  home_team = game_id[-3:].upper()  # Drop .html
  ymd = game_id[:8]
  with open(filepath) as fin:
    soup = BeautifulSoup(fin)
  player_href = lambda s: s.startswith('/players/') and s.endswith('html')
  stats_as = soup.findAll(name='a', href=player_href)
  active_rows = [a.parent.parent for a in stats_as]
  data = {}

  teams = FindTeams(soup)

  for row in active_rows:
    try:
      player_id = PlayerIdFromPlayerLink(row.td.a.get('href'))
    except AttributeError as e:
      if 'Inactive' not in row.td.text.strip():
        raise
      else:
        continue

    if not player_id:
      continue

    record_id = player_id + ':' + game_id
    d = data.get(record_id, {})
    table = row.findParent(name='table')
    try:
      team_id = table.get('id')[:3].upper()
    except Exception:
      print 'RRR', row
      raise
    assert team_id in teams, (team_id, teams)
    d['player_id'] = player_id
    d['team'] = team_id
    d['opponent'] = teams.difference({team_id}).pop()
    d['is_home'] = team_id == home_team
    d['game_id'] = game_id
    d['date'] = ymd
    field_names = [th.get('data-stat') for th in table.thead.findAll(IsStatName)]
    values = [x.text.strip() for x in row.findAll('td')]
    if len(values) == 2:
      if 'Did Not Play' in values[1]:
        continue
      if 'Player Suspended' in values[1]:
        continue
      assert False, row
    assert len(values) == len(field_names), (values, field_names)
    for field, value in zip(field_names, values):
      v1 = ProcessFieldValue(field, value)
      if v1 is not None:
        d[field] = v1
    data[record_id] = d
  df = pd.DataFrame.from_dict(data).transpose()
  csv_fname = fname[:-5] + '.csv'
  print fname
  df.to_csv(os.path.join(out_dir, csv_fname))
  return df
