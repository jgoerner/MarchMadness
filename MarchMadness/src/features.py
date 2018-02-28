import pandas as pd
from sqlalchemy import text

from utils import get_connection, get_table, write_table

def calculate_wins_per_team_per_season():
    """Get wins per season per team"""
    # get the source table
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
    # get source table
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