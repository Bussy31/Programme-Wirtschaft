import streamlit as st
import pandas as pd
import altair as alt

# --- Setup ---
st.set_page_config(page_title="Profi-Übung: ABC-Analyse", layout="wide")

# CSS für eine bessere Optik
st.markdown("""
    <style>
    .header-row {
        font-weight: bold;
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
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
st.markdown(
    "Passe Menge und Preis an, füge neue Artikel hinzu, sortiere sie per Pfeil und lege die Klassengrenzen fest.")

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
            <span style="width: 5%;">Rang</span>
            <span style="width: 15%;">Artikel</span>
            <span style="width: 8%;">Menge</span>
            <span style="width: 8%;">Preis</span>
            <span style="width: 12%;">Umsatz (€)</span>
            <span style="width: 10%;">Anteil %</span>
            <span style="width: 10%;">Kum. %</span>
            <span style="width: 10%;">Klasse</span>
            <span style="width: 10%;">Aktion</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. ZEILEN ---
current_list = st.session_state.schueler_liste

gesamt_umsatz_live = sum(item['Menge'] * item['Preis'] for item in current_list)
live_kumuliert = 0.0

for i, item in enumerate(current_list):
    with st.container():
        cols = st.columns([0.5, 1.5, 0.8, 0.8, 1.2, 1, 1, 1, 1])

        with cols[0]:
            st.markdown(f"**{i + 1}.**")

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
            st.number_input("Umsatz", value=b_umsatz, key=f"ums_{item['id']}", label_visibility="collapsed", step=1.0)

        with cols[5]:
            st.number_input("Anteil", value=b_anteil, key=f"ant_{item['id']}", label_visibility="collapsed", step=0.01,
                            format="%.2f")

        with cols[6]:
            st.number_input("Kumul.", value=live_kumuliert, key=f"kum_{item['id']}", label_visibility="collapsed",
                            step=0.01, format="%.2f")

        with cols[7]:
            st.selectbox("Klasse", options=auswahl_optionen, index=vorauswahl_index, key=f"kl_{item['id']}",
                         label_visibility="collapsed")

        with cols[8]:
            c_up, c_down = st.columns(2)
            if c_up.button("↑", key=f"up_{item['id']}", disabled=(i == 0)):
                move_item(i, 'up')
                st.rerun()
            if c_down.button("↓", key=f"down_{item['id']}", disabled=(i == len(current_list) - 1)):
                move_item(i, 'down')
                st.rerun()
    st.divider()

# NEU: Buttons nebeneinander für Plus und Minus
col_add, col_remove, _ = st.columns([2, 2, 6])
with col_add:
    if st.button("➕ Artikel hinzufügen", use_container_width=True):
        add_item()
        st.rerun()
with col_remove:
    # Button ist deaktiviert, wenn nur noch 1 Artikel da ist
    if st.button("➖ Letzte Zeile löschen", use_container_width=True, disabled=(len(current_list) <= 1)):
        st.session_state.schueler_liste.pop()
        st.rerun()

st.write("")  # Kleiner Abstand zum Prüfen-Button

# --- 5. AUSWERTUNG & DIAGRAMM ---
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

        artikel_namen_fuer_chart = []
        einzel_anteil_fuer_chart = []
        kumulierte_werte_fuer_chart = []

        for i, item in enumerate(current_list):
            u_ist = item['Menge'] * item['Preis']
            a_ist = (u_ist / gesamt_umsatz_live * 100) if gesamt_umsatz_live > 0 else 0.0
            kum_check += a_ist

            artikel_namen_fuer_chart.append(f"{i + 1}. {item['Artikel']}")

            # NEU: Direkt auf 2 Nachkommastellen runden für das Diagramm
            einzel_anteil_fuer_chart.append(round(a_ist, 2))
            kumulierte_werte_fuer_chart.append(round(kum_check, 2))

            if kum_check <= grenze_a + 0.01:
                korrekt_klasse = "A"
            elif kum_check <= grenze_b + 0.01:
                korrekt_klasse = "B"
            else:
                korrekt_klasse = "C"

            u_schueler = st.session_state.get(f"ums_{item['id']}", 0.0)
            a_schueler = st.session_state.get(f"ant_{item['id']}", 0.0)
            k_schueler = st.session_state.get(f"kum_{item['id']}", 0.0)
            klasse_schueler = st.session_state.get(f"kl_{item['id']}", "-")

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
                f"✅ Alles korrekt! Die Klassifizierung lautet: A bis {grenze_a}%, B bis {grenze_b}%, C bis {grenze_c}%. Hier ist dein Pareto-Diagramm:")
            st.balloons()

            chart_data = pd.DataFrame({
                "Artikel": artikel_namen_fuer_chart,
                "Anteil einzeln (%)": einzel_anteil_fuer_chart,
                "Kumulierter Umsatz (%)": kumulierte_werte_fuer_chart
            })

            base = alt.Chart(chart_data).encode(
                x=alt.X("Artikel:N", sort=None, title="Artikel (nach Rang)")
            )

            # NEU: Tooltips hinzugefügt
            bars = base.mark_bar(color="#93c5fd", size=40, opacity=0.8).encode(
                y=alt.Y("Anteil einzeln (%):Q", scale=alt.Scale(domain=[0, 100]), title="Prozent (%)"),
                tooltip=[alt.Tooltip("Artikel:N"), alt.Tooltip("Anteil einzeln (%):Q", format=".2f")]
            )

            # NEU: Tooltips hinzugefügt
            line = base.mark_line(color="#0284c7", point=True, strokeWidth=3).encode(
                y=alt.Y("Kumulierter Umsatz (%):Q"),
                tooltip=[alt.Tooltip("Artikel:N"), alt.Tooltip("Kumulierter Umsatz (%):Q", format=".2f")]
            )

            combo_chart = alt.layer(bars, line).properties(height=400)
            st.altair_chart(combo_chart, use_container_width=True)