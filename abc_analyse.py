import streamlit as st
import pandas as pd
import altair as alt
import io

# --- Versuche FPDF für den PDF-Export zu laden ---
try:
    from fpdf import FPDF

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# --- Setup ---
st.set_page_config(page_title="Profi-Übung: ABC-Analyse", layout="wide")

# --- COPYRIGHT FOOTER ---
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

# CSS für softe Optik, perfekte Zentrierung & Buttons
st.markdown("""
    <style>
    /* Styling für die Überschriften: Flexbox für absolute vertikale & horizontale Zentrierung */
    .col-header {
        display: flex;
        align-items: center;       /* Vertikal zentriert */
        justify-content: center;   /* Horizontal zentriert */
        height: 45px;              /* Feste Höhe für saubere Ausrichtung */
        font-weight: 700;
        color: #334155;
        background-color: #e2e8f0; /* Leichtes Grau als Hintergrund */
        border-radius: 4px;
        font-size: 1.05rem;
        margin-bottom: 5px;
    }

    /* Buttons (+, -, Pfeile) in den Blautönen des Diagramms */
    button[kind="secondary"] {
        background-color: #e0f2fe !important; 
        color: #0284c7 !important; 
        border: none !important; 
        border-radius: 6px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out;
    }
    button[kind="secondary"]:hover {
        background-color: #93c5fd !important; 
        color: #ffffff !important;
    }

    /* Millimetergenaue Ausrichtung der Rang-Zahlen an die Textfelder */
    .rang-text {
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 6px; 
        text-align: center;
        color: #334155;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Interaktive ABC-Analyse")
st.markdown("Passe Menge und Preis an, berechne die Anteile und beobachte, wie sich dein Live-Diagramm aufbaut!")

if not PDF_AVAILABLE:
    st.warning(
        "⚠️ Um den PDF-Export nutzen zu können, öffne dein Terminal und installiere FPDF mit: `pip install fpdf`")

# --- 1. EINSTELLUNGEN ---
with st.sidebar:
    st.header("⚙️ Klassengrenzen")
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
    st.session_state.schueler_liste.append({'id': neue_id, 'Artikel': 'Neuer Artikel', 'Menge': 0, 'Preis': 0.0})


# --- ZENTRALES SPALTEN-VERHÄLTNIS ---
COL_RATIOS = [0.6, 1.8, 0.9, 0.9, 1.1, 0.9, 0.9, 0.9, 1.0]

# --- 3. HEADER-ZEILE (Mit kleinen Gaps für eine kompaktere Optik) ---
with st.container(border=True):
    h_cols = st.columns(COL_RATIOS, gap="small")
    headers = ["Rang", "Artikel", "Menge", "Preis", "Umsatz (€)", "Anteil %", "Kum. %", "Klasse", "Aktion"]

    for col, title in zip(h_cols, headers):
        col.markdown(f"<div class='col-header'>{title}</div>", unsafe_allow_html=True)

# --- 4. ZEILEN DER TABELLE ---
current_list = st.session_state.schueler_liste
gesamt_umsatz_live = sum(item['Menge'] * item['Preis'] for item in current_list)
live_kumuliert = 0.0

for i, item in enumerate(current_list):
    with st.container(border=True):
        cols = st.columns(COL_RATIOS, gap="small")

        with cols[0]:
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

        vorauswahl_klasse = "A" if live_kumuliert <= grenze_a + 0.01 else (
            "B" if live_kumuliert <= grenze_b + 0.01 else "C")
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

# --- 5. BUTTONS (+ / -) ---
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
col_space1, col_add, col_remove, col_space2 = st.columns([1.5, 2, 2, 1.5])
with col_add:
    if st.button("➕ Weiteren Artikel hinzufügen", use_container_width=True):
        add_item()
        st.rerun()
with col_remove:
    if st.button("➖ Letzten Artikel entfernen", use_container_width=True, disabled=(len(current_list) <= 1)):
        st.session_state.schueler_liste.pop()
        st.rerun()

st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

# --- 6. LIVE-DIAGRAMM ---
st.subheader("📊 Live-Pareto-Diagramm deiner Eingaben")
st.info(
    "Dieses Diagramm baut sich aus deinen eingegebenen Werten oben auf. Achte darauf, dass die Linie stetig steigt!")

chart_data = pd.DataFrame({
    "Artikel": [f"{i + 1}. {item['Artikel']}" for i, item in enumerate(current_list)],
    "Anteil einzeln (%)": [round(item['eingabe_ant'], 2) for item in current_list],
    "Kumulierter Umsatz (%)": [round(item['eingabe_kum'], 2) for item in current_list]
})

base = alt.Chart(chart_data).encode(x=alt.X("Artikel:N", sort=None, title="Artikel (nach Rang)"))
bars = base.mark_bar(color="#93c5fd", size=40, opacity=0.8).encode(
    y=alt.Y("Anteil einzeln (%):Q", scale=alt.Scale(domain=[0, 100]), title="Prozent (%)"),
    tooltip=[alt.Tooltip("Artikel:N"), alt.Tooltip("Anteil einzeln (%):Q", format=".2f")]
)
line = base.mark_line(color="#0284c7", point=True, strokeWidth=3).encode(
    y=alt.Y("Kumulierter Umsatz (%):Q"),
    tooltip=[alt.Tooltip("Artikel:N"), alt.Tooltip("Kumulierter Umsatz (%):Q", format=".2f")]
)

st.altair_chart(alt.layer(bars, line).properties(height=400), use_container_width=True)

# --- 7. AUSWERTUNG & PDF EXPORT ---
st.markdown("<hr/>", unsafe_allow_html=True)
st.subheader("🏁 Abschluss & Sicherung")

col_prüfen, col_pdf = st.columns(2)

with col_prüfen:
    if st.button("Analyse final prüfen", use_container_width=True, type="primary"):
        sol_df = pd.DataFrame(current_list)
        sol_df['Echter_Umsatz'] = sol_df['Menge'] * sol_df['Preis']
        is_sorted = all(
            sol_df['Echter_Umsatz'].iloc[j] >= sol_df['Echter_Umsatz'].iloc[j + 1] for j in range(len(sol_df) - 1))

        if not is_sorted:
            st.error("❌ Die Reihenfolge stimmt noch nicht. Der höchste Umsatz muss auf Rang 1!")
        else:
            fehler, kum_check = False, 0.0
            for i, item in enumerate(current_list):
                u_ist = item['Menge'] * item['Preis']
                a_ist = (u_ist / gesamt_umsatz_live * 100) if gesamt_umsatz_live > 0 else 0.0
                kum_check += a_ist
                korrekt_klasse = "A" if kum_check <= grenze_a + 0.01 else ("B" if kum_check <= grenze_b + 0.01 else "C")

                if abs(item['eingabe_ums'] - u_ist) > 0.5 or abs(item['eingabe_ant'] - a_ist) > 0.05 or abs(
                        item['eingabe_kum'] - kum_check) > 0.05:
                    st.error(f"❌ Rechenfehler bei Rang {i + 1} ({item['Artikel']}). (Toleranz: ±0,05 % bzw. ±0,50 €)")
                    fehler = True
                    break
                if item['eingabe_kl'] != korrekt_klasse:
                    st.error(f"❌ Falsche Klasse (A, B oder C) bei Rang {i + 1} ({item['Artikel']}).")
                    fehler = True
                    break

            if not fehler:
                st.success("✅ Alles korrekt! Deine Klassifizierung ist perfekt berechnet.")
                st.balloons()

with col_pdf:
    if PDF_AVAILABLE:
        def create_pdf(daten):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Auswertung: ABC-Analyse", ln=True, align="C")
            pdf.ln(5)

            # Tabellenkopf
            pdf.set_font("Arial", 'B', 10)
            pdf.set_fill_color(230, 230, 230)
            headers_pdf = ["Rang", "Artikel", "Menge", "Preis", "Umsatz", "Ant. %", "Kum. %", "Kl."]
            w = [12, 55, 15, 25, 25, 20, 20, 15]  # Spaltenbreiten im PDF

            for i in range(len(headers_pdf)):
                pdf.cell(w[i], 8, headers_pdf[i], border=1, align="C", fill=True)
            pdf.ln()

            # Tabellendaten
            pdf.set_font("Arial", '', 10)
            for i, item in enumerate(daten):
                pdf.cell(w[0], 8, f"{i + 1}.", border=1, align="C")
                pdf.cell(w[1], 8, str(item.get('Artikel', '-')), border=1)
                pdf.cell(w[2], 8, str(item.get('Menge', 0)), border=1, align="C")
                pdf.cell(w[3], 8, f"{item.get('Preis', 0):.2f} EUR", border=1, align="R")
                pdf.cell(w[4], 8, f"{item.get('eingabe_ums', 0):.2f} EUR", border=1, align="R")
                pdf.cell(w[5], 8, f"{item.get('eingabe_ant', 0):.2f} %", border=1, align="R")
                pdf.cell(w[6], 8, f"{item.get('eingabe_kum', 0):.2f} %", border=1, align="R")
                pdf.cell(w[7], 8, str(item.get('eingabe_kl', '-')), border=1, align="C")
                pdf.ln()

            # Ausgabe je nach fpdf Version als String oder Bytes
            try:
                return pdf.output(dest='S').encode('latin-1')
            except AttributeError:
                return pdf.output()


        pdf_bytes = create_pdf(current_list)
        st.download_button(
            label="📄 Ergebnisse als PDF speichern",
            data=pdf_bytes,
            file_name="ABC_Analyse_Auswertung.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.button("📄 PDF Export (Modul 'fpdf' fehlt!)", disabled=True, use_container_width=True)