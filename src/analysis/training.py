from analysis import fanduel_analysis
from lib.expression import LeafOrExpr, AbstractExpression, Leaf


## TODO: Try me!!!111

def Train(model, df, expressions, output_signal, df_filter):
  df = df_filter.Filter(df)
  input_exprs = [LeafOrExpr(x) for x in expressions]
  signals = [x.Eval(df) for x in input_exprs]
  target = LeafOrExpr(output_signal).Eval(df)
  return model.fit(zip(*signals), target)


def PlotPerStep(model, dfs, input_signals, output_signal,
                df_filter):
  pass


def CompareOnVirtualGames(df, df_filter, input_signals, **models):
  df = df_filter.Filter(df)
  signals = [LeafOrExpr(x).Eval(df) for x in input_signals]
  candidates = []
  for name, model in sorted(models.iteritems()):
    if isinstance(model, (basestring, AbstractExpression)):
      candidates.append(LeafOrExpr(model))
    else:
      df[name] = model.predict(zip(*signals))
      candidates.append(Leaf(name))
  fanduel_analysis.CheckVirtualFDGames(candidates, df, df_filter=df_filter)


def EvalModel(df, model, input_signals):
  if isinstance(model, (basestring, AbstractExpression)):
    return LeafOrExpr(model).Eval(df)
  else:
    signals = [LeafOrExpr(x).Eval(df) for x in input_signals]
    return model.predict(zip(*signals))
