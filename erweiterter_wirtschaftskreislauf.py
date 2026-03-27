import streamlit as st
import streamlit.components.v1 as components

# --- Seiten-Setup ---
st.set_page_config(page_title="Wirtschafts-Lab Pro", layout="wide")

st.title("Der erweiterte Wirtschaftskreislauf")
st.markdown("Beobachte das Modell und ordne alle **Geld- und Güterströme** korrekt zu!")
st.divider()

# --- Alle Antwortmöglichkeiten aus dem Diagramm ---
optionen = [
    "Bitte wählen...",
    "Steuern, Sozialabgaben", "Transferleistungen",
    "staatlicher Konsum", "Steuern abzüglich Subventionen",
    "Spareinlagen", "Investitionen",
    "Konsumausgaben", "Konsumgüter",
    "Einkommen", "Arbeitskraft",
    "Transfer der Haushalte", "Transfer des Auslands",
    "Zahlungen für Exporte", "Zahlungen für Importe",
    "staatliche Ersparnisse", "staatliche Kreditaufnahme"
]

# --- Eingabefelder imGrid-Layout (Fokus auf den Kern, klar getrennt) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("1. Haushalte & Staat")
    h_s = st.selectbox("Haushalte ➔ Staat (Geldstrom):", optionen, key="hs")
    s_h = st.selectbox("Staat ➔ Haushalte (Geldstrom):", optionen, key="sh")
    u_s = st.selectbox("Unternehmen ➔ Staat (Geldstrom):", optionen, key="us")
    s_u = st.selectbox("Staat ➔ Unternehmen (Güterstrom):", optionen, key="su")

    # Logik-Check für die Kategorie
    staat_correct = (
            h_s == "Steuern, Sozialabgaben" and s_h == "Transferleistungen" and
            u_s == "Steuern abzüglich Subventionen" and s_u == "staatlicher Konsum"
    )

    if staat_correct:
        st.success("🎉 Kategorie 'Mit dem Staat' korrekt gelöst!")

with col2:
    st.subheader("2. Kernkreislauf (H & U)")
    h_u_geld = st.selectbox("Haushalte ➔ Unternehmen (Geldstrom):", optionen, key="hug")
    u_h_gut = st.selectbox("Unternehmen ➔ Haushalte (Güterstrom):", optionen, key="uhg")

    u_h_geld = st.selectbox("Unternehmen ➔ Haushalte (Geldstrom):", optionen, key="uhl")
    h_u_gut = st.selectbox("Haushalte ➔ Unternehmen (Faktoren):", optionen, key="hua")

    kern_correct = (
            h_u_geld == "Konsumausgaben" and u_h_gut == "Konsumgüter" and
            u_h_geld == "Einkommen" and h_u_gut == "Arbeitskraft"
    )

    if kern_correct:
        st.success("🎉 Kategorie 'Kern (H & U)' korrekt gelöst!")

with col3:
    st.subheader("3. Banken")
    h_b = st.selectbox("Haushalte ➔ Banken (Geldstrom):", optionen, key="hb")
    b_u = st.selectbox("Banken ➔ Unternehmen (Geldstrom):", optionen, key="bu")
    s_b = st.selectbox("Staat ➔ Banken (Geldstrom):", optionen, key="sb")
    b_s = st.selectbox("Banken ➔ Staat (Geldstrom):", optionen, key="bs")

    banken_correct = (
            h_b == "Spareinlagen" and b_u == "Investitionen" and
            s_b == "staatliche Ersparnisse" and b_s == "staatliche Kreditaufnahme"
    )

    if banken_correct:
        st.success("🎉 Kategorie 'Über die Banken' korrekt gelöst!")

with col4:
    st.subheader("4. Ausland")
    h_a = st.selectbox("Haushalte ➔ Ausland (Geldstrom):", optionen, key="ha")
    a_h = st.selectbox("Ausland ➔ Haushalte (Geldstrom):", optionen, key="ah")
    a_u = st.selectbox("Ausland ➔ Unternehmen (Geldstrom):", optionen, key="au")
    u_a = st.selectbox("Unternehmen ➔ Ausland (Geldstrom):", optionen, key="ua")

    ausland_correct = (
            a_u == "Zahlungen für Exporte" and u_a == "Zahlungen für Importe" and
            h_a == "Transfer der Haushalte" and a_h == "Transfer des Auslands"
    )

    if ausland_correct:
        st.success("🎉 Kategorie 'Mit dem Ausland' korrekt gelöst!")

