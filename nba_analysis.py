# Import Pandas
import pandas as pd
# Import NumPy
import numpy as np
# Import matplotlib
import matplotlib.pyplot as plt

# Import data from 'Player Game Data.csv' as player_game_data_df
player_game_data_df = pd.read_csv("NBA Data/Player Game Data.csv")

# # Descriptive statistics for player_game_data_df
# # Update Pandas settings to show all columns
# pd.set_option('display.max_columns', None)
# ## Use '.shape' to print the number of rows and columns in player_game_data_df
# print(player_game_data_df.shape)
# ## Use '.head()' to print the first 5 rows of player_game_data_df
# print(player_game_data_df.head())
# ## Use '.tail()' to print the last 5 rows of player_game_data_df
# print(player_game_data_df.tail())
# ## Use '.dtypes' to print the data types of each column
# print(player_game_data_df.dtypes)
# ## Use '.describe()' to print the descriptive statistics for each numerical column
# print(player_game_data_df.describe())

# Import data from 'Team Games Played.csv' as team_games_played_df
team_games_played_df = pd.read_csv("NBA Data/Team Games Played.csv")

"""
Q1. Find the highest scoring player on each team
- Highest scoring = highest average points per game
- Final dataframe should include 30 rows (1 row per team), sorted in descending order by avg_ppg

Q2. Find the highest scoring player on each team that played at least half the team's games
"""

# Make a copy of player_game_data_df
top_scorer_per_team_df = player_game_data_df.copy()

# Merge top_scorer_per_team_df with team_games_played_df
top_scorer_per_team_df = pd.merge(
    top_scorer_per_team_df,
    team_games_played_df,
    how = "left",
    on = "TEAM_ID",
)

# Create a new column called "player_game_count" that counts the number of games each player played
top_scorer_per_team_df["player_game_count"] = top_scorer_per_team_df.groupby(
    ["PLAYER_ID"]
)["PLAYER_ID"].transform("count")

# Create a new column called "player_game_percentage" that calculates the percentage of a team's
# games a player played in
top_scorer_per_team_df["player_game_percentage"] = (
    top_scorer_per_team_df["player_game_count"] / top_scorer_per_team_df["team_game_count"]
)

# Filter out players that played in less than half the team's games
## Define a games_played_cutoff variable that stores the cutoff value
games_played_cutoff = .9
top_scorer_per_team_df = top_scorer_per_team_df[
    top_scorer_per_team_df["player_game_percentage"] > games_played_cutoff
]

# Calculate the average points per game for each player
## Grouping variable: 'PLAYER_ID'
## Computation variable: 'PTS'
## Transformation: 'mean'
top_scorer_per_team_df["avg_ppg"] = top_scorer_per_team_df.groupby(
    ["PLAYER_ID"]
)["PTS"].transform("mean")
# Round avg_ppg to 1 decimal place
top_scorer_per_team_df["avg_ppg"] = top_scorer_per_team_df["avg_ppg"].round(1)

# Remove duplicate rows in dataframe to only include one row per player
## Need to filter before we rank or else it will count each player multiple times
top_scorer_per_team_df = top_scorer_per_team_df.drop_duplicates(subset = ["PLAYER_ID"])

# Rank players on each team by avg_ppg
top_scorer_per_team_df["team_avg_ppg_ranking"] = top_scorer_per_team_df.groupby(
    ["TEAM_ID"]
)["avg_ppg"].rank(ascending = False)

# Filter the dataframe to only include the top players on each team
## Filter: "team_avg_ppg_ranking" == 1
top_scorer_per_team_df = top_scorer_per_team_df[
    top_scorer_per_team_df["team_avg_ppg_ranking"] == 1
]

# Sort players by avg_ppg
top_scorer_per_team_df = top_scorer_per_team_df.sort_values(by = ["avg_ppg"], ascending = False)

# Specify the columns we want to include in the final dataframe
top_scorer_columns = [
    "PLAYER_ID",
    "PLAYER_NAME",
    "TEAM_ID",
    "TEAM_ABBREVIATION",
    "TEAM_NAME",
    "avg_ppg",
    # Add player_game_count and player_game_percentage
]
top_scorer_per_team_df = top_scorer_per_team_df[top_scorer_columns]

# Save the dataframe
top_scorer_per_team_df.to_csv("Top Scorers Per Team.csv", index = False)

"""
Q3. Create an algorithm to find the MVP of the 2019 regular season

MVP algorithm:
-> Pct of team's points
-> + Pct of team's assists
-> + Pct of team's rebounds
-> +/- win bonus (+.25 for win, -.25 for loss)
"""

# Make a copy of player_game_data_df and name it 'mvp_rankings_df'
mvp_rankings_df = player_game_data_df.copy()

