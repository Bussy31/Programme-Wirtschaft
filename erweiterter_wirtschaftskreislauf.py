import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Wirtschaftskreislauf Pro", layout="wide")

st.title("🌐 Der offene Wirtschaftskreislauf")
st.markdown("Setze die fehlenden Begriffe in die richtigen Felder ein, um den Kreislauf zu starten!")
st.divider()

# --- Die Auswahlmöglichkeiten ---
optionen_staat = ["Bitte wählen...", "staatliche Ersparnisse", "staatliche Kreditaufnahme"]
optionen_stroeme = [
    "Bitte wählen...", "Steuern, Sozialabgaben", "Transferleistungen",
    "staatlicher Konsum", "Steuern abzüglich Subventionen",
    "Spareinlagen", "Investitionen",
    "Einkommen", "Konsumausgaben",
    "Zahlungen für Exporte", "Zahlungen für Importe",
    "Transfer der Haushalte", "Transfer des Auslands"
]

# --- Phase 1: Die roten Boxen beim Staat ---
st.subheader("1. Die Lage des Staates")
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.info("🏛️ **Staat**")
    box_links = st.selectbox("Rotes Feld links (Wenn der Staat Geld übrig hat):", optionen_staat, key="b_l")
    box_rechts = st.selectbox("Rotes Feld rechts (Wenn der Staat Schulden macht):", optionen_staat, key="b_r")

st.divider()

# --- Phase 2: Die Geldströme (Pfeile) ---
st.subheader("2. Die Geldströme verbinden")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Haushalte ↔ Staat**")
    h_zu_s = st.selectbox("Fließt von Haushalten an Staat:", optionen_stroeme, key="hs")
    s_zu_h = st.selectbox("Fließt von Staat an Haushalte:", optionen_stroeme, key="sh")

    st.markdown("**Haushalte ↔ Ausland**")
    h_zu_a = st.selectbox("Fließt von Haushalten ans Ausland:", optionen_stroeme, key="ha")
    a_zu_h = st.selectbox("Fließt vom Ausland an Haushalte:", optionen_stroeme, key="ah")

with col2:
    st.markdown("**Der Kernkreislauf**")
    u_zu_h = st.selectbox("Fließt von Unternehmen an Haushalte (für Arbeit):", optionen_stroeme, key="uh")
    h_zu_u = st.selectbox("Fließt von Haushalten an Unternehmen (für Güter):", optionen_stroeme, key="hu")

    st.markdown("**Über die Banken**")
    h_zu_b = st.selectbox("Fließt von Haushalten an Banken:", optionen_stroeme, key="hb")
    b_zu_u = st.selectbox("Fließt von Banken an Unternehmen:", optionen_stroeme, key="bu")

with col3:
    st.markdown("**Unternehmen ↔ Staat**")
    u_zu_s = st.selectbox("Fließt von Unternehmen an Staat:", optionen_stroeme, key="us")
    s_zu_u = st.selectbox("Fließt von Staat an Unternehmen:", optionen_stroeme, key="su")

    st.markdown("**Unternehmen ↔ Ausland**")
    a_zu_u = st.selectbox("Fließt vom Ausland an Unternehmen:", optionen_stroeme, key="au")
    u_zu_a = st.selectbox("Fließt von Unternehmen ans Ausland:", optionen_stroeme, key="ua")

# --- Logik-Check: Stimmt alles mit deinem Bild überein? ---
alles_richtig = (
        box_links == "staatliche Ersparnisse" and
        box_rechts == "staatliche Kreditaufnahme" and
        h_zu_s == "Steuern, Sozialabgaben" and
        s_zu_h == "Transferleistungen" and
        u_zu_h == "Einkommen" and
        h_zu_u == "Konsumausgaben" and
        h_zu_b == "Spareinlagen" and
        b_zu_u == "Investitionen" and
        u_zu_s == "Steuern abzüglich Subventionen" and
        s_zu_u == "staatlicher Konsum" and
        a_zu_u == "Zahlungen für Exporte" and
        u_zu_a == "Zahlungen für Importe" and
        h_zu_a == "Transfer der Haushalte" and
        a_zu_h == "Transfer des Auslands"
)

st.divider()

