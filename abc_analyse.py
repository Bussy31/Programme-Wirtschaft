import streamlit as st
import pandas as pd

# --- Seiten-Setup ---
st.set_page_config(page_title="Übung: ABC-Sortierung", layout="wide")

st.title("📦 Übung: Die ABC-Analyse - Sortierung")
st.markdown("""
**Deine Aufgabe:** Sortiere die untenstehenden Artikel-Kacheln. 
Bringe sie in die korrekte Reihenfolge für die ABC-Analyse (der Artikel mit dem **höchsten Gesamtwert** muss ganz nach oben).
Nutze die Pfeil-Tasten `⬆️` und `⬇️` an den Kacheln, um sie zu verschieben.
""")

st.divider()

# --- 1. DATENBASIS & LOGIK (Im Session State, damit Sortierung bleibt) ---

# Ausgangsdaten (Unsortiert)
if 'schueler_liste' not in st.session_state:
    raw_data = [
        {'id': 1, 'Artikel': 'Druckerpapier', 'Menge': 100, 'Preis': 5},
        {'id': 2, 'Artikel': 'Toner Schwarz', 'Menge': 10, 'Preis': 80},
        {'id': 3, 'Artikel': 'Schreibtisch Premium', 'Menge': 5, 'Preis': 1200},
        {'id': 4, 'Artikel': 'Kugelschreiber', 'Menge': 500, 'Preis': 1},
        {'id': 5, 'Artikel': 'Bürostuhl', 'Menge': 15, 'Preis': 300},
    ]
    # WICHTIG: Wir berechnen den Wert NICHT vor, das sollen die SuS machen.
    st.session_state.schueler_liste = raw_data


# Funktion zum Tauschen von Elementen in der Liste
def move_item(index, direction):
    liste = st.session_state.schueler_liste
    if direction == 'up' and index > 0:
        liste[index], liste[index - 1] = liste[index - 1], liste[index]
    elif direction == 'down' and index < len(liste) - 1:
        liste[index], liste[index + 1] = liste[index + 1], liste[index]
    st.session_state.schueler_liste = liste


# --- 2. DARSTELLUNG ALS KACHELN (Tabellenfrei) ---

st.subheader("Aktuelle Reihenfolge (deine Sortierung):")

current_list = st.session_state.schueler_liste

# Wir iterieren durch die Liste und bauen für jeden Artikel eine Kachel
for i, item in enumerate(current_list):
    # Jede Kachel bekommt einen eigenen Container mit Rahmen
    with st.container(border=True):
        # Spalten-Layout innerhalb der Kachel: [Pfeile, Info, Platzhalter für Schüler-Rechnung]
        col_pfeile, col_info, col_rechnung = st.columns([1, 4, 3])

        # Spalte 1: Die Sortier-Pfeile
        with col_pfeile:
            st.write(" ")  # Ein bisschen Platz nach oben
            # Oben-Pfeil (deaktiviert beim ersten Element)
            if st.button("⬆️", key=f"up_{item['id']}", disabled=(i == 0), use_container_width=True):
                move_item(i, 'up')
                st.rerun()  # Seite neu laden, um Sortierung zu zeigen

            # Unten-Pfeil (deaktiviert beim letzten Element)
            if st.button("⬇️", key=f"down_{item['id']}", disabled=(i == len(current_list) - 1),
                         use_container_width=True):
                move_item(i, 'down')
                st.rerun()

        # Spalte 2: Artikel-Informationen (Fett und groß)
        with col_info:
            st.markdown(f"### Pos. {i + 1}: **{item['Artikel']}**")
            st.markdown(f"Menge: **{item['Menge']}** Stück")
            st.markdown(f"Preis: **{item['Preis']} €** / Stück")

        # Spalte 3: Hier muss der Schüler rechnen
        with col_rechnung:
            st.write(" ")
            # Ein Eingabefeld für den Gesamtwert, den der Schüler ausrechnen muss
            st.number_input(f"Berechneter Gesamtwert (€)", min_value=0.0, step=1.0, key=f"wert_eingabe_{item['id']}")
            st.caption("Rechne: Menge * Preis")

st.divider()


# --- 3. DIE LÖSUNG (Hintergrund-Berechnung zum Vergleich) ---
@st.cache_data  # Cache, damit wir nicht jedes Mal neu rechnen müssen
def get_solution():
    sol_df = pd.DataFrame([
        {'Artikel': 'Druckerpapier', 'Menge': 100, 'Preis': 5},
        {'Artikel': 'Toner Schwarz', 'Menge': 10, 'Preis': 80},
        {'Artikel': 'Schreibtisch Premium', 'Menge': 5, 'Preis': 1200},
        {'Artikel': 'Kugelschreiber', 'Menge': 500, 'Preis': 1},
        {'Artikel': 'Bürostuhl', 'Menge': 15, 'Preis': 300},
    ])
    sol_df['Echter_Wert'] = sol_df['Menge'] * sol_df['Preis']
    # Richtig sortieren
    sol_df_sorted = sol_df.sort_values(by='Echter_Wert', ascending=False).reset_index(drop=True)
    return sol_df_sorted


solution_df = get_solution()

# --- 4. PRÜFUNG ---
if st.button("Sortierung und Werte prüfen", use_container_width=True):
    alles_richtig = True

    # Gehe die aktuelle Schüler-Liste durch und vergleiche mit der Lösung
    for i, item in enumerate(current_list):
        # 1. Check: Artikel-Reihenfolge
        richtiger_artikel_hier = solution_df.loc[i, 'Artikel']
        if item['Artikel'] != richtiger_artikel_hier:
            st.error(
                f"Fehler an Position {i + 1}: Hier sollte nicht '{item['Artikel']}' stehen. Überprüfe den Gesamtwert!")
            alles_richtig = False
            break  # Sobald ein Sortierfehler da ist, brechen wir ab

        # 2. Check: Berechneter Wert (aus dem Session State holen via Key)
        schueler_wert = st.session_state.get(f"wert_eingabe_{item['id']}", 0.0)
        echter_wert = solution_df.loc[i, 'Echter_Wert']

        if abs(schueler_wert - echter_wert) > 0.1:
            st.error(f"Fehler bei '{item['Artikel']}': Dein berechneter Gesamtwert ({schueler_wert} €) ist falsch.")
            alles_richtig = False
            break

    if alles_richtig:
        st.balloons()
        st.success("🎉 Hervorragend! Du hast alle Artikel korrekt berechnet und in die richtige Reihenfolge gebracht.")
        st.write(
            "Jetzt bist du bereit für den nächsten Schritt: Die Berechnung der kumulierten Anteile und die Klassifizierung (A, B, C).")