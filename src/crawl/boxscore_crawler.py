import os
import time
import random

import requests
from bs4 import BeautifulSoup


















# TODO: take games from http://www.basketball-reference.com/leagues/NBA_2015_games.html
from crawl import boxscore_parser

BASE_BREF_PATH = 'http://www.basketball-reference.com'
DATA_DIR = 'C:/Coding/FanDuel/data/crawl'
DELAY = 10.  # How often do we request pages.


def PathForGamesForDay(y, m, d):
  return BASE_BREF_PATH + '/boxscores/index.cgi?day=%d&month=%d&year=%d' % (d, m, y)


def GetGameLinks(y, m, d):
  soup = BeautifulSoup(requests.get(PathForGamesForDay(y, m, d)).text)

  bad_links = []
  for td in soup.findAll('td', class_='align_right bold_text'):
    a = td.a
    if a.text == 'Final':
      yield BASE_BREF_PATH + a['href']
    else:
      bad_links.append(str(td))

  if bad_links:
    print 'Bad:', (y, m, d), bad_links


def CrawlGamesForDay(y, m, d):
  season = y if m <= 7 else y + 1
  html_dir = os.path.join(DATA_DIR, '%d' % season, 'raw', 'regular')
  csv_dir = os.path.join(DATA_DIR, '%d' % season, 'csv', 'regular')
  if not os.path.isdir(html_dir):
    os.makedirs(html_dir)

  for url in GetGameLinks(y, m, d):
    time.sleep(random.random() * DELAY)
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    fname = os.path.basename(url)
    filepath = os.path.join(html_dir, fname)
    with open(filepath, 'w') as fout:
      fout.write(soup.prettify(formatter='html'))
    boxscore_parser.HtmlToCsv(html_dir, csv_dir, fname)