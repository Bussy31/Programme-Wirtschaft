import streamlit as st
import random
import pandas as pd
import io
import matplotlib.pyplot as plt
from fpdf import FPDF

st.set_page_config(page_title="Musterland Simulation", layout="wide", initial_sidebar_state="expanded")

# --- 1. DATENBANK DER SZENARIEN (Prozentuale Logik) ----
alle_szenarien = [
    {
        "id": "1", "titel": "🚨 Globale Rezession",
        "text": "Die Weltwirtschaft schwächelt. Die Leute kaufen weniger ein.",
        "option_a": {"text": "Staatliche Bauprojekte starten", "effekte": [
            {"typ": "wachstum", "basis": "industrie", "prozent": 0.15, "ver": {"staat": 1.0},
             "vert": {"loehne": 0.8, "gewinne": 0.2}}]},
        "option_b": {"text": "Steuern für Unternehmen senken", "effekte": [
            {"typ": "wachstum", "basis": "dienstleistung", "prozent": 0.10, "ver": {"investitionen": 1.0},
             "vert": {"loehne": 0.2, "gewinne": 0.8}}]}
    },
    {
        "id": "2", "titel": "🔬 KI-Durchbruch", "text": "Eine neue Software beschleunigt Büroarbeiten enorm.",
        "option_a": {"text": "Technologie ins Ausland verkaufen", "effekte": [
            {"typ": "wachstum", "basis": "dienstleistung", "prozent": 0.20, "ver": {"export": 1.0},
             "vert": {"loehne": 0.3, "gewinne": 0.7}}]},
        "option_b": {"text": "Im Inland nutzen & Preise senken", "effekte": [
            {"typ": "wachstum", "basis": "dienstleistung", "prozent": 0.15, "ver": {"konsum": 1.0},
             "vert": {"loehne": 0.6, "gewinne": 0.4}}]}
    },
    {
        "id": "3", "titel": "🌪️ Jahrhundert-Dürre", "text": "Es regnet wochenlang nicht. Die Ernten vertrocknen.",
        "option_a": {"text": "Bauern mit Steuergeldern retten", "effekte": [
            {"typ": "wachstum", "basis": "landwirtschaft", "prozent": -0.30, "ver": {"konsum": 0.5, "staat": 0.5},
             "vert": {"loehne": 0.4, "gewinne": 0.6}}]},
        "option_b": {"text": "Freier Markt (Keine Hilfe)", "effekte": [
            {"typ": "wachstum", "basis": "landwirtschaft", "prozent": -0.40, "ver": {"konsum": 1.0},
             "vert": {"loehne": 0.5, "gewinne": 0.5}}]}
    },
    {
        "id": "4", "titel": "🪧 Generalstreik",
        "text": "Die Industriearbeiter legen die Fabriken lahm und fordern mehr Geld.",
        "option_a": {"text": "Lohnerhöhungen erzwingen", "effekte": [
            {"typ": "verteilung_shift", "basis": "loehne", "prozent": 0.15}]},
        "option_b": {"text": "Streik polizeilich auflösen", "effekte": [
            {"typ": "wachstum", "basis": "industrie", "prozent": -0.10, "ver": {"export": 1.0},
             "vert": {"loehne": 0.5, "gewinne": 0.5}}]}
    },
    {
        "id": "5", "titel": "🏖️ Tourismus-Boom", "text": "Ein Hollywood-Film wurde in deinem Land gedreht!",
        "option_a": {"text": "Luxus-Resorts bauen (Fokus Ausland)", "effekte": [
            {"typ": "wachstum", "basis": "dienstleistung", "prozent": 0.25, "ver": {"export": 1.0},
             "vert": {"loehne": 0.4, "gewinne": 0.6}}]},
        "option_b": {"text": "Naturparks fördern (Fokus Inland)", "effekte": [
            {"typ": "wachstum", "basis": "dienstleistung", "prozent": 0.15, "ver": {"konsum": 1.0},
             "vert": {"loehne": 0.7, "gewinne": 0.3}}]}
    },
    {
        "id": "6", "titel": "🚜 Traktoren-Mangel", "text": "Die Landwirtschaft ist veraltet und unproduktiv.",
        "option_a": {"text": "Staat kauft moderne Maschinen", "effekte": [
            {"typ": "wachstum", "basis": "industrie", "prozent": 0.10, "ver": {"staat": 1.0},
             "vert": {"loehne": 0.5, "gewinne": 0.5}},
            {"typ": "wachstum", "basis": "landwirtschaft", "prozent": 0.15, "ver": {"konsum": 1.0},
             "vert": {"loehne": 0.2, "gewinne": 0.8}}]},
        "option_b": {"text": "Kredite für Bauern erleichtern", "effekte": [
            {"typ": "wachstum", "basis": "landwirtschaft", "prozent": 0.10, "ver": {"investitionen": 1.0},
             "vert": {"loehne": 0.5, "gewinne": 0.5}}]}
    },
    {
        "id": "7", "titel": "🚀 Start-Up Welle", "text": "Viele junge Menschen gründen eigene IT-Firmen.",
        "option_a": {"text": "Gründer finanziell fördern", "effekte": [
            {"typ": "wachstum", "basis": "dienstleistung", "prozent": 0.20, "ver": {"staat": 0.5, "investitionen": 0.5},
             "vert": {"loehne": 0.8, "gewinne": 0.2}}]},
        "option_b": {"text": "Aufkäufe durch Großkonzerne zulassen", "effekte": [
            {"typ": "wachstum", "basis": "dienstleistung", "prozent": 0.30, "ver": {"export": 1.0},
             "vert": {"loehne": 0.1, "gewinne": 0.9}}]}
    },
    {
        "id": "8", "titel": "🛳️ Häfen verstopft", "text": "Globale Lieferketten sind gerissen, Exporte stauen sich.",
        "option_a": {"text": "Inlandskonsum anregen", "effekte": [
            {"typ": "wachstum", "basis": "industrie", "prozent": -0.15, "ver": {"export": 1.0},
             "vert": {"loehne": 0.2, "gewinne": 0.8}},
            {"typ": "wachstum", "basis": "dienstleistung", "prozent": 0.10, "ver": {"konsum": 1.0},
             "vert": {"loehne": 0.6, "gewinne": 0.4}}]},
        "option_b": {"text": "Warten und hoffen", "effekte": [
            {"typ": "wachstum", "basis": "industrie", "prozent": -0.20, "ver": {"export": 1.0},
             "vert": {"loehne": 0.5, "gewinne": 0.5}}]}
    },
    {
        "id": "9", "titel": "🍎 Bio-Trend",
        "text": "Die Menschen wollen gesünder essen und zahlen mehr für gute Lebensmittel.",
        "option_a": {"text": "Bio-Siegel staatlich pushen", "effekte": [
            {"typ": "wachstum", "basis": "landwirtschaft", "prozent": 0.25, "ver": {"konsum": 1.0},
             "vert": {"loehne": 0.4, "gewinne": 0.6}}]},
        "option_b": {"text": "Massenproduktion für Export beibehalten", "effekte": [
            {"typ": "wachstum", "basis": "landwirtschaft", "prozent": 0.10, "ver": {"export": 1.0},
             "vert": {"loehne": 0.1, "gewinne": 0.9}}]}
    },
    {
        "id": "10", "titel": "🎓 Bildungsoffensive",
        "text": "Die Regierung überlegt, massiv in Schulen und Unis zu investieren.",
        "option_a": {"text": "Kostenlose Unis für alle", "effekte": [
            {"typ": "wachstum", "basis": "dienstleistung", "prozent": 0.15, "ver": {"staat": 1.0},
             "vert": {"loehne": 0.9, "gewinne": 0.1}}]},
        "option_b": {"text": "Forschungsgelder für Industrie", "effekte": [
            {"typ": "wachstum", "basis": "industrie", "prozent": 0.15, "ver": {"investitionen": 1.0},
             "vert": {"loehne": 0.3, "gewinne": 0.7}}]}
    }
]


