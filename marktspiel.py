import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker  # NEU: Um die Diagramm-Achsen auf Komma umzustellen
import random
import os
from fpdf import FPDF

def format_preis(wert):
    if wert is None or pd.isna(wert):
        return "0,00"
    return f"{wert:.2f}".replace('.', ',')

st.set_page_config(layout="wide", page_title="Marktspiel", page_icon="📈")

# --- COPYRIGHT FOOTER (Unten rechts) ---
footer_html = """
<style>
.footer {
    position: fixed;
    bottom: 10px;
    right: 15px;
    font-size: 12px;
    color: #888888;
    z-index: 100;
}
</style>
<div class="footer">© Philipp Bußmann</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)

# --- DATENBANK SETUP ---
def init_db():
    conn = sqlite3.connect('marktspiel.db')
    c = conn.cursor()

    # Tabelle für die Spieleinstellungen
    c.execute('''CREATE TABLE IF NOT EXISTS Game_Setup
                 (spiel_id TEXT PRIMARY KEY, gegenstand TEXT, min_preis REAL, max_preis REAL, aktuelle_runde INTEGER)''')

    # Tabelle für die Spieler
    c.execute('''CREATE TABLE IF NOT EXISTS Players
                 (spieler_name TEXT, spiel_id TEXT, rolle TEXT, PRIMARY KEY(spieler_name, spiel_id))''')

    # Tabelle für die Gebote
    c.execute('''CREATE TABLE IF NOT EXISTS Bids
                 (spieler_name TEXT, spiel_id TEXT, runde INTEGER, gebot REAL)''')

    conn.commit()
    conn.close()


# --- LOGIK: SPIELER HINZUFÜGEN & ROLLE ZUWEISEN ---
def spieler_hinzufuegen(spiel_id, spieler_name):
    conn = sqlite3.connect('marktspiel.db')
    c = conn.cursor()

    # 1. Zählen, wie viele Spieler schon in DIESEM Spiel sind
    c.execute("SELECT COUNT(*) FROM Players WHERE spiel_id=?", (spiel_id,))
    anzahl_spieler = c.fetchone()[0]

    # 2. Abwechselnde Rollenverteilung (Gerade Zahl = Nachfrager, Ungerade Zahl = Anbieter)
    if anzahl_spieler % 2 == 0:
        rolle = "Nachfrager"
    else:
        rolle = "Anbieter"

    # 3. Spieler in die Datenbank eintragen
    try:
        c.execute("INSERT INTO Players (spieler_name, spiel_id, rolle) VALUES (?, ?, ?)",
                  (spieler_name, spiel_id, rolle))
        conn.commit()
        erfolg = True
    except sqlite3.IntegrityError:
        erfolg = False  # Passiert, wenn der Name in diesem Spiel schon existiert

    conn.close()
    return erfolg, rolle


# --- LOGIK: SPIEL ERSTELLEN ---
def spiel_erstellen(spiel_id, gegenstand, min_preis, max_preis):
    conn = sqlite3.connect('marktspiel.db')
    c = conn.cursor()

    try:
        # aktuelle_runde startet immer bei 1
        c.execute(
            "INSERT INTO Game_Setup (spiel_id, gegenstand, min_preis, max_preis, aktuelle_runde) VALUES (?, ?, ?, ?, 1)",
            (spiel_id, gegenstand, min_preis, max_preis))
        conn.commit()
        erfolg = True
    except sqlite3.IntegrityError:
        erfolg = False  # Passiert, wenn diese Spiel-ID schon in der Datenbank existiert

    conn.close()
    return erfolg


# --- LOGIK: SPIELDATEN ABRUFEN ---
def get_spiel_daten(spiel_id):
    conn = sqlite3.connect('marktspiel.db')
    c = conn.cursor()
    c.execute("SELECT gegenstand, min_preis, max_preis, aktuelle_runde FROM Game_Setup WHERE spiel_id=?", (spiel_id,))
    daten = c.fetchone()
    conn.close()
    return daten  # Gibt (gegenstand, min, max, runde) zurück oder None


# --- LOGIK: GEBOT ABGEBEN ---
def gebot_abgeben(spieler_name, spiel_id, runde, gebot):
    conn = sqlite3.connect('marktspiel.db')
    c = conn.cursor()

    # Prüfen, ob für diese Runde schon ein Gebot existiert (Update) oder ob es neu ist (Insert)
    c.execute("SELECT * FROM Bids WHERE spieler_name=? AND spiel_id=? AND runde=?", (spieler_name, spiel_id, runde))
    existiert = c.fetchone()

    if existiert:
        c.execute("UPDATE Bids SET gebot=? WHERE spieler_name=? AND spiel_id=? AND runde=?",
                  (gebot, spieler_name, spiel_id, runde))
    else:
        c.execute("INSERT INTO Bids (spieler_name, spiel_id, runde, gebot) VALUES (?, ?, ?, ?)",
                  (spieler_name, spiel_id, runde, gebot))

    conn.commit()
    conn.close()


# --- LOGIK: RUNDE AUSWERTEN ---
def runde_auswerten(spiel_id, runde):
    conn = sqlite3.connect('marktspiel.db')
    c = conn.cursor()

    c.execute('''
              SELECT B.spieler_name, B.gebot, P.rolle
              FROM Bids B
                       JOIN Players P ON B.spieler_name = P.spieler_name AND B.spiel_id = P.spiel_id
              WHERE B.spiel_id = ?
                AND B.runde = ?
              ''', (spiel_id, runde))

    gebote = c.fetchall()
    conn.close()

    # NEU: Wir sortieren ganze Datensätze (Name, Preis, Rolle), nicht nur die Preise!
    anbieter = sorted([g for g in gebote if g[2] == 'Anbieter'], key=lambda x: x[1])
    nachfrager = sorted([g for g in gebote if g[2] == 'Nachfrager'], key=lambda x: x[1], reverse=True)

    transaktionen = 0
    gleichgewichtspreis = None
    matches = []  # Hier speichern wir, wer mit wem gehandelt hat

    for a, n in zip(anbieter, nachfrager):
        a_name, a_preis, _ = a
        n_name, n_preis, _ = n

        if n_preis >= a_preis:
            transaktionen += 1
            gleichgewichtspreis = (n_preis + a_preis) / 2

            # Deal speichern für das PDF und Dashboard!
            matches.append({
                'kaeufer': n_name, 'k_preis': n_preis,
                'verkaeufer': a_name, 'v_preis': a_preis,
                'deal_preis': gleichgewichtspreis
            })
        else:
            break  # Handel stoppt, Käufer will weniger zahlen als Verkäufer verlangt

    # Gibt jetzt 4 Dinge zurück (inklusive der Match-Liste)
    return transaktionen, gleichgewichtspreis, len(gebote), matches

# --- LOGIK: NÄCHSTE RUNDE STARTEN ---
def naechste_runde_starten(spiel_id):
    conn = sqlite3.connect('marktspiel.db')
    c = conn.cursor()
    c.execute("UPDATE Game_Setup SET aktuelle_runde = aktuelle_runde + 1 WHERE spiel_id=?", (spiel_id,))
    conn.commit()
    conn.close()


# --- LOGIK: DATENBANK RESET (NUR ADMIN) ---
def reset_database():
    conn = sqlite3.connect('marktspiel.db')
    c = conn.cursor()

    # Löscht alle Einträge aus den Tabellen, behält aber die Struktur bei
    c.execute("DELETE FROM Game_Setup")
    c.execute("DELETE FROM Players")
    c.execute("DELETE FROM Bids")

    conn.commit()
    conn.close()


def generiere_testdaten(spiel_id):
    """Erzeugt 20 fiktive Schüler mit zufälligen Geboten für die aktuelle Runde."""
    conn = sqlite3.connect('marktspiel.db')
    c = conn.cursor()

    # Spieldaten holen
    c.execute("SELECT min_preis, max_preis, aktuelle_runde FROM Game_Setup WHERE spiel_id=?", (spiel_id,))
    res = c.fetchone()
    if not res: return
    mini, maxi, runde = res

    test_namen = ["Lukas", "Julia", "Tim", "Sophie", "Max", "Emma", "Felix", "Lena", "Moritz", "Mia",
                  "Paul", "Hannah", "Leon", "Lea", "Jonas", "Laura", "Noah", "Anna", "Elias", "Mila"]

    for i, name in enumerate(test_namen):
        rolle = "Nachfrager" if i % 2 == 0 else "Anbieter"
        # Spieler anlegen (falls noch nicht da)
        try:
            c.execute("INSERT INTO Players (spieler_name, spiel_id, rolle) VALUES (?, ?, ?)", (name, spiel_id, rolle))
        except sqlite3.IntegrityError:
            pass

            # Zufälliges Gebot abgeben
        gebot = round(random.uniform(mini, maxi), 2)
        # Bestehendes Gebot für diese Runde überschreiben oder neu anlegen
        c.execute("DELETE FROM Bids WHERE spieler_name=? AND spiel_id=? AND runde=?", (name, spiel_id, runde))
        c.execute("INSERT INTO Bids (spieler_name, spiel_id, runde, gebot) VALUES (?, ?, ?, ?)",
                  (name, spiel_id, runde, gebot))

    conn.commit()
    conn.close()


def get_abgabe_status(spiel_id, runde):
    """Gibt eine Liste aller Spieler und deren Abgabestatus (True/False) zurück."""
    conn = sqlite3.connect('marktspiel.db')
    c = conn.cursor()
    c.execute('''
              SELECT P.spieler_name,
                     P.rolle,
                     (SELECT COUNT(*)
                      FROM Bids B
                      WHERE B.spieler_name = P.spieler_name AND B.spiel_id = P.spiel_id AND B.runde = ?) as abgegeben
              FROM Players P
              WHERE P.spiel_id = ?
              ''', (runde, spiel_id))
    status = c.fetchall()
    conn.close()
    return status

# Initiale Ausführung beim Start
init_db()



# --- STREAMLIT OBERFLÄCHE & NAVIGATION ---

# Session State initialisieren (merkt sich, wo der Nutzer ist)
if 'ansicht' not in st.session_state:
    st.session_state.ansicht = 'startseite'

# --- STARTSEITE ---
if st.session_state.ansicht == 'startseite':
    st.title("🍏 Das Markt- und Gleichgewichts-Spiel")
    st.subheader("Basierend auf dem 'Pit Market'-Experiment von Vernon Smith")
    st.write("Willkommen! Bitte wähle deine Rolle:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👨‍🏫 Ich bin Lehrer:in (Spiel erstellen)"):
            st.session_state.ansicht = 'lehrer_setup'
            st.rerun()

    with col2:
        if st.button("🧑‍🎓 Ich bin Schüler:in (Spiel beitreten)"):
            st.session_state.ansicht = 'schueler_join'
            st.rerun()

    st.divider()

    # --- ADMIN BEREICH ---
    with st.expander("🛠️ Admin-Bereich (Datenbank Reset)"):
        st.write("Bitte mit Admin-Zugangsdaten anmelden, um das System zurückzusetzen.")

        # Eingabefelder für Login
        admin_user = st.text_input("Benutzername", key="admin_user")
        admin_pass = st.text_input("Passwort", type="password", key="admin_pass")

        # Hier trägst du im Code dein Wunsch-Passwort ein (statt 'DEIN_PASSWORT')
        if st.button("Login überprüfen"):
            if admin_user == "admin" and admin_pass == "1234":
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("Falscher Benutzername oder Passwort.")

        # Wenn der Admin erfolgreich eingeloggt ist (wird im Session State gemerkt)
        if st.session_state.get('is_admin', False):
            st.success("Erfolgreich als Admin angemeldet!")
            st.warning("⚠️ ACHTUNG: Ein Klick auf diesen Button löscht ALLE Spiele, Spieler und Gebote unwiderruflich!")

            if st.button("🔥 Komplette Datenbank resetten", type="primary"):
                reset_database()
                st.success("Datenbank wurde komplett geleert! Das System ist wieder sauber.")
                st.session_state.is_admin = False  # Nach dem Löschen loggen wir den Admin zur Sicherheit wieder aus

# --- LEHRER BEREICH: SPIEL ERSTELLEN ---
elif st.session_state.ansicht == 'lehrer_setup':
    st.header("⚙️ Neues Spiel erstellen")

    with st.form("setup_form"):
        spiel_id = st.text_input("Spiel-ID (z. B. ID20):")
        gegenstand = st.text_input("Gegenstand (z. B. Äpfel, Konzertkarten):")

        col1, col2 = st.columns(2)
        with col1:
            min_preis = st.number_input("Mindestpreis (€):", min_value=0.0, value=0.50, step=0.10)
        with col2:
            max_preis = st.number_input("Höchstpreis (€):", min_value=0.1, value=5.00, step=0.10)

        submit = st.form_submit_button("Spiel starten")

        if submit:
            if spiel_id and gegenstand and min_preis < max_preis:
                erfolg = spiel_erstellen(spiel_id, gegenstand, min_preis, max_preis)
                if erfolg:
                    st.success("Spiel erfolgreich erstellt!")
                    # Lehrer-Daten im Session State merken
                    st.session_state.spiel_id = spiel_id
                    st.session_state.ansicht = 'lehrer_dashboard'
                    st.rerun()
                else:
                    st.error("Diese Spiel-ID existiert bereits. Bitte wähle eine andere.")
            else:
                st.warning("Bitte fülle alle Felder korrekt aus (Mindestpreis muss kleiner als Höchstpreis sein).")

    if st.button("Zurück"):
        st.session_state.ansicht = 'startseite'
        st.rerun()

# --- LEHRER BEREICH: DASHBOARD ---
elif st.session_state.ansicht == 'lehrer_dashboard':
    st.header(f"📊 Dashboard - Spiel: {st.session_state.spiel_id}")

    spiel_daten = get_spiel_daten(st.session_state.spiel_id)
    if not spiel_daten:
        st.error("Spiel nicht gefunden.")
        st.stop()

    gegenstand, min_preis, max_preis, aktuelle_runde = spiel_daten
    st.subheader(f"🔄 Aktuelle Runde: {aktuelle_runde} (Handelsobjekt: {gegenstand})")

    # --- DATEN ERST ABFRAGEN ---
    conn = sqlite3.connect('marktspiel.db')
    c = conn.cursor()
    # 1. Anzahl der angemeldeten Schüler
    c.execute("SELECT COUNT(*) FROM Players WHERE spiel_id=?", (st.session_state.spiel_id,))
    anzahl_spieler = c.fetchone()[0]

    # 2. Anzahl der bereits abgegebenen Gebote in DIESER Runde
    c.execute("SELECT COUNT(*) FROM Bids WHERE spiel_id=? AND runde=?", (st.session_state.spiel_id, aktuelle_runde))
    anzahl_gebote = c.fetchone()[0]
    conn.close()

    # --- DANN DIE UI ANZEIGEN ---
    st.write(f"👥 Angemeldete Schüler: {anzahl_spieler}")

    # Jetzt ist 'anzahl_gebote' definiert und st.progress funktioniert!
    fortschritt = anzahl_gebote / anzahl_spieler if anzahl_spieler > 0 else 0.0
    st.progress(fortschritt)
    st.write(f"📝 Gebote abgegeben: {anzahl_gebote} von {anzahl_spieler}")


    st.divider()

    # --- TEST-TOOLS ---
    with st.expander("🧪 Test-Werkzeuge (nur für Entwicklung)", expanded=False):
        if st.button("20 Dummy-Schüler:innen & Gebote erzeugen"):
            generiere_testdaten(st.session_state.spiel_id)
            st.success("Testdaten generiert! Bitte Seite aktualisieren.")
            st.rerun()


    # --- STEUERUNG ---
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Ansicht aktualisieren"):
            st.rerun()

    with col2:
        if st.button("📈 Markt auswerten"):
            if anzahl_gebote > 0:
                transaktionen, gleichgewicht, _, _ = runde_auswerten(st.session_state.spiel_id, aktuelle_runde)
                st.session_state.auswertung_text = f"**Ergebnis Runde {aktuelle_runde}:**\nEs kamen {transaktionen} Geschäfte zustande. Der Gleichgewichtspreis liegt bei ca. {format_preis(gleichgewicht)} €" if gleichgewicht else f"**Ergebnis Runde {aktuelle_runde}:**\nEs kam kein Geschäft zustande. Die Preisvorstellungen lagen zu weit auseinander!"
            else:
                st.warning("Noch keine Gebote abgegeben!")

    with col3:
        if st.button("⏭️ Nächste Runde starten"):
            naechste_runde_starten(st.session_state.spiel_id)
            st.session_state.auswertung_text = ""  # Textfeld zurücksetzen
            st.rerun()

    if 'auswertung_text' in st.session_state and st.session_state.auswertung_text:
        st.divider()  # Optische Trennung von den Buttons
        st.success(st.session_state.auswertung_text)

        # Diagramm direkt im Dashboard anzeigen
        conn = sqlite3.connect('marktspiel.db')
        df_runde = pd.read_sql_query('''
                                     SELECT P.rolle AS Rolle, B.gebot AS Gebot_in_Euro
                                     FROM Bids B
                                              JOIN Players P ON B.spieler_name = P.spieler_name AND B.spiel_id = P.spiel_id
                                     WHERE B.spiel_id = ?
                                       AND B.runde = ?
                                     ''', conn, params=(st.session_state.spiel_id, aktuelle_runde))
        conn.close()

        if not df_runde.empty:
            nachfrage = df_runde[df_runde['Rolle'] == 'Nachfrager']['Gebot_in_Euro'].sort_values(
                ascending=False).tolist()
            angebot = df_runde[df_runde['Rolle'] == 'Anbieter']['Gebot_in_Euro'].sort_values(
                ascending=True).tolist()

            # figsize etwas breiter machen für bessere Beamer-Darstellung
            fig, ax = plt.subplots(figsize=(12, 6))

            # 1. Die originalen Treppen-Funktionen (Schüler-Gebote)
            ax.step(range(1, len(nachfrage) + 1), nachfrage, where='mid', label='Nachfrage (Treppe)', color='#1f77b4',
                    marker='o', linewidth=2)
            ax.step(range(1, len(angebot) + 1), angebot, where='mid', label='Angebot (Treppe)', color='#ff7f0e',
                    marker='o',
                    linewidth=2)

            # Wir ziehen eine Gerade vom ersten bis zum letzten Punkt in einer dunkleren Farbe
            # --- NEU: Die geraden Trendlinien (jetzt transparent!) ---
            if len(nachfrage) > 1:
                ax.plot([1, len(nachfrage)], [nachfrage[0], nachfrage[-1]],
                        color='#104a75', linestyle='-', linewidth=4, label='Nachfrage (Trend)', alpha=0.3)

            if len(angebot) > 1:
                ax.plot([1, len(angebot)], [angebot[0], angebot[-1]],
                        color='#b35900', linestyle='-', linewidth=4, label='Angebot (Trend)', alpha=0.3)
            # ------------------------------------

            ax.set_title(f"Marktgleichgewicht - Runde {aktuelle_runde}", fontsize=16)

            # --- NEU: Eindeutige Beschriftung ---
            ax.set_xlabel("Schüler*innen", fontsize=12)
            ax.set_ylabel("Preis in €", fontsize=12)
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: format_preis(x)))

            # Wir suchen uns die längste Liste (Nachfrager oder Anbieter), um das Maximum der Achse zu kennen
            max_menge = max(len(nachfrage), len(angebot))
            if max_menge > 0:
                ax.set_xticks(range(1, max_menge + 1))

            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend(fontsize=12)

            # st.pyplot zwingt das Diagramm auf die volle Breite der Spalte/Seite
            st.pyplot(fig, use_container_width=True)

    st.divider()

    # --- NEUER BEENDEN BUTTON ---
    if st.button("🛑 Spiel beenden & Gesamtauswertung anzeigen", type="primary"):
        st.session_state.ansicht = 'lehrer_auswertung'
        st.rerun()

# --- LEHRER BEREICH: GESAMTAUSWERTUNG ---
elif st.session_state.ansicht == 'lehrer_auswertung':
    st.header(f"🏁 Gesamtauswertung (Zahlen-Report) - Spiel: {st.session_state.spiel_id}")

    conn = sqlite3.connect('marktspiel.db')
    query = '''
            SELECT B.runde AS Runde, P.rolle AS Rolle, B.gebot AS Gebot, B.spieler_name AS Name
            FROM Bids B
                     JOIN Players P ON B.spieler_name = P.spieler_name AND B.spiel_id = P.spiel_id
            WHERE B.spiel_id = ?
            '''
    df = pd.read_sql_query(query, conn, params=(st.session_state.spiel_id,))
    conn.close()

    if df.empty:
        st.warning("Es wurden noch keine Gebote in diesem Spiel abgegeben.")
    else:
        alle_runden = sorted(df['Runde'].unique())

        from fpdf import FPDF
        import os

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"Marktspiel Auswertung - Spiel-ID: {st.session_state.spiel_id}", ln=True, align='C')
        pdf.ln(5)

        spieler_statistik = {}

        for r in alle_runden:
            r_int = int(r)
            st.subheader(f"📝 Ergebnisse aus Runde {r_int}")

            # --- Wir fangen jetzt die 'matches' auf! ---
            transaktionen, gleichgewicht, _, matches = runde_auswerten(st.session_state.spiel_id, r_int)

            if gleichgewicht is not None:
                fakten_text = f"✅ **Gleichgewichtspreis:** {format_preis(gleichgewicht)} €  |  🤝 **Transaktionen (Verkäufe):** {transaktionen}"
                pdf_fakten = f"Gleichgewichtspreis: {format_preis(gleichgewicht)} EUR  |  Transaktionen: {transaktionen}"
            else:
                fakten_text = f"❌ **Kein Geschäft zustande gekommen** (Preisvorstellungen zu weit entfernt)"
                pdf_fakten = "Kein Geschaeft zustande gekommen."

            st.info(fakten_text)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"Runde {r_int}", ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.cell(0, 8, pdf_fakten, ln=True)

            # --- NEU: ZUSTANDE GEKOMMENE DEALS ANZEIGEN ---
            if matches:
                with st.expander("🤝 Wer hat mit wem gehandelt? (Klick zum Ausklappen)", expanded=False):
                    pdf.set_font("Arial", 'B', 10)
                    pdf.cell(0, 8, "Details der Transaktionen (Deals):", ln=True)
                    pdf.set_font("Arial", '', 10)

                    for m in matches:
                        deal_str = f"🛍️ **{m['kaeufer']}** (bot {format_preis(m['k_preis'])}€) kauft von **{m['verkaeufer']}** (wollte {format_preis(m['v_preis'])}€) ➡️ Preis: **{format_preis(m['deal_preis'])} €**"
                        st.write(deal_str)
                        pdf_deal = f"-> {m['kaeufer']} (bot {format_preis(m['k_preis'])} EUR) kauft von {m['verkaeufer']} (wollte {format_preis(m['v_preis'])} EUR) zum Preis von {format_preis(m['deal_preis'])} EUR"

                        # Text fürs PDF vorbereiten (Umlaute ersetzen)
                        pdf_deal = f"-> {m['kaeufer']} (bot {m['k_preis']:.2f} EUR) kauft von {m['verkaeufer']} (wollte {m['v_preis']:.2f} EUR) zum Preis von {m['deal_preis']:.2f} EUR"
                        pdf_deal = pdf_deal.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
                        pdf.cell(0, 6, pdf_deal, ln=True)

                        k = m['kaeufer']
                        v = m['verkaeufer']
                        p = m['deal_preis']
                        if k not in spieler_statistik: spieler_statistik[k] = {'Rolle': 'Nachfrager', 'Deals': 0,
                                                                               'Geld': 0.0}
                        if v not in spieler_statistik: spieler_statistik[v] = {'Rolle': 'Anbieter', 'Deals': 0,
                                                                               'Geld': 0.0}
                        spieler_statistik[k]['Deals'] += 1;
                        spieler_statistik[k]['Geld'] += p
                        spieler_statistik[v]['Deals'] += 1;
                        spieler_statistik[v]['Geld'] += p
            pdf.ln(5)

            # Tabellendaten
            df_runde = df[df['Runde'] == r_int]
            df_nachfrage = df_runde[df_runde['Rolle'] == 'Nachfrager'].sort_values(by='Gebot', ascending=False)
            df_angebot = df_runde[df_runde['Rolle'] == 'Anbieter'].sort_values(by='Gebot', ascending=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🛒 Nachfrager (Käufer)**")
                df_n_disp = df_nachfrage[['Name', 'Gebot']].copy()
                df_n_disp['Gebot'] = df_n_disp['Gebot'].apply(lambda x: format_preis(x))
                st.dataframe(df_n_disp, hide_index=True, use_container_width=True)
            with col2:
                st.markdown("**🏭 Anbieter (Verkäufer)**")
                df_a_disp = df_angebot[['Name', 'Gebot']].copy()
                df_a_disp['Gebot'] = df_a_disp['Gebot'].apply(lambda x: format_preis(x))
                st.dataframe(df_a_disp, hide_index=True, use_container_width=True)

            # Tabelle ins PDF
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(95, 8, "Nachfrager (Kaeufer - Absteigend)", border=1, align='C')
            pdf.cell(95, 8, "Anbieter (Verkaeufer - Aufsteigend)", border=1, align='C', ln=True)

            pdf.set_font("Arial", '', 10)
            nachfrage_list = df_nachfrage[['Name', 'Gebot']].values.tolist()
            angebot_list = df_angebot[['Name', 'Gebot']].values.tolist()
            max_len = max(len(nachfrage_list), len(angebot_list))

            for i in range(max_len):
                n_text = f"{nachfrage_list[i][0]}: {format_preis(nachfrage_list[i][1])} EUR" if i < len(
                    nachfrage_list) else ""
                a_text = f"{angebot_list[i][0]}: {format_preis(angebot_list[i][1])} EUR" if i < len(
                    angebot_list) else ""
                n_text = n_text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
                a_text = a_text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
                pdf.cell(95, 8, n_text, border=1)
                pdf.cell(95, 8, a_text, border=1, ln=True)

            # --- NEU: DIAGRAMM FÜRS PDF GENERIEREN ---
            pdf.ln(5)  # Etwas Abstand nach der Tabelle

            # 1. Daten extrahieren (nur die Gebote aus der Liste)
            n_preise = [x[1] for x in nachfrage_list]
            a_preise = [x[1] for x in angebot_list]

            # 2. Diagramm unsichtbar im Hintergrund zeichnen
            fig_pdf, ax_pdf = plt.subplots(figsize=(10, 5))
            ax_pdf.step(range(1, len(n_preise) + 1), n_preise, where='mid', label='Nachfrage', color='#1f77b4',
                        marker='o', linewidth=2)
            ax_pdf.step(range(1, len(a_preise) + 1), a_preise, where='mid', label='Angebot', color='#ff7f0e',
                        marker='o', linewidth=2)

            # Die schimmernden Trendlinien auch im PDF
            if len(n_preise) > 1:
                ax_pdf.plot([1, len(n_preise)], [n_preise[0], n_preise[-1]], color='#104a75', linestyle='-',
                            linewidth=4, alpha=0.3)
            if len(a_preise) > 1:
                ax_pdf.plot([1, len(a_preise)], [a_preise[0], a_preise[-1]], color='#b35900', linestyle='-',
                            linewidth=4, alpha=0.3)

            ax_pdf.set_title(f"Marktgleichgewicht - Runde {r_int}", fontsize=14)
            ax_pdf.set_xlabel("", fontsize=10)
            ax_pdf.set_ylabel("Preis in EUR", fontsize=10)
            ax_pdf.grid(True, linestyle='--', alpha=0.7)

            max_m = max(len(n_preise), len(a_preise))
            if max_m > 0:
                ax_pdf.set_xticks(range(1, max_m + 1))

            ax_pdf.legend(fontsize=10)

            # 3. Als Bild speichern, ins PDF packen und direkt wieder löschen
            img_path = f"temp_plot_{r_int}.png"
            fig_pdf.savefig(img_path, bbox_inches='tight')  # bbox_inches='tight' schneidet weiße Ränder ab
            plt.close(fig_pdf)  # WICHTIG: Speicher im Hintergrund wieder freigeben!

            pdf.image(img_path, w=170)  # Bild zentriert einfügen (ca. 170mm breit)

            try:
                os.remove(img_path)
            except:
                pass
            # --- ENDE DIAGRAMM FÜRS PDF ---


            if r != alle_runden[-1]:
                pdf.add_page()
            else:
                pdf.ln(10)

            st.divider()  # Optische Trennung im Streamlit-Dashboard

        st.divider()  # Optische Trennung im Streamlit-Dashboard (DIESE ZEILE GIBT ES SCHON)

        # ==========================================
        # --- NEU: BESTENLISTE AM ENDE DES SPIELS ---
        # ==========================================
        if spieler_statistik:
            st.header("🏆 Gesamtranking & Statistiken")
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Bestenliste & Statistiken", ln=True, align='C')
            pdf.ln(5)

            anbieter_stats = []
            nachfrager_stats = []

            for name, daten in spieler_statistik.items():
                schnitt = daten['Geld'] / daten['Deals'] if daten['Deals'] > 0 else 0
                eintrag = {'Name': name, 'Deals': daten['Deals'], 'Summe': daten['Geld'], 'Schnitt': schnitt}
                if daten['Rolle'] == 'Anbieter':
                    anbieter_stats.append(eintrag)
                else:
                    nachfrager_stats.append(eintrag)

            # Sortieren! Anbieter: Meiste Deals, dann höchster Umsatz. Käufer: Meiste Deals, dann niedrigste Ausgaben.
            anbieter_stats = sorted(anbieter_stats, key=lambda x: (x['Deals'], x['Summe']), reverse=True)
            nachfrager_stats = sorted(nachfrager_stats, key=lambda x: (x['Deals'], -x['Summe']), reverse=True)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Top Verkäufer (Umsatz)")
                df_a = pd.DataFrame(anbieter_stats)
                if not df_a.empty:
                    df_a.columns = ['Name', 'Erfolgreiche Deals', 'Gesamtumsatz (€)', 'Ø Preis (€)']
                    st.dataframe(df_a.style.format(
                        {'Gesamtumsatz (€)': lambda x: format_preis(x), 'Ø Preis (€)': lambda x: format_preis(x)}),
                                 hide_index=True)

            with col2:
                st.subheader("Top Käufer (Schnäppchenjäger)")
                df_n = pd.DataFrame(nachfrager_stats)
                if not df_n.empty:
                    df_n.columns = ['Name', 'Erfolgreiche Deals', 'Ausgaben gesamt (€)', 'Ø Preis (€)']
                    st.dataframe(df_n.style.format(
                        {'Ausgaben gesamt (€)': lambda x: format_preis(x), 'Ø Preis (€)': lambda x: format_preis(x)}),
                                 hide_index=True)


            # --- Ranking ins PDF schreiben ---
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "Top Verkaeufer (Meiste Deals & Hoher Umsatz)", ln=True)
            pdf.set_font("Arial", '', 10)
            for a in anbieter_stats:
                text = f"{a['Name']} -> {a['Deals']} Deals | Umsatz: {format_preis(a['Summe'])} EUR | Durchschnittspreis: {format_preis(a['Schnitt'])} EUR"
                text = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
                pdf.cell(0, 6, text, ln=True)

            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "Top Kaeufer (Meiste Deals & Geringe Ausgaben)", ln=True)
            pdf.set_font("Arial", '', 10)
            for n in nachfrager_stats:
                text = f"{n['Name']} -> {n['Deals']} Deals | Ausgaben: {n['Summe']:.2f} EUR | Durchschnittspreis: {n['Schnitt']:.2f} EUR"
                text = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
                pdf.cell(0, 6, text, ln=True)
        # ==========================================

        st.write("### 📥 Daten exportieren")
        pdf_path = f"auswertung_{st.session_state.spiel_id}.pdf"
        pdf.output(pdf_path, 'F')

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        st.download_button(
            label="📄 PDF-Report herunterladen",
            data=pdf_bytes,
            file_name=pdf_path,
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

        try:
            os.remove(pdf_path)
        except:
            pass

    st.write("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Zurück zur Startseite (Spiel endgültig verlassen)"):
        for key in ['spiel_id', 'auswertung_text']:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.ansicht = 'startseite'
        st.rerun()

# --- SCHÜLER BEREICH ---
elif st.session_state.ansicht == 'schueler_join':
    st.header("Spiel beitreten")

    eingabe_id = st.text_input("Spiel-ID (vom Lehrer):")
    eingabe_name = st.text_input("Dein Vorname:")

    if st.button("Beitreten"):
        if eingabe_id and eingabe_name:
            erfolg, zugewiesene_rolle = spieler_hinzufuegen(eingabe_id, eingabe_name)
            if erfolg:
                st.success(f"Erfolgreich beigetreten! Du bist: **{zugewiesene_rolle}**")
                # Hier merken wir uns Name und ID für diesen Schüler
                st.session_state.spieler_name = eingabe_name
                st.session_state.spiel_id = eingabe_id
                st.session_state.rolle = zugewiesene_rolle
                # NEU: Wir leiten den Schüler in die Spielphase weiter!
                st.session_state.ansicht = 'schueler_spiel'
                st.rerun()
            else:
                st.error("Dieser Name existiert bereits in diesem Spiel. Bitte wähle einen anderen.")
        else:
            st.warning("Bitte ID und Name eingeben!")

    if st.button("Zurück"):
        st.session_state.ansicht = 'startseite'
        st.rerun()

# --- SCHÜLER BEREICH: SPIELPHASE (Marktplatz) ---
elif st.session_state.ansicht == 'schueler_spiel':
    st.header(f"🛒 Marktplatz - Spiel: {st.session_state.spiel_id}")

    # Aktuelle Daten vom Lehrer aus der Datenbank holen
    spiel_daten = get_spiel_daten(st.session_state.spiel_id)

    if spiel_daten:
        gegenstand, min_preis, max_preis, aktuelle_runde = spiel_daten

        st.subheader(f"🔄 Aktuelle Runde: {aktuelle_runde}")
        st.write(f"Hallo **{st.session_state.spieler_name}**! Deine Rolle ist: **{st.session_state.rolle}**")

        # Text je nach Rolle anpassen
        if st.session_state.rolle == "Anbieter":
            st.info(f"Du bist Verkäufer. Zu welchem Preis möchtest du **{gegenstand}** auf dem Markt anbieten?")
        else:
            st.info(f"Du bist Käufer. Was bist du maximal bereit, für **{gegenstand}** zu zahlen?")

        # Formular für die Preiseingabe
        with st.form("gebot_form"):
            # Slider oder Number-Input innerhalb der vom Lehrer gesetzten Grenzen
            mein_gebot = st.number_input("Dein Preis (€):",
                                         min_value=float(min_preis),
                                         max_value=float(max_preis),
                                         value=float(min_preis),
                                         step=0.10)

            submit_gebot = st.form_submit_button("Preis verbindlich eintragen")

            if submit_gebot:
                gebot_abgeben(st.session_state.spieler_name, st.session_state.spiel_id, aktuelle_runde, mein_gebot)
                st.success(
                    f"✅ Dein Gebot von {format_preis(mein_gebot)} € für Runde {aktuelle_runde} wurde gespeichert!")

        # Aktualisieren-Knopf, falls der Lehrer die nächste Runde gestartet hat
        if st.button("🔄 Seite aktualisieren (Warten auf nächste Runde)"):
            st.rerun()

        st.divider()
        st.subheader("Wer ist schon fertig?")
        status_liste = get_abgabe_status(st.session_state.spiel_id, aktuelle_runde)

        # Kurze Zusammenfassung für die Schüler
        fertig = sum(1 for s in status_liste if s[2] > 0)
        st.write(f"Gesamtfortschritt: {fertig} von {len(status_liste)} Schülern haben abgegeben.")

        # Optional: Kleine Icons der Mitschüler (ohne Namen, um Anonymität zu wahren)
        tracker_icons = "".join(["✅" if s[2] > 0 else "⚪" for s in status_liste])
        st.title(tracker_icons)

    else:
        st.error("Fehler: Spieldaten konnten nicht gefunden werden. Vielleicht hat der Lehrer das Spiel beendet?")