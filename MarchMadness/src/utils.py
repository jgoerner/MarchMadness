from itertools import combinations
import warnings

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import beta
from sqlalchemy import create_engine, text


def get_connection():
    """Returns a database engine to connect to postgres"""
    engine = create_engine("postgres://postgres@postgres_container:5432")
    return engine

def table_exists(t_name):
    """Check if a given table already exists in the database"""
    query = text('SELECT * FROM pg_catalog.pg_tables WHERE tablename=:table')
    return pd.read_sql(query, con=get_connection(), params={'table': t_name}).shape[0] > 0

def get_table(t_name):
    """Return the requested table as a pandas DataFrame"""
    if not table_exists(t_name):
        return None
    else:
        table = pd.read_sql("SELECT * FROM {table}".format(table=t_name), con=get_connection())
    return table

def write_table(dataframe, t_name, prefix="t_derived_"):
    """Write a dataframe to the database"""
    t_name_composed = prefix + t_name
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Must pass a DataFrame!")
    if table_exists(t_name_composed):
        raise ValueError("Table {} already exists".format(t_name_composed))
    else:
        dataframe.to_sql(t_name_composed, con=get_connection(), index=False)
    return t_name_composed

def enumerate_matches(df_teams):
    """Calculate all match combinations"""
    # check if dataframe
    if not isinstance(df_teams, pd.DataFrame):
        raise ValueError("Must specify a pandas DataFrame object, got {}".format(type(df_teams)))
        
    # check has team_id
    if not "team_id" in df_teams.columns:
        raise ValueError("Dataframe lacks the column 'team_id'")
    
    # get combination of teams
    idx = np.array(list(combinations(range(df_teams.shape[0]), 2)))
    
    # extract relevant slices
    df_tmp_a = df_teams.loc[idx.T[0],:].reset_index().drop("index", axis=1)
    df_tmp_b = df_teams.loc[idx.T[1],:].reset_index().drop("index", axis=1)

    # combine
    df_result = pd.merge(df_tmp_a, df_tmp_b, right_index=True, left_index=True, suffixes=('_a', '_b'))
    return df_result

def calc_odds(df_teams, N_SAMPLE=1000, N_EXPERIMENT=1000):
    """Calculate the odds between two competing teams"""
    # check if dataframe
    if not isinstance(df_teams, pd.DataFrame):
        raise ValueError("Must specify a pandas DataFrame object, got {}".format(type(df_teams)))

    # check columns wins_x and losses_x are given 
    if not set(["wins_a", "losses_a", "wins_b", "losses_b"]).issubset(set(df_teams.columns)):
        raise ValueError("Need to provide the columns 'wins_a', 'losses_a', 'wins_b', 'losses_b'")

    # check N_SAMPLE x N_EXPERIMENT not too large
    if N_SAMPLE*N_EXPERIMENT > 1000*1000:
        warnings.warn(
            "Running {} experiments with {} samples is quite a lot, dead kernel ahead...".format(N_EXPERIMENT,N_SAMPLE),
            RuntimeWarning
        )
        
    odds = np.zeros(df_teams.shape[0])
    for idx, row in df_teams.iterrows():
        beta_team_a = beta(row["wins_a"], row["losses_a"])
        beta_team_b = beta(row["wins_b"], row["losses_b"])
        
        sample_a = beta_team_a.rvs((N_SAMPLE, N_EXPERIMENT)) 
        sample_b = beta_team_b.rvs((N_SAMPLE, N_EXPERIMENT))
        sample_odds = (np.sum(sample_a > sample_b, axis=0) / N_SAMPLE)
        
        odds[idx] = np.mean(sample_odds)
        
    df_result = df_teams.copy()
    df_result["odds_a"] = odds
    return df_result

def plot_odds(df_row):
    # check if dataframe
    if not isinstance(df_row, pd.Series):
        raise ValueError("Must specify a pandas Series object, got {}".format(type(df_row)))    
    
    # check contains necessary cols
    if not set(
        ["team_id_a", "team_id_b", "wins_a", "losses_a", "wins_b", "losses_b", "odds_a"]).issubset(set(df_row.index)):
        raise ValueError(
            "Need to provide the columns 'team_id_a', 'team_id_b',wins_a', 'losses_a', 'wins_b', 'losses_b', 'odds_a'")
    
    # generate data
    x = np.linspace(0, 1, 100)
    beta_a = beta(df_row["wins_a"], df_row["losses_a"]).pdf(x)
    beta_b = beta(df_row["wins_b"], df_row["losses_b"]).pdf(x)
    # plot data
    plt.plot(x, beta_a, label=int(df_row["team_id_a"]))
    plt.plot(x, beta_b, label=int(df_row["team_id_b"]))
    plt.legend(loc=0)
    plt.title(
        "{} vs. {}\nP(Winner = {}) ~ {}%".format(
            int(df_row["team_id_a"]),
            int(df_row["team_id_b"]),
            int(df_row["team_id_a"]),
            np.round(df_row["odds_a"]*100, 4)
        ))