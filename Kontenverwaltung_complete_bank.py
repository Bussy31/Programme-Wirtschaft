import streamlit as st
import pandas as pd
from fpdf import FPDF
import copy
import json
import os
import uuid

# ---  SEITEN-KONFIGURATION  ---
st.set_page_config(page_title="Buchhaltungstrainer 2026", layout="wide")

# --- COPYRIGHT FOOTER (Unten rechts) ---
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

# --- HILFSFUNKTION FÜR DEUTSCHE ZAHLENFORMATIERUNG ---
def format_german_num(value):
    """Wandelt US-Zahlenformat (1,000.00) in deutsches Format (1.000,00) um."""
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --- SESSION STATE (Das Gedächtnis der App) ---
if "konten" not in st.session_state:
    st.session_state.konten = {}
if "journal" not in st.session_state:
    st.session_state.journal = []
if "form_msg" not in st.session_state:
    st.session_state.form_msg = None

if "soll_count" not in st.session_state:
    st.session_state.soll_count = 1
if "haben_count" not in st.session_state:
    st.session_state.haben_count = 1

# ==========================================
# SEITENLEISTE: SPEICHERN & LADEN
# ==========================================
# NEU: Ein kleiner Zähler im Gedächtnis, um das Upload-Feld nach dem Laden zu leeren
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

st.sidebar.header("💾 Speichern & Laden")
st.sidebar.write("Sichere hier deinen aktuellen Stand, um später weiterzuarbeiten.")

# --- SPEICHERN (Download) ---
save_data = {
    "konten": st.session_state.konten,
    "journal": st.session_state.journal,
    "sort_orders": st.session_state.get("sort_orders", {"Aktiv": [], "Passiv": [], "Aufwand": [], "Ertrag": []})
}
# Wandeln das Paket in einen speicherbaren Text um
json_string = json.dumps(save_data, indent=4)

st.sidebar.download_button(
    label="⬇️ Aktuellen Stand herunterladen",
    file_name="buchhaltung_speicherstand.json",
    mime="application/json",
    data=json_string,
    use_container_width=True
)

st.sidebar.divider()

# --- LADEN (Upload) ---
# NEU: Der Zähler ist an den Schlüssel (Key) des Uploaders gebunden
uploaded_file = st.sidebar.file_uploader(
    "⬆️ Speicherstand laden",
    type=["json"],
    key=f"file_uploader_{st.session_state.uploader_key}"
)

if st.sidebar.button("🔄 Daten aus Datei jetzt laden", use_container_width=True):
    if uploaded_file is not None:
        try:
            # Datei lesen und zurückübersetzen
            loaded_data = json.load(uploaded_file)

            # Die aktuellen Daten im System überschreiben
            st.session_state.konten = loaded_data.get("konten", {})
            st.session_state.journal = loaded_data.get("journal", [])
            if "sort_orders" in loaded_data:
                st.session_state.sort_orders = loaded_data["sort_orders"]

            # NEU: Wir erhöhen den Zähler um 1.
            # Dadurch wirft Streamlit das alte Upload-Feld (inklusive Datei) weg und macht ein leeres hin!
            st.session_state.uploader_key += 1

            # Seite sofort neu laden, um die T-Konten zu zeigen und das Feld zu leeren
            st.rerun()

        except Exception as e:
            st.sidebar.error("❌ Fehler beim Laden der Datei. Ist es die richtige Datei?")
    else:
        st.sidebar.warning("Bitte ziehe zuerst eine Datei in das Feld oben.")


def add_soll_row():
    st.session_state.soll_count += 1


def add_haben_row():
    st.session_state.haben_count += 1


def remove_soll_row():
    if st.session_state.soll_count > 1:
        st.session_state.soll_count -= 1


def remove_haben_row():
    if st.session_state.haben_count > 1:
        st.session_state.haben_count -= 1


def reset_buchung():
    st.session_state.soll_count = 1
    st.session_state.haben_count = 1
    keys_to_delete = [
        key for key in st.session_state.keys()
        if key.startswith("s_val_") or key.startswith("h_val_") or key.startswith("s_kto_") or key.startswith("h_kto_")
    ]
    for key in keys_to_delete:
        del st.session_state[key]


# --- DATEN-MANAGER ---
def rebuild_accounts():
    """Setzt alle Konten auf den AB zurück und bucht das gesamte Journal neu durch."""
    for name, daten in st.session_state.konten.items():
        daten["Soll"] = [x for x in daten["Soll"] if x[1] == "AB"]
        daten["Haben"] = [x for x in daten["Haben"] if x[1] == "AB"]

    new_journal = []
    for idx, entry in enumerate(st.session_state.journal):
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


# --- CALLBACK FUNKTIONEN FÜR NEUE KONTEN ---
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


def add_special_konto(name, kategorie, seite):
    if name not in st.session_state.konten:
        st.session_state.konten[name] = {"Kategorie": kategorie, "Seite": seite, "Soll": [], "Haben": []}
        st.session_state.form_msg = {"type": "success", "text": f"Spezialkonto '{name}' erfolgreich angelegt!"}
    else:
        st.session_state.form_msg = {"type": "error", "text": f"Das Konto '{name}' existiert bereits!"}


# --- TABS ERSTELLEN ---
tab1, tab2, tab3, tab4 = st.tabs(
    ["1. Konten & Eröffnung", "2. Buchen (Grundbuch)", "3. T-Konten & Abschluss", "4. PDF Export"])

