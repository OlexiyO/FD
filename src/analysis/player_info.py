from collections import namedtuple
import string


GOOD_CHARS = string.letters + ' '


def NormalizeName(value):
  return (''.join(c for c in value if c in GOOD_CHARS)).lower()

class Position(object):
  PG = 'PG'
  SG = 'SG'
  SF = 'SF'
  PF = 'PF'
  C = 'C'


Position.ALL = [Position.C, Position.PF, Position.PG, Position.SF, Position.SG]
Position.FD_REQUEST = {Position.C: 1, Position.SG: 2, Position.SF: 2, Position.PF: 2, Position.PG: 2}


class PlayerStatus(object):
  OUT = 'OUT'
  GTD = 'GTD'
  OK = ''


class PlayerInfo(namedtuple(
  'PlayerInfo', ['position', 'name', 'salary', 'pts', 'health', 'status', 'pid'])):
  def __new__(cls, position, name, salary, pts,
              health='', status=PlayerStatus.OK, pid=None):
    return super(PlayerInfo, cls).__new__(
      cls, position=position, name=NormalizeName(name), salary=salary, pts=pts,
      health=health, status=status, pid=pid)

  def Override(self, **kwargs):
    d = self._asdict()
    d.update(kwargs)
    return PlayerInfo(**d)