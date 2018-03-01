from features import (
    calculate_wins_per_team_per_season, 
    calculate_losses_per_team_per_season,
    calculate_mean_score_per_team_per_season,
    calculate_seed_rank_per_team_per_season,
)

def derive_features():
    # Define features to be derived as (name, function)
    features = [
        ("wins per team per season", calculate_wins_per_team_per_season),
        ("losses per team per season", calculate_losses_per_team_per_season),
        ("mean score per team per season", calculate_mean_score_per_team_per_season),
        ("seed rank per team per season", calculate_seed_rank_per_team_per_season),
    ]
    
    print("\n" + "/"*112)
    print("/" + " "*41 + "Deriving Univariate Features" + " "*41 + "/")
    print("/"*112 + "\n\n")
    
    for (f_name, f_func) in features:
        print("#"*(len(f_name)+13))
        print("# Deriving {} #".format(f_name))
        print("#"*(len(f_name)+13))
        try:
            t_name = f_func()
            print("Created\n\n")
        except ValueError as e:
            print(e, end="\n\n")

if __name__ == "__main__":
    derive_features()