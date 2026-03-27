import streamlit as st
import pandas as pd
import altair as alt

# --- Setup ---
st.set_page_config(page_title="Profi-Übung: ABC-Analyse", layout="wide")

# CSS für eine perfekte, softe Optik
st.markdown("""
    <style>
    .header-row {
        font-weight: bold;
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
    }

    /* Zarte, blaue Färbung für alle Aktions-Buttons (+, -, Pfeile) */
    button[kind="secondary"] {
        background-color: #f0f9ff !important;
        color: #0284c7 !important;
        border: 1px solid #bae6fd !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out;
    }
    button[kind="secondary"]:hover {
        background-color: #e0f2fe !important;
        border-color: #7dd3fc !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }

    /* Millimetergenaue vertikale Ausrichtung der Rang-Zahlen */
    .rang-text {
        font-size: 1rem;
        font-weight: 600;
        margin-top: 8px; 
        text-align: center;
        color: #334155;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Interaktive ABC-Analyse")
st.markdown("Passe Menge und Preis an, berechne die Anteile und beobachte, wie sich dein Live-Diagramm aufbaut!")

# --- 1. EINSTELLUNGEN ---
with st.sidebar:
    st.header("⚙️ Klassengrenzen")
    st.info("Lege fest, bis zu wie viel Prozent der kumulierte Umsatz für die jeweilige Klasse geht.")
    grenze_a = st.slider("A-Güter bis (%)", 0, 100, 80)
    grenze_b = st.slider("B-Güter bis (%)", grenze_a, 100, 95)
    grenze_c = st.slider("C-Güter bis (%)", grenze_b, 100, 100)
    st.write(f"Klassen: A (0-{grenze_a}%), B ({grenze_a}-{grenze_b}%), C ({grenze_b}-{grenze_c}%)")

# --- 2. DATEN & SESSION STATE ---
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


def add_item():
    neue_id = max([item['id'] for item in st.session_state.schueler_liste], default=0) + 1
    st.session_state.schueler_liste.append({
        'id': neue_id,
        'Artikel': 'Neuer Artikel',
        'Menge': 0,
        'Preis': 0.0
    })


# --- 3. HEADER-ZEILE ---
st.markdown("""
    <div class="header-row">
        <div style="display: flex; justify-content: space-between;">
            <span style="width: 5%; text-align: center;">Rang</span>
            <span style="width: 15%;">Artikel</span>
            <span style="width: 8%;">Menge</span>
            <span style="width: 8%;">Preis</span>
            <span style="width: 12%;">Umsatz (€)</span>
            <span style="width: 10%;">Anteil %</span>
            <span style="width: 10%;">Kum. %</span>
            <span style="width: 10%;">Klasse</span>
            <span style="width: 10%; text-align: center;">Aktion</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. ZEILEN DER TABELLE ---
current_list = st.session_state.schueler_liste

gesamt_umsatz_live = sum(item['Menge'] * item['Preis'] for item in current_list)
live_kumuliert = 0.0

for i, item in enumerate(current_list):
    with st.container():
        cols = st.columns([0.5, 1.5, 0.8, 0.8, 1.2, 1, 1, 1, 1])

        with cols[0]:
            # Die Klasse 'rang-text' kümmert sich um die perfekte Ausrichtung
            st.markdown(f"<div class='rang-text'>{i + 1}.</div>", unsafe_allow_html=True)

        with cols[1]:
            item['Artikel'] = st.text_input("Artikel", value=item['Artikel'], key=f"art_{item['id']}",
                                            label_visibility="collapsed")

        with cols[2]:
            item['Menge'] = st.number_input("Menge", value=int(item['Menge']), key=f"men_{item['id']}",
                                            label_visibility="collapsed", step=1)

        with cols[3]:
            item['Preis'] = st.number_input("Preis", value=float(item['Preis']), key=f"pre_{item['id']}",
                                            label_visibility="collapsed", step=0.5)

        b_umsatz = float(item['Menge'] * item['Preis'])
        b_anteil = (b_umsatz / gesamt_umsatz_live * 100) if gesamt_umsatz_live > 0 else 0.0
        live_kumuliert += b_anteil

        if live_kumuliert <= grenze_a + 0.01:
            vorauswahl_klasse = "A"
        elif live_kumuliert <= grenze_b + 0.01:
            vorauswahl_klasse = "B"
        else:
            vorauswahl_klasse = "C"

        auswahl_optionen = ["-", "A", "B", "C"]
        vorauswahl_index = auswahl_optionen.index(vorauswahl_klasse)

        with cols[4]:
            item['eingabe_ums'] = st.number_input("Umsatz", value=b_umsatz, key=f"ums_{item['id']}",
                                                  label_visibility="collapsed", step=1.0)

        with cols[5]:
            item['eingabe_ant'] = st.number_input("Anteil", value=b_anteil, key=f"ant_{item['id']}",
                                                  label_visibility="collapsed", step=0.01, format="%.2f",
                                                  max_value=100.0)

        with cols[6]:
            item['eingabe_kum'] = st.number_input("Kumul.", value=live_kumuliert, key=f"kum_{item['id']}",
                                                  label_visibility="collapsed", step=0.01, format="%.2f",
                                                  max_value=100.5)

        with cols[7]:
            item['eingabe_kl'] = st.selectbox("Klasse", options=auswahl_optionen, index=vorauswahl_index,
                                              key=f"kl_{item['id']}", label_visibility="collapsed")

        with cols[8]:
            c_up, c_down = st.columns(2)
            if c_up.button("↑", key=f"up_{item['id']}", disabled=(i == 0)):
                move_item(i, 'up')
                st.rerun()
            if c_down.button("↓", key=f"down_{item['id']}", disabled=(i == len(current_list) - 1)):
                move_item(i, 'down')
                st.rerun()

    # Unsichtbarer Puffer für eine schöne Struktur ohne harte Linien
    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

# --- 5. GETRENNTE & GERAHMTE BUTTONS (+ / -) ---
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

col_space1, col_add_frame, col_remove_frame, col_space2 = st.columns([1.5, 2, 2, 1.5])

with col_add_frame:
    with st.container(border=True):
        if st.button("➕ Weiteren Artikel hinzufügen", use_container_width=True):
            add_item()
            st.rerun()

with col_remove_frame:
    with st.container(border=True):
        if st.button("➖ Letzten Artikel entfernen", use_container_width=True, disabled=(len(current_list) <= 1)):
            st.session_state.schueler_liste.pop()
            st.rerun()

st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

# --- 6. LIVE-DIAGRAMM ---
st.subheader("📊 Live-Pareto-Diagramm deiner Eingaben")
st.info(
    "Dieses Diagramm baut sich aus deinen eingegebenen Werten oben auf. Achte darauf, dass die Linie stetig steigt!")

artikel_namen_live = [f"{i + 1}. {item['Artikel']}" for i, item in enumerate(current_list)]
anteil_einzeln_live = [round(item['eingabe_ant'], 2) for item in current_list]
kumuliert_live = [round(item['eingabe_kum'], 2) for item in current_list]

chart_data = pd.DataFrame({
    "Artikel": artikel_namen_live,
    "Anteil einzeln (%)": anteil_einzeln_live,
    "Kumulierter Umsatz (%)": kumuliert_live
})

base = alt.Chart(chart_data).encode(
    x=alt.X("Artikel:N", sort=None, title="Artikel (nach Rang)")
)

bars = base.mark_bar(color="#93c5fd", size=40, opacity=0.8).encode(
    y=alt.Y("Anteil einzeln (%):Q", scale=alt.Scale(domain=[0, 100]), title="Prozent (%)"),
    tooltip=[alt.Tooltip("Artikel:N"), alt.Tooltip("Anteil einzeln (%):Q", format=".2f")]
)

line = base.mark_line(color="#0284c7", point=True, strokeWidth=3).encode(
    y=alt.Y("Kumulierter Umsatz (%):Q"),
    tooltip=[alt.Tooltip("Artikel:N"), alt.Tooltip("Kumulierter Umsatz (%):Q", format=".2f")]
)

combo_chart = alt.layer(bars, line).properties(height=400)
st.altair_chart(combo_chart, use_container_width=True)

# --- 7. AUSWERTUNG GANZ UNTEN ---
st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

if st.button("Analyse final prüfen", use_container_width=True, type="primary"):
    sol_df = pd.DataFrame(current_list)
    sol_df['Echter_Umsatz'] = sol_df['Menge'] * sol_df['Preis']

    is_sorted = all(
        sol_df['Echter_Umsatz'].iloc[j] >= sol_df['Echter_Umsatz'].iloc[j + 1] for j in range(len(sol_df) - 1))

    if not is_sorted:
        st.error(
            "❌ Die Reihenfolge stimmt noch nicht. Der Artikel mit dem höchsten Umsatz muss auf Rang 1! (Benutze die Pfeile zum Sortieren)")
    else:
        fehler = False
        kum_check = 0.0

        for i, item in enumerate(current_list):
            u_ist = item['Menge'] * item['Preis']
            a_ist = (u_ist / gesamt_umsatz_live * 100) if gesamt_umsatz_live > 0 else 0.0
            kum_check += a_ist

            if kum_check <= grenze_a + 0.01:
                korrekt_klasse = "A"
            elif kum_check <= grenze_b + 0.01:
                korrekt_klasse = "B"
            else:
                korrekt_klasse = "C"

            u_schueler = item['eingabe_ums']
            a_schueler = item['eingabe_ant']
            k_schueler = item['eingabe_kum']
            klasse_schueler = item['eingabe_kl']

            if abs(u_schueler - u_ist) > 0.5 or abs(a_schueler - a_ist) > 0.05 or abs(k_schueler - kum_check) > 0.05:
                st.error(f"❌ Rechenfehler bei Rang {i + 1} ({item['Artikel']}). (Toleranz: ±0,05 % bzw. ±0,50 €)")
                fehler = True
                break

            if klasse_schueler != korrekt_klasse:
                st.error(f"❌ Falsche Klasse (A, B oder C) bei Rang {i + 1} ({item['Artikel']}).")
                fehler = True
                break

        if not fehler:
            st.success(
                f"✅ Alles korrekt! Deine Klassifizierung ist perfekt berechnet und die Lorenz-Kurve ist stimmig.")
            st.balloons()