# --- 2. HILFSFUNKTIONEN FÜR LOGIK UND MATHEMATIK ---
def ziehe_3_szenarien():
    gezogen = []
    for _ in range(3):
        if len(st.session_state.uebrige_szenarien) > 0:
            gezogen.append(st.session_state.uebrige_szenarien.pop())
    return gezogen


def berechne_bip():
    return sum(st.session_state.ent.values())


def sichere_vorjahr():
    st.session_state.alt_bip = berechne_bip()


def naechstes_jahr():
    sichere_vorjahr()
    st.session_state.bip_historie.append({"Jahr": st.session_state.jahr, "BIP": berechne_bip()})
    st.session_state.jahr += 1

    st.session_state.aktuelle_szenarien = ziehe_3_szenarien()
    st.session_state.entscheidungen_getroffen = [False] * len(st.session_state.aktuelle_szenarien)
    st.session_state.ereignis_logbuch = []
    st.rerun()


def erstelle_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)

    def clean_text(text):
        text = text.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
        text = text.replace('Ä', 'Ae').replace('Ö', 'Oe').replace('Ü', 'Ue').replace('ß', 'ss')
        return text.encode('ascii', 'ignore').decode('ascii')

    land = clean_text(st.session_state.land_name)
    waehrung = clean_text(st.session_state.waehrung)

    pdf.cell(0, 10, f"Wirtschaftsbericht: {land}", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Stand: Jahr {st.session_state.jahr}", ln=True, align='C')
    pdf.ln(5)

    # 1. Startbedingungen
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. Startbedingungen (Jahr 1):", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Anfangs-BIP: {st.session_state.start_bip} {waehrung}", ln=True)
    pdf.ln(5)

    # 2. Aktuelle Zahlen
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. Aktuelle Wirtschaftslage:", ln=True)
    pdf.set_font("Arial", '', 12)
    bip = berechne_bip()
    pdf.cell(0, 8, f"BIP Gesamt: {bip} {waehrung}", ln=True)
    pdf.cell(0, 8,
             f"Entstehung: Agrar ({st.session_state.ent['landwirtschaft']}), Industrie ({st.session_state.ent['industrie']}), Dienstleistung ({st.session_state.ent['dienstleistung']})",
             ln=True)
    pdf.cell(0, 8,
             f"Verwendung: Konsum ({st.session_state.ver['konsum']}), Invest ({st.session_state.ver['investitionen']}), Staat ({st.session_state.ver['staat']}), Export ({st.session_state.ver['export']})",
             ln=True)
    pdf.cell(0, 8,
             f"Verteilung: Loehne ({st.session_state.vert['loehne']}), Gewinne ({st.session_state.vert['gewinne']})",
             ln=True)
    pdf.ln(5)

    # (Das Diagramm wurde hier zur Fehlervermeidung entfernt)

    # 3. Historie der Entscheidungen (MIT AUSWIRKUNGEN)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "3. Chronik der Ereignisse (Auswirkungen auf das BIP):", ln=True)

    letztes_jahr = 0
    for eintrag in st.session_state.alle_entscheidungen:
        if eintrag['jahr'] != letztes_jahr:
            pdf.ln(3)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, f"--- Jahr {eintrag['jahr']} ---", ln=True)
            letztes_jahr = eintrag['jahr']

        # Titel fett drucken
        titel_sauber = clean_text(eintrag['log']['titel'])
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 6, f"> {titel_sauber}", ln=True)
        pdf.set_font("Arial", '', 10)

        # Hilfsfunktion, um die Dictionaries in sauberen Text umzuwandeln
        def format_dict(d):
            teile = []
            for k, v in d.items():
                if v != 0:
                    vorzeichen = "+" if v > 0 else ""
                    teile.append(f"{k} ({vorzeichen}{v})")
            return ", ".join(teile) if teile else "Keine"

        # Auslesen der Werte aus dem Logbuch
        log = eintrag['log']
        ent_str = clean_text(format_dict(log['ent']))
        ver_str = clean_text(format_dict(log['ver']))
        vert_str = clean_text(format_dict(log['vert']))

        # Eingerückt in das PDF schreiben
        pdf.set_x(20)
        pdf.cell(0, 5, f"Entstehung: {ent_str}", ln=True)
        pdf.set_x(20)
        pdf.cell(0, 5, f"Verwendung: {ver_str}", ln=True)
        pdf.set_x(20)
        pdf.cell(0, 5, f"Verteilung: {vert_str}", ln=True)
        pdf.ln(2)  # Kleine Lücke zwischen den Ereignissen

    return bytes(pdf.output(dest='S'), encoding='latin1')


