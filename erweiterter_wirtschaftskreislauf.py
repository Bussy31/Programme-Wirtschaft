import streamlit as st
import streamlit.components.v1 as components

# --- Seiten-Setup ---
st.set_page_config(page_title="Wirtschafts-Lab Pro", layout="wide")

st.title("🌐 Eco-Lab: Das offene Wirtschaftssystem")
st.markdown("Beobachte das Modell und ordne alle **Geld- und Güterströme** korrekt zu!")
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

# --- Eingabefelder imGrid-Layout (Fokus auf den Kern, klar getrennt) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Haushalte & Staat/Ausland")
    st.markdown("**Zum Staat**")
    h_s = st.selectbox("Haushalte ➔ Staat (Geldstrom):", optionen, key="hs")
    s_h = st.selectbox("Staat ➔ Haushalte (Geldstrom):", optionen, key="sh")
    st.markdown("**Zum Ausland**")
    h_a = st.selectbox("Haushalte ➔ Ausland (Geldstrom):", optionen, key="ha")
    a_h = st.selectbox("Ausland ➔ Haushalte (Geldstrom):", optionen, key="ah")

with col2:
    st.subheader("2. Kernkreislauf (H & U)")
    st.markdown("**Güter <-> Geld direkt**")
    h_u_geld = st.selectbox("Haushalte ➔ Unternehmen (Geldstrom für Käufe):", optionen, key="hug")
    u_h_gut = st.selectbox("Unternehmen ➔ Haushalte (Güterstrom):", optionen, key="uhg")

    u_h_geld = st.selectbox("Unternehmen ➔ Haushalte (Geldstrom für Arbeit):", optionen, key="uhl")
    h_u_gut = st.selectbox("Haushalte ➔ Unternehmen (Faktoren: Arbeit etc.):", optionen, key="hua")

with col3:
    st.subheader("3. Banken, Unternehmen & Staat/Ausland")
    st.markdown("**Über die Banken**")
    h_b = st.selectbox("Haushalte ➔ Banken (Geldstrom):", optionen, key="hb")
    b_u = st.selectbox("Banken ➔ Unternehmen (Geldstrom):", optionen, key="bu")

    st.markdown("**Zum Staat**")
    u_s = st.selectbox("Unternehmen ➔ Staat (Geldstrom):", optionen, key="us")
    s_u = st.selectbox("Staat ➔ Unternehmen (Geldstrom für Käufe):", optionen, key="su")

    st.markdown("**Zum Ausland**")
    a_u = st.selectbox("Ausland ➔ Unternehmen (Geldstrom für Exporte):", optionen, key="au")
    u_a = st.selectbox("Unternehmen ➔ Ausland (Geldstrom für Importe):", optionen, key="ua")

# --- Logik-Check (Fast alle 16 Ströme) ---
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
        s_u == "staatlicher Konsum" and
        h_a == "Transfer der Haushalte" and
        a_h == "Transfer des Auslands" and
        a_u == "Zahlungen für Exporte" and
        u_a == "Zahlungen für Importe"
)

st.divider()

# --- Feedback-Nachricht (erst wenn alles richtig ist) ---
if alles_richtig:
    st.success("🎉 Meisterhaft! Du hast das komplette offene Wirtschaftssystem korrekt verstanden und zugeordnet.")
else:
    st.info(
        "💡 Das System läuft! Aber einige Beschriftungen in den Feldern oben fehlen noch oder sind nicht korrekt. Orientier dich am Diagramm.")

# --- HTML & CSS für das neue, verbesserte Design & Animation ---
dauer = 5.0  # Feste Geschwindigkeit

