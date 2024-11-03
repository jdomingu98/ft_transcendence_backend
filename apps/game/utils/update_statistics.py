from ..models import Statistics, LocalMatch

def calculate_win_or_lose_match(user_statistics, match):
    if(match.num_goals_scored > match.num_goals_against):
        user_statistics.num_matches_won += 1
    if(match.num_goals_scored < match.num_goals_against):
        user_statistics.num_matches_defeat += 1

def calculate_max_streak(user_statistics, match):
    current_streak = user_statistics.max_streak
    if(match.num_goals_scored > match.num_goals_against):
        current_streak += 1
    else:
        current_streak = 0
    return current_streak

def calculate_win_rate(user_statistics, match):
    num_matches = user_statistics.num_matches
    num_victories = user_statistics.num_matches_won
    num_defeat = user_statistics.num_matches_defeat
    if(num_matches == 0):
        win_rate = 100
    elif num_victories + num_defeat == 0:
        win_rate = 100
    else:
        win_rate = (num_victories / (num_victories + num_defeat)) * 100
    return win_rate
    
def calculate_punctuation(user_statistics, match):
    if match.num_goals_scored > match.num_goals_against:
        user_statistics.punctuation += 10
    elif match.num_goals_scored < match.num_goals_against:
        user_statistics.punctuation -= 5
    user_statistics.punctuation = max(user_statistics.punctuation, 0)


def update_statistics(user, match):
    statistics = Statistics.objects.get(user=user)

    calculate_win_or_lose_match(statistics, match)
    statistics.num_matches += 1
    statistics.max_streak = calculate_max_streak(statistics, match)

    calculate_punctuation(statistics, match)
    statistics.win_rate = calculate_win_rate(statistics, match)

    statistics.num_goals_scored += match.num_goals_scored
    statistics.num_goals_against += match.num_goals_against
    statistics.num_goals_stopped += match.num_goals_stopped_a

    statistics.time_played += match.time_played
    
    statistics.save()