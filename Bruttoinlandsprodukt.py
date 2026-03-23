import streamlit as st

st.set_page_config(page_title="Musterland BIP Simulator", layout="wide")

# --- Initialisierung (Session State) ---
if "setup_abgeschlossen" not in st.session_state:
    st.session_state.setup_abgeschlossen = False
    st.session_state.land_name = ""
    st.session_state.waehrung = "Taler"
    st.session_state.nachricht = "Willkommen! Bitte gründe zuerst dein Land in der Seitenleiste."

    # Wirtschaftsdaten
    st.session_state.ent = {"landwirtschaft": 0, "industrie": 0, "dienstleistung": 0}
    st.session_state.ver = {"konsum": 0, "investitionen": 0, "staat": 0, "export": 0}
    st.session_state.vert = {"loehne": 0, "gewinne": 0}

# --- Szenarien mit ENTSCHEIDUNGEN ---
# Hier haben die Schüler jetzt die Wahl!
szenarien = {
    "krise": {
        "titel": "🚨 Wirtschaftskrise: Die Nachfrage bricht ein!",
        "text": "Die Bürger haben Angst vor der Zukunft und sparen ihr Geld, statt es auszugeben. Der Konsum sinkt. Was tust du?",
        "option_a": {
            "text": "Option A: Der Staat greift ein und baut neue Schulen (Staatsausgaben erhöhen).",
            "effekt_ent": {"industrie": 1000},  # Bauwirtschaft brummt
            "effekt_ver": {"staat": 1000},  # Staat zahlt
            "effekt_vert": {"loehne": 800, "gewinne": 200},
            "feedback": "Gute Wahl! Die Staatsausgaben haben die Krise abgefedert. Die Bauarbeiter haben gute Löhne bekommen."
        },
        "option_b": {
            "text": "Option B: Steuern für Unternehmen senken, damit sie investieren.",
            "effekt_ent": {"dienstleistung": 800},  # Mehr Aufträge für Berater/IT
            "effekt_ver": {"investitionen": 800},
            "effekt_vert": {"loehne": 200, "gewinne": 600},
            "feedback": "Die Unternehmen freuen sich über die Steuergeschenke und investieren. Allerdings steigen vor allem die Gewinne, weniger die Löhne."
        }
    },
    "technologie": {
        "titel": "🔬 technologischer Durchbruch!",
        "text": "Eine neue Maschine wurde erfunden, die Fahrräder doppelt so schnell baut. Wie nutzt dein Land das?",
        "option_a": {
            "text": "Option A: Wir exportieren die Maschinen ins Ausland!",
            "effekt_ent": {"industrie": 1200},
            "effekt_ver": {"export": 1200},
            "effekt_vert": {"loehne": 500, "gewinne": 700},
            "feedback": "Dein Land wird zum Exportweltmeister! Die Industrie floriert und die Unternehmensgewinne schießen in die Höhe."
        },
        "option_b": {
            "text": "Option B: Wir nutzen sie im Inland, um billigere Fahrräder für alle Bürger zu bauen.",
            "effekt_ent": {"industrie": 800},
            "effekt_ver": {"konsum": 800},
            "effekt_vert": {"loehne": 400, "gewinne": 400},
            "feedback": "Der private Konsum steigt, weil sich jetzt jeder ein Fahrrad leisten kann. Ein ausgeglichenes Wachstum!"
        }
    }
}


# --- Funktion zum Anwenden der Entscheidung ---
def wende_entscheidung_an(option, feedback_text):
    for key, val in option["effekt_ent"].items():
        st.session_state.ent[key] += val
    for key, val in option["effekt_ver"].items():
        st.session_state.ver[key] += val
    for key, val in option["effekt_vert"].items():
        st.session_state.vert[key] += val
    st.session_state.nachricht = f"✅ **Auswirkung:** {feedback_text}"


