import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="Musterland Simulation", layout="wide", initial_sidebar_state="expanded")

# --- 1. DATENBANK DER SZENARIEN ---
# (Für den Test auf 6 aufgestockt, damit wir 2 Jahre à 3 Ereignisse haben)
alle_szenarien = [
    {
        "id": "krise", "titel": "🚨 Wirtschaftskrise",
        "text": "Die Bürger haben Angst vor der Zukunft und sparen ihr Geld. Der Konsum sinkt drastisch.",
        "option_a": {"text": "Staatliche Bauprojekte starten", "ent": {"industrie": 1000}, "ver": {"staat": 1000},
                     "vert": {"loehne": 800, "gewinne": 200}, "msg": "Die Bauaufträge federn die Krise ab!"},
        "option_b": {"text": "Steuern für Unternehmen senken", "ent": {"dienstleistung": 500},
                     "ver": {"investitionen": 500}, "vert": {"loehne": 100, "gewinne": 400},
                     "msg": "Die Unternehmen investieren, aber die Masse hat weiterhin kein Geld."}
    },
    {
        "id": "tech", "titel": "🔬 Neue KI-Software",
        "text": "Eine neue KI wurde entwickelt, die Prozesse in der Dienstleistung automatisiert.",
        "option_a": {"text": "Ins Ausland verkaufen", "ent": {"dienstleistung": 1200}, "ver": {"export": 1200},
                     "vert": {"loehne": 300, "gewinne": 900},
                     "msg": "Ein Export-Hit! Die Gewinne der IT-Firmen explodieren."},
        "option_b": {"text": "Für eigene Bürger subventionieren", "ent": {"dienstleistung": 800},
                     "ver": {"konsum": 800}, "vert": {"loehne": 600, "gewinne": 200},
                     "msg": "Bürger profitieren, der private Konsum steigt."}
    },
    {
        "id": "natur", "titel": "🌪️ Ernteausfall",
        "text": "Ein schweres Unwetter hat Teile der Ernte zerstört.",
        "option_a": {"text": "Bauern entschädigen", "ent": {"landwirtschaft": -500},
                     "ver": {"staat": 500, "konsum": -1000}, "vert": {"loehne": -200, "gewinne": -300},
                     "msg": "Der Staat hilft, was Steuergelder kostet."},
        "option_b": {"text": "Nichts tun", "ent": {"landwirtschaft": -1000}, "ver": {"konsum": -1000},
                     "vert": {"loehne": -400, "gewinne": -600},
                     "msg": "Harte Zeiten für die Bauern. Das BIP bricht hier ein."}
    },
    {
        "id": "streik", "titel": "🪧 LKW-Fahrer streiken",
        "text": "Die Logistik steht still. Die Industrie kann nicht liefern.",
        "option_a": {"text": "Löhne erhöhen lassen", "ent": {"industrie": -200}, "ver": {"export": -200},
                     "vert": {"loehne": +500, "gewinne": -700},
                     "msg": "Die Gewinne brechen ein, aber die Löhne steigen!"},
        "option_b": {"text": "Streik verbieten", "ent": {"industrie": 400}, "ver": {"export": 400},
                     "vert": {"loehne": 0, "gewinne": 400}, "msg": "Industrie brummt, aber Unzufriedenheit wächst."}
    },
    {
        "id": "tourismus", "titel": "🏖️ Tourismus-Boom",
        "text": "Ein berühmter Film wurde hier gedreht. Touristen stürmen das Land.",
        "option_a": {"text": "Hotels ausbauen (Fokus Ausland)", "ent": {"dienstleistung": 600}, "ver": {"export": 600},
                     "vert": {"loehne": 200, "gewinne": 400},
                     "msg": "Der Tourismus-Export bringt frisches Geld von außen!"},
        "option_b": {"text": "Freizeitparks bauen (Fokus Inland)", "ent": {"dienstleistung": 400},
                     "ver": {"konsum": 400}, "vert": {"loehne": 300, "gewinne": 100},
                     "msg": "Die eigenen Bürger geben mehr Geld für Freizeit aus."}
    },
    {
        "id": "subvention", "titel": "🚜 Traktoren-Mangel",
        "text": "Die Landwirtschaft braucht neue Maschinen, aber diese sind zu teuer.",
        "option_a": {"text": "Staat kauft Traktoren", "ent": {"industrie": 300}, "ver": {"staat": 300},
                     "vert": {"loehne": 100, "gewinne": 200},
                     "msg": "Die heimische Industrie freut sich über den Staatsauftrag."},
        "option_b": {"text": "Bauern Kredite geben", "ent": {"landwirtschaft": 200}, "ver": {"investitionen": 200},
                     "vert": {"loehne": 100, "gewinne": 100}, "msg": "Die Bauern investieren selbst in ihre Zukunft."}
    }
]


