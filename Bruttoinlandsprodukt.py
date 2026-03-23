import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="Musterland Simulation", layout="wide", initial_sidebar_state="expanded")

# --- 1. DATENBANK DER SZENARIEN ---
alle_szenarien = [
    {
        "id": "krise", "titel": "🚨 Wirtschaftskrise: Die Nachfrage bricht ein!",
        "text": "Die Bürger haben Angst vor der Zukunft und sparen ihr Geld, statt es auszugeben. Der Konsum sinkt drastisch.",
        "option_a": {"text": "Staatliche Bauprojekte starten (Schulden machen)", "ent": {"industrie": 1000},
                     "ver": {"staat": 1000}, "vert": {"loehne": 800, "gewinne": 200},
                     "msg": "Die Staatsausgaben haben die Krise abgefedert!"},
        "option_b": {"text": "Steuern für Unternehmen senken", "ent": {"dienstleistung": 500},
                     "ver": {"investitionen": 500}, "vert": {"loehne": 100, "gewinne": 400},
                     "msg": "Die Unternehmen investieren ein wenig, aber die breite Masse hat weiterhin kein Geld."}
    },
    {
        "id": "tech", "titel": "🔬 Technologischer Durchbruch!",
        "text": "Eine neue KI wurde entwickelt, die viele Prozesse in der Dienstleistung automatisiert.",
        "option_a": {"text": "Technologie ins Ausland verkaufen", "ent": {"dienstleistung": 1200},
                     "ver": {"export": 1200}, "vert": {"loehne": 300, "gewinne": 900},
                     "msg": "Ein Export-Hit! Die Gewinne der IT-Firmen explodieren."},
        "option_b": {"text": "Technologie für eigene Bürger subventionieren", "ent": {"dienstleistung": 800},
                     "ver": {"konsum": 800}, "vert": {"loehne": 600, "gewinne": 200},
                     "msg": "Die Bürger profitieren enorm, der private Konsum steigt."}
    },
    {
        "id": "natur", "titel": "🌪️ Naturkatastrophe",
        "text": "Ein schweres Unwetter hat Teile der landwirtschaftlichen Ernte zerstört.",
        "option_a": {"text": "Bauern finanziell entschädigen", "ent": {"landwirtschaft": -500},
                     "ver": {"staat": 500, "konsum": -1000}, "vert": {"loehne": -200, "gewinne": -300},
                     "msg": "Der Staat greift ein. Das dämpft den Fall, kostet aber staatliches Geld."},
        "option_b": {"text": "Nichts tun (Freier Markt)", "ent": {"landwirtschaft": -1000}, "ver": {"konsum": -1000},
                     "vert": {"loehne": -400, "gewinne": -600},
                     "msg": "Harte Zeiten für die Bauern. Das BIP bricht in diesem Sektor ein."}
    },
    {
        "id": "streik", "titel": "🪧 Großer Streik der LKW-Fahrer",
        "text": "Die Logistik steht still, weil die Fahrer mehr Lohn fordern. Die Industrie kann nicht liefern.",
        "option_a": {"text": "Unternehmen zwingen, Löhne zu erhöhen", "ent": {"industrie": -200},
                     "ver": {"export": -200}, "vert": {"loehne": +500, "gewinne": -700},
                     "msg": "Die Gewinne brechen ein, aber die Löhne steigen! Das BIP verändert sich kaum, nur die Verteilung."},
        "option_b": {"text": "Streik verbieten (Wirtschaft schützen)", "ent": {"industrie": 400},
                     "ver": {"export": 400}, "vert": {"loehne": 0, "gewinne": 400},
                     "msg": "Die Industrie brummt weiter, aber die Unzufriedenheit der Arbeiter wächst (Löhne stagnieren)."}
    }
]

# --- 2. INITIALISIERUNG DES STATE ---
if "setup" not in st.session_state:
    st.session_state.setup = False
    st.session_state.jahr = 1
    st.session_state.bip_historie = []

    # Pools für die Runden
    st.session_state.uebrige_szenarien = alle_szenarien.copy()
    random.shuffle(st.session_state.uebrige_szenarien)
    st.session_state.aktuelles_szenario = st.session_state.uebrige_szenarien.pop()
    st.session_state.entscheidung_getroffen = False
    st.session_state.ereignis_feedback = ""

    # Wirtschaftsdaten (Aktuelles Jahr)
    st.session_state.ent = {"landwirtschaft": 0, "industrie": 0, "dienstleistung": 0}
    st.session_state.ver = {"konsum": 0, "investitionen": 0, "staat": 0, "export": 0}
    st.session_state.vert = {"loehne": 0, "gewinne": 0}

    # Wirtschaftsdaten (Vorjahr für Delta-Berechnung)
    st.session_state.alt_ent = {}
    st.session_state.alt_ver = {}
    st.session_state.alt_vert = {}
    st.session_state.alt_bip = 0


