import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Raiffeisen Landhandel Simulator", layout="wide")

# --- SESSION STATE (Das Kurzzeitgedächtnis für den Login) ---
if "logged_in_team" not in st.session_state:
    st.session_state.logged_in_team = None

# Datenbankverbindung
conn = sqlite3.connect('landhandel.db', check_same_thread=False)
c = conn.cursor()

# --- LOGIN BEREICH ---
if st.session_state.logged_in_team is None:
    st.title("🔒 Login: Raiffeisen Landhandel")

    # Teams aus DB laden
    c.execute("SELECT team_name FROM Teams")
    teams = [row[0] for row in c.fetchall()]

    with st.form("login_form"):
        selected_team = st.selectbox("Wähle dein Team:", teams)
        entered_password = st.text_input("Passwort:", type="password")
        login_button = st.form_submit_button("Einloggen")

        if login_button:
            # Passwort in der DB prüfen
            c.execute("SELECT password FROM Teams WHERE team_name=?", (selected_team,))
            correct_password = c.fetchone()[0]

            if entered_password == correct_password:
                st.session_state.logged_in_team = selected_team
                st.success("Erfolgreich eingeloggt!")
                st.rerun()  # Seite neu laden, um das Dashboard anzuzeigen
            else:
                st.error("❌ Falsches Passwort!")

    # Wenn nicht eingeloggt, wird der Rest der Seite nicht geladen:
    st.stop()

# --- AB HIER: DAS EIGENTLICHE DASHBOARD ---
team_name = st.session_state.logged_in_team

# Logout-Button in der Seitenleiste
st.sidebar.markdown(f"Eingeloggt als: **{team_name}**")
if st.sidebar.button("🚪 Ausloggen"):
    st.session_state.logged_in_team = None
    st.rerun()

# Spielstatus abrufen
c.execute("SELECT current_round, market_news FROM Game_State WHERE game_id='Klasse10B'")
game_state = c.fetchone()
current_round = game_state[0]
news = game_state[1]

st.title(f"🚜 Management Cockpit: {team_name}")

# Kontostand abrufen
c.execute("SELECT bank_balance FROM Teams WHERE team_name=?", (team_name,))
bank_balance = c.fetchone()[0]