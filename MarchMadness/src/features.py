import pandas as pd
from sqlalchemy import text

from utils import get_connection, get_table, write_table

def calculate_wins_per_team_per_season():
    """Calculate wins per season per team"""
    df_regular_season = get_table("t_original_regular_season_compact_results")
    df_wins_per_team_per_seaons = df_regular_season.groupby(["Season","WTeamID"]).size().reset_index()
    df_wins_per_team_per_seaons.columns = ["Season", "TeamID", "Wins"]
    write_table(df_wins_per_team_per_seaons, "wins_per_team_per_season")

def calculate_losses_per_team_per_season():
    """Calculate losses per season per team"""
    df_regular_season = get_table("t_original_regular_season_compact_results")
    df_losses_per_team_per_season = df_regular_season.groupby(["Season","LTeamID"]).size().reset_index()
    df_losses_per_team_per_season.columns = ["Season", "TeamID", "Losses"]
    write_table(df_losses_per_team_per_season, "losses_per_team_per_season")