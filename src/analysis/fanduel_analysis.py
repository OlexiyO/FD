from analysis import knapsack
from analysis.player_info import Position


def Emulate(fd_data, player_predictions, player_results,
            requests=Position.FD_REQUEST, salary_cap=60000):
  """

  Args:
    fd_data: [PlayerInfo]
    predictions: dict(player_id --> number)
    results: dict(player_id --> number)

  Returns:
    How many points would've been scored.
  """
  updated_data = [
    pi.Override(pts=player_predictions.get(pi.pid, 0))
    for pi in fd_data]
  best = knapsack.BestChoice(updated_data, requests, salary_cap)
  return sum(player_results.get(pi.pid, 0) for pi in best)


# TODO: Write code which reads all FD files, and runs predictions on them.
# TODO: Create several ASTs, and try to see how big are wins.
# TODO: Check how rest affects performance.
