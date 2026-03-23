import streamlit as st
import streamlit.components.v1 as components

# --- Seiten-Setup ---
st.set_page_config(page_title="Die Offene Volkswirtschaft", layout="wide")

st.title("🌍 Die Offene Volkswirtschaft (Profi-Level)")
st.markdown(
    "Das absolute Meisterstück! Das Design nutzt die volle Breite, alle 16 Linien sind integriert und die Emojis fließen als echter Doppel-Strom. Löse alle 16 Kacheln, um die Kontrolle über die Weltkonjunktur zu erhalten.")
st.divider()

# --- Alle Antwortmöglichkeiten aus dem Diagramm ---
optionen = [
    "Bitte wählen...",
    "Steuern, Sozialabgaben", "Transferleistungen",
    "staatlicher Konsum", "Steuern abzüglich Subventionen",
    "Spareinlagen", "Investitionen",
    "Konsumausgaben", "Konsumgüter",
    "Einkommen", "Arbeitskraft, Boden, Kapital",
    "Transfer der Haushalte", "Transfer des Auslands",
    "Zahlungen für Exporte", "Zahlungen für Importe",
    "staatliche Ersparnisse", "staatliche Kreditaufnahme"
]

# --- Die Kacheln zum Ausfüllen (4 Spalten, volle Breite) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("🏛️ Mit dem Staat")
    h_s = st.selectbox("Haushalte ➔ Staat:", optionen, key="hs")
    s_h = st.selectbox("Staat ➔ Haushalte:", optionen, key="sh")
    u_s = st.selectbox("Unternehmen ➔ Staat:", optionen, key="us")
    s_u = st.selectbox("Staat ➔ Unternehmen:", optionen, key="su")

with col2:
    st.subheader("🛍️ Der Kern (H & U)")
    h_u_geld = st.selectbox("Haushalte ➔ Unternehmen (Geld):", optionen, key="hug")
    u_h_gut = st.selectbox("Unternehmen ➔ Haushalte (Güter):", optionen, key="uhg")
    u_h_geld = st.selectbox("Unternehmen ➔ Haushalte (Lohn):", optionen, key="uhl")
    h_u_gut = st.selectbox("Haushalte ➔ Unternehmen (Arbeit):", optionen, key="hua")

with col3:
    st.subheader("🏦 Über die Banken")
    h_b = st.selectbox("Haushalte ➔ Banken:", optionen, key="hb")
    b_u = st.selectbox("Banken ➔ Unternehmen:", optionen, key="bu")
    s_b = st.selectbox("Staat ➔ Banken:", optionen, key="sb")
    b_s = st.selectbox("Banken ➔ Staat:", optionen, key="bs")

with col4:
    st.subheader("🌍 Mit dem Ausland")
    a_u = st.selectbox("Ausland ➔ Unternehmen (Exportgeld):", optionen, key="au")
    u_a = st.selectbox("Unternehmen ➔ Ausland (Importgeld):", optionen, key="ua")
    h_a = st.selectbox("Haushalte ➔ Ausland:", optionen, key="ha")
    a_h = st.selectbox("Ausland ➔ Haushalte:", optionen, key="ah")

# --- Logik-Prüfung für die 16 Felder ---
alles_richtig = (
        h_s == "Steuern, Sozialabgaben" and s_h == "Transferleistungen" and
        u_s == "Steuern abzüglich Subventionen" and s_u == "staatlicher Konsum" and
        h_u_geld == "Konsumausgaben" and u_h_gut == "Konsumgüter" and
        u_h_geld == "Einkommen" and h_u_gut == "Arbeitskraft, Boden, Kapital" and
        h_b == "Spareinlagen" and b_u == "Investitionen" and
        s_b == "staatliche Ersparnisse" and b_s == "staatliche Kreditaufnahme" and
        a_u == "Zahlungen für Exporte" and u_a == "Zahlungen für Importe" and
        h_a == "Transfer der Haushalte" and a_h == "Transfer des Auslands"
)

st.divider()

# Standardwerte für die Animation
dauer = 6.0
konjunktur = 5

