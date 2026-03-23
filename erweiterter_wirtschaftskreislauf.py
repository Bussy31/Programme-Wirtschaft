import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Wirtschaftskreislauf Basis", layout="wide")

st.title("🔄 Der Wirtschaftskreislauf")
st.markdown("Beobachte das Modell und ordne die wichtigsten **Geld- und Güterströme** richtig zu!")
st.divider()

# --- Alle Antwortmöglichkeiten ---
optionen = [
    "Bitte wählen...",
    "Steuern, Sozialabgaben", "Transferleistungen",
    "staatlicher Konsum", "Steuern abzüglich Subventionen",
    "Spareinlagen", "Investitionen",
    "Konsumausgaben", "Konsumgüter",
    "Einkommen", "Arbeitskraft, Boden, Kapital"
]

# --- Eingabefelder (Fokus auf den Kern, klar getrennt nach Geld/Gütern) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Haushalte & Staat")
    h_s = st.selectbox("Haushalte ➔ Staat (Geldstrom):", optionen, key="hs")
    s_h = st.selectbox("Staat ➔ Haushalte (Geldstrom):", optionen, key="sh")

with col2:
    st.subheader("2. Der Kern (Haushalte & Unternehmen)")
    h_u_geld = st.selectbox("Haushalte ➔ Unternehmen (Geldstrom für Einkäufe):", optionen, key="hug")
    u_h_gut = st.selectbox("Unternehmen ➔ Haushalte (Güterstrom):", optionen, key="uhg")

    u_h_geld = st.selectbox("Unternehmen ➔ Haushalte (Geldstrom für Arbeit):", optionen, key="uhl")
    h_u_gut = st.selectbox("Haushalte ➔ Unternehmen (Faktoren: Arbeit/Kapital):", optionen, key="hua")

with col3:
    st.subheader("3. Banken, Unternehmen & Staat")
    h_b = st.selectbox("Haushalte ➔ Banken (Geldstrom):", optionen, key="hb")
    b_u = st.selectbox("Banken ➔ Unternehmen (Geldstrom):", optionen, key="bu")

    u_s = st.selectbox("Unternehmen ➔ Staat (Geldstrom):", optionen, key="us")
    s_u = st.selectbox("Staat ➔ Unternehmen (Geldstrom für Güter):", optionen, key="su")

# --- Logik-Check (Nur die Basis-Ströme) ---
alles_richtig = (
        h_s == "Steuern, Sozialabgaben" and
        s_h == "Transferleistungen" and
        h_u_geld == "Konsumausgaben" and
        u_h_gut == "Konsumgüter" and
        u_h_geld == "Einkommen" and
        h_u_gut == "Arbeitskraft, Boden, Kapital" and
        h_b == "Spareinlagen" and
        b_u == "Investitionen" and
        u_s == "Steuern abzüglich Subventionen" and
        s_u == "staatlicher Konsum"
)

st.divider()

# --- Feedback-Nachricht ---
if alles_richtig:
    st.success("🎉 Meisterhaft! Du hast die Kernströme der Wirtschaft perfekt verstanden und richtig zugeordnet.")
else:
    st.info(
        "💡 Die Wirtschaft läuft bereits! Aber einige Begriffe in den Feldern oben fehlen noch oder sind nicht ganz korrekt. Schau genau hin!")

# --- HTML & CSS für die dauerhafte Animation ---
dauer = 5.0  # Feste, angenehme Geschwindigkeit

