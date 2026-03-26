import streamlit as st
import pandas as pd
from fpdf import FPDF


# --- HILFSFUNKTIONEN ---

# Verhindert Fehler, wenn Felder noch leer (None) sind
def val(x):
    return x if x is not None else 0.0


def erstelle_pdf(brutto, vl_ag, st_sv_gehalt, lohnsteuer, kist, kv_an, rv_an, av_an, pv_an, netto, vs, ueberweisung):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 15, "Deine Gehaltsabrechnung 2026", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("helvetica", size=12)

    abrechnungs_daten = [
        ("Bruttogehalt", f"{brutto:.2f} EUR"),
        ("+ VL Arbeitgeber", f"{vl_ag:.2f} EUR"),
        ("Steuer- / SV-Brutto", f"{st_sv_gehalt:.2f} EUR"),
        ("", ""),
        ("- Lohnsteuer", f"{lohnsteuer:.2f} EUR"),
        ("- Kirchensteuer", f"{kist:.2f} EUR"),
        ("- Krankenversicherung (KV)", f"{kv_an:.2f} EUR"),
        ("- Rentenversicherung (RV)", f"{rv_an:.2f} EUR"),
        ("- Arbeitslosenversicherung (AV)", f"{av_an:.2f} EUR"),
        ("- Pflegeversicherung (PV)", f"{pv_an:.2f} EUR"),
        ("", ""),
        ("Nettogehalt", f"{netto:.2f} EUR"),
        ("- Vermoegenswirksames Sparen", f"{vs:.2f} EUR"),
        ("", ""),
    ]

    for position, betrag in abrechnungs_daten:
        if position == "":
            pdf.cell(0, 5, "-" * 60, ln=True)
        else:
            pdf.cell(120, 10, position)
            pdf.cell(50, 10, betrag, ln=True, align="R")

    pdf.set_font("helvetica", "B", 12)
    pdf.cell(120, 10, "Ueberweisungsbetrag")
    pdf.cell(50, 10, f"{ueberweisung:.2f} EUR", ln=True, align="R")

    ausgabe = pdf.output()
    if isinstance(ausgabe, str):
        return ausgabe.encode('latin-1')
    return bytes(ausgabe)


# --- STREAMLIT APP ---

st.set_page_config(page_title="Gehaltsabrechnung interaktiv", page_icon="💶", layout="centered")

st.title("💶 Deine Gehaltsabrechnung (2026)")
st.markdown("""
Fülle das folgende Formular vollständig aus. 
Du musst alle Werte, Beitragsbemessungsgrenzen und Beitragssätze komplett eigenständig eintragen. 
""")

st.header("1. Grunddaten")
col1, col2 = st.columns(2)
with col1:
    brutto_input = st.number_input("Bruttogehalt (€):", min_value=0.0, value=None)
    vl_ag_input = st.number_input("VL Arbeitgeber (€):", min_value=0.0, value=None)
with col2:
    lohnsteuer_input = st.number_input("Lohnsteuer (€):", min_value=0.0, value=None)
    vs_input = st.number_input("Vermögensw. Sparen (€):", min_value=0.0, value=None)

st.header("2. Kirchensteuer")
kist_satz_input = st.number_input("Kirchensteuersatz (in %):", min_value=0.0, max_value=10.0, value=None)

st.header("3. Beitragsbemessungsgrenzen (BBG)")
col_bbg1, col_bbg2 = st.columns(2)
with col_bbg1:
    bbg_kv_pv_input = st.number_input("BBG für KV & PV (€):", min_value=0.0, value=None)
with col_bbg2:
    bbg_rv_av_input = st.number_input("BBG für RV & AV (€):", min_value=0.0, value=None)

st.header("4. Sozialversicherungen (Arbeitnehmeranteil)")
col_satz1, col_satz2 = st.columns(2)
with col_satz1:
    kv_an_input = st.number_input("Krankenversicherung (%):", min_value=0.0, value=None)
    rv_an_input = st.number_input("Rentenversicherung (%):", min_value=0.0, value=None)
with col_satz2:
    av_an_input = st.number_input("Arbeitslosenversicherung (%):", min_value=0.0, value=None)
    pv_an_input = st.number_input("Pflegeversicherung (%):", min_value=0.0, value=None)

st.divider()

# Alles wird erst berechnet, wenn dieser Button gedrückt wird
if st.button("Gehalt berechnen & Auswerten", type="primary"):
    # Werte auslesen (leere Felder werden zu 0.0)
    brutto = val(brutto_input)
    vl_ag = val(vl_ag_input)
    lohnsteuer = val(lohnsteuer_input)
    vs = val(vs_input)

    st_sv_gehalt = brutto + vl_ag

    kist_satz = val(kist_satz_input) / 100
    kist = lohnsteuer * kist_satz

    bbg_kv_pv = val(bbg_kv_pv_input)
    bbg_rv_av = val(bbg_rv_av_input)

    basis_kv_pv = min(st_sv_gehalt, bbg_kv_pv) if bbg_kv_pv > 0 else st_sv_gehalt
    basis_rv_av = min(st_sv_gehalt, bbg_rv_av) if bbg_rv_av > 0 else st_sv_gehalt

    kv_an = basis_kv_pv * (val(kv_an_input) / 100)
    rv_an = basis_rv_av * (val(rv_an_input) / 100)
    av_an = basis_rv_av * (val(av_an_input) / 100)
    pv_an = basis_kv_pv * (val(pv_an_input) / 100)

    abzuege_gesamt = lohnsteuer + kist + kv_an + rv_an + av_an + pv_an
    netto = st_sv_gehalt - abzuege_gesamt
    ueberweisung = netto - vs

    # Ausgabe
    st.header("Ergebnis deiner Abrechnung")

    daten = {
        "Position": [
            "Bruttogehalt", "+ VL Arbeitgeber", "======================", "Steuer- / SV-Brutto",
            "- Lohnsteuer", "- Kirchensteuer", "- Krankenversicherung (KV)", "- Rentenversicherung (RV)",
            "- Arbeitslosenversicherung (AV)", "- Pflegeversicherung (PV)", "======================",
            "Nettogehalt", "- Vermögenswirksames Sparen", "======================", "Überweisungsbetrag"
        ],
        "Betrag (€)": [
            f"{brutto:.2f}", f"{vl_ag:.2f}", "---", f"{st_sv_gehalt:.2f}",
            f"-{lohnsteuer:.2f}", f"-{kist:.2f}", f"-{kv_an:.2f}", f"-{rv_an:.2f}",
            f"-{av_an:.2f}", f"-{pv_an:.2f}", "---", f"{netto:.2f}", f"-{vs:.2f}", "---", f"{ueberweisung:.2f}"
        ]
    }

    st.dataframe(pd.DataFrame(daten), use_container_width=True, hide_index=True)

    col_end1, col_end2 = st.columns(2)
    col_end1.metric("Dein Nettogehalt", f"{netto:.2f} €")
    col_end2.metric("Tatsächliche Überweisung", f"{ueberweisung:.2f} €")

    st.subheader("📄 Ergebnisse sichern")

    pdf_bytes = erstelle_pdf(brutto, vl_ag, st_sv_gehalt, lohnsteuer, kist, kv_an, rv_an, av_an, pv_an, netto, vs,
                             ueberweisung)

    st.download_button(
        label="📥 Gehaltsabrechnung als PDF herunterladen",
        data=pdf_bytes,
        file_name="Gehaltsabrechnung_Ergebnis.pdf",
        mime="application/pdf",
        type="primary"
    )