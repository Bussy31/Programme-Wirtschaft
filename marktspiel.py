import streamlit as st
import sqlite3
import pandas as pd

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

    # Alle Gebote der aktuellen Runde mit der jeweiligen Rolle des Schülers abrufen
    c.execute('''
              SELECT B.spieler_name, B.gebot, P.rolle
              FROM Bids B
                       JOIN Players P ON B.spieler_name = P.spieler_name AND B.spiel_id = P.spiel_id
              WHERE B.spiel_id = ?
                AND B.runde = ?
              ''', (spiel_id, runde))

    gebote = c.fetchall()
    conn.close()

    # Listen sortieren für das Marktgleichgewicht
    # Anbieter wollen teuer verkaufen, fangen beim Matchen aber billig an (aufsteigend)
    anbieter_preise = sorted([g[1] for g in gebote if g[2] == 'Anbieter'])
    # Nachfrager wollen billig kaufen, fangen beim Matchen hoch an (absteigend)
    nachfrager_preise = sorted([g[1] for g in gebote if g[2] == 'Nachfrager'], reverse=True)

    transaktionen = 0
    gleichgewichtspreis = None

    # Paare bilden und prüfen, ob ein Handel zustande kommt
    for a_preis, n_preis in zip(anbieter_preise, nachfrager_preise):
        if n_preis >= a_preis:
            transaktionen += 1
            # Als einfachen Gleichgewichtspreis nehmen wir die Mitte der beiden Gebote
            gleichgewichtspreis = (n_preis + a_preis) / 2
        else:
            break  # Sobald ein Käufer weniger zahlen will, als der Verkäufer fordert, stoppt der Handel

    return transaktionen, gleichgewichtspreis, len(gebote)

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

# Initiale Ausführung beim Start
init_db()

# --- STREAMLIT OBERFLÄCHE & NAVIGATION ---

# Session State initialisieren (merkt sich, wo der Nutzer ist)
if 'ansicht' not in st.session_state:
    st.session_state.ansicht = 'startseite'

# --- STARTSEITE ---
if st.session_state.ansicht == 'startseite':
    st.title("🍏 Das Markt & Gleichgewichts-Spiel")
    st.write("Willkommen! Bitte wähle deine Rolle:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👨‍🏫 Ich bin Lehrer (Spiel erstellen)"):
            st.session_state.ansicht = 'lehrer_setup'
            st.rerun()

    with col2:
        if st.button("🧑‍🎓 Ich bin Schüler (Spiel beitreten)"):
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
            if admin_user == "admin" and admin_pass == "6836":
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

    # Spieldaten und aktuelle Runde holen
    spiel_daten = get_spiel_daten(st.session_state.spiel_id)
    if not spiel_daten:
        st.error("Spiel nicht gefunden.")
        st.stop()

    gegenstand, min_preis, max_preis, aktuelle_runde = spiel_daten
    st.subheader(f"🔄 Aktuelle Runde: {aktuelle_runde}")
    st.write(f"Gehandelt wird: **{gegenstand}**")

    # Spieler aus der Datenbank laden
    conn = sqlite3.connect('marktspiel.db')
    c = conn.cursor()
    c.execute("SELECT spieler_name, rolle FROM Players WHERE spiel_id=?", (st.session_state.spiel_id,))
    spieler_liste = c.fetchall()
    conn.close()

    anzahl_spieler = len(spieler_liste)
    st.write(f"👥 Angemeldete Schüler: {anzahl_spieler}")

    # Prüfen, wie viele schon ein Gebot abgegeben haben, um es dem Lehrer anzuzeigen
    _, _, anzahl_gebote = runde_auswerten(st.session_state.spiel_id, aktuelle_runde)

    st.progress(anzahl_gebote / anzahl_spieler if anzahl_spieler > 0 else 0.0)
    st.write(f"📝 Gebote in dieser Runde abgegeben: {anzahl_gebote} von {anzahl_spieler}")

    st.divider()

    # --- STEUERUNG ---
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Ansicht aktualisieren"):
            st.rerun()

    with col2:
        if st.button("📈 Markt auswerten"):
            if anzahl_gebote > 0:
                transaktionen, gleichgewicht, _ = runde_auswerten(st.session_state.spiel_id, aktuelle_runde)
                st.session_state.auswertung_text = f"**Ergebnis Runde {aktuelle_runde}:**\nEs kamen {transaktionen} Geschäfte zustande. Der Gleichgewichtspreis liegt bei ca. {gleichgewicht:.2f} €" if gleichgewicht else f"**Ergebnis Runde {aktuelle_runde}:**\nEs kam kein Geschäft zustande. Die Preisvorstellungen lagen zu weit auseinander!"
            else:
                st.warning("Noch keine Gebote abgegeben!")

    with col3:
        if st.button("⏭️ Nächste Runde starten"):
            naechste_runde_starten(st.session_state.spiel_id)
            st.session_state.auswertung_text = ""  # Textfeld zurücksetzen
            st.rerun()

    # Auswertung anzeigen, falls der Button geklickt wurde
    if 'auswertung_text' in st.session_state and st.session_state.auswertung_text:
        st.success(st.session_state.auswertung_text)

    st.divider()

    # --- NEUER BEENDEN BUTTON ---
    if st.button("🛑 Spiel beenden & Gesamtauswertung anzeigen", type="primary"):
        st.session_state.ansicht = 'lehrer_auswertung'
        st.rerun()

# --- LEHRER BEREICH: GESAMTAUSWERTUNG ---
elif st.session_state.ansicht == 'lehrer_auswertung':
    st.header(f"🏁 Gesamtauswertung - Spiel: {st.session_state.spiel_id}")

    # Daten aus der Datenbank holen und als Pandas Tabelle (DataFrame) aufbereiten
    conn = sqlite3.connect('marktspiel.db')
    query = '''
        SELECT B.runde AS Runde, B.spieler_name AS Name, P.rolle AS Rolle, B.gebot AS Gebot_in_Euro
        FROM Bids B
        JOIN Players P ON B.spieler_name = P.spieler_name AND B.spiel_id = P.spiel_id
        WHERE B.spiel_id = ?
        ORDER BY B.runde ASC, P.rolle ASC, B.gebot_in_Euro DESC
    '''
    df = pd.read_sql_query(query, conn, params=(st.session_state.spiel_id,))
    conn.close()

    if df.empty:
        st.warning("Es wurden keine Gebote in diesem Spiel abgegeben.")
    else:
        st.write("Hier ist die komplette Übersicht aller Runden und Spieler:")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # CSV Export vorbereiten (sep=';' sorgt dafür, dass deutsches Excel das sofort richtig liest)
        csv = df.to_csv(index=False, sep=';', decimal=',').encode('utf-8')

        st.download_button(
            label="📥 Daten als Excel/CSV herunterladen",
            data=csv,
            file_name=f"marktspiel_auswertung_{st.session_state.spiel_id}.csv",
            mime="text/csv",
        )

    st.divider()
    if st.button("Zurück zur Startseite (Spiel endgültig verlassen)"):
        # Session State aufräumen, damit kein altes Spiel im Speicher bleibt
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
                st.success(f"✅ Dein Gebot von {mein_gebot:.2f} € für Runde {aktuelle_runde} wurde gespeichert!")

        # Aktualisieren-Knopf, falls der Lehrer die nächste Runde gestartet hat
        if st.button("🔄 Seite aktualisieren (Warten auf nächste Runde)"):
            st.rerun()

    else:
        st.error("Fehler: Spieldaten konnten nicht gefunden werden. Vielleicht hat der Lehrer das Spiel beendet?")