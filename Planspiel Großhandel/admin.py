import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Lehrer Admin-Panel", layout="wide")

conn = sqlite3.connect('landhandel.db', check_same_thread=False)
c = conn.cursor()

st.title("👨‍🏫 Admin-Konsole: Landhandel-Simulator")

# Aktuellen Status abrufen
c.execute("SELECT current_round, market_news FROM Game_State WHERE game_id='Klasse10B'")
game_state = c.fetchone()
curr_round = game_state[0]

st.header(f"Status: Monat {curr_round}")

# --- ÜBERSICHT: WER HAT ABGEGEBEN? ---
st.subheader("Eingangscheck der Teams")

# Abfrage: Welche Teams haben in der aktuellen Runde schon in Global_Decisions unterschrieben?
submitted_teams = pd.read_sql_query("""
                                    SELECT team_name, advisory_budget
                                    FROM Global_Decisions
                                    WHERE round = ?
                                    """, conn, params=(curr_round,))

c.execute("SELECT team_name FROM Teams")
all_teams = [row[0] for row in c.fetchall()]

for team in all_teams:
    if team in submitted_teams['team_name'].values:
        st.success(f"✅ {team}: Daten abgegeben.")
    else:
        st.error(f"❌ {team}: Wartet noch...")

st.divider()

# --- DIE AUSWERTUNGS-LOGIK ---
st.subheader("Runden-Auswertung")
st.warning("Achtung: Erst drücken, wenn alle Teams abgegeben haben!")

if st.button("Simulation für diesen Monat berechnen ⚙️"):

    # --- NEU 1: Vertriebsbudget abziehen und für später merken ---
    global_decisions = pd.read_sql_query("""
                                         SELECT team_name, advisory_budget
                                         FROM Global_Decisions
                                         WHERE round = ?
                                         """, conn, params=(curr_round,))

    team_budgets = {}
    for _, row in global_decisions.iterrows():
        t_name = row['team_name']
        budget = row['advisory_budget']
        team_budgets[t_name] = budget

        # Budget direkt vom Konto abziehen
        c.execute("UPDATE Teams SET bank_balance = bank_balance - ? WHERE team_name=?", (budget, t_name))

    # --- 2. Globale Marktwerte ---
    markt_nachfrage = {1: 800, 2: 600, 3: 200, 4: 400, 5: 100}
    bestell_fixkosten = 500.0

    # --- 3. Berechnung pro Produkt ---
    for p_id in markt_nachfrage:
        angebote = pd.read_sql_query("""
                                     SELECT team_name, order_quantity, selling_price
                                     FROM Product_Decisions
                                     WHERE round = ?
                                       AND product_id = ?
                                     """, conn, params=(curr_round, p_id))

        if not angebote.empty:
            # NEU 2: Den Außendienst-Effekt berechnen
            # Jedem Angebot das jeweilige Team-Budget zuordnen
            angebote['advisory_budget'] = angebote['team_name'].map(team_budgets)

            # Je 500€ Budget wirkt der Preis für den Kunden 1€ günstiger
            angebote['effektiver_preis'] = angebote['selling_price'] - (angebote['advisory_budget'] / 500.0)

            # Wir sortieren nach dem effektiven Preis (je niedriger, desto besser)
            angebote = angebote.sort_values(by='effektiver_preis')

            nachfrage_noch_offen = markt_nachfrage[p_id]

            for _, row in angebote.iterrows():
                t_name = row['team_name']

                # Bestandsdaten holen
                c.execute("SELECT quantity FROM Inventory WHERE team_name=? AND product_id=?", (t_name, p_id))
                bestand_alt = c.fetchone()[0]

                # Verfügbare Menge
                verfuegbar = bestand_alt + row['order_quantity']

                # Verkauf berechnen
                verkauft = min(nachfrage_noch_offen, verfuegbar)
                nachfrage_noch_offen -= verkauft
                bestand_neu = verfuegbar - verkauft

                # Kostenrechnung
                c.execute("SELECT base_purchase_price, storage_cost_per_unit FROM Products WHERE product_id=?", (p_id,))
                p_info = c.fetchone()
                ek_preis = p_info[0]
                lager_kost_satz = p_info[1]

                umsatz = verkauft * row['selling_price']
                wareneinsatz = row['order_quantity'] * ek_preis
                aktuelle_bestellkosten = bestell_fixkosten if row['order_quantity'] > 0 else 0.0
                aktuelle_lagerkosten = bestand_neu * lager_kost_satz

                # Gewinn aus DIESEM Produkt (ohne das Vertriebsbudget, das wurde oben schon pauschal abgezogen)
                gewinn = umsatz - wareneinsatz - aktuelle_bestellkosten - aktuelle_lagerkosten

                # DB-Update
                c.execute("UPDATE Inventory SET quantity = ? WHERE team_name=? AND product_id=?",
                          (bestand_neu, t_name, p_id))
                c.execute("UPDATE Teams SET bank_balance = bank_balance + ? WHERE team_name=?", (gewinn, t_name))

    # Runde erhöhen
    next_round = curr_round + 1
    c.execute("UPDATE Game_State SET current_round = ? WHERE game_id='Klasse10B'", (next_round,))
    conn.commit()

    st.balloons()
    st.success(
        f"Monat {curr_round} erfolgreich ausgewertet! Spedition, Lager und Vertrieb wurden berechnet. Wir sind nun in Monat {next_round}.")
    st.rerun()

    # 2. Runde erhöhen
    next_round = curr_round + 1
    c.execute("UPDATE Game_State SET current_round = ? WHERE game_id='Klasse10B'", (next_round,))
    conn.commit()
    st.balloons()
    st.success(f"Monat {curr_round} erfolgreich ausgewertet! Wir befinden uns nun in Monat {next_round}.")
    st.rerun()

conn.close()