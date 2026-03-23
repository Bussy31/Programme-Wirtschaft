import streamlit as st
import random

# --- Seitenkonfiguration ---
st.set_page_config(page_title="Musterland BIP Simulator", layout="wide")

# --- Initialisierung des Wirtschafts-Status (Session State) ---
# Das ist wichtig, damit Streamlit die Werte beim Klicken nicht vergisst.
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.land_name = "Fantasia"
    st.session_state.waehrung = "Taler"

    # Basiswerte Entstehungsrechnung
    st.session_state.ent_landwirtschaft = 2000
    st.session_state.ent_industrie = 5000
    st.session_state.ent_dienstleistung = 3000

    # Basiswerte Verwendungsrechnung
    st.session_state.ver_konsum = 6000
    st.session_state.ver_investitionen = 2000
    st.session_state.ver_staat = 1500
    st.session_state.ver_export_netto = 500

    # Basiswerte Verteilungsrechnung
    st.session_state.vert_loehne = 6500
    st.session_state.vert_gewinne = 3500

    st.session_state.letztes_szenario = "Willkommen in deinem Musterland! Ziehe eine Ereigniskarte, um zu sehen, wie sich die Wirtschaft entwickelt."

# --- Szenarien-Datenbank ---
# Jedes Szenario verändert die Werte so, dass das BIP am Ende bei allen 3 Methoden gleich bleibt!
szenarien = [
    {
        "titel": "Der Staat baut eine neue Autobahn",
        "text": "Die Regierung investiert massiv in die Infrastruktur. Bauunternehmen haben volle Auftragsbücher und stellen neue Leute ein.",
        "effekt_ent": {"ent_industrie": 1000},
        "effekt_ver": {"ver_staat": 1000},
        "effekt_vert": {"vert_loehne": 700, "vert_gewinne": 300}
    },
    {
        "titel": "Unwetter zerstört Ernte",
        "text": "Ein heftiger Sturm vernichtet einen Großteil der Apfelernte. Die Bauern machen Verluste und die Leute können weniger Obst kaufen.",
        "effekt_ent": {"ent_landwirtschaft": -500},
        "effekt_ver": {"ver_konsum": -500},
        "effekt_vert": {"vert_gewinne": -500}
    },
    {
        "titel": "Lohnkürzungen in der Fahrradfabrik",
        "text": "Die Chefs der Industrie kürzen die Löhne der Arbeiter um 10%. Die Produktion bleibt gleich, aber die Arbeiter haben weniger Geld, während die Chefs mehr Gewinn verbuchen.",
        "effekt_ent": {},  # Keine Änderung bei der Entstehung!
        "effekt_ver": {},  # Keine Änderung bei der Verwendung (in diesem vereinfachten Modell)!
        "effekt_vert": {"vert_loehne": -400, "vert_gewinne": 400}  # Nullsummenspiel
    },
    {
        "titel": "Export-Boom bei Maschinen",
        "text": "Das Ausland reißt uns unsere Industrieprodukte aus den Händen. Die Fabriken machen Rekordgewinne.",
        "effekt_ent": {"ent_industrie": 800},
        "effekt_ver": {"ver_export_netto": 800},
        "effekt_vert": {"vert_gewinne": 800}
    },
    {
        "titel": "Bürger gehen öfter ins Restaurant",
        "text": "Die Stimmung ist gut! Die Menschen sparen weniger und geben ihr Geld lieber für Friseure, Restaurants und Kinos aus.",
        "effekt_ent": {"ent_dienstleistung": 600},
        "effekt_ver": {"ver_konsum": 600},
        "effekt_vert": {"vert_loehne": 400, "vert_gewinne": 200}
    }
]


# --- Funktion zum Anwenden eines Szenarios ---
def anwenden_szenario(szenario):
    st.session_state.letztes_szenario = f"**{szenario['titel']}**\n\n{szenario['text']}"

    for key, val in szenario["effekt_ent"].items():
        st.session_state[key] += val
    for key, val in szenario["effekt_ver"].items():
        st.session_state[key] += val
    for key, val in szenario["effekt_vert"].items():
        st.session_state[key] += val


