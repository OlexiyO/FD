from analysis import fanduel_analysis
from lib.expression import LeafOrExpr, AbstractExpression, Leaf


def _PrepareSignals(df, input_signals):
  return zip(*[LeafOrExpr(x).Eval(df) for x in input_signals])


def Train(model, df, input_signals, output_signal, df_filter):
  df = df_filter.Filter(df)
  target = LeafOrExpr(output_signal).Eval(df)
  return model.fit(_PrepareSignals(df, input_signals), target)


def CompareOnVirtualGames(df, df_filter, input_signals, **models):
  df = df_filter.Filter(df)
  candidates = []
  data = _PrepareSignals(df, input_signals)
  for name, model in sorted(models.iteritems()):
    if isinstance(model, (basestring, AbstractExpression)):
      candidates.append(LeafOrExpr(model))
    else:
      df[name] = model.predict(data)
      candidates.append(Leaf(name))
  fanduel_analysis.CheckVirtualFDGames(candidates, df, df_filter=df_filter)


def EvalModel(df, model, input_signals):
  if isinstance(model, (basestring, AbstractExpression)):
    return LeafOrExpr(model).Eval(df)
  else:
    return model.predict(_PrepareSignals(df, input_signals))


def PerStepScores(df, model, input_signals, output_signal):
  data = _PrepareSignals(df, input_signals)
  target = LeafOrExpr(output_signal).Eval(df)
  loss_fn = model.loss_
  d = []
  for prediction in model.staged_predict(data):
    d.append(loss_fn(prediction, target))
  return d


# Method to plot submodel

def BuildPWL(node, points):
  node = LeafOrExpr(node)
  x0, y0 = points[0]
  res = y0 & (node <= x0)
  for i, (x1, y1) in enumerate(points):
    x0, y0 = points[i - 1]
    slope = float(y1 - y0) / (x1 - x0)
    res |= (y0 + slope * (node - x0)) & (node <= x1)
  return res | points[-1][1]