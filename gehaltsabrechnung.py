import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile


# --- HILFSFUNKTION FÜR DEN PDF-EXPORT ---
def erstelle_pdf(brutto, vl_ag, st_sv_gehalt, lohnsteuer,
                 kist, kist_satz,
                 kv_an, kv_satz,
                 rv_an, rv_satz,
                 av_an, av_satz,
                 pv_an, pv_satz,
                 netto, vs, ueberweisung):
    pdf = FPDF()
    pdf.add_page()

    # Farben definieren (RGB)
    schwarz = (0, 0, 0)
    dunkelgrau = (100, 100, 100)
    grau_bg = (240, 240, 240)

    # --- HEADER ---
    pdf.set_font("helvetica", "B", 18)
    pdf.set_fill_color(*grau_bg)
    pdf.cell(0, 15, " Entgeltabrechnung 2026", border=0, ln=True, align="L", fill=True)
    pdf.ln(5)

    # --- TABELLENKOPF ---
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(130, 8, "Position", border="B")
    pdf.cell(60, 8, "Betrag", border="B", ln=True, align="R")
    pdf.ln(2)

    # --- HILFSFUNKTION FÜR ZEILEN ---
    def zeile(pos, betrag, font_style="", font_size=11, text_color=schwarz, border=0, fill=False):
        pdf.set_font("helvetica", font_style, font_size)
        pdf.set_text_color(*text_color)
        if fill:
            pdf.set_fill_color(*grau_bg)
        pdf.cell(130, 8, pos, border=border, fill=fill)
        pdf.cell(60, 8, betrag, border=border, ln=True, align="R", fill=fill)

    # --- DATEN EINTRAGEN ---
    # 1. Brutto
    zeile("Bruttogehalt", f"{brutto:.2f} EUR")
    zeile("+ Vermögenswirksame Leistungen (AG)", f"{vl_ag:.2f} EUR")

    # Zwischensumme: SV-Brutto
    zeile("Steuer- / SV-Brutto", f"{st_sv_gehalt:.2f} EUR", font_style="B", border="T", fill=True)
    pdf.ln(3)

    # 2. Steuern
    zeile("Steuern", "", font_style="I", font_size=9, text_color=dunkelgrau)
    zeile("- Lohnsteuer", f"{lohnsteuer:.2f} EUR")
    # %g sorgt dafür, dass 9.0 als 9 und 7.8 als 7.8 angezeigt wird
    zeile(f"- Kirchensteuer ({kist_satz:g} %)", f"{kist:.2f} EUR")
    pdf.ln(2)

    # 3. Sozialversicherungen
    zeile("Sozialversicherungsbeiträge (AN-Anteil)", "", font_style="I", font_size=9, text_color=dunkelgrau)
    zeile(f"- Krankenversicherung ({kv_satz:g} %)", f"{kv_an:.2f} EUR")
    zeile(f"- Rentenversicherung ({rv_satz:g} %)", f"{rv_an:.2f} EUR")
    zeile(f"- Arbeitslosenversicherung ({av_satz:g} %)", f"{av_an:.2f} EUR")
    zeile(f"- Pflegeversicherung ({pv_satz:g} %)", f"{pv_an:.2f} EUR")
    pdf.ln(3)

    # Zwischensumme: Netto
    zeile("Nettogehalt", f"{netto:.2f} EUR", font_style="B", border="T", fill=True)
    pdf.ln(3)

    # 4. Abzüge vom Netto
    zeile("- Vermögenswirksames Sparen (VS)", f"{vs:.2f} EUR")
    pdf.ln(4)

    # 5. AUSZAHLUNGSBETRAG
    pdf.set_text_color(0, 0, 0)  # Schwarz erzwingen für den Rahmen
    zeile("Überweisungsbetrag", f"{ueberweisung:.2f} EUR", font_style="B", font_size=14, border=1, fill=True)

    # --- EXPORT ---
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        tmp.seek(0)
        pdf_bytes = tmp.read()

    return pdf_bytes


# --- STREAMLIT APP ---

st.set_page_config(page_title="Gehaltsabrechnung interaktiv", page_icon="💶", layout="centered")

st.title("💶 Entgeltabrechnung erstellen")
st.info("""
**Willkommen!** Fülle das folgende Formular vollständig aus. Nutze die Tastenfeld-Eingabe oder die +/- Buttons.
Du musst alle Werte, Beitragsbemessungsgrenzen und Beitragssätze komplett eigenständig eintragen. 
""")

# --- Abschnitt 1 ---
with st.container(border=True):
    st.header("🏢 1. Grunddaten")
    col1, col2 = st.columns(2)
    with col1:
        brutto = st.number_input("Bruttogehalt (€):", min_value=0.0, value=0.0, step=100.0)
        vl_ag = st.number_input("VL Arbeitgeber (€):", min_value=0.0, value=0.0, step=10.0)
    with col2:
        lohnsteuer = st.number_input("Lohnsteuer (€):", min_value=0.0, value=0.0, step=10.0)
        vs = st.number_input("Vermögensw. Sparen (€):", min_value=0.0, value=0.0, step=10.0)