def anwenden(option, titel, index):
    ereignis_log = {"titel": f"{titel} ({option['text']})", "ent": {}, "ver": {}, "vert": {}}

    for effekt in option["effekte"]:
        if effekt["typ"] == "wachstum":
            basis_wert = st.session_state.ent[effekt["basis"]]
            delta = int(basis_wert * effekt["prozent"])

            st.session_state.ent[effekt["basis"]] += delta
            ereignis_log["ent"][effekt["basis"]] = ereignis_log["ent"].get(effekt["basis"], 0) + delta

            verteilt_ver = 0
            items_ver = list(effekt["ver"].items())
            for i, (ziel, anteil) in enumerate(items_ver):
                v_delta = delta - verteilt_ver if i == len(items_ver) - 1 else int(delta * anteil)
                verteilt_ver += v_delta
                st.session_state.ver[ziel] += v_delta
                ereignis_log["ver"][ziel] = ereignis_log["ver"].get(ziel, 0) + v_delta

            verteilt_vert = 0
            items_vert = list(effekt["vert"].items())
            for i, (ziel, anteil) in enumerate(items_vert):
                v_delta = delta - verteilt_vert if i == len(items_vert) - 1 else int(delta * anteil)
                verteilt_vert += v_delta
                st.session_state.vert[ziel] += v_delta
                ereignis_log["vert"][ziel] = ereignis_log["vert"].get(ziel, 0) + v_delta

        elif effekt["typ"] == "verteilung_shift":
            basis_wert = st.session_state.vert[effekt["basis"]]
            delta = int(basis_wert * effekt["prozent"])
            anderes_ziel = "gewinne" if effekt["basis"] == "loehne" else "loehne"

            st.session_state.vert[effekt["basis"]] += delta
            st.session_state.vert[anderes_ziel] -= delta

            ereignis_log["vert"][effekt["basis"]] = ereignis_log["vert"].get(effekt["basis"], 0) + delta
            ereignis_log["vert"][anderes_ziel] = ereignis_log["vert"].get(anderes_ziel, 0) - delta

    st.session_state.ereignis_logbuch.append(ereignis_log)
    st.session_state.alle_entscheidungen.append({"jahr": st.session_state.jahr, "log": ereignis_log})
    st.session_state.entscheidungen_getroffen[index] = True


