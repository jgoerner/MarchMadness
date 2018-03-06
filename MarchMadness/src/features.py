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


def calculate_ncaa_wins_per_team():
    """Get all NCAA wins per team"""
    df_ncaa = get_table("t_original_ncaa_tourney_compact_results")
    df_ncaa_wins_per_team = df_ncaa.groupby("w_team_id").size().reset_index()
    df_ncaa_wins_per_team.columns = ["team_id", "wins"]
    write_table(df_ncaa_wins_per_team, "ncaa_wins_per_team")


def calculate_ncaa_losses_per_team():
    """Get all NCAA wins per team"""
    df_ncaa = get_table("t_original_ncaa_tourney_compact_results")
    df_ncaa_losses_per_team = df_ncaa.groupby("l_team_id").size().reset_index()
    df_ncaa_losses_per_team.columns = ["team_id", "losses"]
    write_table(df_ncaa_losses_per_team, "ncaa_losses_per_team")


def calculate_wins_per_team_per_season_by_ot():
    """Get regular season wins split (binary) by OT"""
    df_regular_season = get_table("t_original_regular_season_compact_results")
    
    # Aggregate
    df_wins_per_team_per_seaons_no_ot = \
    df_regular_season[df_regular_season["num_ot"] == 0]\
    .groupby(["season","w_team_id"]).size().reset_index()
    
    # Cosmetics
    df_wins_per_team_per_seaons_no_ot.rename(columns={"w_team_id":"team_id", 0:"wins_no_ot"}, inplace=True) 
    
    # Aggregate
    df_wins_per_team_per_seaons_ot = \
    df_regular_season[df_regular_season["num_ot"] > 0]\
    .groupby(["season","w_team_id"]).size().reset_index()
    
    # cosmetics
    df_wins_per_team_per_seaons_ot.rename(columns={"w_team_id":"team_id", 0:"wins_ot"}, inplace=True)

    # join outer(!) to include teams that never or only won via OT
    df_wins_per_team_per_seaons_by_ot = \
    pd.merge(
        df_wins_per_team_per_seaons_no_ot,
        df_wins_per_team_per_seaons_ot,
        on=["season", "team_id"],
        how="outer"
    )

    # cosmetics
    df_wins_per_team_per_seaons_by_ot.fillna(0, inplace=True)
    df_wins_per_team_per_seaons_by_ot["wins_ot"] = df_wins_per_team_per_seaons_by_ot["wins_ot"].astype(int)
    df_wins_per_team_per_seaons_by_ot["wins_no_ot"] = df_wins_per_team_per_seaons_by_ot["wins_no_ot"].astype(int)
    write_table(df_wins_per_team_per_seaons_by_ot, "wins_per_team_per_seaons_by_ot")


def calculate_losses_per_team_per_season_by_ot():
    df_regular_season = get_table("t_original_regular_season_compact_results")

    # Aggregate
    df_losses_per_team_per_seaons_no_ot = \
    df_regular_season[df_regular_season["num_ot"] == 0]\
    .groupby(["season","l_team_id"]).size().reset_index()

    # Cosmetics
    df_losses_per_team_per_seaons_no_ot.rename(columns={"l_team_id":"team_id", 0:"losses_no_ot"}, inplace=True) 

    # Aggregate
    df_losses_per_team_per_seaons_ot = \
    df_regular_season[df_regular_season["num_ot"] > 0]\
    .groupby(["season","l_team_id"]).size().reset_index()

    # cosmetics
    df_losses_per_team_per_seaons_ot.rename(columns={"l_team_id":"team_id", 0:"losses_ot"}, inplace=True)

    # join outer(!) to include teams that never or only won via OT
    df_losses_per_team_per_seaons_by_ot = \
    pd.merge(
        df_losses_per_team_per_seaons_no_ot,
        df_losses_per_team_per_seaons_ot,
        on=["season", "team_id"],
        how="outer"
    )

    # cosmetics
    df_losses_per_team_per_seaons_by_ot.fillna(0, inplace=True)
    df_losses_per_team_per_seaons_by_ot["losses_ot"] = df_losses_per_team_per_seaons_by_ot["losses_ot"].astype(int)
    df_losses_per_team_per_seaons_by_ot["losses_no_ot"] = df_losses_per_team_per_seaons_by_ot["losses_no_ot"].astype(int)
    write_table(df_losses_per_team_per_seaons_by_ot, "losses_per_team_per_seaons_by_ot")

