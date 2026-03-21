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
# TAB 1: KONTENPLAN & ERÖFFNUNGSBILANZ
# ==========================================
with tab1:
    st.subheader("1. Konten anlegen")
    st.markdown(
        "Leg hier die benötigten Konten an. **Hinweis:** Die Konten *Vorsteuer* und *Umsatzsteuer* werden beim ersten Eintrag automatisch vom System mit angelegt.")

    c1, c2, c3 = st.columns([2, 1, 1])
    # HIER WURDE DER BEISPIELTEXT ENTFERNT
    konto_name = c1.text_input("Kontoname")
    kategorie = c2.selectbox("Kategorie", ["Aktiv", "Passiv", "Aufwand", "Ertrag"])
    start_saldo = c3.number_input("Anfangsbestand (nur bei Bestandskonten)", min_value=0.0, step=100.0, format="%.2f")

    if st.button("Konto hinzufügen"):
        if konto_name:
            if konto_name in st.session_state.konten:
                st.warning("Dieses Konto existiert bereits!")
            else:
                # Prüfen, ob dies das allererste Konto ist
                is_first = len(st.session_state.konten) == 0

                # Das vom Nutzer gewünschte Konto anlegen
                st.session_state.konten[konto_name] = {
                    "Kategorie": kategorie,
                    "Soll": [],
                    "Haben": []
                }

                # Anfangsbestand buchen, falls vorhanden
                if start_saldo > 0:
                    if kategorie in ["Aktiv", "Aufwand"]:
                        st.session_state.konten[konto_name]["Soll"].append((start_saldo, "AB", ""))
                    else:
                        st.session_state.konten[konto_name]["Haben"].append((start_saldo, "AB", ""))

                # Wenn es das erste Konto war, Steuern automatisch ergänzen
                if is_first:
                    if "Vorsteuer" not in st.session_state.konten:
                        st.session_state.konten["Vorsteuer"] = {"Kategorie": "Aktiv", "Soll": [], "Haben": []}
                    if "Umsatzsteuer" not in st.session_state.konten:
                        st.session_state.konten["Umsatzsteuer"] = {"Kategorie": "Passiv", "Soll": [], "Haben": []}
                    st.success(
                        f"Konto '{konto_name}' erfolgreich angelegt! (Vorsteuer & Umsatzsteuer wurden automatisch hinzugefügt)")
                else:
                    st.success(f"Konto '{konto_name}' erfolgreich angelegt!")
                st.rerun()
        else:
            st.warning("Bitte einen Kontonamen eingeben.")

    st.divider()
    st.subheader("Bisherige Konten")
    if not st.session_state.konten:
        st.write("Noch keine Konten angelegt.")
    else:
        # Tabellarische Übersicht der angelegten Konten
        konten_liste_anzeige = []
        for name, daten in st.session_state.konten.items():
            soll_sum = sum([val[0] for val in daten["Soll"] if val[1] == "AB"])
            haben_sum = sum([val[0] for val in daten["Haben"] if val[1] == "AB"])
            ab = soll_sum if daten["Kategorie"] in ["Aktiv", "Aufwand"] else haben_sum
            konten_liste_anzeige.append({"Konto": name, "Kategorie": daten["Kategorie"], "Anfangsbestand": ab})

        st.dataframe(konten_liste_anzeige, use_container_width=True)

        if st.button("Alle Konten löschen (Reset)", type="primary"):
            st.session_state.konten = {}
            st.session_state.journal = []
            st.rerun()

