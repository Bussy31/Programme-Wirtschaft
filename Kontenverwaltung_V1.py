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
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)  # Trick für die Button-Höhe
        if st.button("🟢 Aktivkonto (Soll)", use_container_width=True):
            name = kto_name.strip()
            if name and name not in st.session_state.konten:
                st.session_state.konten[name] = {"Seite": "Soll", "Soll": [], "Haben": []}
                if eb_wert > 0:
                    st.session_state.konten[name]["Soll"].append((eb_wert, "AB", ""))
                st.success(f"Aktivkonto '{name}' angelegt!")
                st.rerun()
            elif not name:
                st.error("Bitte einen Namen eingeben.")
            else:
                st.error("Konto existiert bereits!")
    with col4:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)  # Trick für die Button-Höhe
        if st.button("🔵 Passivkonto (Haben)", use_container_width=True):
            name = kto_name.strip()
            if name and name not in st.session_state.konten:
                st.session_state.konten[name] = {"Seite": "Haben", "Soll": [], "Haben": []}
                if eb_wert > 0:
                    st.session_state.konten[name]["Haben"].append((eb_wert, "AB", ""))
                st.success(f"Passivkonto '{name}' angelegt!")
                st.rerun()
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

    # Konten-Tabelle und Bearbeitung
    if konten_liste:
        df_konten = pd.DataFrame(konten_liste)
        st.dataframe(df_konten, use_container_width=True, hide_index=True)

        with st.expander("✏️ Konto bearbeiten oder löschen"):
            selected_kto = st.selectbox("Konto auswählen:", options=[k["Konto"] for k in konten_liste])

            if selected_kto:
                # Aktuelle Werte abrufen
                k_daten = st.session_state.konten[selected_kto]
                cur_ab = 0.0
                if k_daten["Soll"] and k_daten["Soll"][0][1] == "AB":
                    cur_ab = k_daten["Soll"][0][0]
                elif k_daten["Haben"] and k_daten["Haben"][0][1] == "AB":
                    cur_ab = k_daten["Haben"][0][0]

                c_edit1, c_edit2, c_edit3 = st.columns(3)
                with c_edit1:
                    new_k_name = st.text_input("Name", value=selected_kto)
                with c_edit2:
                    new_k_ab = st.number_input("AB-Wert (€)", value=float(cur_ab), min_value=0.0, step=100.0)
                with c_edit3:
                    new_k_seite = st.selectbox("Typ", options=["Soll", "Haben"],
                                               index=0 if k_daten["Seite"] == "Soll" else 1)

                cb1, cb2 = st.columns(2)
                with cb1:
                    if st.button("💾 Änderungen speichern", use_container_width=True, type="primary"):
                        new_k_name = new_k_name.strip()
                        if not new_k_name:
                            st.error("Der Name darf nicht leer sein.")
                        elif new_k_name != selected_kto and new_k_name in st.session_state.konten:
                            st.error("Ein Konto mit diesem Namen existiert bereits!")
                        else:
                            # 1. Wenn der Name sich ändert, im Dictionary und im Journal anpassen
                            if new_k_name != selected_kto:
                                st.session_state.konten[new_k_name] = st.session_state.konten.pop(selected_kto)
                                for i, (nr, s, h, b) in enumerate(st.session_state.journal):
                                    new_s = new_k_name if s == selected_kto else s
                                    new_h = new_k_name if h == selected_kto else h
                                    st.session_state.journal[i] = (nr, new_s, new_h, b)

                            # 2. Werte aktualisieren
                            st.session_state.konten[new_k_name]["Seite"] = new_k_seite
                            # Alte AB-Werte entfernen
                            st.session_state.konten[new_k_name]["Soll"] = [x for x in
                                                                           st.session_state.konten[new_k_name]["Soll"]
                                                                           if x[1] != "AB"]
                            st.session_state.konten[new_k_name]["Haben"] = [x for x in
                                                                            st.session_state.konten[new_k_name]["Haben"]
                                                                            if x[1] != "AB"]
                            # Neuen AB-Wert setzen
                            if new_k_ab > 0:
                                st.session_state.konten[new_k_name][new_k_seite].insert(0, (new_k_ab, "AB", ""))

                            rebuild_accounts()
                            st.rerun()

                with cb2:
                    if st.button("🗑️ Konto endgültig löschen", use_container_width=True):
                        in_use = any(s == selected_kto or h == selected_kto for _, s, h, _ in st.session_state.journal)
                        if in_use:
                            st.error("Konto wird im Journal verwendet! Bitte zuerst die Buchungen löschen.")
                        else:
                            del st.session_state.konten[selected_kto]
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

        with st.expander("✏️ Buchung bearbeiten oder löschen"):
            # Ein übersichtliches Wörterbuch für das Dropdown erstellen
            b_dict = {f"Nr. {b[0]}: {b[1]} an {b[2]} ({b[3]:.2f} €)": i for i, b in enumerate(st.session_state.journal)}
            selected_b = st.selectbox("Buchung auswählen:", options=list(b_dict.keys()))

            if selected_b:
                idx = b_dict[selected_b]
                b_nr, old_s, old_h, old_betrag = st.session_state.journal[idx]

                c_edit1, c_edit2, c_edit3 = st.columns(3)
                with c_edit1:
                    new_b_s = st.selectbox("Neues Soll-Konto", options=kto_namen,
                                           index=kto_namen.index(old_s) if old_s in kto_namen else 0)
                with c_edit2:
                    new_b_h = st.selectbox("Neues Haben-Konto", options=kto_namen,
                                           index=kto_namen.index(old_h) if old_h in kto_namen else 0)
                with c_edit3:
                    new_b_betrag = st.number_input("Neuer Betrag (€)", value=float(old_betrag), min_value=0.01,
                                                   step=10.0)

                cb1, cb2 = st.columns(2)
                with cb1:
                    if st.button("💾 Buchung speichern", use_container_width=True, type="primary"):
                        st.session_state.journal[idx] = (b_nr, new_b_s, new_b_h, new_b_betrag)
                        rebuild_accounts()
                        st.rerun()
                with cb2:
                    if st.button("🗑️ Buchung löschen", use_container_width=True):
                        st.session_state.journal.pop(idx)
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
        pdf.set_xy(