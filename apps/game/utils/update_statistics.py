from ..models import Statistics
from ..models import LocalMatch


def update_statistics(statistics: Statistics, match: LocalMatch):
    statistics.num_matches += 1
    statistics.num_goals_scored += match.num_goals_scored
    statistics.num_goals_against += match.num_goals_against
    statistics.num_goals_stopped += match.num_goals_stopped_a
    statistics.time_played += match.time_played

    if is_win(match):
        statistics.num_matches_won += 1
        statistics.current_streak += 1
        statistics.punctuation += 10
        statistics.max_streak = max(statistics.max_streak, statistics.current_streak)
    else:
        statistics.current_streak = 0
        statistics.punctuation = max(statistics.punctuation - 5, 0)

    statistics.win_rate = statistics.num_matches_won / statistics.num_matches * 100 if statistics.num_matches > 0 else 100
    statistics.save()


def is_win(match):
    return match.num_goals_scored > match.num_goals_against
