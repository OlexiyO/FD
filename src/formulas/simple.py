from lib import expression

from lib.expression import *


E = expression.EOperators
from analysis import training


golden = Leaf('fantasy_pts')
expr1 = Leaf('fantasy_pts_per_game')
old_tempo = Leaf('team_poss_per_game')
predicted_tempo = (Leaf('team_poss_per_game') + Leaf('other_poss_per_game')) / 2.
tempo_mult = predicted_tempo / old_tempo
expr2 = expr1 * tempo_mult

rest_adjust = (-.3 & (Leaf('player_rest') == 1)) | 0.
expr3 = expr1 + rest_adjust
expr4 = expr2 + rest_adjust

# Coaches trust good players more with no rest!!
# rest_adjust_for_good = 1. & (Leaf('player_rest') == 1) & (Leaf('player_previous_minutes') > 30)
#expr5 = expr4 + rest_adjust_for_good
expr6 = expr4 + ((.5 & Leaf('is_home')) | 0.)

home_adjust_big = (1. & (Leaf('minutes_per_game') > 25) & Leaf('is_home'))
home_adjust_small = (.5 & Leaf('is_home'))
expr7 = expr4 + (home_adjust_big | home_adjust_small | 0)

off_part = Leaf('pts_per_game') + 1.5 * Leaf('ast_per_game')
off_part *= Leaf('other_def_rating_per_game') / 1.041
other_part = 1.2 * Leaf('trb_per_game')
other_part += 2. * (Leaf('blk_per_game') + Leaf('stl_per_game'))
other_part -= Leaf('tov_per_game')
cumulative_score = (off_part + other_part) * tempo_mult
cumulative_score_with_home = cumulative_score + ((.5 & Leaf('is_home')) | 0.)

import numpy as np

extra0 = training.BuildPWL(E.Log(tempo_mult), [(-0.03, 0.96), (0.05, 1.019)])
extra1 = training.BuildPWL(Leaf('other_def_rating_per_game'), [(0.95, 1.), (1.12, 1.13)])

log = np.log
extra0a = E.Exp(training.BuildPWL(E.Log(tempo_mult),
                                  [(-0.03, log(0.96)), (0.05, log(1.019))]))
extra1a = E.Exp(training.BuildPWL(E.Log(Leaf('other_def_rating_per_game')),
                                  [(log(0.95), log(1.)), (log(1.12), log(1.13))]))
scoring = extra0a * extra1a * Leaf('fantasy_pts_per_game')

mpg_adjust = (Leaf('minutes_mean_last_5') | Leaf('minutes_per_game') | 10.) / (Leaf('minutes_per_game') | 10.)
with_mpg_adjust = Leaf('fantasy_pts_per_game') * mpg_adjust

# mpg_mix = Leaf('fantasy_pts_per_game') * mpg_adjust +