if alles_richtig:
    st.success("🎉 Perfekt! Das Diagramm ist vollständig. Die Simulation startet...")

    konjunktur = st.slider("Wirtschaftslage (Geschwindigkeit)", 1, 10, 5)
    dauer = 8.0 - (konjunktur * 0.6)

    # --- Das komplette HTML/CSS für die Animation ---
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        .canvas {{
            position: relative; width: 100%; max-width: 800px; height: 500px;
            background-color: #e3f2fd; border-radius: 10px; margin: 0 auto;
            border: 2px solid #90caf9; overflow: hidden; font-family: sans-serif;
        }}

        .akteur {{
            position: absolute; background: #1565c0; color: white; border-radius: 8px;
            text-align: center; font-weight: bold; z-index: 10; display: flex;
            align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}

        /* Positionierung wie in deinem Bild */
        .staat {{ width: 140px; height: 50px; left: 330px; top: 30px; background: #0d47a1; }}
        .haushalte {{ width: 140px; height: 80px; left: 40px; top: 210px; background: #64b5f6; color: black; }}
        .banken {{ width: 140px; height: 80px; left: 330px; top: 210px; background: #90caf9; color: black; }}
        .unternehmen {{ width: 140px; height: 80px; left: 620px; top: 210px; background: #90caf9; color: black; }}
        .ausland {{ width: 140px; height: 50px; left: 330px; top: 420px; background: #0d47a1; }}

        .rote-box {{
            position: absolute; background: #c62828; color: white; padding: 5px;
            border-radius: 5px; font-size: 11px; z-index: 10;
        }}
        .rb-links {{ left: 160px; top: 100px; }}
        .rb-rechts {{ left: 490px; top: 100px; }}

        /* Die fliegenden Emojis (Geldströme) */
        .emoji {{ position: absolute; font-size: 20px; z-index: 20; background: rgba(255,255,255,0.7); border-radius: 50%; padding: 2px; }}

        @keyframes move_h_s {{ 0%{{left:110px; top:210px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:330px; top:55px; opacity:0;}} }}
        @keyframes move_s_h {{ 0%{{left:330px; top:45px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:110px; top:200px; opacity:0;}} }}

        @keyframes move_u_s {{ 0%{{left:690px; top:210px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:470px; top:55px; opacity:0;}} }}
        @keyframes move_s_u {{ 0%{{left:470px; top:45px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:690px; top:200px; opacity:0;}} }}

        @keyframes move_h_b {{ 0%{{left:180px; top:240px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:330px; top:240px; opacity:0;}} }}
        @keyframes move_b_u {{ 0%{{left:470px; top:240px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:620px; top:240px; opacity:0;}} }}

        @keyframes move_u_h {{ 0%{{left:620px; top:270px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:180px; top:270px; opacity:0;}} }}
        @keyframes move_h_u {{ 0%{{left:180px; top:210px; opacity:0;}} 20%{{top: 150px; opacity:1;}} 80%{{top: 150px; opacity:1;}} 100%{{left:620px; top:210px; opacity:0;}} }} /* Bogen obenrum */

        @keyframes move_a_u {{ 0%{{left:470px; top:430px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:660px; top:290px; opacity:0;}} }}
        @keyframes move_u_a {{ 0%{{left:680px; top:290px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:470px; top:450px; opacity:0;}} }}

        @keyframes move_a_h {{ 0%{{left:330px; top:430px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:140px; top:290px; opacity:0;}} }}
        @keyframes move_h_a {{ 0%{{left:120px; top:290px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:330px; top:450px; opacity:0;}} }}

        .e_hs {{ animation: move_h_s {dauer}s linear infinite; }}
        .e_sh {{ animation: move_s_h {dauer}s linear infinite; }}
        .e_us {{ animation: move_u_s {dauer}s linear infinite; }}
        .e_su {{ animation: move_s_u {dauer}s linear infinite; }}
        .e_hb {{ animation: move_h_b {dauer}s linear infinite; }}
        .e_bu {{ animation: move_b_u {dauer}s linear infinite; }}
        .e_uh {{ animation: move_u_h {dauer}s linear infinite; }}
        .e_hu {{ animation: move_h_u {dauer}s linear infinite; }}
        .e_au {{ animation: move_a_u {dauer}s linear infinite; }}
        .e_ua {{ animation: move_u_a {dauer}s linear infinite; }}
        .e_ah {{ animation: move_a_h {dauer}s linear infinite; }}
        .e_ha {{ animation: move_h_a {dauer}s linear infinite; }}

    </style>
    </head>
    <body>
        <div class="canvas">
            <svg width="100%" height="100%" style="position:absolute; top:0; left:0; z-index:1;">
                <line x1="110" y1="210" x2="330" y2="55" stroke="#1565c0" stroke-width="2"/>
                <line x1="690" y1="210" x2="470" y2="55" stroke="#1565c0" stroke-width="2"/>
                <line x1="180" y1="250" x2="620" y2="250" stroke="#000" stroke-width="4"/>
                <path d="M 110 210 Q 400 50 690 210" fill="transparent" stroke="#ffca28" stroke-width="20" opacity="0.6"/>
                <line x1="470" y1="445" x2="670" y2="290" stroke="#1565c0" stroke-width="2"/>
                <line x1="330" y1="445" x2="130" y2="290" stroke="#1565c0" stroke-width="2"/>
            </svg>

            <div class="akteur staat">Staat</div>
            <div class="akteur haushalte">Haushalte</div>
            <div class="akteur banken">Banken</div>
            <div class="akteur unternehmen">Unternehmen</div>
            <div class="akteur ausland">Ausland</div>

            <div class="rote-box rb-links">staatliche Ersparnisse</div>
            <div class="rote-box rb-rechts">staatliche Kreditaufnahme</div>

            <div class="emoji e_hs">🪙</div>
            <div class="emoji e_sh">💶</div>
            <div class="emoji e_us">🪙</div>
            <div class="emoji e_su">💶</div>
            <div class="emoji e_hb">🐖</div>
            <div class="emoji e_bu">🏗️</div>
            <div class="emoji e_uh">💶</div>
            <div class="emoji e_hu">🛍️</div>
            <div class="emoji e_au">💶</div>
            <div class="emoji e_ua">💸</div>
            <div class="emoji e_ah">💶</div>
            <div class="emoji e_ha">💸</div>
        </div>
    </body>
    </html>
    """

    components.html(html_code, height=550)

else:
    st.info("💡 Wähle alle Begriffe korrekt aus. Sobald alles stimmt, startet die Simulation automatisch!")