# Calculate each player's share of points, assists, and rebounds for the season

# # Method 1. Do it manually
# Calculate the total team points, assists, and rebounds in each game
mvp_rankings_df["team_PTS"] = mvp_rankings_df.groupby(
    ["TEAM_ID", "GAME_ID"]
)["PTS"].transform("sum")

mvp_rankings_df["team_AST"] = mvp_rankings_df.groupby(
    ["TEAM_ID", "GAME_ID"]
)["AST"].transform("sum")

mvp_rankings_df["team_REB"] = mvp_rankings_df.groupby(
    ["TEAM_ID", "GAME_ID"]
)["REB"].transform("sum")

## Calculate the share of points, assists, and rebounds each player is responsible for
mvp_rankings_df["share_of_team_PTS"] = mvp_rankings_df["PTS"] / mvp_rankings_df["team_PTS"]
mvp_rankings_df["share_of_team_AST"] = mvp_rankings_df["AST"] / mvp_rankings_df["team_AST"]
mvp_rankings_df["share_of_team_REB"] = mvp_rankings_df["REB"] / mvp_rankings_df["team_REB"]

## Calculate each player's avg share of points, assists, and rebounds for the season
mvp_rankings_df["season_avg_share_of_PTS"] = mvp_rankings_df.groupby(["PLAYER_ID"])["share_of_team_PTS"].transform("mean").round(1)
mvp_rankings_df["season_avg_share_of_AST"] = mvp_rankings_df.groupby(["PLAYER_ID"])["share_of_team_AST"].transform("mean").round(1)
mvp_rankings_df["season_avg_share_of_REB"] = mvp_rankings_df.groupby(["PLAYER_ID"])["share_of_team_REB"].transform("mean").round(1)

## Calculate each player's total share of points, assists, and rebounds for the season
mvp_rankings_df["season_share_of_PTS"] = mvp_rankings_df.groupby(["PLAYER_ID"])["share_of_team_PTS"].transform("sum")
mvp_rankings_df["season_share_of_AST"] = mvp_rankings_df.groupby(["PLAYER_ID"])["share_of_team_AST"].transform("sum")
mvp_rankings_df["season_share_of_REB"] = mvp_rankings_df.groupby(["PLAYER_ID"])["share_of_team_REB"].transform("sum")

## Calculate each player's average points, assists, and rebounds for the season
mvp_rankings_df["season_avg_PTS"] = mvp_rankings_df.groupby(["PLAYER_ID"])["PTS"].transform("mean")
mvp_rankings_df["season_avg_AST"] = mvp_rankings_df.groupby(["PLAYER_ID"])["AST"].transform("mean")
mvp_rankings_df["season_avg_REB"] = mvp_rankings_df.groupby(["PLAYER_ID"])["REB"].transform("mean")

# Method 2. List + For Loop
# Define a list with the columns we want to calculate each player's share of in each game
share_columns = [
    "PTS",
    "AST",
    "REB",
]

# Loop through each column in share_columns
for column in share_columns:
    # Calculate the total team points, assists, and rebounds in each game
    mvp_rankings_df["team_" + column] = mvp_rankings_df.groupby(
        ["TEAM_ID", "GAME_ID"]
    )[column].transform("sum")

    # Calculate the share of points, assists, and rebounds each player is responsible for
    mvp_rankings_df["share_of_team_" + column] = (
        mvp_rankings_df[column] / mvp_rankings_df["team_" + column]
    )
    
    # Calculate each player's avg share of points, assists, and rebounds for the season
    mvp_rankings_df["season_avg_share_of_" + column] = mvp_rankings_df.groupby(
        ["PLAYER_ID"]
    )["share_of_team_" + column].transform("mean").round(2)

    # Calculate each player's total share of points, assists, and rebounds for the season
    mvp_rankings_df["season_total_share_of_" + column] = mvp_rankings_df.groupby(
        ["PLAYER_ID"]
    )["share_of_team_" + column].transform("sum").round(1)

    # Calculate each player's average points, assists, and rebounds for the season
    mvp_rankings_df["season_avg_" + column] = mvp_rankings_df.groupby(
        ["PLAYER_ID"]
    )[column].transform("mean").round(1)

# Calculate the player's win bonus for each game (+.25 for win, -.25 for loss)
# Method 1. Lambda Function
## Create a variable named win_bonus equal to .25
win_bonus = .25

## Define a method that returns the win_bonus if the team won or -win_bonus if the team lost
def calculate_win_bonus(game_result, win_bonus):
    if game_result == "W":
        return win_bonus
    elif game_result == "L":
        return -win_bonus

