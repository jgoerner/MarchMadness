import pandas as pd
from sqlalchemy import text

from utils import get_connection, get_table, write_table

def calculate_wins_per_team_per_season():
    """Get wins per season per team"""
    df_regular_season = get_table("t_original_regular_season_compact_results")
    df_wins_per_team_per_seaons = df_regular_season.groupby(["season","w_team_id"]).size().reset_index()
    df_wins_per_team_per_seaons.columns = ["season", "team_id", "wins"]
    write_table(df_wins_per_team_per_seaons, "wins_per_team_per_season")

def calculate_losses_per_team_per_season():
    """Get losses per season per team"""
    df_regular_season = get_table("t_original_regular_season_compact_results")
    df_losses_per_team_per_season = df_regular_season.groupby(["season","l_team_id"]).size().reset_index()
    df_losses_per_team_per_season.columns = ["season", "team_id", "losses"]
    write_table(df_losses_per_team_per_season, "losses_per_team_per_season")

def calculate_mean_score_per_team_per_season():
    """Get the average score per team per season"""
    pd = get_table("t_original_regular_season_compact_results")
    # cover case team == winner
    df_scores_winner = pd[["season", "w_team_id", "w_score"]]
    df_scores_winner.columns = ["season", "team_id", "score"]
    # cover case team == loser
    df_scores_looser = pd[["season", "l_team_id", "l_score"]]
    df_scores_looser.columns = ["season", "team_id", "score"]
    # combine winner & loser frames
    df_scores_teams = df_scores_winner.append(df_scores_looser)
    df_mean_scores_per_team_per_season = df_scores_teams.groupby(["season", "team_id"])["score"].mean().reset_index()
    df_mean_scores_per_team_per_season.columns = ["season", "team_id", "score_avg"]
    write_table(df_mean_scores_per_team_per_season, "mean_score_per_team_per_season")
    
def calculate_seed_rank_per_team_per_season():
    df_seed_rank_per_team_per_season = get_table("t_original_ncaa_tourney_seeds")
    # strip beginning region and optional "a/b" (which might be of interest later on)
    df_seed_rank_per_team_per_season["seed_rank"] = df_seed_rank_per_team_per_season["seed"].apply(
        lambda seed: int(seed[1:]) if len(seed) == 3 else int(seed[1:-1]))
    df_seed_rank_per_team_per_season.drop("seed", axis=1, inplace=True)
    write_table(df_seed_rank_per_team_per_season, "seed_rank_per_team_per_season")

def calculate_mean_stats_per_team_per_season():
    df_detailed_results = get_table("t_original_ncaa_tourney_detailed_results")
    df_results_winner = df_detailed_results[
        ['season',
         'w_team_id',
         'w_score',
         'wfgm',
         'wfga',
         'wfgm3',
         'wfga3',
         'wftm',
         'wfta',
         'wor',
         'wdr',
         'w_ast',
         'wto',
         'w_stl',
         'w_blk',
         'wpf']
    ]
    df_results_loser = df_detailed_results[
        ['season',
        'l_team_id',
        'l_score',
        'lfgm',
        'lfga',
        'lfgm3',
        'lfga3',
        'lftm',
        'lfta',
        'lor',
        'ldr',
        'l_ast',
        'lto',
        'l_stl',
        'l_blk',
        'lpf']
    ]
    df_results_winner.columns = map(lambda x: x.lstrip("w_"), df_results_winner.columns)
    df_results_loser.columns = map(lambda x: x.lstrip("l_"), df_results_loser.columns)
    df_mean_stats_per_team_per_season =\
        df_results_winner.append(df_results_loser).groupby(["season", "team_id"]).mean().reset_index()
    write_table(df_mean_stats_per_team_per_season, "mean_stats_per_team_per_season")