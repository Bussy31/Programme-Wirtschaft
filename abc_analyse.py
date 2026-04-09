import streamlit as st
import pandas as pd
import altair as alt
import json
from streamlit_local_storage import LocalStorage
import io

# --- Versuche FPDF für den PDF-Export zu laden ---
try:
    from fpdf import FPDF

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# --- Setup ---
st.set_page_config(page_title="Profi-Übung: ABC-Analyse", layout="wide")

# NEU: Local Storage GANZ OBEN initialisieren, damit er überall verfügbar ist!
localS = LocalStorage()

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

# CSS für anpassungsfähige Optik (Light/Dark Mode kompatibel)
st.markdown("""
    <style>
    /* Millimetergenaue Ausrichtung der Rang-Zahlen an die Textfelder */
    .rang-text {
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 6px; 
        text-align: center;
        color: var(--text-color); /* Passt sich automatisch Hell/Dunkel an */
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗂️ Interaktive ABC-Analyse")
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

    st.markdown("---")  # Trennstrich

    # NEU: Der korrigierte Reset-Button (ohne st.rerun)
    if st.button("🔄 Alles löschen & Neu starten", use_container_width=True):
        # 1. Wir leeren den Zwischenspeicher komplett (alle vorherigen Eingaben weg)
        st.session_state.clear()

        # 2. WICHTIG: Wir setzen diesen Marker, damit das Skript gleich NICHT
        # versucht, die alten Daten wieder aus dem Browser-Speicher zu laden!
        st.session_state.daten_geladen = True

        # 3. Wir stellen die 5 leeren Startzeilen wieder her
        st.session_state.schueler_liste = [
            {'id': 1, 'Artikel': '', 'Menge': 0, 'Preis': 0.0},
            {'id': 2, 'Artikel': '', 'Menge': 0, 'Preis': 0.0},
            {'id': 3, 'Artikel': '', 'Menge': 0, 'Preis': 0.0},
            {'id': 4, 'Artikel': '', 'Menge': 0, 'Preis': 0.0},
            {'id': 5, 'Artikel': '', 'Menge': 0, 'Preis': 0.0},
        ]
        st.rerun()
        # KEIN st.rerun() hier! Das Skript läuft jetzt einfach weiter,
        # zeichnet die leere Tabelle und überschreibt ganz am Ende
        # automatisch den Speicher im Browser.

# --- 2. DATEN & SESSION STATE ---
# Versuchen, alte Daten aus dem Browser zu laden
gespeicherte_daten = localS.getItem("abc_daten")

# Wenn Daten da sind, diese laden (aber nur einmalig beim Start)
if gespeicherte_daten and "daten_geladen" not in st.session_state:
    try:
        st.session_state.schueler_liste = json.loads(gespeicherte_daten)
        st.session_state.daten_geladen = True
    except json.JSONDecodeError:
        pass

# Falls gar keine Daten da sind, leere Standardliste erstellen:
if 'schueler_liste' not in st.session_state:
    st.session_state.schueler_liste = [
        {'id': 1, 'Artikel': '', 'Menge': 0, 'Preis': 0.0},
        {'id': 2, 'Artikel': '', 'Menge': 0, 'Preis': 0.0},
        {'id': 3, 'Artikel': '', 'Menge': 0, 'Preis': 0.0},
        {'id': 4, 'Artikel': '', 'Menge': 0, 'Preis': 0.0},
        {'id': 5, 'Artikel': '', 'Menge': 0, 'Preis': 0.0},
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
    st.session_state.schueler_liste.append({'id': neue_id, 'Artikel': '', 'Menge': 0, 'Preis': 0.0})


# --- ZENTRALES SPALTEN-VERHÄLTNIS ---
COL_RATIOS = [0.6, 1.8, 0.9, 0.9, 1.1, 0.9, 0.9, 0.9, 1.0]

# --- 3. DIE PERFEKTE KOPFZEILE (Light & Dark Mode kompatibel) ---
headers = ["Rang", "Artikel", "Menge", "Preis", "Umsatz (€)", "Anteil %", "Kum. %", "Klasse", "Aktion"]

header_html = "<div style='display: flex; gap: 0.5rem; background-color: var(--secondary-background-color); padding: 12px 15px; border-radius: 8px; margin-bottom: 10px; align-items: center; border: 1px solid var(--border-color);'>"
for ratio, title in zip(COL_RATIOS, headers):
    header_html += f"<div style='flex: {ratio} 1 0%; text-align: center; font-weight: 700; color: var(--text-color); font-size: 1.05rem;'>{title}</div>"
header_html += "</div>"

st.markdown(header_html, unsafe_allow_html=True)

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

        auswahl_optionen = ["-", "A", "B", "C"]

        # --- NEU: Keine Automatik mehr, wir laden nur die vorherige Auswahl ---
        aktueller_wert = item.get('eingabe_kl', '-')
        vorauswahl_index = auswahl_optionen.index(aktueller_wert) if aktueller_wert in auswahl_optionen else 0

        with cols[4]:
            item['eingabe_ums'] = st.number_input("Umsatz", value=b_umsatz, key=f"ums_{item['id']}",
                                                  label_visibility="collapsed", step=1.0)
        with cols[5]:
            # max_value=100.0 entfernt, um Abstürze beim Tippen zu verhindern
            item['eingabe_ant'] = st.number_input("Anteil", value=b_anteil, key=f"ant_{item['id']}",
                                                  label_visibility="collapsed", step=0.01, format="%.2f")
        with cols[6]:
            # max_value=100.5 entfernt, um Abstürze beim Tippen zu verhindern
            item['eingabe_kum'] = st.number_input("Kumul.", value=live_kumuliert, key=f"kum_{item['id']}",
                                                  label_visibility="collapsed", step=0.01, format="%.2f")
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

with col_pdf:
    if PDF_AVAILABLE:
        def create_pdf(daten):
            pdf = FPDF()
            pdf.add_page()

            # Titel
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Auswertung: ABC-Analyse", ln=True, align="C")
            pdf.ln(5)

            # Tabellenkopf
            pdf.set_font("Arial", 'B', 9)
            pdf.set_fill_color(226, 232, 240)  # Passend zum Web-Grau
            headers_pdf = ["Rang", "Artikel", "Menge", "Preis", "Umsatz (Eing.)", "Ant. %", "Kum. %", "Kl."]
            w = [10, 48, 15, 25, 30, 20, 20, 15]  # Breiten (Total = 183, ca. Seitenbreite)

            for i in range(len(headers_pdf)):
                pdf.cell(w[i], 8, headers_pdf[i], border=1, align="C", fill=True)
            pdf.ln()

            # Tabellendaten
            pdf.set_font("Arial", '', 9)
            gesamt_umsatz_echt = sum(item['Menge'] * item['Preis'] for item in daten)

            for i, item in enumerate(daten):
                pdf.cell(w[0], 8, f"{i + 1}.", border=1, align="C")
                artikel_name = str(item.get('Artikel', '-')).encode('latin-1', 'replace').decode('latin-1')
                # Falls das Feld komplett leer ist, einen Bindestrich drucken für die Optik
                if not artikel_name.strip():
                    artikel_name = "-"
                pdf.cell(w[1], 8, artikel_name, border=1)
                pdf.cell(w[2], 8, str(item.get('Menge', 0)), border=1, align="C")
                pdf.cell(w[3], 8, f"{item.get('Preis', 0):.2f} EUR", border=1, align="R")

                # Werte aus den Eingabefeldern der SuS
                pdf.cell(w[4], 8, f"{item.get('eingabe_ums', 0):.2f} EUR", border=1, align="R")
                pdf.cell(w[5], 8, f"{item.get('eingabe_ant', 0):.2f} %", border=1, align="R")
                pdf.cell(w[6], 8, f"{item.get('eingabe_kum', 0):.2f} %", border=1, align="R")
                pdf.cell(w[7], 8, str(item.get('eingabe_kl', '-')), border=1, align="C")
                pdf.ln()

            # Rechenweg für die SuS!
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "Detaillierte Rechenwege (Musterloesung):", ln=True)

            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"Gesamtumsatz = Summe aller Umsaetze = {gesamt_umsatz_echt:,.2f} EUR", ln=True)
            pdf.ln(4)

            kum_ist = 0.0
            for i, item in enumerate(daten):
                u_ist = item['Menge'] * item['Preis']
                a_ist = (u_ist / gesamt_umsatz_echt * 100) if gesamt_umsatz_echt > 0 else 0.0
                kum_alt = kum_ist
                kum_ist += a_ist

                klasse = "A" if kum_ist <= grenze_a + 0.01 else ("B" if kum_ist <= grenze_b + 0.01 else "C")
                artikel_name = str(item.get('Artikel', '-')).encode('latin-1', 'replace').decode('latin-1')
                if not artikel_name.strip():
                    artikel_name = f"Artikel {i + 1}"

                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 6, f"Rang {i + 1}: {artikel_name}", ln=True)
                pdf.set_font("Arial", '', 10)
                pdf.cell(0, 5, f"   - Umsatz: {item['Menge']} Stk. * {item['Preis']:.2f} EUR = {u_ist:,.2f} EUR",
                         ln=True)
                pdf.cell(0, 5, f"   - Anteil: ({u_ist:,.2f} EUR / {gesamt_umsatz_echt:,.2f} EUR) * 100 = {a_ist:.2f} %",
                         ln=True)
                pdf.cell(0, 5, f"   - Kumuliert: {kum_alt:.2f} % + {a_ist:.2f} % = {kum_ist:.2f} %", ln=True)
                pdf.cell(0, 5, f"   - Klasse: {klasse} (da Anteil <= Grenze)", ln=True)
                pdf.ln(3)

            # Rückgabe als Download-Bytes
            try:
                return pdf.output(dest='S').encode('latin-1')
            except AttributeError:
                return pdf.output()


        pdf_bytes = create_pdf(current_list)
        st.download_button(
            label="📄 Ergebnisse & Rechenwege als PDF speichern",
            data=pdf_bytes,
            file_name="ABC_Analyse_Auswertung.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.button("📄 PDF Export (Modul 'fpdf' fehlt!)", disabled=True, use_container_width=True)

# --- 8. AUTOMATISCHES SPEICHERN ---
aktuelle_daten = json.dumps(st.session_state.schueler_liste)
if aktuelle_daten != gespeicherte_daten:
    localS.setItem("abc_daten", aktuelle_daten)