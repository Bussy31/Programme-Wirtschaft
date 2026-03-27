import streamlit as st
import pandas as pd
from fpdf import FPDF
import uuid
import os


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

    schwarz = (0, 0, 0)
    dunkelgrau = (100, 100, 100)
    grau_bg = (240, 240, 240)

    pdf.set_font("helvetica", "B", 18)
    pdf.set_fill_color(*grau_bg)
    pdf.cell(0, 15, "Entgeltabrechnung", border=0, ln=True, align="L", fill=True)
    pdf.ln(5)

    pdf.set_font("helvetica", "B", 11)
    pdf.cell(130, 8, "Position", border="B")
    pdf.cell(60, 8, "Betrag", border="B", ln=True, align="R")
    pdf.ln(2)

    def zeile(pos, betrag, font_style="", font_size=11, text_color=schwarz, border=0, fill=False):
        pdf.set_font("helvetica", font_style, font_size)
        pdf.set_text_color(*text_color)
        if fill:
            pdf.set_fill_color(*grau_bg)
        pdf.cell(130, 8, pos, border=border, fill=fill)
        pdf.cell(60, 8, betrag, border=border, ln=True, align="R", fill=fill)

    zeile("Bruttogehalt", f"{brutto:.2f} EUR")
    zeile("+ Vermögenswirksame Leistungen (AG)", f"{vl_ag:.2f} EUR")

    zeile("Steuer- / SV-Brutto", f"{st_sv_gehalt:.2f} EUR", font_style="B", border="T", fill=True)
    pdf.ln(3)

    zeile("Steuern", "", font_style="I", font_size=9, text_color=dunkelgrau)
    zeile("- Lohnsteuer", f"{lohnsteuer:.2f} EUR")
    zeile(f"- Kirchensteuer ({kist_satz:g} %)", f"{kist:.2f} EUR")
    pdf.ln(2)

    zeile("Sozialversicherungsbeiträge (AN-Anteil)", "", font_style="I", font_size=9, text_color=dunkelgrau)
    zeile(f"- Krankenversicherung ({kv_satz:g} %)", f"{kv_an:.2f} EUR")
    zeile(f"- Rentenversicherung ({rv_satz:g} %)", f"{rv_an:.2f} EUR")
    zeile(f"- Arbeitslosenversicherung ({av_satz:g} %)", f"{av_an:.2f} EUR")
    zeile(f"- Pflegeversicherung ({pv_satz:g} %)", f"{pv_an:.2f} EUR")
    pdf.ln(3)

    zeile("Nettogehalt", f"{netto:.2f} EUR", font_style="B", border="T", fill=True)
    pdf.ln(3)

    zeile("- Vermögenswirksames Sparen (VS)", f"{vs:.2f} EUR")
    pdf.ln(4)

    pdf.set_text_color(0, 0, 0)
    zeile("Überweisungsbetrag", f"{ueberweisung:.2f} EUR", font_style="B", border=1, fill=True)

    temp_pdf_path = f"temp_loesung_{uuid.uuid4().hex}.pdf"
    pdf.output(temp_pdf_path)

    # Liest das PDF in den Arbeitsspeicher
    with open(temp_pdf_path, "rb") as pdf_file:
        PDFbyte = pdf_file.read()

    # Datei direkt wieder von der Festplatte löschen, um Müll zu vermeiden
    if os.path.exists(temp_pdf_path):
        os.remove(temp_pdf_path)

    return PDFbyte


# --- STREAMLIT APP ---

st.set_page_config(page_title="Entgeltabrechnung", page_icon="💶", layout="centered")

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
        brutto = st.number_input("Bruttogehalt (€):", min_value=0.0, value=None, step=100.0)
        vl_ag = st.number_input("VL Arbeitgeber (€):", min_value=0.0, value=None, step=10.0)
    with col2:
        lohnsteuer = st.number_input("Lohnsteuer (€):", min_value=0.0, value=None, step=10.0)
        vs = st.number_input("Vermögensw. Sparen (€):", min_value=0.0, value=None, step=10.0)

