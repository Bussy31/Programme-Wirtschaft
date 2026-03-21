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

# Für dynamische Buchungssätze
if "soll_count" not in st.session_state:
    st.session_state.soll_count = 1
if "haben_count" not in st.session_state:
    st.session_state.haben_count = 1


def add_soll_row():
    st.session_state.soll_count += 1


def add_haben_row():
    st.session_state.haben_count += 1


def reset_buchung():
    st.session_state.soll_count = 1
    st.session_state.haben_count = 1
    for key in list(st.session_state.keys()):
        if key.startswith("s_kto_") or key.startswith("s_val_") or key.startswith("h_kto_") or key.startswith("h_val_"):
            del st.session_state[key]


# --- DATEN-MANAGER ---
def rebuild_accounts():
    """Setzt alle Konten auf den AB zurück und bucht das gesamte Journal neu durch."""
    for name, daten in st.session_state.konten.items():
        daten["Soll"] = [x for x in daten["Soll"] if x[1] == "AB"]
        daten["Haben"] = [x for x in daten["Haben"] if x[1] == "AB"]

    new_journal = []
    for idx, entry in enumerate(st.session_state.journal):
        # Fallback für ganz alte Versionen
        if isinstance(entry, tuple):
            nr, s, h, b = entry
            entry = {"nr": idx + 1, "soll": [{"konto": s, "betrag": b}], "haben": [{"konto": h, "betrag": b}]}

        nr = idx + 1
        entry["nr"] = nr
        new_journal.append(entry)

        soll_list = entry["soll"]
        haben_list = entry["haben"]

        gk_soll = haben_list[0]["konto"] if len(haben_list) == 1 else "Diverse"
        gk_haben = soll_list[0]["konto"] if len(soll_list) == 1 else "Diverse"

        for s in soll_list:
            if s["konto"] in st.session_state.konten:
                st.session_state.konten[s["konto"]]["Soll"].append((s["betrag"], str(nr), gk_soll))
        for h in haben_list:
            if h["konto"] in st.session_state.konten:
                st.session_state.konten[h["konto"]]["Haben"].append((h["betrag"], str(nr), gk_haben))

    st.session_state.journal = new_journal


# --- CALLBACK FUNKTION FÜR NEUE KONTEN ---
def add_konto(kategorie, seite):
    name = st.session_state.kto_name_input.strip()
    eb_wert = st.session_state.kto_wert_input

    if kategorie in ["Aufwand", "Ertrag", "GuV"]:
        eb_wert = 0.0

    if name and name not in st.session_state.konten:
        st.session_state.konten[name] = {"Kategorie": kategorie, "Seite": seite, "Soll": [], "Haben": []}
        if eb_wert > 0:
            st.session_state.konten[name][seite].append((eb_wert, "AB", ""))

        st.session_state.form_msg = {"type": "success", "text": f"{kategorie} '{name}' erfolgreich angelegt!"}
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

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.button("🟢 Aktivkonto", use_container_width=True, on_click=add_konto, args=("Aktiv", "Soll"))
    with col2:
        st.button("🔵 Passivkonto", use_container_width=True, on_click=add_konto, args=("Passiv", "Haben"))
    with col3:
        st.button("🔴 Aufwandskonto", use_container_width=True, on_click=add_konto, args=("Aufwand", "Soll"))
    with col4:
        st.button("🟡 Ertragskonto", use_container_width=True, on_click=add_konto, args=("Ertrag", "Haben"))
    with col5:
        st.button("⚪ Konto (Neutral)", use_container_width=True, on_click=add_konto, args=("Konto", "Soll"))

    if st.session_state.form_msg:
        if st.session_state.form_msg["type"] == "success":
            st.success(st.session_state.form_msg["text"])
        else:
            st.error(st.session_state.form_msg["text"])
        st.session_state.form_msg = None

    st.divider()

    sum_aktiv_ab = 0
    sum_passiv_ab = 0
    konten_liste = []

    for name, werte in st.session_state.konten.items():
        s = sum(item[0] for item in werte["Soll"])
        h = sum(item[0] for item in werte["Haben"])

        kat = werte.get("Kategorie", "Aktiv" if werte["Seite"] == "Soll" else "Passiv")
        konten_liste.append({"Konto": name, "Kategorie": kat, "Soll": s, "Haben": h, "Saldo": abs(s - h)})

        if kat in ["Aktiv", "Konto"] and werte["Soll"] and werte["Soll"][0][1] == "AB":
            sum_aktiv_ab += werte["Soll"][0][0]
        if kat in ["Passiv", "Konto"] and werte["Haben"] and werte["Haben"][0][1] == "AB":
            sum_passiv_ab += werte["Haben"][0][0]

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
                    kat_options = ["Aktiv", "Passiv", "Aufwand", "Ertrag", "GuV", "Konto"]
                    current_kat = k_daten.get("Kategorie", "Aktiv")
                    new_k_kat = st.selectbox("Kategorie", options=kat_options,
                                             index=kat_options.index(current_kat) if current_kat in kat_options else 0)

                cb1, cb2 = st.columns(2)
                with cb1:
                    if st.button("💾 Änderungen speichern", use_container_width=True, type="primary"):
                        if not new_k_name.strip():
                            st.error("Der Name darf nicht leer sein.")
                        elif new_k_name != selected_kto and new_k_name in st.session_state.konten:
                            st.error("Konto existiert bereits!")
                        else:
                            new_seite = "Soll" if new_k_kat in ["Aktiv", "Aufwand", "Konto"] else "Haben"
                            if new_k_kat in ["Aufwand", "Ertrag", "GuV"]:
                                new_k_ab = 0.0

                            if new_k_name != selected_kto:
                                st.session_state.konten[new_k_name] = st.session_state.konten.pop(selected_kto)
                                for entry in st.session_state.journal:
                                    for s in entry["soll"]:
                                        if s["konto"] == selected_kto: s["konto"] = new_k_name
                                    for h in entry["haben"]:
                                        if h["konto"] == selected_kto: h["konto"] = new_k_name

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
                        in_use = any(any(s["konto"] == selected_kto for s in entry["soll"]) or
                                     any(h["konto"] == selected_kto for h in entry["haben"])
                                     for entry in st.session_state.journal)
                        if in_use:
                            st.error("Konto wird im Journal verwendet! Bitte zuerst die Buchungen löschen.")
                        else:
                            del st.session_state.konten[selected_kto]
                            st.rerun()

