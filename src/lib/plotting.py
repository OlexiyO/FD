from matplotlib import pyplot as plt

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
  # C = len(x)
  #indices = np.random.random_sample(C) < (3000. / C)
  #return x[indices], y[indices]
  return x, y


def ScatterPlot(x, *ys):
  plt.figure(figsize=(12, 8))
  for y, c in zip(ys, COLORS):
    x1, y1 = _Random5k(x, y)
    plt.scatter(x1, y1, c=c, marker='.', lw=0)
  plt.show()


def LinePlot(x, *ys):
  plt.figure(figsize=(12, 8))
  for y, c in zip(ys, COLORS):
    x1, y1 = _Random5k(x, y)
    plt.plot(x1, y1, c=c)
  plt.show()


def HistogramPlot(*ys):
  plt.figure(figsize=(12, 8))
  clrs = COLORS[:len(ys)]
  plt.hist(ys, bins=20, color=clrs, edgecolor='white', histtype='bar')
  plt.show()