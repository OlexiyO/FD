import os

from analysis import load
from analysis.player_info import NormalizeName
from crawl import fanduel_parser


IDS_MAPPING_PATH = 'C:/Coding/FanDuel/fd_html/ids_mapping'
FD_DIR = 'C:/Coding/FanDuel/fd_html/'
FDID_TO_PID_MAPPING = None
PID_TO_POSITION_MAPPING = None


def GetPlayerPosition(pid):
  global PID_TO_POSITION_MAPPING
  if PID_TO_POSITION_MAPPING is None:
    PID_TO_POSITION_MAPPING = {
      GetPlayerIdFromFDId(fdid): v[0]
      for unused_fname, fdid, v in AllFDData()
    }

  return PID_TO_POSITION_MAPPING.get(pid)


def GetPlayerIdFromFDId(fd_id):
  global FDID_TO_PID_MAPPING
  if FDID_TO_PID_MAPPING is None:
    with open(IDS_MAPPING_PATH) as fin:
      FDID_TO_PID_MAPPING = eval(fin.read())
  return FDID_TO_PID_MAPPING.get(fd_id, None)


SPECIAL_NAMES = {
  'dennis schroeder': 'dennis schrder',
  'phil flip pressey': 'phil pressey',
  'johnny obryant': None,
  'glenn robinson iii': 'glenn robinson',
  'roy devyn marble': 'devyn marble',
  'joel embiid': None,
  'glen rice jr': 'glen rice',
  'jose juan barea': 'jose barea',
  'tim hardaway jr': 'tim hardaway',
  'mitch mcgary': None,
  'ishmael smith': None,
  'damien inglis': None,
  'luc richard mbah a moute': 'luc mbah a moute',
  'brad beal': 'bradley beal',
  'grant jerrett': None,
  'perry jones iii': 'perry jones',
}


def MapName(fd_name):
  return SPECIAL_NAMES.get(fd_name, fd_name)


def AllFDData():
  for fname in os.listdir(FD_DIR):
    if not fname.endswith('.html'):
      continue
    tmp = fanduel_parser.ParseFDFile(os.path.join(FD_DIR, fname))
    for fdid, v in tmp.iteritems():
      yield fname, fdid, v


def CreateIds():
  fd_ids = {}
  for fname, fdid, v in AllFDData():
    name = NormalizeName(v[1])
    if name in fd_ids:
      assert fd_ids[name] == fdid
    fd_ids[name] = fdid

  DF_14 = load.LoadDataForSeason(2014)
  DF_15 = load.LoadDataForSeason(2015)
  br_ids = {}
  for df in [DF_14, DF_15]:
    for _, row in df.iterrows():
      pid = row['player_id']
      pname = NormalizeName(row['player'])
      if pname in br_ids and br_ids[pname] != pid:
        assert pid.startswith('mitchto0'), (pid, pname, br_ids[pname])
      br_ids[pname] = pid

  fd_to_br = {fdid: br_ids[MapName(name)] for name, fdid in fd_ids.iteritems()
              if MapName(name) is not None}
  with open(IDS_MAPPING_PATH, 'w') as fout:
    fout.write(str(fd_to_br))