# --- 3. INITIALISIERUNG ---
if "setup" not in st.session_state:
    st.session_state.setup = False
    st.session_state.jahr = 1
    st.session_state.ziel_jahre = 5  # Standardwert
    st.session_state.bip_historie = []

    st.session_state.uebrige_szenarien = alle_szenarien.copy()
    random.shuffle(st.session_state.uebrige_szenarien)

    st.session_state.aktuelle_szenarien = []
    st.session_state.entscheidungen_getroffen = []
    st.session_state.ereignis_logbuch = []
    st.session_state.alle_entscheidungen = []
    st.session_state.start_bip = 0

    st.session_state.ent = {"landwirtschaft": 0, "industrie": 0, "dienstleistung": 0}
    st.session_state.ver = {"konsum": 0, "investitionen": 0, "staat": 0, "export": 0}
    st.session_state.vert = {"loehne": 0, "gewinne": 0}

# --- 4. UI: GRÜNDUNGSPHASE (LINKE SEITE) ---
with st.sidebar:
    st.header("🛠️ 1. Land gründen")
    if not st.session_state.setup:
        st.session_state.land_name = st.text_input("Landesname:", "Fantasia")
        st.session_state.waehrung = st.text_input("Währung:", "Taler")
        ziel_jahre_input = st.number_input("Dauer der Simulation (Jahre):", min_value=1, max_value=20, value=5)

        st.write("---")
        st.write("**Arbeitskräfte verteilen:**")
        anteil_agrar = st.slider("Landwirtschaft (%)", 0, 100, 15)
        anteil_industrie = st.slider("Industrie (%)", 0, 100, 45)
        anteil_dienst = st.slider("Dienstleistung (%)", 0, 100, 40)

        summe = anteil_agrar + anteil_industrie + anteil_dienst

        if summe == 100:
            st.success(f"Summe: {summe}% - Perfekt!")
            if st.button("Simulation starten", type="primary"):
                st.session_state.setup = True
                st.session_state.ziel_jahre = ziel_jahre_input  # Speichert die Dauer
                st.session_state.ent = {"landwirtschaft": anteil_agrar * 100, "industrie": anteil_industrie * 100,
                                        "dienstleistung": anteil_dienst * 100}
                bip = berechne_bip()
                st.session_state.ver = {"konsum": int(bip * 0.5), "investitionen": int(bip * 0.2),
                                        "staat": int(bip * 0.2), "export": int(bip * 0.1)}
                st.session_state.vert = {"loehne": int(bip * 0.65), "gewinne": int(bip * 0.35)}

                st.session_state.start_bip = bip
                sichere_vorjahr()
                st.session_state.aktuelle_szenarien = ziehe_3_szenarien()
                st.session_state.entscheidungen_getroffen = [False] * len(st.session_state.aktuelle_szenarien)
                st.rerun()
        else:
            st.error(f"Achtung: Die Summe muss exakt 100% ergeben! (Aktuell: {summe}%)")
    else:
        st.success(f"Regierung von {st.session_state.land_name}")
        st.metric("Aktuelles Jahr", f"{st.session_state.jahr} von {st.session_state.ziel_jahre}")
        if st.button("Neustart / Reset"):
            st.session_state.clear()
            st.rerun()
        st.write("---")
        pdf_daten = erstelle_pdf()
        st.download_button(
            label="📄 Verlauf als PDF exportieren",
            data=pdf_daten,
            file_name=f"Wirtschaftsbericht_{st.session_state.land_name}_Jahr_{st.session_state.jahr}.pdf",
            mime="application/pdf"
        )

