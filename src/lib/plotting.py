from matplotlib import pyplot as plt

colors = 'bygr'


def _Random5k(x, y):
  # C = len(x)
  #indices = np.random.random_sample(C) < (3000. / C)
  #return x[indices], y[indices]
  return x, y


def ScatterPlot(x, *ys):
  plt.figure(figsize=(12, 8))
  for y, c in zip(ys, colors):
    x1, y1 = _Random5k(x, y)
    plt.scatter(x1, y1, c=c, marker='.', lw=0)
  plt.show()


def LinePlot(x, *ys):
  plt.figure(figsize=(12, 8))
  for y, c in zip(ys, colors):
    x1, y1 = _Random5k(x, y)
    plt.plot(x1, y1, c=c)
  plt.show()


def HistogramPlot(*ys):
  plt.figure(figsize=(12, 8))
  for y, c in zip(ys, colors):
    plt.hist(y, bins=20, c=c)
  plt.show()