# ==========================================
# TAB 1: KONTEN & ERÖFFNUNG
# ==========================================
with tab1:
    st.subheader("Konto eröffnen")

    col_n, col_w = st.columns([2, 1])
    with col_n:
        st.text_input("Kontoname:", key="kto_name_input")
    with col_w:
        st.number_input("AB-Wert (€):", min_value=0.0, step=100.0, key="kto_wert_input")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("🟢 Aktivkonto", use_container_width=True, on_click=add_konto, args=("Aktiv", "Soll"))
    with col2:
        st.button("🔵 Passivkonto", use_container_width=True, on_click=add_konto, args=("Passiv", "Haben"))
    with col3:
        st.button("🔴 Aufwandskonto", use_container_width=True, on_click=add_konto, args=("Aufwand", "Soll"))
    with col4:
        st.button("🟡 Ertragskonto", use_container_width=True, on_click=add_konto, args=("Ertrag", "Haben"))

    st.write("")
    st.markdown("**Spezialkonten (mit 1 Klick anlegen):**")

    scol1, scol2, scol3 = st.columns(3)
    with scol1:
        st.button("📊 GuV-Konto eröffnen", use_container_width=True, on_click=add_special_konto,
                  args=("GuV", "GuV", "Soll"))
    with scol2:
        st.button("📉 Vorsteuer eröffnen", use_container_width=True, on_click=add_special_konto,
                  args=("Vorsteuer", "Aktiv", "Soll"))
    with scol3:
        st.button("📈 Umsatzsteuer eröffnen", use_container_width=True, on_click=add_special_konto,
                  args=("Umsatzsteuer", "Passiv", "Haben"))

    # --- NEU: Gemischtes Konto (Kontokorrent / Bank) ---
    st.write("")
    st.markdown("**Gemischtes Konto:**")
    c_b1, c_b2, c_b3, c_b4 = st.columns([2, 1, 1, 1])
    with c_b1:
        bank_name = st.text_input("Name:", value="Kundenkontokorrent", key="bank_name")
    with c_b2:
        bank_ab_soll = st.number_input("AB Soll (Debitoren):", min_value=0.0, step=100.0, key="bank_soll")
    with c_b3:
        bank_ab_haben = st.number_input("AB Haben (Kreditoren):", min_value=0.0, step=100.0, key="bank_haben")
    with c_b4:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🏦 Eröffnen", use_container_width=True):
            if bank_name and bank_name not in st.session_state.konten:
                st.session_state.konten[bank_name] = {"Kategorie": "Gemischt", "Seite": "Soll", "Soll": [],
                                                      "Haben": []}
                if bank_ab_soll > 0:
                    st.session_state.konten[bank_name]["Soll"].append((bank_ab_soll, "AB", ""))
                if bank_ab_haben > 0:
                    st.session_state.konten[bank_name]["Haben"].append((bank_ab_haben, "AB", ""))
                st.session_state.form_msg = {"type": "success", "text": f"Gemischtes Konto '{bank_name}' eröffnet!"}
                st.rerun()
            else:
                st.error("Name fehlt oder existiert schon!")


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

        for val, ref, _ in werte["Soll"]:
            if ref == "AB": sum_aktiv_ab += val
        for val, ref, _ in werte["Haben"]:
            if ref == "AB": sum_passiv_ab += val

    diff = abs(sum_aktiv_ab - sum_passiv_ab)

    st.subheader("Eröffnungsbilanz-Check")
    m1, m2, m3 = st.columns(3)
    m1.metric("Summe Aktiv (AB)", f"{format_german_num(sum_aktiv_ab)} €")
    m2.metric("Summe Passiv (AB)", f"{format_german_num(sum_passiv_ab)} €")
    m3.metric("Differenz", f"{format_german_num(diff)} €")

    if diff > 0.01:
        st.error(f"⚠️ Achtung: Die Eröffnungsbilanz ist nicht ausgeglichen! (Differenz: {format_german_num(diff)} €)")
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
                    kat_options = ["Aktiv", "Passiv", "Aufwand", "Ertrag", "GuV", "Abschluss"]
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
                            new_seite = "Soll" if new_k_kat in ["Aktiv", "Aufwand", "GuV", "Abschluss"] else "Haben"
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
    st.subheader("Neuer Buchungssatz")

    kto_namen = list(st.session_state.konten.keys())

    if not kto_namen:
        st.info("Bitte lege zuerst unter '1. Konten & Eröffnung' Konten an.")
    else:
        st.write("Wähle Konten aus. Für zusammengesetzte Buchungssätze klicke auf '➕ Zeile hinzufügen'.")

        soll_items = []
        haben_items = []
        col_soll, col_haben = st.columns(2)

        with col_soll:
            st.markdown("**Soll**")
            for i in range(st.session_state.soll_count):
                c1, c2 = st.columns([2, 1])
                with c1:
                    kto = st.selectbox(f"Soll-Konto {i + 1}", kto_namen, key=f"s_kto_{i}", label_visibility="collapsed")
                with c2:
                    betrag = st.number_input(f"Betrag {i + 1}", min_value=0.0, step=100.0, key=f"s_val_{i}",
                                             label_visibility="collapsed")
                if betrag > 0:
                    soll_items.append({"konto": kto, "betrag": betrag})

            btn_col_s1, btn_col_s2 = st.columns(2)
            with btn_col_s1:
                st.button("➕ Zeile hinzufügen", on_click=add_soll_row, use_container_width=True, key="add_soll_btn")
            with btn_col_s2:
                st.button("🗑️ Zeile entfernen", on_click=remove_soll_row, use_container_width=True, key="rem_soll_btn",
                          disabled=st.session_state.soll_count <= 1)

        with col_haben:
            st.markdown("**an Haben**")
            for i in range(st.session_state.haben_count):
                c1, c2 = st.columns([2, 1])
                with c1:
                    kto = st.selectbox(f"Haben-Konto {i + 1}", kto_namen, key=f"h_kto_{i}",
                                       label_visibility="collapsed")
                with c2:
                    betrag = st.number_input(f"Betrag {i + 1}", min_value=0.0, step=100.0, key=f"h_val_{i}",
                                             label_visibility="collapsed")
                if betrag > 0:
                    haben_items.append({"konto": kto, "betrag": betrag})

            btn_col_h1, btn_col_h2 = st.columns(2)
            with btn_col_h1:
                st.button("➕ Zeile hinzufügen", on_click=add_haben_row, use_container_width=True, key="add_haben_btn")
            with btn_col_h2:
                st.button("🗑️ Zeile entfernen", on_click=remove_haben_row, use_container_width=True, key="rem_haben_btn",
                          disabled=st.session_state.haben_count <= 1)

        st.write("")

        if st.button("💾 Buchen", type="primary", use_container_width=True):
            s_sum = sum(item["betrag"] for item in soll_items)
            h_sum = sum(item["betrag"] for item in haben_items)

            if not soll_items or not haben_items:
                st.error("Bitte mindestens ein Soll- und ein Haben-Konto mit Betrag > 0 angeben.")
            elif abs(s_sum - h_sum) > 0.01:
                st.error(
                    f"Fehler: Soll ({format_german_num(s_sum)} €) und Haben ({format_german_num(h_sum)} €) stimmen nicht überein! (Differenz: {format_german_num(abs(s_sum - h_sum))} €)")
            else:
                nr = len(st.session_state.journal) + 1
                st.session_state.journal.append({"nr": nr, "soll": soll_items, "haben": haben_items})
                rebuild_accounts()
                st.success("Erfolgreich gebucht!")
                reset_buchung()
                st.rerun()

    st.divider()
    st.subheader("Grundbuch")

    if st.session_state.journal:
        journal_display = []
        for entry in st.session_state.journal:
            soll_str = "\n".join([f"{s['konto']} ({format_german_num(s['betrag'])} €)" for s in entry["soll"]])
            haben_str = "\n".join([f"{h['konto']} ({format_german_num(h['betrag'])} €)" for h in entry["haben"]])
            journal_display.append({"Nr": entry["nr"], "Soll": soll_str, "Haben": haben_str})

        st.dataframe(pd.DataFrame(journal_display), use_container_width=True, hide_index=True)

        with st.expander("🗑️ Buchung löschen (Stornieren)"):
            b_dict = {f"Nr. {entry['nr']}: {entry['soll'][0]['konto']} an {entry['haben'][0]['konto']}...": i for
                      i, entry in enumerate(st.session_state.journal)}
            selected_b = st.selectbox("Buchung auswählen:", options=list(b_dict.keys()))

            if selected_b:
                idx = b_dict[selected_b]
                if st.button("🗑️ Gewählte Buchung endgültig löschen", use_container_width=True, type="primary",
                             key=f"del_btn_{idx}"):
                    st.session_state.journal.pop(idx)
                    rebuild_accounts()
                    st.rerun()
    else:
        st.write("Noch keine Buchungen vorhanden.")

