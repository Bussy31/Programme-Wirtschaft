import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Profi-Buchhaltungstrainer 2026 - Ultimate Edition", layout="wide")
st.title("📊 Profi-Buchhaltungstrainer 2026 - Ultimate Edition")

# --- SESSION STATE (Das Gedächtnis der App) ---
if "konten" not in st.session_state:
    st.session_state.konten = {}
if "journal" not in st.session_state:
    st.session_state.journal = []


# --- DATEN-MANAGER ---
def rebuild_accounts():
    """Setzt alle Konten auf den AB zurück und bucht das gesamte Journal neu durch."""
    # 1. Konten auf AB zurücksetzen
    for name, daten in st.session_state.konten.items():
        daten["Soll"] = [x for x in daten["Soll"] if x[1] == "AB"]
        daten["Haben"] = [x for x in daten["Haben"] if x[1] == "AB"]

    # 2. Journal neu durchbuchen
    new_journal = []
    for idx, (old_nr, s, h, b) in enumerate(st.session_state.journal):
        nr = idx + 1
        new_journal.append((nr, s, h, b))
        st.session_state.konten[s]["Soll"].append((b, str(nr), h))
        st.session_state.konten[h]["Haben"].append((b, str(nr), s))
    st.session_state.journal = new_journal


# --- TABS ERSTELLEN ---
tab1, tab2, tab3 = st.tabs(["1. Konten & Eröffnung", "2. Buchen (Journal)", "3. Abschluss & PDF"])

# ==========================================
# TAB 1: KONTEN & ERÖFFNUNG
# ==========================================
with tab1:
    st.subheader("Konto eröffnen")

    # Eingabeformular für neues Konto
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        kto_name = st.text_input("Kontoname:")
    with col2:
        eb_wert = st.number_input("AB-Wert (€):", min_value=0.0, value=0.0, step=100.0)
    with col3:
        if st.button("🟢 Aktivkonto (Soll)", use_container_width=True):
            name = kto_name.strip()
            if name and name not in st.session_state.konten:
                st.session_state.konten[name] = {"Seite": "Soll", "Soll": [], "Haben": []}
                if eb_wert > 0:
                    st.session_state.konten[name]["Soll"].append((eb_wert, "AB", ""))
                st.success(f"Aktivkonto '{name}' angelegt!")
            elif not name:
                st.error("Bitte einen Namen eingeben.")
            else:
                st.error("Konto existiert bereits!")
    with col4:
        if st.button("🔵 Passivkonto (Haben)", use_container_width=True):
            name = kto_name.strip()
            if name and name not in st.session_state.konten:
                st.session_state.konten[name] = {"Seite": "Haben", "Soll": [], "Haben": []}
                if eb_wert > 0:
                    st.session_state.konten[name]["Haben"].append((eb_wert, "AB", ""))
                st.success(f"Passivkonto '{name}' angelegt!")
            elif not name:
                st.error("Bitte einen Namen eingeben.")
            else:
                st.error("Konto existiert bereits!")

    st.divider()

    # Bilanz-Check Berechnung
    sum_aktiv_ab = 0
    sum_passiv_ab = 0
    konten_liste = []

    for name, werte in st.session_state.konten.items():
        s = sum(item[0] for item in werte["Soll"])
        h = sum(item[0] for item in werte["Haben"])
        konten_liste.append({"Konto": name, "Typ": werte["Seite"], "Soll": s, "Haben": h, "Saldo": abs(s - h)})

        if werte["Seite"] == "Soll" and werte["Soll"] and werte["Soll"][0][1] == "AB":
            sum_aktiv_ab += werte["Soll"][0][0]
        if werte["Seite"] == "Haben" and werte["Haben"] and werte["Haben"][0][1] == "AB":
            sum_passiv_ab += werte["Haben"][0][0]

    if len(st.session_state.journal) == 0:
        sum_aktiv = sum_aktiv_ab
        sum_passiv = sum_passiv_ab
    else:
        sum_aktiv = sum(max(0, sum(i[0] for i in v["Soll"]) - sum(i[0] for i in v["Haben"])) for v in
                        st.session_state.konten.values())
        sum_passiv = sum(max(0, sum(i[0] for i in v["Haben"]) - sum(i[0] for i in v["Soll"])) for v in
                         st.session_state.konten.values())

    diff = abs(sum_aktiv - sum_passiv)

    # Bilanz-Check Anzeige
    st.subheader("Bilanz-Check")
    m1, m2, m3 = st.columns(3)
    m1.metric("Summe Aktiv", f"{sum_aktiv:,.2f} €")
    m2.metric("Summe Passiv", f"{sum_passiv:,.2f} €")
    if diff > 0.01:
        m3.error(f"Differenz: {diff:,.2f} €")
    else:
        m3.success(f"Differenz: {diff:,.2f} € (Ausgeglichen!)")

    # Konten-Tabelle
    if konten_liste:
        df_konten = pd.DataFrame(konten_liste)
        st.dataframe(df_konten, use_container_width=True, hide_index=True)

        # Konto löschen (als einfaches Dropdown)
        with st.expander("Konto löschen"):
            kto_to_delete = st.selectbox("Wähle ein Konto zum Löschen", options=[k["Konto"] for k in konten_liste])
            if st.button("Konto endgültig löschen", type="primary"):
                in_use = any(s == kto_to_delete or h == kto_to_delete for _, s, h, _ in st.session_state.journal)
                if in_use:
                    st.error("Konto wird im Journal verwendet! Zuerst Buchung löschen.")
                else:
                    del st.session_state.konten[kto_to_delete]
                    st.success("Gelöscht!")
                    st.rerun()

