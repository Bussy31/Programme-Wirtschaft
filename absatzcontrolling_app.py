import streamlit as st
import pandas as pd
import altair as alt
import json
import os
import tempfile
import uuid

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


st.set_page_config(
    page_title="Absatzcontrolling – AgriGeno eG",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

_LAST_SAVED = {}


def _get_save_file():
    """Lokale Browser-Persistenz ist deaktiviert. JSON-Export/Import ist der zuverlässige Weg."""
    return None


def save_to_file(data: dict):
    """Lokale Datei-Speicherung ist deaktiviert."""
    return


def load_from_file():
    """Lokale Datei-Ladung ist deaktiviert."""
    return None


def do_autosave(force=False):
    """Lokale Auto-Save-Funktion ist deaktiviert."""
    return


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
.bcg-feld { border-radius:10px; padding:1rem 1.2rem; min-height:340px;
    border:2px solid #e2e8f0; margin-bottom:4px; }
.bcg-feld b { font-size:1rem; }

/* ── Mülleimer-Buttons in schmalen Spalten verkleinern (Container Queries) ── */
[data-testid="column"] { container-type: inline-size; }
@container (max-width: 150px) {
    .stButton > button {
        padding: 1px 5px !important;
        min-height: 24px !important;
        height: 24px !important;
        font-size: 0.78rem !important;
        line-height: 1 !important;
        font-weight: 700 !important;
    }
}

/* ── Globale Input-Optimierung ── */
.stTextInput input,
.stNumberInput input {
    font-size: 0.82rem !important;
}
.stSelectbox > div > div { font-size: 0.82rem !important; }

/* +/- Spinner ausblenden – Browser-nativ */
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
    -webkit-appearance: none !important;
    margin: 0 !important;
}
input[type="number"] { -moz-appearance: textfield !important; }

/* +/- Buttons von Streamlit selbst ausblenden */
[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"],
[data-testid="stNumberInput"] button {
    display: none !important;
}



/* ── Tablet-Optimierung (481px – 1024px) ── */
@media (max-width: 1024px) and (min-width: 481px) {
    /* Etwas kleinere Basis-Schrift damit mehr auf den Bildschirm passt */
    html, body, [class*="css"] { font-size: 13px !important; }

    /* Horizontales Scrollen für Zeilen mit vielen Spalten */
    [data-testid="stHorizontalBlock"] {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        flex-wrap: nowrap !important;
    }
    [data-testid="column"] {
        min-width: 80px !important;
        flex-shrink: 0 !important;
    }

    /* Touch-freundliche Eingabefelder (mind. 42px Tipp-Fläche) */
    .stTextInput input,
    .stNumberInput input {
        min-height: 42px !important;
        font-size: 0.88rem !important;
        padding: 6px 8px !important;
    }
    .stSelectbox > div > div {
        min-height: 42px !important;
        font-size: 0.88rem !important;
    }
    .stButton > button {
        min-height: 42px !important;
        font-size: 0.85rem !important;
        padding: 4px 10px !important;
    }

    /* Header kompakter */
    .main-header { padding: 1.2rem 1.5rem !important; }
    .main-header h1 { font-size: 1.5rem !important; }
    .main-header p { font-size: 0.85rem !important; }

    /* Tabellen-Header */
    .table-header { padding: 8px 10px !important; }
    .table-header div { font-size: 0.78rem !important; }

    /* BCG-Matrix kompakter */
    .bcg-feld { min-height: 240px !important; padding: 0.75rem !important; }
    .bcg-feld b { font-size: 0.9rem !important; }

    /* Metriken */
    .metric-box .val { font-size: 1.3rem !important; }
    .metric-box { padding: 0.75rem !important; }
}
</style>
<div class="footer">© Philipp Bußmann</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  STARTDATEN (leer – Schüler tragen selbst ein)
# ─────────────────────────────────────────────
TESTDATEN_STAMM = []
TESTDATEN_PLZ   = []
TESTDATEN_BCG   = []
TESTDATEN_ABC   = []
TESTDATEN_RP    = []
TESTDATEN_DB    = []
TESTDATEN_BEWERTUNG = []


# ─────────────────────────────────────────────
#  DATEI-BASIERTE PERSISTENZ
# ─────────────────────────────────────────────
SAVE_KEYS = ['stammdaten', 'plz_produkte', 'abc_liste', 'bcg_liste', 'rp_liste', 'db_produkte', 'bewertung_liste']
_LAST_SAVED = {}
_PENDING_CHANGES = 0

def save_to_file(data: dict):
    """Speichert Daten zu JSON-Datei – speichert nur, wenn sich etwas geändert hat."""
    file_path = _get_save_file()
    data_str = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if _LAST_SAVED.get(file_path) == data_str:
        return
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        _LAST_SAVED[file_path] = data_str
    except Exception:
        pass


def load_from_file():
    """Lädt Daten aus der Session-spezifischen JSON-Datei."""
    file_path = _get_save_file()
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return None

def do_autosave(force=False):
    """Speichert Session-State Daten. Bei force=True sofort, sonst nach 5 Änderungen."""
    global _PENDING_CHANGES
    file_path = _get_save_file()
    data = {k: st.session_state[k] for k in SAVE_KEYS if k in st.session_state}

    if force:
        save_to_file(data)
        _PENDING_CHANGES = 0
        return

    data_str = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if _LAST_SAVED.get(file_path) != data_str:
        _PENDING_CHANGES += 1
        if _PENDING_CHANGES >= 5:
            save_to_file(data)
            _PENDING_CHANGES = 0


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if 'state_loaded' not in st.session_state:
    st.session_state.state_loaded = False
if 'json_import_key' not in st.session_state:
    st.session_state.json_import_key = 0
if 'json_import_success' not in st.session_state:
    st.session_state.json_import_success = False

if not st.session_state.state_loaded:
    loaded = load_from_file()
    if loaded:
        for k, v in loaded.items():
            st.session_state[k] = v
    else:
        st.session_state.stammdaten   = TESTDATEN_STAMM
        st.session_state.plz_produkte = TESTDATEN_PLZ
        st.session_state.bcg_liste    = TESTDATEN_BCG
        st.session_state.abc_liste    = TESTDATEN_ABC
        st.session_state.rp_liste     = TESTDATEN_RP
        st.session_state.db_produkte  = TESTDATEN_DB
        st.session_state.bewertung_liste = TESTDATEN_BEWERTUNG
    st.session_state.state_loaded = True

for k, v in [('stammdaten', TESTDATEN_STAMM), ('plz_produkte', TESTDATEN_PLZ),
              ('bcg_liste', TESTDATEN_BCG), ('abc_liste', TESTDATEN_ABC),
              ('rp_liste', TESTDATEN_RP), ('db_produkte', TESTDATEN_DB),
              ('bewertung_liste', TESTDATEN_BEWERTUNG)]:
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
#  HELPER – allgemein
# ─────────────────────────────────────────────
def safe_str(s):
    """Konvertiert einen String zu Latin-1 (für fpdf1 kompatibel)."""
    return str(s).encode('latin-1', 'replace').decode('latin-1')

def _is_fpdf2():
    try:
        import fpdf as _m
        ver = str(getattr(_m, 'FPDF_VERSION', getattr(_m, '__version__', '1')))
        return int(ver.split('.')[0]) >= 2
    except Exception:
        return False

_FPDF2 = _is_fpdf2()

def pdf_output(pdf):
    """Gibt das PDF als bytes zurück.
    WICHTIG: pdf.output() darf nur EINMAL aufgerufen werden!
    Bei fpdf1 schließt der erste Aufruf das Dokument (State=3).
    """
    if _FPDF2:
        result = pdf.output()
        return bytes(result) if isinstance(result, (bytes, bytearray)) else result.encode('latin-1', 'replace')
    else:
        raw = pdf.output(dest='S')
        if isinstance(raw, (bytes, bytearray)):
            return bytes(raw)
        return raw.encode('latin-1', 'replace')

def fmt_de(val, decimals=2):
    """Formatiert eine Zahl nach deutschem Standard: 1.234,56 (Punkt = Tausender, Komma = Dezimal)."""
    s = f"{float(val):,.{decimals}f}"   # englisch: 1,234.56
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')

def pdf_download_button(label, build_fn, filename):
    if PDF_AVAILABLE:
        try:
            data = build_fn()
            if data and len(data) > 100:
                st.download_button(label=label, data=data, file_name=filename,
                                   mime="application/pdf", use_container_width=True)
            else:
                st.error("PDF leer – bitte Terminal auf Fehler prüfen.")
        except Exception as e:
            st.error(f"PDF-Fehler: {e}")
    else:
        st.button("PDF (fpdf fehlt)", disabled=True, use_container_width=True)

def get_stammdaten_namen():
    return [p['name'] for p in st.session_state.stammdaten if p.get('name','').strip()]

def produkt_auswahl_widget(modul_key: str):
    """Widget zur Produktauswahl – speichert nach Bestätigung."""
    namen = get_stammdaten_namen()
    if not namen:
        return None
    with st.expander("📋 Produkte aus Stammdaten übernehmen", expanded=False):
        st.caption("Wähle Produkte aus und klicke auf Übernehmen.")
        selected = st.multiselect("Produkte:", options=namen,
                                  key=f"sel_{modul_key}", label_visibility="collapsed")
        if selected and st.button("Ausgewählte übernehmen", key=f"import_{modul_key}"):
            return selected
    return None

def get_export_json():
    keys = ['stammdaten','plz_produkte','abc_liste','bcg_liste','rp_liste','db_produkte','bewertung_liste']
    return json.dumps({k: st.session_state[k] for k in keys if k in st.session_state},
                      ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
#  HELPER – Diagramme als PNG (für PDF-Export)
# ─────────────────────────────────────────────
def _plz_y(t):
    """PLZ-Umsatzkurve (schematisch).
    Einführung: flach/zögerlich; Wachstum: steil; Reife: Plateau; Sättigung: moderat; Degeneration: steil.
    """
    if t < 10: return max(0, t * t * 0.38)         # Einführung: quadratisch flach  0→38
    if t < 22: return 38 + 57 * (t - 10) / 12      # Wachstum: steil               38→95
    if t < 30: return 95 - 6 * (t - 22) / 8        # Reife: leicht abfallend       95→89
    if t < 40: return 89 - 24 * (t - 30) / 10      # Sättigung: moderat            89→65
    return max(0, 65 - 55 * (t - 40) / 10)         # Degeneration: steil           65→10→0

PLZ_PHASEN_X = {
    "Einführung": 5, "Wachstum": 16, "Reife": 26,
    "Sättigung": 35, "Degeneration": 45
}

def create_plz_chart_png():
    """Rendert den PLZ-Chart via Matplotlib in eine temporäre PNG-Datei.
    Gibt den Dateipfad zurück (oder None bei Fehler). Datei muss nach Nutzung gelöscht werden.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        x = list(range(51))
        y = [_plz_y(t) for t in x]

        fig, ax = plt.subplots(figsize=(13, 4.2))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')

        phase_defs = [
            (0,  10, '#38bdf8', 'Einführung'),
            (10, 22, '#34d399', 'Wachstum'),
            (22, 30, '#fbbf24', 'Reife'),
            (30, 40, '#fb923c', 'Sättigung'),
            (40, 50, '#f87171', 'Degeneration'),
        ]
        for start, end, color, name in phase_defs:
            xs = [t for t in x if start <= t <= end]
            ys = [_plz_y(t) for t in xs]
            ax.fill_between(xs, 0, ys, alpha=0.25, color=color)
            if start > 0:
                ax.axvline(x=start, color='#cbd5e1', linewidth=0.8, linestyle='--')
            mid = (start + end) / 2
            ax.text(mid, 118, name, ha='center', va='bottom', fontsize=9,
                    color='#334155', fontweight='bold')

        ax.plot(x, y, color='#0284c7', linewidth=2.8)

        # Produkt-Annotationen
        counter = {p: 0 for p in PLZ_PHASEN_X}
        for item in st.session_state.get('plz_produkte', []):
            ph = item.get('Phase_eingabe', '-')
            if ph in PLZ_PHASEN_X and item.get('Produkt', '').strip():
                xc = PLZ_PHASEN_X[ph]
                yc = _plz_y(xc)
                off = counter[ph] * 12
                counter[ph] += 1
                kurz = item['Produkt']
                kurz = (kurz[:28] + '..') if len(kurz) > 28 else kurz
                ax.plot(xc, yc + 5 + off, 'o', color='#dc2626', markersize=7, zorder=5)
                ax.text(xc, yc + 12 + off, kurz, ha='center', fontsize=7.5,
                        color='#dc2626', fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.85, ec='none'))

        ax.set_xlim(0, 50)
        ax.set_ylim(-5, 132)
        ax.set_xticks([])
        ax.set_xlabel('Zeitachse →', fontsize=9, color='#64748b')
        ax.set_ylabel('Umsatz / Gewinn (schematisch)', fontsize=9, color='#64748b')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for sp in ['bottom', 'left']:
            ax.spines[sp].set_color('#e2e8f0')
        ax.tick_params(colors='#94a3b8')

        plt.tight_layout(pad=0.5)
        f = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        fname = f.name; f.close()
        fig.savefig(fname, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        return fname
    except Exception:
        return None


def create_bcg_matrix_png(felder):
    """Rendert die BCG-Matrix via Matplotlib in eine temporäre PNG-Datei.
    Gibt den Dateipfad zurück (oder None bei Fehler). Datei muss nach Nutzung gelöscht werden.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches

        fig, ax = plt.subplots(figsize=(9, 7))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.set_xticks([]); ax.set_yticks([])

        # (label, bg-color, x0, x1, y0, y1, products)
        quads = [
            ('Question Marks', '#fefce8', 0.0, 0.5, 0.5, 1.0, felder.get('❓ Question Mark', [])),
            ('Stars',          '#f0fdf4', 0.5, 1.0, 0.5, 1.0, felder.get('⭐ Star',          [])),
            ('Poor Dogs',      '#fff1f2', 0.0, 0.5, 0.0, 0.5, felder.get('🐕 Poor Dog',      [])),
            ('Cash Cows',      '#eff6ff', 0.5, 1.0, 0.0, 0.5, felder.get('🐄 Cash Cow',      [])),
        ]

        for label, color, x0, x1, y0, y1, prods in quads:
            rect = mpatches.Rectangle((x0, y0), x1 - x0, y1 - y0,
                                      facecolor=color, edgecolor='#cbd5e1',
                                      linewidth=2, zorder=0)
            ax.add_patch(rect)
            cx = (x0 + x1) / 2
            # Feldbezeichnung klar INNEN oben im Quadranten platzieren
            ax.text(cx, y1 - 0.04, label, ha='center', va='top',
                    fontsize=11, fontweight='bold', color='#1e293b', zorder=2)
            # Produkte unterhalb der Bezeichnung
            for i, prod in enumerate(prods[:4]):
                safe_p = safe_str(prod)[:30]
                ax.text(cx, y1 - 0.17 - i * 0.10, f'• {safe_p}',
                        ha='center', va='top', fontsize=8, color='#475569',
                        bbox=dict(boxstyle='round,pad=0.15', fc='white', alpha=0.85, ec='none'),
                        zorder=3)

        ax.axvline(0.5, color='#64748b', linewidth=2.0, zorder=1)
        ax.axhline(0.5, color='#64748b', linewidth=2.0, zorder=1)

        # Achsenbeschriftungen
        ax.text(0.25, -0.05, 'Niedriger Marktanteil', ha='center', va='top',
                fontsize=8.5, color='#64748b', transform=ax.transAxes)
        ax.text(0.75, -0.05, 'Hoher Marktanteil', ha='center', va='top',
                fontsize=8.5, color='#64748b', transform=ax.transAxes)
        ax.text(1.05, 0.75, 'Hohes\nMarktwachstum', ha='left', va='center',
                fontsize=8.5, color='#64748b', transform=ax.transAxes)
        ax.text(1.05, 0.25, 'Niedriges\nMarktwachstum', ha='left', va='center',
                fontsize=8.5, color='#64748b', transform=ax.transAxes)

        for spine in ax.spines.values():
            spine.set_edgecolor('#e2e8f0')

        plt.tight_layout(pad=1.5)
        f = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        fname = f.name; f.close()
        fig.savefig(fname, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        return fname
    except Exception:
        return None


def create_abc_pareto_png(current):
    """Rendert das ABC-Pareto-Diagramm (Schüler-Eingaben) via Matplotlib als temporäre PNG-Datei.
    Gibt den Dateipfad zurück (oder None bei Fehler). Datei muss nach Nutzung gelöscht werden.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        artikel = [f"{i+1}. {safe_str(x.get('Artikel',''))[:22]}"
                   for i, x in enumerate(current) if x.get('Artikel','').strip()]
        anteile   = [x.get('ei_ant', 0.0) for x in current if x.get('Artikel','').strip()]
        kumuliert = [x.get('ei_kum', 0.0) for x in current if x.get('Artikel','').strip()]

        if not artikel:
            return None

        fig, ax1 = plt.subplots(figsize=(14, 4.5))
        fig.patch.set_facecolor('white')
        ax1.set_facecolor('white')

        xs = list(range(len(artikel)))
        ax1.bar(xs, anteile, color='#93c5fd', alpha=0.85, width=0.55, zorder=2)
        ax1.set_ylabel('Anteil (%)', color='#334155', fontsize=9)
        ax1.set_ylim(0, 105)
        ax1.set_xticks(xs)
        ax1.set_xticklabels(artikel, rotation=30, ha='right', fontsize=7.5)
        ax1.tick_params(colors='#94a3b8')
        ax1.set_title('Pareto-Diagramm (eigene Eingaben)', fontsize=10,
                      color='#1e293b', fontweight='bold', pad=8)

        ax2 = ax1.twinx()
        ax2.plot(xs, kumuliert, color='#0284c7', linewidth=2.5,
                 marker='o', markersize=5, zorder=3)
        ax2.set_ylabel('Kumuliert (%)', color='#0284c7', fontsize=9)
        ax2.set_ylim(0, 110)
        ax2.tick_params(colors='#0284c7')

        for sp in ax1.spines.values(): sp.set_edgecolor('#e2e8f0')
        for sp in ax2.spines.values(): sp.set_edgecolor('#e2e8f0')

        plt.tight_layout(pad=0.5)
        f = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        fname = f.name; f.close()
        fig.savefig(fname, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        return fname
    except Exception:
        return None


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
        "💰 DB-Rechnung",
        "⚡ Renner-Penner-Liste",
        "📋 Gesamtauswertung",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.info("⚠️ Lokale Browser-Speicherung ist deaktiviert. Bitte nutze den JSON-Export unten.")

    st.markdown("---")
    st.markdown("#### 📤 JSON Export / Import")
    st.download_button("⬇️ JSON exportieren", data=get_export_json(),
                       file_name="agrigeno_daten.json", mime="application/json",
                       use_container_width=True)
    st.caption("JSON-Datei auswählen und anschließend laden:")
    uploaded = st.file_uploader("JSON importieren", type=["json"],
                                 key=f"json_import_{st.session_state.json_import_key}",
                                 label_visibility="collapsed")
    if st.session_state.json_import_success:
        st.success("✅ Daten wurden erfolgreich geladen!")
        st.session_state.json_import_success = False
    if uploaded is not None:
        if st.button("📂 JSON laden", use_container_width=True):
            try:
                imported = json.load(uploaded)
                for k, v in imported.items():
                    st.session_state[k] = v
                # Widget-Keys explizit setzen damit alle Felder sofort korrekte Werte zeigen
                _rp_clean = lambda s: s.replace("🏆 ","").replace("😴 ","").replace("❓ ","").replace("💀 ","").strip()
                _rp_opt = ["-","Renner","Schlaefer","Fragezeichen","Penner"]
                for item in imported.get('stammdaten', []):
                    st.session_state[f"s_n_{item['id']}"]  = item.get('name', '')
                    st.session_state[f"s_a_{item['id']}"]  = int(item.get('absatz', 0))
                    st.session_state[f"s_p_{item['id']}"]  = float(item.get('preis', 0.0))
                    st.session_state[f"s_l_{item['id']}"]  = item.get('liegezeit', '')
                for item in imported.get('plz_produkte', []):
                    st.session_state[f"plz_p_{item['id']}"] = item.get('Produkt', '')
                    st.session_state[f"plz_e_{item['id']}"] = item.get('Phase_eingabe', '-')
                for item in imported.get('bcg_liste', []):
                    st.session_state[f"bcg_p_{item['id']}"] = item.get('Produkt', '')
                    st.session_state[f"bcg_w_{item['id']}"] = item.get('wachstum_text', '')
                    st.session_state[f"bcg_a_{item['id']}"] = item.get('anteil_text', '')
                    st.session_state[f"bcg_f_{item['id']}"] = item.get('ei_feld', '-')
                for item in imported.get('abc_liste', []):
                    st.session_state[f"abc_art_{item['id']}"] = item.get('Artikel', '')
                    st.session_state[f"abc_men_{item['id']}"] = int(item.get('Menge', 0))
                    st.session_state[f"abc_pre_{item['id']}"] = float(item.get('Preis', 0.0))
                    st.session_state[f"abc_ums_{item['id']}"] = float(item.get('ei_ums', 0.0))
                    st.session_state[f"abc_ant_{item['id']}"] = float(item.get('ei_ant', 0.0))
                    st.session_state[f"abc_kum_{item['id']}"] = float(item.get('ei_kum', 0.0))
                    st.session_state[f"abc_kl_{item['id']}"]  = item.get('ei_kl', '-')
                for item in imported.get('rp_liste', []):
                    st.session_state[f"rp_p_{item['id']}"]  = item.get('Produkt', '')
                    st.session_state[f"rp_a_{item['id']}"]  = int(item.get('Absatz', 0))
                    st.session_state[f"rp_d_{item['id']}"]  = float(item.get('DB', 0.0))
                    v = _rp_clean(item.get('typ_eingabe', '-'))
                    st.session_state[f"rp_te_{item['id']}"] = v if v in _rp_opt else '-'
                for item in imported.get('db_produkte', []):
                    st.session_state[f"db_p_{item['id']}"]  = item.get('Produkt', '')
                    st.session_state[f"db_pr_{item['id']}"] = float(item.get('Preis', 0.0))
                    st.session_state[f"db_vk_{item['id']}"] = float(item.get('var_k', 0.0))
                    st.session_state[f"db_fk_{item['id']}"] = float(item.get('fix_k', 0.0))
                    st.session_state[f"db_me_{item['id']}"] = int(item.get('Menge', 0))
                for item in imported.get('bewertung_liste', []):
                    st.session_state[f"bew_p_{item['id']}"]  = item.get('Produkt', '')
                    st.session_state[f"bew_t_{item['id']}"]  = item.get('bewertung', '')
                do_autosave(force=True)
                st.session_state.json_import_key += 1   # Uploader zurücksetzen
                st.session_state.json_import_success = True
                st.rerun()
            except Exception as e:
                st.error(f"Fehler beim Laden: {e}")

    if st.button("✕ Alle Daten löschen", use_container_width=True):
        st.session_state.stammdaten   = TESTDATEN_STAMM
        st.session_state.plz_produkte = TESTDATEN_PLZ
        st.session_state.bcg_liste    = TESTDATEN_BCG
        st.session_state.abc_liste    = TESTDATEN_ABC
        st.session_state.rp_liste     = TESTDATEN_RP
        st.session_state.db_produkte  = TESTDATEN_DB
        st.session_state.bewertung_liste = TESTDATEN_BEWERTUNG
        do_autosave(force=True); st.rerun()

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
        sid = item['id']
        if f"s_n_{sid}" not in st.session_state: st.session_state[f"s_n_{sid}"] = item.get('name', '')
        if f"s_a_{sid}" not in st.session_state: st.session_state[f"s_a_{sid}"] = int(item.get('absatz', 0))
        if f"s_p_{sid}" not in st.session_state: st.session_state[f"s_p_{sid}"] = float(item.get('preis', 0.0))
        if f"s_l_{sid}" not in st.session_state: st.session_state[f"s_l_{sid}"] = item.get('liegezeit', '')
        with st.container(border=True):
            c1,c2,c3,c4,c5 = st.columns([2.4,1.1,1.1,1.5,0.5], gap="small")
            with c1: item['name']      = st.text_input("N", key=f"s_n_{sid}", label_visibility="collapsed")
            with c2: item['absatz']    = st.number_input("A", key=f"s_a_{sid}", label_visibility="collapsed", step=100, min_value=0)
            with c3: item['preis']     = st.number_input("P", key=f"s_p_{sid}", label_visibility="collapsed", step=0.5, format="%.2f", min_value=0.0)
            with c4: item['liegezeit'] = st.text_input("L", key=f"s_l_{sid}", label_visibility="collapsed")
            with c5:
                _, mid, _ = st.columns([0.2, 1, 0.2])
                with mid:
                    if st.button("✕", key=f"s_del_{item['id']}", disabled=(len(stamm) <= 1),
                                 use_container_width=False):
                        st.session_state.stammdaten = [x for x in stamm if x['id'] != item['id']]
                        do_autosave(force=True); st.rerun()

    ca, _ = st.columns([2, 5])
    with ca:
        if st.button("➕ Artikel hinzufügen", use_container_width=True):
            stamm_add(); do_autosave(force=True); st.rerun()

    namen = [p['name'] for p in stamm if p.get('name','').strip()]
    if namen:
        st.success(f"✅ {len(namen)} Artikel gespeichert")

    st.markdown("---")
    st.subheader("📚 Module – Reihenfolge der Lernsituation")
    st.markdown("""
    <div class="info-card"><h4>① 🔄 Produktlebenszyklus</h4>
    <p>Jedes Produkt durchläuft typischerweise fünf Phasen: Einführung, Wachstum, Reife, Sättigung und
    Degeneration. In diesem Modul ordnest du die AgriGeno-Produkte den passenden PLZ-Phasen zu – sie
    erscheinen dann direkt in der schematischen Kurve.</p></div>

    <div class="info-card"><h4>② 🔷 Portfoliomatrix (BCG)</h4>
    <p>Die BCG-Matrix klassifiziert Produkte nach Marktwachstum und relativem Marktanteil in vier Felder:
    Stars, Question Marks, Cash Cows und Poor Dogs. Du ordnest die AgriGeno-Produkte selbst ein und
    leitest daraus die passende Normstrategie ab.</p></div>

    <div class="info-card"><h4>③ 📦 ABC-Analyse</h4>
    <p>Die ABC-Analyse bewertet Artikel nach ihrer Umsatzbedeutung (Pareto-Prinzip): Wenige A-Artikel
    machen einen Großteil des Umsatzes aus, viele C-Artikel nur einen kleinen Teil. Du berechnest
    Umsatzanteile, kumulative Werte und trägst die ABC-Klasse ein.</p></div>

    <div class="info-card"><h4>④ 💰 DB-Rechnung</h4>
    <p>Der Deckungsbeitrag zeigt, wie viel ein Produkt nach Abzug der variablen Kosten zum Unternehmensergebnis
    beiträgt. Du berechnest DB I (Stückbeitrag) und DB II (Gesamtbeitrag je Produkt) – die Grundlage für die
    Renner-Penner-Einordnung.</p></div>

    <div class="info-card"><h4>⑤ ⚡ Renner-Penner-Liste</h4>
    <p>Die Renner-Penner-Analyse kombiniert Absatz und Deckungsbeitrag: Renner sind absatz- und ertragsstarke
    Produkte, Penner sind in beiden Dimensionen schwach. Du klassifizierst alle Produkte und leitest
    sortimentspolitische Maßnahmen ab.</p></div>
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

    x_vals = list(range(0, 51))
    df_plz = pd.DataFrame({
        "Zeit": x_vals,
        "Umsatz": [_plz_y(t) for t in x_vals],
        "Phase": [PHASEN[0] if t<10 else PHASEN[1] if t<22 else PHASEN[2] if t<30
                  else PHASEN[3] if t<40 else PHASEN[4] for t in x_vals]
    })

    plz_prod = st.session_state.plz_produkte
    annot_rows = []
    phase_counter = {p: 0 for p in PHASEN}
    for item in plz_prod:
        ph = item.get('Phase_eingabe', '-')
        if ph in PHASEN and item.get('Produkt','').strip():
            xc = PHASEN_INFO[ph]['x_center']
            yc = _plz_y(xc)
            offset = phase_counter[ph] * 8
            phase_counter[ph] += 1
            kurz = item['Produkt']
            kurz = kurz[:30] + '…' if len(kurz) > 30 else kurz
            annot_rows.append({"Zeit": xc, "Umsatz": yc + 5 + offset, "Label": kurz})

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

    # ── Phasen-Info-Karten (gleiche Höhe) ──
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
        do_autosave(force=True); st.rerun()

    def plz_add():
        nid = max([x['id'] for x in st.session_state.plz_produkte], default=0)+1
        st.session_state.plz_produkte.append({'id':nid,'Produkt':'','Phase_eingabe':'-'})

    if not st.session_state.plz_produkte:
        plz_add()

    optionen_plz = ["-"] + PHASEN
    hdr_plz = "<div class='table-header'>"
    for r, h in zip([3.2, 2.2, 0.6], ["Produktname", "Meine PLZ-Phase", "Aktion"]):
        hdr_plz += f"<div style='flex:{r} 1 0%;text-align:{'center' if r < 1 else 'left'}'>{h}</div>"
    hdr_plz += "</div>"
    st.markdown(hdr_plz, unsafe_allow_html=True)

    should_save_later = False
    for item in st.session_state.plz_produkte:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3.2, 2.2, 0.6], gap="small")
            with c1:
                new_val = st.text_input("P", value=item['Produkt'],
                    key=f"plz_p_{item['id']}", label_visibility="collapsed",
                    placeholder="Produktname …")
                if new_val != item['Produkt']:
                    item['Produkt'] = new_val
                    should_save_later = True
            with c2:
                pi = optionen_plz.index(item['Phase_eingabe']) if item['Phase_eingabe'] in optionen_plz else 0
                new_val = st.selectbox("Ph", options=optionen_plz, index=pi,
                    key=f"plz_e_{item['id']}", label_visibility="collapsed")
                if new_val != item['Phase_eingabe']:
                    item['Phase_eingabe'] = new_val
                    should_save_later = True
            with c3:
                _, mid, _ = st.columns([0.3, 1, 0.3])
                with mid:
                    if st.button("✕", key=f"plz_del_{item['id']}",
                                 disabled=(len(st.session_state.plz_produkte) <= 1),
                                 use_container_width=False):
                        st.session_state.plz_produkte = [x for x in st.session_state.plz_produkte
                                                         if x['id'] != item['id']]
                        do_autosave(force=True); st.rerun()

    if st.button("➕ Produkt hinzufügen", key="plz_add"):
        plz_add(); do_autosave(force=True); st.rerun()
    
    # Am Ende: Speichern wenn nötig (lazy save)
    if should_save_later:
        do_autosave()

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── PDF-Export mit Diagramm ──
    def build_plz_pdf():
        pdf = FPDF(); pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Produktlebenszyklus - Auswertung", ln=True, align="C"); pdf.ln(3)

        # PLZ-Kurve als Bild einbetten
        img_path = create_plz_chart_png()
        if img_path:
            try:
                pdf.image(img_path, x=10, y=None, w=190)
                pdf.ln(4)
            except Exception:
                pass
            finally:
                try: os.unlink(img_path)
                except Exception: pass

        # Tabelle
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(226, 232, 240)
        for h, w in zip(["Produkt", "Gewaehlte PLZ-Phase"], [120, 65]):
            pdf.cell(w, 8, h, border=1, align="C", fill=True)
        pdf.ln(); pdf.set_font("Arial", '', 9)
        for item in st.session_state.plz_produkte:
            if not item['Produkt']: continue
            pdf.cell(120, 8, safe_str(item['Produkt']), border=1)
            pdf.cell(65, 8, safe_str(item['Phase_eingabe']), border=1, align="C"); pdf.ln()
        return pdf_output(pdf)

    pdf_download_button("📄 PLZ als PDF (mit Diagramm)", build_plz_pdf, "Produktlebenszyklus.pdf")


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

    # ── Theorie: BCG-Felder direkt sichtbar (wie PLZ-Phasenkarten) ──
    st.subheader("📋 BCG-Felder im Detail")
    bcg_theory = [
        {"icon":"⭐","name":"Stars","farbe":"#f0fdf4","border":"#86efac",
         "wachstum":"Hoch","anteil":"Hoch","strategie":"Investieren",
         "info":"Marktführer in wachsenden Märkten. Erfordern hohe Investitionen, erwirtschaften aber starke Erträge. Sie sind die Zukunft des Unternehmens und werden zu Cash Cows, wenn das Marktwachstum nachlässt.",
         "massnahme":"Marktposition ausbauen, Investitionen aufrechterhalten, aktiv bewerben"},
        {"icon":"❓","name":"Question Marks","farbe":"#fefce8","border":"#fde047",
         "wachstum":"Hoch","anteil":"Niedrig","strategie":"Selektieren",
         "info":"Produkte in wachsenden Märkten mit noch geringem Marktanteil. Hoher Kapitalbedarf bei ungewisser Zukunft – können zu Stars oder Poor Dogs werden.",
         "massnahme":"Selektiv in erfolgversprechende Produkte investieren, andere abstoßen"},
        {"icon":"🐄","name":"Cash Cows","farbe":"#eff6ff","border":"#93c5fd",
         "wachstum":"Niedrig","anteil":"Hoch","strategie":"Abschöpfen",
         "info":"Starke Marktposition in reifen, wachstumsschwachen Märkten. Erwirtschaften hohe Überschüsse bei geringem Investitionsbedarf und finanzieren andere Bereiche.",
         "massnahme":"Gewinne abschöpfen, zur Finanzierung von Stars und Question Marks nutzen"},
        {"icon":"🐕","name":"Poor Dogs","farbe":"#fff1f2","border":"#fca5a5",
         "wachstum":"Niedrig","anteil":"Niedrig","strategie":"Desinvestieren",
         "info":"Schwache Position in stagnierenden Märkten. Binden Ressourcen ohne nennenswerten Ertrag. Empfehlung ist meist der geordnete Rückzug aus dem Markt.",
         "massnahme":"Marktaustritt planen, Ressourcen für Stars und Question Marks freigeben"},
    ]
    cards_html = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;align-items:stretch;margin-bottom:1rem;">'
    for info in bcg_theory:
        cards_html += f"""
        <div style="background:{info['farbe']};border:1.5px solid {info['border']};border-radius:10px;
            padding:0.9rem;box-sizing:border-box;display:flex;flex-direction:column;">
          <div style="font-size:1.4rem;text-align:center;margin-bottom:4px;">{info['icon']}</div>
          <b style="font-size:0.9rem;">{info['name']}</b>
          <p style="font-size:0.73rem;color:#334155;margin:6px 0 3px;">
            <b>Marktwachstum:</b> {info['wachstum']}<br/>
            <b>Marktanteil:</b> {info['anteil']}<br/>
            <b>Normstrategie:</b> {info['strategie']}</p>
          <p style="font-size:0.72rem;color:#475569;margin:4px 0;">{info['info']}</p>
          <p style="font-size:0.72rem;color:#1e40af;margin:4px 0;"><b>Maßnahme:</b> {info['massnahme']}</p>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

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
        do_autosave()  # Speichern OHNE rerun!
        st.rerun()

    def bcg_add():
        nid = max([x['id'] for x in st.session_state.bcg_liste], default=0)+1
        st.session_state.bcg_liste.append(
            {'id':nid,'Produkt':'','wachstum_text':'','anteil_text':'','ei_feld':'-'})

    if not st.session_state.bcg_liste:
        bcg_add()

    st.subheader("📋 Produkte einordnen")
    st.markdown("""
    <div class="hint-box">
    Beschreibe Marktwachstum und Marktanteil in eigenen Worten (z.B. „hoch", „gering", „stagnierend")
    und wähle das passende BCG-Feld. Die Matrix unten aktualisiert sich sofort.
    </div>
    """, unsafe_allow_html=True)

    COL_BCG = [2.0, 1.2, 1.2, 1.6, 0.55]
    hdr_b = "<div class='table-header'>"
    for r, h in zip(COL_BCG, ["Produkt", "Marktwachstum", "Rel. Marktanteil", "Mein BCG-Feld", "Aktion"]):
        hdr_b += f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr_b += "</div>"
    st.markdown(hdr_b, unsafe_allow_html=True)

    bcg = st.session_state.bcg_liste
    
    # Optimierung: Nach dem Rendern speichern, nicht vorher!
    should_save_later = False
    
    for item in bcg:
        with st.container(border=True):
            cols = st.columns(COL_BCG, gap="small")
            with cols[0]:
                new_val = st.text_input("P", value=item['Produkt'],
                    key=f"bcg_p_{item['id']}", label_visibility="collapsed", placeholder="Produktname …")
                if new_val != item['Produkt']:
                    item['Produkt'] = new_val
                    should_save_later = True
            with cols[1]:
                new_val = st.text_input("W", value=item.get('wachstum_text', ''),
                    key=f"bcg_w_{item['id']}", label_visibility="collapsed", placeholder="z.B. hoch, gering …")
                if new_val != item.get('wachstum_text', ''):
                    item['wachstum_text'] = new_val
                    should_save_later = True
            with cols[2]:
                new_val = st.text_input("A", value=item.get('anteil_text', ''),
                    key=f"bcg_a_{item['id']}", label_visibility="collapsed", placeholder="z.B. hoch, niedrig …")
                if new_val != item.get('anteil_text', ''):
                    item['anteil_text'] = new_val
                    should_save_later = True
            with cols[3]:
                fi = FELDER_OPT.index(item.get('ei_feld', '-')) if item.get('ei_feld', '-') in FELDER_OPT else 0
                new_val = st.selectbox("F", options=FELDER_OPT, index=fi,
                    key=f"bcg_f_{item['id']}", label_visibility="collapsed")
                if new_val != item.get('ei_feld', '-'):
                    item['ei_feld'] = new_val
                    should_save_later = True
            with cols[4]:
                _, mid, _ = st.columns([0.3, 1, 0.3])
                with mid:
                    if st.button("✕", key=f"bcg_del_{item['id']}", disabled=(len(bcg) <= 1),
                                 use_container_width=False):
                        st.session_state.bcg_liste = [x for x in bcg if x['id'] != item['id']]
                        do_autosave(force=True); st.rerun()

    if st.button("➕ Produkt hinzufügen", key="bcg_add"):
        bcg_add(); do_autosave(force=True); st.rerun()
    
    # Am Ende: Speichern wenn nötig (lazy save)
    if should_save_later:
        do_autosave()

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
        bcg_box("❓ Question Marks", "#fefce8", felder["❓ Question Mark"], "Selektieren")
        bcg_box("🐕 Poor Dogs",      "#fff1f2", felder["🐕 Poor Dog"],      "Desinvestieren")
    with right_col:
        bcg_box("⭐ Stars",    "#f0fdf4", felder["⭐ Star"],    "Investieren")
        bcg_box("🐄 Cash Cows","#eff6ff", felder["🐄 Cash Cow"],"Abschöpfen")
    st.markdown("""<div style="font-size:0.8rem;color:#64748b;text-align:center;margin-top:4px;font-weight:600;">
        ↓ Niedriges Marktwachstum</div>""", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── PDF-Export mit Matrix-Bild ──
    def build_bcg_pdf():
        pdf = FPDF(); pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Portfoliomatrix (BCG) - Auswertung", ln=True, align="C"); pdf.ln(3)

        # BCG-Matrix als Bild einbetten
        img_path = create_bcg_matrix_png(felder)
        if img_path:
            try:
                # Zentriert, etwas breiter für bessere Lesbarkeit
                pdf.image(img_path, x=15, y=None, w=180)
                pdf.ln(6)
            except Exception:
                pass
            finally:
                try: os.unlink(img_path)
                except Exception: pass

        # Tabelle – Emojis vollständig entfernen (verhindert doppelte Bezeichnungen)
        def clean_feld(s):
            return (s.replace("⭐ Star", "Star")
                     .replace("❓ Question Mark", "Question Mark")
                     .replace("🐄 Cash Cow", "Cash Cow")
                     .replace("🐕 Poor Dog", "Poor Dog")
                     .replace("⭐", "").replace("❓", "")
                     .replace("🐄", "").replace("🐕", "").strip())

        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(226, 232, 240)
        # Spalten: Produkt 65 | Marktwachstum 45 | Rel. Anteil 40 | BCG-Feld 40  = 190 mm
        for h, w in zip(["Produkt", "Marktwachstum", "Rel. Marktanteil", "BCG-Feld"],
                        [65, 55, 45, 35]):
            pdf.cell(w, 8, h, border=1, align="C", fill=True)
        pdf.ln(); pdf.set_font("Arial", '', 9)
        for item in bcg:
            if not item['Produkt']: continue
            pdf.cell(65, 8, safe_str(item['Produkt']), border=1)
            pdf.cell(50, 8, safe_str(item.get('wachstum_text', '')), border=1)
            pdf.cell(50, 8, safe_str(item.get('anteil_text', '')), border=1)
            pdf.cell(35, 8, safe_str(clean_feld(item.get('ei_feld', '-'))), border=1, align="C")
            pdf.ln()
        return pdf_output(pdf)

    pdf_download_button("📄 Portfolio als PDF (mit Matrix)", build_bcg_pdf, "Portfoliomatrix.pdf")


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

    # ── Theorie: ABC-Klassen direkt sichtbar ──
    st.subheader("📋 ABC-Klassen im Detail")
    abc_theory = [
        {"icon":"🥇","name":"A-Artikel","farbe":"#f0fdf4","border":"#86efac",
         "anteil_art":"ca. 10–20 %","anteil_ums":"ca. 70–80 %",
         "info":"Wenige, besonders umsatzstarke Artikel. Sie machen den Großteil des Gesamtumsatzes aus und sind für das Unternehmen unverzichtbar.",
         "massnahme":"Hohe Lagerpriorität, enge Kontrolle, sichere Verfügbarkeit gewährleisten"},
        {"icon":"🥈","name":"B-Artikel","farbe":"#fefce8","border":"#fde047",
         "anteil_art":"ca. 30–40 %","anteil_ums":"ca. 15–25 %",
         "info":"Artikel mit mittlerer Umsatzbedeutung. Regelmäßige Überprüfung sinnvoll – Potenzial für Aufstieg in die A-Klasse oder Abstieg in C.",
         "massnahme":"Standard-Controlling, Entwicklung beobachten, Potenzial prüfen"},
        {"icon":"🥉","name":"C-Artikel","farbe":"#fff1f2","border":"#fca5a5",
         "anteil_art":"ca. 50–60 %","anteil_ums":"ca. 5–10 %",
         "info":"Viele Artikel mit geringem Umsatzbeitrag. Binden Lagerkapazität, Kapital und Verwaltungsaufwand ohne nennenswerten Ertrag.",
         "massnahme":"Vereinfachte Verwaltung, Sortimentsbereinigung prüfen, Bestellmengen reduzieren"},
    ]
    abc_cards_html = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.6rem;align-items:stretch;margin-bottom:1rem;">'
    for info in abc_theory:
        abc_cards_html += f"""
        <div style="background:{info['farbe']};border:1.5px solid {info['border']};border-radius:10px;
            padding:0.9rem;box-sizing:border-box;display:flex;flex-direction:column;">
          <div style="font-size:1.4rem;text-align:center;margin-bottom:4px;">{info['icon']}</div>
          <b style="font-size:0.9rem;">{info['name']}</b>
          <p style="font-size:0.73rem;color:#334155;margin:6px 0 3px;">
            <b>Anteil Artikel:</b> {info['anteil_art']}<br/>
            <b>Anteil Umsatz:</b> {info['anteil_ums']}</p>
          <p style="font-size:0.72rem;color:#475569;margin:4px 0;">{info['info']}</p>
          <p style="font-size:0.72rem;color:#1e40af;margin:4px 0;"><b>Maßnahme:</b> {info['massnahme']}</p>
        </div>"""
    abc_cards_html += '</div>'
    st.markdown(abc_cards_html, unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)

    with st.expander("⚙️ Klassengrenzen festlegen", expanded=True):
        cg1, cg2, cg3 = st.columns(3)
        with cg1:
            grenze_a = st.number_input("A-Klasse bis (kumuliert %)", value=80, min_value=1,
                                        max_value=99, step=1, key="abc_ga")
        with cg2:
            grenze_b = st.number_input("B-Klasse bis (kumuliert %)", value=95,
                                        min_value=grenze_a+1, max_value=99, step=1, key="abc_gb")
        with cg3:
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
        do_autosave(force=True); st.rerun()

    def abc_move(index, direction):
        l = st.session_state.abc_liste
        if direction=='up' and index>0: l[index],l[index-1] = l[index-1],l[index]
        elif direction=='down' and index<len(l)-1: l[index],l[index+1] = l[index+1],l[index]

    def abc_add():
        nid = max([x['id'] for x in st.session_state.abc_liste], default=0) + 1
        st.session_state.abc_liste.append({'id':nid,'Artikel':'','Menge':0,'Preis':0.0,
                                            'ei_ums':0.0,'ei_ant':0.0,'ei_kum':0.0,'ei_kl':'-'})

    if not st.session_state.abc_liste:
        abc_add()

    COL = [0.5,1.8,0.9,0.9,1.1,0.9,0.9,0.9,1.2]
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
                cu, cd, cx = st.columns(3)
                if cu.button("↑", key=f"abc_up_{item['id']}", disabled=(i==0), use_container_width=True):
                    abc_move(i,'up'); do_autosave(force=True); st.rerun()
                if cd.button("↓", key=f"abc_dn_{item['id']}", disabled=(i==len(current)-1), use_container_width=True):
                    abc_move(i,'down'); do_autosave(force=True); st.rerun()
                if cx.button("✕", key=f"abc_del_{item['id']}", disabled=(len(current)<=1), use_container_width=False):
                    st.session_state.abc_liste = [x for x in current if x['id'] != item['id']]
                    do_autosave(force=True); st.rerun()

    ca, _ = st.columns([2, 5])
    with ca:
        if st.button("➕ Artikel hinzufügen", use_container_width=True):
            abc_add(); do_autosave(force=True); st.rerun()

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

    # ── PDF-Export (Querformat für mehr Platz bei Artikelbezeichnungen) ──
    def build_abc_pdf():
        # Querformat: A4 landscape = 297 × 210 mm → nutzbare Breite ~277 mm
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "ABC-Analyse - Auswertung", ln=True, align="C"); pdf.ln(4)
        pdf.set_font("Arial", '', 10)
        # Grenzen aus Session State holen (falls nicht verfügbar, Defaults nutzen)
        _grenze_a = st.session_state.get('abc_ga', 80)
        _grenze_b = st.session_state.get('abc_gb', 95)
        pdf.cell(0, 6, f"Klassengrenzen: A bis {_grenze_a}%  |  B bis {_grenze_b}%  |  C bis 100%",
                 ln=True, align="C"); pdf.ln(4)

        # Aktuelle Daten aus Session State
        _current = st.session_state.get('abc_liste', [])
        
        # Pareto-Diagramm (Schüler-Eingaben) einbetten
        pareto_path = create_abc_pareto_png(_current)
        if pareto_path:
            try:
                pdf.image(pareto_path, x=10, y=None, w=270)
                pdf.ln(4)
            except Exception:
                pass
            finally:
                try: os.unlink(pareto_path)
                except Exception: pass

        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(226, 232, 240)
        # Spaltenbreiten (Summe = 275 mm)
        cols_w = [10, 85, 22, 32, 38, 26, 26, 20]
        cols_h = ["Nr.", "Artikel", "Menge", "Preis (EUR)", "Umsatz (EUR)", "Anteil %", "Kum. %", "Klasse"]
        for h, w in zip(cols_h, cols_w):
            pdf.cell(w, 8, h, border=1, align="C", fill=True)
        pdf.ln(); pdf.set_font("Arial", '', 9)
        for i, item in enumerate(_current):
            if not item['Artikel']: continue
            # Nur Schüler-Eingaben exportieren – keine berechneten Vergleichswerte
            pdf.cell(10, 8, f"{i+1}.", border=1, align="C")
            pdf.cell(85, 8, safe_str(item.get('Artikel', '-')), border=1)
            pdf.cell(22, 8, str(item.get('Menge', 0)), border=1, align="R")
            pdf.cell(32, 8, fmt_de(item.get('Preis', 0)), border=1, align="R")
            pdf.cell(38, 8, fmt_de(item.get('ei_ums', 0.0)), border=1, align="R")
            pdf.cell(26, 8, fmt_de(item.get('ei_ant', 0.0)) + " %", border=1, align="R")
            pdf.cell(26, 8, fmt_de(item.get('ei_kum', 0.0)) + " %", border=1, align="R")
            pdf.cell(20, 8, str(item.get('ei_kl', '-')), border=1, align="C"); pdf.ln()
        return pdf_output(pdf)

    pdf_download_button("📄 ABC-Analyse als PDF (Querformat)", build_abc_pdf, "ABC_Analyse.pdf")


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

    # ── Theorie: Renner-Penner-Typen direkt sichtbar ──
    st.subheader("📋 Renner-Penner-Typen im Detail")
    rp_theory = [
        {"icon":"🏆","name":"Renner","farbe":"#f0fdf4","border":"#86efac",
         "absatz":"Hoch","db":"Hoch",
         "info":"Die erfolgreichsten Produkte im Sortiment: hoher Absatz kombiniert mit hohem Deckungsbeitrag. Sie sind die Tragsäulen des Unternehmens und sichern die Liquidität.",
         "massnahme":"Stärken ausbauen, Verfügbarkeit sichern, gezielt bewerben"},
        {"icon":"😴","name":"Schläfer","farbe":"#fefce8","border":"#fde047",
         "absatz":"Niedrig","db":"Hoch",
         "info":"Hohe Marge, aber zu geringe Absatzmengen. Oft handelt es sich um unbekannte oder schlecht platzierte Produkte mit ungenutztem Potenzial.",
         "massnahme":"Reaktivieren durch bessere Platzierung, Werbung oder Aktionen"},
        {"icon":"❓","name":"Fragezeichen","farbe":"#eff6ff","border":"#93c5fd",
         "absatz":"Hoch","db":"Niedrig",
         "info":"Hoher Absatz, aber kaum Gewinn. Häufig durch zu niedrige Preise oder hohe variable Kosten. Binden Kapazitäten ohne entsprechenden Ertrag.",
         "massnahme":"Preise erhöhen, Kosten senken oder Sortimentsabgang prüfen"},
        {"icon":"💀","name":"Penner","farbe":"#fff1f2","border":"#fca5a5",
         "absatz":"Niedrig","db":"Niedrig",
         "info":"Weder Absatz noch Gewinn. Binden Lagerplatz, Kapital und Personalressourcen ohne nennenswerten Beitrag zum Unternehmensergebnis.",
         "massnahme":"Aus dem Sortiment nehmen, Lagerplatz für Renner freigeben"},
    ]
    cols_rp_t = st.columns(4)
    for col, info in zip(cols_rp_t, rp_theory):
        with col:
            st.markdown(f"""
            <div style="background:{info['farbe']};border:1.5px solid {info['border']};border-radius:10px;
                padding:0.9rem;box-sizing:border-box;">
              <div style="font-size:1.4rem;text-align:center;margin-bottom:4px;">{info['icon']}</div>
              <b style="font-size:0.9rem;">{info['name']}</b>
              <p style="font-size:0.73rem;color:#334155;margin:6px 0 3px;">
                <b>Absatz:</b> {info['absatz']}<br/>
                <b>Deckungsbeitrag:</b> {info['db']}</p>
              <p style="font-size:0.72rem;color:#475569;margin:4px 0;">{info['info']}</p>
              <p style="font-size:0.72rem;color:#1e40af;margin:4px 0;"><b>Maßnahme:</b> {info['massnahme']}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # Schwellenwerte intern (nicht mehr als UI-Eingabe)
    absatz_grenze = 500
    db_grenze = 10.0

    if 'rp_liste' not in st.session_state:
        st.session_state.rp_liste = TESTDATEN_RP[:]

    def get_rp_typ(absatz, db):
        h_a = absatz >= absatz_grenze; h_d = db >= db_grenze
        if h_a and h_d:     return "Renner"
        if not h_a and h_d: return "Schlaefer"
        if h_a and not h_d: return "Fragezeichen"
        return "Penner"

    sel_rp = produkt_auswahl_widget("rp")
    if sel_rp:
        existing = [x['Produkt'] for x in st.session_state.rp_liste]
        nid = max([x['id'] for x in st.session_state.rp_liste], default=0)
        for name in sel_rp:
            if name not in existing:
                nid += 1
                st.session_state.rp_liste.append({'id':nid,'Produkt':name,'Absatz':0,'DB':0.0,'typ_eingabe':'-'})
        st.session_state.rp_liste = [x for x in st.session_state.rp_liste if x['Produkt'].strip()]
        do_autosave(force=True); st.rerun()

    def rp_add():
        nid = max([x['id'] for x in st.session_state.rp_liste], default=0)+1
        st.session_state.rp_liste.append({'id':nid,'Produkt':'','Absatz':0,'DB':0.0,'typ_eingabe':'-'})

    if not st.session_state.rp_liste:
        rp_add()

    rp = st.session_state.rp_liste
    # Dropdown-Optionen ohne Emojis (latin-1 sicher)
    typen_opt = ["-","Renner","Schlaefer","Fragezeichen","Penner"]
    typen_display = {"-":"-","Renner":"🏆 Renner","Schlaefer":"😴 Schläfer",
                     "Fragezeichen":"❓ Fragezeichen","Penner":"💀 Penner"}

    hdr_rp = "<div class='table-header'>"
    for r, h in zip([2.0, 1.0, 1.0, 1.5, 0.55], ["Produkt", "Absatz (Stk.)", "DB (EUR/Stk.)", "Mein Typ", "Aktion"]):
        hdr_rp += f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr_rp += "</div>"
    st.markdown(hdr_rp, unsafe_allow_html=True)

    for item in rp:
        with st.container(border=True):
            cols = st.columns([2.0, 1.0, 1.0, 1.5, 0.55], gap="small")
            with cols[0]: item['Produkt'] = st.text_input("P", value=item['Produkt'], key=f"rp_p_{item['id']}", label_visibility="collapsed")
            with cols[1]: item['Absatz']  = st.number_input("A", value=int(item['Absatz']), key=f"rp_a_{item['id']}", label_visibility="collapsed", step=10, min_value=0)
            with cols[2]: item['DB']      = st.number_input("D", value=float(item['DB']), key=f"rp_d_{item['id']}", label_visibility="collapsed", step=0.5, format="%.2f")
            with cols[3]:
                raw = item.get('typ_eingabe', '-')
                raw_clean = raw.replace("🏆 ","").replace("😴 ","").replace("❓ ","").replace("💀 ","").strip()
                if raw_clean not in typen_opt: raw_clean = '-'
                ti = typen_opt.index(raw_clean)
                sel = st.selectbox("T", options=typen_opt, index=ti, key=f"rp_te_{item['id']}",
                                   label_visibility="collapsed",
                                   format_func=lambda v: typen_display.get(v, v))
                item['typ_eingabe'] = sel
            with cols[4]:
                _, mid, _ = st.columns([0.3, 1, 0.3])
                with mid:
                    if st.button("✕", key=f"rp_del_{item['id']}", disabled=(len(rp) <= 1),
                                 use_container_width=False):
                        st.session_state.rp_liste = [x for x in rp if x['id'] != item['id']]
                        do_autosave(force=True); st.rerun()

    if st.button("➕ Produkt hinzufügen", key="rp_add"):
        rp_add(); do_autosave(force=True); st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)

    def build_rp_pdf():
        pdf = FPDF(); pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Renner-Penner-Liste", ln=True, align="C"); pdf.ln(6)
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(226, 232, 240)
        for h, w in zip(["Produkt","Absatz","DB (EUR/Stk.)","Mein Typ"],[70, 30, 35, 55]):
            pdf.cell(w, 8, h, border=1, align="C", fill=True)
        pdf.ln(); pdf.set_font("Arial", '', 9)
        for item in rp:
            if not item['Produkt']: continue
            pdf.cell(70, 8, safe_str(item['Produkt']), border=1)
            pdf.cell(30, 8, str(item['Absatz']), border=1, align="R")
            pdf.cell(35, 8, fmt_de(item['DB']), border=1, align="R")
            pdf.cell(55, 8, safe_str(item.get('typ_eingabe', '-')), border=1, align="C"); pdf.ln()
        return pdf_output(pdf)

    pdf_download_button("📄 Liste als PDF", build_rp_pdf, "Renner_Penner_Liste.pdf")


# ═══════════════════════════════════════════════════════════
#  MODUL: GESAMTAUSWERTUNG
# ═══════════════════════════════════════════════════════════
elif modul == "📋 Gesamtauswertung":
    st.markdown("""
    <div class="main-header">
        <h1>📋 Gesamtauswertung</h1>
        <p>Schreibe deine Bewertung zu jedem Produkt auf</p>
    </div>
    """, unsafe_allow_html=True)

    if 'bewertung_liste' not in st.session_state:
        st.session_state.bewertung_liste = TESTDATEN_BEWERTUNG[:]

    sel_bew = produkt_auswahl_widget("bew")
    if sel_bew:
        existing = [x['Produkt'] for x in st.session_state.bewertung_liste]
        nid = max([x['id'] for x in st.session_state.bewertung_liste], default=0)
        for name in sel_bew:
            if name not in existing:
                nid += 1
                st.session_state.bewertung_liste.append({'id':nid,'Produkt':name,'bewertung':''})
        st.session_state.bewertung_liste = [x for x in st.session_state.bewertung_liste if x['Produkt'].strip()]
        do_autosave(force=True); st.rerun()

    def bew_add():
        nid = max([x['id'] for x in st.session_state.bewertung_liste], default=0)+1
        st.session_state.bewertung_liste.append({'id':nid,'Produkt':'','bewertung':''})

    if not st.session_state.bewertung_liste:
        bew_add()

    bew = st.session_state.bewertung_liste

    hdr_bew = "<div class='table-header'>"
    for r, h in zip([2.0, 5.0, 0.55], ["Produkt", "Bewertung", "Aktion"]):
        hdr_bew += f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr_bew += "</div>"
    st.markdown(hdr_bew, unsafe_allow_html=True)

    for item in bew:
        with st.container(border=True):
            cols = st.columns([2.0, 5.0, 0.55], gap="small")
            with cols[0]: item['Produkt'] = st.text_input("P", value=item['Produkt'], key=f"bew_p_{item['id']}", label_visibility="collapsed")
            with cols[1]: item['bewertung'] = st.text_area("B", value=item['bewertung'], key=f"bew_t_{item['id']}", label_visibility="collapsed", height=80)
            with cols[2]:
                _, mid, _ = st.columns([0.3, 1, 0.3])
                with mid:
                    if st.button("✕", key=f"bew_del_{item['id']}", disabled=(len(bew) <= 1),
                                 use_container_width=False):
                        st.session_state.bewertung_liste = [x for x in bew if x['id'] != item['id']]
                        do_autosave(force=True); st.rerun()

    if st.button("➕ Produkt hinzufügen", key="bew_add"):
        bew_add(); do_autosave(force=True); st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)

    def build_bew_pdf():
        pdf = FPDF(orientation='L'); pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Gesamtauswertung", ln=True, align="C"); pdf.ln(4)
        pdf.set_font("Arial", '', 9)
        for item in bew:
            if not item['Produkt']: continue
            prod_text = safe_str(item['Produkt'])
            bew_text = safe_str(item['bewertung'])
            pdf.set_font("Arial", 'B', 9)
            pdf.cell(0, 6, f"Produkt: {prod_text}", ln=True, border=1)
            pdf.set_font("Arial", '', 8)
            pdf.multi_cell(0, 4, f"Bewertung:\n{bew_text}", border=1)
            pdf.ln(2)
        return pdf_output(pdf)

    pdf_download_button("📄 Auswertung als PDF", build_bew_pdf, "Gesamtauswertung.pdf")


# ═══════════════════════════════════════════════════════════
#  MODUL 5: DB-RECHNUNG
# ═══════════════════════════════════════════════════════════
elif modul == "💰 DB-Rechnung":
    st.markdown("""
    <div class="main-header">
        <h1>💰 Deckungsbeitragsrechnung</h1>
        <p>DB I und DB II selbst berechnen – Verbundartikel: Kälber-Iglu &amp; Tränkeeimer</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Theorie: Deckungsbeitrag direkt sichtbar ──
    st.subheader("📋 Deckungsbeitrag im Detail")
    db_theory = [
        {"icon":"💶","name":"DB I – Stückdeckungsbeitrag","farbe":"#f0fdf4","border":"#86efac",
         "formel":"DB I = Verkaufspreis − variable Kosten/Stk. (Einkauf + Bezug + variable Verkaufskosten)",
         "info":"Der DB I zeigt, wie viel ein einzelnes Produkt nach Abzug aller variablen Kosten zum Ergebnis beiträgt. Variable Kosten entstehen direkt durch jede verkaufte Einheit (z. B. Einkaufspreis, Fracht, Provisionen). Ein negativer DB I bedeutet: Jedes verkaufte Stück verursacht Verlust.",
         "massnahme":"Verkaufspreis erhöhen oder variable Kosten senken, wenn DB I negativ oder zu gering"},
        {"icon":"💰","name":"DB II – Stückdeckungsbeitrag nach Fixkosten","farbe":"#eff6ff","border":"#93c5fd",
         "formel":"DB II = DB I − anteilige Produktfixkosten/Stk. (Lager, Verwaltung)",
         "info":"Der DB II zieht vom DB I noch die anteiligen Produktfixkosten ab – also die Fixkosten, die einem Produkt direkt zugeordnet werden können (z. B. Lager- und Verwaltungskosten). Ist DB II negativ, deckt das Produkt nicht einmal seine zurechenbaren Fixkosten.",
         "massnahme":"Fixkosten senken oder Produkt aus dem Sortiment nehmen, wenn DB II dauerhaft negativ"},
        {"icon":"📊","name":"Verbundprodukte & Sortimentspolitik","farbe":"#fefce8","border":"#fde047",
         "formel":"Verbundeffekt: Zusatzdeckungsbeitrag aus Koppelverkäufen einrechnen",
         "info":"Manche Produkte haben einen negativen DB II, sichern aber den Verkauf anderer, margenstarker Produkte (Verbundprodukte). Hier ist der kombinierte DB beider Produkte entscheidend – nicht der isolierte Wert des Einzelprodukts.",
         "massnahme":"Verbundeffekte quantifizieren: Wie viele Iglus werden nur wegen der Eimer verkauft?"},
    ]
    db_cards_html = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.6rem;align-items:stretch;margin-bottom:1rem;">'
    for info in db_theory:
        db_cards_html += f"""
        <div style="background:{info['farbe']};border:1.5px solid {info['border']};border-radius:10px;
            padding:0.9rem;box-sizing:border-box;display:flex;flex-direction:column;">
          <div style="font-size:1.4rem;text-align:center;margin-bottom:4px;">{info['icon']}</div>
          <b style="font-size:0.9rem;">{info['name']}</b>
          <p style="font-size:0.73rem;color:#1e40af;margin:6px 0 3px;font-family:monospace;
              background:#e0f2fe;padding:4px 6px;border-radius:5px;">{info['formel']}</p>
          <p style="font-size:0.72rem;color:#475569;margin:4px 0;">{info['info']}</p>
          <p style="font-size:0.72rem;color:#1e40af;margin:4px 0;"><b>Hinweis:</b> {info['massnahme']}</p>
        </div>"""
    db_cards_html += '</div>'
    st.markdown(db_cards_html, unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)

    if 'db_produkte' not in st.session_state:
        st.session_state.db_produkte = TESTDATEN_DB[:]

    sel_db = produkt_auswahl_widget("db")
    if sel_db:
        existing = [x['Produkt'] for x in st.session_state.db_produkte]
        nid = max([x['id'] for x in st.session_state.db_produkte], default=0)
        stamm_map = {p['name']:p for p in st.session_state.stammdaten}
        for name in sel_db:
            if name not in existing:
                nid += 1
                sd = stamm_map.get(name,{})
                st.session_state.db_produkte.append({
                    'id':nid,'Produkt':name,'Preis':float(sd.get('preis',0.0)),
                    'var_k':0.0,'fix_k':0.0,'Menge':int(sd.get('absatz',0)),
                    'ei_db1':0.0,'ei_db2':0.0})
        st.session_state.db_produkte = [x for x in st.session_state.db_produkte if x['Produkt'].strip()]
        do_autosave(force=True); st.rerun()

    def db_add():
        nid = max([x['id'] for x in st.session_state.db_produkte], default=0)+1
        st.session_state.db_produkte.append({'id':nid,'Produkt':'','Preis':0.0,'var_k':0.0,
                                              'fix_k':0.0,'Menge':0,'ei_db1':0.0,'ei_db2':0.0})

    if not st.session_state.db_produkte:
        db_add()

    db_prod = st.session_state.db_produkte
    COL_DB = [1.6, 0.85, 0.85, 0.85, 0.8, 1.0, 1.1, 0.55]
    hdr_db = "<div class='table-header'>"
    for r, h in zip(COL_DB, ["Produkt", "Preis (€/Stk.)", "Var. Kosten (€/Stk.)", "Fix. Kosten (€/Stk.)", "Menge", "DB I (€/Stk.)", "DB II (€/Stk.)", "Akt."]):
        hdr_db += f"<div style='flex:{r} 1 0%;'>{h}</div>"
    hdr_db += "</div>"
    st.markdown(hdr_db, unsafe_allow_html=True)

    for item in db_prod:
        with st.container(border=True):
            cols = st.columns(COL_DB, gap="small")
            with cols[0]: item['Produkt'] = st.text_input("P",  value=item['Produkt'],                         key=f"db_p_{item['id']}",  label_visibility="collapsed")
            with cols[1]: item['Preis']   = st.number_input("Pr", value=float(item['Preis']),                  key=f"db_pr_{item['id']}", label_visibility="collapsed", step=0.5,  format="%.2f", min_value=0.0)
            with cols[2]: item['var_k']   = st.number_input("Vk", value=float(item['var_k']),                  key=f"db_vk_{item['id']}", label_visibility="collapsed", step=0.5,  format="%.2f", min_value=0.0)
            with cols[3]: item['fix_k']   = st.number_input("Fk", value=float(item.get('fix_k', 0.0)),        key=f"db_fk_{item['id']}", label_visibility="collapsed", step=0.5,  format="%.2f", min_value=0.0)
            with cols[4]: item['Menge']   = st.number_input("Me", value=int(item['Menge']),                    key=f"db_me_{item['id']}", label_visibility="collapsed", step=10,   min_value=0)
            with cols[5]: item['ei_db1']  = st.number_input("D1", value=float(item.get('ei_db1', 0.0)),       key=f"db_d1_{item['id']}", label_visibility="collapsed", step=0.5,  format="%.2f")
            with cols[6]: item['ei_db2']  = st.number_input("D2", value=float(item.get('ei_db2', 0.0)),       key=f"db_d2_{item['id']}", label_visibility="collapsed", step=0.5,  format="%.2f")
            with cols[7]:
                _, mid, _ = st.columns([0.3, 1, 0.3])
                with mid:
                    if st.button("✕", key=f"db_del_{item['id']}", disabled=(len(db_prod) <= 1),
                                 use_container_width=False):
                        st.session_state.db_produkte = [x for x in db_prod if x['id'] != item['id']]
                        do_autosave(force=True); st.rerun()

    if st.button("➕ Produkt hinzufügen", key="db_add"):
        db_add(); do_autosave(force=True); st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)

    def build_db_pdf():
        # Querformat: A4 landscape = 297 × 210 mm → nutzbare Breite ~277 mm
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Deckungsbeitragsrechnung", ln=True, align="C"); pdf.ln(3)
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 6, "DB I = Verkaufspreis - variable Kosten/Stk. (Einkauf + Bezug + Provisionen)   |   DB II = DB I - anteilige Fixkosten/Stk. (Lager, Verwaltung)",
                 ln=True, align="C"); pdf.ln(4)
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(226, 232, 240)
        # Querformat: Produkt 80 | Preis 32 | Var.K 35 | Fix.K 35 | Menge 22 | DB I 35 | DB II 35 = 274 mm
        for h, w in zip(["Produkt", "Preis (EUR/Stk.)", "Var. Kosten (EUR/Stk.)", "Fix. Kosten (EUR/Stk.)", "Menge", "DB I (EUR/Stk.)", "DB II (EUR/Stk.)"],
                        [80, 32, 35, 35, 22, 35, 35]):
            pdf.cell(w, 8, h, border=1, align="C", fill=True)
        pdf.ln(); pdf.set_font("Arial", '', 9)
        for item in db_prod:
            if not item['Produkt']: continue
            pdf.cell(80, 8, safe_str(item['Produkt']),           border=1)
            pdf.cell(32, 8, fmt_de(item['Preis']),               border=1, align="R")
            pdf.cell(35, 8, fmt_de(item['var_k']),               border=1, align="R")
            pdf.cell(35, 8, fmt_de(item.get('fix_k', 0.0)),     border=1, align="R")
            pdf.cell(22, 8, str(item['Menge']),                   border=1, align="R")
            pdf.cell(35, 8, fmt_de(item.get('ei_db1', 0.0)),    border=1, align="R")
            pdf.cell(35, 8, fmt_de(item.get('ei_db2', 0.0)),    border=1, align="R")
            pdf.ln()
        return pdf_output(pdf)

    pdf_download_button("📄 DB-Rechnung als PDF", build_db_pdf, "DB_Rechnung.pdf")

do_autosave()