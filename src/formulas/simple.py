from analysis.expression import *

expr1 = Leaf('fantasy_pts_per_game')
old_tempo = Leaf('team_poss_per_game')
predicted_tempo = (Leaf('team_poss_per_game') + Leaf('other_poss_per_game')) / 2.
tempo_mult = predicted_tempo / old_tempo
expr2 = expr1 * tempo_mult