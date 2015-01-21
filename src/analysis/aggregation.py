class Aggregator(object):
  def getAndUpdate(self, value):
    res = self.get()
    self.update(value)
    return res

  def update(self, value):
    raise NotImplementedError

  def get(self):
    raise NotImplementedError


class Mean(Aggregator):
  def __init__(self):
    super(Mean, self).__init__()
    self._sum = 0
    self._count = 0

  def get(self):
    return float(self._sum) / self._count if self._count else 0

  def update(self, value):
    self._count += 1
    self._sum += value


class MedianLastN(Aggregator):
  def __init__(self, N):
    super(MedianLastN, self).__init__()
    self._N = N
    self._data = [0] * self._N
    self._count = 0
    self._index = 0

  def get(self):
    return sorted(self._data[:self._count])[self._count / 2] if self._count else 0

  def update(self, value):
    if self._count < self._N:
      self._count += 1

    self._data[self._index] = value
    self._index += 1
    self._index %= self._N


class MeanLastN(Aggregator):
  def __init__(self, N):
    super(MeanLastN, self).__init__()
    self._N = N
    self._data = [0] * self._N
    self._sum = 0
    self._count = 0
    self._index = 0

  def get(self):
    return float(self._sum) / self._count if self._count else 0

  def update(self, value):
    if self._count < self._N:
      self._count += 1
    else:
      self._sum -= self._data[self._index]

    self._data[self._index] = value
    self._sum += value
    self._index += 1
    self._index %= self._N


class TotalCount(Aggregator):
  def __init__(self):
    super(TotalCount, self).__init__()
    self._count = 0

  def get(self):
    return self._count

  def update(self, unused_value):
    self._count += 1


MeanLast10 = lambda: MeanLastN(10)
LastOne = lambda: MeanLastN(1)

MedianLast10 = lambda: MedianLastN(10)