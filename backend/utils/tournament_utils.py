import random
from rest_framework.exceptions import ValidationError

def process_end_match(tournament, user_a, user_b, num_goals_scored, num_goals_against):
    if num_goals_scored > num_goals_against:
        loser = user_b
    elif num_goals_against > num_goals_scored:
        loser = user_a
    else:
        loser = random.choice([user_a, user_b])

    if loser in tournament.players:
        tournament.players.remove(loser)

    tournament.current_order_round += 1

    if tournament.current_order_round > tournament.total_order_round:
        tournament.current_order_round = 1
        tournament.current_round += 1
        tournament.total_order_round = len(tournament.players) // 2

    tournament.save()

    return tournament