# ==========================================
# TAB 2: JOURNAL (BUCHEN)
# ==========================================
with tab2:
    st.subheader("Neuer Buchungssatz")

    kto_namen = list(st.session_state.konten.keys())

    if not kto_namen:
        st.info("Bitte lege zuerst unter '1. Konten & Eröffnung' Konten an.")
    else:
        with st.form("buchung_form", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns([2, 1, 2, 2])
            with col1:
                b_soll = st.selectbox("Soll:", options=kto_namen)
            with col2:
                st.markdown("<h4 style='text-align: center; margin-top: 30px;'>an</h4>", unsafe_allow_html=True)
            with col3:
                b_haben = st.selectbox("Haben:", options=kto_namen)
            with col4:
                b_betrag = st.number_input("Betrag (€):", min_value=0.01, value=100.0, step=10.0)

            submit_buchung = st.form_submit_button("Buchen", type="primary", use_container_width=True)

            if submit_buchung:
                nr = len(st.session_state.journal) + 1
                st.session_state.journal.append((nr, b_soll, b_haben, b_betrag))
                rebuild_accounts()
                st.success(f"Erfolgreich gebucht: {b_soll} an {b_haben} ({b_betrag} €)")
                st.rerun()

    st.divider()
    st.subheader("Journal")

    if st.session_state.journal:
        df_journal = pd.DataFrame(st.session_state.journal, columns=["Nr", "Soll", "Haben", "Betrag (€)"])
        st.dataframe(df_journal, use_container_width=True, hide_index=True)

        with st.expander("Buchung löschen"):
            buchung_to_delete = st.selectbox("Wähle Buchungsnummer zum Löschen",
                                             options=[b[0] for b in st.session_state.journal])
            if st.button("Buchung löschen", type="primary"):
                # Finde den Index und lösche
                idx_to_delete = next(i for i, b in enumerate(st.session_state.journal) if b[0] == buchung_to_delete)
                st.session_state.journal.pop(idx_to_delete)
                rebuild_accounts()
                st.rerun()
    else:
        st.write("Noch keine Buchungen vorhanden.")

# ==========================================
# TAB 3: ABSCHLUSS & PDF
# ==========================================
with tab3:
    st.subheader("PDF Lösung generieren")


    # Die originalen PDF-Zeichenfunktionen als Hilfsfunktionen
    def draw_bilanz_pdf(pdf, title, links, rechts):
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(180, 10, title, ln=True, align="C")
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(90, 8, "Aktiva", border="TLB", align="C")
        pdf.cell(90, 8, "Passiva", border="TRB", align="C", ln=True)

        pdf.set_font("Helvetica", "", 10)
        max_len = max(len(links), len(rechts))
        sum_links = sum(val for _, val in links)
        sum_rechts = sum(val for _, val in rechts)

        for i in range(max_len):
            if i < len(links):
                pdf.cell(60, 6, links[i][0][:25], border="L")
                pdf.cell(30, 6, f"{links[i][1]:,.2f}", border="R", align="R")
            else:
                pdf.cell(90, 6, "", border="LR")

            if i < len(rechts):
                pdf.cell(60, 6, rechts[i][0][:25])
                pdf.cell(30, 6, f"{rechts[i][1]:,.2f}", border="R", align="R", ln=True)
            else:
                pdf.cell(90, 6, "", border="R", ln=True)

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 8, "Summe", border="TLB")
        pdf.cell(30, 8, f"{sum_links:,.2f}", border="TRB", align="R")
        pdf.cell(60, 8, "Summe", border="TLB")
        pdf.cell(30, 8, f"{sum_rechts:,.2f}", border="TRB", align="R", ln=True)
        pdf.ln(10)


    def draw_single_t_konto(pdf, x, y, name, werte):
        pdf.set_xy(x, y)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(90, 8, f"S                            {name[:20]}                            H", border="B", align="C")
        y += 8
        pdf.set_xy(x, y)
        pdf.set_font("Helvetica", "", 9)
        max_len = max(len(werte["Soll"]), len(werte["Haben"]))

        for i in range(max_len):
            if i < len(werte["Soll"]):
                val, ref, gkto = werte["Soll"][i]
                s_text = f"{ref}) {gkto}" if gkto else str(ref)
                s_val = f"{val:,.2f}"
            else:
                s_text, s_val = "", ""

            if i < len(werte["Haben"]):
                val, ref, gkto = werte["Haben"][i]
                h_text = f"{ref}) {gkto}" if gkto else str(ref)
                h_val = f"{val:,.2f}"
            else:
                h_text, h_val = "", ""

            pdf.cell(27, 6, s_text[:15], border="L")
            pdf.cell(18, 6, s_val, border="R", align="R")
            pdf.cell(27, 6, h_text[:15])
            pdf.cell(18, 6, h_val, border="R", align="R")
            y += 6
            pdf.set_xy(x, y)

        s_sum = sum(i[0] for i in werte["Soll"])
        h_sum = sum(i[0] for i in werte["Haben"])
        sb = abs(s_sum - h_sum)

        pdf.set_font("Helvetica", "I", 9)
        if s_sum >= h_sum:
            pdf.cell(45, 6, "", border="LR")
            pdf.cell(20, 6, "SB", align="L")
            pdf.cell(25, 6, f"{sb:,.2f}", border="R", align="R")
        else:
            pdf.cell(20, 6, "SB", border="L", align="L")
            pdf.cell(25, 6, f"{sb:,.2f}", border="R", align="R")
            pdf.cell(45, 6, "", border="R")
        y += 6
        pdf.set_xy(x, y)

        max_sum = max(s_sum, h_sum)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(20, 6, "", border="TLB")
        pdf.cell(25, 6, f"{max_sum:,.2f}", border="TRB", align="R")
        pdf.cell(20, 6, "", border="TLB")
        pdf.cell(25, 6, f"{max_sum:,.2f}", border="TRB", align="R")
        return y + 10


    if st.button("📄 PDF generieren & vorbereiten", type="primary"):
        pdf = FPDF()
        pdf.add_page()

        eb_aktiv, eb_passiv = [], []
        for name, daten in st.session_state.konten.items():
            if daten["Seite"] == "Soll" and daten["Soll"] and daten["Soll"][0][1] == "AB":
                eb_aktiv.append((name, daten["Soll"][0][0]))
            if daten["Seite"] == "Haben" and daten["Haben"] and daten["Haben"][0][1] == "AB":
                eb_passiv.append((name, daten["Haben"][0][0]))
        draw_bilanz_pdf(pdf, "Eröffnungsbilanz", eb_aktiv, eb_passiv)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Grundbuch", ln=True)
        pdf.set_font("Helvetica", "", 10)
        if not st.session_state.journal:
            pdf.cell(0, 6, "(Keine Buchungen)", ln=True)
        for nr, s, h, b in st.session_state.journal:
            pdf.cell(0, 6, f"{nr}) {s} {b:,.2f} an {h} {b:,.2f}", ln=True)
        pdf.ln(10)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Hauptbuch (Aktivkonten links, Passivkonten rechts)", ln=True)
        aktiv_konten = [(k, v) for k, v in st.session_state.konten.items() if v["Seite"] == "Soll"]
        passiv_konten = [(k, v) for k, v in st.session_state.konten.items() if v["Seite"] == "Haben"]
        max_konten_len = max(len(aktiv_konten), len(passiv_konten))

        for i in range(max_konten_len):
            start_y = pdf.get_y()
            if start_y > 230:
                pdf.add_page()
                start_y = pdf.get_y()
            y_left = start_y
            y_right = start_y
            if i < len(aktiv_konten):
                y_left = draw_single_t_konto(pdf, 10, start_y, aktiv_konten[i][0], aktiv_konten[i][1])
            if i < len(passiv_konten):
                y_right = draw_single_t_konto(pdf, 105, start_y, passiv_konten[i][0], passiv_konten[i][1])
            pdf.set_y(max(y_left, y_right))
            pdf.set_x(10)

        if pdf.get_y() > 220:
            pdf.add_page()
        else:
            pdf.ln(10)

        sb_aktiv, sb_passiv = [], []
        for name, daten in st.session_state.konten.items():
            s_sum = sum(i[0] for i in daten["Soll"])
            h_sum = sum(i[0] for i in daten["Haben"])
            if s_sum > h_sum:
                sb_aktiv.append((name, s_sum - h_sum))
            elif h_sum > s_sum:
                sb_passiv.append((name, h_sum - s_sum))
            elif s_sum > 0:
                if daten["Seite"] == "Soll":
                    sb_aktiv.append((name, 0.0))
                else:
                    sb_passiv.append((name, 0.0))
        draw_bilanz_pdf(pdf, "Schlussbilanz", sb_aktiv, sb_passiv)

        # PDF in eine temporäre Datei speichern, einlesen und zum Download freigeben
        temp_pdf_path = "temp_loesung.pdf"
        pdf.output(temp_pdf_path)

        with open(temp_pdf_path, "rb") as pdf_file:
            PDFbyte = pdf_file.read()

        st.success("PDF wurde erfolgreich generiert!")
        st.download_button(label="📥 PDF jetzt herunterladen",
                           data=PDFbyte,
                           file_name="Buchhaltung_Loesung_Komplett.pdf",
                           mime='application/octet-stream')