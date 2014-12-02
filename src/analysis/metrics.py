def L1(real_score, predicted_score):
  return (predicted_score - real_score).abs().mean()


def L1PreferUnderrated(real_score, predicted_score, underrated_penalty=.5):
  diff = (predicted_score - real_score).astype(float)
  diff.update(underrated_penalty * diff[diff < 0])
  return diff.abs().mean()