# Calculate the win_bonus for each row
mvp_rankings_df["win_bonus"] = mvp_rankings_df["WL"].apply(
    lambda x: calculate_win_bonus(x, win_bonus)
)

# Method 2. NumPy
## Import NumPy at the top of the file
mvp_rankings_df["win_bonus"] = np.where(
    mvp_rankings_df["WL"] == "W",
    win_bonus,
    -win_bonus,
)

# Calculate the 'game_mvp_score' for each player in each game by adding
# 'pct_of_team_points', 'pct_of_team_assists', 'pct_of_team_rebounds', and 'win_bonus'
mvp_rankings_df["game_mvp_score"] = (
    mvp_rankings_df["share_of_team_PTS"]
    + mvp_rankings_df["share_of_team_AST"]
    + mvp_rankings_df["share_of_team_REB"]
    + mvp_rankings_df["win_bonus"]
)

# Calculate the player's total win bonus for the season
mvp_rankings_df["season_win_bonus"] = mvp_rankings_df.groupby(
    ["PLAYER_ID"]
)["win_bonus"].transform("sum")

# Calculate the 'season_mvp_score' for each player
mvp_rankings_df["season_mvp_score"] = mvp_rankings_df.groupby(
    ["PLAYER_ID"]
)["game_mvp_score"].transform("sum")

# Deduplicate mvp_rankings_df to only include 1 row per player
deduplicated_mvp_rankings_df = mvp_rankings_df.drop_duplicates(subset = ["PLAYER_ID"])

# Rank players by 'season_mvp_score'
deduplicated_mvp_rankings_df["season_mvp_ranking"] = deduplicated_mvp_rankings_df["season_mvp_score"].rank(ascending = False)

# Sort dataframe by season_mvp_ranking
deduplicated_mvp_rankings_df = deduplicated_mvp_rankings_df.sort_values(by = ["season_mvp_ranking"])

# Specify the columns we'd like to keep in deduplicated_mvp_rankings_df
mvp_columns = [
    "TEAM_ID",
    "TEAM_NAME",
    "PLAYER_ID",
    "PLAYER_NAME",
    "season_avg_PTS",
    "season_avg_AST",
    "season_avg_REB",
    "season_avg_share_of_PTS",
    "season_avg_share_of_AST",
    "season_avg_share_of_REB",
    "season_total_share_of_PTS",
    "season_total_share_of_AST",
    "season_total_share_of_REB",
    "season_win_bonus",
    "season_mvp_score",
    "season_mvp_ranking",
]
deduplicated_mvp_rankings_df = deduplicated_mvp_rankings_df[mvp_columns]

# Save deduplicated_mvp_rankings_df to a csv as 'MVP Rankings.csv'
deduplicated_mvp_rankings_df.to_csv("MVP Rankings.csv", index = False)

"""
Q4. Create visualizations for the following:
-> Create a bar chart showing the season_mvp_score for the top 10 MVP candidates
-> Make a scatterplot to demonstrate the relationship between our season_mvp_score and
average points per game
-> Make a histogram to show the distribution of game_mvp_score scored for the player you
would vote for MVP
"""
# Create a bar chart showing the season_mvp_score for the top 10 MVP candidates
# Create a copy of mvp_rankings_df that only includes the top 10 MVP candidates
top_mvp_rankings_df = deduplicated_mvp_rankings_df.copy()

mvp_cutoff = 10
top_mvp_rankings_df = top_mvp_rankings_df[top_mvp_rankings_df["season_mvp_ranking"] <= mvp_cutoff]

# Create the bar chart
top_mvp_rankings_df.plot.bar(x = "PLAYER_NAME", y = "season_mvp_score")

# Make a scatterplot to demonstrate the relationship between our season_mvp_score and
# season_avg_PTS
mvp_scatter_data_df = deduplicated_mvp_rankings_df.copy()

mvp_scatter_data_df.plot.scatter(x = "season_avg_PTS", y = "season_mvp_score")

# Make a histogram to show the distribution of game_mvp_score scored for the player you
# would vote for MVP
# Find the PLAYER_ID value for the player our algorithm believes should be the mvp
mvp_player_id = deduplicated_mvp_rankings_df.loc[
    deduplicated_mvp_rankings_df["season_mvp_ranking"] == 1,
    "PLAYER_ID",
].values[0]

# Make a copy of the mvp_rankings_df
mvp_hist_data_df = mvp_rankings_df.copy()

# Filter mvp_hist_data_df on the MVP
mvp_hist_data_df = mvp_hist_data_df[mvp_hist_data_df["PLAYER_ID"] == mvp_player_id]

# Create a histogram for the game_mvp_score values
mvp_hist_data_df.hist(column = "game_mvp_score")

# Display all charts
plt.show()