# --- UI Aufbau: Seitenleiste (Gründungsphase) ---
with st.sidebar:
    st.header("🛠️ 1. Land gründen")

    if not st.session_state.setup_abgeschlossen:
        land = st.text_input("Name deines Landes:", "Fantasia")
        waehrung = st.text_input("Währung:", "Taler")

        st.write("**Verteile 100% deiner Arbeitskräfte:**")
        # Slider für die Wirtschaftssektoren
        anteil_agrar = st.slider("Landwirtschaft (%)", 0, 100, 20)
        anteil_industrie = st.slider("Industrie (%)", 0, 100 - anteil_agrar, 50)
        anteil_dienst = 100 - (anteil_agrar + anteil_industrie)
        st.info(f"Dienstleistungen: {anteil_dienst}% (wird automatisch berechnet)")

        if st.button("Wirtschaft starten", type="primary"):
            st.session_state.setup_abgeschlossen = True
            st.session_state.land_name = land
            st.session_state.waehrung = waehrung

            # Startwerte berechnen (1% = 100 Währungseinheiten)
            st.session_state.ent["landwirtschaft"] = anteil_agrar * 100
            st.session_state.ent["industrie"] = anteil_industrie * 100
            st.session_state.ent["dienstleistung"] = anteil_dienst * 100

            basis_bip = 100 * 100  # Gesamt-BIP am Start ist immer 10000

            # Verwendungsrechnung Start (vereinfachte Standardverteilung)
            st.session_state.ver["konsum"] = int(basis_bip * 0.55)
            st.session_state.ver["investitionen"] = int(basis_bip * 0.20)
            st.session_state.ver["staat"] = int(basis_bip * 0.20)
            st.session_state.ver["export"] = int(basis_bip * 0.05)

            # Verteilungsrechnung Start
            st.session_state.vert["loehne"] = int(basis_bip * 0.70)
            st.session_state.vert["gewinne"] = int(basis_bip * 0.30)

            st.session_state.nachricht = "Wirtschaft erfolgreich gestartet! Du bist jetzt Wirtschaftsminister."
            st.rerun()
    else:
        st.success(f"Land: {st.session_state.land_name}")
        if st.button("Neu starten"):
            st.session_state.clear()
            st.rerun()

# --- Hauptbereich ---
st.title("🌍 Mein Musterland")

if st.session_state.setup_abgeschlossen:
    # 1. Feedback anzeigen
    st.info(st.session_state.nachricht)

    # 2. Entscheidungs-Bereich (Hier ist die Interaktivität!)
    st.markdown("---")
    st.subheader("⚖️ Als Wirtschaftsminister musst du entscheiden:")

    # Für das Beispiel zeigen wir einfach beide Szenarien untereinander,
    # man könnte sie später auch nacheinander aufrufen.
    col_sz1, col_sz2 = st.columns(2)

    with col_sz1:
        st.write(f"**{szenarien['krise']['titel']}**")
        st.write(szenarien['krise']['text'])
        if st.button(szenarien['krise']['option_a']['text'], key="k_a"):
            wende_entscheidung_an(szenarien['krise']['option_a'], szenarien['krise']['option_a']['feedback'])
            st.rerun()
        if st.button(szenarien['krise']['option_b']['text'], key="k_b"):
            wende_entscheidung_an(szenarien['krise']['option_b'], szenarien['krise']['option_b']['feedback'])
            st.rerun()

    with col_sz2:
        st.write(f"**{szenarien['technologie']['titel']}**")
        st.write(szenarien['technologie']['text'])
        if st.button(szenarien['technologie']['option_a']['text'], key="t_a"):
            wende_entscheidung_an(szenarien['technologie']['option_a'],
                                  szenarien['technologie']['option_a']['feedback'])
            st.rerun()
        if st.button(szenarien['technologie']['option_b']['text'], key="t_b"):
            wende_entscheidung_an(szenarien['technologie']['option_b'],
                                  szenarien['technologie']['option_b']['feedback'])
            st.rerun()

    st.markdown("---")

    # 3. BIP Dashboard (Die drei Säulen)
    summe_ent = sum(st.session_state.ent.values())
    summe_ver = sum(st.session_state.ver.values())
    summe_vert = sum(st.session_state.vert.values())

    st.header(f"📊 Dashboard: Das BIP von {st.session_state.land_name}")

    tab1, tab2, tab3 = st.tabs(["🏭 Entstehung", "🛒 Verwendung", "💰 Verteilung"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Landwirtschaft", f"{st.session_state.ent['landwirtschaft']} {st.session_state.waehrung}")
        c2.metric("Industrie", f"{st.session_state.ent['industrie']} {st.session_state.waehrung}")
        c3.metric("Dienstleistungen", f"{st.session_state.ent['dienstleistung']} {st.session_state.waehrung}")
        st.success(f"BIP (Entstehung): {summe_ent} {st.session_state.waehrung}")

    with tab2:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Konsum", f"{st.session_state.ver['konsum']} {st.session_state.waehrung}")
        c2.metric("Investitionen", f"{st.session_state.ver['investitionen']} {st.session_state.waehrung}")
        c3.metric("Staat", f"{st.session_state.ver['staat']} {st.session_state.waehrung}")
        c4.metric("Nettoexporte", f"{st.session_state.ver['export']} {st.session_state.waehrung}")
        st.success(f"BIP (Verwendung): {summe_ver} {st.session_state.waehrung}")

    with tab3:
        c1, c2 = st.columns(2)
        c1.metric("Löhne", f"{st.session_state.vert['loehne']} {st.session_state.waehrung}")
        c2.metric("Gewinne", f"{st.session_state.vert['gewinne']} {st.session_state.waehrung}")
        st.success(f"BIP (Verteilung): {summe_vert} {st.session_state.waehrung}")

else:
    st.warning("👈 Bitte richte dein Land in der linken Seitenleiste ein, um zu beginnen!")