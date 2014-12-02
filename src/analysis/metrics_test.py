from unittest import TestCase

import pandas as pd

from analysis import metrics


class MetricsTest(TestCase):
  def testL1(self):
    x = pd.Series([0., 10., 100.])
    y = pd.Series([0., 20., 90.])
    z = pd.Series([-10., -20., 90.])
    self.assertEqual(20 / 3., metrics.L1(x, y))
    self.assertEqual(20 / 3., metrics.L1(y, x))
    self.assertEqual(50 / 3., metrics.L1(x, z))
    self.assertEqual(50 / 3., metrics.L1(z, x))
    self.assertEqual(50 / 3., metrics.L1(y, z))
    self.assertEqual(50 / 3., metrics.L1(z, y))

  def testL1PreferUnderrated(self):
    x = pd.Series([0., 10., 120.])
    y = pd.Series([0., 20., 90.])
    z = pd.Series([-10., -20., 90.])
    self.assertEqual(25 / 3., metrics.L1PreferUnderrated(x, y))
    self.assertEqual(35 / 3., metrics.L1PreferUnderrated(y, x))
    self.assertEqual(13 / 3., metrics.L1PreferUnderrated(x, y, underrated_penalty=.1))
    self.assertEqual(31 / 3., metrics.L1PreferUnderrated(y, x, underrated_penalty=.1))

    self.assertEqual(35 / 3., metrics.L1PreferUnderrated(x, z))
    self.assertEqual(70 / 3., metrics.L1PreferUnderrated(z, x))
    self.assertEqual(14 / 3., metrics.L1PreferUnderrated(x, z, underrated_penalty=.2))
    self.assertEqual(70 / 3., metrics.L1PreferUnderrated(z, x, underrated_penalty=.2))

    self.assertEqual(25 / 3., metrics.L1PreferUnderrated(y, z))
    self.assertEqual(50 / 3., metrics.L1PreferUnderrated(z, y))