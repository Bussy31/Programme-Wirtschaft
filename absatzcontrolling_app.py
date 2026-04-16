import streamlit as st
import pandas as pd
import altair as alt
import math

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ─────────────────────────────────────────────
#  SEITEN-KONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Absatzcontrolling",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  GLOBALES CSS Test
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 1rem !important;
    padding: 8px 0 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #334155 !important;
}

/* Hauptbereich */
.main-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    color: white;
    padding: 2rem 2.5rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    border-left: 5px solid #38bdf8;
}
.main-header h1 { margin: 0; font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; }
.main-header p  { margin: 0.4rem 0 0; color: #94a3b8; font-size: 1rem; }

/* Karten */
.info-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.info-card h4 { margin: 0 0 0.4rem; color: #0f172a; font-size: 1rem; font-weight: 600; }
.info-card p  { margin: 0; color: #475569; font-size: 0.9rem; }

/* Primär-Buttons */
button[kind="primary"] {
    background: #0284c7 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
button[kind="secondary"] {
    background-color: #e0f2fe !important;
    color: #0284c7 !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
}
button[kind="secondary"]:hover {
    background-color: #93c5fd !important;
    color: #ffffff !important;
}

/* Tabellen-Header */
.table-header {
    display: flex;
    gap: 0.5rem;
    background: #e2e8f0;
    padding: 10px 15px;
    border-radius: 8px;
    margin-bottom: 8px;
    border: 1px solid #cbd5e1;
}
.table-header div {
    text-align: center;
    font-weight: 700;
    color: #334155;
    font-size: 0.95rem;
}

/* Footer */
.footer {
    position: fixed;
    bottom: 10px;
    right: 15px;
    font-size: 11px;
    color: #94a3b8;
    z-index: 100;
    font-family: 'IBM Plex Mono', monospace;
}

/* Rang-Zahl */
.rang-text {
    font-size: 1.05rem;
    font-weight: 600;
    margin-top: 6px;
    text-align: center;
    color: #334155;
}

/* Metriken */
.metric-box {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.metric-box .val { font-size: 1.6rem; font-weight: 700; color: #0284c7; font-family: 'IBM Plex Mono', monospace; }
.metric-box .lbl { font-size: 0.8rem; color: #64748b; margin-top: 2px; }

/* Ampel-Badges */
.badge-a { background:#dcfce7; color:#166534; padding:2px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; }
.badge-b { background:#fef9c3; color:#854d0e; padding:2px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; }
.badge-c { background:#fee2e2; color:#991b1b; padding:2px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; }
.badge-renner { background:#dcfce7; color:#166534; padding:2px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; }
.badge-penner  { background:#fee2e2; color:#991b1b; padding:2px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; }
</style>

<div class="footer">© Philipp Bußmann</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Absatzcontrolling")
    st.markdown("---")
    modul = st.radio(
        "Modul wählen:",
        options=[
            "🏠 Startseite",
            "📦 ABC-Analyse",
            "🔷 Portfoliomatrix",
            "🔄 Produktlebenszyklus",
            "⚡ Renner-Penner-Liste",
            "💰 DB-Rechnung",
        ],
        label_visibility="collapsed"
    )
    st.markdown("---")
    if not PDF_AVAILABLE:
        st.warning("⚠️ PDF-Export: `pip install fpdf`")


# ═══════════════════════════════════════════════════════════
#  HELPER: PDF-GENERATOR (allgemein)
# ═══════════════════════════════════════════════════════════
def pdf_download_button(label: str, build_fn, filename: str):
    """Zeigt Download-Button wenn PDF verfügbar, sonst disabled-Button."""
    if PDF_AVAILABLE:
        pdf_bytes = build_fn()
        st.download_button(
            label=label,
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.button(f"📄 PDF Export (fpdf fehlt!)", disabled=True, use_container_width=True)


def pdf_output(pdf):
    try:
        return pdf.output(dest='S').encode('latin-1')
    except AttributeError:
        return pdf.output()


def safe_str(s):
    return str(s).encode('latin-1', 'replace').decode('latin-1')


# ═══════════════════════════════════════════════════════════
#  MODUL 0: STARTSEITE
# ═══════════════════════════════════════════════════════════
if modul == "🏠 Startseite":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Absatzcontrolling</h1>
        <p>Interaktive Lernapp · 5 Module · Mit PDF-Export</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>📦 ABC-Analyse</h4>
            <p>Artikel nach Umsatzbedeutung klassifizieren. Pareto-Diagramm, Klassengrenzen, Prüfung & PDF-Export.</p>
        </div>
        <div class="info-card">
            <h4>🔷 Portfoliomatrix</h4>
            <p>Produkte in die BCG-Matrix einordnen: Stars, Cash Cows, Question Marks & Poor Dogs.</p>
        </div>
        <div class="info-card">
            <h4>🔄 Produktlebenszyklus</h4>
            <p>Phasen des PLZ verstehen und Produkte den Phasen zuordnen.</p>
        </div>
    """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>⚡ Renner-Penner-Liste</h4>
            <p>Produkte nach Absatz und DB klassifizieren – Renner, Schläfer, Fragezeichen oder Penner.</p>
        </div>
        <div class="info-card">
            <h4>💰 DB-Rechnung</h4>
            <p>Deckungsbeitragsrechnung: DB I und DB II berechnen, Gewinnschwelle ermitteln.</p>
        </div>
        """, unsafe_allow_html=True)

    st.info("👈 Wähle ein Modul in der linken Seitenleiste.")


# ═══════════════════════════════════════════════════════════
#  MODUL 1: ABC-ANALYSE
# ═══════════════════════════════════════════════════════════
elif modul == "📦 ABC-Analyse":
    st.markdown("""
    <div class="main-header">
        <h1>📦 ABC-Analyse</h1>
        <p>Klassifiziere Artikel nach ihrer Umsatzbedeutung</p>
    </div>
    """, unsafe_allow_html=True)

    # Klassengrenzen
    with st.sidebar:
        st.markdown("#### ⚙️ Klassengrenzen")
        grenze_a = st.slider("A-Güter bis (%)", 0, 100, 80)
        grenze_b = st.slider("B-Güter bis (%)", grenze_a, 100, 95)
        grenze_c = st.slider("C-Güter bis (%)", grenze_b, 100, 100)

    # Session State
    if 'abc_liste' not in st.session_state:
        st.session_state.abc_liste = [
            {'id': i, 'Artikel': '', 'Menge': 0, 'Preis': 0.0} for i in range(1, 6)
        ]

    def abc_move(index, direction):
        l = st.session_state.abc_liste
        if direction == 'up' and index > 0:
            l[index], l[index-1] = l[index-1], l[index]
        elif direction == 'down' and index < len(l)-1:
            l[index], l[index+1] = l[index+1], l[index]
        st.session_state.abc_liste = l

    def abc_add():
        neue_id = max([x['id'] for x in st.session_state.abc_liste], default=0) + 1
        st.session_state.abc_liste.append({'id': neue_id, 'Artikel': '', 'Menge': 0, 'Preis': 0.0})

    COL = [0.5, 1.8, 0.9, 0.9, 1.1, 0.9, 0.9, 0.9, 1.0]
    headers_abc = ["Rang", "Artikel", "Menge", "Preis", "Umsatz (€)", "Anteil %", "Kum. %", "Klasse", "Aktion"]
    hdr = "<div class='table-header'>"
    for r, h in zip(COL, headers_abc):
        hdr += f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr += "</div>"
    st.markdown(hdr, unsafe_allow_html=True)

    current = st.session_state.abc_liste
    gesamt = sum(x['Menge']*x['Preis'] for x in current)
    kum = 0.0

    for i, item in enumerate(current):
        with st.container(border=True):
            cols = st.columns(COL, gap="small")
            with cols[0]:
                st.markdown(f"<div class='rang-text'>{i+1}.</div>", unsafe_allow_html=True)
            with cols[1]:
                item['Artikel'] = st.text_input("Artikel", value=item['Artikel'], key=f"abc_art_{item['id']}", label_visibility="collapsed")
            with cols[2]:
                item['Menge'] = st.number_input("Menge", value=int(item['Menge']), key=f"abc_men_{item['id']}", label_visibility="collapsed", step=1)
            with cols[3]:
                item['Preis'] = st.number_input("Preis", value=float(item['Preis']), key=f"abc_pre_{item['id']}", label_visibility="collapsed", step=0.5)

            umsatz = float(item['Menge']*item['Preis'])
            anteil = (umsatz/gesamt*100) if gesamt > 0 else 0.0
            kum += anteil
            klasse_vor = "A" if kum <= grenze_a+0.01 else ("B" if kum <= grenze_b+0.01 else "C")
            optionen = ["-","A","B","C"]

            with cols[4]:
                item['ei_ums'] = st.number_input("Umsatz", value=umsatz, key=f"abc_ums_{item['id']}", label_visibility="collapsed", step=1.0)
            with cols[5]:
                item['ei_ant'] = st.number_input("Anteil", value=anteil, key=f"abc_ant_{item['id']}", label_visibility="collapsed", step=0.01, format="%.2f", max_value=100.0)
            with cols[6]:
                item['ei_kum'] = st.number_input("Kum.", value=kum, key=f"abc_kum_{item['id']}", label_visibility="collapsed", step=0.01, format="%.2f", max_value=100.5)
            with cols[7]:
                item['ei_kl'] = st.selectbox("Kl.", options=optionen, index=optionen.index(klasse_vor), key=f"abc_kl_{item['id']}", label_visibility="collapsed")
            with cols[8]:
                cu, cd = st.columns(2)
                if cu.button("↑", key=f"abc_up_{item['id']}", disabled=(i==0)):
                    abc_move(i,'up'); st.rerun()
                if cd.button("↓", key=f"abc_dn_{item['id']}", disabled=(i==len(current)-1)):
                    abc_move(i,'down'); st.rerun()

    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    ca, cr, _ = st.columns([2,2,3])
    with ca:
        if st.button("➕ Artikel hinzufügen", use_container_width=True):
            abc_add(); st.rerun()
    with cr:
        if st.button("➖ Letzten entfernen", use_container_width=True, disabled=(len(current)<=1)):
            st.session_state.abc_liste.pop(); st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.subheader("📊 Live-Pareto-Diagramm")

    chart_data = pd.DataFrame({
        "Artikel": [f"{i+1}. {x['Artikel']}" for i,x in enumerate(current)],
        "Anteil (%)": [round(x.get('ei_ant',0),2) for x in current],
        "Kumuliert (%)": [round(x.get('ei_kum',0),2) for x in current],
    })
    base = alt.Chart(chart_data).encode(x=alt.X("Artikel:N", sort=None))
    bars = base.mark_bar(color="#93c5fd", size=40, opacity=0.8).encode(
        y=alt.Y("Anteil (%):Q", scale=alt.Scale(domain=[0,100])),
        tooltip=["Artikel:N", alt.Tooltip("Anteil (%):Q", format=".2f")]
    )
    line = base.mark_line(color="#0284c7", point=True, strokeWidth=3).encode(
        y=alt.Y("Kumuliert (%):Q"),
        tooltip=["Artikel:N", alt.Tooltip("Kumuliert (%):Q", format=".2f")]
    )
    st.altair_chart(alt.layer(bars, line).properties(height=380), use_container_width=True)

    st.markdown("<hr/>", unsafe_allow_html=True)
    cp, cd_btn = st.columns(2)

    with cp:
        if st.button("✅ Analyse prüfen", use_container_width=True, type="primary"):
            sol = sorted(current, key=lambda x: x['Menge']*x['Preis'], reverse=True)
            if any(current[j]['Menge']*current[j]['Preis'] < current[j+1]['Menge']*current[j+1]['Preis'] for j in range(len(current)-1)):
                st.error("❌ Reihenfolge falsch – höchster Umsatz muss auf Rang 1!")
            else:
                fehler = False
                kk = 0.0
                g = sum(x['Menge']*x['Preis'] for x in current)
                for i, item in enumerate(current):
                    u = item['Menge']*item['Preis']
                    a = (u/g*100) if g>0 else 0
                    kk += a
                    kl_soll = "A" if kk<=grenze_a+0.01 else ("B" if kk<=grenze_b+0.01 else "C")
                    if abs(item.get('ei_ums',0)-u)>0.5 or abs(item.get('ei_ant',0)-a)>0.05 or abs(item.get('ei_kum',0)-kk)>0.05:
                        st.error(f"❌ Rechenfehler bei Rang {i+1} ({item['Artikel']})")
                        fehler=True; break
                    if item.get('ei_kl','-') != kl_soll:
                        st.error(f"❌ Falsche Klasse bei Rang {i+1} ({item['Artikel']}). Erwartet: {kl_soll}")
                        fehler=True; break
                if not fehler:
                    st.success("✅ Alles korrekt! Perfekte Klassifizierung.")

    with cd_btn:
        def build_abc_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial",'B',16)
            pdf.cell(0,10,"Auswertung: ABC-Analyse",ln=True,align="C")
            pdf.ln(4)
            pdf.set_font("Arial",'B',9)
            pdf.set_fill_color(226,232,240)
            hds = ["Rang","Artikel","Menge","Preis","Umsatz","Ant.%","Kum.%","Kl."]
            ws  = [10,50,15,25,30,20,20,13]
            for h,w in zip(hds,ws): pdf.cell(w,8,h,border=1,align="C",fill=True)
            pdf.ln()
            pdf.set_font("Arial",'',9)
            g2 = sum(x['Menge']*x['Preis'] for x in current)
            kk2=0.0
            for i,item in enumerate(current):
                u=item['Menge']*item['Preis']; a=(u/g2*100) if g2>0 else 0; kk2+=a
                kl="A" if kk2<=grenze_a+0.01 else("B" if kk2<=grenze_b+0.01 else "C")
                pdf.cell(ws[0],8,f"{i+1}.",border=1,align="C")
                pdf.cell(ws[1],8,safe_str(item.get('Artikel','-') or '-'),border=1)
                pdf.cell(ws[2],8,str(item.get('Menge',0)),border=1,align="C")
                pdf.cell(ws[3],8,f"{item.get('Preis',0):.2f}",border=1,align="R")
                pdf.cell(ws[4],8,f"{item.get('ei_ums',u):.2f}",border=1,align="R")
                pdf.cell(ws[5],8,f"{item.get('ei_ant',a):.2f}%",border=1,align="R")
                pdf.cell(ws[6],8,f"{item.get('ei_kum',kk2):.2f}%",border=1,align="R")
                pdf.cell(ws[7],8,str(item.get('ei_kl',kl)),border=1,align="C")
                pdf.ln()
            pdf.ln(8)
            pdf.set_font("Arial",'B',11)
            pdf.cell(0,8,"Rechenweg (Musterloesung):",ln=True)
            pdf.set_font("Arial",'',10)
            pdf.cell(0,6,f"Gesamtumsatz = {g2:,.2f} EUR",ln=True)
            kk3=0.0
            for i,item in enumerate(current):
                u=item['Menge']*item['Preis']; a=(u/g2*100) if g2>0 else 0; ka=kk3; kk3+=a
                kl="A" if kk3<=grenze_a+0.01 else("B" if kk3<=grenze_b+0.01 else "C")
                pdf.set_font("Arial",'B',10); pdf.cell(0,6,f"Rang {i+1}: {safe_str(item.get('Artikel',f'Artikel {i+1}') or f'Artikel {i+1}')}",ln=True)
                pdf.set_font("Arial",'',10)
                pdf.cell(0,5,f"  Umsatz: {item['Menge']} * {item['Preis']:.2f} = {u:,.2f} EUR",ln=True)
                pdf.cell(0,5,f"  Anteil: {u:,.2f}/{g2:,.2f}*100 = {a:.2f}%",ln=True)
                pdf.cell(0,5,f"  Kumuliert: {ka:.2f}% + {a:.2f}% = {kk3:.2f}%  ->  Klasse {kl}",ln=True)
                pdf.ln(2)
            return pdf_output(pdf)
        pdf_download_button("📄 PDF speichern", build_abc_pdf, "ABC_Analyse.pdf")


# ═══════════════════════════════════════════════════════════
#  MODUL 2: PORTFOLIOMATRIX (BCG)
# ═══════════════════════════════════════════════════════════
elif modul == "🔷 Portfoliomatrix":
    st.markdown("""
    <div class="main-header">
        <h1>🔷 Portfoliomatrix (BCG)</h1>
        <p>Produkte nach Marktwachstum und relativem Marktanteil einordnen</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Theorie: Die vier Felder", expanded=False):
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            st.success("⭐ **Stars**\nHohes Wachstum, hoher Anteil → Investieren")
        with c2:
            st.warning("❓ **Question Marks**\nHohes Wachstum, niedriger Anteil → Selektieren")
        with c3:
            st.info("🐄 **Cash Cows**\nNiedriges Wachstum, hoher Anteil → Abschöpfen")
        with c4:
            st.error("🐕 **Poor Dogs**\nNiedriges Wachstum, niedriger Anteil → Desinvestieren")

    if 'bcg_liste' not in st.session_state:
        st.session_state.bcg_liste = [
            {'id': i, 'Produkt': '', 'Wachstum': 0.0, 'Anteil': 0.0, 'Umsatz': 0.0} for i in range(1,4)
        ]

    def bcg_add():
        nid = max([x['id'] for x in st.session_state.bcg_liste], default=0)+1
        st.session_state.bcg_liste.append({'id':nid,'Produkt':'','Wachstum':0.0,'Anteil':0.0,'Umsatz':0.0})

    with st.sidebar:
        st.markdown("#### ⚙️ Grenzwerte")
        wachstum_grenze = st.number_input("Wachstumsschwelle (%)", value=10.0, step=0.5, format="%.1f")
        anteil_grenze   = st.number_input("Marktanteils-Schwelle (rel.)", value=1.0, step=0.1, format="%.1f")

    st.subheader("📋 Produkteingabe")
    COL_BCG = [1.8, 1.2, 1.2, 1.2, 0.8]
    hdrs_bcg = ["Produkt", "Marktwachstum (%)", "Rel. Marktanteil", "Umsatz (€)", "Aktion"]
    hdr_b = "<div class='table-header'>"
    for r,h in zip(COL_BCG, hdrs_bcg):
        hdr_b += f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr_b += "</div>"
    st.markdown(hdr_b, unsafe_allow_html=True)

    bcg = st.session_state.bcg_liste
    for item in bcg:
        with st.container(border=True):
            cols = st.columns(COL_BCG, gap="small")
            with cols[0]: item['Produkt']  = st.text_input("Prod",  value=item['Produkt'],  key=f"bcg_p_{item['id']}", label_visibility="collapsed")
            with cols[1]: item['Wachstum'] = st.number_input("Wachs", value=float(item['Wachstum']), key=f"bcg_w_{item['id']}", label_visibility="collapsed", step=0.5, format="%.1f")
            with cols[2]: item['Anteil']   = st.number_input("Anteil", value=float(item['Anteil']),  key=f"bcg_a_{item['id']}", label_visibility="collapsed", step=0.1, format="%.2f")
            with cols[3]: item['Umsatz']   = st.number_input("Umsatz", value=float(item['Umsatz']),  key=f"bcg_u_{item['id']}", label_visibility="collapsed", step=100.0)
            with cols[4]:
                if st.button("🗑️", key=f"bcg_del_{item['id']}", disabled=(len(bcg)<=1)):
                    st.session_state.bcg_liste = [x for x in bcg if x['id']!=item['id']]; st.rerun()

    if st.button("➕ Produkt hinzufügen", use_container_width=False):
        bcg_add(); st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.subheader("🗺️ Portfolio-Matrix")

    def get_feld(w, a):
        if w >= wachstum_grenze and a >= anteil_grenze: return "⭐ Star"
        if w >= wachstum_grenze and a <  anteil_grenze: return "❓ Question Mark"
        if w <  wachstum_grenze and a >= anteil_grenze: return "🐄 Cash Cow"
        return "🐕 Poor Dog"

    # Vierfelder-Tabelle
    felder = {"⭐ Star":[],"❓ Question Mark":[],"🐄 Cash Cow":[],"🐕 Poor Dog":[]}
    for item in bcg:
        if item['Produkt']:
            felder[get_feld(item['Wachstum'], item['Anteil'])].append(item['Produkt'])

    col_q, col_s = st.columns(2)
    col_d, col_c = st.columns(2)

    def render_feld(container, name, color, items):
        with container:
            st.markdown(f"""
            <div style="background:{color};border-radius:10px;padding:1rem 1.2rem;min-height:120px;border:2px solid #e2e8f0;">
                <b style="font-size:1.1rem;">{name}</b><br/>
                {"<br/>".join([f"• {p}" for p in items]) if items else "<i style='color:#94a3b8;'>Keine Produkte</i>"}
            </div>""", unsafe_allow_html=True)

    render_feld(col_q, "❓ Question Marks", "#fefce8", felder["❓ Question Mark"])
    render_feld(col_s, "⭐ Stars",           "#f0fdf4", felder["⭐ Star"])
    render_feld(col_d, "🐕 Poor Dogs",       "#fff1f2", felder["🐕 Poor Dog"])
    render_feld(col_c, "🐄 Cash Cows",       "#eff6ff", felder["🐄 Cash Cow"])

    st.caption("← Niedriger Marktanteil | Hoher Marktanteil →  (oben = hohes Wachstum, unten = niedriges Wachstum)")

    # Scatter-Chart
    if any(item['Produkt'] for item in bcg):
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.subheader("📉 Diagramm")
        df_bcg = pd.DataFrame([{
            "Produkt": item['Produkt'] or f"P{i+1}",
            "Marktwachstum (%)": item['Wachstum'],
            "Rel. Marktanteil": item['Anteil'],
            "Umsatz (€)": max(item['Umsatz'], 1),
            "Feld": get_feld(item['Wachstum'], item['Anteil'])
        } for i,item in enumerate(bcg) if item['Produkt']])

        color_map = {"⭐ Star":"#22c55e","❓ Question Mark":"#f59e0b","🐄 Cash Cow":"#3b82f6","🐕 Poor Dog":"#ef4444"}
        scatter = alt.Chart(df_bcg).mark_circle(opacity=0.85).encode(
            x=alt.X("Rel. Marktanteil:Q", title="Relativer Marktanteil"),
            y=alt.Y("Marktwachstum (%):Q", title="Marktwachstum (%)"),
            size=alt.Size("Umsatz (€):Q", scale=alt.Scale(range=[200,2000])),
            color=alt.Color("Feld:N", scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values()))),
            tooltip=["Produkt:N","Marktwachstum (%):Q","Rel. Marktanteil:Q","Umsatz (€):Q","Feld:N"]
        )
        labels = alt.Chart(df_bcg).mark_text(dy=-12, fontWeight=600).encode(
            x="Rel. Marktanteil:Q", y="Marktwachstum (%):Q", text="Produkt:N"
        )
        st.altair_chart(alt.layer(scatter,labels).properties(height=400), use_container_width=True)

    # PDF
    st.markdown("<hr/>", unsafe_allow_html=True)
    def build_bcg_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial",'B',16)
        pdf.cell(0,10,"Portfoliomatrix (BCG-Analyse)",ln=True,align="C")
        pdf.ln(4)
        pdf.set_font("Arial",'B',9)
        pdf.set_fill_color(226,232,240)
        hs=["Produkt","Marktwachstum (%)","Rel. Marktanteil","Umsatz (EUR)","Feld"]
        ws=[55,40,40,40,40]
        for h,w in zip(hs,ws): pdf.cell(w,8,h,border=1,align="C",fill=True)
        pdf.ln()
        pdf.set_font("Arial",'',9)
        for item in bcg:
            feld = get_feld(item['Wachstum'],item['Anteil'])
            feld_clean = feld.replace("⭐","Star").replace("❓","?").replace("🐄","Cash Cow").replace("🐕","Poor Dog")
            pdf.cell(ws[0],8,safe_str(item['Produkt'] or '-'),border=1)
            pdf.cell(ws[1],8,f"{item['Wachstum']:.1f}%",border=1,align="R")
            pdf.cell(ws[2],8,f"{item['Anteil']:.2f}",border=1,align="R")
            pdf.cell(ws[3],8,f"{item['Umsatz']:,.2f}",border=1,align="R")
            pdf.cell(ws[4],8,safe_str(feld_clean),border=1,align="C")
            pdf.ln()
        return pdf_output(pdf)
    pdf_download_button("📄 Portfolio als PDF", build_bcg_pdf, "Portfoliomatrix.pdf")


# ═══════════════════════════════════════════════════════════
#  MODUL 3: PRODUKTLEBENSZYKLUS
# ═══════════════════════════════════════════════════════════
elif modul == "🔄 Produktlebenszyklus":
    st.markdown("""
    <div class="main-header">
        <h1>🔄 Produktlebenszyklus</h1>
        <p>Phasen des PLZ verstehen und Produkte zuordnen</p>
    </div>
    """, unsafe_allow_html=True)

    PHASEN = ["Einführung", "Wachstum", "Reife", "Sättigung", "Degeneration"]
    PHASEN_INFO = {
        "Einführung":   {"farbe":"#e0f2fe","icon":"🌱","merkmale":"Niedriger Umsatz, hohe Kosten, Verlust, wenig Konkurrenz","strategie":"Markterschließung, Werbung, Skimming oder Penetrationsstrategie"},
        "Wachstum":     {"farbe":"#dcfce7","icon":"📈","merkmale":"Umsatz steigt stark, Gewinne steigen, mehr Wettbewerber","strategie":"Marktdurchdringung, Qualitätsverbesserung, Preissenkung"},
        "Reife":        {"farbe":"#fef9c3","icon":"🏆","merkmale":"Umsatz auf Höchststand, Gewinne beginnen zu sinken","strategie":"Produktdifferenzierung, neue Zielgruppen erschließen"},
        "Sättigung":    {"farbe":"#fed7aa","icon":"📊","merkmale":"Umsatz stagniert, starker Preiswettbewerb, Gewinne sinken","strategie":"Kostenreduktion, Relaunch, Nischenstrategie"},
        "Degeneration": {"farbe":"#fee2e2","icon":"📉","merkmale":"Umsatz und Gewinn fallen stark, Marktaustritt nahe","strategie":"Eliminierung oder Nischenpflege, Ressourcen umschichten"},
    }

    # PLZ-Kurve
    st.subheader("📈 PLZ-Kurve")
    x = list(range(0, 51))
    def plz_umsatz(t):
        if t < 10: return max(0, -5 + 8*t)
        if t < 22: return 75 + 20*(t-10)/12
        if t < 30: return 95 - 5*(t-22)/8
        if t < 40: return 90 - 25*(t-30)/10
        return max(0, 65 - 25*(t-40)/10)

    df_plz = pd.DataFrame({
        "Zeit": x,
        "Umsatz": [plz_umsatz(t) for t in x],
        "Phase": [PHASEN[0] if t<10 else PHASEN[1] if t<22 else PHASEN[2] if t<30 else PHASEN[3] if t<40 else PHASEN[4] for t in x]
    })
    farben_map = {p:PHASEN_INFO[p]["farbe"].replace("#","") for p in PHASEN}
    line_chart = alt.Chart(df_plz).mark_area(opacity=0.3).encode(
        x=alt.X("Zeit:Q", title="Zeitachse"),
        y=alt.Y("Umsatz:Q", title="Umsatz / Gewinn (schematisch)"),
        color=alt.Color("Phase:N", scale=alt.Scale(
            domain=PHASEN,
            range=["#38bdf8","#34d399","#fbbf24","#fb923c","#f87171"]
        )),
        tooltip=["Phase:N","Umsatz:Q"]
    )
    line2 = alt.Chart(df_plz).mark_line(strokeWidth=3, color="#0284c7").encode(
        x="Zeit:Q", y="Umsatz:Q"
    )
    st.altair_chart(alt.layer(line_chart, line2).properties(height=320), use_container_width=True)

    # Phasen-Info-Karten
    st.subheader("📋 Phasen im Detail")
    cols = st.columns(5)
    for i, (phase, info) in enumerate(PHASEN_INFO.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="background:{info['farbe']};border-radius:10px;padding:1rem;min-height:200px;border:1px solid #e2e8f0;">
                <div style="font-size:1.5rem;text-align:center;">{info['icon']}</div>
                <b style="font-size:0.95rem;">{phase}</b>
                <p style="font-size:0.78rem;color:#334155;margin-top:6px;"><b>Merkmale:</b><br/>{info['merkmale']}</p>
                <p style="font-size:0.78rem;color:#334155;"><b>Strategie:</b><br/>{info['strategie']}</p>
            </div>""", unsafe_allow_html=True)

    # Produkt-Zuordnung
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.subheader("🏷️ Produkte den Phasen zuordnen")

    if 'plz_produkte' not in st.session_state:
        st.session_state.plz_produkte = [{'id':i,'Produkt':'','Phase_eingabe':'-','Phase_richtig':PHASEN[0]} for i in range(1,4)]

    def plz_add():
        nid = max([x['id'] for x in st.session_state.plz_produkte], default=0)+1
        st.session_state.plz_produkte.append({'id':nid,'Produkt':'','Phase_eingabe':'-','Phase_richtig':PHASEN[0]})

    plz_prod = st.session_state.plz_produkte
    COL_PLZ = [2.0, 1.5, 1.5, 0.8]
    hdr_plz = "<div class='table-header'>"
    for r,h in zip(COL_PLZ,["Produktname","Meine Phase (Schüler)","Richtige Phase (Lehrer)","Aktion"]):
        hdr_plz += f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr_plz += "</div>"
    st.markdown(hdr_plz, unsafe_allow_html=True)

    optionen_plz = ["-"] + PHASEN
    for item in plz_prod:
        with st.container(border=True):
            cols = st.columns(COL_PLZ, gap="small")
            with cols[0]: item['Produkt'] = st.text_input("P", value=item['Produkt'], key=f"plz_p_{item['id']}", label_visibility="collapsed")
            with cols[1]: item['Phase_eingabe'] = st.selectbox("E", options=optionen_plz, index=optionen_plz.index(item['Phase_eingabe']) if item['Phase_eingabe'] in optionen_plz else 0, key=f"plz_e_{item['id']}", label_visibility="collapsed")
            with cols[2]: item['Phase_richtig'] = st.selectbox("R", options=PHASEN, index=PHASEN.index(item['Phase_richtig']) if item['Phase_richtig'] in PHASEN else 0, key=f"plz_r_{item['id']}", label_visibility="collapsed")
            with cols[3]:
                if st.button("🗑️", key=f"plz_del_{item['id']}", disabled=(len(plz_prod)<=1)):
                    st.session_state.plz_produkte = [x for x in plz_prod if x['id']!=item['id']]; st.rerun()

    if st.button("➕ Produkt hinzufügen", key="plz_add"):
        plz_add(); st.rerun()

    col_pcheck, col_ppdf = st.columns(2)
    with col_pcheck:
        if st.button("✅ Zuordnung prüfen", use_container_width=True, type="primary"):
            fehler = False
            for item in plz_prod:
                if not item['Produkt']: continue
                if item['Phase_eingabe'] == '-':
                    st.warning(f"⚠️ {item['Produkt']}: Keine Phase gewählt.")
                    fehler = True
                elif item['Phase_eingabe'] != item['Phase_richtig']:
                    st.error(f"❌ {item['Produkt']}: Eingabe '{item['Phase_eingabe']}' ist falsch. Richtig: '{item['Phase_richtig']}'")
                    fehler = True
            if not fehler:
                st.success("✅ Alle Zuordnungen korrekt!")

    with col_ppdf:
        def build_plz_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial",'B',16)
            pdf.cell(0,10,"Produktlebenszyklus – Auswertung",ln=True,align="C")
            pdf.ln(4)
            pdf.set_font("Arial",'B',10)
            pdf.cell(0,8,"Phasenuebersicht:",ln=True)
            pdf.set_font("Arial",'',9)
            for phase, info in PHASEN_INFO.items():
                pdf.set_font("Arial",'B',9); pdf.cell(0,6,safe_str(phase),ln=True)
                pdf.set_font("Arial",'',9)
                pdf.cell(0,5,f"  Merkmale: {safe_str(info['merkmale'])}",ln=True)
                pdf.cell(0,5,f"  Strategie: {safe_str(info['strategie'])}",ln=True)
                pdf.ln(2)
            if any(x['Produkt'] for x in plz_prod):
                pdf.ln(4)
                pdf.set_font("Arial",'B',10); pdf.cell(0,8,"Produktzuordnung:",ln=True)
                pdf.set_font("Arial",'B',9)
                pdf.set_fill_color(226,232,240)
                for h,w in zip(["Produkt","Eingabe (SuS)","Richtige Phase","Status"],[65,40,45,30]):
                    pdf.cell(w,8,h,border=1,align="C",fill=True)
                pdf.ln()
                pdf.set_font("Arial",'',9)
                for item in plz_prod:
                    if not item['Produkt']: continue
                    status = "OK" if item['Phase_eingabe']==item['Phase_richtig'] else "Falsch"
                    pdf.cell(65,8,safe_str(item['Produkt']),border=1)
                    pdf.cell(40,8,safe_str(item['Phase_eingabe']),border=1,align="C")
                    pdf.cell(45,8,safe_str(item['Phase_richtig']),border=1,align="C")
                    pdf.cell(30,8,status,border=1,align="C")
                    pdf.ln()
            return pdf_output(pdf)
        pdf_download_button("📄 PLZ als PDF", build_plz_pdf, "Produktlebenszyklus.pdf")


# ═══════════════════════════════════════════════════════════
#  MODUL 4: RENNER-PENNER-LISTE
# ═══════════════════════════════════════════════════════════
elif modul == "⚡ Renner-Penner-Liste":
    st.markdown("""
    <div class="main-header">
        <h1>⚡ Renner-Penner-Liste</h1>
        <p>Produkte nach Absatz und Deckungsbeitrag klassifizieren</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Theorie", expanded=False):
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.success("🏆 **Renner**\nHoher Absatz + Hoher DB")
        with c2: st.warning("😴 **Schläfer**\nNiedriger Absatz + Hoher DB → reaktivieren")
        with c3: st.info("❓ **Fragezeichen**\nHoher Absatz + Niedriger DB → Kosten senken")
        with c4: st.error("💀 **Penner**\nNiedriger Absatz + Niedriger DB → eliminieren")

    with st.sidebar:
        st.markdown("#### ⚙️ Schwellenwerte")
        absatz_grenze = st.number_input("Absatz-Schwelle (Stk.)", value=100, step=10)
        db_grenze     = st.number_input("DB-Schwelle (€/Stk.)", value=10.0, step=1.0, format="%.2f")

    if 'rp_liste' not in st.session_state:
        st.session_state.rp_liste = [
            {'id':i,'Produkt':'','Absatz':0,'DB':0.0} for i in range(1,5)
        ]

    def rp_add():
        nid = max([x['id'] for x in st.session_state.rp_liste],default=0)+1
        st.session_state.rp_liste.append({'id':nid,'Produkt':'','Absatz':0,'DB':0.0})

    def get_rp_typ(absatz, db):
        h_a = absatz >= absatz_grenze
        h_d = db >= db_grenze
        if h_a and h_d:  return "🏆 Renner"
        if not h_a and h_d: return "😴 Schläfer"
        if h_a and not h_d: return "❓ Fragezeichen"
        return "💀 Penner"

    rp = st.session_state.rp_liste
    COL_RP = [1.8, 1.0, 1.0, 1.2, 1.0, 0.8]
    hdr_rp = "<div class='table-header'>"
    for r,h in zip(COL_RP,["Produkt","Absatz (Stk.)","DB (€/Stk.)","Typ (Eingabe)","Richtiger Typ","Aktion"]):
        hdr_rp += f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr_rp += "</div>"
    st.markdown(hdr_rp, unsafe_allow_html=True)

    typen_opt = ["-","🏆 Renner","😴 Schläfer","❓ Fragezeichen","💀 Penner"]
    for item in rp:
        with st.container(border=True):
            cols = st.columns(COL_RP, gap="small")
            with cols[0]: item['Produkt'] = st.text_input("P", value=item['Produkt'], key=f"rp_p_{item['id']}", label_visibility="collapsed")
            with cols[1]: item['Absatz']  = st.number_input("A", value=int(item['Absatz']),  key=f"rp_a_{item['id']}", label_visibility="collapsed", step=10)
            with cols[2]: item['DB']      = st.number_input("D", value=float(item['DB']),   key=f"rp_d_{item['id']}", label_visibility="collapsed", step=0.5, format="%.2f")
            typ_richtig = get_rp_typ(item['Absatz'], item['DB'])
            with cols[3]:
                item['typ_eingabe'] = st.selectbox("TE", options=typen_opt,
                    index=typen_opt.index(item.get('typ_eingabe','-')) if item.get('typ_eingabe','-') in typen_opt else 0,
                    key=f"rp_te_{item['id']}", label_visibility="collapsed")
            with cols[4]:
                st.markdown(f"<div style='padding-top:8px;text-align:center;font-weight:600;font-size:0.85rem;'>{typ_richtig}</div>", unsafe_allow_html=True)
            with cols[5]:
                if st.button("🗑️", key=f"rp_del_{item['id']}", disabled=(len(rp)<=1)):
                    st.session_state.rp_liste = [x for x in rp if x['id']!=item['id']]; st.rerun()

    if st.button("➕ Produkt hinzufügen", key="rp_add"):
        rp_add(); st.rerun()

    # Auswertungsmatrix
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.subheader("📊 Matrix-Auswertung")
    felder_rp = {"🏆 Renner":[],"😴 Schläfer":[],"❓ Fragezeichen":[],"💀 Penner":[]}
    for item in rp:
        if item['Produkt']:
            felder_rp[get_rp_typ(item['Absatz'],item['DB'])].append(item['Produkt'])

    cq2,cs2 = st.columns(2)
    cd2,cc2 = st.columns(2)

    def rp_box(container, name, color, items):
        with container:
            st.markdown(f"""
            <div style="background:{color};border-radius:10px;padding:1rem 1.2rem;min-height:100px;border:1px solid #e2e8f0;">
                <b style="font-size:1.05rem;">{name}</b><br/>
                {"<br/>".join([f"• {p}" for p in items]) if items else "<i style='color:#94a3b8;'>Keine</i>"}
            </div>""", unsafe_allow_html=True)

    rp_box(cq2, "😴 Schläfer",    "#fefce8", felder_rp["😴 Schläfer"])
    rp_box(cs2, "🏆 Renner",      "#f0fdf4", felder_rp["🏆 Renner"])
    rp_box(cd2, "💀 Penner",      "#fff1f2", felder_rp["💀 Penner"])
    rp_box(cc2, "❓ Fragezeichen","#eff6ff", felder_rp["❓ Fragezeichen"])
    st.caption("← Niedriger Absatz | Hoher Absatz →  (oben = hoher DB, unten = niedriger DB)")

    col_rcheck, col_rpdf = st.columns(2)
    with col_rcheck:
        if st.button("✅ Eingaben prüfen", use_container_width=True, type="primary"):
            fehler = False
            for item in rp:
                if not item['Produkt']: continue
                soll = get_rp_typ(item['Absatz'],item['DB'])
                if item.get('typ_eingabe','-') == '-':
                    st.warning(f"⚠️ {item['Produkt']}: Kein Typ gewählt.")
                    fehler = True
                elif item.get('typ_eingabe') != soll:
                    st.error(f"❌ {item['Produkt']}: '{item['typ_eingabe']}' falsch → Richtig: {soll}")
                    fehler = True
            if not fehler:
                st.success("✅ Alle Klassifizierungen korrekt!")

    with col_rpdf:
        def build_rp_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial",'B',16)
            pdf.cell(0,10,"Renner-Penner-Liste – Auswertung",ln=True,align="C")
            pdf.ln(4)
            pdf.set_font("Arial",'',10)
            pdf.cell(0,6,f"Schwellenwerte: Absatz >= {absatz_grenze} Stk. | DB >= {db_grenze:.2f} EUR/Stk.",ln=True)
            pdf.ln(4)
            pdf.set_font("Arial",'B',9); pdf.set_fill_color(226,232,240)
            for h,w in zip(["Produkt","Absatz (Stk.)","DB (EUR/Stk.)","Eingabe (SuS)","Richtiger Typ"],[55,30,35,45,45]):
                pdf.cell(w,8,h,border=1,align="C",fill=True)
            pdf.ln()
            pdf.set_font("Arial",'',9)
            for item in rp:
                if not item['Produkt']: continue
                soll = get_rp_typ(item['Absatz'],item['DB'])
                soll_c = soll.replace("🏆","").replace("😴","").replace("❓","").replace("💀","").strip()
                ei_c   = item.get('typ_eingabe','-').replace("🏆","").replace("😴","").replace("❓","").replace("💀","").strip()
                pdf.cell(55,8,safe_str(item['Produkt']),border=1)
                pdf.cell(30,8,str(item['Absatz']),border=1,align="R")
                pdf.cell(35,8,f"{item['DB']:.2f}",border=1,align="R")
                pdf.cell(45,8,safe_str(ei_c),border=1,align="C")
                pdf.cell(45,8,safe_str(soll_c),border=1,align="C")
                pdf.ln()
            return pdf_output(pdf)
        pdf_download_button("📄 Liste als PDF", build_rp_pdf, "Renner_Penner_Liste.pdf")


# ═══════════════════════════════════════════════════════════
#  MODUL 5: DB-RECHNUNG
# ═══════════════════════════════════════════════════════════
elif modul == "💰 DB-Rechnung":
    st.markdown("""
    <div class="main-header">
        <h1>💰 Deckungsbeitragsrechnung</h1>
        <p>DB I und DB II berechnen, Gewinnschwelle ermitteln</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Theorie: Deckungsbeitragsrechnung", expanded=False):
        st.markdown("""
        | Formel | Beschreibung |
        |---|---|
        | **DB I** = Erlös − variable Kosten | Deckungsbeitrag pro Stück |
        | **DB II** = DB I × Absatzmenge | Gesamter Deckungsbeitrag |
        | **Gewinn** = DB II − Fixkosten | Unternehmensergebnis |
        | **BEP (Menge)** = Fixkosten ÷ DB I | Gewinnschwelle in Stück |
        | **BEP (Umsatz)** = BEP × Preis | Gewinnschwelle in € |
        """)

    if 'db_produkte' not in st.session_state:
        st.session_state.db_produkte = [
            {'id':i,'Produkt':'','Preis':0.0,'var_k':0.0,'Menge':0,
             'ei_db1':0.0,'ei_db2':0.0,'ei_bep':0.0} for i in range(1,4)
        ]

    with st.sidebar:
        st.markdown("#### ⚙️ Fixkosten")
        fixkosten = st.number_input("Fixkosten gesamt (€)", value=5000.0, step=100.0, format="%.2f")

    def db_add():
        nid = max([x['id'] for x in st.session_state.db_produkte],default=0)+1
        st.session_state.db_produkte.append({'id':nid,'Produkt':'','Preis':0.0,'var_k':0.0,'Menge':0,'ei_db1':0.0,'ei_db2':0.0,'ei_bep':0.0})

    db_prod = st.session_state.db_produkte
    COL_DB = [1.5, 1.0, 1.0, 1.0, 1.0, 1.1, 1.1, 0.7]
    hdrs_db = ["Produkt","Preis (€)","Var.K. (€)","Menge","DB I (€)","DB II (€)","BEP (Stk.)","Akt."]

    hdr_db = "<div class='table-header'>"
    for r,h in zip(COL_DB, hdrs_db):
        hdr_db += f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr_db += "</div>"
    st.markdown(hdr_db, unsafe_allow_html=True)

    gesamtdb2 = 0.0
    for item in db_prod:
        db1_soll = item['Preis'] - item['var_k']
        db2_soll = db1_soll * item['Menge']
        bep_soll = (fixkosten / db1_soll) if db1_soll > 0 else 0
        gesamtdb2 += db2_soll

        with st.container(border=True):
            cols = st.columns(COL_DB, gap="small")
            with cols[0]: item['Produkt'] = st.text_input("P", value=item['Produkt'], key=f"db_p_{item['id']}", label_visibility="collapsed")
            with cols[1]: item['Preis']   = st.number_input("Pr", value=float(item['Preis']), key=f"db_pr_{item['id']}", label_visibility="collapsed", step=0.5, format="%.2f")
            with cols[2]: item['var_k']   = st.number_input("Vk", value=float(item['var_k']), key=f"db_vk_{item['id']}", label_visibility="collapsed", step=0.5, format="%.2f")
            with cols[3]: item['Menge']   = st.number_input("Me", value=int(item['Menge']),  key=f"db_me_{item['id']}", label_visibility="collapsed", step=10)
            with cols[4]: item['ei_db1']  = st.number_input("D1", value=float(item['ei_db1']), key=f"db_d1_{item['id']}", label_visibility="collapsed", step=0.5, format="%.2f")
            with cols[5]: item['ei_db2']  = st.number_input("D2", value=float(item['ei_db2']), key=f"db_d2_{item['id']}", label_visibility="collapsed", step=10.0, format="%.2f")
            with cols[6]: item['ei_bep']  = st.number_input("BP", value=float(item['ei_bep']), key=f"db_bp_{item['id']}", label_visibility="collapsed", step=1.0, format="%.0f")
            with cols[7]:
                if st.button("🗑️", key=f"db_del_{item['id']}", disabled=(len(db_prod)<=1)):
                    st.session_state.db_produkte = [x for x in db_prod if x['id']!=item['id']]; st.rerun()

    if st.button("➕ Produkt hinzufügen", key="db_add"):
        db_add(); st.rerun()

    # Gesamtübersicht
    st.markdown("<hr/>", unsafe_allow_html=True)
    gewinn = gesamtdb2 - fixkosten
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class='metric-box'><div class='val'>{gesamtdb2:,.2f} €</div><div class='lbl'>Gesamt DB II</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='metric-box'><div class='val'>{fixkosten:,.2f} €</div><div class='lbl'>Fixkosten</div></div>""", unsafe_allow_html=True)
    with c3:
        farbe = "#f0fdf4" if gewinn >= 0 else "#fff1f2"
        st.markdown(f"""<div class='metric-box' style='background:{farbe};'><div class='val'>{gewinn:+,.2f} €</div><div class='lbl'>Gewinn / Verlust</div></div>""", unsafe_allow_html=True)

    col_dbcheck, col_dbpdf = st.columns(2)
    with col_dbcheck:
        if st.button("✅ Rechnung prüfen", use_container_width=True, type="primary"):
            fehler = False
            for item in db_prod:
                if not item['Produkt']: continue
                db1s = item['Preis'] - item['var_k']
                db2s = db1s * item['Menge']
                beps = (fixkosten/db1s) if db1s > 0 else 0
                if abs(item['ei_db1']-db1s) > 0.05:
                    st.error(f"❌ {item['Produkt']}: DB I falsch (eingegeben: {item['ei_db1']:.2f} | richtig: {db1s:.2f})"); fehler=True; break
                if abs(item['ei_db2']-db2s) > 0.5:
                    st.error(f"❌ {item['Produkt']}: DB II falsch (eingegeben: {item['ei_db2']:.2f} | richtig: {db2s:.2f})"); fehler=True; break
                if db1s > 0 and abs(item['ei_bep']-beps) > 1:
                    st.error(f"❌ {item['Produkt']}: BEP falsch (eingegeben: {item['ei_bep']:.0f} | richtig: {beps:.0f})"); fehler=True; break
            if not fehler:
                st.success("✅ Alle Berechnungen korrekt!")

    with col_dbpdf:
        def build_db_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial",'B',16)
            pdf.cell(0,10,"Deckungsbeitragsrechnung – Auswertung",ln=True,align="C")
            pdf.ln(4)
            pdf.set_font("Arial",'B',9); pdf.set_fill_color(226,232,240)
            hs=["Produkt","Preis","Var.K.","Menge","DB I","DB II","BEP (Stk.)"]
            ws=[50,22,22,20,25,28,25]
            for h,w in zip(hs,ws): pdf.cell(w,8,h,border=1,align="C",fill=True)
            pdf.ln()
            pdf.set_font("Arial",'',9)
            g_db2=0
            for item in db_prod:
                if not item['Produkt']: continue
                db1=item['Preis']-item['var_k']
                db2=db1*item['Menge']
                bep=(fixkosten/db1) if db1>0 else 0
                g_db2+=db2
                pdf.cell(ws[0],8,safe_str(item['Produkt']),border=1)
                pdf.cell(ws[1],8,f"{item['Preis']:.2f}",border=1,align="R")
                pdf.cell(ws[2],8,f"{item['var_k']:.2f}",border=1,align="R")
                pdf.cell(ws[3],8,str(item['Menge']),border=1,align="R")
                pdf.cell(ws[4],8,f"{item['ei_db1']:.2f}",border=1,align="R")
                pdf.cell(ws[5],8,f"{item['ei_db2']:.2f}",border=1,align="R")
                pdf.cell(ws[6],8,f"{item['ei_bep']:.0f}",border=1,align="R")
                pdf.ln()
            pdf.ln(6)
            pdf.set_font("Arial",'B',10); pdf.cell(0,7,"Gesamtergebnis:",ln=True)
            pdf.set_font("Arial",'',10)
            g = g_db2 - fixkosten
            pdf.cell(0,6,f"Gesamt DB II = {g_db2:,.2f} EUR",ln=True)
            pdf.cell(0,6,f"Fixkosten   = {fixkosten:,.2f} EUR",ln=True)
            pdf.cell(0,6,f"Gewinn/Verlust = {g:+,.2f} EUR",ln=True)
            pdf.ln(6)
            pdf.set_font("Arial",'B',10); pdf.cell(0,7,"Rechenwege (Musterloesung):",ln=True)
            pdf.set_font("Arial",'',9)
            for item in db_prod:
                if not item['Produkt']: continue
                db1=item['Preis']-item['var_k']
                db2=db1*item['Menge']
                bep=(fixkosten/db1) if db1>0 else 0
                pdf.set_font("Arial",'B',9); pdf.cell(0,6,safe_str(item['Produkt']),ln=True)
                pdf.set_font("Arial",'',9)
                pdf.cell(0,5,f"  DB I  = {item['Preis']:.2f} - {item['var_k']:.2f} = {db1:.2f} EUR",ln=True)
                pdf.cell(0,5,f"  DB II = {db1:.2f} * {item['Menge']} = {db2:,.2f} EUR",ln=True)
                if db1>0: pdf.cell(0,5,f"  BEP  = {fixkosten:,.2f} / {db1:.2f} = {bep:.1f} Stk.",ln=True)
                pdf.ln(2)
            return pdf_output(pdf)
        pdf_download_button("📄 DB-Rechnung als PDF", build_db_pdf, "DB_Rechnung.pdf")
