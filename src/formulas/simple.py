from lib.expression import *

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