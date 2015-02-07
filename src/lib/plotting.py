from matplotlib import pyplot as plt
import numpy as np

# From http://colorbrewer2.org/
COLORS = [
  '#b3e2cd',
  '#fdcdac',
  '#cbd5e8',
  '#f4cae4',
  '#e6f5c9',
  '#fff2ae',
  '#f1e2cc',
]


def _Random5k(x, y):
  C = len(x)
  if C <= 5000:
    return x, y
  indices = np.random.random_sample(C) < (5000. / C)
  return x[indices], y[indices]
  # return x, y


def ScatterPlot(x, *ys):
  plt.figure(figsize=(12, 8))
  for y, c in zip(ys, COLORS):
    x1, y1 = _Random5k(x, y)
    plt.scatter(x1, y1, s=150, c=c, marker='.', lw=0)
  plt.legend(NLabels(len(ys)))
  plt.show()


def LinePlot(x, *ys):
  plt.figure(figsize=(12, 8))
  for y, c in zip(ys, COLORS):
    x1, y1 = _Random5k(x, y)
    plt.plot(x1, y1, linewidth=2, c=c)
  plt.legend(NLabels(len(ys)))
  plt.show()


def HistogramPlot(*ys):
  plt.figure(figsize=(12, 8))
  clrs = COLORS[:len(ys)]
  plt.hist(ys, bins=20, color=clrs, edgecolor='white', histtype='bar')
  plt.legend(NLabels(len(ys)))
  plt.show()


def NLabels(cnt):
  return ['%d' % n for n in range(1, cnt + 1)]