# --- 5. UI: HAUPTBEREICH (SIMULATION) ---
if st.session_state.setup:
    st.title(f"🌍 {st.session_state.land_name}")

    # Prüfen, ob wir das Limit der Jahre überschritten haben (Spielende)
    if st.session_state.jahr > st.session_state.ziel_jahre:
        st.balloons()
        st.success(
            f"🏁 **Simulation beendet!** Du hast dein Land erfolgreich {st.session_state.ziel_jahre} Jahre lang regiert.")
        st.markdown("Schau dir unten im Dashboard an, wie sich deine Entscheidungen langfristig ausgewirkt haben.")
    else:
        st.subheader(f"Jahr {st.session_state.jahr}")
        if len(st.session_state.aktuelle_szenarien) > 0:
            alle_fertig = all(st.session_state.entscheidungen_getroffen)

            if not alle_fertig:
                st.markdown("Treffe eine Entscheidung für anstehende Ereignisse. **Sie verschwinden nach dem Klick!**")
                for i, sz in enumerate(st.session_state.aktuelle_szenarien):
                    if not st.session_state.entscheidungen_getroffen[i]:
                        st.markdown(f"### ⚡ {sz['titel']}")
                        st.write(sz["text"])

                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button(sz["option_a"]["text"], key=f"a_{st.session_state.jahr}_{sz['id']}",
                                         use_container_width=True):
                                anwenden(sz["option_a"], sz["titel"], i)
                                st.rerun()
                        with c2:
                            if st.button(sz["option_b"]["text"], key=f"b_{st.session_state.jahr}_{sz['id']}",
                                         use_container_width=True):
                                anwenden(sz["option_b"], sz["titel"], i)
                                st.rerun()
                        st.divider()
            else:
                st.success("✅ Du hast alle Entscheidungen für dieses Jahr getroffen.")

                # Check ob es das letzte Jahr ist, um den Button-Text anzupassen -
                if st.session_state.jahr < st.session_state.ziel_jahre:
                    if st.button("➡️ Jahr abschließen & Nächstes Jahr starten", type="primary"):
                        naechstes_jahr()
                else:
                    if st.button("🏁 Simulation beenden & Auswertung ansehen", type="primary"):
                        naechstes_jahr()
                        st.session_state.jahr -= 1
        else:
            st.warning("Es gibt keine weiteren Ereignisse mehr in der Datenbank! Die Simulation wird beendet.")

    st.markdown("---")

    st.markdown("---")

    # --- DASHBOARD & TABELLE/DIAGRAMM MIT LOGBUCH ---
    akt_bip = berechne_bip()
    st.header(f"📊 Wirtschafts-Dashboard (BIP: {akt_bip} {st.session_state.waehrung})")

    if len(st.session_state.bip_historie) > 0:
        # Historie inklusive aktuellem Jahr vorbereiten
        historie_komplett = st.session_state.bip_historie + [{"Jahr": st.session_state.jahr, "BIP": akt_bip}]
        df = pd.DataFrame(historie_komplett)

        # Tabs für Tabelle und Diagramm erstellen (Tabelle ist zuerst = Standard)
        tab_tabelle, tab_diagramm = st.tabs(["📋 Tabelle", "📈 Diagramm"])

        with tab_tabelle:
            st.dataframe(df, hide_index=True, use_container_width=True)

        with tab_diagramm:
            # Für das Diagramm nutzen wir das Jahr als Index
            df_chart = df.set_index("Jahr")
            st.line_chart(df_chart, y="BIP", height=200)


    def zeige_logs(kategorie, sektor_key):
        for log in st.session_state.ereignis_logbuch:
            if sektor_key in log[kategorie]:
                wert = log[kategorie][sektor_key]
                if wert != 0:
                    farbe = "green" if wert > 0 else "red"
                    vorzeichen = "+" if wert > 0 else ""
                    st.caption(f"_{log['titel']}_: :{farbe}[**{vorzeichen}{wert}**]")


    t1, t2, t3 = st.tabs(["🏭 Entstehung", "🛒 Verwendung", "💰 Verteilung"])

    with t1:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Landwirtschaft", st.session_state.ent["landwirtschaft"])
            zeige_logs("ent", "landwirtschaft")
        with c2:
            st.metric("Industrie", st.session_state.ent["industrie"])
            zeige_logs("ent", "industrie")
        with c3:
            st.metric("Dienstleistung", st.session_state.ent["dienstleistung"])
            zeige_logs("ent", "dienstleistung")

    with t2:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Konsum", st.session_state.ver["konsum"])
            zeige_logs("ver", "konsum")
        with c2:
            st.metric("Investitionen", st.session_state.ver["investitionen"])
            zeige_logs("ver", "investitionen")
        with c3:
            st.metric("Staatsausgaben", st.session_state.ver["staat"])
            zeige_logs("ver", "staat")
        with c4:
            st.metric("Nettoexporte", st.session_state.ver["export"])
            zeige_logs("ver", "export")

    with t3:
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Löhne", st.session_state.vert["loehne"])
            zeige_logs("vert", "loehne")
        with c2:
            st.metric("Gewinne", st.session_state.vert["gewinne"])
            zeige_logs("vert", "gewinne")