# ==========================================
# TAB 3: T-KONTEN ANSICHT & ABSCHLUSS
# ==========================================
with tab3:
    st.subheader("Aktuelle T-Konten & Abschluss")

    if not st.session_state.konten:
        st.info("Bitte lege zuerst unter '1. Konten & Eröffnung' Konten an.")
    else:
        st.write(
            "Wähle ein Konto aus, um die Buchungen zu überprüfen und es manuell abzuschließen. Abschlussbuchungen können Sie im Grundbuch wieder löschen.")

        # --- NEU: Zählen, ob es bereits abgeschlossene Konten gibt ---
        closed_count = 0
        for k, v in st.session_state.konten.items():
            s_sum = sum(item[0] for item in v["Soll"])
            h_sum = sum(item[0] for item in v["Haben"])
            if abs(s_sum - h_sum) < 0.01:
                closed_count += 1

        # --- NEU: Checkbox direkt an den Session State koppeln ---
        if "hide_closed_accounts" not in st.session_state:
            st.session_state.hide_closed_accounts = True

        # Checkbox ist nur aktiv ("drückbar"), wenn es abgeschlossene Konten gibt
        nur_offene_konten = st.checkbox(
            "Bereits abgeschlossene Konten ausblenden",
            key="hide_closed_accounts",  # <-- HIER IST DIE MAGIE
            disabled=(closed_count == 0)
        )

        # HINWEIS: Die alte Zeile zum manuellen Speichern fällt hier komplett weg!

        if closed_count == 0:
            st.caption("💡 Diese Option wird klickbar, sobald das erste Konto abgeschlossen ist.")

        # --- Liste aufbauen ---
        kto_namen_t = []
        for k, v in st.session_state.konten.items():
            s_sum = sum(item[0] for item in v["Soll"])
            h_sum = sum(item[0] for item in v["Haben"])

            # Wenn der Haken drin ist, überspringen wir Konten mit Saldo 0
            if nur_offene_konten and abs(s_sum - h_sum) < 0.01:
                continue

            kto_namen_t.append(k)

        if not kto_namen_t and nur_offene_konten:
            st.success("🎉 Glückwunsch! Alle Konten sind ausgeglichen und abgeschlossen.")
        else:
            selected_t_kto = st.selectbox("Wähle ein Konto aus:", options=kto_namen_t)

            if selected_t_kto:
                k_daten = st.session_state.konten[selected_t_kto]

            st.write("")
            st.markdown(
                f"<h4 style='text-align: center; border-bottom: 2px solid #333; padding-bottom: 5px;'>{selected_t_kto}</h4>",
                unsafe_allow_html=True)

            col_s, col_h = st.columns(2)

            soll_entries = k_daten["Soll"]
            haben_entries = k_daten["Haben"]

            s_sum = sum(item[0] for item in soll_entries)
            h_sum = sum(item[0] for item in haben_entries)

            max_len = max(len(soll_entries), len(haben_entries))

            with col_s:
                st.markdown("**Soll**")
                html_s = ""
                for i in range(max_len):
                    if i < len(soll_entries):
                        val, ref, gkto = soll_entries[i]
                        # HIER EBK STATT AB
                        if ref == "AB":
                            text = "EBK"
                        else:
                            text = f"{ref}) {gkto}" if gkto else str(ref)
                        html_s += f"<div style='display: flex; justify-content: space-between;'><span>{text}</span><span><b>{format_german_num(val)} €</b></span></div>"
                    else:
                        html_s += "<div style='display: flex; justify-content: space-between;'><span>&nbsp;</span><span>&nbsp;</span></div>"
                st.markdown(html_s, unsafe_allow_html=True)
                st.markdown("---")
                st.markdown(
                    f"<div style='display: flex; justify-content: space-between;'><span><b>Summe:</b></span><span><b>{format_german_num(s_sum)} €</b></span></div>",
                    unsafe_allow_html=True)

            with col_h:
                st.markdown("**Haben**")
                html_h = ""
                for i in range(max_len):
                    if i < len(haben_entries):
                        val, ref, gkto = haben_entries[i]
                        # HIER EBK STATT AB
                        if ref == "AB":
                            text = "EBK"
                        else:
                            text = f"{ref}) {gkto}" if gkto else str(ref)
                        html_h += f"<div style='display: flex; justify-content: space-between;'><span>{text}</span><span><b>{format_german_num(val)} €</b></span></div>"
                    else:
                        html_h += "<div style='display: flex; justify-content: space-between;'><span>&nbsp;</span><span>&nbsp;</span></div>"
                st.markdown(html_h, unsafe_allow_html=True)
                st.markdown("---")
                st.markdown(
                    f"<div style='display: flex; justify-content: space-between;'><span><b>Summe:</b></span><span><b>{format_german_num(h_sum)} €</b></span></div>",
                    unsafe_allow_html=True)

            st.write("")
            saldo = abs(s_sum - h_sum)

            st.divider()
            st.markdown("### 🔒 Konto manuell abschließen")
            kat = k_daten.get("Kategorie", "")

            # --- NEU: SONDERFALL GEMISCHTES KONTO (KKK) ---
            if kat == "Gemischt":
                st.info("🏦 **Gemischtes Konto:** Trage die Endbestände aus der Auswertung der Nebenbücher ein.")
                c_g1, c_g2 = st.columns(2)
                with c_g1:
                    eb_soll = st.number_input("Endbestand Kreditoren (Buchung ins Soll):", min_value=0.0, step=100.0, key="eb_soll")
                with c_g2:
                    eb_haben = st.number_input("Endbestand Debitoren (Buchung ins Haben):", min_value=0.0, step=100.0, key="eb_haben")

                if st.button("🏦 Gemischtes Konto abschließen", type="primary"):
                    # Die magische Prüfung: Sind beide Seiten inkl. Endbestände gleich groß?
                    if abs((s_sum + eb_soll) - (h_sum + eb_haben)) > 0.01:
                        st.error(f"Fehler! Soll ({format_german_num(s_sum + eb_soll)} €) und Haben ({format_german_num(h_sum + eb_haben)} €) sind nicht ausgeglichen.")
                    else:
                        if "SBK" not in st.session_state.konten:
                            st.session_state.konten["SBK"] = {"Kategorie": "Abschluss", "Seite": "Soll", "Soll": [], "Haben": []}

                        nr = len(st.session_state.journal) + 1
                        # 1. Verbindlichkeiten buchen (KKK an SBK)
                        if eb_soll > 0:
                            st.session_state.journal.append({"nr": nr, "soll": [{"konto": selected_t_kto, "betrag": eb_soll}], "haben": [{"konto": "SBK", "betrag": eb_soll}]})
                            nr += 1
                        # 2. Forderungen buchen (SBK an KKK)
                        if eb_haben > 0:
                            st.session_state.journal.append({"nr": nr, "soll": [{"konto": "SBK", "betrag": eb_haben}], "haben": [{"konto": selected_t_kto, "betrag": eb_haben}]})

                        rebuild_accounts()
                        st.success(f"Das Bankkonto '{selected_t_kto}' wurde perfekt abgeschlossen!")
                        st.rerun()

            # --- NORMALER ABSCHLUSS (Für alle anderen Konten) ---
            else:
                if saldo == 0:
                    st.success("✅ Dieses Konto ist ausgeglichen und somit bereits abgeschlossen!")
                else:
                    st.info(f"Dieses Konto hat einen Saldo von **{format_german_num(saldo)} €**. Bestimme die Abschlussseite und das Gegenkonto.")

                    c_abs1, c_abs2, c_abs3 = st.columns(3)
                    with c_abs1:
                        abs_seite = st.selectbox("Abschlussbuchung auf Seite:", ["Soll", "Haben"])
                    with c_abs2:
                        abs_betrag = st.number_input("Abschlussbetrag (€):", min_value=0.0, step=100.0, format="%.2f")
                    with c_abs3:
                        default_g = "GuV" if kat in ["Aufwand", "Ertrag"] else "SBK"
                        mögliche_gegenkonten = list(st.session_state.konten.keys())
                        for missing in ["SBK", "GuV", "Eigenkapital"]:
                            if missing not in mögliche_gegenkonten:
                                mögliche_gegenkonten.append(missing)
                        mögliche_gegenkonten = [k for k in mögliche_gegenkonten if k != selected_t_kto]
                        try:
                            def_idx = mögliche_gegenkonten.index(default_g)
                        except ValueError:
                            def_idx = 0
                        abs_gegenkonto = st.selectbox("Gegenkonto (z.B. SBK, GuV):", mögliche_gegenkonten, index=def_idx)

                    if st.button("Abschlussbuchung eintragen", type="primary"):
                        expected_seite = "Haben" if s_sum > h_sum else "Soll"

                        if abs_betrag != saldo:
                            st.error(f"Falscher Betrag! Der Saldo beträgt exakt {format_german_num(saldo)} €.")
                        elif abs_seite != expected_seite:
                            st.error(f"Falsche Seite! Der Saldo muss im {expected_seite} gebucht werden.")
                        else:
                            if abs_gegenkonto not in st.session_state.konten:
                                neue_kat = "Abschluss" if abs_gegenkonto == "SBK" else ("GuV" if abs_gegenkonto == "GuV" else "Passiv")
                                st.session_state.konten[abs_gegenkonto] = {"Kategorie": neue_kat, "Seite": "Soll" if neue_kat == "GuV" else "Haben", "Soll": [], "Haben": []}

                            nr = len(st.session_state.journal) + 1
                            if abs_seite == "Haben":
                                st.session_state.journal.append({"nr": nr, "soll": [{"konto": abs_gegenkonto, "betrag": abs_betrag}], "haben": [{"konto": selected_t_kto, "betrag": abs_betrag}]})
                            else:
                                st.session_state.journal.append({"nr": nr, "soll": [{"konto": selected_t_kto, "betrag": abs_betrag}], "haben": [{"konto": abs_gegenkonto, "betrag": abs_betrag}]})

                            rebuild_accounts()
                            st.success(f"Erfolgreich gebucht! Das Konto '{selected_t_kto}' ist nun abgeschlossen.")
                            st.rerun()