# --- 3. HILFSFUNKTIONEN ---
def berechne_bip():
    return sum(st.session_state.ent.values())


def sichere_vorjahr():
    st.session_state.alt_ent = st.session_state.ent.copy()
    st.session_state.alt_ver = st.session_state.ver.copy()
    st.session_state.alt_vert = st.session_state.vert.copy()
    st.session_state.alt_bip = berechne_bip()


def naechstes_jahr():
    sichere_vorjahr()
    # Aktuelles BIP in der Historie speichern
    st.session_state.bip_historie.append({"Jahr": st.session_state.jahr, "BIP": berechne_bip()})

    st.session_state.jahr += 1
    st.session_state.entscheidung_getroffen = False
    st.session_state.ereignis_feedback = ""

    if len(st.session_state.uebrige_szenarien) > 0:
        st.session_state.aktuelles_szenario = st.session_state.uebrige_szenarien.pop()
    else:
        st.session_state.aktuelles_szenario = None  # Spielende
    st.rerun()


def anwenden(option):
    for k, v in option["ent"].items(): st.session_state.ent[k] += v
    for k, v in option["ver"].items(): st.session_state.ver[k] += v
    for k, v in option["vert"].items(): st.session_state.vert[k] += v
    st.session_state.ereignis_feedback = option["msg"]
    st.session_state.entscheidung_getroffen = True


# --- 4. UI: GRÜNDUNGSPHASE ---
with st.sidebar:
    st.header("🛠️ 1. Land gründen")
    if not st.session_state.setup:
        st.session_state.land_name = st.text_input("Landesname:", "Ecotopia")
        st.session_state.waehrung = st.text_input("Währung:", "Taler")
        st.write("**Arbeitskräfte verteilen (Start-Wirtschaft):**")
        anteil_agrar = st.slider("Landwirtschaft (%)", 0, 100, 15)
        anteil_industrie = st.slider("Industrie (%)", 0, 100 - anteil_agrar, 45)
        anteil_dienst = 100 - (anteil_agrar + anteil_industrie)
        st.info(f"Dienstleistungen: {anteil_dienst}%")

        if st.button("Simulation starten", type="primary"):
            st.session_state.setup = True
            # Startwerte berechnen (Multiplier: 100)
            st.session_state.ent = {"landwirtschaft": anteil_agrar * 100, "industrie": anteil_industrie * 100,
                                    "dienstleistung": anteil_dienst * 100}
            bip = berechne_bip()
            st.session_state.ver = {"konsum": int(bip * 0.5), "investitionen": int(bip * 0.2), "staat": int(bip * 0.2),
                                    "export": int(bip * 0.1)}
            st.session_state.vert = {"loehne": int(bip * 0.65), "gewinne": int(bip * 0.35)}
            sichere_vorjahr()
            st.rerun()
    else:
        st.success(f"Regierung von {st.session_state.land_name}")
        st.metric("Aktuelles Jahr", st.session_state.jahr)
        if st.button("Neustart / Reset"):
            st.session_state.clear()
            st.rerun()

