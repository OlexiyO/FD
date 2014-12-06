import pandas as pd

OPERS = {
  'add': '+',
  'sub': '-',
  'mul': '*',
  'div': '/',
  'fillna': '|',

}

__all__ = ['AbstractExpression', 'Leaf', 'BinaryDFMethod']

class AbstractExpression(object):
  def Expr(self):
    raise NotImplementedError

  def Eval(self, df):
    raise NotImplementedError

  def __add__(self, other):
    return BinaryDFMethod('add', self, other)

  def __radd__(self, other):
    return BinaryDFMethod('add', other, self)

  def __sub__(self, other):
    return BinaryDFMethod('sub', self, other)

  def __rsub__(self, other):
    return BinaryDFMethod('sub', other, self)

  def __mul__(self, other):
    return BinaryDFMethod('mul', self, other)

  def __rmul__(self, other):
    return BinaryDFMethod('mul', other, self)

  def __rdiv__(self, other):
    return BinaryDFMethod('div', other, self)

  def __div__(self, other):
    return BinaryDFMethod('div', self, other)

  def __neg__(self):
    return 0 - self

  def __or__(self, other):
    return BinaryDFMethod('fillna', self, other)

  def __invert__(self):
    return Func(lambda x: pd.Series(1., index=x.index)[x.isnull()].reindex(x.index),
                lambda x: '~(%s)' & x,
                self)

  def __and__(self, other):
    return Func(lambda x, y: x[~y.isnull()].reindex(x.index),
                lambda x, y: '(%s) & (%s)' & (x, y),
                self, other)


def CreateConst(x):
  return x if isinstance(x, AbstractExpression) else Const(x)


class Func(AbstractExpression):
  def __init__(self, func, printout, *args):
    self._func = func
    self._printout = printout
    self._args = [CreateConst(a) for a in args]

  def Eval(self, df):
    return self._func(*[a.Eval(df) for a in self._args])

  def Expr(self):
    return self._printout(*[a.Expr() for a in self._args])


class BinaryDFMethod(AbstractExpression):
  def __init__(self, what, a, b):
    self._oper = what
    self._a = CreateConst(a)
    self._b = CreateConst(b)

  def Eval(self, df):
    x = self._a.Eval(df)
    y = self._b.Eval(df)
    return getattr(x, self._oper)(y)

  def Expr(self):
    return '(%s) %s (%s)' % (self._a.Expr(), OPERS[self._oper], self._b.Expr())


class Leaf(AbstractExpression):
  def __init__(self, name):
    self._name = name

  def Expr(self):
    return self._name

  def Eval(self, df):
    return df[self._name]


class Const(AbstractExpression):
  def __init__(self, value):
    self._value = float(value)

  def Expr(self):
    return self._value

  def Eval(self, df):
    return pd.Series(self._value, index=df.index)