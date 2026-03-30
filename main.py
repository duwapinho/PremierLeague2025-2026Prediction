import pandas as pd
import numpy as np


played =  pd.read_csv("data/EPL_clean.csv")  #Matches already played in season 25/26
future = pd.read_csv("data/remainingmatchesEPL.csv") #Matches that needs to be simulated

full = pd.concat([played,future], ignore_index=True)  #merging files


played_matches = full[full["FTHG"].notna()].copy()
future_matches = full[full["FTHG"].isna()].copy()  #creating data copy where we can separate played matches and future matches.

league_home_avg = played_matches["FTHG"].mean()
league_away_avg = played_matches["FTAG"].mean()

home_scored = played_matches.groupby("HomeTeam")["FTHG"].mean()
home_conceded = played_matches.groupby("HomeTeam")["FTAG"].mean()

away_scored = played_matches.groupby("AwayTeam")["FTAG"].mean()
away_conceded = played_matches.groupby("AwayTeam")["FTHG"].mean()


def get_strengths(team):
    attack_home = home_scored.get(team, league_home_avg) / league_home_avg
    defense_home = home_conceded.get(team, league_away_avg) / league_away_avg

    attack_away = away_scored.get(team, league_away_avg) / league_away_avg
    defense_away = away_conceded.get(team, league_home_avg) / league_home_avg

    return attack_home, defense_home, attack_away, defense_away     #Creating teams strength based on first 30 league games, separating away and home form.


def simulate_match(home, away):
    ah, dh, _, _ = get_strengths(home)     #taking teams strenght, separating by home and away form.
    _, _, aa, da = get_strengths(away)

    expected_home = ah * da * league_home_avg   #expected home/away goals
    expected_away = aa * dh * league_away_avg

    home_goals = np.random.poisson(expected_home)   #generating goals based on Poisson distribution
    away_goals = np.random.poisson(expected_away)

    return home_goals, away_goals    #function that trying to predict match result


def build_table(matches):
    teams = sorted(set(matches["HomeTeam"]).union(matches["AwayTeam"]))  #collects all teams.

    table = pd.DataFrame(index=teams, columns=["pts", "gf", "ga"], data=0)  #creating empty table with Pts-Points Gf- goals scored, ga- goals conceded

    for _, row in matches.iterrows():
        h, a = row["HomeTeam"], row["AwayTeam"]
        hg, ag = row["FTHG"], row["FTAG"]

        table.loc[h, "gf"] += hg
        table.loc[h, "ga"] += ag
        table.loc[a, "gf"] += ag
        table.loc[a, "ga"] += hg  #adding goals

        if hg > ag:
            table.loc[h, "pts"] += 3
        elif hg < ag:
            table.loc[a, "pts"] += 3
        else:
            table.loc[h, "pts"] += 1
            table.loc[a, "pts"] += 1    #awards points

    table["gd"] = table["gf"] - table["ga"]   #creating goals difference
    table = table.sort_values(["pts", "gd", "gf"], ascending=False) #sorting by points then goals difference then goals scored.
    table["position"] = range(1, len(table) + 1)  #adding table position

    return table     #building final table based on first 30 matches and simulated ones.


simulated = []

for _, row in future_matches.iterrows():
    hg, ag = simulate_match(row["HomeTeam"], row["AwayTeam"])  #simulating match result

    simulated.append({
        "Date": row["Date"],
        "HomeTeam": row["HomeTeam"],
        "AwayTeam": row["AwayTeam"],
        "FTHG": hg,
        "FTAG": ag
    })  #saving result to the list

simulated_df = pd.DataFrame(simulated)  #from list to table

print("Remaining Matches")
for _, row in simulated_df.iterrows():
    print(f'{row["Date"]}: {row["HomeTeam"]} {row["FTHG"]}-{row["FTAG"]} {row["AwayTeam"]}')  #printing results in Python Console

simulated_df.to_csv("data/predicted_matches.csv", index=False)  #saving to csv

all_matches = pd.concat([
    played_matches[["HomeTeam", "AwayTeam", "FTHG", "FTAG"]],
    simulated_df[["HomeTeam", "AwayTeam", "FTHG", "FTAG"]]
], ignore_index=True)    #past 30 matches + simulated ones.

final_table = build_table(all_matches)

print("Premier League Table 2025/26")
print(final_table)

def table_notes(pos):
    if pos == 1:
        return "Champions"
    elif pos in [2, 3, 4, 5]:
        return "Champions League Qualification"
    elif pos in [6, 7]:
        return "Europe League Qualification"
    elif pos == 8:
        return "Conference League Qualification"
    elif pos in [18, 19, 20]:
        return "Relegation to Championship"
    else:
        return ""    #creating notes to final table.

final_table["status"] = final_table["position"].apply(table_notes)
final_table.index.name = "Team"
final_table.to_csv("data/final_table.csv")