# --- Abschnitt 2 ---
with st.container(border=True):
    st.header("⛪ 2. Kirchensteuer")
    kist_satz_input = st.number_input("Kirchensteuersatz (in %):", min_value=0.0, max_value=10.0, value=None, step=1.0)

# --- Abschnitt 3 ---
with st.container(border=True):
    st.header("📊 3. Beitragsbemessungsgrenzen (BBG)")
    col_bbg1, col_bbg2 = st.columns(2)
    with col_bbg1:
        bbg_kv_pv = st.number_input("BBG für KV & PV (€):", min_value=0.0, value=None, step=100.0)
    with col_bbg2:
        bbg_rv_av = st.number_input("BBG für RV & AV (€):", min_value=0.0, value=None, step=100.0)

# --- Abschnitt 4 ---
with st.container(border=True):
    st.header("🏥 4. Sozialversicherungen (Arbeitnehmeranteil)")
    col_satz1, col_satz2 = st.columns(2)
    with col_satz1:
        kv_an_input = st.number_input("Krankenversicherung (%):", min_value=0.0, value=None, step=0.1)
        rv_an_input = st.number_input("Rentenversicherung (%):", min_value=0.0, value=None, step=0.1)
    with col_satz2:
        av_an_input = st.number_input("Arbeitslosenversicherung (%):", min_value=0.0, value=None, step=0.1)
        pv_an_input = st.number_input("Pflegeversicherung (%):", min_value=0.0, value=None, step=0.1)

st.markdown("<br>", unsafe_allow_html=True)

# Alles wird erst berechnet, wenn dieser Button gedrückt wird
if st.button("🚀 Entgelt berechnen & Auswerten", type="primary", use_container_width=True):
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

        # Einklappbare Tabelle (Expander)
        with st.expander("📋 Detaillierte Abrechnungstabelle anzeigen", expanded=False):
            # Wir nutzen hier eine Markdown-Tabelle. Das erlaubt uns, Zwischensummen fett zu machen
            # und das Design passt sich perfekt an den Hell/Dunkel-Modus von Streamlit an.
            st.markdown("""
                            <style>
                            table {
                                width: 100%;
                            }
                            </style>
                        """, unsafe_allow_html=True)
            tabelle_markdown = f"""
| Position | Betrag (€) |
| :--- | ---: |
| Bruttogehalt | {brutto:.2f} |
| + VL Arbeitgeber | {vl_ag:.2f} |
| **Steuer- / SV-Brutto** | **{st_sv_gehalt:.2f}** |
| - Lohnsteuer | -{lohnsteuer:.2f} |
| - Kirchensteuer ({kist_satz_input:g} %) | -{kist:.2f} |
| - Krankenversicherung ({kv_an_input:g} %) | -{kv_an:.2f} |
| - Rentenversicherung ({rv_an_input:g} %) | -{rv_an:.2f} |
| - Arbeitslosenversicherung ({av_an_input:g} %) | -{av_an:.2f} |
| - Pflegeversicherung ({pv_an_input:g} %) | -{pv_an:.2f} |
| **Nettogehalt** | **{netto:.2f}** |
| - Vermögenswirksames Sparen | -{vs:.2f} |
| **Überweisungsbetrag** | **{ueberweisung:.2f}** |
"""
            st.markdown(tabelle_markdown)

        st.divider()

        pdf_bytes = erstelle_pdf(brutto, vl_ag, st_sv_gehalt, lohnsteuer,
                                 kist, kist_satz_input,
                                 kv_an, kv_an_input,
                                 rv_an, rv_an_input,
                                 av_an, av_an_input,
                                 pv_an, pv_an_input,
                                 netto, vs, ueberweisung)

        st.download_button(
            label="📥 Entgeltabrechnung als PDF herunterladen",
            data=pdf_bytes,
            file_name="Entgeltabrechnung_Ergebnis.pdf",
            mime="application/pdf",
            type="primary"
        )