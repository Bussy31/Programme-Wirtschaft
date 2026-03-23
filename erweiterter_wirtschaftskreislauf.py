import streamlit as st
import streamlit.components.v1 as components

# --- Seiten-Setup ---
st.set_page_config(page_title="Die Offene Volkswirtschaft", layout="wide")

st.title("🌍 Die Offene Volkswirtschaft!")
st.markdown(
    "Das absolute Profi-Level: Jetzt ist unsere Wirtschaft globalisiert. Wir handeln mit dem **Ausland**. Löse das finale Rätsel, um den globalen Geldkreislauf zu starten!")
st.divider()

# --- Phase 1: Das Finale Puzzle ---
st.subheader("Level 3: Die globalen Ströme")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("🚢 **Export-Erlöse (Geld)**")
    export_von = st.selectbox("Geld für unsere Exporte fließt vom Ausland an...",
                              ["Bitte wählen", "Unternehmen", "Haushalte", "Staat"], key="ex")

with col2:
    st.markdown("🌍 **Import-Ausgaben (Geld)**")
    import_von = st.selectbox("Geld für Importwaren fließt ans Ausland von...",
                              ["Bitte wählen", "Unternehmen", "Haushalte", "Banken"], key="im")

with col3:
    st.markdown("🪙 **Steuern**")
    steuer_zu = st.selectbox("Steuern von Haushalten & Unternehmen fließen an...",
                             ["Bitte wählen", "Staat", "Banken", "Ausland"], key="st")

with col4:
    st.markdown("🐖 **Ersparnisse**")
    sparen_zu = st.selectbox("Ersparnisse der Haushalte fließen an...", ["Bitte wählen", "Staat", "Banken", "Ausland"],
                             key="sp")

# Logik-Prüfung für die finale Stufe
alle_richtig = (
        export_von == "Unternehmen" and
        import_von == "Unternehmen" and
        steuer_zu == "Staat" and
        sparen_zu == "Banken"
)

st.divider()