# --- 2. HILFSFUNKTIONEN FÜR RUNDEN ---
def ziehe_3_szenarien():
    gezogen = []
    # Ziehe bis zu 3 Szenarien (falls weniger übrig sind, nimmt er den Rest)
    for _ in range(3):
        if len(st.session_state.uebrige_szenarien) > 0:
            gezogen.append(st.session_state.uebrige_szenarien.pop())
    return gezogen


def berechne_bip():
    return sum(st.session_state.ent.values())


def sichere_vorjahr():
    st.session_state.alt_ent = st.session_state.ent.copy()
    st.session_state.alt_ver = st.session_state.ver.copy()
    st.session_state.alt_vert = st.session_state.vert.copy()
    st.session_state.alt_bip = berechne_bip()


def naechstes_jahr():
    sichere_vorjahr()
    st.session_state.bip_historie.append({"Jahr": st.session_state.jahr, "BIP": berechne_bip()})
    st.session_state.jahr += 1

    # Neue Runde vorbereiten
    st.session_state.aktuelle_szenarien = ziehe_3_szenarien()
    st.session_state.entscheidungen_getroffen = [False] * len(st.session_state.aktuelle_szenarien)
    st.session_state.ereignis_feedbacks = [""] * len(st.session_state.aktuelle_szenarien)
    st.rerun()


def anwenden(option, index):
    for k, v in option["ent"].items(): st.session_state.ent[k] += v
    for k, v in option["ver"].items(): st.session_state.ver[k] += v
    for k, v in option["vert"].items(): st.session_state.vert[k] += v

    st.session_state.ereignis_feedbacks[index] = option["msg"]
    st.session_state.entscheidungen_getroffen[index] = True


# --- 3. INITIALISIERUNG DES STATE ---
if "setup" not in st.session_state:
    st.session_state.setup = False
    st.session_state.jahr = 1
    st.session_state.bip_historie = []

    st.session_state.uebrige_szenarien = alle_szenarien.copy()
    random.shuffle(st.session_state.uebrige_szenarien)

    # Wird erst nach Setup gefüllt
    st.session_state.aktuelle_szenarien = []
    st.session_state.entscheidungen_getroffen = []
    st.session_state.ereignis_feedbacks = []

    st.session_state.ent = {"landwirtschaft": 0, "industrie": 0, "dienstleistung": 0}
    st.session_state.ver = {"konsum": 0, "investitionen": 0, "staat": 0, "export": 0}
    st.session_state.vert = {"loehne": 0, "gewinne": 0}

    st.session_state.alt_ent, st.session_state.alt_ver, st.session_state.alt_vert = {}, {}, {}
    st.session_state.alt_bip = 0

