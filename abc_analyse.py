import streamlit as st
import pandas as pd

# --- Setup ---
st.set_page_config(page_title="Profi-Übung: ABC-Analyse", layout="wide")

# CSS für eine bessere Optik der "Header-Zeile"
st.markdown("""
    <style>
    .header-row {
        font-weight: bold;
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Interaktive ABC-Analyse")
st.markdown("Berechne die Werte, sortiere die Artikel per Pfeil und lege die Klassengrenzen fest.")

# --- 1. EINSTELLUNGEN (Grenzwerte selbst festlegen) ---
with st.sidebar:
    st.header("⚙️ Klassengrenzen")
    st.info("Lege fest, bis zu wie viel Prozent der kumulierte Umsatz für die jeweilige Klasse geht.")
    grenze_a = st.slider("A-Güter bis (%)", 0, 100, 80)
    grenze_b = st.slider("B-Güter bis (%)", grenze_a, 100, 95)
    st.write(f"C-Güter: ab {grenze_b}% bis 100%")

# --- 2. DATEN & SESSION STATE ---
if 'schueler_liste' not in st.session_state:
    st.session_state.schueler_liste = [
        {'id': 1, 'Artikel': 'Druckerpapier', 'Menge': 100, 'Preis': 5},
        {'id': 2, 'Artikel': 'Toner Schwarz', 'Menge': 10, 'Preis': 80},
        {'id': 3, 'Artikel': 'Schreibtisch Premium', 'Menge': 5, 'Preis': 1200},
        {'id': 4, 'Artikel': 'Kugelschreiber', 'Menge': 500, 'Preis': 1},
        {'id': 5, 'Artikel': 'Bürostuhl', 'Menge': 15, 'Preis': 300},
    ]


def move_item(index, direction):
    liste = st.session_state.schueler_liste
    if direction == 'up' and index > 0:
        liste[index], liste[index - 1] = liste[index - 1], liste[index]
    elif direction == 'down' and index < len(liste) - 1:
        liste[index], liste[index + 1] = liste[index + 1], liste[index]
    st.session_state.schueler_liste = liste


# --- 3. HEADER-ZEILE (Horizontal) ---
st.markdown("""
    <div class="header-row">
        <div style="display: flex; justify-content: space-between;">
            <span style="width: 5%;">Rang</span>
            <span style="width: 15%;">Artikel</span>
            <span style="width: 8%;">Menge</span>
            <span style="width: 10%;">Preis/Stk.</span>
            <span style="width: 12%;">Umsatz (€)</span>
            <span style="width: 12%;">Anteil %</span>
            <span style="width: 12%;">Kum. Anteil %</span>
            <span style="width: 10%;">Aktion</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. KACHELN (Horizontal nebeneinander) ---
current_list = st.session_state.schueler_liste
gesamt_umsatz_ueberpruefung = sum(item['Menge'] * item['Preis'] for item in current_list)

for i, item in enumerate(current_list):
    with st.container(border=True):
        # Wir nutzen 8 Spalten für deine gewünschten Werte
        cols = st.columns([0.5, 1.5, 1, 1, 1.5, 1.5, 1.5, 1])

        with cols[0]:  # Rang
            st.markdown(f"**{i + 1}.**")

        with cols[1]:  # Artikel
            st.markdown(f"**{item['Artikel']}**")

        with cols[2]:  # Menge
            st.markdown(f"{item['Menge']}")

        with cols[3]:  # Preis
            st.markdown(f"{item['Preis']} €")

        with cols[4]:  # Umsatz (Eingabe)
            st.number_input("Umsatz", key=f"ums_{item['id']}", label_visibility="collapsed", step=1.0)

        with cols[5]:  # Anteil % (Eingabe)
            st.number_input("Anteil", key=f"ant_{item['id']}", label_visibility="collapsed", step=0.01, format="%.2f")

        with cols[6]:  # Kumulierter Anteil % (Eingabe)
            st.number_input("Kumul.", key=f"kum_{item['id']}", label_visibility="collapsed", step=0.01, format="%.2f")

        with cols[7]:  # Aktion (Pfeile)
            c_up, c_down = st.columns(2)
            if c_up.button("⬆️", key=f"up_{item['id']}", disabled=(i == 0)):
                move_item(i, 'up')
                st.rerun()
            if c_down.button("⬇️", key=f"down_{item['id']}", disabled=(i == len(current_list) - 1)):
                move_item(i, 'down')
                st.rerun()

# --- 5. AUSWERTUNG ---
st.divider()
if st.button("Analyse final prüfen", use_container_width=True):
    # Lösung berechnen
    sol_df = pd.DataFrame(current_list)
    sol_df['Echter_Umsatz'] = sol_df['Menge'] * sol_df['Preis']

    # Check 1: Sortierung (Umsatz absteigend)
    is_sorted = all(
        sol_df['Echter_Umsatz'].iloc[j] >= sol_df['Echter_Umsatz'].iloc[j + 1] for j in range(len(sol_df) - 1))

    if not is_sorted:
        st.error("❌ Die Reihenfolge stimmt noch nicht. Der Artikel mit dem höchsten Umsatz muss auf Rang 1!")
    else:
        # Check 2: Rechenwerte
        fehler = False
        kum_check = 0
        for i, item in enumerate(current_list):
            u_ist = item['Menge'] * item['Preis']
            a_ist = (u_ist / gesamt_umsatz_ueberpruefung) * 100
            kum_check += a_ist

            u_schueler = st.session_state.get(f"ums_{item['id']}", 0.0)
            a_schueler = st.session_state.get(f"ant_{item['id']}", 0.0)
            k_schueler = st.session_state.get(f"kum_{item['id']}", 0.0)

            if abs(u_schueler - u_ist) > 1 or abs(a_schueler - a_ist) > 0.5 or abs(k_schueler - kum_check) > 0.5:
                st.error(f"❌ Rechenfehler bei Rang {i + 1} ({item['Artikel']}).")
                fehler = True
                break

        if not fehler:
            st.success(f"✅ Alles korrekt! Die Klassifizierung lautet: "
                       f"A bis {grenze_a}%, B bis {grenze_b}%, Rest C.")
            st.balloons()