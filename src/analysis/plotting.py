from matplotlib import pyplot as plt


def ScatterPlot(x, *ys):
  plt.figure(figsize=(12, 8))
  for y in ys:
    plt.scatter(x, y)
  plt.show()


def LinePlot(x, *ys):
  plt.figure(figsize=(12, 8))
  for y in ys:
    plt.plot(x, y)
  plt.show()


def HistogramPlot(*ys):
  plt.figure(figsize=(12, 8))
  for y in ys:
    plt.hist(y, bins=20)
  plt.show()