from unittest import TestCase

from crawl.fanduel_parser import GameInfo, ParseGameInfo


class FDParser(TestCase):
  def testParseGameInfo(self):
    self.assertEqual(GameInfo(is_home=True, team='PHI', opponent='OKC'), ParseGameInfo("OKC@<b>PHI</b>"))
    self.assertEqual(GameInfo(is_home=False, team='CLE', opponent='TOR'), ParseGameInfo("<b>CLE</b>@TOR"))
    self.assertEqual(GameInfo(is_home=False, team='BRK', opponent='NYK'), ParseGameInfo("<b>BKN</b>@NY"))
    self.assertEqual(GameInfo(is_home=True, team='GSW', opponent='NOP'), ParseGameInfo("NO@<b>GS</b>"))
    self.assertEqual(GameInfo(is_home=True, team='SAS', opponent='NOP'), ParseGameInfo("NO@<b>SA</b>"))
    self.assertEqual(GameInfo(is_home=True, team='CHO', opponent='NOP'), ParseGameInfo("NO@<b>CHA</b>"))