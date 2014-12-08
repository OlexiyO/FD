import itertools


def PrintData(*args, **kwargs):
  topn = kwargs.pop('topn', 20)
  assert not kwargs
  if topn > 0:
    a = 0
    b = topn
  else:
    a = len(args[0]) + topn  # topn is negative
    b = None
  if len(args) < 1:
    for v in itertools.islice(args[0], a, b):
      print v
  else:
    data = [[] for _ in args]

    for i, val in enumerate(itertools.islice(itertools.izip(*args), a, b)):
      for j, x in enumerate(val):
        data[j].append(str(x))
    for i, col in enumerate(data):
      maxw = max(len(s) for s in col)
      data[i] = [s.ljust(maxw) for s in col]
    for vals in itertools.izip(*data):
      print '\t'.join('%s' % s for s in vals)

