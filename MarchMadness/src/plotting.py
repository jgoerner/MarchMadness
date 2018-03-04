from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import beta

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