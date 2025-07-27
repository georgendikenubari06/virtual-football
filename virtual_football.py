import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Sportybet Virtual Football V15", layout="wide")

SPORTYBET_GREEN = "#16A34A"
BACKGROUND = "#f8f9fa"

# ---------------- SESSION STATES ----------------
if "round" not in st.session_state:
    st.session_state.round = 1
if "league_table" not in st.session_state:
    st.session_state.league_table = pd.DataFrame({
        "Team": [
            "Arsenal", "Chelsea", "Liverpool", "Man City",
            "Man Utd", "Tottenham", "Leicester", "Everton",
            "West Ham", "Wolves"
        ],
        "P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0
    })
if "fixtures" not in st.session_state:
    st.session_state.fixtures = []
if "results" not in st.session_state:
    st.session_state.results = []
if "betslip" not in st.session_state:
    st.session_state.betslip = []
if "top_scorers" not in st.session_state:
    st.session_state.top_scorers = {team: 0 for team in [
        "Arsenal", "Chelsea", "Liverpool", "Man City",
        "Man Utd", "Tottenham", "Leicester", "Everton",
        "West Ham", "Wolves"
    ]}

teams = st.session_state.league_table["Team"].tolist()
team_strength = {team: random.randint(70, 95) for team in teams}

# ---------------- STYLE ----------------
st.markdown(f"""
    <style>
        body {{
            background-color: {BACKGROUND};
            color: #333;
        }}
        .sporty-header {{
            background-color: {SPORTYBET_GREEN};
            color: white;
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            font-size: 28px;
            font-weight: bold;
        }}
        .nav-tabs {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .nav-tabs button {{
            background-color: white;
            border: 2px solid {SPORTYBET_GREEN};
            color: {SPORTYBET_GREEN};
            border-radius: 8px;
            padding: 8px 15px;
            font-weight: bold;
        }}
        .nav-tabs button:hover {{
            background-color: {SPORTYBET_GREEN};
            color: white;
        }}
        .match-card {{
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 6px solid {SPORTYBET_GREEN};
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .bet-slip {{
            background-color: white;
            border-radius: 10px;
            padding: 10px;
            border: 2px solid {SPORTYBET_GREEN};
        }}
    </style>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def generate_fixtures():
    random.shuffle(teams)
    st.session_state.fixtures = [(teams[i], teams[i+1]) for i in range(0, len(teams), 2)]

def generate_odds(home, away):
    diff = (team_strength[home] - team_strength[away]) / 100
    home_win_prob = 0.4 + diff * 0.3
    away_win_prob = 0.4 - diff * 0.3
    draw_prob = max(0.1, 1 - (home_win_prob + away_win_prob))
    return {
        "1": round(1 / max(0.05, home_win_prob), 2),
        "X": round(1 / max(0.05, draw_prob), 2),
        "2": round(1 / max(0.05, away_win_prob), 2)
    }

def add_to_betslip(match, pick, odd):
    st.session_state.betslip.append({"Match": match, "Pick": pick, "Odd": odd})

def simulate_match(home, away):
    home_avg = team_strength[home] / 60
    away_avg = team_strength[away] / 60
    g1 = np.random.poisson(home_avg)
    g2 = np.random.poisson(away_avg)
    st.session_state.top_scorers[home] += g1
    st.session_state.top_scorers[away] += g2
    update_league(home, away, g1, g2)
    return g1, g2

def update_league(home, away, g1, g2):
    table = st.session_state.league_table
    table.loc[table["Team"] == home, ["P", "GF", "GA"]] += [1, g1, g2]
    table.loc[table["Team"] == away, ["P", "GF", "GA"]] += [1, g2, g1]
    table["GD"] = table["GF"] - table["GA"]

    if g1 > g2:
        table.loc[table["Team"] == home, "W"] += 1
        table.loc[table["Team"] == away, "L"] += 1
        table.loc[table["Team"] == home, "Pts"] += 3
    elif g2 > g1:
        table.loc[table["Team"] == away, "W"] += 1
        table.loc[table["Team"] == home, "L"] += 1
        table.loc[table["Team"] == away, "Pts"] += 3
    else:
        table.loc[table["Team"] == home, "D"] += 1
        table.loc[table["Team"] == away, "D"] += 1
        table.loc[table["Team"] == home, "Pts"] += 1
        table.loc[table["Team"] == away, "Pts"] += 1
    st.session_state.league_table = table

def auto_play_season():
    for rnd in range(st.session_state.round, 11):
        st.subheader(f"Round {rnd} Results")
        generate_fixtures()
        for home, away in st.session_state.fixtures:
            g1, g2 = simulate_match(home, away)
            res = f"{home} {g1} - {g2} {away}"
            st.session_state.results.append(res)
            st.write(res)
            time.sleep(0.2)
        st.session_state.round += 1
    st.success("🏆 Season Completed!")

# ---------------- HEADER ----------------
st.markdown(f'<div class="sporty-header">⚽ Sportybet Virtual Football V15</div>', unsafe_allow_html=True)

# ---------------- NAVIGATION ----------------
tab = st.radio("Navigation", ["🏠 Home", "📅 Fixtures & Betting", "🧾 Bet Slip", "🏟 Results", "🏆 League Table"])

# ---------------- HOME ----------------
if tab == "🏠 Home":
    st.subheader("Welcome to Sportybet Virtual Football V15")
    st.write("Enjoy betting, fixtures, results, and live commentary — just like Sportybet!")
    if st.button("▶ Auto-Play Full Season"):
        auto_play_season()

# ---------------- FIXTURES & BETTING ----------------
elif tab == "📅 Fixtures & Betting":
    st.subheader(f"Fixtures - Round {st.session_state.round}")
    if not st.session_state.fixtures:
        generate_fixtures()

    for home, away in st.session_state.fixtures:
        odds = generate_odds(home, away)
        st.markdown(f"""
        <div class="match-card">
            <b>{home}</b> vs <b>{away}</b><br>
            Odds → 1: {odds['1']} | X: {odds['X']} | 2: {odds['2']}
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"{home} WIN ({odds['1']})", key=f"{home}-1"):
                add_to_betslip(f"{home} vs {away}", "1", odds['1'])
        with col2:
            if st.button(f"DRAW ({odds['X']})", key=f"{home}-X"):
                add_to_betslip(f"{home} vs {away}", "X", odds['X'])
        with col3:
            if st.button(f"{away} WIN ({odds['2']})", key=f"{home}-2"):
                add_to_betslip(f"{home} vs {away}", "2", odds['2'])

    if st.button("▶ Play This Round"):
        st.subheader("🏟 Match Results")
        for home, away in st.session_state.fixtures:
            g1, g2 = simulate_match(home, away)
            result = f"{home} {g1} - {g2} {away}"
            st.session_state.results.append(result)
            st.write(result)
        st.session_state.round += 1
        generate_fixtures()

# ---------------- BET SLIP ----------------
elif tab == "🧾 Bet Slip":
    st.subheader("Your Bet Slip")
    if st.session_state.betslip:
        slip_df = pd.DataFrame(st.session_state.betslip)
        total_odd = round(np.prod(slip_df["Odd"]), 2)
        st.table(slip_df)
        st.write(f"**Total Odds:** {total_odd}")
    else:
        st.info("No selections yet.")

# ---------------- RESULTS ----------------
elif tab == "🏟 Results":
    st.subheader("Match Results")
    if st.session_state.results:
        for res in st.session_state.results[-10:]:
            st.write(f"- {res}")
    else:
        st.info("No results yet.")

# ---------------- LEAGUE TABLE ----------------
elif tab == "🏆 League Table":
    st.subheader("Current Standings")
    table = st.session_state.league_table.sort_values(by=["Pts", "GD", "GF"], ascending=[False, False, False])
    st.table(table.reset_index(drop=True))

    st.subheader("🎯 Top Scorers")
    top_scorers_df = pd.DataFrame(list(st.session_state.top_scorers.items()), columns=["Team", "Goals"])
    top_scorers_df = top_scorers_df.sort_values(by="Goals", ascending=False)
    st.table(top_scorers_df)
