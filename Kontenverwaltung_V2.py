import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import copy

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Profi-Buchhaltungstrainer 2026 - Ultimate Edition", layout="wide")
st.title("📊 Profi-Buchhaltungstrainer 2026 - Ultimate Edition")

# --- SESSION STATE (Das Gedächtnis der App) ---
if "konten" not in st.session_state:
    st.session_state.konten = {}
if "journal" not in st.session_state:
    st.session_state.journal = []
if "form_msg" not in st.session_state:
    st.session_state.form_msg = None
if "form_msg_guv" not in st.session_state:
    st.session_state.form_msg_guv = None


# --- DATEN-MANAGER ---
def rebuild_accounts():
    """Setzt alle Konten auf den AB zurück und bucht das gesamte Journal neu durch."""
    for name, daten in st.session_state.konten.items():
        daten["Soll"] = [x for x in daten["Soll"] if x[1] == "AB"]
        daten["Haben"] = [x for x in daten["Haben"] if x[1] == "AB"]

    new_journal = []
    for idx, (old_nr, s, h, b) in enumerate(st.session_state.journal):
        nr = idx + 1
        new_journal.append((nr, s, h, b))
        st.session_state.konten[s]["Soll"].append((b, str(nr), h))
        st.session_state.konten[h]["Haben"].append((b, str(nr), s))
    st.session_state.journal = new_journal


# --- CALLBACK FUNKTION FÜR NEUE KONTEN ---
def add_konto(kategorie, seite):
    name = st.session_state.kto_name_input.strip()
    eb_wert = st.session_state.kto_wert_input

    # Erfolgskonten und GuV haben keinen Anfangsbestand
    if kategorie in ["Aufwand", "Ertrag", "GuV"]:
        eb_wert = 0.0

    if name and name not in st.session_state.konten:
        st.session_state.konten[name] = {"Kategorie": kategorie, "Seite": seite, "Soll": [], "Haben": []}
        if eb_wert > 0:
            st.session_state.konten[name][seite].append((eb_wert, "AB", ""))

        st.session_state.form_msg = {"type": "success", "text": f"{kategorie}skonto '{name}' erfolgreich angelegt!"}

        # GuV Automatik
        if kategorie in ["Aufwand", "Ertrag"] and "GuV" not in st.session_state.konten:
            st.session_state.konten["GuV"] = {"Kategorie": "GuV", "Seite": "Haben", "Soll": [], "Haben": []}
            st.session_state.form_msg_guv = "ℹ️ Info: Das Gewinn- und Verlustkonto (GuV) wurde automatisch mit erzeugt!"

        # Felder zurücksetzen
        st.session_state.kto_name_input = ""
        st.session_state.kto_wert_input = 0.0
    elif not name:
        st.session_state.form_msg = {"type": "error", "text": "Bitte einen Kontonamen eingeben."}
    else:
        st.session_state.form_msg = {"type": "error", "text": "Dieses Konto existiert bereits!"}


# --- TABS ERSTELLEN ---
tab1, tab2, tab3 = st.tabs(["1. Konten & Eröffnung", "2. Buchen (Grundbuch)", "3. Abschluss & PDF"])