# --- 5. UI: HAUPTBEREICH (SIMULATION) ---
if st.session_state.setup:
    st.title(f"🌍 {st.session_state.land_name} - Jahr {st.session_state.jahr}")

    # --- AKTIVES REGIERUNGSPULT (Das können sie JEDES Jahr machen) ---
    with st.expander("🏛️ Regierungspult: Deine aktiven Maßnahmen für dieses Jahr", expanded=True):
        st.markdown("Hier kannst du als Minister aktiv in die Wirtschaft eingreifen.")
        col_reg1, col_reg2 = st.columns(2)
        with col_reg1:
            steuern = st.selectbox("Steuerpolitik anpassen:", ["Keine Änderung", "Steuern senken (Fördert Konsum)",
                                                               "Steuern erhöhen (Fördert Staat)"])
        with col_reg2:
            subvention = st.selectbox("Subventionen vergeben an:",
                                      ["Niemanden", "Landwirtschaft", "Industrie", "Dienstleistung"])

        if st.button("Maßnahmen durchsetzen"):
            # Einfache Logik für aktive Eingriffe:
            if steuern == "Steuern senken (Fördert Konsum)":
                anwenden({"ent": {}, "ver": {"staat": -400, "konsum": 400}, "vert": {"loehne": 200, "gewinne": 200},
                          "msg": "Steuern gesenkt: Der Staat hat weniger, Bürger mehr."})
            elif steuern == "Steuern erhöhen (Fördert Staat)":
                anwenden({"ent": {}, "ver": {"staat": 400, "konsum": -400}, "vert": {"loehne": -200, "gewinne": -200},
                          "msg": "Steuern erhöht: Staatseinnahmen steigen, Konsum sinkt."})

            if subvention != "Niemanden":
                sektor = subvention.lower()
                anwenden({"ent": {sektor: 300}, "ver": {"staat": 300}, "vert": {"gewinne": 300, "loehne": 0},
                          "msg": f"{subvention} wurde gefördert!"})
            st.success("Gesetze wurden erlassen!")

    st.markdown("---")

    # --- ZUFALLS-SZENARIO ---
    if st.session_state.aktuelles_szenario:
        sz = st.session_state.aktuelles_szenario
        st.subheader(sz["titel"])
        st.write(sz["text"])

        # HIER IST DER TRICK: Knöpfe verschwinden, wenn Entscheidung getroffen!
        if not st.session_state.entscheidung_getroffen:
            c1, c2 = st.columns(2)
            with c1:
                if st.button(sz["option_a"]["text"], use_container_width=True):
                    anwenden(sz["option_a"])
                    st.rerun()
            with c2:
                if st.button(sz["option_b"]["text"], use_container_width=True):
                    anwenden(sz["option_b"])
                    st.rerun()
        else:
            st.info(f"✅ **Auswirkung:** {st.session_state.ereignis_feedback}")
            if st.button("➡️ Jahr abschließen & Nächste Runde", type="primary"):
                naechstes_jahr()
    else:
        st.success("🎉 Du hast alle Szenarien durchgespielt! Schau dir deine Wirtschaftsdaten an.")

    st.markdown("---")

    # --- DASHBOARD & DIAGRAMME ---
    akt_bip = berechne_bip()
    st.header(f"📊 Wirtschafts-Dashboard (BIP: {akt_bip} {st.session_state.waehrung})")

    # Diagramm-Verlauf anzeigen, wenn es Historie gibt
    if len(st.session_state.bip_historie) > 0:
        df = pd.DataFrame(st.session_state.bip_historie).set_index("Jahr")
        # Füge aktuelles Jahr temporär zum Graphen hinzu
        df.loc[st.session_state.jahr] = akt_bip
        st.line_chart(df, y="BIP", height=200)

    # Tabs mit Metriken und Delta (Veränderung zum Vorjahr)
    t1, t2, t3 = st.tabs(["🏭 Entstehung", "🛒 Verwendung", "💰 Verteilung"])


    def delta(aktuell, alt):
        return int(aktuell - alt)


    with t1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Landwirtschaft", st.session_state.ent["landwirtschaft"],
                  delta(st.session_state.ent["landwirtschaft"], st.session_state.alt_ent["landwirtschaft"]))
        c2.metric("Industrie", st.session_state.ent["industrie"],
                  delta(st.session_state.ent["industrie"], st.session_state.alt_ent["industrie"]))
        c3.metric("Dienstleistung", st.session_state.ent["dienstleistung"],
                  delta(st.session_state.ent["dienstleistung"], st.session_state.alt_ent["dienstleistung"]))

    with t2:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Privater Konsum", st.session_state.ver["konsum"],
                  delta(st.session_state.ver["konsum"], st.session_state.alt_ver["konsum"]))
        c2.metric("Investitionen", st.session_state.ver["investitionen"],
                  delta(st.session_state.ver["investitionen"], st.session_state.alt_ver["investitionen"]))
        c3.metric("Staatsausgaben", st.session_state.ver["staat"],
                  delta(st.session_state.ver["staat"], st.session_state.alt_ver["staat"]))
        c4.metric("Nettoexporte", st.session_state.ver["export"],
                  delta(st.session_state.ver["export"], st.session_state.alt_ver["export"]))

    with t3:
        c1, c2 = st.columns(2)
        c1.metric("Löhne (Arbeitnehmer)", st.session_state.vert["loehne"],
                  delta(st.session_state.vert["loehne"], st.session_state.alt_vert["loehne"]))
        c2.metric("Gewinne (Unternehmen)", st.session_state.vert["gewinne"],
                  delta(st.session_state.vert["gewinne"], st.session_state.alt_vert["gewinne"]))

else:
    st.info("Bitte gründe dein Land in der Seitenleiste (links).")