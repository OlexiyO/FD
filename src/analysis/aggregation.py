import numpy as np

class Aggregator(object):
  def getAndUpdate(self, value):
    res = self.get()
    self.update(value)
    return res

  def update(self, value):
    raise NotImplementedError

  def get(self):
    raise NotImplementedError

  @staticmethod
  def numOutputs():
    return 1


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


class _LastNKeeper(object):
  def __init__(self, N):
    self._N = N
    self._data = [0] * self._N
    self._count = 0
    self._index = 0

  def Add(self, value):
    res = None if self._count < self._N else self._data[self._index]
    self._count = min(self._N, self._count + 1)
    self._data[self._index] = value
    self._index += 1
    self._index %= self._N
    return res

  def Count(self):
    return self._count

  def Data(self):
    start_index = (self._index - self._count + self._N) % self._N
    for i in range(self._count):
      yield self._data[(start_index + i) % self._N]


class MeanLastN(Aggregator):
  def __init__(self, N):
    super(MeanLastN, self).__init__()
    self._nkeeper = _LastNKeeper(N)
    self._sum = 0

  def get(self):
    count = self._nkeeper.Count()
    return float(self._sum) / count if count else 0

  def update(self, value):
    dropped = self._nkeeper.Add(value)
    if dropped is not None:
      self._sum -= dropped
    self._sum += value


class TotalCount(Aggregator):
  def __init__(self):
    super(TotalCount, self).__init__()
    self._count = 0

  def get(self):
    return self._count

  def update(self, unused_value):
    self._count += 1


class AfterChange(Aggregator):
  """Finds best 1-d split, and finds average after that change."""

  def __init__(self, N, min_split):
    assert N >= 2 * min_split, (N, min_split)
    self._N = N
    self._min_split = min_split
    self._nkeeper = _LastNKeeper(N)
    self._sum = 0

  def get(self):
    count = self._nkeeper.Count()
    lsum = 0
    if count < self._N:
      return np.nan, np.nan
    stop_at = count - self._min_split
    diff, res = 0, 0
    for i, v in enumerate(self._nkeeper.Data()):
      if i >= stop_at:
        break
      lsum += v
      lcount = i + 1
      if lcount >= self._min_split:
        lval = lsum / float(i + 1)
        rval = (self._sum - lsum) / float(count - lcount)
        new_diff = rval - lval
        if abs(new_diff) > abs(diff):
          diff, res = new_diff, rval

    return res, diff

  def update(self, value):
    dropped = self._nkeeper.Add(value)
    if dropped is not None:
      self._sum -= dropped
    self._sum += value

  @staticmethod
  def numOutputs():
    return 2


MeanLast10 = lambda: MeanLastN(10)
MeanLast5 = lambda: MeanLastN(5)
MeanLast3 = lambda: MeanLastN(3)
LastOne = lambda: MeanLastN(1)
AfterChange10_4 = lambda: AfterChange(10, 4)
AfterChange15_5 = lambda: AfterChange(15, 5)

MedianLast10 = lambda: MedianLastN(10)