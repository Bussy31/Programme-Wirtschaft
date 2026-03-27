import streamlit as st
import pandas as pd

# --- Setup ---
st.set_page_config(page_title="ABC-Analyse Pro", layout="wide")

# CSS für ein extrem sauberes UI (ohne Rahmen um die Pfeile)
st.markdown("""
    <style>
    .header-row {
        font-weight: bold;
        background-color: #0284c7;
        color: white;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .stButton button {
        border: none;
        background: transparent;
        font-size: 1.2rem;
        padding: 0;
    }
    .stButton button:hover {
        background: #e0f2fe;
        color: #0284c7;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Interaktives ABC-Analyse Lab")
st.markdown("Berechne die Werte, sortiere die Artikel korrekt und erstelle die Lorenz-Kurve.")

# --- 1. DATENBASIS (Session State) ---
if 'schueler_liste' not in st.session_state:
    st.session_state.schueler_liste = [
        {'id': 1, 'Artikel': 'Schreibtisch Premium', 'Menge': 5, 'Preis': 1200.0},
        {'id': 2, 'Artikel': 'Bürostuhl', 'Menge': 15, 'Preis': 300.0},
        {'id': 3, 'Artikel': 'Toner Schwarz', 'Menge': 10, 'Preis': 80.0},
        {'id': 4, 'Artikel': 'Druckerpapier', 'Menge': 100, 'Preis': 5.0},
        {'id': 5, 'Artikel': 'Kugelschreiber', 'Menge': 500, 'Preis': 1.0},
    ]


def move_item(index, direction):
    liste = st.session_state.schueler_liste
    if direction == 'up' and index > 0:
        liste[index], liste[index - 1] = liste[index - 1], liste[index]
    elif direction == 'down' and index < len(liste) - 1:
        liste[index], liste[index + 1] = liste[index + 1], liste[index]
    st.session_state.schueler_liste = liste


# --- 2. KLASSENGRENZEN EINSTELLEN ---
with st.sidebar:
    st.header("⚙️ Klassengrenzen (%)")
    st.info("Lege die kumulierten Prozentwerte für die Güterklassen fest.")
    g_a = st.number_input("A-Güter bis:", min_value=1, max_value=100, value=80)
    g_b = st.number_input("B-Güter bis:", min_value=g_a, max_value=100, value=95)
    g_c = st.number_input("C-Güter bis:", min_value=g_b, max_value=100, value=100)
    st.caption(f"Logik: A (0-{g_a}%), B ({g_a}-{g_b}%), C ({g_b}-{g_c}%)")

# --- 3. HEADER-ZEILE ---
st.markdown("""
    <div class="header-row">
        <div style="width: 5%;">Rang</div>
        <div style="width: 15%;">Artikel</div>
        <div style="width: 10%;">Menge</div>
        <div style="width: 10%;">Preis (€)</div>
        <div style="width: 12%;">Umsatz (€)</div>
        <div style="width: 12%;">Anteil %</div>
        <div style="width: 12%;">Kum. %</div>
        <div style="width: 10%;">Sortieren</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. ARTIKEL-ZEILEN (Eingabe) ---
current_list = st.session_state.schueler_liste

for i, item in enumerate(current_list):
    cols = st.columns([0.5, 1.5, 1, 1, 1.2, 1.2, 1.2, 1])

    with cols[0]:
        st.write(f"**{i + 1}.**")
    with cols[1]:
        item['Artikel'] = st.text_input("Name", value=item['Artikel'], key=f"n_{item['id']}",
                                        label_visibility="collapsed")
    with cols[2]:
        item['Menge'] = st.number_input("M", value=item['Menge'], key=f"m_{item['id']}", label_visibility="collapsed",
                                        step=1)
    with cols[3]:
        item['Preis'] = st.number_input("P", value=item['Preis'], key=f"p_{item['id']}", label_visibility="collapsed",
                                        step=0.5)
    with cols[4]:
        # Starthilfe: Umsatz wird initial vorgeschlagen
        st.number_input("U", key=f"u_{item['id']}", value=float(item['Menge'] * item['Preis']),
                        label_visibility="collapsed")
    with cols[5]:
        st.number_input("A", key=f"a_{item['id']}", value=0.0, format="%.2f", label_visibility="collapsed")
    with cols[6]:
        st.number_input("K", key=f"k_{item['id']}", value=0.0, format="%.2f", label_visibility="collapsed")
    with cols[7]:
        c1, c2 = st.columns(2)
        if c1.button("↑", key=f"up_{item['id']}", disabled=(i == 0)):
            move_item(i, 'up')
            st.rerun()
        if c2.button("↓", key=f"down_{item['id']}", disabled=(i == len(current_list) - 1)):
            move_item(i, 'down')
            st.rerun()

    st.divider()

# --- 5. VALIDIERUNG & LORENZ-KURVE ---
if st.button("🚀 Analyse prüfen & Diagramm generieren", use_container_width=True, type="primary"):
    total_val = sum(it['Menge'] * it['Preis'] for it in current_list)

    # Check 1: Sortierung
    is_sorted = True
    for j in range(len(current_list) - 1):
        if (current_list[j]['Menge'] * current_list[j]['Preis']) < (
                current_list[j + 1]['Menge'] * current_list[j + 1]['Preis']):
            is_sorted = False
            break

    if not is_sorted:
        st.error("❌ Sortierung falsch! Der Artikel mit dem höchsten Umsatz muss ganz oben stehen.")
    else:
        # Check 2: Werte
        fehler = False
        running_kum = 0
        kumulierte_werte_fuer_chart = [0.0]  # Startpunkt für Diagramm bei 0

        for i, it in enumerate(current_list):
            korrekt_u = it['Menge'] * it['Preis']
            korrekt_a = (korrekt_u / total_val) * 100
            running_kum += korrekt_a
            kumulierte_werte_fuer_chart.append(running_kum)

            s_u = st.session_state.get(f"u_{it['id']}", 0.0)
            s_a = st.session_state.get(f"a_{it['id']}", 0.0)
            s_k = st.session_state.get(f"k_{it['id']}", 0.0)

            # Toleranz für Rundungsfehler
            if abs(s_u - korrekt_u) > 0.1 or abs(s_a - korrekt_a) > 0.5 or abs(s_k - running_kum) > 0.5:
                st.error(f"❌ Rechenfehler bei Rang {i + 1} ({it['Artikel']}). Prüfe deine Eingaben!")
                fehler = True
                break

        if not fehler:
            st.success("🎉 Perfekt gerechnet! Hier ist deine Lorenz-Kurve:")

            # Lorenz-Kurve berechnen (Prozent der Artikel vs. Prozent des Wertes)
            anzahl_artikel = len(current_list)
            artikel_prozent_schritte = [0.0] + [((i + 1) / anzahl_artikel) * 100 for i in range(anzahl_artikel)]

            chart_data = pd.DataFrame({
                "Artikelmenge (%)": artikel_prozent_schritte,
                "Kumulierter Umsatz (%)": kumulierte_werte_fuer_chart
            }).set_index("Artikelmenge (%)")

            # Diagramm zeichnen (Linie statt Balken)
            st.line_chart(chart_data, y="Kumulierter Umsatz (%)", height=400)

            st.info(
                f"**Interpretation:** Wie du im Diagramm siehst, generieren die ersten {artikel_prozent_schritte[1]:.0f}% der Artikel bereits {kumulierte_werte_fuer_chart[1]:.1f}% des gesamten Wertes!")