# ==========================================
# TAB 2: JOURNAL (BUCHEN)
# ==========================================
with tab2:
    st.subheader("Neuer Buchungssatz (Einfach oder Zusammengesetzt)")

    kto_namen = list(st.session_state.konten.keys())

    if not kto_namen:
        st.info("Bitte lege zuerst unter '1. Konten & Eröffnung' Konten an.")
    else:
        st.write("Wähle Konten aus. Für zusammengesetzte Buchungssätze klicke auf '➕ Zeile hinzufügen'.")

        # --- EINGABEBEREICH ---
        soll_items = []
        haben_items = []

        col_soll, col_haben = st.columns(2)

        # SOLLSEITE
        with col_soll:
            st.markdown("**Soll**")
            for i in range(st.session_state.soll_count):
                c1, c2 = st.columns([2, 1])
                with c1:
                    kto = st.selectbox(f"Soll-Konto {i + 1}", kto_namen, key=f"s_kto_{i}", label_visibility="collapsed")
                with c2:
                    betrag = st.number_input(f"Betrag {i + 1}", min_value=0.0, step=10.0, key=f"s_val_{i}",
                                             label_visibility="collapsed")

                if betrag > 0:
                    soll_items.append({"konto": kto, "betrag": betrag})

            st.button("➕ Soll-Zeile hinzufügen", on_click=add_soll_row, use_container_width=True)

        # HABENSEITE
        with col_haben:
            st.markdown("**an Haben**")
            for i in range(st.session_state.haben_count):
                c1, c2 = st.columns([2, 1])
                with c1:
                    kto = st.selectbox(f"Haben-Konto {i + 1}", kto_namen, key=f"h_kto_{i}",
                                       label_visibility="collapsed")
                with c2:
                    betrag = st.number_input(f"Betrag {i + 1}", min_value=0.0, step=10.0, key=f"h_val_{i}",
                                             label_visibility="collapsed")

                if betrag > 0:
                    haben_items.append({"konto": kto, "betrag": betrag})

            st.button("➕ Haben-Zeile hinzufügen", on_click=add_haben_row, use_container_width=True)

        st.write("")  # Abstand

        # BUCHEN BUTTON
        if st.button("💾 Buchen", type="primary", use_container_width=True):
            s_sum = sum(item["betrag"] for item in soll_items)
            h_sum = sum(item["betrag"] for item in haben_items)

            if not soll_items or not haben_items:
                st.error("Bitte mindestens ein Soll- und ein Haben-Konto mit Betrag > 0 angeben.")
            elif abs(s_sum - h_sum) > 0.01:
                st.error(
                    f"Fehler: Soll ({s_sum:,.2f} €) und Haben ({h_sum:,.2f} €) stimmen nicht überein! (Differenz: {abs(s_sum - h_sum):,.2f} €)")
            else:
                nr = len(st.session_state.journal) + 1
                st.session_state.journal.append({"nr": nr, "soll": soll_items, "haben": haben_items})
                rebuild_accounts()
                st.success("Erfolgreich gebucht!")
                reset_buchung()
                st.rerun()

    st.divider()
    st.subheader("Journal")

    if st.session_state.journal:
        journal_display = []
        for entry in st.session_state.journal:
            soll_str = "\n".join([f"{s['konto']} ({s['betrag']:,.2f} €)" for s in entry["soll"]])
            haben_str = "\n".join([f"{h['konto']} ({h['betrag']:,.2f} €)" for h in entry["haben"]])
            journal_display.append({"Nr": entry["nr"], "Soll": soll_str, "Haben": haben_str})

        st.dataframe(pd.DataFrame(journal_display), use_container_width=True, hide_index=True)

        with st.expander("🗑️ Buchung löschen"):
            # Buchungen für das Dropdown-Menü aufbereiten
            b_dict = {f"Nr. {entry['nr']}: {entry['soll'][0]['konto']} an {entry['haben'][0]['konto']}...": i for
                      i, entry in enumerate(st.session_state.journal)}
            selected_b = st.selectbox("Buchung auswählen:", options=list(b_dict.keys()))

            if selected_b:
                idx = b_dict[selected_b]

                # Habe dem Löschen-Button vorsichtshalber noch einen eindeutigen 'key' gegeben, damit er 100% sicher funktioniert
                if st.button("🗑️ Gewählte Buchung endgültig löschen", use_container_width=True, type="primary",
                             key=f"del_btn_{idx}"):
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
            if konten_liste_namen:
                erfolg_zu = st.selectbox("Erfolgskonten abschließen über:", options=konten_liste_namen,
                                         index=default_guv_idx)
            else:
                erfolg_zu = None
        with col_a2:
            if konten_liste_namen:
                guv_zu = st.selectbox("Gewinn- und Verlustkonto abschließen über:", options=konten_liste_namen,
                                      index=default_ek_idx)
            else:
                guv_zu = None

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
            pdf.cell(30, 8, f"{sum_rechts:,.2f}", border="TRB", align="R", ln=True)
            pdf.ln(10)


        def draw_single_t_konto(pdf, x, y, name, werte):
            pdf.set_xy(x, y)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(90, 8, f"S                            {name[:20]}                            H", border="B",
                     align="C")
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
            sb = round(abs(s_sum - h_sum), 2)

            if sb > 0:
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


        def draw_wide_t_konto(pdf, x, y, name, werte):
            pdf.set_xy(x, y)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(180, 8,
                     f"Soll                                                    {name[:40]}                                                    Haben",
                     border="B", align="C")
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

                pdf.cell(60, 6, s_text[:35], border="L")
                pdf.cell(30, 6, s_val, border="R", align="R")
                pdf.cell(60, 6, h_text[:35])
                pdf.cell(30, 6, h_val, border="R", align="R")
                y += 6
                pdf.set_xy(x, y)

            s_sum = sum(i[0] for i in werte["Soll"])
            h_sum = sum(i[0] for i in werte["Haben"])
            sb = round(abs(s_sum - h_sum), 2)

            if sb > 0:
                pdf.set_font("Helvetica", "I", 9)
                if s_sum >= h_sum:
                    pdf.cell(90, 6, "", border="LR")
                    pdf.cell(60, 6, "SB", align="L")
                    pdf.cell(30, 6, f"{sb:,.2f}", border="R", align="R")
                else:
                    pdf.cell(60, 6, "SB", border="L", align="L")
                    pdf.cell(30, 6, f"{sb:,.2f}", border="R", align="R")
                    pdf.cell(90, 6, "", border="R")
                y += 6
                pdf.set_xy(x, y)

            max_sum = max(s_sum, h_sum)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(60, 6, "", border="TLB")
            pdf.cell(30, 6, f"{max_sum:,.2f}", border="TRB", align="R")
            pdf.cell(60, 6, "", border="TLB")
            pdf.cell(30, 6, f"{max_sum:,.2f}", border="TRB", align="R")
            return y + 10


        if st.button("📄 Abschlussbuchungen & PDF generieren", type="primary"):
            temp_konten = copy.deepcopy(st.session_state.konten)
            temp_journal = copy.deepcopy(st.session_state.journal)

            original_journal_len = len(temp_journal)

            if erfolg_zu:
                for k_name, k_data in list(temp_konten.items()):
                    kat = k_data.get("Kategorie", "")
                    if kat in ["Aufwand", "Ertrag"]:
                        s_sum = sum(i[0] for i in k_data["Soll"])
                        h_sum = sum(i[0] for i in k_data["Haben"])
                        saldo = abs(s_sum - h_sum)
                        if saldo > 0:
                            nr = len(temp_journal) + 1
                            if s_sum > h_sum:
                                temp_journal.append({"nr": nr, "soll": [{"konto": erfolg_zu, "betrag": saldo}],
                                                     "haben": [{"konto": k_name, "betrag": saldo}]})
                                temp_konten[erfolg_zu]["Soll"].append((saldo, str(nr), k_name))
                                temp_konten[k_name]["Haben"].append((saldo, str(nr), erfolg_zu))
                            else:
                                temp_journal.append({"nr": nr, "soll": [{"konto": k_name, "betrag": saldo}],
                                                     "haben": [{"konto": erfolg_zu, "betrag": saldo}]})
                                temp_konten[k_name]["Soll"].append((saldo, str(nr), erfolg_zu))
                                temp_konten[erfolg_zu]["Haben"].append((saldo, str(nr), k_name))

                if erfolg_zu in temp_konten and guv_zu:
                    guv_data = temp_konten[erfolg_zu]
                    g_s_sum = sum(i[0] for i in guv_data["Soll"])
                    g_h_sum = sum(i[0] for i in guv_data["Haben"])
                    g_saldo = abs(g_s_sum - g_h_sum)
                    if g_saldo > 0:
                        nr = len(temp_journal) + 1
                        if g_s_sum > g_h_sum:
                            temp_journal.append({"nr": nr, "soll": [{"konto": guv_zu, "betrag": g_saldo}],
                                                 "haben": [{"konto": erfolg_zu, "betrag": g_saldo}]})
                            temp_konten[guv_zu]["Soll"].append((g_saldo, str(nr), erfolg_zu))
                            temp_konten[erfolg_zu]["Haben"].append((g_saldo, str(nr), guv_zu))
                        else:
                            temp_journal.append({"nr": nr, "soll": [{"konto": erfolg_zu, "betrag": g_saldo}],
                                                 "haben": [{"konto": guv_zu, "betrag": g_saldo}]})
                            temp_konten[erfolg_zu]["Soll"].append((g_saldo, str(nr), guv_zu))
                            temp_konten[guv_zu]["Haben"].append((g_saldo, str(nr), erfolg_zu))

            # --- PDF ERSTELLUNG START ---
            pdf = FPDF()
            pdf.add_page()

            # 1. Eröffnungsbilanz
            eb_aktiv, eb_passiv = [], []
            for name, daten in temp_konten.items():
                if daten.get("Kategorie") in ["Aktiv", "Konto"] and daten["Soll"] and daten["Soll"][0][1] == "AB":
                    eb_aktiv.append((name, daten["Soll"][0][0]))
                if daten.get("Kategorie") in ["Passiv", "Konto"] and daten["Haben"] and daten["Haben"][0][1] == "AB":
                    eb_passiv.append((name, daten["Haben"][0][0]))
            draw_bilanz_pdf(pdf, "Eröffnungsbilanz", eb_aktiv, eb_passiv)

            # 2. Journal
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "Grundbuch (selbst gebuchte Geschäftsfälle)", ln=True)
            pdf.set_font("Helvetica", "", 10)
            if original_journal_len == 0:
                pdf.cell(0, 6, "(Keine manuellen Buchungen)", ln=True)
            for entry in temp_journal[:original_journal_len]:
                s_lines = [f"{s['konto']} {s['betrag']:,.2f}" for s in entry["soll"]]
                h_lines = [f"an {h['konto']} {h['betrag']:,.2f}" for h in entry["haben"]]

                pdf.cell(0, 6, f"{entry['nr']}) " + s_lines[0], ln=True)
                for s in s_lines[1:]:
                    pdf.cell(8, 6, "")
                    pdf.cell(0, 6, s, ln=True)
                for h in h_lines:
                    pdf.cell(15, 6, "")
                    pdf.cell(0, 6, h, ln=True)
                pdf.ln(2)

            pdf.ln(5)

            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "Abschlussbuchungen (automatisch erstellt)", ln=True)
            pdf.set_font("Helvetica", "", 10)
            if len(temp_journal) == original_journal_len:
                pdf.cell(0, 6, "(Keine Abschlussbuchungen notwendig)", ln=True)
            for entry in temp_journal[original_journal_len:]:
                s_lines = [f"{s['konto']} {s['betrag']:,.2f}" for s in entry["soll"]]
                h_lines = [f"an {h['konto']} {h['betrag']:,.2f}" for h in entry["haben"]]

                pdf.cell(0, 6, f"{entry['nr']}) " + s_lines[0], ln=True)
                for s in s_lines[1:]:
                    pdf.cell(8, 6, "")
                    pdf.cell(0, 6, s, ln=True)
                for h in h_lines:
                    pdf.cell(15, 6, "")
                    pdf.cell(0, 6, h, ln=True)
                pdf.ln(2)

            pdf.ln(10)

            # 3. Hauptbuch - Bestandskonten
            if pdf.get_y() > 240: pdf.add_page()
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Hauptbuch - Bestandskonten", ln=True)
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 6, "(Steuerkonten zu Beginn, danach Aktiv- links & Passivkonten rechts)", ln=True)
            pdf.ln(4)

            vst_data = temp_konten.pop("Vorsteuer", None)
            ust_data = temp_konten.pop("Umsatzsteuer", None)

            if vst_data or ust_data:
                start_y = pdf.get_y()
                if start_y > 230: pdf.add_page(); start_y = pdf.get_y()
                y_left = start_y
                y_right = start_y
                if vst_data: y_left = draw_single_t_konto(pdf, 10, start_y, "Vorsteuer", vst_data)
                if ust_data: y_right = draw_single_t_konto(pdf, 105, start_y, "Umsatzsteuer", ust_data)
                pdf.set_y(max(y_left, y_right) + 5)
                pdf.set_x(10)

            aktiv_konten = [(k, v) for k, v in temp_konten.items() if v.get("Kategorie") in ["Aktiv", "Konto"]]
            passiv_konten = [(k, v) for k, v in temp_konten.items() if v.get("Kategorie") == "Passiv"]

            for i in range(max(len(aktiv_konten), len(passiv_konten))):
                start_y = pdf.get_y()
                if start_y > 230: pdf.add_page(); start_y = pdf.get_y()
                y_left = start_y
                y_right = start_y
                if i < len(aktiv_konten): y_left = draw_single_t_konto(pdf, 10, start_y, aktiv_konten[i][0],
                                                                       aktiv_konten[i][1])
                if i < len(passiv_konten): y_right = draw_single_t_konto(pdf, 105, start_y, passiv_konten[i][0],
                                                                         passiv_konten[i][1])
                pdf.set_y(max(y_left, y_right))
                pdf.set_x(10)

            # 4. Hauptbuch - Erfolgskonten
            if pdf.get_y() > 220:
                pdf.add_page()
            else:
                pdf.ln(10)

            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Hauptbuch - Erfolgskonten", ln=True)
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 6, "(GuV oben, Aufwandskonten links, Ertragskonten rechts)", ln=True)
            pdf.ln(4)

            if erfolg_zu and erfolg_zu in temp_konten:
                if pdf.get_y() > 200: pdf.add_page()
                next_y = draw_wide_t_konto(pdf, 10, pdf.get_y(), erfolg_zu, temp_konten[erfolg_zu])
                pdf.set_y(next_y + 5)

            aufwand_konten = [(k, v) for k, v in temp_konten.items() if v.get("Kategorie") == "Aufwand"]
            ertrag_konten = [(k, v) for k, v in temp_konten.items() if v.get("Kategorie") == "Ertrag"]

            for i in range(max(len(aufwand_konten), len(ertrag_konten))):
                start_y = pdf.get_y()
                if start_y > 230: pdf.add_page(); start_y = pdf.get_y()
                y_left = start_y
                y_right = start_y
                if i < len(aufwand_konten): y_left = draw_single_t_konto(pdf, 10, start_y, aufwand_konten[i][0],
                                                                         aufwand_konten[i][1])
                if i < len(ertrag_konten): y_right = draw_single_t_konto(pdf, 105, start_y, ertrag_konten[i][0],
                                                                         ertrag_konten[i][1])
                pdf.set_y(max(y_left, y_right))
                pdf.set_x(10)

            # 5. Schlussbilanz
            if pdf.get_y() > 220:
                pdf.add_page()
            else:
                pdf.ln(10)

            sb_aktiv, sb_passiv = [], []

            if vst_data: temp_konten["Vorsteuer"] = vst_data
            if ust_data: temp_konten["Umsatzsteuer"] = ust_data

            for name, daten in temp_konten.items():
                if daten.get("Kategorie") in ["Aktiv", "Passiv", "Konto"]:
                    s_sum = sum(i[0] for i in daten["Soll"])
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