# --- Logik-Check (Fast alle 16 Ströme) ---
alles_richtig = staat_correct and kern_correct and banken_correct and ausland_correct

st.divider()

if alles_richtig:
    st.success("🎉 Meisterhaft! Du hast das komplette offene Wirtschaftssystem korrekt verstanden und zugeordnet.")
else:
    st.info(
        "❕ Einige Beschriftungen in den Feldern oben fehlen noch oder sind nicht korrekt. Orientier dich am Wirtschaftskreislauf.")

# --- NEU: PDF Export der Lösungen ---
from fpdf import FPDF

def generiere_loesungs_pdf():
    pdf = FPDF()
    pdf.add_page()

    # Titel
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Lösungen: Offenes Wirtschaftssystem", ln=True, align="C")
    pdf.ln(5)

    # Inhalt (Umlaute als ae, oe, ue geschrieben, da Standard-Arial im PDF sonst zicken kann)
    pdf.set_font("Arial", size=12)
    loesungen = [
        "1. Haushalte & Staat",
        "   - Haushalte -> Staat: Steuern, Sozialabgaben",
        "   - Staat -> Haushalte: Transferleistungen",
        "   - Unternehmen -> Staat: Steuern abzüglich Subventionen",
        "   - Staat -> Unternehmen: staatlicher Konsum",
        "",
        "2. Kernkreislauf (H & U)",
        "   - Haushalte -> Unternehmen: Konsumausgaben",
        "   - Unternehmen -> Haushalte: Konsumgüter",
        "   - Unternehmen -> Haushalte: Einkommen",
        "   - Haushalte -> Unternehmen: Arbeitskraft",
        "",
        "3. Banken",
        "   - Haushalte -> Banken: Spareinlagen",
        "   - Banken -> Unternehmen: Investitionen",
        "   - Staat -> Banken: staatliche Ersparnisse",
        "   - Banken -> Staat: staatliche Kreditaufnahme",
        "",
        "4. Ausland",
        "   - Haushalte -> Ausland: Transfer der Haushalte",
        "   - Ausland -> Haushalte: Transfer des Auslands",
        "   - Ausland -> Unternehmen: Zahlungen für Exporte",
        "   - Unternehmen -> Ausland: Zahlungen für Importe"
    ]

    for zeile in loesungen:
        pdf.cell(0, 7, txt=zeile, ln=True)

    # PDF als Bytes zurückgeben (latin-1 Encoding ist wichtig für fpdf)
    return bytes(pdf.output(dest="S").encode("latin-1"))


# Button zum Download anzeigen
if alles_richtig:
    st.write("Brauchst du die Lösungen auf Papier?")
    st.download_button(
        label="📄 Lösungen als PDF herunterladen",
        data=generiere_loesungs_pdf(),
        file_name="Loesungen_Wirtschaftskreislauf.pdf",
        mime="application/pdf"
    )
    st.divider()

# --- Wirtschaftspolitik-Regler (Konjunktur & EZB) ---
st.subheader("📈 Steuere die Wirtschaftspolitik!")

col_regler1, col_regler2 = st.columns(2)

with col_regler1:
    st.markdown("**Konjunktur (Fiskalpolitik)**")
    konjunktur = st.slider("Wirtschaftslage (1 = Krise, 10 = Boom)", min_value=1, max_value=10, value=5)

with col_regler2:
    st.markdown("**Leitzins (Geldpolitik der EZB)**")
    # Normalzins jetzt auf 2.5% angepasst!
    zins = st.slider("EZB-Leitzins (in %)", min_value=0.0, max_value=5.0, value=2.5, step=0.5)

# ==========================================
# 1. MATHE (Muss zwingend VOR dem HTML kommen!)
# ==========================================

# Basis-Geschwindigkeit durch Konjunktur
dauer = 8.0 - (konjunktur * 0.6)
verzogerung = dauer / 2

# Extreme EZB-Mathe für spürbares Tempo (Basis 2.5%)
if zins == 2.5:
    dauer_sparen = dauer
    dauer_kredit = dauer
elif zins > 2.5:
    # Zins hoch: Sparen rast, Kredite schleichen
    intensitaet = (zins - 2.5) / 2.5  # Wert zwischen 0 und 1
    dauer_sparen = dauer * (1.0 - (intensitaet * 0.85)) # bis zu 85% schneller
    dauer_kredit = dauer * (1.0 + (intensitaet * 4.0))  # bis zu 400% langsamer
