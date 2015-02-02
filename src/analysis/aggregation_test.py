from unittest import TestCase

import numpy as np

from analysis import aggregation


class AggregationTest(TestCase):
  def testLast(self):
    x = aggregation.LastOne()
    self.assertEqual(0., x.get())
    self.assertEqual(0., x.get())
    self.assertEqual(0., x.get())
    self.assertEqual(0., x.getAndUpdate(5.))
    self.assertEqual(5, x.get())
    x.update(10.)
    self.assertEqual(10., x.get())
    self.assertEqual(10., x.getAndUpdate(15.))
    self.assertEqual(15., x.get())

  def testLast10(self):
    x = aggregation.MeanLast10()
    self.assertEqual(0., x.get())
    x.update(10)
    self.assertEqual(10., x.get())
    self.assertEqual(10., x.getAndUpdate(20.))
    self.assertEqual(15., x.get())

    for n in range(4):
      x.update(0.)
    # Now: 10, 20, 0, 0, 0, 0
    self.assertEqual(5., x.get())

    # Now: 10, 20, 0, 0, 0, 0, 30, 30, 30, 30
    for n in range(4):
      x.update(30.)

    self.assertEqual(15., x.get())
    self.assertEqual(15., x.getAndUpdate(40.))
    # Now: 40, 20, 0, 0, 0, 0, 30, 30, 30, 30
    self.assertEqual(18., x.get())

    for n in range(4):
      x.update(50.)
    # Now: 40, 50, 50, 50, 50, 0, 30, 30, 30, 30
    self.assertEqual(36., x.get())

  def testMean(self):
    x = aggregation.Mean()
    self.assertEqual(0., x.get())
    x.update(10)
    self.assertEqual(10., x.get())
    self.assertEqual(10., x.getAndUpdate(20.))
    self.assertEqual(15., x.get())

    for n in range(4):
      x.update(0.)
    # Now: 10, 20, 0, 0, 0, 0
    self.assertEqual(5., x.get())

    # Now: 10, 20, 0, 0, 0, 0, 30, 30, 30, 30
    for n in range(4):
      x.update(30.)

    self.assertEqual(15., x.get())
    self.assertEqual(15., x.getAndUpdate(40.))
    # Now: 10, 20, 0, 0, 0, 0, 30, 30, 30, 30, 40
    self.assertEqual(190. / 11., x.get())

    for n in range(4):
      x.update(50.)
    # Now: 10, 20, 0, 0, 0, 0, 30, 30, 30, 30, 40, 50, 50, 50, 50
    self.assertEqual(390. / 15., x.get())

  def testAfterChange(self):
    x = aggregation.AfterChange(5, 2)
    self.assertTrue(np.isnan(x.get()))
    x.update(0)
    x.update(2)
    x.update(1)
    x.update(10)
    self.assertTrue(np.isnan(x.get()))
    x.update(8)
    self.assertEqual(9, x.get())
    x.update(0)
    self.assertEqual(6, x.get())
    x.update(0)
    self.assertEqual(0, x.get())