if alles_richtig:
    st.success("🎉 Weltklasse! Du hast das komplette 5-Sektoren-Modell gelöst. Du kontrollierst nun die Wirtschaft!")

    st.subheader("📈 Steuere die globale Konjunktur!")
    konjunktur = st.slider("Weltwirtschaftslage (1 = Krise, 10 = Boom)", min_value=1, max_value=10, value=5)

    if konjunktur <= 3:
        st.error("📉 **Krise:** Geldströme stocken, die Wirtschaft kühlt massiv ab.")
    elif konjunktur >= 8:
        st.success("🚀 **Boom:** Rekord-Umsätze! Alles fließt in rasantem Tempo.")
    else:
        st.info("⚖️ **Normalphase:** Stabiler, ausbalancierter Kreislauf.")

    dauer = 9.0 - (konjunktur * 0.7)  # Bei Boom (10) = 2s, bei Krise (1) = 8.3s

verzogerung = dauer / 2  # Für den perfekten Doppel-Emoji-Abstand

# --- Das coole HTML/CSS Template (volle Breite, alle 16 Linien) ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    .kreislauf-box {{
        position: relative; width: 100%; max-width: 1200px; height: 850px;
        background-color: #f8f9fa; border-radius: 15px; margin: 0 auto;
        border: 2px solid #e9ecef; font-family: sans-serif; overflow: hidden;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}

    .akteur {{
        position: absolute; width: 180px; height: 100px; background: white;
        border: 4px solid #333; border-radius: 12px; text-align: center;
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; font-size: 20px; z-index: 10;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }}

    /* Perfektes Kreuz-Layout für kreuzungsfreie Linien */
    .staat {{ left: 510px; top: 40px; border-color: #d62728; color: #d62728; height: 80px; }}
    .haushalte {{ left: 40px; top: 350px; border-color: #1f77b4; color: #1f77b4; height: 120px; }}
    .banken {{ left: 510px; top: 360px; border-color: #ff7f0e; color: #ff7f0e; }}
    .unternehmen {{ left: 980px; top: 350px; border-color: #2ca02c; color: #2ca02c; height: 120px; }}
    .ausland {{ left: 510px; top: 730px; border-color: #9467bd; color: #9467bd; height: 80px; }}

    .objekt {{
        position: absolute; font-size: 26px; z-index: 5; background: #f8f9fa; 
        border-radius: 50%; padding: 2px; transform: translate(-50%, -50%);
    }}

    /* --- Animations-Zuordnungen --- */
    .e_hs {{ animation: l_hs {dauer}s linear infinite; }}
    .e_sh {{ animation: l_sh {dauer}s linear infinite; }}
    .e_us {{ animation: l_us {dauer}s linear infinite; }}
    .e_su {{ animation: l_su {dauer}s linear infinite; }}
    .e_sb {{ animation: l_sb {dauer}s linear infinite; }}
    .e_bs {{ animation: l_bs {dauer}s linear infinite; }}
    .e_hb {{ animation: l_hb {dauer}s linear infinite; }}
    .e_bu {{ animation: l_bu {dauer}s linear infinite; }}
    .e_ha {{ animation: l_ha {dauer}s linear infinite; }}
    .e_ah {{ animation: l_ah {dauer}s linear infinite; }}
    .e_ua {{ animation: l_ua {dauer}s linear infinite; }}
    .e_au {{ animation: l_au {dauer}s linear infinite; }}
    .e_hug {{ animation: l_hug {dauer}s linear infinite; }}
    .e_uhw {{ animation: l_uhw {dauer}s linear infinite; }}
    .e_uhe {{ animation: l_uhe {dauer}s linear infinite; }}
    .e_hua {{ animation: l_hua {dauer}s linear infinite; }}

    /* --- Die Keyframes (16 Perfekte Routen) --- */
    @keyframes l_hs {{ 0%{{left:180px; top:350px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:510px; top:120px; opacity:0;}} }}
    @keyframes l_sh {{ 0%{{left:510px; top:100px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:150px; top:350px; opacity:0;}} }}
    @keyframes l_us {{ 0%{{left:1020px; top:350px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:690px; top:120px; opacity:0;}} }}
    @keyframes l_su {{ 0%{{left:690px; top:100px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:1050px; top:350px; opacity:0;}} }}

    @keyframes l_sb {{ 0%{{left:580px; top:120px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:580px; top:360px; opacity:0;}} }}
    @keyframes l_bs {{ 0%{{left:620px; top:360px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:620px; top:120px; opacity:0;}} }}

    @keyframes l_hb {{ 0%{{left:220px; top:410px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:510px; top:410px; opacity:0;}} }}
    @keyframes l_bu {{ 0%{{left:690px; top:410px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:980px; top:410px; opacity:0;}} }}

    @keyframes l_ha {{ 0%{{left:180px; top:470px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:510px; top:730px; opacity:0;}} }}
    @keyframes l_ah {{ 0%{{left:510px; top:750px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:150px; top:470px; opacity:0;}} }}
    @keyframes l_ua {{ 0%{{left:1020px; top:470px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:690px; top:730px; opacity:0;}} }}
    @keyframes l_au {{ 0%{{left:690px; top:750px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:1050px; top:470px; opacity:0;}} }}

    /* H <-> U Direkt (Fahren über und unter der Bank vorbei) */
    @keyframes l_hug {{ 0%{{left:220px; top:320px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:980px; top:320px; opacity:0;}} }}
    @keyframes l_uhw {{ 0%{{left:980px; top:340px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:220px; top:340px; opacity:0;}} }}
    @keyframes l_uhe {{ 0%{{left:980px; top:480px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:220px; top:480px; opacity:0;}} }}
    @keyframes l_hua {{ 0%{{left:220px; top:500px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:980px; top:500px; opacity:0;}} }}

    /* Kleine Text-Labels für die Ströme */
    .label {{ position: absolute; font-size: 13px; font-weight: bold; z-index: 1; transform: translate(-50%, -50%); padding: 2px 5px; background: rgba(248, 249, 250, 0.9); border-radius: 4px;}}

    .lbl-hs {{ left: 345px; top: 235px; color: #d62728; }}
    .lbl-sh {{ left: 290px; top: 200px; color: #d62728; }}
    .lbl-us {{ left: 855px; top: 235px; color: #d62728; }}
    .lbl-su {{ left: 910px; top: 200px; color: #d62728; }}

    .lbl-sb {{ left: 580px; top: 240px; color: #ff7f0e; }}
    .lbl-bs {{ left: 620px; top: 240px; color: #ff7f0e; }}
    .lbl-hb {{ left: 365px; top: 410px; color: #ff7f0e; }}
    .lbl-bu {{ left: 835px; top: 410px; color: #ff7f0e; }}

    .lbl-ha {{ left: 345px; top: 600px; color: #9467bd; }}
    .lbl-ah {{ left: 290px; top: 630px; color: #9467bd; }}
    .lbl-ua {{ left: 855px; top: 600px; color: #9467bd; }}
    .lbl-au {{ left: 910px; top: 630px; color: #9467bd; }}

    .lbl-hug {{ left: 600px; top: 320px; color: #1f77b4; }}
    .lbl-uhw {{ left: 600px; top: 340px; color: #2ca02c; }}
    .lbl-uhe {{ left: 600px; top: 480px; color: #2ca02c; }}
    .lbl-hua {{ left: 600px; top: 500px; color: #1f77b4; }}

</style>
</head>
<body>
    <div class="kreislauf-box">

        <svg style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:0;">
            <line x1="180" y1="350" x2="510" y2="120" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>
            <line x1="150" y1="350" x2="510" y2="100" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>
            <line x1="1020" y1="350" x2="690" y2="120" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>
            <line x1="1050" y1="350" x2="690" y2="100" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>

            <line x1="580" y1="120" x2="580" y2="360" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>
            <line x1="620" y1="120" x2="620" y2="360" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>

            <line x1="220" y1="410" x2="510" y2="410" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>
            <line x1="690" y1="410" x2="980" y2="410" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>

            <line x1="180" y1="470" x2="510" y2="730" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>
            <line x1="150" y1="470" x2="510" y2="750" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>
            <line x1="1020" y1="470" x2="690" y2="730" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>
            <line x1="1050" y1="470" x2="690" y2="750" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>

            <line x1="220" y1="320" x2="980" y2="320" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>
            <line x1="220" y1="340" x2="980" y2="340" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>
            <line x1="220" y1="480" x2="980" y2="480" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>
            <line x1="220" y1="500" x2="980" y2="500" stroke="#ced4da" stroke-width="3" stroke-dasharray="6,6"/>
        </svg>

        <div class="akteur staat">Staat</div>
        <div class="akteur haushalte">Haushalte</div>
        <div class="akteur banken">Banken</div>
        <div class="akteur unternehmen">Unternehmen</div>
        <div class="akteur ausland">Ausland</div>

        <div class="label lbl-hs">Steuern ↗</div> <div class="label lbl-sh">↙ Transfers</div>
        <div class="label lbl-us">↖ Steuern</div> <div class="label lbl-su">Konsum ↘</div>
        <div class="label lbl-sb">Sparen ↓</div> <div class="label lbl-bs">↑ Kredite</div>
        <div class="label lbl-hb">Sparen →</div> <div class="label lbl-bu">Investitionen →</div>
        <div class="label lbl-ha">Transfers ↘</div> <div class="label lbl-ah">↖ Transfers</div>
        <div class="label lbl-ua">Importe ↙</div> <div class="label lbl-au">↗ Exporte</div>
        <div class="label lbl-hug">Konsumausgaben →</div> <div class="label lbl-uhw">← Konsumgüter</div>
        <div class="label lbl-uhe">← Einkommen</div> <div class="label lbl-hua">Arbeitskraft →</div>

        <div class="objekt e_hs">🪙</div> <div class="objekt e_hs" style="animation-delay: {verzogerung}s;">🪙</div>
        <div class="objekt e_sh">💶</div> <div class="objekt e_sh" style="animation-delay: {verzogerung}s;">💶</div>
        <div class="objekt e_us">🪙</div> <div class="objekt e_us" style="animation-delay: {verzogerung}s;">🪙</div>
        <div class="objekt e_su">💶</div> <div class="objekt e_su" style="animation-delay: {verzogerung}s;">💶</div>

        <div class="objekt e_sb">🐖</div> <div class="objekt e_sb" style="animation-delay: {verzogerung}s;">🐖</div>
        <div class="objekt e_bs">🏦</div> <div class="objekt e_bs" style="animation-delay: {verzogerung}s;">🏦</div>
        <div class="objekt e_hb">🐖</div> <div class="objekt e_hb" style="animation-delay: {verzogerung}s;">🐖</div>
        <div class="objekt e_bu">🏗️</div> <div class="objekt e_bu" style="animation-delay: {verzogerung}s;">🏗️</div>

        <div class="objekt e_ha">💸</div> <div class="objekt e_ha" style="animation-delay: {verzogerung}s;">💸</div>
        <div class="objekt e_ah">💶</div> <div class="objekt e_ah" style="animation-delay: {verzogerung}s;">💶</div>
        <div class="objekt e_ua">💸</div> <div class="objekt e_ua" style="animation-delay: {verzogerung}s;">💸</div>
        <div class="objekt e_au">💶</div> <div class="objekt e_au" style="animation-delay: {verzogerung}s;">💶</div>

        <div class="objekt e_hug">💶</div> <div class="objekt e_hug" style="animation-delay: {verzogerung}s;">💶</div>
        <div class="objekt e_uhw">🛍️</div> <div class="objekt e_uhw" style="animation-delay: {verzogerung}s;">🛍️</div>
        <div class="objekt e_uhe">💶</div> <div class="objekt e_uhe" style="animation-delay: {verzogerung}s;">💶</div>
        <div class="objekt e_hua">🧑‍🔧</div> <div class="objekt e_hua" style="animation-delay: {verzogerung}s;">🧑‍🔧</div>

    </div>
</body>
</html>
"""

components.html(html_code, height=880)