else:
    # Zins niedrig: Kredite rasen, Sparen schleicht
    intensitaet = (2.5 - zins) / 2.5  # Wert zwischen 0 und 1
    dauer_kredit = dauer * (1.0 - (intensitaet * 0.85))
    dauer_sparen = dauer * (1.0 + (intensitaet * 4.0))

# Sicherheits-Limits (CSS darf nicht 0 oder negativ sein)
dauer_sparen = max(0.4, dauer_sparen)
dauer_kredit = max(0.4, dauer_kredit)

# Verzögerung für das jeweils zweite Emoji auf der Bahn
verzogerung_sparen = dauer_sparen / 2
verzogerung_kredit = dauer_kredit / 2

# --- HTML & CSS für das neue, verbesserte Design & Animation ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    .canvas {{
        position: relative; width: 100%; max-width: 1000px; height: 750px;
        background-color: #f8f9fa; border-radius: 10px; margin: 0 auto;
        border: 2px solid #ced4da; overflow: hidden; font-family: sans-serif;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}

    .akteur {{
        position: absolute; background: white; color: #333; border-radius: 10px;
        text-align: center; font-weight: bold; z-index: 10; display: flex;
        align-items: center; justify-content: center; 
        border: 4px solid #333; font-size: 18px;
    }}

    /* Layout */
    .staat {{ width: 180px; height: 80px; left: 410px; top: 20px; border-color: #d62728; }}
    .ausland {{ width: 180px; height: 80px; left: 410px; top: 650px; border-color: #9467bd; }}
    .banken {{ width: 180px; height: 100px; left: 410px; top: 220px; border-color: #ff7f0e; }} /* Banken nach unten korrigiert! */
    .haushalte {{ width: 180px; height: 140px; left: 30px; top: 330px; border-color: #1f77b4; }} /* Große Boxen bleiben */
    .unternehmen {{ width: 180px; height: 140px; left: 790px; top: 330px; border-color: #2ca02c; }}

    /* Fliegende Emojis (Güter & Geld) */
    .emoji {{ position: absolute; font-size: 24px; z-index: 20; background: #f8f9fa; border-radius: 50%; padding: 2px; transform: translate(-50%, -50%);}}

    /* --- Labels & Pfeile --- */
    .label {{
        position: absolute; font-size: 12px; font-weight: bold; color: #666; 
        z-index: 15; background: rgba(248, 249, 250, 0.9); padding: 2px 5px; border-radius: 4px;
        text-align: center; display: flex; align-items: center; justify-content: center;
    }}

    /* Positionierung aller 16 Labels passend zu den parallelen Linien */
    .lbl-hs {{ left: 260px; top: 215px; transform: translate(-50%, -50%); color: #d62728;}}
    .lbl-sh {{ left: 350px; top: 215px; transform: translate(-50%, -50%); color: #d62728;}}
    .lbl-us {{ left: 740px; top: 215px; transform: translate(-50%, -50%); color: #d62728;}}
    .lbl-su {{ left: 650px; top: 215px; transform: translate(-50%, -50%); color: #d62728;}}

    .lbl-sb {{ left: 450px; top: 160px; transform: translate(-50%, -50%); color: #ff7f0e;}}
    .lbl-bs {{ left: 550px; top: 160px; transform: translate(-50%, -50%); color: #ff7f0e;}}

    .lbl-hb {{ left: 310px; top: 320px; transform: translate(-50%, -50%); color: #ff7f0e;}}
    .lbl-bu {{ left: 690px; top: 320px; transform: translate(-50%, -50%); color: #ff7f0e;}}

    .lbl-ha {{ left: 260px; top: 560px; transform: translate(-50%, -50%); color: #9467bd;}}
    .lbl-ah {{ left: 350px; top: 560px; transform: translate(-50%, -50%); color: #9467bd;}}
    .lbl-ua {{ left: 740px; top: 560px; transform: translate(-50%, -50%); color: #9467bd;}}
    .lbl-au {{ left: 650px; top: 560px; transform: translate(-50%, -50%); color: #9467bd;}}

    /* Labels Kern H<->U */
    .label-hu {{ left: 500px; transform: translate(-50%, -50%); }}
    .lbl-hu-g {{ top: 370px; color: #1f77b4; }}
    .lbl-uh-w {{ top: 390px; color: #2ca02c; }}
    .lbl-uh-e {{ top: 410px; color: #2ca02c; }}
    .lbl-hu-a {{ top: 430px; color: #1f77b4; }}

    /* --- Animations-Routen (Jetzt wieder mit parallelen, separaten Pfaden!) --- */
    @keyframes m_hs {{ 0%{{left:120px; top:330px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:450px; top:100px; opacity:0;}} }}
    @keyframes m_sh {{ 0%{{left:490px; top:100px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:160px; top:330px; opacity:0;}} }}

    @keyframes m_us {{ 0%{{left:880px; top:330px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:550px; top:100px; opacity:0;}} }}
    @keyframes m_su {{ 0%{{left:510px; top:100px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:840px; top:330px; opacity:0;}} }}

    @keyframes m_ha {{ 0%{{left:120px; top:470px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:450px; top:650px; opacity:0;}} }}
    @keyframes m_ah {{ 0%{{left:490px; top:650px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:160px; top:470px; opacity:0;}} }}

    @keyframes m_ua {{ 0%{{left:880px; top:470px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:550px; top:650px; opacity:0;}} }}
    @keyframes m_au {{ 0%{{left:510px; top:650px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:840px; top:470px; opacity:0;}} }}
    @keyframes l_ua_gueter {{ 0%{{left:550px; top:650px; opacity:0;}} 10%{{opacity: 1;}} 90%{{opacity: 1;}} 100%{{left:880px; top:470px; opacity:0;}} }}
    @keyframes l_au_gueter {{ 0%{{left:840px; top:470px; opacity:0;}} 10%{{opacity: 1;}} 90%{{opacity: 1;}} 100%{{left:510px; top:650px; opacity:0;}} }}

    @keyframes m_sb {{ 0%{{left:480px; top:100px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:480px; top:220px; opacity:0;}} }}
    @keyframes m_bs {{ 0%{{left:520px; top:220px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:520px; top:100px; opacity:0;}} }}

    @keyframes m_hb {{ 0%{{left:210px; top:340px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:410px; top:280px; opacity:0;}} }}
    @keyframes m_bu {{ 0%{{left:590px; top:280px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:790px; top:340px; opacity:0;}} }}

    /* Kern H <-> U (4 Parallel) */
    @keyframes m_hu_geld {{ 0%{{left:210px; top:370px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:790px; top:370px; opacity:0;}} }}
    @keyframes m_uh_gut {{ 0%{{left:790px; top:390px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:210px; top:390px; opacity:0;}} }}
    @keyframes m_uh_geld {{ 0%{{left:790px; top:410px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:210px; top:410px; opacity:0;}} }}
    @keyframes m_hu_gut {{ 0%{{left:210px; top:430px; opacity:0;}} 10%{{opacity:1;}} 90%{{opacity:1;}} 100%{{left:790px; top:430px; opacity:0;}} }}

    /* Zuweisung */
    .e_hs {{ animation: m_hs {dauer}s linear infinite; }}
    .e_sh {{ animation: m_sh {dauer}s linear infinite; }}
    .e_us {{ animation: m_us {dauer}s linear infinite; }}
    .e_su {{ animation: m_su {dauer}s linear infinite; }}
    .e_sb {{ animation: m_sb {dauer_sparen}s linear infinite; }}
    .e_bs {{ animation: m_bs {dauer_kredit}s linear infinite; }}
    .e_hb {{ animation: m_hb {dauer_sparen}s linear infinite; }}
    .e_bu {{ animation: m_bu {dauer_kredit}s linear infinite; }}
    .e_ha {{ animation: m_ha {dauer}s linear infinite; }}
    .e_ah {{ animation: m_ah {dauer}s linear infinite; }}
    .e_ua {{ animation: m_ua {dauer}s linear infinite; }}
    .e_au {{ animation: m_au {dauer}s linear infinite; }}
    .e_ua_g {{ animation: l_ua_gueter {dauer}s linear infinite; }}
    .e_au_g {{ animation: l_au_gueter {dauer}s linear infinite; }}
    .e_hu_geld {{ animation: m_hu_geld {dauer}s linear infinite; }}
    .e_uh_gut {{ animation: m_uh_gut {dauer}s linear infinite; }}
    .e_uh_geld {{ animation: m_uh_geld {dauer}s linear infinite; }}
    .e_hu_gut {{ animation: m_hu_gut {dauer}s linear infinite; }}

</style>
</head>
<body>
    <div class="canvas">

        <svg width="100%" height="100%" style="position:absolute; top:0; left:0; z-index:1;">
            <line x1="120" y1="330" x2="450" y2="100" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="160" y1="330" x2="490" y2="100" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>

            <line x1="880" y1="330" x2="550" y2="100" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="840" y1="330" x2="510" y2="100" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>

            <line x1="480" y1="100" x2="480" y2="220" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="520" y1="100" x2="520" y2="220" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>

            <line x1="210" y1="340" x2="410" y2="280" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="590" y1="280" x2="790" y2="340" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>

            <line x1="120" y1="470" x2="450" y2="650" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="160" y1="470" x2="490" y2="650" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>

            <line x1="880" y1="470" x2="550" y2="650" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>
            <line x1="840" y1="470" x2="510" y2="650" stroke="#ced4da" stroke-width="3" stroke-dasharray="5,5"/>

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

        <div class="label lbl-hs">Steuern ↗</div>
        <div class="label lbl-sh">↙ Transfers</div>
        <div class="label lbl-us">↖ Steuern</div>
        <div class="label lbl-su">Subventionen ↘</div>

        <div class="label lbl-sb">Sparen ↓</div>
        <div class="label lbl-bs">Kredite ↑</div>

        <div class="label lbl-hb">Sparen ↗</div>
        <div class="label lbl-bu">Investitionen ↘</div>

        <div class="label lbl-ha">Transfers ↘</div>
        <div class="label lbl-ah">↖ Transfers</div>
        <div class="label lbl-ua">↙ Importe</div>
        <div class="label lbl-au">Exporte ↗</div>

        <div class="label label-hu lbl-hu-g">Konsumausgaben →</div>
        <div class="label label-hu lbl-uh-w">Konsumgüter ←</div>
        <div class="label label-hu lbl-uh-e">Einkommen ←</div>
        <div class="label label-hu lbl-hu-a">Arbeitskraft →</div>

        <div class="emoji e_hs" title="Steuern" style="animation-delay: {verzogerung}s;">🪙</div>
        
        <div class="emoji e_sh" title="Transfers" style="animation-delay: {verzogerung}s;">💶</div>
        
        <div class="emoji e_us" title="Steuern" style="animation-delay: {verzogerung}s;">🪙</div>
        
        <div class="emoji e_su" title="Konsum" style="animation-delay: {verzogerung}s;">💶</div>

        <div class="emoji e_sb" title="Ersparnisse" style="animation-delay: {verzogerung}s;">🐖</div>
        
        <div class="emoji e_bs" title="Schulden" style="animation-delay: {verzogerung}s;">🏦</div>
        
        <div class="emoji e_hb" title="Spareinlagen" style="animation-delay: {verzogerung}s;">🐖</div>
        
        <div class="emoji e_bu" title="Investitionen" style="animation-delay: {verzogerung}s;">🏗️</div>

        <div class="emoji e_ha" title="Transfer ins Ausland" style="animation-delay: {verzogerung}s;">💸</div>
        
        <div class="emoji e_ah" title="Transfer aus Ausland" style="animation-delay: {verzogerung}s;">💶</div>
        
        <div class="emoji e_ua" title="Zahlung für Importe" style="animation-delay: {verzogerung}s;">💸</div>

        <div class="emoji e_au" title="Zahlung für Exporte" style="animation-delay: {verzogerung}s;">💶</div>
        
        <div class="emoji e_ua_g" title="Güter für Importe" style="animation-delay: {verzogerung}s;">📦</div>

        <div class="emoji e_au_g" title="Güter für Exporte" style="animation-delay: {verzogerung}s;">📦</div>

        <div class="emoji e_hu_geld" title="Konsumausgaben" style="animation-delay: {verzogerung}s;">💶</div>
        
        <div class="emoji e_uh_gut" title="Konsumgüter" style="animation-delay: {verzogerung}s;">🛍️</div>
        
        <div class="emoji e_uh_geld" title="Einkommen" style="animation-delay: {verzogerung}s;">💶</div>
        
        <div class="emoji e_hu_gut" title="Arbeit/Faktoren" style="animation-delay: {verzogerung}s;">🧑‍🔧</div>

    </div>
</body>
</html>
"""
html_animation = html_code.replace("ANIM_DURATION", str(dauer)).replace("ANIM_DELAY", str(verzogerung))

components.html(html_code, height=750)