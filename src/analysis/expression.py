import pandas as pd

OPERS = {
  'add': '+',
  'sub': '-',
  'mul': '*',
  'div': '/',
}


class AbstractExpression(object):
  def Expr(self):
    raise NotImplementedError

  def Eval(self, df):
    raise NotImplementedError

  def __add__(self, other):
    return BinaryOperation('add', self, other)

  def __radd__(self, other):
    return BinaryOperation('add', other, self)

  def __sub__(self, other):
    return BinaryOperation('sub', self, other)

  def __rsub__(self, other):
    return BinaryOperation('sub', other, self)

  def __mul__(self, other):
    return BinaryOperation('mul', self, other)

  def __rmul__(self, other):
    return BinaryOperation('mul', other, self)

  def __rdiv__(self, other):
    return BinaryOperation('div', other, self)

  def __div__(self, other):
    return BinaryOperation('div', self, other)

  def __neg__(self):
    return 0 - self


def CreateConst(x):
  return x if isinstance(x, AbstractExpression) else Const(x)


class BinaryOperation(AbstractExpression):
  def __init__(self, what, a, b):
    self._oper = what
    self._a = CreateConst(a)
    self._b = CreateConst(b)

  def Eval(self, df):
    x = self._a.Eval(df)
    y = self._b.Eval(df)
    return getattr(x, self._oper)(y)

  def Expr(self):
    print '(%s) %s (%s)' % (self._a.Expr(), OPERS[self._oper], self._b.Expr())


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