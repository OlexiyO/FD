from lib.misc_functions import PrintRows


def L1(real_score, predicted_score):
  return (predicted_score - real_score).abs().mean()


def L1PreferUnderrated(real_score, predicted_score, underrated_penalty=.5):
  diff = (predicted_score - real_score).astype(float)
  diff.update(underrated_penalty * diff[diff < 0])
  return diff.abs().mean()


class DistanceMetric(object):
  def __init__(self, golden_score):
    self._golden_score = golden_score

  def Compute(self, df, prediction):
    raise NotImplementedError


class L1Metric(DistanceMetric):
  def Compute(self, df, prediction):
    return (prediction.Eval(df) - self._golden_score.Eval(df)).abs().mean()


def CompareOnDataSets(metric, dfs, predictions):
  def Generate():
    empty_row = [''] * (len(dfs) + 1)
    yield [''] + ['%s' % df.name for df in dfs]
    base = [metric.Compute(df, predictions[0]) for df in dfs]
    for i, pred in enumerate(predictions):
      vals1 = [metric.Compute(df, pred) for df in dfs]
      yield ['%d' % (i + 1)] + ['%.2f' % v for v in vals1]
      if i:  # Do not print deltas for the base
        yield ['%d' % (i + 1)] + ['%+.2f' % (v1 - v0) for v0, v1 in zip(base, vals1)]
      yield empty_row

  PrintRows(Generate())
