import streamlit as st
import streamlit.components.v1 as components

# --- Seiten-Setup ---
st.set_page_config(page_title="Wirtschaftskreislauf", layout="wide")

st.title("🔄 Baue den Wirtschaftskreislauf!")
st.markdown(
    "Damit die Wirtschaft funktioniert, müssen **Geld** und **Güter/Dienstleistungen** in einem ewigen Tauschgeschäft fließen. Kannst du die Ströme richtig verbinden?")
st.divider()

# --- Phase 1: Das horizontale Puzzle ---
st.subheader("Wer liefert was an wen?")

# Wir nutzen 4 Spalten für ein sauberes, horizontales Layout
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

# --- Phase 2: Die Logik-Prüfung ---
# Beide Bedingungen müssen jetzt erfüllt sein!
lohn_richtig = (lohn_von == "Unternehmen" and lohn_zu == "Haushalte")
arbeit_richtig = (arbeit_von == "Haushalte" and arbeit_zu == "Unternehmen")

st.divider()

if lohn_richtig and arbeit_richtig:
    st.success("🎉 Perfekt! Der Kreislauf ist vollständig geschlossen. Schau, wie alles in Bewegung gerät!")

    # --- Phase 3: Die erweiterte HTML/CSS Animation ---
    html_animation = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        /* Das Spielfeld */
        .kreislauf-box {
            position: relative;
            width: 100%;
            max-width: 650px;
            height: 300px;
            background-color: #f8f9fa;
            border-radius: 15px;
            margin: 0 auto;
            border: 2px solid #e9ecef;
            font-family: sans-serif;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        /* Die zwei Hauptakteure */
        .akteur {
            position: absolute;
            width: 130px;
            height: 90px;
            background: white;
            border: 3px solid #333;
            border-radius: 10px;
            text-align: center;
            line-height: 90px;
            font-weight: bold;
            font-size: 16px;
            top: 105px;
            z-index: 10;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .unternehmen { left: 30px; border-color: #2ca02c; color: #2ca02c;}
        .haushalte { right: 30px; border-color: #1f77b4; color: #1f77b4;}

        /* --- Die Verbindungslinien (Pfeile) --- */
        .track {
            position: absolute;
            height: 3px;
            background-color: #adb5bd;
            width: 360px; /* Verbindet die Akteure passgenau */
            left: 160px;
            z-index: 1;
        }

        .track-top { top: 125px; }
        .track-bottom { top: 175px; }

        /* Pfeilspitze nach rechts (oben) */
        .track-top::after {
            content: '';
            position: absolute;
            right: -2px;
            top: -6px;
            border-top: 7px solid transparent;
            border-bottom: 7px solid transparent;
            border-left: 12px solid #adb5bd;
        }

        /* Pfeilspitze nach links (unten) */
        .track-bottom::before {
            content: '';
            position: absolute;
            left: -2px;
            top: -6px;
            border-top: 7px solid transparent;
            border-bottom: 7px solid transparent;
            border-right: 12px solid #adb5bd;
        }

        /* --- Die fliegenden Objekte --- */
        .objekt {
            position: absolute;
            font-size: 26px;
            z-index: 5;
            background: #f8f9fa; /* Verdeckt die Linie hinter dem Emoji leicht */
            border-radius: 50%;
        }

        .geld { top: 110px; animation: moveRight 3s linear infinite; }
        .gueter { top: 160px; animation: moveLeft 3s linear infinite; }

        /* Die Animations-Routen (angepasst an die Schienen) */
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

        /* Beschriftung der Linien */
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
            <div class="objekt geld" style="animation-delay: 1.5s;">💶</div>

            <div class="track track-bottom"></div>
            <div class="objekt gueter">👷</div>
            <div class="objekt gueter" style="animation-delay: 1.5s;">👷</div>
            <div class="label label-bottom">Arbeitskraft</div>

        </div>
    </body>
    </html>
    """

    components.html(html_animation, height=350)

elif lohn_von != "Bitte wählen" or arbeit_von != "Bitte wählen":
    st.info(
        "💡 Fast! Denk daran: Wer gibt seine Arbeitskraft her, und wer bezahlt am Ende den Lohn dafür? Verbinde alle vier Felder richtig.")