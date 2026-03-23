import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Kreislauf Animation", layout="wide")
st.title("🧩 Baue den Wirtschaftskreislauf!")

# --- Phase 1: Das Puzzle (stark vereinfacht für den Test) ---
st.markdown("Verbinde die Akteure richtig, um den Kreislauf zu starten.")

col1, col2 = st.columns(2)
with col1:
    lohn_von = st.selectbox("Geld fließt von...", ["Bitte wählen", "Unternehmen", "Haushalte"])
    lohn_zu = st.selectbox("...zu", ["Bitte wählen", "Unternehmen", "Haushalte"])

# Logik-Check (Nur wenn Unternehmen -> Haushalte gewählt ist, geht es los)
if lohn_von == "Unternehmen" and lohn_zu == "Haushalte":
    st.success("🎉 Richtig! Das Geld fließt.")

    # --- Phase 2: Unsere selbstgebaute, fließende Animation ---
    # Wir schreiben ein kleines Stück HTML & CSS, das die Boxen und fliegenden Partikel zeichnet.

    html_animation = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        /* Das Spielfeld */
        .kreislauf-box {
            position: relative;
            width: 100%;
            max-width: 600px;
            height: 300px;
            background-color: #f8f9fa;
            border-radius: 15px;
            margin: 0 auto;
            border: 2px solid #e9ecef;
            font-family: sans-serif;
            overflow: hidden;
        }

        /* Die zwei Hauptakteure */
        .akteur {
            position: absolute;
            width: 120px;
            height: 80px;
            background: white;
            border: 3px solid #333;
            border-radius: 10px;
            text-align: center;
            line-height: 80px;
            font-weight: bold;
            top: 110px;
            z-index: 10;
        }
        .unternehmen { left: 40px; border-color: #2ca02c; }
        .haushalte { right: 40px; border-color: #1f77b4; }

        /* Fließendes Geld (oben) */
        .geld {
            position: absolute;
            font-size: 24px;
            top: 60px;
            left: 170px;
            animation: moveRight 2.5s linear infinite;
        }

        /* Fließende Güter (unten) */
        .gueter {
            position: absolute;
            font-size: 24px;
            bottom: 60px;
            right: 170px;
            animation: moveLeft 2.5s linear infinite;
        }

        /* Die Animations-Routen */
        @keyframes moveRight {
            0% { left: 160px; opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { left: calc(100% - 190px); opacity: 0; }
        }

        @keyframes moveLeft {
            0% { right: 160px; opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { right: calc(100% - 190px); opacity: 0; }
        }

        /* Beschriftung der Pfeile */
        .label { position: absolute; width: 100%; text-align: center; color: #666; font-size: 14px; }
        .label-top { top: 30px; }
        .label-bottom { bottom: 30px; }
    </style>
    </head>
    <body>
        <div class="kreislauf-box">
            <div class="label label-top">Einkommen / Löhne ➔</div>

            <div class="akteur unternehmen">Unternehmen</div>

            <div class="geld">💶</div>
            <div class="geld" style="animation-delay: 1.25s;">💶</div>

            <div class="akteur haushalte">Haushalte</div>

            <div class="gueter">📦</div>
            <div class="gueter" style="animation-delay: 1.25s;">📦</div>

            <div class="label label-bottom">⬅ Arbeitskraft</div>
        </div>
    </body>
    </html>
    """

    # Hier betten wir unser HTML in Streamlit ein
    components.html(html_animation, height=350)

else:
    st.info("Wer zahlt die Löhne? Wähle oben das Richtige aus.")