# --- 4. UI: GRÜNDUNGSPHASE (LINKE SEITE) ---
with st.sidebar:
    st.header("🛠️ 1. Land gründen")
    if not st.session_state.setup:
        st.session_state.land_name = st.text_input("Landesname:", "Fantasia")
        st.session_state.waehrung = st.text_input("Währung:", "Taler")

        st.write("---")
        st.write("**Arbeitskräfte verteilen (Start-Wirtschaft):**")
        anteil_agrar = st.slider("Landwirtschaft (%)", 0, 100, 15)
        anteil_industrie = st.slider("Industrie (%)", 0, 100, 45)
        anteil_dienst = st.slider("Dienstleistung (%)", 0, 100, 40)

        summe = anteil_agrar + anteil_industrie + anteil_dienst

        # Prüfung auf exakt 100%
        if summe == 100:
            st.success(f"Summe: {summe}% - Perfekt!")
            if st.button("Simulation starten", type="primary"):
                st.session_state.setup = True

                st.session_state.ent = {"landwirtschaft": anteil_agrar * 100, "industrie": anteil_industrie * 100,
                                        "dienstleistung": anteil_dienst * 100}
                bip = berechne_bip()
                st.session_state.ver = {"konsum": int(bip * 0.5), "investitionen": int(bip * 0.2),
                                        "staat": int(bip * 0.2), "export": int(bip * 0.1)}
                st.session_state.vert = {"loehne": int(bip * 0.65), "gewinne": int(bip * 0.35)}

                sichere_vorjahr()
                # Ziehe die ersten 3 Szenarien für Jahr 1
                st.session_state.aktuelle_szenarien = ziehe_3_szenarien()
                st.session_state.entscheidungen_getroffen = [False] * len(st.session_state.aktuelle_szenarien)
                st.session_state.ereignis_feedbacks = [""] * len(st.session_state.aktuelle_szenarien)
                st.rerun()
        else:
            st.error(f"Achtung: Die Summe muss exakt 100% ergeben! (Aktuell: {summe}%)")

    else:
        st.success(f"Regierung von {st.session_state.land_name}")
        st.metric("Aktuelles Jahr", st.session_state.jahr)
        if st.button("Neustart / Reset"):
            st.session_state.clear()
            st.rerun()

# --- 5. UI: HAUPTBEREICH (SIMULATION) ---
if st.session_state.setup:
    st.title(f"🌍 {st.session_state.land_name} - Jahr {st.session_state.jahr}")

    st.subheader("⚖️ Entscheidungen in diesem Jahr")
    st.markdown("Du musst als Minister auf folgende 3 Ereignisse reagieren:")

    # Schleife durch die bis zu 3 gezogenen Szenarien
    if len(st.session_state.aktuelle_szenarien) > 0:
        for i, sz in enumerate(st.session_state.aktuelle_szenarien):
            st.markdown(f"### Ereignis {i + 1}: {sz['titel']}")
            st.write(sz["text"])

            # Wenn noch keine Entscheidung für dieses Ereignis getroffen wurde: Buttons zeigen
            if not st.session_state.entscheidungen_getroffen[i]:
                c1, c2 = st.columns(2)
                with c1:
                    # Der Key muss einzigartig sein, sonst meckert Streamlit
                    if st.button(sz["option_a"]["text"], key=f"btn_a_{st.session_state.jahr}_{sz['id']}",
                                 use_container_width=True):
                        anwenden(sz["option_a"], i)
                        st.rerun()
                with c2:
                    if st.button(sz["option_b"]["text"], key=f"btn_b_{st.session_state.jahr}_{sz['id']}",
                                 use_container_width=True):
                        anwenden(sz["option_b"], i)
                        st.rerun()
            else:
                # Feedback anzeigen, nachdem gedrückt wurde
                st.info(f"✅ **Auswirkung:** {st.session_state.ereignis_feedbacks[i]}")

            st.divider()

        # Prüfen, ob für ALLE Szenarien dieses Jahres eine Entscheidung getroffen wurde
        if all(st.session_state.entscheidungen_getroffen):
            st.success("Du hast alle Entscheidungen für dieses Jahr getroffen. Schau dir unten dein Dashboard an!")
            if st.button("➡️ Jahr abschließen & Nächstes Jahr starten", type="primary"):
                naechstes_jahr()
    else:
        st.success("🎉 Glückwunsch! Du hast alle Szenarien der Simulation durchgespielt!")

    st.markdown("---")

    # --- DASHBOARD & DIAGRAMME ---
    akt_bip = berechne_bip()
    st.header(f"📊 Wirtschafts-Dashboard (BIP: {akt_bip} {st.session_state.waehrung})")

    if len(st.session_state.bip_historie) > 0:
        df = pd.DataFrame(st.session_state.bip_historie).set_index("Jahr")
        df.loc[st.session_state.jahr] = akt_bip
        st.line_chart(df, y="BIP", height=200)

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
    st.info("Bitte gründe dein Land in der Seitenleiste (links). Wähle genau 100% aus, um zu starten.")