# ==========================================
# TAB 4: PDF EXPORT
# ==========================================
with tab4:
    if not st.session_state.konten:
        st.info("Bitte erst Konten anlegen.")
    else:
        special_konten = ["GuV", "SBK"]

        # 1. Konten nach Kategorien sortieren (Logik im Hintergrund)
        kategorien = {"Aktiv": [], "Passiv": [], "Aufwand": [], "Ertrag": []}

        for k, v in st.session_state.konten.items():
            if k in special_konten:
                continue

            # --- NEU: Vor- und Umsatzsteuer Logik (Verrechnung vs. SBK) ---
            if k in ["Vorsteuer", "Umsatzsteuer"]:
                s_sum = sum(item[0] for item in v["Soll"])
                h_sum = sum(item[0] for item in v["Haben"])

                # Prüfen, ob "SBK" bei diesem Konto irgendwo als Gegenkonto auftaucht
                has_sbk = any(gkto == "SBK" for _, _, gkto in v["Soll"]) or \
                          any(gkto == "SBK" for _, _, gkto in v["Haben"])

                # Verstecken NUR dann, wenn:
                # 1. Beträge drauf sind (nicht komplett unbenutzt)
                # 2. Der Saldo 0 ist (wurde abgeschlossen)
                # 3. Es NICHT ins SBK ging (wurde also gegen das andere Steuerkonto verrechnet)
                if (s_sum > 0 or h_sum > 0) and abs(s_sum - h_sum) < 0.01 and not has_sbk:
                    continue
                    # -------------------------------------------------------------------------

            kat = v.get("Kategorie", "")

            if kat in ["Aktiv", "Konto", "Abschluss", "Gemischt"]:
                kategorien["Aktiv"].append(k)

            if kat in ["Passiv", "Gemischt"]:
                kategorien["Passiv"].append(k)

            if kat == "Aufwand":
                kategorien["Aufwand"].append(k)

            if kat == "Ertrag":
                kategorien["Ertrag"].append(k)

        # 2. Session State (Gedächtnis) für die 4 Listen anlegen/aktualisieren
        if "sort_orders" not in st.session_state:
            st.session_state.sort_orders = {"Aktiv": [], "Passiv": [], "Aufwand": [], "Ertrag": []}

        for gruppe, konten in kategorien.items():
            # Alte (gelöschte) Konten entfernen
            st.session_state.sort_orders[gruppe] = [k for k in st.session_state.sort_orders[gruppe] if k in konten]
            # Neue Konten unten anhängen
            for k in konten:
                if k not in st.session_state.sort_orders[gruppe]:
                    st.session_state.sort_orders[gruppe].append(k)

        # --- AB HIER STARTET DIE EINKLAPPBARE BOX ---
        with st.expander("⚙️ Reihenfolge der Konten anpassen (richtige Reihenfolge in der Bilanz)", expanded=False):
            st.write(
                "Verschiebe die Konten innerhalb ihrer Kategorie nach oben oder unten. Die Steuerkonten, GuV und SBK werden im PDF automatisch an die richtigen Stellen gesetzt.")


            # 3. Hilfsfunktion, um eine Liste mit Pfeilen zu zeichnen
            def draw_sortable_list(gruppe):
                liste = st.session_state.sort_orders[gruppe]
                if not liste:
                    st.write(f"<span style='color:gray; font-size:14px;'>Keine {gruppe}konten vorhanden</span>",
                             unsafe_allow_html=True)
                for i, kto in enumerate(liste):
                    c_name, c_up, c_down = st.columns([5, 1, 1])
                    with c_name:
                        st.markdown(f"<div style='padding-top: 5px; font-size: 15px;'><b>{i + 1}.</b> {kto}</div>",
                                    unsafe_allow_html=True)
                    with c_up:
                        if st.button("⬆️", key=f"up_{gruppe}_{kto}", disabled=(i == 0), use_container_width=True):
                            # DIREKT im Session State tauschen, damit Streamlit es nicht vergisst!
                            st.session_state.sort_orders[gruppe][i], st.session_state.sort_orders[gruppe][i - 1] = \
                                st.session_state.sort_orders[gruppe][i - 1], st.session_state.sort_orders[gruppe][i]
                            st.rerun()
                    with c_down:
                        if st.button("⬇️", key=f"down_{gruppe}_{kto}", disabled=(i == len(liste) - 1),
                                     use_container_width=True):
                            # DIREKT im Session State tauschen, damit Streamlit es nicht vergisst!
                            st.session_state.sort_orders[gruppe][i], st.session_state.sort_orders[gruppe][i + 1] = \
                                st.session_state.sort_orders[gruppe][i + 1], st.session_state.sort_orders[gruppe][i]
                            st.rerun()

            # 4. Das Layout auf dem Bildschirm aufbauen
            st.markdown("#### 🏛️ Bestandskonten")
            col_akt, col_pas = st.columns(2)

            with col_akt:
                # Packt die Liste in eine schöne Box mit Rahmen
                with st.container(border=True):
                    st.markdown("**Aktivkonten (Links)**")
                    draw_sortable_list("Aktiv")

            with col_pas:
                with st.container(border=True):
                    st.markdown("**Passivkonten (Rechts)**")
                    draw_sortable_list("Passiv")

            st.write("")
            st.markdown("#### 📈 Erfolgskonten")
            col_auf, col_ert = st.columns(2)

            with col_auf:
                with st.container(border=True):
                    st.markdown("**Aufwandskonten (Links)**")
                    draw_sortable_list("Aufwand")

            with col_ert:
                with st.container(border=True):
                    st.markdown("**Ertragskonten (Rechts)**")
                    draw_sortable_list("Ertrag")

        # 5. Für die PDF-Generierung alle sortierten Konten in einer langen Liste zusammenfassen
        sorted_user_konten = (
                st.session_state.sort_orders["Aktiv"] +
                st.session_state.sort_orders["Passiv"] +
                st.session_state.sort_orders["Aufwand"] +
                st.session_state.sort_orders["Ertrag"]
        )

        st.subheader("Jahresabschluss als PDF exportieren")
        st.markdown("Das System druckt nun den genauen Stand deiner Buchhaltung aus.")

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
                    pdf.cell(30, 6, format_german_num(links[i][1]), border="R", align="R")
                else:
                    pdf.cell(90, 6, "", border="LR")

                if i < len(rechts):
                    pdf.cell(60, 6, rechts[i][0][:25])
                    pdf.cell(30, 6, format_german_num(rechts[i][1]), border="R", align="R", ln=True)
                else:
                    pdf.cell(90, 6, "", border="R", ln=True)

            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(60, 8, "Summe", border="TLB")
            pdf.cell(30, 8, format_german_num(sum_links), border="TRB", align="R")
            pdf.cell(60, 8, "Summe", border="TLB")
            pdf.cell(30, 8, format_german_num(sum_rechts), border="TRB", align="R", ln=True)
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
                    if ref == "AB":
                        s_text = "EBK"
                    else:
                        s_text = f"{ref}) {gkto}" if gkto else str(ref)
                    s_val = format_german_num(val)
                else:
                    s_text, s_val = "", ""

                if i < len(werte["Haben"]):
                    val, ref, gkto = werte["Haben"][i]
                    if ref == "AB":
                        h_text = "EBK"
                    else:
                        h_text = f"{ref}) {gkto}" if gkto else str(ref)
                    h_val = format_german_num(val)
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

            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(27, 6, "", border="TLB")
            pdf.cell(18, 6, format_german_num(s_sum), border="TRB", align="R")
            pdf.cell(27, 6, "", border="TLB")
            pdf.cell(18, 6, format_german_num(h_sum), border="TRB", align="R")
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
                    if ref == "AB":
                        s_text = "EBK"
                    else:
                        s_text = f"{ref}) {gkto}" if gkto else str(ref)
                    s_val = format_german_num(val)
                else:
                    s_text, s_val = "", ""

                if i < len(werte["Haben"]):
                    val, ref, gkto = werte["Haben"][i]
                    if ref == "AB":
                        h_text = "EBK"
                    else:
                        h_text = f"{ref}) {gkto}" if gkto else str(ref)
                    h_val = format_german_num(val)
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

            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(60, 6, "", border="TLB")
            pdf.cell(30, 6, format_german_num(s_sum), border="TRB", align="R")
            pdf.cell(60, 6, "", border="TLB")
            pdf.cell(30, 6, format_german_num(h_sum), border="TRB", align="R")
            return y + 10


        if st.button("📄 PDF generieren", type="primary"):
            temp_konten = {}

            # 1. Spezialkonten unberührt lassen (werden im PDF-Skript ohnehin fest positioniert)
            for k in ["GuV", "SBK"]:
                if k in st.session_state.konten:
                    temp_konten[k] = copy.deepcopy(st.session_state.konten[k])

            # 2. Dann die vom Nutzer sortierten Konten hinzufügen
            for k in sorted_user_konten:
                temp_konten[k] = copy.deepcopy(st.session_state.konten[k])

            for k in st.session_state.konten:
                if k not in temp_konten:
                    temp_konten[k] = copy.deepcopy(st.session_state.konten[k])

            temp_journal = copy.deepcopy(st.session_state.journal)

            # --- PDF ERSTELLUNG START ---
            pdf = FPDF()
            pdf.add_page()

            # 1. Eröffnungsbilanz
            eb_aktiv, eb_passiv = [], []
            for name, daten in temp_konten.items():
                # Durchsucht alle Soll-Einträge nach einem "AB" (erfasst auch gemischte Konten)
                for val, ref, _ in daten["Soll"]:
                    if ref == "AB":
                        eb_aktiv.append((name, val))

                # Durchsucht alle Haben-Einträge nach einem "AB" (erfasst auch gemischte Konten)
                for val, ref, _ in daten["Haben"]:
                    if ref == "AB":
                        eb_passiv.append((name, val))
            eb_aktiv.sort(key=lambda x: st.session_state.sort_orders["Aktiv"].index(x[0]) if x[0] in
                                                                                             st.session_state.sort_orders[
                                                                                                 "Aktiv"] else 999)
            eb_passiv.sort(key=lambda x: st.session_state.sort_orders["Passiv"].index(x[0]) if x[0] in
                                                                                               st.session_state.sort_orders[
                                                                                                   "Passiv"] else 999)
            gemischte_namen = [k for k, v in st.session_state.konten.items() if
                               v.get("Kategorie") == "Gemischt"]

            eb_aktiv_bilanz = [("Debitoren" if n in gemischte_namen else n, v) for n, v in eb_aktiv]
            eb_passiv_bilanz = [("Kreditoren" if n in gemischte_namen else n, v) for n, v in eb_passiv]

            draw_bilanz_pdf(pdf, "Eröffnungsbilanz", eb_aktiv_bilanz, eb_passiv_bilanz)

            # 1.5 Eröffnungsbilanzkonto (EBK) generieren (Seitenverkehrt zur EB)
            if eb_aktiv or eb_passiv:
                if pdf.get_y() > 220:
                    pdf.add_page()
                else:
                    pdf.ln(10)

                ebk_data = {"Soll": [], "Haben": []}
                # Passiva ins Soll des EBK (Wir übergeben den Namen als 'ref' und lassen 'gkto' leer, um die Klammer zu vermeiden)
                for name, val in eb_passiv:
                    ebk_data["Soll"].append((val, name, ""))
                # Aktiva ins Haben des EBK
                for name, val in eb_aktiv:
                    ebk_data["Haben"].append((val, name, ""))

                next_y = draw_wide_t_konto(pdf, 10, pdf.get_y(), "Eröffnungsbilanzkonto (EBK)", ebk_data)
                pdf.set_y(next_y + 5)

            # 2. Grundbuch
            if pdf.get_y() > 240:
                pdf.add_page()
            else:
                pdf.ln(10)

            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "Grundbuch", ln=True)
            pdf.set_font("Helvetica", "", 9)

            if len(temp_journal) == 0:
                pdf.cell(0, 6, "(Keine Buchungen vorhanden)", ln=True)
            else:
                half_idx = (len(temp_journal) + 1) // 2

                for i in range(half_idx):
                    if pdf.get_y() > 260:
                        pdf.add_page()

                    l_entry = temp_journal[i]
                    r_entry = temp_journal[half_idx + i] if (half_idx + i) < len(temp_journal) else None

                    l_s_lines = [f"{s['konto']} {format_german_num(s['betrag'])}" for s in l_entry["soll"]]
                    l_h_lines = [f"an {h['konto']} {format_german_num(h['betrag'])}" for h in l_entry["haben"]]

                    r_s_lines, r_h_lines = [], []
                    if r_entry:
                        r_s_lines = [f"{s['konto']} {format_german_num(s['betrag'])}" for s in r_entry["soll"]]
                        r_h_lines = [f"an {h['konto']} {format_german_num(h['betrag'])}" for h in r_entry["haben"]]

                    start_y = pdf.get_y()

                    # LINKE SPALTE (x = 10)
                    pdf.set_xy(10, start_y)
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.cell(8, 6, f"{l_entry['nr']})")
                    pdf.set_font("Helvetica", "", 9)
                    y_left = start_y
                    for s in l_s_lines:
                        pdf.set_xy(18, y_left)
                        pdf.cell(85, 6, s)
                        y_left += 6
                    for h in l_h_lines:
                        pdf.set_xy(25, y_left)
                        pdf.cell(78, 6, h)
                        y_left += 6

                    # RECHTE SPALTE (x = 105)
                    y_right = start_y
                    if r_entry:
                        pdf.set_xy(105, start_y)
                        pdf.set_font("Helvetica", "B", 9)
                        pdf.cell(8, 6, f"{r_entry['nr']})")
                        pdf.set_font("Helvetica", "", 9)
                        for s in r_s_lines:
                            pdf.set_xy(113, y_right)
                            pdf.cell(85, 6, s)
                            y_right += 6
                        for h in r_h_lines:
                            pdf.set_xy(120, y_right)
                            pdf.cell(78, 6, h)
                            y_right += 6

                    pdf.set_y(max(y_left, y_right) + 2)

            # 3. Hauptbuch - Bestandskonten
            if pdf.get_y() > 240:
                pdf.add_page()
            else:
                pdf.ln(10)

            # Schöne Überschrift für die Bestandskonten hinzufügen
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Hauptbuch - Bestandskonten", ln=True)

            # --- NEU: Gemischte Konten (KKK) suchen und als großes Konto ganz oben zeichnen ---
            gemischte_konten = [(k, v) for k, v in list(temp_konten.items()) if
                                v.get("Kategorie") == "Gemischt"]
            for gk_name, gk_data in gemischte_konten:
                if pdf.get_y() > 200:
                    pdf.add_page()
                # Zeichnet das Konto über die volle Breite
                next_y = draw_wide_t_konto(pdf, 10, pdf.get_y(), f"{gk_name} (Gemischtes Konto)", gk_data)
                pdf.set_y(next_y + 5)
                # Konto aus der Liste werfen, damit es nicht unten nochmal als kleines Konto gezeichnet wird
                temp_konten.pop(gk_name, None)

            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 6, "(Aktivkonten links & Passivkonten rechts)", ln=True)
            pdf.ln(4)

            sbk_data = temp_konten.pop("SBK", None)

            aktiv_konten = [(k, v) for k, v in temp_konten.items() if
                            v.get("Kategorie") in ["Aktiv", "Konto", "Abschluss"]]
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
            if pdf.get_y() > 190:
                pdf.add_page()
            else:
                pdf.ln(10)

            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Hauptbuch - Erfolgskonten", ln=True)
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 6, "(Aufwandskonten links & Ertragskonten rechts)", ln=True)
            pdf.ln(4)

            guv_data = temp_konten.pop("GuV", None)
            if guv_data:
                if pdf.get_y() > 200: pdf.add_page()
                next_y = draw_wide_t_konto(pdf, 10, pdf.get_y(), "Gewinn- und Verlustkonto (GuV)", guv_data)
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

            # 5. Schlussbilanzkonto (SBK)
            if sbk_data:
                # --- NEU: Einträge im T-Konto des SBK getrennt nach Aktiv und Passiv sortieren --
                sbk_data["Soll"].sort(
                    key=lambda x: st.session_state.sort_orders["Aktiv"].index(x[2]) if x[2] in
                                                                                       st.session_state.sort_orders[
                                                                                           "Aktiv"] else 999)
                sbk_data["Haben"].sort(
                    key=lambda x: st.session_state.sort_orders["Passiv"].index(x[2]) if x[2] in
                                                                                        st.session_state.sort_orders[
                                                                                            "Passiv"] else 999)

                benoetigte_hoehe_sbk = 35 + (max(len(sbk_data["Soll"]), len(sbk_data["Haben"])) * 6)
                if pdf.get_y() + benoetigte_hoehe_sbk > 265:  # <-- Wir brechen viel früher um!
                    pdf.add_page()
                else:
                    pdf.ln(10)
                next_y = draw_wide_t_konto(pdf, 10, pdf.get_y(), "Schlussbilanzkonto (SBK)", sbk_data)
                pdf.set_y(next_y + 5)
            else:
                pdf.set_font("Helvetica", "I", 10)
                pdf.cell(0, 6,
                         "(Kein Schlussbilanzkonto vorhanden. Es wurden noch keine Konten manuell über das SBK abgeschlossen.)",
                         ln=True)

            # 6. Schlussbilanz aus dem SBK generieren
            if sbk_data:
                # 1. Daten holen
                sb_aktiv = [(gkto, val) for val, ref, gkto in sbk_data["Soll"]]
                sb_passiv = [(gkto, val) for val, ref, gkto in sbk_data["Haben"]]

                # 2. Sortieren
                sb_aktiv.sort(key=lambda x: st.session_state.sort_orders["Aktiv"].index(x[0]) if x[0] in
                                                                                                 st.session_state.sort_orders[
                                                                                                     "Aktiv"] else 999)
                sb_passiv.sort(key=lambda x: st.session_state.sort_orders["Passiv"].index(x[0]) if x[0] in
                                                                                                   st.session_state.sort_orders[
                                                                                                       "Passiv"] else 999)

                # 3. Umbenennen
                gemischte_namen = [k for k, v in st.session_state.konten.items() if
                                   v.get("Kategorie") == "Gemischt"]
                sb_aktiv_bilanz = [("Debitoren" if n in gemischte_namen else n, v) for n, v in sb_aktiv]
                sb_passiv_bilanz = [("Kreditoren" if n in gemischte_namen else n, v) for n, v in sb_passiv]

                # --- NEU: Sehr strikter Seitenumbruch für die Bilanz ---
                benoetigte_hoehe_sb = 35 + (max(len(sb_aktiv_bilanz), len(sb_passiv_bilanz)) * 6)

                if pdf.get_y() + benoetigte_hoehe_sb > 265:  # <-- Wir brechen viel früher um!
                    pdf.add_page()
                else:
                    pdf.ln(10)

                # 4. Bilanz zeichnen
                draw_bilanz_pdf(pdf, "Schlussbilanz", sb_aktiv_bilanz, sb_passiv_bilanz)


            # Generiert einen einzigartigen Namen, z.B. "temp_loesung_8f3a1b...pdf"
            temp_pdf_path = f"temp_loesung_{uuid.uuid4().hex}.pdf"
            pdf.output(temp_pdf_path)

            with open(temp_pdf_path, "rb") as pdf_file:
                PDFbyte = pdf_file.read()

            # Datei direkt wieder vom Server löschen, der Inhalt ist ja jetzt in "PDFbyte" gespeichert
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

            st.success("PDF erfolgreich generiert! Dein aktueller Arbeitsstand wurde gedruckt.")
            st.download_button(label="📥 PDF jetzt herunterladen", data=PDFbyte,
                               file_name="Jahresabschluss_export.pdf", mime='application/octet-stream')