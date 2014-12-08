from analysis.expression import *

golden = Leaf('fantasy_pts')
expr1 = Leaf('fantasy_pts_per_game')
old_tempo = Leaf('team_poss_per_game')
predicted_tempo = (Leaf('team_poss_per_game') + Leaf('other_poss_per_game')) / 2.
tempo_mult = predicted_tempo / old_tempo
expr2 = expr1 * tempo_mult

rest_adjust = (-.3 & (Leaf('player_rest') == 1)) | 0.
expr3 = expr1 + rest_adjust
expr4 = expr2 + rest_adjust

rest_adjust_smart = ((-.3 &
                      (Leaf('player_rest') == 1)) &
                     (Leaf('player_previous_minutes') > 30.)) | 0.
expr5 = expr2 + rest_adjust_smart