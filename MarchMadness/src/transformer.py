# TODO
# Based on the postgres tables, the following sklearn.Transformer shall be implemented:
# - wins/losses reg season (optinally by OT)
# - wins/losses historical NCAA (optinally by OT)
# - odd calculation (specify columns for $\alpha$ and $\beta$)

import os
os.chdir("/home/jovyan/work")

import pandas as pd
from sklearn.base import TransformerMixin

from src.utils import get_table


class WinLossTransformer(TransformerMixin):
    """TODO: Docstring here"""
    
    def __init__(self, team_id_a, team_id_b, split_by_ot=False):
        self.team_id_a = team_id_a
        self.team_id_b = team_id_b
        self.split_by_ot = split_by_ot
    
    def fit(self, X):
        # minor sanity checking
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Must pass a pandas DataFrame, got {}".format(type(X)))
        col_diff = set([self.team_id_a, self.team_id_b, "season"]) - set(X.columns)
        if len(col_diff) > 0:
            raise ValueError(
                "Specified columns can't be found in provided DataFrame: {}".format(col_diff))
        return self
    
    def transform(self, X):
        ### WINS ###
        if self.split_by_ot:
            df_wins = get_table("t_derived_wins_per_team_per_season_by_ot")
            win_cols = ["wins_no_ot", "wins_ot"]
        else:
            df_wins = get_table("t_derived_wins_per_team_per_season")
            win_cols = ["wins"]
        # merge team a
        df_merged_wins_a = pd.merge(
            X,
            df_wins,
            how="left",
            left_on=["season", self.team_id_a],
            right_on=["season", "team_id"],
        )[win_cols]
        # suffix to 'a' columns
        df_merged_wins_a.columns = map(lambda c: c + "_a", df_merged_wins_a.columns)
        # merge team b
        df_merged_wins_b = pd.merge(
            X,
            df_wins,
            how="left",
            left_on=["season", self.team_id_b],
            right_on=["season", "team_id"],
        )[win_cols]
        # suffix to 'b' columns
        df_merged_wins_b.columns = map(lambda c: c + "_b", df_merged_wins_b.columns)
        df_merged_wins = pd.merge(
            df_merged_wins_a,
            df_merged_wins_b,
            left_index=True,
            right_index=True,
        
        )
        df_final = pd.merge(
            X,
            df_merged_wins,
            left_index=True,
            right_index=True
        )
        
        ### LOSSES ###
        if self.split_by_ot:
            df_losses = get_table("t_derived_losses_per_team_per_season_by_ot")
            loss_cols = ["losses_no_ot", "losses_ot"]
        else:
            df_losses = get_table("t_derived_losses_per_team_per_season")
            loss_cols = ["losses"]
        # merge team a
        df_merged_losses_a = pd.merge(
            X,
            df_losses,
            how="left",
            left_on=["season", self.team_id_a],
            right_on=["season", "team_id"],
        )[loss_cols]
        # suffix to 'a' columns
        df_merged_losses_a.columns = map(lambda c: c + "_a", df_merged_losses_a.columns)
        # merge team b
        df_merged_losses_b = pd.merge(
            X,
            df_losses,
            how="left",
            left_on=["season", self.team_id_b],
            right_on=["season", "team_id"],
        )[loss_cols]
        # suffix to 'b' columns
        df_merged_losses_b.columns = map(lambda c: c + "_b", df_merged_losses_b.columns)
        df_merged_losses = pd.merge(
            df_merged_losses_a,
            df_merged_losses_b,
            left_index=True,
            right_index=True,
        
        )
        df_final_wins = pd.merge(
            X,
            df_merged_wins,
            left_index=True,
            right_index=True
        )
        df_final = pd.merge(
            df_final_wins,
            df_merged_losses,
            left_index=True,
            right_index=True,
        )
        
        return df_final