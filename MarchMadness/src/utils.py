from itertools import combinations
import warnings

import numpy as np
import pandas as pd
from scipy.stats import beta
from sklearn.metrics import log_loss
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
    # df_teams.reset_index(inplace=True) # to be implemented
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

def sample_submission_to_df(df_submission):
    """Declutter the submission file's id"""
    # check is df
    if not isinstance(df_submission, pd.DataFrame):
        raise ValueError("Must pass a pandas DatFrame, got {}".format(type(df_submission)))
    # check has cols
    if not "id" in df_submission.columns:
        raise ValueError("DataFrame must contain an 'id' column")

    # build the dataframe
    df_result = pd.DataFrame()
    df_result["season"] = df_submission["id"].apply(lambda item: item[:4])
    df_result["team_id_a"] = df_submission["id"].apply(lambda item: item[5:9])
    df_result["team_id_b"] = df_submission["id"].apply(lambda item: item[10:])
    
    # conver to numerical colums types
    df_result = df_result.apply(pd.to_numeric)
    return df_result

def build_surrogate_keys(df, team_cols):
    """Concat season team id A (lower) and team id B (upper)"""
    # check df
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Must pass a pandas DataFrame, got {}".format(type(df)))
    # check df contains 'seasons'
    if not "season" in df.columns:
        raise ValueError("DataFrame must have a 'season' column")
    # check len(team_cols) == 2
    if len(team_cols) != 2:
        raise ValueError("Specify exactly 2 team columns, got {}".format(len(team_cols)))
    # check cols in df
    if not set(team_cols).issubset(df.columns):
        raise ValueError("Team columns must be present in df columns")
    df_result = df.copy()
    key = \
        df["season"].astype(str)\
        + "_" + df[team_cols].min(axis=1).astype(str)\
        + "_" + df[team_cols].max(axis=1).astype(str)
    df_result["surrogate_key"] = key
    return df_result

def evaluate_log_loss(preds):
    """Evaluate log loss, given that all true labels are 1"""
    # check that preds are series
    if not isinstance (preds, pd.Series):
        raise ValueError("Must pass a pandas Series, got {}".format(type(preds)))
    true_labels = np.ones(len(preds))
    ll = log_loss(true_labels, preds, labels=[1, 0])
    return ll