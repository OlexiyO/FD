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
  def __str__(self):
    return self.Expr()

  def __repr__(self):
    return self.Expr()

  def Expr(self):
    raise NotImplementedError

  def Eval(self, df):
    raise NotImplementedError

  def Filter(self, df):
    return df[~self.Eval(df).isnull()]

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

  def __ror__(self, other):
    return BinaryDFMethod('fillna', other, self)

  def __invert__(self):
    return Func(lambda x: pd.Series(1., index=x.index)[x.isnull()],
                lambda x: '~%s' % x,
                self)

  def __rand__(self, other):
    return Func(lambda x, y: x[~y.isnull()],
                lambda x, y: '%s & %s' % (x, y),
                other, self)

  def __and__(self, other):
    return Func(lambda x, y: x[~y.isnull()],
                lambda x, y: '%s & %s' % (x, y),
                self, other)

  def __eq__(self, other):
    return Func(lambda x, y: pd.Series(1., index=x.index)[x == y],
                lambda x, y: '%s == %s' % (x, y),
                self, other)

  def __gt__(self, other):
    return Func(lambda x, y: pd.Series(1., index=x.index)[x > y],
                lambda x, y: '%s > %s' % (x, y),
                self, other)

  def __ge__(self, other):
    return Func(lambda x, y: pd.Series(1., index=x.index)[x >= y],
                lambda x, y: '%s >= %s' % (x, y),
                self, other)

  def __le__(self, other):
    return Func(lambda x, y: pd.Series(1., index=x.index)[x <= y],
                lambda x, y: '%s <= %s' % (x, y),
                self, other)

  def __lt__(self, other):
    return Func(lambda x, y: pd.Series(1., index=x.index)[x < y],
                lambda x, y: '%s < %s' % (x, y),
                self, other)

  def __ne__(self, other):
    return Func(lambda x, y: pd.Series(1., index=x.index)[x != y],
                lambda x, y: '%s != %s' % (x, y),
                self, other)


def CreateConst(x):
  return x if isinstance(x, AbstractExpression) else Const(x)


class Func(AbstractExpression):
  def __init__(self, func, printout, *args):
    self._func = func
    self._printout = printout
    self._args = [CreateConst(a) for a in args]

  def Eval(self, df):
    evaled_args = [a.Eval(df) for a in self._args]
    return self._func(*evaled_args).reindex(evaled_args[0].index)

  def Expr(self):
    return '(%s)' % self._printout(*[a.Expr() for a in self._args])


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
    return '(%s %s %s)' % (self._a.Expr(), OPERS[self._oper], self._b.Expr())


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
    return '%s' % self._value

  def Eval(self, df):
    return pd.Series(self._value, index=df.index)


def LeafOrExpr(x):
  if isinstance(x, AbstractExpression):
    return x
  if not isinstance(x, basestring):
    raise TypeError('%s %s' % (type(x), x))
  return Leaf(x)