html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    .canvas {{
        position: relative; width: 100%; max-width: 1000px; height: 750px;
        background-color: #f8f9fa; border-radius: 10px; margin: 0 auto;
        border: 2px solid #ced4da; overflow: hidden; font-family: sans-serif;
    }}

    .akteur {{
        position: absolute; background: white; color: #333; border-radius: 10px;
        text-align: center; font-weight: bold; z-index: 10; display: flex;
        align-items: center; justify-content: center; 
        border: 4px solid #333; font-size: 18px;
    }}

    /* Vergrößertes Sektoren-Layout (Kreuz) */
    .staat {{ width: 180px; height: 80px; left: 410px; top: 20px; border-color: #d62728; }}
    .ausland {{ width: 180px; height: 80px; left: 410px; top: 650px; border-color: #9467bd; }}
    .banken {{ width: 180px; height: 100px; left: 410px; top: 150px; border-color: #ff7f0e; }} /* Bank weiter nach oben */
    .haushalte {{ width: 180px; height: 100px; left: 30px; top: 350px; border-color: #1f77b4; }}
    .unternehmen {{ width: 180px; height: 100px; left: 790px; top: 350px; border-color: #2ca02c; }}

    /* Fliegende Emojis (Güter & Geld) */
    .emoji {{ position: absolute; font-size: 24px; z-index: 20; background: #f8f9fa; border-radius: 50%; padding: 2px;}}

    /* --- Labels & Pfeile (CSS Overlay) --- */
    .label {{
        position: absolute; font-size: 12px; font-weight: bold; color: #666; 
        z-index: 15; background: rgba(248, 249, 250, 0.9); padding: 2px 5px; border-radius: 4px;
        text-align: center; display: flex; align-items: center; justify-content: center;
    }}
    /* Positionierung aller 16 Labels */
    .lbl-hs {{ left: 310px; top: 225px; transform: translate(-50%, -50%); color: #d62728;}}
    .lbl-sh {{ left: 310px; top: 225px; transform: translate(-50%, -50%); color: #d62728;}}
    .lbl-us {{ left: 690px; top: 225px; transform: translate(-50%, -50%); color: #d62728;}}
    .lbl-su {{ left: 690px; top: 225px; transform: translate(-50%, -50%); color: #d62728;}}
    .lbl-sb {{ left: 500px; top: 125px; transform: translate(-50%, -50%); color: #ff7f0e;}}
    .lbl-bs {{ left: 500px; top: 125px; transform: translate(-50%, -50%); color: #ff7f0e;}}
    .lbl-hb {{ left: 310px; top: 300px; transform: translate(-50%, -50%); color: #ff7f0e;}}
    .lbl-bu {{ left: 690px; top: 300px; transform: translate(-50%, -50%); color: #ff7f0e;}}
    .lbl-ha {{ left: 310px; top: 550px; transform: translate(-50%, -50%); color: #9467bd;}}
    .lbl-ah {{ left: 310px; top: 550px; transform: translate(-50%, -50%); color: #9467bd;}}
    .lbl-ua {{ left: 690px; top: 550px; transform: translate(-50%, -50%); color: #9467bd;}}
    .lbl-au {{ left: 690px; top: 550px; transform: translate(-50%, -50%); color: #9467bd;}}
    /* Labels Kern H<->U (alle zentral) */
    .label-hu {{ left: 500px; transform: translate(-50%, -50%); }}
    .lbl-hu-g {{ top: 370px; color: #1f77b4; }}
    .lbl-uh-w {{ top: 390px; color: #2ca02c; }}
    .lbl-uh-e {{ top: 410px; color: #2ca02c; }}
    .lbl-hu-a {{ top: 430px; color: #1f77b4; }}


    /* --- Animations-Routen (Alles auf geraden Schienen) --- */
    /* Basis-Kreuz H/U <-> Staat/Ausland */
    @keyframes m_hs {{ 0%{{left:120px; top:350px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:500px; top:100px; opacity:0;}} }}
    @keyframes m_sh {{ 0%{{left:500px; top:100px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:120px; top:350px; opacity:0;}} }}
    @keyframes m_us {{ 0%{{left:880px; top:350px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:500px; top:100px; opacity:0;}} }}
    @keyframes m_su {{ 0%{{left:500px; top:100px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:880px; top:350px; opacity:0;}} }}
    @keyframes m_ha {{ 0%{{left:120px; top:450px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:500px; top:650px; opacity:0;}} }}
    @keyframes m_ah {{ 0%{{left:500px; top:650px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:120px; top:450px; opacity:0;}} }}
    @keyframes m_ua {{ 0%{{left:880px; top:450px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:500px; top:650px; opacity:0;}} }}
    @keyframes m_au {{ 0%{{left:500px; top:650px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:880px; top:450px; opacity:0;}} }}
    /* Vertikal Staat <-> Bank */
    @keyframes m_sb {{ 0%{{left:500px; top:100px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:500px; top:150px; opacity:0;}} }}
    @keyframes m_bs {{ 0%{{left:500px; top:150px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:500px; top:100px; opacity:0;}} }}
    /* Diagonal über Bank */
    @keyframes m_hb {{ 0%{{left:120px; top:350px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:500px; top:250px; opacity:0;}} }}
    @keyframes m_bu {{ 0%{{left:500px; top:250px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:880px; top:350px; opacity:0;}} }}

    /* Kern H <-> U (4 Parallel und Gerade) */
    @keyframes m_hu_geld {{ 0%{{left:210px; top:370px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:770px; top:370px; opacity:0;}} }}
    @keyframes m_uh_gut {{ 0%{{left:770px; top:390px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:210px; top:390px; opacity:0;}} }}
    @keyframes m_uh_geld {{ 0%{{left:770px; top:410px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:210px; top:410px; opacity:0;}} }}
    @keyframes m_hu_gut {{ 0%{{left:210px; top:430px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:770px; top:430px; opacity:0;}} }}

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
            <line x1="120" y1="350" x2="500" y2="100" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="880" y1="350" x2="500" y2="100" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="500" y1="100" x2="500" y2="150" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="500" y1="150" x2="500" y2="100" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="120" y1="350" x2="500" y2="250" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="500" y1="250" x2="880" y2="350" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="120" y1="450" x2="500" y2="650" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="880" y1="450" x2="500" y2="650" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>

            <line x1="210" y1="370" x2="790" y2="370" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="790" y1="390" x2="210" y2="390" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="790" y1="410" x2="210" y2="410" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="210" y1="430" x2="790" y2="430" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
        </svg>

        <div class="akteur staat">Staat</div>
        <div class="akteur haushalte">Haushalte</div>
        <div class="akteur banken">Banken</div>
        <div class="akteur unternehmen">Unternehmen</div>
        <div class="akteur ausland">Ausland</div>

        <div class="label lbl-hs">Steuern, Sozialabgaben →</div>
        <div class="label lbl-sh">Transferleistungen ←</div>
        <div class="label lbl-us">Steuern abzüglich Subventionen →</div>
        <div class="label lbl-su">staatlicher Konsum ←</div>
        <div class="label lbl-sb">staatliche Ersparnisse ↓</div>
        <div class="label lbl-bs">staatliche Kreditaufnahme ↑</div>
        <div class="label lbl-hb">Spareinlagen →</div>
        <div class="label lbl-bu">Investitionen →</div>
        <div class="label lbl-ha">Transfer der Haushalte ↓</div>
        <div class="label lbl-ah">Transfer des Auslands ↑</div>
        <div class="label lbl-ua">Zahlungen für Importe ↓</div>
        <div class="label lbl-au">Zahlungen für Exporte ↑</div>
        <div class="label label-hu lbl-hu-g">Konsumausgaben →</div>
        <div class="label label-hu lbl-uh-w">Konsumgüter ←</div>
        <div class="label label-hu lbl-uh-e">Einkommen ←</div>
        <div class="label label-hu lbl-hu-a">Arbeitskraft, Boden, Kapital →</div>

        <div class="emoji e_hs" title="Steuern">🪙</div>
        <div class="emoji e_sh" title="Transfers">💶</div>
        <div class="emoji e_us" title="Steuern">🪙</div>
        <div class="emoji e_su" title="Subventionen">💶</div>
        <div class="emoji e_sb" title="Ersparnisse">🐖</div>
        <div class="emoji e_bs" title="Schulden">🏦</div>
        <div class="emoji e_hb" title="Spareinlagen">🐖</div>
        <div class="emoji e_bu" title="Investitionen">🏗️</div>
        <div class="emoji e_ha" title="Transfer ins Ausland">💸</div>
        <div class="emoji e_ah" title="Transfer aus Ausland">💶</div>
        <div class="emoji e_ua" title="Zahlung für Importe">💸</div>
        <div class="emoji e_au" title="Zahlung für Exporte">💶</div>
        <div class="emoji e_hu_geld" title="Konsumausgaben">💶</div>
        <div class="emoji e_uh_gut" title="Konsumgüter">🛍️</div>
        <div class="emoji e_uh_geld" title="Einkommen">💶</div>
        <div class="emoji e_hu_gut" title="Arbeit/Faktoren">🧑‍🔧</div>

    </div>
</body>
</html>
"""

# Die Animation wird immer gerendert (height angepasst)
components.html(html_code, height=750)