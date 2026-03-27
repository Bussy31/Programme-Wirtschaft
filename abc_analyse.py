import streamlit as st
import pandas as pd

# --- Setup ---
st.set_page_config(page_title="Profi-Übung: ABC-Analyse", layout="wide")

# CSS für eine bessere Optik der "Header-Zeile" und rahmenlose Pfeile
st.markdown("""
    <style>
    .header-row {
        font-weight: bold;
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    /* Entfernt die Rahmen NUR von den kleinen Hoch/Runter-Pfeilen (Secondary Buttons) */
    button[kind="secondary"] {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        font-size: 1.5rem !important;
    }
    button[kind="secondary"]:hover {
        background-color: #e0f2fe !important;
        color: #0284c7 !important;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Interaktive ABC-Analyse")
st.markdown("Passe Menge und Preis an, sortiere die Artikel per Pfeil und lege die Klassengrenzen fest.")

# --- 1. EINSTELLUNGEN (Grenzwerte selbst festlegen) ---
with st.sidebar:
    st.header("⚙️ Klassengrenzen")
    st.info("Lege fest, bis zu wie viel Prozent der kumulierte Umsatz für die jeweilige Klasse geht.")
    grenze_a = st.slider("A-Güter bis (%)", 0, 100, 80)
    grenze_b = st.slider("B-Güter bis (%)", grenze_a, 100, 95)
    grenze_c = st.slider("C-Güter bis (%)", grenze_b, 100, 100)
    st.write(f"Klassen: A (0-{grenze_a}%), B ({grenze_a}-{grenze_b}%), C ({grenze_b}-{grenze_c}%)")

# --- 2. DATEN & SESSION STATE (Bereits korrekt sortiert!) ---
if 'schueler_liste' not in st.session_state:
    st.session_state.schueler_liste = [
        {'id': 3, 'Artikel': 'Schreibtisch Premium', 'Menge': 5, 'Preis': 1200.0},
        {'id': 5, 'Artikel': 'Bürostuhl', 'Menge': 15, 'Preis': 300.0},
        {'id': 2, 'Artikel': 'Toner Schwarz', 'Menge': 10, 'Preis': 80.0},
        {'id': 1, 'Artikel': 'Druckerpapier', 'Menge': 100, 'Preis': 5.0},
        {'id': 4, 'Artikel': 'Kugelschreiber', 'Menge': 500, 'Preis': 1.0},
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
            <span style="width: 10%;">Menge</span>
            <span style="width: 10%;">Preis/Stk.</span>
            <span style="width: 12%;">Umsatz (€)</span>
            <span style="width: 12%;">Anteil %</span>
            <span style="width: 12%;">Kum. %</span>
            <span style="width: 10%;">Aktion</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. ZEILEN (Horizontal nebeneinander) ---
current_list = st.session_state.schueler_liste

# Gesamtwert vorab berechnen, damit wir die Beispielrechnung in den Feldern live vorbefüllen können
gesamt_umsatz_live = sum(item['Menge'] * item['Preis'] for item in current_list)
live_kumuliert = 0.0

for i, item in enumerate(current_list):
    with st.container():
        cols = st.columns([0.5, 1.5, 1, 1, 1.2, 1.2, 1.2, 1])

        with cols[0]:  # Rang
            st.markdown(f"**{i + 1}.**")

        with cols[1]:  # Artikel
            item['Artikel'] = st.text_input("Artikel", value=item['Artikel'], key=f"art_{item['id']}",
                                            label_visibility="collapsed")

        with cols[2]:  # Menge
            item['Menge'] = st.number_input("Menge", value=int(item['Menge']), key=f"men_{item['id']}",
                                            label_visibility="collapsed", step=1)

        with cols[3]:  # Preis
            item['Preis'] = st.number_input("Preis", value=float(item['Preis']), key=f"pre_{item['id']}",
                                            label_visibility="collapsed", step=0.5)

        # -- Hintergrundrechnung für die Beispiel-Befüllung --
        b_umsatz = float(item['Menge'] * item['Preis'])
        b_anteil = (b_umsatz / gesamt_umsatz_live * 100) if gesamt_umsatz_live > 0 else 0.0
        live_kumuliert += b_anteil

        with cols[4]:  # Umsatz (Vorbefüllt)
            st.number_input("Umsatz", value=b_umsatz, key=f"ums_{item['id']}", label_visibility="collapsed", step=1.0)

        with cols[5]:  # Anteil % (Vorbefüllt)
            st.number_input("Anteil", value=b_anteil, key=f"ant_{item['id']}", label_visibility="collapsed", step=0.01,
                            format="%.2f")

        with cols[6]:  # Kumulierter Anteil % (Vorbefüllt)
            st.number_input("Kumul.", value=live_kumuliert, key=f"kum_{item['id']}", label_visibility="collapsed",
                            step=0.01, format="%.2f")

        with cols[7]:  # Aktion (Rahmenlose Pfeile wie in der Pro-Version)
            c_up, c_down = st.columns(2)
            if c_up.button("↑", key=f"up_{item['id']}", disabled=(i == 0)):
                move_item(i, 'up')
                st.rerun()
            if c_down.button("↓", key=f"down_{item['id']}", disabled=(i == len(current_list) - 1)):
                move_item(i, 'down')
                st.rerun()
    st.divider()

# --- 5. AUSWERTUNG ---
# Durch type="primary" heben wir den Button hervor und er wird vom CSS oben ignoriert
if st.button("Analyse final prüfen", use_container_width=True, type="primary"):
    # Lösung berechnen
    sol_df = pd.DataFrame(current_list)
    sol_df['Echter_Umsatz'] = sol_df['Menge'] * sol_df['Preis']

    # Check 1: Sortierung (Umsatz absteigend)
    is_sorted = all(
        sol_df['Echter_Umsatz'].iloc[j] >= sol_df['Echter_Umsatz'].iloc[j + 1] for j in range(len(sol_df) - 1))

    if not is_sorted:
        st.error(
            "❌ Die Reihenfolge stimmt noch nicht. Der Artikel mit dem höchsten Umsatz muss auf Rang 1! (Benutze die Pfeile zum Sortieren)")
    else:
        # Check 2: Rechenwerte
        fehler = False
        kum_check = 0
        for i, item in enumerate(current_list):
            u_ist = item['Menge'] * item['Preis']
            a_ist = (u_ist / gesamt_umsatz_live) * 100
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
                       f"A bis {grenze_a}%, B bis {grenze_b}%, C bis {grenze_c}%.")
            st.balloons()