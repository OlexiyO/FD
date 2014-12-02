from collections import namedtuple
import itertools


__all__ = ['Position', 'PlayerInfo', 'BestChoice']


class Position(object):
  PG = 'PG'
  SG = 'SG'
  SF = 'SF'
  PF = 'PF'
  C = 'C'


Position.ALL = [Position.C, Position.PF, Position.PG, Position.SF, Position.SG]

PlayerInfo = namedtuple('PlayerInfo', ['position', 'name', 'salary', 'pts'])


def BestChoice(players, per_position_counts, salary_cap):
  candidates = sorted(players)
  assert all(c.salary % 100 == 0 for c in candidates)
  request = sorted(itertools.chain(*(itertools.repeat(p, cnt) for p, cnt in per_position_counts.iteritems())))
  S = int(salary_cap / 100)
  C = len(candidates)
  N = len(request)
  memo = []
  for n in range(N + 1):
    memo.append([])
    for p in range(C + 1):
      memo[n].append([None] * (S + 1))

  BAD = -10000000.

  def GV(request_index, candidate_index, salary_left):
    if request_index == N:
      return 0
    if candidate_index >= C:
      return BAD
    if memo[request_index][candidate_index][salary_left] is not None:
      return memo[request_index][candidate_index][salary_left]
    c1 = candidates[candidate_index]
    sal1 = int((c1.salary + 99) / 100)
    skip_score = GV(request_index, candidate_index + 1, salary_left)
    if c1.position != request[request_index] or sal1 > salary_left:
      memo[request_index][candidate_index][salary_left] = skip_score
      return skip_score
    else:
      res = max(skip_score, c1.pts + GV(request_index + 1, candidate_index + 1, salary_left - sal1))
      memo[request_index][candidate_index][salary_left] = res
      return res

  best_pts = GV(0, 0, S)
  ans = []
  eps = 1e-5
  r, c, s = 0, 0, S
  while r < N:
    candidate = candidates[c]
    csal = int((candidate.salary + 99) / 100)
    if (csal <= s and
            candidate.position == request[r] and
              candidate.pts + GV(r + 1, c + 1, s - csal) > best_pts - eps):
      ans.append(candidate)
      best_pts -= candidate.pts
      r += 1
      s -= csal
      c += 1
    else:
      c += 1

  assert len(ans) == len(request)
  return ans