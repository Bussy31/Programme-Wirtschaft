import streamlit as st
import pandas as pd
from fpdf import FPDF


# --- HILFSFUNKTION FÜR DEN PDF-EXPORT ---
def erstelle_pdf(brutto, vl_ag, st_sv_gehalt, lohnsteuer, kist, kv_an, rv_an, av_an, pv_an, netto, vs, ueberweisung):
    pdf = FPDF()
    pdf.add_page()

    # Überschrift
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 15, "Deine Gehaltsabrechnung 2026", ln=True, align="C")
    pdf.ln(5)

    # Standard-Schriftart für die Tabelle
    pdf.set_font("helvetica", size=12)

    # Daten für die Tabelle vorbereiten
    abrechnungs_daten = [
        ("Bruttogehalt", f"{brutto:.2f} EUR"),
        ("+ VL Arbeitgeber", f"{vl_ag:.2f} EUR"),
        ("Steuer- / SV-Brutto", f"{st_sv_gehalt:.2f} EUR"),
        ("", ""),  # Leerzeile
        ("- Lohnsteuer", f"{lohnsteuer:.2f} EUR"),
        ("- Kirchensteuer", f"{kist:.2f} EUR"),
        ("- Krankenversicherung (KV)", f"{kv_an:.2f} EUR"),
        ("- Rentenversicherung (RV)", f"{rv_an:.2f} EUR"),
        ("- Arbeitslosenversicherung (AV)", f"{av_an:.2f} EUR"),
        ("- Pflegeversicherung (PV)", f"{pv_an:.2f} EUR"),
        ("", ""),  # Leerzeile
        ("Nettogehalt", f"{netto:.2f} EUR"),
        ("- Vermoegenswirksames Sparen", f"{vs:.2f} EUR"),
        ("", ""),  # Leerzeile
    ]

    # Tabelle ins PDF schreiben
    for position, betrag in abrechnungs_daten:
        if position == "":
            # Trennlinie bei Leerzeilen
            pdf.cell(0, 5, "-" * 60, ln=True)
        else:
            pdf.cell(120, 10, position)
            pdf.cell(50, 10, betrag, ln=True, align="R")

    # Abschlusssumme fett drucken
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(120, 10, "Ueberweisungsbetrag")
    pdf.cell(50, 10, f"{ueberweisung:.2f} EUR", ln=True, align="R")

    # PDF als Bytes zurückgeben (für den Streamlit Download-Button)
    return bytes(pdf.output())


# --- STREAMLIT APP ---

# Konfiguration der Seite
st.set_page_config(page_title="Gehaltsabrechnung interaktiv", page_icon="💶", layout="centered")

st.title("💶 Deine interaktive Gehaltsabrechnung (2026)")
st.markdown("""
Willkommen zur Gehaltsabrechnung! Hier rechnet der Computer nicht einfach alles für dich aus. 
Du musst **Schritt für Schritt** die richtigen Daten eingeben und die korrekten Beitragssätze auswählen. 
Viel Erfolg! 🚀
""")

tab1, tab2, tab3, tab4 = st.tabs(["1️⃣ Grunddaten", "2️⃣ Steuern", "3️⃣ Sozialabgaben", "4️⃣ Ergebnis"])

with tab1:
    st.header("1. Grunddaten eingeben")
    st.info("Trage hier die grundlegenden Gehaltsdaten und die Lohnsteuer laut Tabelle ein.")

    col1, col2 = st.columns(2)
    with col1:
        brutto = st.number_input("Bruttogehalt (€):", min_value=0.0, value=3500.0, step=100.0)
        vl_ag = st.number_input("VL Arbeitgeber (€):", min_value=0.0, value=40.0, step=10.0)
    with col2:
        lohnsteuer = st.number_input("Lohnsteuer (€):", min_value=0.0, value=350.0, step=10.0)
        vs = st.number_input("Vermögensw. Sparen (€):", min_value=0.0, value=40.0, step=10.0)

    st_sv_gehalt = brutto + vl_ag
    st.success(f"Dein Steuer- und SV-Brutto liegt somit bei: **{st_sv_gehalt:.2f} €**")

with tab2:
    st.header("2. Kirchensteuer")
    kist_pflicht = st.radio("Kirchensteuer berechnen?", ["Nein", "Ja"])

    if kist_pflicht == "Ja":
        kist_satz = st.selectbox("Welcher Kirchensteuersatz gilt in NRW?", [0.08, 0.09],
                                 format_func=lambda x: f"{x * 100}%")
        kist = lohnsteuer * kist_satz
    else:
        kist = 0.0

    st.metric("Berechnete Kirchensteuer", f"{kist:.2f} €")

with tab3:
    st.header("3. Die Sozialversicherungen")

    st.subheader("Beitragsbemessungsgrenzen (BBG)")
    col_bbg1, col_bbg2 = st.columns(2)
    with col_bbg1:
        bbg_kv_pv = st.selectbox("BBG für Kranken- & Pflegeversicherung (€):", [5000.00, 5812.50, 8450.00], index=1)
    with col_bbg2:
        bbg_rv_av = st.selectbox("BBG für Renten- & Arbeitslosenversicherung (€):", [5812.50, 7100.00, 8450.00],
                                 index=2)

    basis_kv_pv = min(st_sv_gehalt, bbg_kv_pv)
    basis_rv_av = min(st_sv_gehalt, bbg_rv_av)

    st.subheader("Arbeitnehmeranteil (in %)")
    col_satz1, col_satz2 = st.columns(2)
    with col_satz1:
        kv_an_satz = st.selectbox("Krankenversicherung:", [7.3, 7.8, 14.6], index=1) / 100
        rv_an_satz = st.selectbox("Rentenversicherung:", [9.3, 18.6, 7.5], index=0) / 100
    with col_satz2:
        av_an_satz = st.selectbox("Arbeitslosenversicherung:", [1.2, 1.3, 2.6], index=1) / 100
        pv_an_satz = st.selectbox("Pflegeversicherung:", [1.7, 2.4, 3.4], index=1) / 100

    kv_an = basis_kv_pv * kv_an_satz
    rv_an = basis_rv_av * rv_an_satz
    av_an = basis_rv_av * av_an_satz
    pv_an = basis_kv_pv * pv_an_satz

with tab4:
    st.header("4. Deine Gehaltsabrechnung")

    abzuege_gesamt = lohnsteuer + kist + kv_an + rv_an + av_an + pv_an
    netto = st_sv_gehalt - abzuege_gesamt
    ueberweisung = netto - vs

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

    st.divider()
    col_end1, col_end2 = st.columns(2)
    col_end1.metric("Dein Nettogehalt", f"{netto:.2f} €")
    col_end2.metric("Tatsächliche Überweisung", f"{ueberweisung:.2f} €")

    # --- PDF EXPORT BUTTON ---
    st.subheader("📄 Ergebnisse sichern")
    st.write("Lade dir deine fertige Gehaltsabrechnung als PDF herunter, um sie abzugeben oder abzuheften.")

    # PDF im Hintergrund generieren
    pdf_bytes = erstelle_pdf(brutto, vl_ag, st_sv_gehalt, lohnsteuer, kist, kv_an, rv_an, av_an, pv_an, netto, vs,
                             ueberweisung)

    # Streamlit Download Button
    st.download_button(
        label="📥 Gehaltsabrechnung als PDF herunterladen",
        data=pdf_bytes,
        file_name="Gehaltsabrechnung_2026.pdf",
        mime="application/pdf",
        type="primary"
    )

    if st.button("Abrechnung abschließen! 🎉"):
        st.balloons()