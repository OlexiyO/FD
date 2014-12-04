from collections import namedtuple


class Position(object):
  PG = 'PG'
  SG = 'SG'
  SF = 'SF'
  PF = 'PF'
  C = 'C'


Position.ALL = [Position.C, Position.PF, Position.PG, Position.SF, Position.SG]


class PlayerStatus(object):
  OUT = 'OUT'
  GTD = 'GTD'
  OK = ''


class PlayerInfo(namedtuple(
  'PlayerInfo', ['position', 'name', 'salary', 'pts', 'health', 'status'])):
  def __new__(cls, position, name, salary, pts, health='', status=''):
    return super(PlayerInfo, cls).__new__(
      cls, position=position, name=name, salary=salary, pts=pts,
      health=health, status=status)
