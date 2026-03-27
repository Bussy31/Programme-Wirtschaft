import streamlit as st
import streamlit.components.v1 as components

# --- Seiten-Setup ---
st.set_page_config(page_title="Wirtschaftskreislauf", layout="wide")

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

st.title("Der einfache Wirtschaftskreislauf")
st.markdown(
    "Damit die Wirtschaft funktioniert, müssen **Geld** und **Güter/Dienstleistungen** in einem ewigen Tauschgeschäft fließen. Kannst du die Ströme richtig verbinden?")
st.divider()

# --- Phase 1: Das horizontale Puzzle ---
st.subheader("Wer liefert was an wen?")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("💶 **Geld (Lohn/Gehalt)**")
    lohn_von = st.selectbox("Fließt von...", ["Bitte wählen", "Unternehmen", "Haushalte"], key="lv")

with col2:
    st.markdown("➔ **Geld-Empfänger**")
    lohn_zu = st.selectbox("...zu", ["Bitte wählen", "Unternehmen", "Haushalte"], key="lz")

with col3:
    st.markdown("📦 **Arbeitskraft (Güter)**")
    arbeit_von = st.selectbox("Fließt von...", ["Bitte wählen", "Unternehmen", "Haushalte"], key="av")

with col4:
    st.markdown("➔ **Arbeits-Empfänger**")
    arbeit_zu = st.selectbox("...zu", ["Bitte wählen", "Unternehmen", "Haushalte"], key="az")

lohn_richtig = (lohn_von == "Unternehmen" and lohn_zu == "Haushalte")
arbeit_richtig = (arbeit_von == "Haushalte" and arbeit_zu == "Unternehmen")

st.divider()

if lohn_richtig and arbeit_richtig:
    st.success("🎉 Perfekt! Der Kreislauf ist vollständig geschlossen.")

# --- NEU: Konjunktur-Regler ---
st.subheader("📈 Steuere die Konjunktur!")
st.markdown("Was passiert in einer Wirtschaftskrise? Und was in einem Boom?")

# Der Slider geht von 1 (Krise) bis 10 (Boom)
konjunktur = st.slider("Wirtschaftslage (1 = Schwere Rezession, 10 = Starker Boom)", min_value=1, max_value=10,
                       value=5)

# Dynamische Anzeige der aktuellen Phase
if konjunktur <= 3:
    st.error("📉 **Rezession:** Die Wirtschaft lahmt. Die Arbeitslosigkeit steigt, es fließt weniger Geld.")
elif konjunktur >= 8:
    st.success("🚀 **Hochkonjunktur (Boom):** Die Wirtschaft brummt! Vollbeschäftigung und hoher Konsum.")
else:
    st.info("⚖️ **Normalphase:** Die Wirtschaft wächst in einem normalen, gesunden Tempo.")

# --- Mathe-Magie für die Animationsgeschwindigkeit ---
# Bei Regler=1: 6 Sekunden (langsam) | Bei Regler=5: 4 Sekunden (normal) | Bei Regler=10: 1.5 Sekunden (schnell)
dauer = 6.5 - (konjunktur * 0.5)
verzogerung = dauer / 2  # Damit das zweite Emoji immer genau auf halber Strecke startet

# --- Phase 3: Die HTML/CSS Animation ---
# Wir benutzen Platzhalter (ANIM_DURATION und ANIM_DELAY), die wir gleich per Python ersetzen
html_template = """
<!DOCTYPE html>
<html>
<head>
<style>
    .kreislauf-box {
        position: relative; width: 100%; max-width: 650px; height: 300px;
        background-color: #f8f9fa; border-radius: 15px; margin: 0 auto;
        border: 2px solid #e9ecef; font-family: sans-serif; overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .akteur {
        position: absolute; width: 130px; height: 90px; background: white;
        border: 3px solid #333; border-radius: 10px; text-align: center;
        line-height: 90px; font-weight: bold; font-size: 16px; top: 105px; z-index: 10;
    }
    .unternehmen { left: 30px; border-color: #2ca02c; color: #2ca02c;}
    .haushalte { right: 30px; border-color: #1f77b4; color: #1f77b4;}

    .track {
        position: absolute; height: 3px; background-color: #adb5bd;
        width: 360px; left: 160px; z-index: 1;
    }
    .track-top { top: 125px; }
    .track-bottom { top: 175px; }

    .track-top::after {
        content: ''; position: absolute; right: -2px; top: -6px;
        border-top: 7px solid transparent; border-bottom: 7px solid transparent; border-left: 12px solid #adb5bd;
    }
    .track-bottom::before {
        content: ''; position: absolute; left: -2px; top: -6px;
        border-top: 7px solid transparent; border-bottom: 7px solid transparent; border-right: 12px solid #adb5bd;
    }

    .objekt {
        position: absolute; font-size: 26px; z-index: 5; background: #f8f9fa; border-radius: 50%; opacity: 0;
    }

    /* HIER WERDEN DIE VARIABLEN EINGESETZT */
    .geld { top: 110px; animation: moveRight ANIM_DURATIONs linear infinite; }
    .gueter { top: 160px; animation: moveLeft ANIM_DURATIONs linear infinite; }

    @keyframes moveRight {
        0% { left: 160px; opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { left: 500px; opacity: 0; }
    }

    @keyframes moveLeft {
        0% { left: 500px; opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { left: 160px; opacity: 0; }
    }

    .label { position: absolute; width: 100%; text-align: center; font-size: 14px; font-weight: bold;}
    .label-top { top: 100px; color: #2ca02c;}
    .label-bottom { top: 195px; color: #1f77b4;}
</style>
</head>
<body>
    <div class="kreislauf-box">
        <div class="akteur unternehmen">Unternehmen</div>
        <div class="akteur haushalte">Haushalte</div>

        <div class="label label-top">Löhne & Gehälter</div>
        <div class="track track-top"></div>
        <div class="objekt geld">💶</div>
        <div class="objekt geld" style="animation-delay: ANIM_DELAYs;">💶</div>

        <div class="track track-bottom"></div>
        <div class="objekt gueter">👷</div>
        <div class="objekt gueter" style="animation-delay: ANIM_DELAYs;">👷</div>
        <div class="label label-bottom">Arbeitskraft</div>
    </div>
</body>
</html>
"""

# Python ersetzt unsere Platzhalter im Text mit den echten, berechneten Zahlen
html_animation = html_template.replace("ANIM_DURATION", str(dauer)).replace("ANIM_DELAY", str(verzogerung))

components.html(html_animation, height=350)

