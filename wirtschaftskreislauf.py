import streamlit as st
import json
import requests
from streamlit_lottie import st_lottie

# --- Seiten-Setup ---
st.set_page_config(page_title="Vom Rätsel zum Kreislauf!", layout="wide")
st.title("🧩 Baue den Wirtschaftskreislauf!")
st.markdown("Verbinde die Akteure richtig. Wenn du es schaffst, erwacht die Wirtschaft zum Leben!")


# --- Funktion zum Laden der Animation ---
# Wir nutzen eine Beispiel-Animation, die Geldströme zeigt.
# Du kannst hier die URL deiner Lieblings-Animation von LottieFiles einsetzen.
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


# Beispiel-Lottie-Animation: "Economic Cycle" (Geldströme)
# Du kannst diese URL durch eine beliebige Lottie-JSON-URL ersetzen.
lottie_economy = load_lottieurl("https://lottie.host/a6e9a78a-c47d-419b-a083-d5d288d75242/f41E3w8w1T.json")

# --- Phase 1: Das Puzzle (Logik wie gehabt) ---
st.subheader("Schritt 1: Wer gibt wem was?")
st.markdown("Wähle die richtige Richtung für jeden Strom aus.")

# Wir vereinfachen das Quiz etwas, um den Fokus auf die Animation zu legen.
col1, col2 = st.columns(2)

with col1:
    st.info("💵 GELDSTRÖME (z.B. Lohn)")
    lohn_von = st.selectbox("Geld fließt von...", ["Bitte wählen", "Haushalte", "Unternehmen"], key="l_von")
    lohn_zu = st.selectbox("...zu", ["Bitte wählen", "Haushalte", "Unternehmen"], key="l_zu")

with col2:
    st.info("📦 GÜTERSTRÖME (z.B. Arbeit)")
    arbeit_von = st.selectbox("Arbeit fließt von...", ["Bitte wählen", "Haushalte", "Unternehmen"], key="a_von")
    arbeit_zu = st.selectbox("...zu", ["Bitte wählen", "Haushalte", "Unternehmen"], key="a_zu")

# --- Phase 2: Logik-Prüfung ---
lohn_richtig = (lohn_von == "Unternehmen" and lohn_zu == "Haushalte")
arbeit_richtig = (arbeit_von == "Haushalte" and arbeit_zu == "Unternehmen")

alle_richtig = lohn_richtig and arbeit_richtig
etwas_ausgewaehlt = (lohn_von != "Bitte wählen" or arbeit_von != "Bitte wählen")

st.divider()

if alle_richtig:
    # --- Phase 3: Die Lottie-Belohnung (Der lebendige Kreislauf!) ---
    st.success("🎉 Hervorragend! Du hast den Kreislauf geschlossen. Jetzt schau, wie das Geld fließt!")

    # Animation anzeigen!
    if lottie_economy:
        # st_lottie zeigt die Animation an.
        # height steuert die Größe.
        # reverse=False heißt, die Animation läuft vorwärts.
        # loop=True heißt, sie läuft unendlich.
        # speed=1 heißt, sie läuft in normaler Geschwindigkeit.
        st_lottie(lottie_economy, height=600, key="economy_sim", loop=True)
        st.markdown("Siehst du die Münzen fließen? Siehst du die Pakete reisen? **Genau so hast du es gebaut!**")
    else:
        st.error("Upps! Die Animation konnte nicht geladen werden.")

elif etwas_ausgewaehlt:
    st.warning("Noch ist der Kreislauf nicht geschlossen. Überlege nochmal: Wer bekommt Lohn für seine Arbeit?")