html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    .canvas {{
        position: relative; width: 100%; max-width: 900px; height: 600px;
        background-color: #f8f9fa; border-radius: 10px; margin: 0 auto;
        border: 2px solid #ced4da; overflow: hidden; font-family: sans-serif;
    }}

    .akteur {{
        position: absolute; background: white; color: #333; border-radius: 8px;
        text-align: center; font-weight: bold; z-index: 10; display: flex;
        align-items: center; justify-content: center; 
        border: 3px solid #333; font-size: 16px;
    }}

    /* Das Kreuz-Layout */
    .staat {{ width: 140px; height: 60px; left: 380px; top: 30px; border-color: #d62728; }}
    .haushalte {{ width: 140px; height: 60px; left: 40px; top: 270px; border-color: #1f77b4; }}
    .banken {{ width: 140px; height: 60px; left: 380px; top: 270px; border-color: #ff7f0e; }}
    .unternehmen {{ width: 140px; height: 60px; left: 720px; top: 270px; border-color: #2ca02c; }}
    .ausland {{ width: 140px; height: 60px; left: 380px; top: 510px; border-color: #9467bd; }}

    /* Fliegende Emojis (Güter & Geld) */
    .emoji {{ position: absolute; font-size: 22px; z-index: 20; background: #f8f9fa; border-radius: 50%; }}

    /* --- Animations-Routen --- */
    @keyframes m_hs {{ 0%{{left:120px; top:270px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:380px; top:80px; opacity:0;}} }}
    @keyframes m_sh {{ 0%{{left:380px; top:50px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:100px; top:250px; opacity:0;}} }}

    @keyframes m_us {{ 0%{{left:760px; top:270px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:520px; top:80px; opacity:0;}} }}
    @keyframes m_su {{ 0%{{left:520px; top:50px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:780px; top:250px; opacity:0;}} }}

    @keyframes m_sb {{ 0%{{left:430px; top:90px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:430px; top:270px; opacity:0;}} }}
    @keyframes m_bs {{ 0%{{left:470px; top:270px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:470px; top:90px; opacity:0;}} }}

    @keyframes m_hb {{ 0%{{left:180px; top:290px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:380px; top:290px; opacity:0;}} }}
    @keyframes m_bu {{ 0%{{left:520px; top:290px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:720px; top:290px; opacity:0;}} }}

    @keyframes m_ha {{ 0%{{left:120px; top:330px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:380px; top:520px; opacity:0;}} }}
    @keyframes m_ah {{ 0%{{left:380px; top:550px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:100px; top:350px; opacity:0;}} }}

    @keyframes m_ua {{ 0%{{left:760px; top:330px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:520px; top:520px; opacity:0;}} }}
    @keyframes m_au {{ 0%{{left:520px; top:550px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:780px; top:350px; opacity:0;}} }}

    @keyframes m_hu_geld {{ 0%{{left:110px; top:270px; opacity:0;}} 20%{{top:140px; opacity:1;}} 80%{{top:140px; opacity:1;}} 100%{{left:790px; top:270px; opacity:0;}} }}
    @keyframes m_uh_gut {{ 0%{{left:790px; top:270px; opacity:0;}} 20%{{top:170px; opacity:1;}} 80%{{top:170px; opacity:1;}} 100%{{left:110px; top:270px; opacity:0;}} }}
    @keyframes m_uh_geld {{ 0%{{left:790px; top:330px; opacity:0;}} 20%{{top:430px; opacity:1;}} 80%{{top:430px; opacity:1;}} 100%{{left:110px; top:330px; opacity:0;}} }}
    @keyframes m_hu_gut {{ 0%{{left:110px; top:330px; opacity:0;}} 20%{{top:460px; opacity:1;}} 80%{{top:460px; opacity:1;}} 100%{{left:790px; top:330px; opacity:0;}} }}

    /* CSS-Klassen Zuweisung */
    .e_hs {{ animation: m_hs {dauer}s linear infinite; }}
    .e_sh {{ animation: m_sh {dauer}s linear infinite; }}
    .e_us {{ animation: m_us {dauer}s linear infinite; }}
    .e_su {{ animation: m_su {dauer}s linear infinite; }}
    .e_sb {{ animation: m_sb {dauer}s linear infinite; }}
    .e_bs {{ animation: m_bs {dauer}s linear infinite; }}
    .e_hb {{ animation: m_hb {dauer}s linear infinite; }}
    .e_bu {{ animation: m_bu {dauer}s linear infinite; }}
    .e_ha {{ animation: m_ha {dauer}s linear infinite; }}
    .e_ah {{ animation: m_ah {dauer}s linear infinite; }}
    .e_ua {{ animation: m_ua {dauer}s linear infinite; }}
    .e_au {{ animation: m_au {dauer}s linear infinite; }}
    .e_hu_geld {{ animation: m_hu_geld {dauer}s linear infinite; }}
    .e_uh_gut {{ animation: m_uh_gut {dauer}s linear infinite; }}
    .e_uh_geld {{ animation: m_uh_geld {dauer}s linear infinite; }}
    .e_hu_gut {{ animation: m_hu_gut {dauer}s linear infinite; }}

</style>
</head>
<body>
    <div class="canvas">

        <svg width="100%" height="100%" style="position:absolute; top:0; left:0; z-index:1;">
            <line x1="130" y1="280" x2="390" y2="90" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="110" y1="260" x2="390" y2="60" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="770" y1="280" x2="530" y2="90" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="790" y1="260" x2="530" y2="60" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>

            <line x1="440" y1="90" x2="440" y2="270" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="480" y1="90" x2="480" y2="270" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>

            <line x1="180" y1="300" x2="380" y2="300" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="520" y1="300" x2="720" y2="300" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>

            <line x1="130" y1="340" x2="390" y2="530" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="110" y1="360" x2="390" y2="560" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="770" y1="340" x2="530" y2="530" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="790" y1="360" x2="530" y2="560" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>

            <path d="M 120 280 Q 450 120 780 280" fill="transparent" stroke="#ffca28" stroke-width="4" stroke-dasharray="5,5"/>
            <path d="M 120 280 Q 450 160 780 280" fill="transparent" stroke="#ffca28" stroke-width="4" stroke-dasharray="5,5"/>
            <path d="M 120 320 Q 450 440 780 320" fill="transparent" stroke="#64b5f6" stroke-width="4" stroke-dasharray="5,5"/>
            <path d="M 120 320 Q 450 480 780 320" fill="transparent" stroke="#64b5f6" stroke-width="4" stroke-dasharray="5,5"/>
        </svg>

        <div class="akteur staat">Staat</div>
        <div class="akteur haushalte">Haushalte</div>
        <div class="akteur banken">Banken</div>
        <div class="akteur unternehmen">Unternehmen</div>
        <div class="akteur ausland">Ausland</div>

        <div class="emoji e_hs" title="Steuern">🪙</div>
        <div class="emoji e_sh" title="Transfers">💶</div>
        <div class="emoji e_us" title="Steuern">🪙</div>
        <div class="emoji e_su" title="Subventionen">💶</div>
        <div class="emoji e_sb" title="Ersparnisse">🐖</div>
        <div class="emoji e_bs" title="Kreditaufnahme">🏦</div>
        <div class="emoji e_hb" title="Spareinlagen">🐖</div>
        <div class="emoji e_bu" title="Investitionen">🏗️</div>
        <div class="emoji e_ha" title="Transfer ins Ausland">💸</div>
        <div class="emoji e_ah" title="Transfer aus Ausland">💶</div>
        <div class="emoji e_ua" title="Zahlung für Importe">💸</div>
        <div class="emoji e_au" title="Zahlung für Exporte">💶</div>
        <div class="emoji e_hu_geld" title="Konsumausgaben">💶</div>
        <div class="emoji e_uh_gut" title="Konsumgüter">🛍️</div>
        <div class="emoji e_uh_geld" title="Einkommen">💶</div>
        <div class="emoji e_hu_gut" title="Arbeit/Boden/Kapital">🧑‍🔧</div>

    </div>
</body>
</html>
"""

# Die Animation wird immer gerendert
components.html(html_code, height=650)