# ==========================================
# TAB 2: BUCHUNGSSÄTZE (Dynamisch)
# ==========================================
with tab2:
    if not st.session_state.konten:
        st.info("Bitte erst Konten im Tab 'Kontenplan' anlegen.")
    else:
        st.subheader("Neuer Buchungssatz")

        # Session-State für dynamische Zeilen
        if "soll_lines" not in st.session_state: st.session_state.soll_lines = 1
        if "haben_lines" not in st.session_state: st.session_state.haben_lines = 1

        konten_liste = list(st.session_state.konten.keys())

        col_soll, col_haben = st.columns(2)

        # SOLL-SEITE
        soll_entries = []
        with col_soll:
            st.markdown("**SOLL**")
            for i in range(st.session_state.soll_lines):
                c1, c2 = st.columns([2, 1])
                k = c1.selectbox(f"Soll-Konto {i + 1}", options=konten_liste, key=f"soll_k_{i}")
                b = c2.number_input(f"Betrag {i + 1}", min_value=0.0, step=10.0, format="%.2f", key=f"soll_b_{i}")
                soll_entries.append((k, b))
            if st.button("➕ Soll-Zeile hinzufügen"):
                st.session_state.soll_lines += 1
                st.rerun()

        # HABEN-SEITE
        haben_entries = []
        with col_haben:
            st.markdown("**HABEN**")
            for i in range(st.session_state.haben_lines):
                c1, c2 = st.columns([2, 1])
                k = c1.selectbox(f"Haben-Konto {i + 1}", options=konten_liste, key=f"haben_k_{i}")
                b = c2.number_input(f"Betrag {i + 1}", min_value=0.0, step=10.0, format="%.2f", key=f"haben_b_{i}")
                haben_entries.append((k, b))
            if st.button("➕ Haben-Zeile hinzufügen"):
                st.session_state.haben_lines += 1
                st.rerun()

        # BERECHNUNG & VALIDIERUNG
        sum_soll = sum(b for k, b in soll_entries)
        sum_haben = sum(b for k, b in haben_entries)

        st.divider()
        st.write(f"**Summe Soll:** {sum_soll:,.2f} € | **Summe Haben:** {sum_haben:,.2f} €")

        soll_clean = [(k, b) for k, b in soll_entries if b > 0]
        haben_clean = [(k, b) for k, b in haben_entries if b > 0]

        if not soll_clean or not haben_clean:
            st.warning("Bitte gib auf beiden Seiten mindestens einen Betrag > 0 ein.")
        elif round(sum_soll, 2) != round(sum_haben, 2):
            st.error("Fehler: Die Summe im Soll muss exakt der Summe im Haben entsprechen!")
        else:
            if st.button("✅ Buchungssatz eintragen", type="primary"):
                nr = len(st.session_state.journal) + 1
                st.session_state.journal.append((nr, soll_clean, haben_clean))

                soll_gegen_str = haben_clean[0][0] if len(haben_clean) == 1 else "Diverse"
                haben_gegen_str = soll_clean[0][0] if len(soll_clean) == 1 else "Diverse"

                for k, b in soll_clean:
                    st.session_state.konten[k]["Soll"].append((b, str(nr), soll_gegen_str))
                for k, b in haben_clean:
                    st.session_state.konten[k]["Haben"].append((b, str(nr), haben_gegen_str))

                st.success(f"Buchungssatz {nr} erfolgreich eingetragen!")

                # --- RESET LOGIK ---
                st.session_state.soll_lines = 1
                st.session_state.haben_lines = 1
                # Löscht alle Eingabewerte aus dem Zwischenspeicher
                for key in list(st.session_state.keys()):
                    if key.startswith("soll_k_") or key.startswith("soll_b_") or key.startswith(
                            "haben_k_") or key.startswith("haben_b_"):
                        del st.session_state[key]
                st.rerun()

        st.divider()
        st.subheader("Bisheriges Journal")
        if not st.session_state.journal:
            st.write("Noch keine Buchungen vorhanden.")
        else:
            for nr, soll_list, haben_list in st.session_state.journal:
                # HTML-Formatierung für bündige Darstellung
                s_html = "<br>".join([f"{k} {b:,.2f} €" for k, b in soll_list])
                h_html = "<br>".join([f"{k} {b:,.2f} €" for k, b in haben_list])

                st.markdown(f"""
                <table style="width:100%; border:none; margin-bottom: 10px;">
                    <tr style="background-color:transparent;">
                        <td style="width:5%; vertical-align:top; border:none;"><b>{nr})</b></td>
                        <td style="width:40%; vertical-align:top; border:none;">{s_html}</td>
                        <td style="width:5%; vertical-align:top; text-align:center; border:none;"><b>an</b></td>
                        <td style="width:50%; vertical-align:top; border:none;">{h_html}</td>
                    </tr>
                </table>
                """, unsafe_allow_html=True)

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

            # ERFOLGSKONTEN ABSCHLIESSEN (Neues Format)
            for k_name, k_data in list(temp_konten.items()):
                kat = k_data.get("Kategorie", "")
                if kat in ["Aufwand", "Ertrag"]:
                    s_sum = sum(i[0] for i in k_data["Soll"]);
                    h_sum = sum(i[0] for i in k_data["Haben"])
                    saldo = abs(s_sum - h_sum)
                    if saldo > 0:
                        nr = len(temp_journal) + 1
                        if s_sum > h_sum:
                            temp_journal.append((nr, [(erfolg_zu, saldo)], [(k_name, saldo)]))
                            temp_konten[erfolg_zu]["Soll"].append((saldo, str(nr), k_name))
                            temp_konten[k_name]["Haben"].append((saldo, str(nr), erfolg_zu))
                        else:
                            temp_journal.append((nr, [(k_name, saldo)], [(erfolg_zu, saldo)]))
                            temp_konten[k_name]["Soll"].append((saldo, str(nr), erfolg_zu))
                            temp_konten[erfolg_zu]["Haben"].append((saldo, str(nr), k_name))

            # GUV ABSCHLIESSEN (Neues Format)
            if erfolg_zu in temp_konten:
                guv_data = temp_konten[erfolg_zu]
                g_s_sum = sum(i[0] for i in guv_data["Soll"]);
                g_h_sum = sum(i[0] for i in guv_data["Haben"])
                g_saldo = abs(g_s_sum - g_h_sum)
                if g_saldo > 0:
                    nr = len(temp_journal) + 1
                    if g_s_sum > g_h_sum:
                        temp_journal.append((nr, [(guv_zu, g_saldo)], [(erfolg_zu, g_saldo)]))
                        temp_konten[guv_zu]["Soll"].append((g_saldo, str(nr), erfolg_zu))
                        temp_konten[erfolg_zu]["Haben"].append((g_saldo, str(nr), guv_zu))
                    else:
                        temp_journal.append((nr, [(erfolg_zu, g_saldo)], [(guv_zu, g_saldo)]))
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

            # 2. Journal PDF Darstellung anpassen (zusammengesetzte Buchungen)
            pdf.set_font("Helvetica", "B", 12);
            pdf.cell(0, 10, "Grundbuch (selbst gebuchte Geschäftsfälle)", ln=True);
            pdf.set_font("Helvetica", "", 10)
            if original_journal_len == 0:
                pdf.cell(0, 6, "(Keine manuellen Buchungen)", ln=True)
            for nr, soll_list, haben_list in temp_journal[:original_journal_len]:
                s_str = " + ".join([f"{k} {b:,.2f}" for k, b in soll_list])
                h_str = " + ".join([f"{k} {b:,.2f}" for k, b in haben_list])
                pdf.multi_cell(0, 6, f"{nr}) {s_str} an {h_str}")

            pdf.ln(5)

            pdf.set_font("Helvetica", "B", 12);
            pdf.cell(0, 10, "Abschlussbuchungen (automatisch erstellt)", ln=True);
            pdf.set_font("Helvetica", "", 10)
            if len(temp_journal) == original_journal_len:
                pdf.cell(0, 6, "(Keine Abschlussbuchungen notwendig)", ln=True)
            for nr, soll_list, haben_list in temp_journal[original_journal_len:]:
                s_str = " + ".join([f"{k} {b:,.2f}" for k, b in soll_list])
                h_str = " + ".join([f"{k} {b:,.2f}" for k, b in haben_list])
                pdf.multi_cell(0, 6, f"{nr}) {s_str} an {h_str}")

            pdf.ln(10)

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