# ==========================================
# TAB 1: KONTEN & ERÖFFNUNG
# ==========================================
with tab1:
    st.subheader("Konto eröffnen")

    col_n, col_w = st.columns([2, 1])
    with col_n:
        st.text_input("Kontoname:", key="kto_name_input")
    with col_w:
        st.number_input("AB-Wert (€) (Nur für Bestandskonten):", min_value=0.0, step=100.0, key="kto_wert_input")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("🟢 Aktivkonto", use_container_width=True, on_click=add_konto, args=("Aktiv", "Soll"))
    with col2:
        st.button("🔵 Passivkonto", use_container_width=True, on_click=add_konto, args=("Passiv", "Haben"))
    with col3:
        st.button("🔴 Aufwandskonto", use_container_width=True, on_click=add_konto, args=("Aufwand", "Soll"))
    with col4:
        st.button("🟡 Ertragskonto", use_container_width=True, on_click=add_konto, args=("Ertrag", "Haben"))

    # Meldungen anzeigen
    if st.session_state.form_msg:
        if st.session_state.form_msg["type"] == "success":
            st.success(st.session_state.form_msg["text"])
        else:
            st.error(st.session_state.form_msg["text"])
        st.session_state.form_msg = None

    if st.session_state.form_msg_guv:
        st.info(st.session_state.form_msg_guv)
        st.session_state.form_msg_guv = None

    st.divider()

    # Bilanz-Check Berechnung
    sum_aktiv_ab = 0
    sum_passiv_ab = 0
    konten_liste = []

    for name, werte in st.session_state.konten.items():
        s = sum(item[0] for item in werte["Soll"])
        h = sum(item[0] for item in werte["Haben"])

        # Fallback für alte Speicherstände
        kat = werte.get("Kategorie", "Aktiv" if werte["Seite"] == "Soll" else "Passiv")
        konten_liste.append({"Konto": name, "Kategorie": kat, "Soll": s, "Haben": h, "Saldo": abs(s - h)})

        if kat == "Aktiv" and werte["Soll"] and werte["Soll"][0][1] == "AB":
            sum_aktiv_ab += werte["Soll"][0][0]
        if kat == "Passiv" and werte["Haben"] and werte["Haben"][0][1] == "AB":
            sum_passiv_ab += werte["Haben"][0][0]

    # Differenz für Laufende Buchungen
    sum_aktiv = sum_aktiv_ab
    sum_passiv = sum_passiv_ab
    if len(st.session_state.journal) > 0:
        sum_aktiv = sum(max(0, sum(i[0] for i in v["Soll"]) - sum(i[0] for i in v["Haben"])) for v in
                        st.session_state.konten.values() if v.get("Kategorie") == "Aktiv")
        sum_passiv = sum(max(0, sum(i[0] for i in v["Haben"]) - sum(i[0] for i in v["Soll"])) for v in
                         st.session_state.konten.values() if v.get("Kategorie") == "Passiv")

    # + Eigenkapital / GuV Ausgleich grob für Anzeige (Die echte Bilanz am Ende macht es per Abschluss)
    diff = abs(sum_aktiv_ab - sum_passiv_ab)

    st.subheader("Eröffnungsbilanz-Check")
    m1, m2, m3 = st.columns(3)
    m1.metric("Summe Aktiv (AB)", f"{sum_aktiv_ab:,.2f} €")
    m2.metric("Summe Passiv (AB)", f"{sum_passiv_ab:,.2f} €")
    m3.metric("Differenz", f"{diff:,.2f} €")

    if diff > 0.01:
        st.error(f"⚠️ Achtung: Die Eröffnungsbilanz ist nicht ausgeglichen! (Differenz: {diff:,.2f} €)")
    elif sum_aktiv_ab > 0:
        st.success("✅ Die Eröffnungsbilanz ist perfekt ausgeglichen!")

    if konten_liste:
        df_konten = pd.DataFrame(konten_liste)
        st.dataframe(df_konten, use_container_width=True, hide_index=True)

        with st.expander("✏️ Konto bearbeiten oder löschen"):
            selected_kto = st.selectbox("Konto auswählen:", options=[k["Konto"] for k in konten_liste])

            if selected_kto:
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
                    kat_options = ["Aktiv", "Passiv", "Aufwand", "Ertrag", "GuV"]
                    current_kat = k_daten.get("Kategorie", "Aktiv")
                    new_k_kat = st.selectbox("Kategorie", options=kat_options, index=kat_options.index(current_kat))

                cb1, cb2 = st.columns(2)
                with cb1:
                    if st.button("💾 Änderungen speichern", use_container_width=True, type="primary"):
                        if not new_k_name.strip():
                            st.error("Der Name darf nicht leer sein.")
                        elif new_k_name != selected_kto and new_k_name in st.session_state.konten:
                            st.error("Konto existiert bereits!")
                        else:
                            new_seite = "Soll" if new_k_kat in ["Aktiv", "Aufwand"] else "Haben"
                            if new_k_kat in ["Aufwand", "Ertrag",
                                             "GuV"]: new_k_ab = 0.0  # Erzwinge AB=0 für Erfolgskonten

                            if new_k_name != selected_kto:
                                st.session_state.konten[new_k_name] = st.session_state.konten.pop(selected_kto)
                                for i, (nr, s, h, b) in enumerate(st.session_state.journal):
                                    st.session_state.journal[i] = (nr, new_k_name if s == selected_kto else s,
                                                                   new_k_name if h == selected_kto else h, b)

                            st.session_state.konten[new_k_name]["Kategorie"] = new_k_kat
                            st.session_state.konten[new_k_name]["Seite"] = new_seite
                            st.session_state.konten[new_k_name]["Soll"] = [x for x in
                                                                           st.session_state.konten[new_k_name]["Soll"]
                                                                           if x[1] != "AB"]
                            st.session_state.konten[new_k_name]["Haben"] = [x for x in
                                                                            st.session_state.konten[new_k_name]["Haben"]
                                                                            if x[1] != "AB"]

                            if new_k_ab > 0:
                                st.session_state.konten[new_k_name][new_seite].insert(0, (new_k_ab, "AB", ""))

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
            with col1: b_soll = st.selectbox("Soll:", options=kto_namen)
            with col2: st.markdown("<h4 style='text-align: center; margin-top: 30px;'>an</h4>", unsafe_allow_html=True)
            with col3: b_haben = st.selectbox("Haben:", options=kto_namen)
            with col4: b_betrag = st.number_input("Betrag (€):", min_value=0.01, value=100.0, step=10.0)

            if st.form_submit_button("Buchen", type="primary", use_container_width=True):
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
    if not st.session_state.konten:
        st.info("Bitte erst Konten anlegen.")
    else:
        st.subheader("Jahresabschluss vorbereiten")
        st.markdown("Bevor das PDF erstellt wird, müssen die Erfolgskonten abgeschlossen werden.")

        konten_liste_namen = list(st.session_state.konten.keys())
        default_guv_idx = konten_liste_namen.index("GuV") if "GuV" in konten_liste_namen else 0
        default_ek_idx = konten_liste_namen.index("Eigenkapital") if "Eigenkapital" in konten_liste_namen else 0

        col_a1, col_a2 = st.columns(2)
        with col_a1:
            erfolg_zu = st.selectbox("Erfolgskonten abschließen über:", options=konten_liste_namen,
                                     index=default_guv_idx)
        with col_a2:
            guv_zu = st.selectbox("Gewinn- und Verlustkonto abschließen über:", options=konten_liste_namen,
                                  index=default_ek_idx)

        st.divider()
        st.subheader("PDF Lösung generieren")


        # --- PDF FUNKTIONEN ---
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
            pdf.cell(30, 8, f"{sum_rechts:,.2f}", border="TRB", align="R", ln=True);
            pdf.ln(10)


        def draw_single_t_konto(pdf, x, y, name, werte):
            pdf.set_xy(x, y)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(90, 8, f"S                            {name[:20]}                            H", border="B",
                     align="C")
            y += 8;
            pdf.set_xy(x, y);
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

                pdf.cell(27, 6, s_text[:15], border="L");
                pdf.cell(18, 6, s_val, border="R", align="R")
                pdf.cell(27, 6, h_text[:15]);
                pdf.cell(18, 6, h_val, border="R", align="R")
                y += 6;
                pdf.set_xy(x, y)

            s_sum = sum(i[0] for i in werte["Soll"]);
            h_sum = sum(i[0] for i in werte["Haben"])
            sb = round(abs(s_sum - h_sum), 2)

            # SB nur zeichnen, wenn das Konto NICHT exakt aufgeht
            if sb > 0:
                pdf.set_font("Helvetica", "I", 9)
                if s_sum >= h_sum:
                    pdf.cell(45, 6, "", border="LR");
                    pdf.cell(20, 6, "SB", align="L");
                    pdf.cell(25, 6, f"{sb:,.2f}", border="R", align="R")
                else:
                    pdf.cell(20, 6, "SB", border="L", align="L");
                    pdf.cell(25, 6, f"{sb:,.2f}", border="R", align="R");
                    pdf.cell(45, 6, "", border="R")
                y += 6;
                pdf.set_xy(x, y)

            max_sum = max(s_sum, h_sum)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(20, 6, "", border="TLB");
            pdf.cell(25, 6, f"{max_sum:,.2f}", border="TRB", align="R")
            pdf.cell(20, 6, "", border="TLB");
            pdf.cell(25, 6, f"{max_sum:,.2f}", border="TRB", align="R")
            return y + 10


        def draw_wide_t_konto(pdf, x, y, name, werte):
            pdf.set_xy(x, y)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(180, 8,
                     f"Soll                                                    {name[:40]}                                                    Haben",
                     border="B", align="C")
            y += 8;
            pdf.set_xy(x, y);
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

                pdf.cell(60, 6, s_text[:35], border="L");
                pdf.cell(30, 6, s_val, border="R", align="R")
                pdf.cell(60, 6, h_text[:35]);
                pdf.cell(30, 6, h_val, border="R", align="R")
                y += 6;
                pdf.set_xy(x, y)

            s_sum = sum(i[0] for i in werte["Soll"]);
            h_sum = sum(i[0] for i in werte["Haben"])
            sb = round(abs(s_sum - h_sum), 2)

            # SB nur zeichnen, wenn das Konto NICHT exakt aufgeht
            if sb > 0:
                pdf.set_font("Helvetica", "I", 9)
                if s_sum >= h_sum:
                    pdf.cell(90, 6, "", border="LR");
                    pdf.cell(60, 6, "SB", align="L");
                    pdf.cell(30, 6, f"{sb:,.2f}", border="R", align="R")
                else:
                    pdf.cell(60, 6, "SB", border="L", align="L");
                    pdf.cell(30, 6, f"{sb:,.2f}", border="R", align="R");
                    pdf.cell(90, 6, "", border="R")
                y += 6;
                pdf.set_xy(x, y)

            max_sum = max(s_sum, h_sum)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(60, 6, "", border="TLB");
            pdf.cell(30, 6, f"{max_sum:,.2f}", border="TRB", align="R")
            pdf.cell(60, 6, "", border="TLB");
            pdf.cell(30, 6, f"{max_sum:,.2f}", border="TRB", align="R")
            return y + 10


        if st.button("📄 Abschlussbuchungen & PDF generieren", type="primary"):
            temp_konten = copy.deepcopy(st.session_state.konten)
            temp_journal = copy.deepcopy(st.session_state.journal)

            # Merken, wie viele Einträge vom Schüler stammen
            original_journal_len = len(temp_journal)

            for k_name, k_data in list(temp_konten.items()):
                kat = k_data.get("Kategorie", "")
                if kat in ["Aufwand", "Ertrag"]:
                    s_sum = sum(i[0] for i in k_data["Soll"]);
                    h_sum = sum(i[0] for i in k_data["Haben"])
                    saldo = abs(s_sum - h_sum)
                    if saldo > 0:
                        nr = len(temp_journal) + 1
                        if s_sum > h_sum:
                            temp_journal.append((nr, erfolg_zu, k_name, saldo))
                            temp_konten[erfolg_zu]["Soll"].append((saldo, str(nr), k_name))
                            temp_konten[k_name]["Haben"].append((saldo, str(nr), erfolg_zu))
                        else:
                            temp_journal.append((nr, k_name, erfolg_zu, saldo))
                            temp_konten[k_name]["Soll"].append((saldo, str(nr), erfolg_zu))
                            temp_konten[erfolg_zu]["Haben"].append((saldo, str(nr), k_name))

            if erfolg_zu in temp_konten:
                guv_data = temp_konten[erfolg_zu]
                g_s_sum = sum(i[0] for i in guv_data["Soll"]);
                g_h_sum = sum(i[0] for i in guv_data["Haben"])
                g_saldo = abs(g_s_sum - g_h_sum)
                if g_saldo > 0:
                    nr = len(temp_journal) + 1
                    if g_s_sum > g_h_sum:
                        temp_journal.append((nr, guv_zu, erfolg_zu, g_saldo))
                        temp_konten[guv_zu]["Soll"].append((g_saldo, str(nr), erfolg_zu))
                        temp_konten[erfolg_zu]["Haben"].append((g_saldo, str(nr), guv_zu))
                    else:
                        temp_journal.append((nr, erfolg_zu, guv_zu, g_saldo))
                        temp_konten[erfolg_zu]["Soll"].append((g_saldo, str(nr), guv_zu))
                        temp_konten[guv_zu]["Haben"].append((g_saldo, str(nr), erfolg_zu))

            # --- PDF ERSTELLUNG START ---
            pdf = FPDF()
            pdf.add_page()

            # 1. Eröffnungsbilanz
            eb_aktiv, eb_passiv = [], []
            for name, daten in temp_konten.items():
                if daten.get("Kategorie") == "Aktiv" and daten["Soll"] and daten["Soll"][0][1] == "AB":
                    eb_aktiv.append((name, daten["Soll"][0][0]))
                if daten.get("Kategorie") == "Passiv" and daten["Haben"] and daten["Haben"][0][1] == "AB":
                    eb_passiv.append((name, daten["Haben"][0][0]))
            draw_bilanz_pdf(pdf, "Eröffnungsbilanz", eb_aktiv, eb_passiv)

            # --- 2. Journal & Abschluss (Zwei Spalten Layout) ---
            pdf.set_font("Helvetica", "B", 12)
            y_start_journal = pdf.get_y()
            col_width = 90  # Breite einer Spalte

            # --- LINKE SPALTE: Grundbuch (Manuelle Buchungen) ---
            pdf.set_xy(10, y_start_journal)
            pdf.cell(col_width, 10, "Grundbuch (Manuell)", ln=False)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_xy(10, y_start_journal + 10)

            if original_journal_len == 0:
                pdf.cell(col_width, 6, "(Keine manuellen Buchungen)", ln=True)
            else:
                for entry in temp_journal[:original_journal_len]:
                    if pdf.get_y() > 260:  # Seitenumbruch-Check
                        pdf.add_page()
                        pdf.set_xy(10, 20)

                    s_lines = [f"{s['konto']} {s['betrag']:,.2f}" for s in entry["soll"]]
                    h_lines = [f"an {h['konto']} {h['betrag']:,.2f}" for h in entry["haben"]]

                    curr_x = 10
                    pdf.set_x(curr_x)
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.cell(8, 6, f"{entry['nr']})")
                    pdf.set_font("Helvetica", "", 9)
                    pdf.cell(col_width - 8, 6, s_lines[0], ln=True)

                    for s in s_lines[1:]:
                        pdf.set_x(curr_x + 8)
                        pdf.cell(col_width - 8, 6, s, ln=True)

                    for h in h_lines:
                        pdf.set_x(curr_x + 13)
                        pdf.cell(col_width - 13, 6, h, ln=True)
                    pdf.ln(1)

            y_end_left = pdf.get_y()

            # --- RECHTE SPALTE: Abschlussbuchungen ---
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_xy(110, y_start_journal)  # Start rechts bei X=110
            pdf.cell(col_width, 10, "Abschlussbuchungen", ln=False)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_xy(110, y_start_journal + 10)

            if len(temp_journal) == original_journal_len:
                pdf.cell(col_width, 6, "(Keine Abschlussbuchungen notwendig)", ln=True)
            else:
                for entry in temp_journal[original_journal_len:]:
                    if pdf.get_y() > 260:
                        pdf.set_xy(110, 20)

                    s_lines = [f"{s['konto']} {s['betrag']:,.2f}" for s in entry["soll"]]
                    h_lines = [f"an {h['konto']} {h['betrag']:,.2f}" for h in entry["haben"]]

                    curr_x = 110
                    pdf.set_x(curr_x)
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.cell(8, 6, f"{entry['nr']})")
                    pdf.set_font("Helvetica", "", 9)
                    pdf.cell(col_width - 8, 6, s_lines[0], ln=True)

                    for s in s_lines[1:]:
                        pdf.set_x(curr_x + 8)
                        pdf.cell(col_width - 8, 6, s, ln=True)

                    for h in h_lines:
                        pdf.set_x(curr_x + 13)
                        pdf.cell(col_width - 13, 6, h, ln=True)
                    pdf.ln(1)

            # Cursor auf den niedrigsten Punkt setzen, damit der Rest (z.B. Konten) darunter weitergeht
            pdf.set_y(max(y_end_left, pdf.get_y()) + 10)

            # 3. Hauptbuch - Bestandskonten
            if pdf.get_y() > 240: pdf.add_page()
            pdf.set_font("Helvetica", "B", 12);
            pdf.cell(0, 8, "Hauptbuch - Bestandskonten", ln=True)
            pdf.set_font("Helvetica", "I", 10);
            pdf.cell(0, 6, "(Aktivkonten links, Passivkonten rechts)", ln=True);
            pdf.ln(4)

            aktiv_konten = [(k, v) for k, v in temp_konten.items() if v.get("Kategorie") == "Aktiv"]
            passiv_konten = [(k, v) for k, v in temp_konten.items() if v.get("Kategorie") == "Passiv"]

            for i in range(max(len(aktiv_konten), len(passiv_konten))):
                start_y = pdf.get_y()
                if start_y > 230: pdf.add_page(); start_y = pdf.get_y()
                y_left = start_y;
                y_right = start_y
                if i < len(aktiv_konten): y_left = draw_single_t_konto(pdf, 10, start_y, aktiv_konten[i][0],
                                                                       aktiv_konten[i][1])
                if i < len(passiv_konten): y_right = draw_single_t_konto(pdf, 105, start_y, passiv_konten[i][0],
                                                                         passiv_konten[i][1])
                pdf.set_y(max(y_left, y_right));
                pdf.set_x(10)

            # 4. Hauptbuch - Erfolgskonten
            if pdf.get_y() > 220:
                pdf.add_page()
            else:
                pdf.ln(10)

            pdf.set_font("Helvetica", "B", 12);
            pdf.cell(0, 8, "Hauptbuch - Erfolgskonten", ln=True)
            pdf.set_font("Helvetica", "I", 10);
            pdf.cell(0, 6, "(GuV oben, Aufwandskonten links, Ertragskonten rechts)", ln=True);
            pdf.ln(4)

            # GuV über die ganze Breite
            if erfolg_zu in temp_konten:
                if pdf.get_y() > 200: pdf.add_page()
                next_y = draw_wide_t_konto(pdf, 10, pdf.get_y(), erfolg_zu, temp_konten[erfolg_zu])
                pdf.set_y(next_y + 5)

            # Aufwand & Ertrag darunter
            aufwand_konten = [(k, v) for k, v in temp_konten.items() if v.get("Kategorie") == "Aufwand"]
            ertrag_konten = [(k, v) for k, v in temp_konten.items() if v.get("Kategorie") == "Ertrag"]

            for i in range(max(len(aufwand_konten), len(ertrag_konten))):
                start_y = pdf.get_y()
                if start_y > 230: pdf.add_page(); start_y = pdf.get_y()
                y_left = start_y;
                y_right = start_y
                if i < len(aufwand_konten): y_left = draw_single_t_konto(pdf, 10, start_y, aufwand_konten[i][0],
                                                                         aufwand_konten[i][1])
                if i < len(ertrag_konten): y_right = draw_single_t_konto(pdf, 105, start_y, ertrag_konten[i][0],
                                                                         ertrag_konten[i][1])
                pdf.set_y(max(y_left, y_right));
                pdf.set_x(10)

            # 5. Schlussbilanz
            if pdf.get_y() > 220:
                pdf.add_page()
            else:
                pdf.ln(10)

            sb_aktiv, sb_passiv = [], []
            for name, daten in temp_konten.items():
                if daten.get("Kategorie") in ["Aktiv", "Passiv"]:
                    s_sum = sum(i[0] for i in daten["Soll"]);
                    h_sum = sum(i[0] for i in daten["Haben"])
                    saldo = abs(s_sum - h_sum)
                    if saldo > 0:
                        if s_sum > h_sum:
                            sb_aktiv.append((name, saldo))
                        else:
                            sb_passiv.append((name, saldo))

            draw_bilanz_pdf(pdf, "Schlussbilanz", sb_aktiv, sb_passiv)

            temp_pdf_path = "temp_loesung.pdf"
            pdf.output(temp_pdf_path)

            with open(temp_pdf_path, "rb") as pdf_file:
                PDFbyte = pdf_file.read()

            st.success("PDF inkl. strukturierter Konten und getrenntem Journal wurde erfolgreich generiert!")
            st.download_button(label="📥 PDF jetzt herunterladen", data=PDFbyte,
                               file_name="Jahresabschluss_Komplett.pdf", mime='application/octet-stream')