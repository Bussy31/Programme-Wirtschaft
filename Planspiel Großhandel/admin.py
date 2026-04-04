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
    # 1. Daten holen
    # Hier definieren wir einen fiktiven Marktbedarf pro Produkt
    # In einem späteren Schritt machen wir das dynamisch/zufällig
    markt_nachfrage = {1: 500, 2: 400, 3: 100, 4: 200, 5: 50}

    # Für jedes Produkt die Verteilung berechnen
    for p_id in markt_nachfrage:
        # Wer hat was zu welchem Preis angeboten?
        angebote = pd.read_sql_query("""
                                     SELECT team_name, order_quantity, selling_price
                                     FROM Product_Decisions
                                     WHERE round = ?
                                       AND product_id = ?
                                     """, conn, params=(curr_round, p_id))

        if not angebote.empty:
            # GANZ SIMPLE LOGIK FÜR DEN START:
            # Das Team mit dem niedrigsten Preis bekommt alle Kunden (bis sein Lager leer ist)
            # (Das verfeinern wir im nächsten Schritt zu einer fairen Verteilung!)
            angebote = angebote.sort_values(by='selling_price')
            rest_nachfrage = markt_nachfrage[p_id]

            for index, row in angebote.iterrows():
                t_name = row['team_name']
                # Aktuellen Lagerbestand + neue Bestellung holen
                c.execute("SELECT quantity FROM Inventory WHERE team_name=? AND product_id=?", (t_name, p_id))
                alt_lager = c.fetchone()[0]
                max_verfügbar = alt_lager + row['order_quantity']

                # Wie viel kann verkauft werden?
                verkauft = min(rest_nachfrage, max_verfügbar)
                rest_nachfrage -= verkauft
                neues_lager = max_verfügbar - verkauft

                # Gewinn berechnen (vereinfacht: Verkaufspreis * Menge - Einkaufspreis * Bestellung)
                c.execute("SELECT base_purchase_price FROM Products WHERE product_id=?", (p_id,))
                ek_preis = c.fetchone()[0]
                umsatz = verkauft * row['selling_price']
                kosten = row['order_quantity'] * ek_preis
                gewinn = umsatz - kosten

                # Datenbank updaten: Lager und Kontostand
                c.execute("UPDATE Inventory SET quantity = ? WHERE team_name=? AND product_id=?",
                          (neues_lager, t_name, p_id))
                c.execute("UPDATE Teams SET bank_balance = bank_balance + ? WHERE team_name=?", (gewinn, t_name))

    # 2. Runde erhöhen
    next_round = curr_round + 1
    c.execute("UPDATE Game_State SET current_round = ? WHERE game_id='Klasse10B'", (next_round,))
    conn.commit()
    st.balloons()
    st.success(f"Monat {curr_round} erfolgreich ausgewertet! Wir befinden uns nun in Monat {next_round}.")
    st.rerun()

conn.close()