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
  FD_REQUEST = {C: 1, SG: 2, SF: 2, PF: 2, PG: 2}
  ALL = [C, PF, PG, SF, SG]


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

  def ShortName(self):
    return '%15s' % self.name[:15]

  def __str__(self):
    basic = '%s, %2s: %4.1f for %5d$' % (self.ShortName(), self.position, self.pts, self.salary)
    if self.health or self.status:
      basic = '(%s %s) %s' % (self.health, self.status, basic)
    return basic