# --- UI Aufbau ---
st.title("🌍 Mein Musterland: Der BIP-Simulator")
st.markdown("Baue deine Wirtschaft auf und beobachte, wie sich Ereignisse auf das Bruttoinlandsprodukt auswirken!")

# Sidebar für Steuerung
with st.sidebar:
    st.header("⚙️ Steuerung")
    st.session_state.land_name = st.text_input("Name deines Landes:", st.session_state.land_name)
    st.session_state.waehrung = st.text_input("Währung:", st.session_state.waehrung)

    st.divider()
    st.subheader("🎲 Ereigniskarte ziehen")
    if st.button("Zufälliges Ereignis auslösen", type="primary"):
        gewaehltes_szenario = random.choice(szenarien)
        anwenden_szenario(gewaehltes_szenario)

    if st.button("Wirtschaft zurücksetzen"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Ereignis-Anzeige
st.info(st.session_state.letztes_szenario)

# --- Berechnungen für die Anzeige ---
summe_ent = st.session_state.ent_landwirtschaft + st.session_state.ent_industrie + st.session_state.ent_dienstleistung
summe_ver = st.session_state.ver_konsum + st.session_state.ver_investitionen + st.session_state.ver_staat + st.session_state.ver_export_netto
summe_vert = st.session_state.vert_loehne + st.session_state.vert_gewinne

st.header(f"Das Bruttoinlandsprodukt von {st.session_state.land_name}")

# --- Tabs für die drei Berechnungsarten ---
tab1, tab2, tab3 = st.tabs(["🏭 Entstehungsrechnung", "🛒 Verwendungsrechnung", "💰 Verteilungsrechnung"])

with tab1:
    st.subheader("Wer hat den Wert erschaffen?")
    st.markdown("Summe aller produzierten Güter und Dienstleistungen (Bruttowertschöpfung).")
    col1, col2, col3 = st.columns(3)
    col1.metric("Landwirtschaft", f"{st.session_state.ent_landwirtschaft} {st.session_state.waehrung}")
    col2.metric("Industrie", f"{st.session_state.ent_industrie} {st.session_state.waehrung}")
    col3.metric("Dienstleistungen", f"{st.session_state.ent_dienstleistung} {st.session_state.waehrung}")
    st.success(f"**BIP (Entstehung): {summe_ent} {st.session_state.waehrung}**")

with tab2:
    st.subheader("Wer kauft die Produkte?")
    st.markdown("Formel: Konsum + Investitionen + Staatsausgaben + Nettoexporte")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Privater Konsum (C)", f"{st.session_state.ver_konsum} {st.session_state.waehrung}")
    col2.metric("Investitionen (I)", f"{st.session_state.ver_investitionen} {st.session_state.waehrung}")
    col3.metric("Staatsausgaben (G)", f"{st.session_state.ver_staat} {st.session_state.waehrung}")
    col4.metric("Nettoexporte (NX)", f"{st.session_state.ver_export_netto} {st.session_state.waehrung}")
    st.success(f"**BIP (Verwendung): {summe_ver} {st.session_state.waehrung}**")

with tab3:
    st.subheader("Wer bekommt das Geld?")
    st.markdown("Aufteilung des Einkommens in Löhne (Arbeitnehmer) und Gewinne (Unternehmen).")
    col1, col2 = st.columns(2)
    col1.metric("Löhne (Arbeitnehmerentgelt)", f"{st.session_state.vert_loehne} {st.session_state.waehrung}")
    col2.metric("Gewinne (Unternehmens-/Vermögenseinkommen)",
                f"{st.session_state.vert_gewinne} {st.session_state.waehrung}")
    st.success(f"**BIP (Verteilung): {summe_vert} {st.session_state.waehrung}**")

# Sicherheitscheck für die Logik (Nur zur Kontrolle, ob du die Szenarien richtig programmiert hast)
if not (summe_ent == summe_ver == summe_vert):
    st.error("Achtung! Die makroökonomische Logik ist fehlerhaft. Das BIP der drei Methoden stimmt nicht überein!")