# --- Abschnitt 2 ---
with st.container(border=True):
    st.header("⛪ 2. Kirchensteuer")
    kist_satz_input = st.number_input("Kirchensteuersatz (in %):", min_value=0.0, max_value=10.0, value=0.0, step=1.0)

# --- Abschnitt 3 ---
with st.container(border=True):
    st.header("📊 3. Beitragsbemessungsgrenzen (BBG)")
    col_bbg1, col_bbg2 = st.columns(2)
    with col_bbg1:
        bbg_kv_pv = st.number_input("BBG für KV & PV (€):", min_value=0.0, value=0.0, step=100.0)
    with col_bbg2:
        bbg_rv_av = st.number_input("BBG für RV & AV (€):", min_value=0.0, value=0.0, step=100.0)

# --- Abschnitt 4 ---
with st.container(border=True):
    st.header("🏥 4. Sozialversicherungen")
    col_satz1, col_satz2 = st.columns(2)
    with col_satz1:
        kv_an_input = st.number_input("Krankenversicherung (%):", min_value=0.0, value=0.0, step=0.1)
        rv_an_input = st.number_input("Rentenversicherung (%):", min_value=0.0, value=0.0, step=0.1)
    with col_satz2:
        av_an_input = st.number_input("Arbeitslosenversicherung (%):", min_value=0.0, value=0.0, step=0.1)
        pv_an_input = st.number_input("Pflegeversicherung (%):", min_value=0.0, value=0.0, step=0.1)

st.markdown("<br>", unsafe_allow_html=True)

# Alles wird erst berechnet, wenn dieser Button gedrückt wird
if st.button("🚀 Gehalt berechnen & Auswerten", type="primary", use_container_width=True):
    st_sv_gehalt = brutto + vl_ag

    kist_satz = kist_satz_input / 100
    kist = lohnsteuer * kist_satz

    basis_kv_pv = min(st_sv_gehalt, bbg_kv_pv) if bbg_kv_pv > 0 else st_sv_gehalt
    basis_rv_av = min(st_sv_gehalt, bbg_rv_av) if bbg_rv_av > 0 else st_sv_gehalt

    kv_an = basis_kv_pv * (kv_an_input / 100)
    rv_an = basis_rv_av * (rv_an_input / 100)
    av_an = basis_rv_av * (av_an_input / 100)
    pv_an = basis_kv_pv * (pv_an_input / 100)

    abzuege_gesamt = lohnsteuer + kist + kv_an + rv_an + av_an + pv_an
    netto = st_sv_gehalt - abzuege_gesamt
    ueberweisung = netto - vs

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.header("🎯 Ergebnis deiner Abrechnung")

        # Prozentzahlen auch in der App-Vorschau anzeigen lassen
        daten = {
            "Position": [
                "Bruttogehalt", "+ VL Arbeitgeber", "======================", "Steuer- / SV-Brutto",
                "- Lohnsteuer",
                f"- Kirchensteuer ({kist_satz_input:g} %)",
                f"- Krankenversicherung ({kv_an_input:g} %)",
                f"- Rentenversicherung ({rv_an_input:g} %)",
                f"- Arbeitslosenversicherung ({av_an_input:g} %)",
                f"- Pflegeversicherung ({pv_an_input:g} %)",
                "======================",
                "Nettogehalt", "- Vermögenswirksames Sparen", "======================", "Überweisungsbetrag"
            ],
            "Betrag (€)": [
                f"{brutto:.2f}", f"{vl_ag:.2f}", "---", f"{st_sv_gehalt:.2f}",
                f"-{lohnsteuer:.2f}",
                f"-{kist:.2f}",
                f"-{kv_an:.2f}",
                f"-{rv_an:.2f}",
                f"-{av_an:.2f}",
                f"-{pv_an:.2f}",
                "---", f"{netto:.2f}", f"-{vs:.2f}", "---", f"{ueberweisung:.2f}"
            ]
        }

        st.dataframe(pd.DataFrame(daten), use_container_width=True, hide_index=True)

        col_end1, col_end2 = st.columns(2)
        col_end1.metric("Dein Nettogehalt", f"{netto:.2f} €")
        col_end2.metric("Tatsächliche Überweisung", f"{ueberweisung:.2f} €")

        st.divider()
        st.subheader("📄 Ergebnisse sichern")

        # Übergabe der eingegebenen Prozentwerte an die PDF-Funktion
        pdf_bytes = erstelle_pdf(brutto, vl_ag, st_sv_gehalt, lohnsteuer,
                                 kist, kist_satz_input,
                                 kv_an, kv_an_input,
                                 rv_an, rv_an_input,
                                 av_an, av_an_input,
                                 pv_an, pv_an_input,
                                 netto, vs, ueberweisung)

        st.download_button(
            label="📥 Gehaltsabrechnung als PDF herunterladen",
            data=pdf_bytes,
            file_name="Gehaltsabrechnung_Ergebnis.pdf",
            mime="application/pdf",
            type="primary"
        )