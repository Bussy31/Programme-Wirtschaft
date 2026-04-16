import streamlit as st
import pandas as pd
import altair as alt
import json

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

import streamlit.components.v1 as components

st.set_page_config(
    page_title="Absatzcontrolling – AgriGeno eG",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

STORAGE_KEY = "absatzcontrolling_v4"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 1rem !important; padding: 8px 0 !important; }
[data-testid="stSidebar"] hr { border-color: #334155 !important; }

/* ── Sidebar Buttons ── */
[data-testid="stSidebar"] .stButton > button {
    background: #0369a1 !important;
    color: #ffffff !important;
    border: 1px solid #0284c7 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #0284c7 !important;
    border-color: #38bdf8 !important;
}
[data-testid="stSidebar"] .stDownloadButton > button {
    background: #075985 !important;
    color: #ffffff !important;
    border: 1px solid #0369a1 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
[data-testid="stSidebar"] .stDownloadButton > button:hover {
    background: #0369a1 !important;
}
[data-testid="stSidebar"] .stFileUploader label { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] {
    background: #1e3a5f !important;
    border: 1px dashed #3b82f6 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] button {
    background: #0369a1 !important;
    color: white !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] span {
    color: #94a3b8 !important;
    font-size: 0.8rem !important;
}

.main-header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); color: white;
    padding: 2rem 2.5rem; border-radius: 12px; margin-bottom: 2rem; border-left: 5px solid #38bdf8; }
.main-header h1 { margin: 0; font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; }
.main-header p  { margin: 0.4rem 0 0; color: #94a3b8; font-size: 1rem; }
.info-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 1.2rem 1.5rem; margin-bottom: 1rem; }
.info-card h4 { margin: 0 0 0.4rem; color: #0f172a; font-size: 1rem; font-weight: 600; }
.info-card p  { margin: 0; color: #475569; font-size: 0.9rem; }
button[kind="primary"] { background: #0284c7 !important; border-radius: 8px !important; font-weight: 600 !important; }
.table-header { display: flex; gap: 0.5rem; background: #e2e8f0; padding: 10px 15px;
    border-radius: 8px; margin-bottom: 8px; border: 1px solid #cbd5e1; }
.table-header div { text-align: center; font-weight: 700; color: #334155; font-size: 0.95rem; }
.footer { position: fixed; bottom: 10px; right: 15px; font-size: 11px; color: #94a3b8;
    z-index: 100; font-family: 'IBM Plex Mono', monospace; }
.rang-text { font-size: 1.05rem; font-weight: 600; margin-top: 6px; text-align: center; color: #334155; }
.metric-box { background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 10px;
    padding: 1rem 1.2rem; text-align: center; }
.metric-box .val { font-size: 1.6rem; font-weight: 700; color: #0284c7; font-family: 'IBM Plex Mono', monospace; }
.metric-box .lbl { font-size: 0.8rem; color: #64748b; margin-top: 2px; }
.hint-box { background:#f0f9ff; border:1px solid #bae6fd; border-radius:8px;
    padding:0.8rem 1rem; margin-bottom:1rem; font-size:0.9rem; color:#0369a1; }
.bcg-feld { border-radius:10px; padding:1rem 1.2rem; min-height:110px;
    border:2px solid #e2e8f0; margin-bottom:4px; }
.bcg-feld b { font-size:1rem; }
</style>
<div class="footer">© Philipp Bußmann</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TESTDATEN (AgriGeno eG – Lernsituation)
# ─────────────────────────────────────────────
TESTDATEN_STAMM = [
    {'id':1, 'name':'301 - Rinder-Ohrmarken (Blanko)',       'absatz':45000, 'preis':0.65,    'liegezeit':'6 Wochen'},
    {'id':2, 'name':'302 - Arbeitshandschuhe "Grip"',        'absatz':18000, 'preis':2.10,    'liegezeit':'5 Wochen'},
    {'id':3, 'name':'103 - Spezial-Bio-Saatgutmischung',     'absatz':3000,  'preis':120.00,  'liegezeit':'1 Woche'},
    {'id':4, 'name':'104 - NPK-Standarddünger (1t BigBag)',  'absatz':1500,  'preis':450.00,  'liegezeit':'2 Wochen'},
    {'id':5, 'name':'203 - Kälber-Tränkeeimer',              'absatz':1000,  'preis':7.00,    'liegezeit':'3 Wochen'},
    {'id':6, 'name':'204 - Kälber-Iglu "Premium"',           'absatz':600,   'preis':350.00,  'liegezeit':'4 Wochen'},
    {'id':7, 'name':'403 - Konventionelles Pressengarn',     'absatz':120,   'preis':45.00,   'liegezeit':'18 Monate'},
    {'id':8, 'name':'105 - Agrar-Drohne (Rehkitzrettung)',   'absatz':10,    'preis':8900.00, 'liegezeit':'3 Wochen'},
]

TESTDATEN_PLZ = [
    {'id':1, 'Produkt':'NPK-Standarddünger (BigBag)',        'Phase_eingabe':'-'},
    {'id':2, 'Produkt':'Agrar-Drohne (Rehkitzrettung)',      'Phase_eingabe':'-'},
    {'id':3, 'Produkt':'Spezial-Bio-Saatgutmischung',        'Phase_eingabe':'-'},
    {'id':4, 'Produkt':'Konventionelles Pressengarn (Rolle)','Phase_eingabe':'-'},
]

TESTDATEN_BCG = [
    {'id':1, 'Produkt':'NPK-Standarddünger (BigBag)',        'wachstum_text':'', 'anteil_text':'', 'ei_feld':'-'},
    {'id':2, 'Produkt':'Agrar-Drohne (Rehkitzrettung)',      'wachstum_text':'', 'anteil_text':'', 'ei_feld':'-'},
    {'id':3, 'Produkt':'Spezial-Bio-Saatgutmischung',        'wachstum_text':'', 'anteil_text':'', 'ei_feld':'-'},
    {'id':4, 'Produkt':'Konventionelles Pressengarn (Rolle)','wachstum_text':'', 'anteil_text':'', 'ei_feld':'-'},
]

TESTDATEN_ABC = [
    {'id':1,'Artikel':'301 - Rinder-Ohrmarken (Blanko)',     'Menge':45000,'Preis':0.65,   'ei_ums':0.0,'ei_ant':0.0,'ei_kum':0.0,'ei_kl':'-'},
    {'id':2,'Artikel':'302 - Arbeitshandschuhe "Grip"',      'Menge':18000,'Preis':2.10,   'ei_ums':0.0,'ei_ant':0.0,'ei_kum':0.0,'ei_kl':'-'},
    {'id':3,'Artikel':'103 - Spezial-Bio-Saatgutmischung',   'Menge':3000, 'Preis':120.00, 'ei_ums':0.0,'ei_ant':0.0,'ei_kum':0.0,'ei_kl':'-'},
    {'id':4,'Artikel':'104 - NPK-Standarddünger (1t BigBag)','Menge':1500, 'Preis':450.00, 'ei_ums':0.0,'ei_ant':0.0,'ei_kum':0.0,'ei_kl':'-'},
    {'id':5,'Artikel':'203 - Kälber-Tränkeeimer',            'Menge':1000, 'Preis':7.00,   'ei_ums':0.0,'ei_ant':0.0,'ei_kum':0.0,'ei_kl':'-'},
    {'id':6,'Artikel':'204 - Kälber-Iglu "Premium"',         'Menge':600,  'Preis':350.00, 'ei_ums':0.0,'ei_ant':0.0,'ei_kum':0.0,'ei_kl':'-'},
    {'id':7,'Artikel':'403 - Konventionelles Pressengarn',   'Menge':120,  'Preis':45.00,  'ei_ums':0.0,'ei_ant':0.0,'ei_kum':0.0,'ei_kl':'-'},
    {'id':8,'Artikel':'105 - Agrar-Drohne (Rehkitzrettung)', 'Menge':10,   'Preis':8900.00,'ei_ums':0.0,'ei_ant':0.0,'ei_kum':0.0,'ei_kl':'-'},
]

TESTDATEN_RP = [
    {'id':1,'Produkt':'301 - Rinder-Ohrmarken','Absatz':45000,'DB':0.20,'typ_eingabe':'-'},
    {'id':2,'Produkt':'103 - Spezial-Bio-Saatgut','Absatz':3000,'DB':35.00,'typ_eingabe':'-'},
    {'id':3,'Produkt':'104 - NPK-Standarddünger','Absatz':1500,'DB':85.00,'typ_eingabe':'-'},
    {'id':4,'Produkt':'105 - Agrar-Drohne','Absatz':10,'DB':1200.00,'typ_eingabe':'-'},
    {'id':5,'Produkt':'403 - Pressengarn','Absatz':120,'DB':5.00,'typ_eingabe':'-'},
]

TESTDATEN_DB = [
    {'id':1,'Produkt':'204 - Kälber-Iglu "Premium"',        'Preis':350.00,'var_k':210.00,'Menge':600, 'ei_db1':0.0,'ei_db2':0.0,'ei_bep':0.0},
    {'id':2,'Produkt':'203 - Kälber-Tränkeeimer',           'Preis':7.00,  'var_k':8.50,  'Menge':1000,'ei_db1':0.0,'ei_db2':0.0,'ei_bep':0.0},
    {'id':3,'Produkt':'104 - NPK-Standarddünger (1t BigBag)','Preis':450.00,'var_k':310.00,'Menge':1500,'ei_db1':0.0,'ei_db2':0.0,'ei_bep':0.0},
]


# ─────────────────────────────────────────────
#  LOCALSTORAGE
# ─────────────────────────────────────────────
def save_to_localstorage(data: dict):
    json_str = json.dumps(data, ensure_ascii=False).replace("\\", "\\\\").replace("`", "\\`")
    components.html(
        f"<script>(function(){{try{{localStorage.setItem('{STORAGE_KEY}',`{json_str}`);}}catch(e){{}}}})();</script>",
        height=0)

def get_persisted_state():
    if "load" in st.query_params:
        try:
            return json.loads(st.query_params["load"])
        except Exception:
            pass
    return None

def do_autosave():
    keys = ['stammdaten','plz_produkte','abc_liste','bcg_liste','rp_liste','db_produkte']
    save_to_localstorage({k: st.session_state[k] for k in keys if k in st.session_state})


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if 'state_loaded' not in st.session_state:
    st.session_state.state_loaded = False

if not st.session_state.state_loaded:
    loaded = get_persisted_state()
    if loaded:
        for k, v in loaded.items():
            st.session_state[k] = v
        st.query_params.clear()
    else:
        # Testdaten laden
        st.session_state.stammdaten   = TESTDATEN_STAMM
        st.session_state.plz_produkte = TESTDATEN_PLZ
        st.session_state.bcg_liste    = TESTDATEN_BCG
        st.session_state.abc_liste    = TESTDATEN_ABC
        st.session_state.rp_liste     = TESTDATEN_RP
        st.session_state.db_produkte  = TESTDATEN_DB
    st.session_state.state_loaded = True

# Fehlende Keys sichern
for k, v in [('stammdaten', TESTDATEN_STAMM), ('plz_produkte', TESTDATEN_PLZ),
              ('bcg_liste', TESTDATEN_BCG), ('abc_liste', TESTDATEN_ABC),
              ('rp_liste', TESTDATEN_RP), ('db_produkte', TESTDATEN_DB)]:
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────
def safe_str(s):
    return str(s).encode('latin-1', 'replace').decode('latin-1')

def _is_fpdf2():
    """Prüft ob fpdf2 (Version >= 2) oder fpdf1 installiert ist."""
    try:
        import fpdf as _m
        ver = str(getattr(_m, 'FPDF_VERSION', getattr(_m, '__version__', '1')))
        return int(ver.split('.')[0]) >= 2
    except Exception:
        return False

_FPDF2 = _is_fpdf2()

def pdf_output(pdf):
    """Gibt das PDF als bytes zurück.

    WICHTIG: pdf.output() darf NUR EINMAL aufgerufen werden!
    Bei fpdf1 schließt der erste Aufruf das Dokument (State=3),
    ein zweiter Aufruf liefert dann leere bytes zurück.
    """
    if _FPDF2:
        # fpdf2: output() gibt bytearray zurück
        result = pdf.output()
        return bytes(result) if isinstance(result, (bytes, bytearray)) else result.encode('latin-1', 'replace')
    else:
        # fpdf1: output(dest='S') gibt Latin-1-String zurück – NUR DIESEN EINEN Aufruf!
        raw = pdf.output(dest='S')
        if isinstance(raw, (bytes, bytearray)):
            return bytes(raw)
        return raw.encode('latin-1', 'replace')

def pdf_download_button(label, build_fn, filename):
    if PDF_AVAILABLE:
        try:
            data = build_fn()
            if data and len(data) > 100:
                st.download_button(label=label, data=data, file_name=filename,
                                   mime="application/pdf", use_container_width=True)
            else:
                st.error("⚠️ PDF leer – bitte Konsole/Terminal auf Fehlermeldungen prüfen.")
        except Exception as e:
            st.error(f"⚠️ PDF-Fehler: {e}")
    else:
        st.button("📄 PDF (fpdf fehlt)", disabled=True, use_container_width=True)

def get_stammdaten_namen():
    return [p['name'] for p in st.session_state.stammdaten if p.get('name','').strip()]

def produkt_auswahl_widget(modul_key: str):
    namen = get_stammdaten_namen()
    if not namen:
        return None
    with st.expander("📋 Produkte aus Stammdaten übernehmen", expanded=False):
        st.caption("Wähle Produkte aus und klicke auf Übernehmen. Alle Felder sind danach noch editierbar.")
        selected = st.multiselect("Produkte:", options=namen,
                                  key=f"sel_{modul_key}", label_visibility="collapsed")
        if selected and st.button("➕ Ausgewählte übernehmen", key=f"import_{modul_key}"):
            return selected
    return None

def get_export_json():
    keys = ['stammdaten','plz_produkte','abc_liste','bcg_liste','rp_liste','db_produkte']
    return json.dumps({k: st.session_state[k] for k in keys if k in st.session_state},
                      ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
#  NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Absatzcontrolling\n#### AgriGeno eG")
    st.markdown("---")
    modul = st.radio("Modul:", options=[
        "🏠 Startseite / Stammdaten",
        "🔄 Produktlebenszyklus",
        "🔷 Portfoliomatrix",
        "📦 ABC-Analyse",
        "⚡ Renner-Penner-Liste",
        "💰 DB-Rechnung",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("#### 💾 Daten")
    if st.button("💾 Speichern", use_container_width=True):
        do_autosave(); st.success("✅ Gespeichert!")

    components.html(f"""
    <script>
    function ladeZustand() {{
        var val = localStorage.getItem('{STORAGE_KEY}');
        if (val) {{
            window.parent.location.href =
                window.parent.location.href.split('?')[0] + '?load=' + encodeURIComponent(val);
        }} else {{ alert('Kein gespeicherter Zustand gefunden.'); }}
    }}
    </script>
    <button onclick="ladeZustand()" style="width:100%;padding:8px 12px;background:#075985;color:white;
        border:1px solid #0369a1;border-radius:8px;font-weight:600;font-size:0.875rem;cursor:pointer;
        margin-top:4px;font-family:'IBM Plex Sans',sans-serif;white-space:nowrap;">
        📂 Aus Browser laden</button>
    """, height=55)

    st.markdown("---")
    st.markdown("#### 📤 Export / Import")
    st.download_button("⬇️ JSON exportieren", data=get_export_json(),
                       file_name="agrigeno_daten.json", mime="application/json",
                       use_container_width=True)
    uploaded = st.file_uploader("⬆️ JSON importieren", type=["json"],
                                 key="json_import", label_visibility="collapsed")
    if uploaded is not None:
        try:
            imported = json.load(uploaded)
            for k, v in imported.items():
                st.session_state[k] = v
            st.success("✅ Importiert!"); st.rerun()
        except Exception as e:
            st.error(f"Fehler: {e}")

    if st.button("🔄 Testdaten zurücksetzen", use_container_width=True):
        st.session_state.stammdaten   = TESTDATEN_STAMM
        st.session_state.plz_produkte = TESTDATEN_PLZ
        st.session_state.bcg_liste    = TESTDATEN_BCG
        st.session_state.abc_liste    = TESTDATEN_ABC
        st.session_state.rp_liste     = TESTDATEN_RP
        st.session_state.db_produkte  = TESTDATEN_DB
        do_autosave(); st.rerun()

    st.markdown("---")
    if not PDF_AVAILABLE:
        st.warning("⚠️ PDF: `pip install fpdf`")


# ═══════════════════════════════════════════════════════════
#  MODUL 0: STARTSEITE / STAMMDATEN
# ═══════════════════════════════════════════════════════════
if modul == "🏠 Startseite / Stammdaten":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Absatzcontrolling · AgriGeno eG</h1>
        <p>Lernsituation: Blindflug im Vertrieb – Produktstammdaten & Modulübersicht</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🗂️ Produktstammdaten")
    st.markdown("""
    <div class="hint-box">
    Trage hier alle Produkte mit ihren Basisdaten ein. In jedem Modul kannst du auswählen,
    welche Produkte für den jeweiligen Analyseschritt relevant sind.
    </div>
    """, unsafe_allow_html=True)

    stamm = st.session_state.stammdaten

    def stamm_add():
        nid = max([x['id'] for x in stamm], default=0) + 1
        stamm.append({'id':nid,'name':'','absatz':0,'preis':0.0,'liegezeit':''})

    if not stamm:
        stamm_add()

    st.markdown("""
    <div class='table-header'>
        <div style='flex:2.4 1 0%'>Artikel-Nr. / Name</div>
        <div style='flex:1.1 1 0%'>Absatz (p.a.)</div>
        <div style='flex:1.1 1 0%'>Stückpreis (€)</div>
        <div style='flex:1.5 1 0%'>Ø Liegezeit im Regal</div>
        <div style='flex:0.5 1 0%'>Löschen</div>
    </div>
    """, unsafe_allow_html=True)

    for item in stamm:
        with st.container(border=True):
            c1,c2,c3,c4,c5 = st.columns([2.4,1.1,1.1,1.5,0.5], gap="small")
            with c1: item['name']      = st.text_input("N", value=item.get('name',''),     key=f"s_n_{item['id']}", label_visibility="collapsed", placeholder="z.B. 301 - Rinder-Ohrmarken")
            with c2: item['absatz']    = st.number_input("A", value=int(item.get('absatz',0)), key=f"s_a_{item['id']}", label_visibility="collapsed", step=100, min_value=0)
            with c3: item['preis']     = st.number_input("P", value=float(item.get('preis',0.0)), key=f"s_p_{item['id']}", label_visibility="collapsed", step=0.5, format="%.2f", min_value=0.0)
            with c4: item['liegezeit'] = st.text_input("L", value=item.get('liegezeit',''), key=f"s_l_{item['id']}", label_visibility="collapsed", placeholder="z.B. 6 Wochen")
            with c5:
                if st.button("🗑️", key=f"s_del_{item['id']}", disabled=(len(stamm)<=1)):
                    st.session_state.stammdaten = [x for x in stamm if x['id']!=item['id']]
                    do_autosave(); st.rerun()

    ca, cb, _ = st.columns([2,2,3])
    with ca:
        if st.button("➕ Artikel hinzufügen", use_container_width=True):
            stamm_add(); do_autosave(); st.rerun()
    with cb:
        if st.button("➖ Letzten entfernen", use_container_width=True, disabled=(len(stamm)<=1)):
            st.session_state.stammdaten.pop(); do_autosave(); st.rerun()

    namen = [p['name'] for p in stamm if p.get('name','').strip()]
    if namen:
        st.success(f"✅ {len(namen)} Artikel gespeichert")

    st.markdown("---")
    st.subheader("📚 Module – Reihenfolge der Lernsituation")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="info-card"><h4>① 🔄 Produktlebenszyklus</h4>
        <p>Produkte den PLZ-Phasen zuordnen und in der Kurve verorten.</p></div>
        <div class="info-card"><h4>② 🔷 Portfoliomatrix</h4>
        <p>Produkte selbst in die BCG-Matrix einordnen: Stars, Cash Cows, Question Marks & Poor Dogs.</p></div>
        <div class="info-card"><h4>③ 📦 ABC-Analyse</h4>
        <p>Artikel nach Umsatzbedeutung klassifizieren – Pareto-Diagramm & Klassengrenzen.</p></div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="info-card"><h4>④ ⚡ Renner-Penner-Liste</h4>
        <p>Produkte nach Absatz und Deckungsbeitrag klassifizieren.</p></div>
        <div class="info-card"><h4>⑤ 💰 DB-Rechnung</h4>
        <p>DB I und DB II selbst berechnen – inkl. Verbundartikel-Analyse (Kälber-Iglu & Tränkeeimer).</p></div>
        """, unsafe_allow_html=True)
    st.info("👈 Wähle ein Modul in der linken Seitenleiste.")


# ═══════════════════════════════════════════════════════════
#  MODUL 1: PRODUKTLEBENSZYKLUS
# ═══════════════════════════════════════════════════════════
elif modul == "🔄 Produktlebenszyklus":
    st.markdown("""
    <div class="main-header">
        <h1>🔄 Produktlebenszyklus</h1>
        <p>Ordne die AgriGeno-Produkte den PLZ-Phasen zu – sie erscheinen dann in der Kurve</p>
    </div>
    """, unsafe_allow_html=True)

    PHASEN = ["Einführung","Wachstum","Reife","Sättigung","Degeneration"]
    PHASEN_INFO = {
        "Einführung":   {"farbe":"#e0f2fe","icon":"🌱","x_center":5,
                         "merkmale":"Niedriger Umsatz, hohe Kosten, Verlust, wenig Konkurrenz",
                         "strategie":"Markterschließung, Werbung, Skimming oder Penetrationsstrategie"},
        "Wachstum":     {"farbe":"#dcfce7","icon":"📈","x_center":16,
                         "merkmale":"Umsatz steigt stark, Gewinne steigen, mehr Wettbewerber",
                         "strategie":"Marktdurchdringung, Qualitätsverbesserung, Preissenkung"},
        "Reife":        {"farbe":"#fef9c3","icon":"🏆","x_center":26,
                         "merkmale":"Umsatz auf Höchststand, Gewinne beginnen zu sinken",
                         "strategie":"Produktdifferenzierung, neue Zielgruppen erschließen"},
        "Sättigung":    {"farbe":"#fed7aa","icon":"📊","x_center":35,
                         "merkmale":"Umsatz stagniert, starker Preiswettbewerb, Gewinne sinken stark",
                         "strategie":"Kostenreduktion, Relaunch oder Nischenstrategie wählen"},
        "Degeneration": {"farbe":"#fee2e2","icon":"📉","x_center":45,
                         "merkmale":"Umsatz und Gewinn fallen stark, Marktaustritt nahe",
                         "strategie":"Eliminierung oder Nischenpflege, Ressourcen umschichten"},
    }

    def plz_umsatz(t):
        if t < 10: return max(0, -5 + 8*t)
        if t < 22: return 75 + 20*(t-10)/12
        if t < 30: return 95 - 5*(t-22)/8
        if t < 40: return 90 - 25*(t-30)/10
        return max(0, 65 - 25*(t-40)/10)

    x = list(range(0, 51))
    df_plz = pd.DataFrame({
        "Zeit": x,
        "Umsatz": [plz_umsatz(t) for t in x],
        "Phase": [PHASEN[0] if t<10 else PHASEN[1] if t<22 else PHASEN[2] if t<30
                  else PHASEN[3] if t<40 else PHASEN[4] for t in x]
    })

    # Produkt-Annotationen aus den SuS-Eingaben
    plz_prod = st.session_state.plz_produkte
    annot_rows = []
    phase_counter = {p: 0 for p in PHASEN}
    for item in plz_prod:
        ph = item.get('Phase_eingabe', '-')
        if ph in PHASEN and item.get('Produkt','').strip():
            xc = PHASEN_INFO[ph]['x_center']
            yc = plz_umsatz(xc)
            # Leicht versetzen wenn mehrere Produkte in selber Phase
            offset = phase_counter[ph] * 8
            phase_counter[ph] += 1
            # Kurzname für Kurve
            kurz = item['Produkt'].split('-')[-1].strip() if '-' in item['Produkt'] else item['Produkt']
            kurz = kurz[:22] + '…' if len(kurz) > 22 else kurz
            annot_rows.append({"Zeit": xc, "Umsatz": yc + 5 + offset, "Label": kurz})

    # Kurve zeichnen
    area = alt.Chart(df_plz).mark_area(opacity=0.2).encode(
        x=alt.X("Zeit:Q", title="Zeitachse", axis=alt.Axis(labels=False, ticks=False)),
        y=alt.Y("Umsatz:Q", title="Umsatz / Gewinn (schematisch)", scale=alt.Scale(domain=[-5,115])),
        color=alt.Color("Phase:N", scale=alt.Scale(domain=PHASEN,
            range=["#38bdf8","#34d399","#fbbf24","#fb923c","#f87171"]),
            legend=alt.Legend(title="Phase")),
        tooltip=["Phase:N"])

    linie = alt.Chart(df_plz).mark_line(strokeWidth=3, color="#0284c7").encode(
        x="Zeit:Q", y="Umsatz:Q")

    layers = [area, linie]

    if annot_rows:
        df_annot = pd.DataFrame(annot_rows)
        punkte = alt.Chart(df_annot).mark_point(size=120, color="#dc2626", filled=True).encode(
            x="Zeit:Q", y="Umsatz:Q", tooltip=["Label:N"])
        texte = alt.Chart(df_annot).mark_text(
            fontSize=11, fontWeight=600, color="#dc2626", dy=-14, align="center"
        ).encode(x="Zeit:Q", y="Umsatz:Q", text="Label:N")
        layers += [punkte, texte]

    st.altair_chart(alt.layer(*layers).properties(height=310), use_container_width=True)

    # ── Phasen-Info-Karten (gleiche Höhe durch feste height) ──
    st.subheader("📋 Phasen im Detail")
    cols5 = st.columns(5)
    for i, (phase, info) in enumerate(PHASEN_INFO.items()):
        with cols5[i]:
            st.markdown(f"""<div style="background:{info['farbe']};border-radius:10px;padding:0.9rem;
                height:240px;overflow-y:auto;border:1px solid #e2e8f0;box-sizing:border-box;">
                <div style="font-size:1.3rem;text-align:center;">{info['icon']}</div>
                <b style="font-size:0.88rem;">{phase}</b>
                <p style="font-size:0.74rem;color:#334155;margin-top:5px;"><b>Merkmale:</b><br/>{info['merkmale']}</p>
                <p style="font-size:0.74rem;color:#334155;"><b>Strategie:</b><br/>{info['strategie']}</p>
                </div>""", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.subheader("🏷️ Produkte den Phasen zuordnen")
    st.markdown("""
    <div class="hint-box">
    Wähle für jedes Produkt die passende PLZ-Phase – es erscheint dann direkt in der Kurve oben.
    </div>
    """, unsafe_allow_html=True)

    if 'plz_produkte' not in st.session_state:
        st.session_state.plz_produkte = TESTDATEN_PLZ[:]

    sel_plz = produkt_auswahl_widget("plz")
    if sel_plz:
        existing = [x['Produkt'] for x in st.session_state.plz_produkte]
        nid = max([x['id'] for x in st.session_state.plz_produkte], default=0)
        for name in sel_plz:
            if name not in existing:
                nid += 1
                st.session_state.plz_produkte.append({'id':nid,'Produkt':name,'Phase_eingabe':'-'})
        st.session_state.plz_produkte = [x for x in st.session_state.plz_produkte if x['Produkt'].strip()]
        do_autosave(); st.rerun()

    def plz_add():
        nid = max([x['id'] for x in st.session_state.plz_produkte], default=0)+1
        st.session_state.plz_produkte.append({'id':nid,'Produkt':'','Phase_eingabe':'-'})

    optionen_plz = ["-"] + PHASEN
    hdr_plz = "<div class='table-header'>"
    for r,h in zip([2.5,2.0,0.7],["Produktname","Meine PLZ-Phase","Aktion"]):
        hdr_plz += f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr_plz += "</div>"
    st.markdown(hdr_plz, unsafe_allow_html=True)

    for item in st.session_state.plz_produkte:
        with st.container(border=True):
            c1,c2,c3 = st.columns([2.5,2.0,0.7], gap="small")
            with c1:
                item['Produkt'] = st.text_input("P", value=item['Produkt'],
                    key=f"plz_p_{item['id']}", label_visibility="collapsed",
                    placeholder="Produktname …")
            with c2:
                pi = optionen_plz.index(item['Phase_eingabe']) if item['Phase_eingabe'] in optionen_plz else 0
                item['Phase_eingabe'] = st.selectbox("Ph", options=optionen_plz, index=pi,
                    key=f"plz_e_{item['id']}", label_visibility="collapsed")
            with c3:
                if st.button("🗑️", key=f"plz_del_{item['id']}",
                             disabled=(len(st.session_state.plz_produkte)<=1)):
                    st.session_state.plz_produkte = [x for x in st.session_state.plz_produkte
                                                     if x['id']!=item['id']]
                    do_autosave(); st.rerun()

    if st.button("➕ Produkt hinzufügen", key="plz_add"):
        plz_add(); do_autosave(); st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)
    col_ppdf, _ = st.columns([1,1])
    with col_ppdf:
        def build_plz_pdf():
            pdf = FPDF(); pdf.add_page()
            pdf.set_font("Arial",'B',16)
            # Kein En-Dash (–) hier, damit latin-1 funktioniert
            pdf.cell(0,10,"Produktlebenszyklus - Auswertung",ln=True,align="C"); pdf.ln(4)
            pdf.set_font("Arial",'B',9); pdf.set_fill_color(226,232,240)
            for h,w in zip(["Produkt","Gewaehlte Phase"],[100,80]):
                pdf.cell(w,8,h,border=1,align="C",fill=True)
            pdf.ln(); pdf.set_font("Arial",'',9)
            for item in st.session_state.plz_produkte:
                if not item['Produkt']: continue
                pdf.cell(100,8,safe_str(item['Produkt']),border=1)
                pdf.cell(80,8,safe_str(item['Phase_eingabe']),border=1,align="C"); pdf.ln()
            return pdf_output(pdf)
        pdf_download_button("📄 PLZ als PDF", build_plz_pdf, "Produktlebenszyklus.pdf")


# ═══════════════════════════════════════════════════════════
#  MODUL 2: PORTFOLIOMATRIX (BCG)
# ═══════════════════════════════════════════════════════════
elif modul == "🔷 Portfoliomatrix":
    st.markdown("""
    <div class="main-header">
        <h1>🔷 Portfoliomatrix (BCG)</h1>
        <p>Ordne die Produkte selbst in die vier BCG-Felder ein</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Theorie: Die vier Felder", expanded=False):
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.success("⭐ **Stars**\nHohes Wachstum, hoher Anteil → Investieren")
        with c2: st.warning("❓ **Question Marks**\nHohes Wachstum, niedriger Anteil → Selektieren")
        with c3: st.info("🐄 **Cash Cows**\nNiedriges Wachstum, hoher Anteil → Abschöpfen")
        with c4: st.error("🐕 **Poor Dogs**\nNiedriges Wachstum, niedriger Anteil → Desinvestieren")

    if 'bcg_liste' not in st.session_state:
        st.session_state.bcg_liste = TESTDATEN_BCG[:]

    FELDER_OPT = ["-","⭐ Star","❓ Question Mark","🐄 Cash Cow","🐕 Poor Dog"]

    sel_bcg = produkt_auswahl_widget("bcg")
    if sel_bcg:
        existing = [x['Produkt'] for x in st.session_state.bcg_liste]
        nid = max([x['id'] for x in st.session_state.bcg_liste], default=0)
        for name in sel_bcg:
            if name not in existing:
                nid += 1
                st.session_state.bcg_liste.append(
                    {'id':nid,'Produkt':name,'wachstum_text':'','anteil_text':'','ei_feld':'-'})
        st.session_state.bcg_liste = [x for x in st.session_state.bcg_liste if x['Produkt'].strip()]
        do_autosave(); st.rerun()

    def bcg_add():
        nid = max([x['id'] for x in st.session_state.bcg_liste], default=0)+1
        st.session_state.bcg_liste.append(
            {'id':nid,'Produkt':'','wachstum_text':'','anteil_text':'','ei_feld':'-'})

    # ── Eingabetabelle ──
    st.subheader("📋 Produkte einordnen")
    st.markdown("""
    <div class="hint-box">
    Beschreibe Marktwachstum und Marktanteil in eigenen Worten (z.B. „hoch", „gering", „stagnierend")
    und wähle das passende BCG-Feld. Die Matrix unten aktualisiert sich sofort.
    </div>
    """, unsafe_allow_html=True)

    COL_BCG = [1.8,1.2,1.2,1.6,0.7]
    hdr_b = "<div class='table-header'>"
    for r,h in zip(COL_BCG,["Produkt","Marktwachstum","Rel. Marktanteil","Mein BCG-Feld","Akt."]):
        hdr_b += f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr_b += "</div>"
    st.markdown(hdr_b, unsafe_allow_html=True)

    bcg = st.session_state.bcg_liste
    for item in bcg:
        with st.container(border=True):
            cols = st.columns(COL_BCG, gap="small")
            with cols[0]:
                item['Produkt'] = st.text_input("P", value=item['Produkt'],
                    key=f"bcg_p_{item['id']}", label_visibility="collapsed", placeholder="Produktname …")
            with cols[1]:
                item['wachstum_text'] = st.text_input("W", value=item.get('wachstum_text',''),
                    key=f"bcg_w_{item['id']}", label_visibility="collapsed",
                    placeholder="z.B. hoch, gering …")
            with cols[2]:
                item['anteil_text'] = st.text_input("A", value=item.get('anteil_text',''),
                    key=f"bcg_a_{item['id']}", label_visibility="collapsed",
                    placeholder="z.B. hoch, niedrig …")
            with cols[3]:
                fi = FELDER_OPT.index(item.get('ei_feld','-')) if item.get('ei_feld','-') in FELDER_OPT else 0
                item['ei_feld'] = st.selectbox("F", options=FELDER_OPT, index=fi,
                    key=f"bcg_f_{item['id']}", label_visibility="collapsed")
            with cols[4]:
                if st.button("🗑️", key=f"bcg_del_{item['id']}", disabled=(len(bcg)<=1)):
                    st.session_state.bcg_liste = [x for x in bcg if x['id']!=item['id']]
                    do_autosave(); st.rerun()

    if st.button("➕ Produkt hinzufügen", key="bcg_add"):
        bcg_add(); do_autosave(); st.rerun()

    # ── Live 2×2-Matrix ──
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.subheader("🗺️ BCG-Matrix (Live-Ansicht)")

    felder = {"⭐ Star":[],"❓ Question Mark":[],"🐄 Cash Cow":[],"🐕 Poor Dog":[]}
    for item in bcg:
        if item['Produkt'].strip() and item.get('ei_feld','-') in felder:
            felder[item['ei_feld']].append(item['Produkt'])

    def bcg_box(name, color, items, caption_text=""):
        produkt_html = ("".join([f"<div style='margin:3px 0;padding:4px 8px;background:white;"
                                  f"border-radius:6px;font-size:0.85rem;border:1px solid #e2e8f0;'>"
                                  f"{''.join(name.split()[0:1])} {p}</div>" for p in items])
                        if items else "<i style='color:#94a3b8;font-size:0.85rem;'>Noch kein Produkt zugeordnet</i>")
        st.markdown(f"""<div class="bcg-feld" style="background:{color};">
            <b style="font-size:1rem;">{name}</b>
            {f'<div style="font-size:0.75rem;color:#64748b;margin-bottom:4px;">{caption_text}</div>' if caption_text else ''}
            <div style="margin-top:6px;">{produkt_html}</div>
            </div>""", unsafe_allow_html=True)

    # ── Achsenbeschriftung (bereinigt – kein verschobenes Layout mehr) ──
    st.markdown("""
    <div style="text-align:center;font-size:0.8rem;color:#64748b;margin-bottom:2px;font-weight:600;">
        ↑ Hohes Marktwachstum
    </div>
    <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#64748b;
        padding:0 8px;margin-bottom:6px;">
        <span>← Niedriger relativer Marktanteil</span>
        <span>Hoher relativer Marktanteil →</span>
    </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns(2)
    with left_col:
        bcg_box("❓ Question Marks", "#fefce8", felder["❓ Question Mark"], "Hoch/Niedrig → Selektieren")
        bcg_box("🐕 Poor Dogs",      "#fff1f2", felder["🐕 Poor Dog"],      "Niedrig/Niedrig → Desinvestieren")
    with right_col:
        bcg_box("⭐ Stars",    "#f0fdf4", felder["⭐ Star"],    "Hoch/Hoch → Investieren")
        bcg_box("🐄 Cash Cows","#eff6ff", felder["🐄 Cash Cow"],"Niedrig/Hoch → Abschöpfen")

    st.markdown("""<div style="font-size:0.8rem;color:#64748b;text-align:center;margin-top:4px;font-weight:600;">
        ↓ Niedriges Marktwachstum</div>""", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)
    # ── PDF-Export (Prüfen-Button entfernt – Besprechung in der Stunde) ──
    def build_bcg_pdf():
        pdf = FPDF(); pdf.add_page()
        pdf.set_font("Arial",'B',16)
        # Kein En-Dash (–) hier, damit latin-1 funktioniert
        pdf.cell(0,10,"Portfoliomatrix - Auswertung",ln=True,align="C"); pdf.ln(4)
        pdf.set_font("Arial",'B',9); pdf.set_fill_color(226,232,240)
        for h,w in zip(["Produkt","Marktwachstum","Rel. Anteil","BCG-Feld"],[55,40,40,55]):
            pdf.cell(w,8,h,border=1,align="C",fill=True)
        pdf.ln(); pdf.set_font("Arial",'',9)
        clean = lambda s: s.replace("⭐","Star").replace("❓","?").replace("🐄","Cash Cow").replace("🐕","Poor Dog")
        for item in bcg:
            if not item['Produkt']: continue
            pdf.cell(55,8,safe_str(item['Produkt']),border=1)
            pdf.cell(40,8,safe_str(item.get('wachstum_text','')),border=1)
            pdf.cell(40,8,safe_str(item.get('anteil_text','')),border=1)
            pdf.cell(55,8,safe_str(clean(item.get('ei_feld','-'))),border=1,align="C"); pdf.ln()
        return pdf_output(pdf)
    pdf_download_button("📄 Portfolio als PDF", build_bcg_pdf, "Portfoliomatrix.pdf")


# ═══════════════════════════════════════════════════════════
#  MODUL 3: ABC-ANALYSE
# ═══════════════════════════════════════════════════════════
elif modul == "📦 ABC-Analyse":
    st.markdown("""
    <div class="main-header">
        <h1>📦 ABC-Analyse</h1>
        <p>Klassifiziere die Artikel nach ihrer Umsatzbedeutung</p>
    </div>
    """, unsafe_allow_html=True)

    # Klassengrenzen IM Hauptbereich (nicht Sidebar)
    with st.expander("⚙️ Klassengrenzen festlegen", expanded=True):
        cg1, cg2, cg3 = st.columns(3)
        with cg1:
            grenze_a = st.number_input("A-Klasse bis (kumuliert %)", value=80, min_value=1,
                                        max_value=99, step=1, key="abc_ga")
        with cg2:
            grenze_b = st.number_input("B-Klasse bis (kumuliert %)", value=95,
                                        min_value=grenze_a+1, max_value=99, step=1, key="abc_gb")
        with cg3:
            # C-Klasse: immer bis 100 %, aber als sichtbares Eingabefeld (Lernzweck)
            _gc_min = min(grenze_b + 1, 100)
            grenze_c = st.number_input("C-Klasse bis (kumuliert %)", value=100,
                                        min_value=_gc_min, max_value=100, step=1, key="abc_gc")
            if grenze_c < 100:
                st.caption("⚠️ In der ABC-Analyse endet C immer bei 100 %.")

    if 'abc_liste' not in st.session_state:
        st.session_state.abc_liste = TESTDATEN_ABC[:]

    sel_abc = produkt_auswahl_widget("abc")
    if sel_abc:
        existing = [x['Artikel'] for x in st.session_state.abc_liste]
        nid = max([x['id'] for x in st.session_state.abc_liste], default=0)
        stamm_map = {p['name']:p for p in st.session_state.stammdaten}
        for name in sel_abc:
            if name not in existing:
                nid += 1
                sd = stamm_map.get(name,{})
                st.session_state.abc_liste.append({
                    'id':nid,'Artikel':name,
                    'Menge':int(sd.get('absatz',0)),'Preis':float(sd.get('preis',0.0)),
                    'ei_ums':0.0,'ei_ant':0.0,'ei_kum':0.0,'ei_kl':'-'})
        st.session_state.abc_liste = [x for x in st.session_state.abc_liste if x['Artikel'].strip()]
        do_autosave(); st.rerun()

    def abc_move(index, direction):
        l = st.session_state.abc_liste
        if direction=='up' and index>0: l[index],l[index-1] = l[index-1],l[index]
        elif direction=='down' and index<len(l)-1: l[index],l[index+1] = l[index+1],l[index]

    def abc_add():
        nid = max([x['id'] for x in st.session_state.abc_liste], default=0)+1
        st.session_state.abc_liste.append({'id':nid,'Artikel':'','Menge':0,'Preis':0.0,
                                            'ei_ums':0.0,'ei_ant':0.0,'ei_kum':0.0,'ei_kl':'-'})

    COL = [0.5,1.8,0.9,0.9,1.1,0.9,0.9,0.9,1.0]
    hdr = "<div class='table-header'>"
    for r,h in zip(COL,["Rang","Artikel","Menge","Preis","Umsatz (€)","Anteil %","Kum. %","Klasse","Aktion"]):
        hdr += f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr += "</div>"
    st.markdown(hdr, unsafe_allow_html=True)

    current = st.session_state.abc_liste
    gesamt = sum(x['Menge']*x['Preis'] for x in current)
    kum_lauf = 0.0

    for i, item in enumerate(current):
        umsatz_soll = float(item['Menge']*item['Preis'])
        anteil_soll = (umsatz_soll/gesamt*100) if gesamt>0 else 0.0
        kum_lauf += anteil_soll
        optionen = ["-","A","B","C"]
        with st.container(border=True):
            cols = st.columns(COL, gap="small")
            with cols[0]: st.markdown(f"<div class='rang-text'>{i+1}.</div>", unsafe_allow_html=True)
            with cols[1]: item['Artikel'] = st.text_input("A", value=item['Artikel'], key=f"abc_art_{item['id']}", label_visibility="collapsed")
            with cols[2]: item['Menge']   = st.number_input("M", value=int(item['Menge']), key=f"abc_men_{item['id']}", label_visibility="collapsed", step=1, min_value=0)
            with cols[3]: item['Preis']   = st.number_input("P", value=float(item['Preis']), key=f"abc_pre_{item['id']}", label_visibility="collapsed", step=0.5, min_value=0.0, format="%.2f")
            with cols[4]: item['ei_ums']  = st.number_input("U", value=float(item.get('ei_ums',0.0)), key=f"abc_ums_{item['id']}", label_visibility="collapsed", step=1.0, min_value=0.0)
            with cols[5]: item['ei_ant']  = st.number_input("An", value=float(item.get('ei_ant',0.0)), key=f"abc_ant_{item['id']}", label_visibility="collapsed", step=0.01, format="%.2f", min_value=0.0, max_value=100.0)
            with cols[6]: item['ei_kum']  = st.number_input("K", value=float(item.get('ei_kum',0.0)), key=f"abc_kum_{item['id']}", label_visibility="collapsed", step=0.01, format="%.2f", min_value=0.0, max_value=100.5)
            with cols[7]:
                kl_idx = optionen.index(item.get('ei_kl','-')) if item.get('ei_kl','-') in optionen else 0
                item['ei_kl'] = st.selectbox("Kl", options=optionen, index=kl_idx, key=f"abc_kl_{item['id']}", label_visibility="collapsed")
            with cols[8]:
                cu,cd = st.columns(2)
                if cu.button("↑", key=f"abc_up_{item['id']}", disabled=(i==0)):
                    abc_move(i,'up'); do_autosave(); st.rerun()
                if cd.button("↓", key=f"abc_dn_{item['id']}", disabled=(i==len(current)-1)):
                    abc_move(i,'down'); do_autosave(); st.rerun()

    ca,cr,_ = st.columns([2,2,3])
    with ca:
        if st.button("➕ Artikel hinzufügen", use_container_width=True):
            abc_add(); do_autosave(); st.rerun()
    with cr:
        if st.button("➖ Letzten entfernen", use_container_width=True, disabled=(len(current)<=1)):
            st.session_state.abc_liste.pop(); do_autosave(); st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.subheader("📊 Pareto-Diagramm (deine Eingaben)")
    chart_data = pd.DataFrame({
        "Artikel": [f"{i+1}. {x['Artikel']}" for i,x in enumerate(current)],
        "Anteil (%)": [round(x.get('ei_ant',0),2) for x in current],
        "Kumuliert (%)": [round(x.get('ei_kum',0),2) for x in current],
    })
    base = alt.Chart(chart_data).encode(x=alt.X("Artikel:N", sort=None))
    bars = base.mark_bar(color="#93c5fd", size=35, opacity=0.85).encode(
        y=alt.Y("Anteil (%):Q", scale=alt.Scale(domain=[0,100])),
        tooltip=["Artikel:N", alt.Tooltip("Anteil (%):Q", format=".2f")])
    line = base.mark_line(color="#0284c7", point=True, strokeWidth=3).encode(
        y=alt.Y("Kumuliert (%):Q"),
        tooltip=["Artikel:N", alt.Tooltip("Kumuliert (%):Q", format=".2f")])
    st.altair_chart(alt.layer(bars, line).properties(height=340), use_container_width=True)

    st.markdown("<hr/>", unsafe_allow_html=True)
    cp, cd_btn = st.columns(2)
    with cp:
        if st.button("✅ Analyse prüfen", use_container_width=True, type="primary"):
            filled = [x for x in current if x['Artikel'].strip()]
            if not filled:
                st.warning("Bitte zuerst Artikel eintragen.")
            elif any(filled[j]['Menge']*filled[j]['Preis'] < filled[j+1]['Menge']*filled[j+1]['Preis']
                     for j in range(len(filled)-1)):
                st.error("❌ Reihenfolge falsch – höchster Umsatz muss auf Rang 1!")
            else:
                fehler = False; kk=0.0
                g = sum(x['Menge']*x['Preis'] for x in filled)
                for i,item in enumerate(filled):
                    u=item['Menge']*item['Preis']; a=(u/g*100) if g>0 else 0; kk+=a
                    kl_soll = "A" if kk<=grenze_a+0.01 else ("B" if kk<=grenze_b+0.01 else "C")
                    if abs(item.get('ei_ums',0)-u)>0.5 or abs(item.get('ei_ant',0)-a)>0.05 or abs(item.get('ei_kum',0)-kk)>0.05:
                        st.error(f"❌ Rechenfehler bei Rang {i+1} ({item['Artikel']})"); fehler=True; break
                    if item.get('ei_kl','-')!=kl_soll:
                        st.error(f"❌ Falsche Klasse bei Rang {i+1} ({item['Artikel']}). Erwartet: {kl_soll}"); fehler=True; break
                if not fehler:
                    st.success("✅ Alles korrekt!")
    with cd_btn:
        def build_abc_pdf():
            pdf=FPDF(); pdf.add_page(); pdf.set_font("Arial",'B',16)
            pdf.cell(0,10,"ABC-Analyse - Auswertung",ln=True,align="C"); pdf.ln(4)
            pdf.set_font("Arial",'B',9); pdf.set_fill_color(226,232,240)
            for h,w in zip(["Rang","Artikel","Menge","Preis","Umsatz","Ant.%","Kum.%","Kl."],[10,52,15,22,28,18,18,12]):
                pdf.cell(w,8,h,border=1,align="C",fill=True)
            pdf.ln(); pdf.set_font("Arial",'',9)
            g2=sum(x['Menge']*x['Preis'] for x in current); kk2=0.0
            for i,item in enumerate(current):
                if not item['Artikel']: continue
                u=item['Menge']*item['Preis']; a=(u/g2*100) if g2>0 else 0; kk2+=a
                kl="A" if kk2<=grenze_a+0.01 else("B" if kk2<=grenze_b+0.01 else "C")
                pdf.cell(10,8,f"{i+1}.",border=1,align="C"); pdf.cell(52,8,safe_str(item.get('Artikel','-')),border=1)
                pdf.cell(15,8,str(item.get('Menge',0)),border=1,align="C"); pdf.cell(22,8,f"{item.get('Preis',0):.2f}",border=1,align="R")
                pdf.cell(28,8,f"{item.get('ei_ums',u):.2f}",border=1,align="R"); pdf.cell(18,8,f"{item.get('ei_ant',a):.2f}%",border=1,align="R")
                pdf.cell(18,8,f"{item.get('ei_kum',kk2):.2f}%",border=1,align="R"); pdf.cell(12,8,str(item.get('ei_kl',kl)),border=1,align="C"); pdf.ln()
            return pdf_output(pdf)
        pdf_download_button("📄 PDF speichern", build_abc_pdf, "ABC_Analyse.pdf")


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
        absatz_grenze = st.number_input("Absatz-Schwelle (Stk.)", value=500, step=100)
        db_grenze     = st.number_input("DB-Schwelle (€/Stk.)", value=10.0, step=1.0, format="%.2f")

    if 'rp_liste' not in st.session_state:
        st.session_state.rp_liste = TESTDATEN_RP[:]

    def get_rp_typ(absatz, db):
        h_a=absatz>=absatz_grenze; h_d=db>=db_grenze
        if h_a and h_d:     return "🏆 Renner"
        if not h_a and h_d: return "😴 Schläfer"
        if h_a and not h_d: return "❓ Fragezeichen"
        return "💀 Penner"

    sel_rp = produkt_auswahl_widget("rp")
    if sel_rp:
        existing=[x['Produkt'] for x in st.session_state.rp_liste]
        nid=max([x['id'] for x in st.session_state.rp_liste], default=0)
        for name in sel_rp:
            if name not in existing:
                nid+=1
                st.session_state.rp_liste.append({'id':nid,'Produkt':name,'Absatz':0,'DB':0.0,'typ_eingabe':'-'})
        st.session_state.rp_liste=[x for x in st.session_state.rp_liste if x['Produkt'].strip()]
        do_autosave(); st.rerun()

    def rp_add():
        nid=max([x['id'] for x in st.session_state.rp_liste], default=0)+1
        st.session_state.rp_liste.append({'id':nid,'Produkt':'','Absatz':0,'DB':0.0,'typ_eingabe':'-'})

    rp=st.session_state.rp_liste
    hdr_rp="<div class='table-header'>"
    for r,h in zip([1.8,1.0,1.0,1.5,0.7],["Produkt","Absatz (Stk.)","DB (€/Stk.)","Mein Typ","Akt."]):
        hdr_rp+=f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr_rp+="</div>"
    st.markdown(hdr_rp, unsafe_allow_html=True)

    typen_opt=["-","🏆 Renner","😴 Schläfer","❓ Fragezeichen","💀 Penner"]
    for item in rp:
        with st.container(border=True):
            cols=st.columns([1.8,1.0,1.0,1.5,0.7],gap="small")
            with cols[0]: item['Produkt']=st.text_input("P",value=item['Produkt'],key=f"rp_p_{item['id']}",label_visibility="collapsed")
            with cols[1]: item['Absatz']=st.number_input("A",value=int(item['Absatz']),key=f"rp_a_{item['id']}",label_visibility="collapsed",step=10,min_value=0)
            with cols[2]: item['DB']=st.number_input("D",value=float(item['DB']),key=f"rp_d_{item['id']}",label_visibility="collapsed",step=0.5,format="%.2f")
            with cols[3]:
                ti=typen_opt.index(item.get('typ_eingabe','-')) if item.get('typ_eingabe','-') in typen_opt else 0
                item['typ_eingabe']=st.selectbox("T",options=typen_opt,index=ti,key=f"rp_te_{item['id']}",label_visibility="collapsed")
            with cols[4]:
                if st.button("🗑️",key=f"rp_del_{item['id']}",disabled=(len(rp)<=1)):
                    st.session_state.rp_liste=[x for x in rp if x['id']!=item['id']]
                    do_autosave(); st.rerun()

    if st.button("➕ Produkt hinzufügen",key="rp_add"):
        rp_add(); do_autosave(); st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)
    col_rcheck,col_rpdf=st.columns(2)
    with col_rcheck:
        if st.button("✅ Eingaben prüfen",use_container_width=True,type="primary"):
            fehler=False
            for item in rp:
                if not item['Produkt']: continue
                soll=get_rp_typ(item['Absatz'],item['DB'])
                if item.get('typ_eingabe','-')=='-':
                    st.warning(f"⚠️ {item['Produkt']}: Kein Typ gewählt."); fehler=True
                elif item.get('typ_eingabe')!=soll:
                    st.error(f"❌ {item['Produkt']}: '{item['typ_eingabe']}' – richtig: {soll}"); fehler=True
            if not fehler:
                st.success("✅ Alle Klassifizierungen korrekt!")
                felder_rp={"🏆 Renner":[],"😴 Schläfer":[],"❓ Fragezeichen":[],"💀 Penner":[]}
                for item in rp:
                    if item['Produkt']: felder_rp[get_rp_typ(item['Absatz'],item['DB'])].append(item['Produkt'])
                cq2,cs2=st.columns(2); cd2,cc2=st.columns(2)
                def rp_box(container,name,color,items):
                    with container:
                        st.markdown(f"""<div style="background:{color};border-radius:10px;padding:1rem;
                            min-height:90px;border:1px solid #e2e8f0;"><b>{name}</b><br/>
                            {"<br/>".join([f"• {p}" for p in items]) if items else "<i style='color:#94a3b8;'>Keine</i>"}
                            </div>""", unsafe_allow_html=True)
                rp_box(cq2,"😴 Schläfer","#fefce8",felder_rp["😴 Schläfer"])
                rp_box(cs2,"🏆 Renner","#f0fdf4",felder_rp["🏆 Renner"])
                rp_box(cd2,"💀 Penner","#fff1f2",felder_rp["💀 Penner"])
                rp_box(cc2,"❓ Fragezeichen","#eff6ff",felder_rp["❓ Fragezeichen"])
                st.caption("← Niedriger Absatz | Hoher Absatz →  (oben = hoher DB)")

    with col_rpdf:
        def build_rp_pdf():
            pdf=FPDF(); pdf.add_page()
            pdf.set_font("Arial",'B',16); pdf.cell(0,10,"Renner-Penner-Liste",ln=True,align="C"); pdf.ln(4)
            pdf.set_font("Arial",'',10)
            pdf.cell(0,6,f"Schwellenwerte: Absatz >= {absatz_grenze} Stk. | DB >= {db_grenze:.2f} EUR/Stk.",ln=True); pdf.ln(4)
            pdf.set_font("Arial",'B',9); pdf.set_fill_color(226,232,240)
            for h,w in zip(["Produkt","Absatz","DB (EUR/Stk.)","Eingabe SuS","Richtiger Typ"],[55,28,32,47,47]):
                pdf.cell(w,8,h,border=1,align="C",fill=True)
            pdf.ln(); pdf.set_font("Arial",'',9)
            clean=lambda s: s.replace("🏆","").replace("😴","").replace("❓","").replace("💀","").strip()
            for item in rp:
                if not item['Produkt']: continue
                soll=get_rp_typ(item['Absatz'],item['DB'])
                pdf.cell(55,8,safe_str(item['Produkt']),border=1)
                pdf.cell(28,8,str(item['Absatz']),border=1,align="R")
                pdf.cell(32,8,f"{item['DB']:.2f}",border=1,align="R")
                pdf.cell(47,8,safe_str(clean(item.get('typ_eingabe','-'))),border=1,align="C")
                pdf.cell(47,8,safe_str(clean(soll)),border=1,align="C"); pdf.ln()
            return pdf_output(pdf)
        pdf_download_button("📄 Liste als PDF", build_rp_pdf, "Renner_Penner_Liste.pdf")


# ═══════════════════════════════════════════════════════════
#  MODUL 5: DB-RECHNUNG
# ═══════════════════════════════════════════════════════════
elif modul == "💰 DB-Rechnung":
    st.markdown("""
    <div class="main-header">
        <h1>💰 Deckungsbeitragsrechnung</h1>
        <p>DB I und DB II selbst berechnen - Verbundartikel: Kaelber-Iglu & Traenkeeimer</p>
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
        """)

    with st.sidebar:
        st.markdown("#### ⚙️ Fixkosten")
        fixkosten = st.number_input("Fixkosten gesamt (€)", value=50000.0, step=1000.0, format="%.2f")

    if 'db_produkte' not in st.session_state:
        st.session_state.db_produkte = TESTDATEN_DB[:]

    sel_db = produkt_auswahl_widget("db")
    if sel_db:
        existing=[x['Produkt'] for x in st.session_state.db_produkte]
        nid=max([x['id'] for x in st.session_state.db_produkte], default=0)
        stamm_map={p['name']:p for p in st.session_state.stammdaten}
        for name in sel_db:
            if name not in existing:
                nid+=1
                sd=stamm_map.get(name,{})
                st.session_state.db_produkte.append({
                    'id':nid,'Produkt':name,'Preis':float(sd.get('preis',0.0)),
                    'var_k':0.0,'Menge':int(sd.get('absatz',0)),
                    'ei_db1':0.0,'ei_db2':0.0,'ei_bep':0.0})
        st.session_state.db_produkte=[x for x in st.session_state.db_produkte if x['Produkt'].strip()]
        do_autosave(); st.rerun()

    def db_add():
        nid=max([x['id'] for x in st.session_state.db_produkte], default=0)+1
        st.session_state.db_produkte.append({'id':nid,'Produkt':'','Preis':0.0,'var_k':0.0,
                                              'Menge':0,'ei_db1':0.0,'ei_db2':0.0,'ei_bep':0.0})

    db_prod=st.session_state.db_produkte
    COL_DB=[1.5,1.0,1.0,1.0,1.0,1.1,1.1,0.6]
    hdr_db="<div class='table-header'>"
    for r,h in zip(COL_DB,["Produkt","Preis (€)","Var.K. (€)","Menge","DB I (€)","DB II (€)","BEP (Stk.)","Akt."]):
        hdr_db+=f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr_db+="</div>"
    st.markdown(hdr_db, unsafe_allow_html=True)

    for item in db_prod:
        with st.container(border=True):
            cols=st.columns(COL_DB,gap="small")
            with cols[0]: item['Produkt']=st.text_input("P",value=item['Produkt'],key=f"db_p_{item['id']}",label_visibility="collapsed")
            with cols[1]: item['Preis']=st.number_input("Pr",value=float(item['Preis']),key=f"db_pr_{item['id']}",label_visibility="collapsed",step=0.5,format="%.2f",min_value=0.0)
            with cols[2]: item['var_k']=st.number_input("Vk",value=float(item['var_k']),key=f"db_vk_{item['id']}",label_visibility="collapsed",step=0.5,format="%.2f",min_value=0.0)
            with cols[3]: item['Menge']=st.number_input("Me",value=int(item['Menge']),key=f"db_me_{item['id']}",label_visibility="collapsed",step=10,min_value=0)
            with cols[4]: item['ei_db1']=st.number_input("D1",value=float(item.get('ei_db1',0.0)),key=f"db_d1_{item['id']}",label_visibility="collapsed",step=0.5,format="%.2f")
            with cols[5]: item['ei_db2']=st.number_input("D2",value=float(item.get('ei_db2',0.0)),key=f"db_d2_{item['id']}",label_visibility="collapsed",step=10.0,format="%.2f")
            with cols[6]: item['ei_bep']=st.number_input("BP",value=float(item.get('ei_bep',0.0)),key=f"db_bp_{item['id']}",label_visibility="collapsed",step=1.0,format="%.0f")
            with cols[7]:
                if st.button("🗑️",key=f"db_del_{item['id']}",disabled=(len(db_prod)<=1)):
                    st.session_state.db_produkte=[x for x in db_prod if x['id']!=item['id']]
                    do_autosave(); st.rerun()

    if st.button("➕ Produkt hinzufügen",key="db_add"):
        db_add(); do_autosave(); st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)
    col_dbcheck,col_dbpdf=st.columns(2)
    with col_dbcheck:
        if st.button("✅ Rechnung prüfen",use_container_width=True,type="primary"):
            fehler=False
            for item in db_prod:
                if not item['Produkt']: continue
                db1s=item['Preis']-item['var_k']
                db2s=db1s*item['Menge']
                beps=(fixkosten/db1s) if db1s>0 else 0
                if abs(item['ei_db1']-db1s)>0.05:
                    st.error(f"❌ {item['Produkt']}: DB I falsch ({item['ei_db1']:.2f} | richtig: {db1s:.2f})"); fehler=True; break
                if abs(item['ei_db2']-db2s)>0.5:
                    st.error(f"❌ {item['Produkt']}: DB II falsch ({item['ei_db2']:.2f} | richtig: {db2s:.2f})"); fehler=True; break
                if db1s>0 and abs(item['ei_bep']-beps)>1:
                    st.error(f"❌ {item['Produkt']}: BEP falsch ({item['ei_bep']:.0f} | richtig: {beps:.0f})"); fehler=True; break
            if not fehler:
                st.success("✅ Alle Berechnungen korrekt!")
                g_db2=sum((x['Preis']-x['var_k'])*x['Menge'] for x in db_prod if x['Produkt'])
                gewinn=g_db2-fixkosten
                c1,c2,c3=st.columns(3)
                with c1: st.markdown(f"""<div class='metric-box'><div class='val'>{g_db2:,.2f} €</div><div class='lbl'>Gesamt DB II</div></div>""",unsafe_allow_html=True)
                with c2: st.markdown(f"""<div class='metric-box'><div class='val'>{fixkosten:,.2f} €</div><div class='lbl'>Fixkosten</div></div>""",unsafe_allow_html=True)
                with c3:
                    farbe="#f0fdf4" if gewinn>=0 else "#fff1f2"
                    st.markdown(f"""<div class='metric-box' style='background:{farbe};'><div class='val'>{gewinn:+,.2f} €</div><div class='lbl'>Gewinn / Verlust</div></div>""",unsafe_allow_html=True)

    with col_dbpdf:
        def build_db_pdf():
            pdf=FPDF(); pdf.add_page()
            pdf.set_font("Arial",'B',16); pdf.cell(0,10,"Deckungsbeitragsrechnung",ln=True,align="C"); pdf.ln(4)
            pdf.set_font("Arial",'B',9); pdf.set_fill_color(226,232,240)
            for h,w in zip(["Produkt","Preis","Var.K.","Menge","DB I","DB II","BEP"],[50,22,22,20,25,28,25]):
                pdf.cell(w,8,h,border=1,align="C",fill=True)
            pdf.ln(); pdf.set_font("Arial",'',9); g_db2_p=0
            for item in db_prod:
                if not item['Produkt']: continue
                db1=item['Preis']-item['var_k']; db2=db1*item['Menge']
                bep=(fixkosten/db1) if db1>0 else 0; g_db2_p+=db2
                pdf.cell(50,8,safe_str(item['Produkt']),border=1)
                pdf.cell(22,8,f"{item['Preis']:.2f}",border=1,align="R"); pdf.cell(22,8,f"{item['var_k']:.2f}",border=1,align="R")
                pdf.cell(20,8,str(item['Menge']),border=1,align="R"); pdf.cell(25,8,f"{item['ei_db1']:.2f}",border=1,align="R")
                pdf.cell(28,8,f"{item['ei_db2']:.2f}",border=1,align="R"); pdf.cell(25,8,f"{item['ei_bep']:.0f}",border=1,align="R"); pdf.ln()
            pdf.ln(4); g_p=g_db2_p-fixkosten
            pdf.set_font("Arial",'B',10); pdf.cell(0,7,"Gesamtergebnis:",ln=True)
            pdf.set_font("Arial",'',10)
            pdf.cell(0,6,f"Gesamt DB II = {g_db2_p:,.2f} EUR",ln=True)
            pdf.cell(0,6,f"Fixkosten   = {fixkosten:,.2f} EUR",ln=True)
            pdf.cell(0,6,f"Gewinn/Verlust = {g_p:+,.2f} EUR",ln=True)
            return pdf_output(pdf)
        pdf_download_button("📄 DB-Rechnung als PDF", build_db_pdf, "DB_Rechnung.pdf")

do_autosave()