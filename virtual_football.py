import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Sportybet Virtual Football V19", layout="wide")

SPORTYBET_GREEN = "#16A34A"
SPORTYBET_RED = "#E53E3E"
SPORTYBET_GRAY = "#F4F4F4"
TEXT_COLOR = "#222222"

# ---------------- STATE ----------------
if "round" not in st.session_state:
    st.session_state.round = 1
if "league_table" not in st.session_state:
    st.session_state.league_table = pd.DataFrame({
        "Team": ["Arsenal","Chelsea","Liverpool","Man City","Man Utd",
                 "Tottenham","Leicester","Everton","West Ham","Wolves"],
        "P":0,"W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Pts":0
    })
if "fixtures" not in st.session_state: st.session_state.fixtures=[]
if "results" not in st.session_state: st.session_state.results=[]
if "betslip" not in st.session_state: st.session_state.betslip=[]
if "live_commentary" not in st.session_state: st.session_state.live_commentary=[]

teams = st.session_state.league_table["Team"].tolist()
strength = {team: random.randint(70,95) for team in teams}

# ---------------- STYLES ----------------
st.markdown(f"""
<style>
body {{background-color: {SPORTYBET_GRAY}; color: {TEXT_COLOR};}}
.sporty-header {{background-color: {SPORTYBET_GREEN}; color: white;
                text-align: center; padding: 15px; border-radius: 8px;
                font-size: 30px; font-weight: bold;}}
.banner {{background-color: white; padding: 20px; border-radius:8px;
          margin-bottom:20px; box-shadow:0 2px 5px rgba(0,0,0,0.1);}}
.highlight-match {{border:3px solid {SPORTYBET_GREEN}; padding:10px;
                   margin:10px 0; border-radius:5px; background:white;}}
.match-card {{background:white; padding:12px; margin-bottom:12px;
              border-left:5px solid {SPORTYBET_GREEN}; border-radius:6px;}}
.odds-btn {{background-color: {SPORTYBET_GREEN}; color: white;
           padding:6px 12px; margin:2px; border-radius:5px;
           font-weight:bold; cursor: pointer;}}
.live-box {{background:white; border:2px solid {SPORTYBET_GREEN};
            padding:8px; border-radius:6px; margin-top:4px;}}
.betslip-panel {{background:white; border:2px solid {SPORTYBET_GREEN};
                 padding:12px; border-radius:8px;}}
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def gen_fixtures():
    random.shuffle(teams)
    st.session_state.fixtures = [(teams[i],teams[i+1]) for i in range(0,len(teams),2)]

def gen_odds(home,away):
    diff=(strength[home]-strength[away])/100
    prob_home=0.4+diff*0.3
    prob_away=0.4-diff*0.3
    prob_draw=max(0.1,1-(prob_home+prob_away))
    return {
      "1":round(1/max(0.05,prob_home),2),
      "X":round(1/max(0.05,prob_draw),2),
      "2":round(1/max(0.05,prob_away),2),
      "O1.5":round(1/0.7,2),"U1.5":round(1/0.3,2),
      "O2.5":round(1/0.55,2),"U2.5":round(1/0.45,2),
      "O3.5":round(1/0.35,2),"U3.5":round(1/0.65,2)
    }

def add_bet(match,pick,odd):
    st.session_state.betslip.append({"Match":match,"Pick":pick,"Odd":odd})

def simulate_live(home,away):
    h=a=0
    st.session_state.live_commentary=[]
    prog=st.progress(0); box=st.empty()
    for minute in range(1,91,5):
        event=""
        if random.random()<0.25:
            if random.random()<0.5: h+=1; event=f"{minute}' GOAL! {home} scores! ({h}-{a})"
            else: a+=1; event=f"{minute}' GOAL! {away} scores! ({h}-{a})"
        elif minute==45: event="Half‑time!"
        elif minute>=90: event="Full‑time!"
        else: event=f"{minute}' Play continues..."
        st.session_state.live_commentary.append(event)
        box.markdown(f"<div class='live-box'>{event}</div>", unsafe_allow_html=True)
        prog.progress(minute/90)
        time.sleep(0.25)
    update_league(home, away, h, a)
    st.session_state.results.append(f"{home} {h} - {a} {away}")

def update_league(home,away,g1,g2):
    tbl=st.session_state.league_table
    tbl.loc[tbl.Team==home,["P","GF","GA"]]+= [1,g1,g2]
    tbl.loc[tbl.Team==away,["P","GF","GA"]]+= [1,g2,g1]
    tbl["GD"]=tbl.GF-tbl.GA
    if g1>g2:
        tbl.loc[tbl.Team==home,"W"]+=1; tbl.loc[tbl.Team==away,"L"]+=1
        tbl.loc[tbl.Team==home,"Pts"]+=3
    elif g2>g1:
        tbl.loc[tbl.Team==away,"W"]+=1; tbl.loc[tbl.Team==home,"L"]+=1
        tbl.loc[tbl.Team==away,"Pts"]+=3
    else:
        tbl.loc[tbl.Team==home,"D"]+=1; tbl.loc[tbl.Team==away,"D"]+=1
        tbl.loc[tbl.Team==home,"Pts"]+=1; tbl.loc[tbl.Team==away,"Pts"]+=1
    st.session_state.league_table=tbl

# ---------------- LAYOUT ----------------
st.markdown(f'<div class="sporty-header">⚽ Sportybet Virtual Football V19</div>', unsafe_allow_html=True)
menu=st.sidebar.radio("Menu",["🏠 Home","📅 Fixtures","🧾 Bet Slip","🏟 Results","🏆 League Table"])

with st.sidebar:
    st.markdown("### 🧾 Bet Slip")
    if st.session_state.betslip:
        df=pd.DataFrame(st.session_state.betslip)
        total=round(np.prod(df.Odd),2)
        st.table(df); st.write(f"**Total Odds:** {total}")
        st.button("Clear Bet Slip", on_click=lambda: st.session_state.betslip.clear())
    else:
        st.info("Select bets to appear here")

if menu=="🏠 Home":
    st.subheader("Featured Matches")
    st.markdown("<div class='banner'><b>🏆 Upcoming Round Matches</b></div>", unsafe_allow_html=True)
    if not st.session_state.fixtures: gen_fixtures()
    for home,away in st.session_state.fixtures[:2]:
        odds=gen_odds(home,away)
        st.markdown(f"<div class='highlight-match'>{home} vs {away} – Odds: 1:{odds['1']} X:{odds['X']} 2:{odds['2']}</div>", unsafe_allow_html=True)
    if st.button("▶ Play Round Live"):
        for home,away in st.session_state.fixtures:
            st.write(f"**{home} vs {away}**"); simulate_live(home,away)
        st.session_state.round+=1; gen_fixtures()

elif menu=="📅 Fixtures":
    st.subheader(f"Round {st.session_state.round} Fixtures")
    if not st.session_state.fixtures: gen_fixtures()
    for home,away in st.session_state.fixtures:
        odds=gen_odds(home,away)
        st.markdown(f"<div class='match-card'><b>{home}</b> vs <b>{away}</b><br>"
                    f"1:{odds['1']} X:{odds['X']} 2:{odds['2']}<br>"
                    f"O1.5:{odds['O1.5']} U1.5:{odds['U1.5']}<br>"
                    f"O2.5:{odds['O2.5']} U2.5:{odds['U2.5']}<br>"
                    f"O3.5:{odds['O3.5']} U3.5:{odds['U3.5']}</div>", unsafe_allow_html=True)
        cols=st.columns(6)
        picks=["1","X","2","O1.5","O2.5","O3.5"]
        for idx,p in enumerate(picks):
            odd=odds[p]
            if cols[idx].button(f"{p} ({odd})", key=f"{home}-{p}"):
                add_bet(f"{home} vs {away}",p,odd)
    if st.button("▶ Play Round Live"):
        for home,away in st.session_state.fixtures:
            st.write(f"**{home} vs {away}**"); simulate_live(home,away)
        st.session_state.round+=1; gen_fixtures()

elif menu=="🧾 Bet Slip":
    st.subheader("Your Bet Slip")
    if st.session_state.betslip:
        df=pd.DataFrame(st.session_state.betslip)
        total=round(np.prod(df.Odd),2)
        st.table(df); st.write(f"**Total Odds:** {total}")
    else:
        st.info("No selections yet")

elif menu=="🏟 Results":
    st.subheader("Recent Results")
    if st.session_state.results:
        for res in st.session_state.results[-10:]: st.write(f"- {res}")
    else: st.info("No results yet")

elif menu=="🏆 League Table":
    st.subheader("League Standings")
    table=st.session_state.league_table.sort_values(by=["Pts","GD","GF"],ascending=[False,False,False])
    st.table(table.reset_index(drop=True))
