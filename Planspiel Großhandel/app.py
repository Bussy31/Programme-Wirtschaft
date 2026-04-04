import streamlit as st
import sqlite3
import pandas as pd

# 1. Seiten-Layout konfigurieren (schön breit für Tabellen)
st.set_page_config(page_title="Raiffeisen Landhandel Simulator", layout="wide")

# 2. Datenbankverbindung herstellen
conn = sqlite3.connect('landhandel.db', check_same_thread=False)
c = conn.cursor()

# 3. Aktuellen Spielstatus (Runde & News) abrufen
c.execute("SELECT current_round, market_news FROM Game_State WHERE game_id='Klasse10B'")
game_state = c.fetchone()
current_round = game_state[0]
news = game_state[1]

# --- KOPFZEILE & LOGIN ---
st.title("🚜 Raiffeisen Landhandel - Management Cockpit")

# Teamauswahl in der Seitenleiste
c.execute("SELECT team_name FROM Teams")
teams = [row[0] for row in c.fetchall()]
team_name = st.sidebar.selectbox("Als Team einloggen:", teams)

# Kontostand des gewählten Teams abrufen
c.execute("SELECT bank_balance FROM Teams WHERE team_name=?", (team_name,))
bank_balance = c.fetchone()[0]

# Oben auf der Seite: Drei schicke Info-Boxen
col1, col2, col3 = st.columns(3)
col1.metric("Aktuelle Runde", f"Monat {current_round}")
col2.metric("Kontostand", f"{bank_balance:,.2f} €")
col3.info(f"📰 **Markt-News:** {news}")

st.divider()

# --- EINGABEMASKE FÜR ENTSCHEIDUNGEN ---
st.subheader("📋 Eure Entscheidungen für diesen Monat")

# Wir nutzen ein st.form, damit nicht bei jedem Klick die Seite neu lädt
with st.form("decision_form"):
    st.markdown("### 👨‍🌾 1. Außendienst & Kundenberatung")
    st.caption("Wie viel Geld investiert ihr in euren Außendienst, um Landwirte von euch zu überzeugen?")
    advisory_budget = st.number_input("Vertriebsbudget (in €):", min_value=0.0, step=100.0)

    st.markdown("### 📦 2. Sortiment & Beschaffung")
    st.caption("Tragt eure Bestellmengen beim Hersteller und eure Verkaufspreise an die Landwirte ein.")

    # Alle Produkte und den aktuellen Lagerbestand des Teams abrufen
    query = """
            SELECT p.product_id, p.name, p.base_purchase_price, p.storage_cost_per_unit, i.quantity
            FROM Products p
                     LEFT JOIN Inventory i ON p.product_id = i.product_id
            WHERE i.team_name = ? \
            """
    products = pd.read_sql_query(query, conn, params=(team_name,))

    # Ein Dictionary, um die Eingaben für alle 5 Produkte zwischenzuspeichern
    decisions = {}

    # Für jedes Produkt eine eigene Eingabezeile bauen
    for index, row in products.iterrows():
        # Zeigt wichtige Infos, um die "Black Box" zu verhindern
        st.markdown(
            f"**{row['name']}** | 🏭 Lagerbestand: **{row['quantity']} t** | 🛒 Einkauf: **{row['base_purchase_price']} €/t** | 📉 Lagerkosten: **{row['storage_cost_per_unit']} €/t**")

        col_a, col_b = st.columns(2)
        with col_a:
            # Bestellmenge beim Hersteller
            order_qty = st.number_input(f"Bestellmenge in Tonnen", min_value=0, step=10, key=f"qty_{row['product_id']}")
        with col_b:
            # Eigener Verkaufspreis (Standardwert ist Einkaufspreis + 20% Aufschlag)
            default_price = float(row['base_purchase_price'] * 1.2)
            sell_price = st.number_input(f"Verkaufspreis in €/t", min_value=0.0, step=5.0, value=default_price,
                                         key=f"price_{row['product_id']}")

        # Daten im Dictionary speichern
        decisions[row['product_id']] = {'qty': order_qty, 'price': sell_price}
        st.write("---")  # Trennlinie zwischen den Produkten

    # Der große Absende-Button
    submitted = st.form_submit_button("Entscheidungen verbindlich absenden 🚀")

    if submitted:
        # Prüfen, ob das Team in dieser Runde schon abgegeben hat
        c.execute("SELECT id FROM Global_Decisions WHERE team_name=? AND round=?", (team_name, current_round))
        if c.fetchone():
            st.error("❌ Euer Team hat für diesen Monat bereits abgegeben! Wartet auf den Lehrer.")
        else:
            # 1. Allgemeines Budget speichern
            c.execute("INSERT INTO Global_Decisions (team_name, round, advisory_budget) VALUES (?, ?, ?)",
                      (team_name, current_round, advisory_budget))

            # 2. Die Entscheidungen für alle 5 Produkte speichern
            for pid, data in decisions.items():
                c.execute(
                    "INSERT INTO Product_Decisions (team_name, round, product_id, order_quantity, selling_price) VALUES (?, ?, ?, ?, ?)",
                    (team_name, current_round, pid, data['qty'], data['price']))

            conn.commit()
            st.success(
                "✅ Erfolgreich gespeichert! Die Daten wurden an die Zentrale übermittelt. Bitte wartet auf die Auswertung.")

conn.close()