def calculate_ncaa_wins_per_team_by_ot():
    df_ncaa = get_table("t_original_ncaa_tourney_compact_results")

    # Aggregate
    df_wins_per_team_historic_ncaa_no_ot =\
    df_ncaa[df_ncaa["num_ot"] == 0].groupby("w_team_id").size().reset_index()

    # Cosmetics
    df_wins_per_team_historic_ncaa_no_ot.rename(columns={"w_team_id":"team_id", 0:"wins_no_ot"}, inplace=True) 

    # Aggregate
    df_wins_per_team_historic_ncaa_ot =\
    df_ncaa[df_ncaa["num_ot"] > 0].groupby("w_team_id").size().reset_index()

    # cosmetics
    df_wins_per_team_historic_ncaa_ot.rename(columns={"w_team_id":"team_id", 0:"wins_ot"}, inplace=True)

    df_wins_per_team_historic_ncaa_by_ot = \
    pd.merge(
        df_wins_per_team_historic_ncaa_no_ot,
        df_wins_per_team_historic_ncaa_ot,
        on=["team_id"],
        how="outer"
    )

    # cosmetics
    df_wins_per_team_historic_ncaa_by_ot.fillna(0, inplace=True)
    df_wins_per_team_historic_ncaa_by_ot["wins_ot"] = df_wins_per_team_historic_ncaa_by_ot["wins_ot"].astype(int)
    df_wins_per_team_historic_ncaa_by_ot["wins_no_ot"] = df_wins_per_team_historic_ncaa_by_ot["wins_no_ot"].astype(int)
    write_table(df_wins_per_team_historic_ncaa_by_ot, "ncaa_wins_per_team_by_ot")

def calculate_ncaa_losses_per_team_by_ot():
    df_ncaa = get_table("t_original_ncaa_tourney_compact_results")

    # Aggregate
    df_losses_per_team_historic_ncaa_no_ot =\
    df_ncaa[df_ncaa["num_ot"] == 0].groupby("l_team_id").size().reset_index()

    # Cosmetics
    df_losses_per_team_historic_ncaa_no_ot.rename(columns={"l_team_id":"team_id", 0:"losses_no_ot"}, inplace=True) 

    # Aggregate
    df_losses_per_team_historic_ncaa_ot =\
    df_ncaa[df_ncaa["num_ot"] > 0].groupby("l_team_id").size().reset_index()

    # cosmetics
    df_losses_per_team_historic_ncaa_ot.rename(columns={"l_team_id":"team_id", 0:"losses_ot"}, inplace=True)

    df_losses_per_team_historic_ncaa_by_ot = \
    pd.merge(
        df_losses_per_team_historic_ncaa_no_ot,
        df_losses_per_team_historic_ncaa_ot,
        on=["team_id"],
        how="outer"
    )

    # cosmetics
    df_losses_per_team_historic_ncaa_by_ot.fillna(0, inplace=True)
    df_losses_per_team_historic_ncaa_by_ot["losses_ot"] = df_losses_per_team_historic_ncaa_by_ot["losses_ot"].astype(int)
    df_losses_per_team_historic_ncaa_by_ot["losses_no_ot"] = df_losses_per_team_historic_ncaa_by_ot["losses_no_ot"].astype(int)
    write_table(df_losses_per_team_historic_ncaa_by_ot, "ncaa_losses_per_team_by_ot")