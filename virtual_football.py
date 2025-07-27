import streamlit as st
import pandas as pd
import numpy as np
import random
from math import exp

st.set_page_config(page_title="Virtual Football League - Sportybet Style", layout="wide")

# ----------------------------------------
# TEAMS & INITIAL SETTINGS
# ----------------------------------------
teams = {
    "Arsenal": 88, "Chelsea": 85, "Liverpool": 90, "Man City": 92,
    "Man Utd": 84, "Tottenham": 83, "Leicester": 80, "Everton": 78,
    "West Ham": 76, "Southampton": 74, "Leeds": 72, "Wolves": 71,
    "Brighton": 70, "Newcastle": 69, "Crystal Palace": 68,
    "Burnley": 66, "Watford": 65, "Norwich": 63, "Brentford": 64, "Fulham": 67
}

def init_league():
    return pd.DataFrame({
        "Team": list(teams.keys()),
        "Played": 0, "Won": 0, "Drawn": 0, "Lost": 0,
        "GF": 0, "GA": 0, "Points": 0
    }).set_index("Team")

if "league_table" not in st.session_state:
    st.session_state.league_table = init_league()
if "round" not in st.session_state:
    st.session_state.round = 1
if "match_history" not in st.session_state:
    st.session_state.match_history = []

# ----------------------------------------
# MATCH SIMULATION
# ----------------------------------------
def poisson_goal_avg(team_strength):
    return max(0.2, team_strength / 50 * 1.5)

def simulate_match(home, away):
    home_avg = poisson_goal_avg(teams[home])
    away_avg = poisson_goal_avg(teams[away])
    home_goals = np.random.poisson(home_avg)
    away_goals = np.random.poisson(away_avg)
    return int(home_goals), int(away_goals)

def update_table(home, away, g1, g2):
    table = st.session_state.league_table
    table.loc[home, "Played"] += 1
    table.loc[away, "Played"] += 1
    table.loc[home, "GF"] += g1
    table.loc[home, "GA"] += g2
    table.loc[away, "GF"] += g2
    table.loc[away, "GA"] += g1
    if g1 > g2:
        table.loc[home, "Won"] += 1
        table.loc[away, "Lost"] += 1
        table.loc[home, "Points"] += 3
    elif g2 > g1:
        table.loc[away, "Won"] += 1
        table.loc[home, "Lost"] += 1
        table.loc[away, "Points"] += 3
    else:
        table.loc[home, "Drawn"] += 1
        table.loc[away, "Drawn"] += 1
        table.loc[home, "Points"] += 1
        table.loc[away, "Points"] += 1

def generate_odds(home, away):
    home_rating = teams[home]
    away_rating = teams[away]
    base = (home_rating - away_rating) / 100.0
    home_win_prob = 0.45 + base * 0.3
    away_win_prob = 0.45 - base * 0.3
    draw_prob = 1 - (home_win_prob + away_win_prob)
    return {
        "1": round(1 / max(0.05, home_win_prob), 2),
        "X": round(1 / max(0.05, draw_prob), 2),
        "2": round(1 / max(0.05, away_win_prob), 2)
    }

def match_commentary(home, away, g1, g2):
    events = []
    goals = sorted(random.sample(range(5, 85), g1 + g2))
    home_count, away_count = 0, 0
    for m in range(0, 91, 10):
        while goals and goals[0] <= m:
            scorer = home if home_count < g1 else away
            events.append(f"{m}' - Goal for {scorer}!")
            if scorer == home:
                home_count += 1
            else:
                away_count += 1
            goals.pop(0)
        events.append(f"{m}' - End to end play...")
    events.append(f"FT: {home} {g1} - {g2} {away}")
    return events

# ----------------------------------------
# UI
# ----------------------------------------
st.title("⚽ Virtual Football - Sportybet Style V3")

tabs = st.tabs(["🏆 League Table", "📅 Fixtures & Results", "🎯 Predictions", "📜 Match History"])

with tabs[0]:
    st.subheader("League Table")
    st.dataframe(st.session_state.league_table.sort_values(by=["Points","GF"], ascending=False))

with tabs[1]:
    st.subheader(f"Round {st.session_state.round} Fixtures")
    team_list = list(teams.keys())
    random.shuffle(team_list)
    fixtures = [(team_list[i], team_list[i+1]) for i in range(0, len(team_list), 2)]
    st.write(pd.DataFrame(fixtures, columns=["Home", "Away"]))

    if st.button("Simulate This Round"):
        for home, away in fixtures:
            g1, g2 = simulate_match(home, away)
            update_table(home, away, g1, g2)
            odds = generate_odds(home, away)
            commentary = match_commentary(home, away, g1, g2)
            st.markdown(f"**{home} {g1} - {g2} {away}** | Odds → 1: {odds['1']} | X: {odds['X']} | 2: {odds['2']}")
            with st.expander(f"Commentary for {home} vs {away}"):
                for event in commentary:
                    st.write(event)
            st.session_state.match_history.append((home, g1, g2, away))
        st.session_state.round += 1
        st.success("Round completed!")

with tabs[2]:
    st.subheader("Correct Score Prediction")
    home = st.selectbox("Select Home Team", list(teams.keys()))
    away = st.selectbox("Select Away Team", [t for t in teams.keys() if t != home])
    if st.button("Predict Score"):
        p1, p2 = simulate_match(home, away)
        odds = generate_odds(home, away)
        st.info(f"Predicted Score: {home} {p1} - {p2} {away}")
        st.write(f"**Odds:** 1 → {odds['1']} | X → {odds['X']} | 2 → {odds['2']}")

with tabs[3]:
    st.subheader("Recent Match History")
    if st.session_state.match_history:
        df = pd.DataFrame(st.session_state.match_history, columns=["Home", "HG", "AG", "Away"])
        st.table(df.tail(10))
    else:
        st.info("No match history yet.")