if alle_richtig:
    st.success("🎉 Weltklasse! Du hast das komplette 5-Sektoren-Modell gelöst. Die Weltwirtschaft läuft!")

    # --- Konjunktur-Regler ---
    st.subheader("📈 Steuere die globale Konjunktur!")

    konjunktur = st.slider("Weltwirtschaftslage (1 = Globale Krise, 10 = Weltweiter Boom)", min_value=1, max_value=10,
                           value=5)

    if konjunktur <= 3:
        st.error("📉 **Weltwirtschaftskrise:** Der Welthandel bricht ein, Exporte und Importe stocken.")
    elif konjunktur >= 8:
        st.success("🚀 **Globaler Boom:** Die Häfen sind voll, der internationale Handel floriert!")
    else:
        st.info("⚖️ **Normalphase:** Stabiler internationaler Handel.")

    # Mathematik für die Geschwindigkeit
    dauer = 7.0 - (konjunktur * 0.5)
    verzogerung = dauer / 2

    # --- Phase 3: Die gigantische 5-Akteur-Animation ---
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        .kreislauf-box {
            position: relative; width: 100%; max-width: 850px; height: 450px;
            background-color: #f8f9fa; border-radius: 15px; margin: 0 auto;
            border: 2px solid #e9ecef; font-family: sans-serif; overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .akteur {
            position: absolute; width: 130px; height: 90px; background: white;
            border: 3px solid #333; border-radius: 10px; text-align: center;
            line-height: 90px; font-weight: bold; font-size: 16px; z-index: 10;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        /* Layout: Ausland links, Unternehmen mittig-links, Haushalte rechts, Staat oben, Banken unten */
        .ausland { left: 20px; top: 180px; border-color: #9467bd; color: #9467bd; }
        .unternehmen { left: 280px; top: 180px; border-color: #2ca02c; color: #2ca02c; }
        .haushalte { left: 640px; top: 180px; border-color: #1f77b4; color: #1f77b4; }
        .staat { left: 460px; top: 20px; border-color: #d62728; color: #d62728; }
        .banken { left: 460px; top: 340px; border-color: #ff7f0e; color: #ff7f0e; }

        .objekt {
            position: absolute; font-size: 24px; z-index: 5; background: #f8f9fa; border-radius: 50%;
        }

        /* --- Animations-Zuordnungen --- */
        .export_geld { animation: l_au ANIM_DURATIONs linear infinite; }
        .import_geld { animation: l_ua ANIM_DURATIONs linear infinite; }
        .lohn { animation: l_uh ANIM_DURATIONs linear infinite; }
        .konsum { animation: l_hu ANIM_DURATIONs linear infinite; }
        .steuer_h { animation: l_hs ANIM_DURATIONs linear infinite; }
        .steuer_u { animation: l_us ANIM_DURATIONs linear infinite; }
        .sparen { animation: l_hb ANIM_DURATIONs linear infinite; }
        .investition { animation: l_bu ANIM_DURATIONs linear infinite; }

        /* --- Die Keyframes (Routen der Emojis) --- */
        /* Ausland <-> Unternehmen */
        @keyframes l_au { 0%{left: 160px; top: 195px; opacity:0;} 10%{opacity:1;} 90%{opacity:1;} 100%{left: 250px; top: 195px; opacity:0;} }
        @keyframes l_ua { 0%{left: 250px; top: 225px; opacity:0;} 10%{opacity:1;} 90%{opacity:1;} 100%{left: 160px; top: 225px; opacity:0;} }

        /* Unternehmen <-> Haushalte */
        @keyframes l_uh { 0%{left: 420px; top: 195px; opacity:0;} 10%{opacity:1;} 90%{opacity:1;} 100%{left: 610px; top: 195px; opacity:0;} }
        @keyframes l_hu { 0%{left: 610px; top: 225px; opacity:0;} 10%{opacity:1;} 90%{opacity:1;} 100%{left: 420px; top: 225px; opacity:0;} }

        /* Staat & Banken */
        @keyframes l_us { 0%{left: 345px; top: 165px; opacity:0;} 10%{opacity:1;} 90%{opacity:1;} 100%{left: 450px; top: 95px; opacity:0;} }
        @keyframes l_hs { 0%{left: 685px; top: 165px; opacity:0;} 10%{opacity:1;} 90%{opacity:1;} 100%{left: 570px; top: 95px; opacity:0;} }
        @keyframes l_hb { 0%{left: 685px; top: 255px; opacity:0;} 10%{opacity:1;} 90%{opacity:1;} 100%{left: 570px; top: 325px; opacity:0;} }
        @keyframes l_bu { 0%{left: 450px; top: 325px; opacity:0;} 10%{opacity:1;} 90%{opacity:1;} 100%{left: 345px; top: 255px; opacity:0;} }

        /* Kleine Text-Labels für die Ströme */
        .label { position: absolute; font-size: 12px; font-weight: bold; color: #666; z-index: 1;}
        .lbl-exp { left: 175px; top: 180px; color: #9467bd;}
        .lbl-imp { left: 175px; top: 245px; color: #9467bd;}
        .lbl-lohn { left: 490px; top: 180px; }
        .lbl-konsum { left: 490px; top: 245px; }
        .lbl-st-h { left: 630px; top: 110px; color: #d62728; }
        .lbl-st-u { left: 380px; top: 110px; color: #d62728; }
        .lbl-spar { left: 630px; top: 310px; color: #ff7f0e; }
        .lbl-inv { left: 380px; top: 310px; color: #ff7f0e; }
    </style>
    </head>
    <body>
        <div class="kreislauf-box">

            <svg style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:0;">
                <line x1="160" y1="210" x2="270" y2="210" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
                <line x1="160" y1="240" x2="270" y2="240" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
                <line x1="420" y1="210" x2="630" y2="210" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
                <line x1="420" y1="240" x2="630" y2="240" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
                <line x1="705" y1="180" x2="550" y2="110" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
                <line x1="345" y1="180" x2="500" y2="110" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
                <line x1="705" y1="270" x2="550" y2="340" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
                <line x1="500" y1="340" x2="345" y2="270" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            </svg>

            <div class="akteur ausland">Ausland</div>
            <div class="akteur unternehmen">Unternehmen</div>
            <div class="akteur haushalte">Haushalte</div>
            <div class="akteur staat">Staat</div>
            <div class="akteur banken">Banken</div>

            <div class="label lbl-exp">Exporte ➔</div>
            <div class="label lbl-imp">⬅ Importe</div>
            <div class="label lbl-lohn">Löhne ➔</div>
            <div class="label lbl-konsum">⬅ Konsum</div>
            <div class="label lbl-st-h">↖ Steuern</div>
            <div class="label lbl-st-u">Steuern ↗</div>
            <div class="label lbl-spar">↙ Sparen</div>
            <div class="label lbl-inv">Kredite ↖</div>

            <div class="objekt export_geld">💶</div> <div class="objekt export_geld" style="animation-delay: ANIM_DELAYs;">💶</div>
            <div class="objekt import_geld">💸</div> <div class="objekt import_geld" style="animation-delay: ANIM_DELAYs;">💸</div>

            <div class="objekt lohn">💶</div> <div class="objekt lohn" style="animation-delay: ANIM_DELAYs;">💶</div>
            <div class="objekt konsum">🛍️</div> <div class="objekt konsum" style="animation-delay: ANIM_DELAYs;">🛍️</div>

            <div class="objekt steuer_h">🪙</div> <div class="objekt steuer_h" style="animation-delay: ANIM_DELAYs;">🪙</div>
            <div class="objekt steuer_u">🪙</div> <div class="objekt steuer_u" style="animation-delay: ANIM_DELAYs;">🪙</div>

            <div class="objekt sparen">🐖</div> <div class="objekt sparen" style="animation-delay: ANIM_DELAYs;">🐖</div>
            <div class="objekt investition">🏗️</div> <div class="objekt investition" style="animation-delay: ANIM_DELAYs;">🏗️</div>

        </div>
    </body>
    </html>
    """

    html_animation = html_template.replace("ANIM_DURATION", str(dauer)).replace("ANIM_DELAY", str(verzogerung))

    components.html(html_animation, height=500)

elif export_von != "Bitte wählen" or import_von != "Bitte wählen":
    st.info("💡 Fast! Denk daran: Wer in unserem Land produziert die Güter, die ans Ausland verkauft werden (Export)?")