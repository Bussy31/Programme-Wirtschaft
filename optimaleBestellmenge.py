import math
import uuid
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import json
from streamlit_local_storage import LocalStorage
import streamlit.components.v1 as components

# --- HILFSFUNKTIONEN ---
def formatiere_waehrung(wert):
    formatiert = f"{wert:,.2f}"
    return formatiert.replace(",", "X").replace(".", ",").replace("X", ".") + " €"

def formatiere_zahl(wert, dezimalstellen=0):
    formatiert = f"{wert:,.{dezimalstellen}f}"
    return formatiert.replace(",", "X").replace(".", ",").replace("X", ".")

def reset_alles():
    # 1. Speicher komplett leeren
    st.session_state.clear()

    # 2. Direkt die Nullen erzwingen, BEVOR die Seite neu lädt
    st.session_state['jahresbedarf'] = 0
    st.session_state['bestellkosten'] = 0.0
    st.session_state['einstandspreis'] = 0.0
    st.session_state['lagerkostensatz'] = 0.0
    st.session_state['mindestbestand'] = 0
    st.session_state['app_modus'] = "📝 Übungsmodus (Manuell)"
    st.session_state['uebungen_daten'] = [
        {"id": str(uuid.uuid4()), "menge": 0, "bk": 0.0, "dls": 0, "dle": 0.0, "lk": 0.0, "gk": 0.0}]

    st.session_state.daten_geladen = True

# --- CSS FÜR MAXIMALE BILDSCHIRMBREITE ---
st.markdown("""
    <style>
    /* Zwingt den Hauptbereich, die volle Breite ohne große Ränder zu nutzen */
    .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 2rem !important;
        max-width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. INITIALISIERUNG (UNZERSTÖRBARER DATENSPEICHER) ---
st.set_page_config(page_title="Bestellmengen-Profi", layout="wide")

# --- LOCAL STORAGE LADEN & INITIALISIEREN ---
localS = LocalStorage()
gespeicherte_daten = localS.getItem("bestell_v5")

if gespeicherte_daten and "daten_geladen" not in st.session_state:
    try:
        geladene_daten = json.loads(gespeicherte_daten)

        if 'uebungen_daten' in geladene_daten: st.session_state['uebungen_daten'] = geladene_daten['uebungen_daten']
        if 'sim_daten' in geladene_daten: st.session_state['sim_daten'] = geladene_daten['sim_daten']
        if 'jahresbedarf' in geladene_daten: st.session_state['jahresbedarf'] = geladene_daten['jahresbedarf']
        if 'bestellkosten' in geladene_daten: st.session_state['bestellkosten'] = geladene_daten['bestellkosten']
        if 'einstandspreis' in geladene_daten: st.session_state['einstandspreis'] = geladene_daten['einstandspreis']
        if 'lagerkostensatz' in geladene_daten: st.session_state['lagerkostensatz'] = geladene_daten['lagerkostensatz']
        if 'mindestbestand' in geladene_daten: st.session_state['mindestbestand'] = geladene_daten['mindestbestand']
        if 'app_modus' in geladene_daten: st.session_state['app_modus'] = geladene_daten['app_modus']

        st.session_state.daten_geladen = True
    except:
        pass

# DEIN GEDANKE: Wenn der Speicher leer ist (oder gelöscht wurde),
# setzen wir hier zentral unsere Standardwerte!
if 'jahresbedarf' not in st.session_state:
    st.session_state['jahresbedarf'] = 0
    st.session_state['bestellkosten'] = 0.0
    st.session_state['einstandspreis'] = 0.0
    st.session_state['lagerkostensatz'] = 0.0
    st.session_state['mindestbestand'] = 0
    st.session_state['app_modus'] = "📝 Übungsmodus (Manuell)"
    # Startwert für die Tabelle
    st.session_state['uebungen_daten'] = [
        {"id": str(uuid.uuid4()), "menge": 0, "bk": 0.0, "dls": 0, "dle": 0.0, "lk": 0.0, "gk": 0.0}]

# Speicher für den Simulator
if 'sim_daten' not in st.session_state:
    st.session_state['sim_daten'] = {
        'modus': "Bestellmenge (Stück)",
        'menge': None,
        'freq': None
    }

# Speicher für den Übungsmodus
if 'uebungen_daten' not in st.session_state:
    st.session_state['uebungen_daten'] = []
    default_mengen = [0.0, 0.0, 0.0]
    for m in default_mengen:
        st.session_state['uebungen_daten'].append({
            'id': str(uuid.uuid4()), 'm': float(m), 'h': 0.0, 'bk': 0.0,
            'dls': 0.0, 'dle': 0.0, 'lk': 0.0, 'gk': 0.0
        })

if 'geprueft' not in st.session_state:
    st.session_state['geprueft'] = False

st.title("📦 Optimale Bestellmenge")

# --- 2. RAHMENDATEN ---
st.sidebar.header("⚙️ Rahmendaten")

# NEU: Überall wurde key="..." hinzugefügt, damit der Speicher sie findet
jahresbedarf = st.sidebar.number_input("Jahresbedarf (Stück)", min_value=0, value=0, step=1000, key="jahresbedarf")
bestellkosten = st.sidebar.number_input("Kosten je Bestellvorgang (€)", min_value=0.0, value=0.0, step=10.0, key="bestellkosten")
einstandspreis = st.sidebar.number_input("Bezugspreis/Stück (€)", min_value=0.0, value=0.0, step=1.0, key="einstandspreis")
lagerkostensatz = st.sidebar.number_input("Lagerkostensatz (%)", min_value=0.0, value=0.0, step=1.0, key="lagerkostensatz")
mindestbestand = st.sidebar.number_input("Mindestbestand (Stück)", min_value=0, value=0, step=100, key="mindestbestand")

st.sidebar.divider()
app_modus = st.sidebar.radio("Haupt-Modus:", ["📝 Übungsmodus (Manuell)","🚀 Simulator (Automatik)"], key="app_modus")

st.sidebar.divider()

# --- RESET BUTTON (Der offizielle Streamlit-Weg) ---
st.sidebar.button("🔄 Alles löschen & Neu starten", use_container_width=True, on_click=reset_alles)

# --- SICHERHEITS-CHECK ---
if jahresbedarf <= 0 or einstandspreis <= 0:
    st.warning("⚠️ Bitte gib für den Jahresbedarf und den Bezugspreis Werte größer als 0 ein.")
    st.stop()

# Basisberechnung für Startwerte (Absicherung gegen Teilen durch 0)
formel_moeglich = True
if lagerkostensatz > 0:
    opt_menge_theorie = math.sqrt((200 * jahresbedarf * bestellkosten) / (einstandspreis * lagerkostensatz))
    opt_k_ges = (jahresbedarf/opt_menge_theorie)*bestellkosten + (mindestbestand + (opt_menge_theorie/2))*einstandspreis*(lagerkostensatz/100)
else:
    formel_moeglich = False
    opt_menge_theorie = float(jahresbedarf) # Fallback
    opt_k_ges = 0.0 # Fallback


# Setze Startwerte für den Simulator, falls noch leer
if st.session_state['sim_daten']['menge'] is None:
    st.session_state['sim_daten']['menge'] = float(int(opt_menge_theorie))
if st.session_state['sim_daten']['freq'] is None:
    st.session_state['sim_daten']['freq'] = float(round(jahresbedarf / opt_menge_theorie, 1))

# ==========================================
# MODUS 1: SIMULATOR
# ==========================================
if app_modus == "🚀 Simulator (Automatik)":
    st.subheader("Automatischer Simulator")

    # Der Fix gegen das Doppel-Klicken: Wir nutzen einen festen Key für den Radio-Button
    eingabe_modus = st.radio(
        "Vorgabe wählen:",
        ["Bestellmenge (Stück)", "Häufigkeit (Bestellungen/Jahr)"],
        horizontal=True,
        key="radio_fix"
    )

    if eingabe_modus == "Bestellmenge (Stück)":
        akt_menge = st.number_input("Menge wählen:", min_value=1.0, value=st.session_state['sim_daten']['menge'],
                                    step=500.0, key="input_m")
        st.session_state['sim_daten']['menge'] = akt_menge
        akt_bestellungen = jahresbedarf / akt_menge
        st.session_state['sim_daten']['freq'] = round(akt_bestellungen, 1)  # Synchronisieren
    else:
        akt_bestellungen = st.number_input("Häufigkeit wählen:", min_value=1.0,
                                           value=st.session_state['sim_daten']['freq'], step=1.0, key="input_h")
        st.session_state['sim_daten']['freq'] = akt_bestellungen
        akt_menge = jahresbedarf / akt_bestellungen
        st.session_state['sim_daten']['menge'] = akt_menge  # Synchronisieren

    # Kostenrechnung
    k_best = akt_bestellungen * bestellkosten
    k_lager = (mindestbestand + (akt_menge / 2)) * einstandspreis * (lagerkostensatz / 100)
    k_ges = k_best + k_lager
    rhythmus = int(360 / akt_bestellungen) if akt_bestellungen > 0 else 0

    # Metriken (wie gehabt)
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Menge", f"{formatiere_zahl(akt_menge)} Stk.", f"{formatiere_zahl(akt_bestellungen, 1)} Bestellungen/Jahr")
    c2.metric("⏱️ Rhythmus", f"Alle {rhythmus} Tage")
    opt_k_ges = (jahresbedarf / opt_menge_theorie) * bestellkosten + (
                mindestbestand + (opt_menge_theorie / 2)) * einstandspreis * (lagerkostensatz / 100)
    c3.metric("💶 Gesamtkosten", formatiere_waehrung(k_ges),
              delta=f"{formatiere_waehrung(k_ges - opt_k_ges)} Abweichung", delta_color="inverse")

    tab_grafik, tab_tabelle, tab_formel = st.tabs(["📉 Grafik", "🧮 Tabelle", "📝 Berechnung"])

    with tab_grafik:
        # Daten für das Diagramm berechnen
        max_x = int(opt_menge_theorie * 2.5)
        schritt = max(100, max_x // 50)
        m_range = list(range(schritt, max_x, schritt))

        y_ges = [
            (jahresbedarf / m) * bestellkosten + (mindestbestand + (m / 2)) * einstandspreis * (lagerkostensatz / 100)
            for m in m_range]
        y_bestell = [(jahresbedarf / m) * bestellkosten for m in m_range]
        y_lager = [(mindestbestand + (m / 2)) * einstandspreis * (lagerkostensatz / 100) for m in m_range]

        fig = go.Figure()
        # Kurven
        fig.add_trace(go.Scatter(x=m_range, y=y_ges, name="Gesamtkosten", line=dict(color='blue', width=3)))
        fig.add_trace(go.Scatter(x=m_range, y=y_bestell, name="Bestellkosten", line=dict(dash='dash', color='gray')))
        fig.add_trace(go.Scatter(x=m_range, y=y_lager, name="Lagerkosten", line=dict(dash='dash', color='orange')))

        # DER AKTUELLE PUNKT (Dein gewählter Wert)
        fig.add_trace(go.Scatter(
            x=[akt_menge], y=[k_ges],
            mode="markers+text",
            name="Deine Wahl",
            text=[f"Hier: {formatiere_zahl(akt_menge)} Stk."],
            textposition="top center",
            marker=dict(color='red', size=12, symbol="diamond")
        ))

        # Layout-Anpassungen
        # Layout-Anpassungen (Im Plotly-Teil)
        fig.update_layout(
            hovermode="x unified",
            separators=",.",
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(title="Bestellmenge (Stück)", tickformat=","),
            # WICHTIG: Wenn opt_k_ges 0 ist, schalten wir das Limit ab (None)
            yaxis=dict(title="Gesamtkosten (€)", tickformat=",", range=[0, opt_k_ges * 2.5] if opt_k_ges > 0 else None)
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab_tabelle:
        t_data = [[n, jahresbedarf / n, n * bestellkosten,
                   (mindestbestand + (jahresbedarf / n / 2)) * einstandspreis * (lagerkostensatz / 100)] for n in
                  range(max(1, int(akt_bestellungen) - 5), int(akt_bestellungen) + 10)]
        df_tab = pd.DataFrame(t_data, columns=["Bestellungen", "Menge", "Bestellk.", "Lagerk."])
        df_tab["Gesamtk."] = df_tab["Bestellk."] + df_tab["Lagerk."]
        st.dataframe(df_tab.style.format(
            {"Menge": "{:,.0f}", "Bestellk.": "{:,.2f} €", "Lagerk.": "{:,.2f} €", "Gesamtk.": "{:,.2f} €"}),
                     use_container_width=True)

    with tab_formel:
        if not formel_moeglich:
            st.warning("⚠️ Die Andler-Formel kann nicht angewendet werden, da der Lagerkostensatz 0% beträgt (Teilen durch Null ist nicht möglich).")
        else:
            st.subheader("Rechenweg (Andler-Formel)")
            st.markdown(f"""
            **Legende der Variablen:**
            * **$B$** (Jahresbedarf): **{formatiere_zahl(jahresbedarf)} Stück**
            * **$K_f$** (Bestellfixe Kosten): **{formatiere_waehrung(bestellkosten)}**
            * **$p$** (Einstandspreis): **{formatiere_waehrung(einstandspreis)}**
            * **$l$** (Lagerkostensatz): **{formatiere_zahl(lagerkostensatz, 1)} %**
            """)
            st.write("---")
            st.markdown("**1. Formel:**")
            st.markdown(r"$\displaystyle x_{opt} = \sqrt{\frac{200 \cdot B \cdot K_f}{p \cdot l}}$")
            st.markdown("**2. Einsetzen:**")
            st.markdown(rf"$\displaystyle x_{{opt}} = \sqrt{{\frac{{200 \cdot {jahresbedarf} \cdot {bestellkosten}}}{{{einstandspreis} \cdot {lagerkostensatz}}}}}$")
            st.markdown("**3. Zwischenschritt:**")
            st.markdown(rf"$\displaystyle x_{{opt}} = \sqrt{{\frac{{{200 * jahresbedarf * bestellkosten}}}{{{einstandspreis * lagerkostensatz}}}}}$")
            st.write("---")
            st.success(f"Optimale Bestellmenge: **{formatiere_zahl(opt_menge_theorie, 2)} Stück**")

# ==========================================
# MODUS 2: ÜBUNGSMODUS
# ==========================================
else:
    st.subheader("📝 Übungsmodus")

    with st.expander("➕ Neue Zeile hinzufügen"):
        n_menge = st.number_input("Start-Menge:", min_value=0.0, value=0.0, step=500.0)
        if st.button("Hinzufügen"):
            st.session_state['uebungen_daten'].append({
                'id': str(uuid.uuid4()), 'm': float(n_menge), 'h': 0.0, 'bk': 0.0,
                'dls': 0.0, 'dle': 0.0, 'lk': 0.0, 'gk': 0.0
            })
            st.rerun()

    cols = st.columns([1.2, 0.9, 1.1, 1.1, 1.1, 1.1, 1.1, 2.0])
    labels = ["Menge", "Häufigkeit", "Bestellkosten", "Ø Lager (Stk)", "Ø Lager (€)", "Lagerkosten", "Gesamtkosten", "Aktionen"]
    for col, label in zip(cols, labels): col.write(f"**{label}**")

    for i, row in enumerate(st.session_state['uebungen_daten']):
        c = st.columns([1.2, 0.9, 1.1, 1.1, 1.1, 1.1, 1.1, 2.0])

        # Eingaben holen sich den Wert aus der Datenbank UND schreiben ihn direkt zurück
        row['m'] = c[0].number_input("M", value=float(row['m']), key=f"m_{row['id']}", label_visibility="collapsed",
                                     step=500.0)
        row['h'] = c[1].number_input("H", value=float(row['h']), key=f"h_{row['id']}", label_visibility="collapsed",
                                     format="%.1f", step=0.1)
        row['bk'] = c[2].number_input("BK", value=float(row['bk']), key=f"bk_{row['id']}", label_visibility="collapsed",
                                      step=10.0)
        row['dls'] = c[3].number_input("DLS", value=float(row['dls']), key=f"dls_{row['id']}",
                                       label_visibility="collapsed", step=100.0)
        row['dle'] = c[4].number_input("DLE", value=float(row['dle']), key=f"dle_{row['id']}",
                                       label_visibility="collapsed", step=100.0)
        row['lk'] = c[5].number_input("LK", value=float(row['lk']), key=f"lk_{row['id']}", label_visibility="collapsed",
                                      step=10.0)
        row['gk'] = c[6].number_input("GK", value=float(row['gk']), key=f"gk_{row['id']}", label_visibility="collapsed",
                                      step=10.0)

        # Berechnung der Korrekturwerte (Soll)
        k_h = jahresbedarf / row['m'] if row['m'] > 0 else 0
        k_bk = k_h * bestellkosten
        k_dls = (row['m'] / 2) + mindestbestand
        k_dle = k_dls * einstandspreis
        k_lk = k_dle * (lagerkostensatz / 100)
        k_gk = k_bk + k_lk

        with c[7]:
            b1, b2, b3, feedback = st.columns([1, 1, 1, 2])

            # Pfeil hoch ist ausgegraut, wenn es die allererste Zeile (Index 0) ist
            if b1.button("↑", key=f"up_{row['id']}", disabled=(i == 0)):
                st.session_state['uebungen_daten'][i], st.session_state['uebungen_daten'][i - 1] = \
                    st.session_state['uebungen_daten'][i - 1], st.session_state['uebungen_daten'][i]
                st.rerun()

            # Pfeil runter ist ausgegraut, wenn es die letzte Zeile der Liste ist
            if b2.button("↓", key=f"dn_{row['id']}", disabled=(i == len(st.session_state['uebungen_daten']) - 1)):
                st.session_state['uebungen_daten'][i], st.session_state['uebungen_daten'][i + 1] = \
                    st.session_state['uebungen_daten'][i + 1], st.session_state['uebungen_daten'][i]
                st.rerun()

            if b3.button("🗑️", key=f"del_{row['id']}"):
                st.session_state['uebungen_daten'].pop(i)
                st.rerun()

            if st.session_state['geprueft']:
                korrekt = (abs(row['h'] - k_h) < 0.1 and abs(row['bk'] - k_bk) < 1.0 and
                           abs(row['dls'] - k_dls) < 1.0 and abs(row['dle'] - k_dle) < 1.0 and
                           abs(row['lk'] - k_lk) < 1.0 and abs(row['gk'] - k_gk) < 1.0)
                icon = "✅" if korrekt else "❌"
                feedback.markdown(
                    f"<div style='display:flex; justify-content:center; align-items:center; height:100%; font-size:24px;'>{icon}</div>",
                    unsafe_allow_html=True)

    st.write("---")

    # --- DATEN-EXPORT (PDF) VORBEREITEN ---
    def erstelle_pdf(daten):
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Optimale Bestellmenge - Übungsergebnisse", ln=True, align="C")
        pdf.ln(5)

        # Spaltenkoepfe formatieren
        pdf.set_font("Arial", "B", 10)
        cols = [25, 25, 35, 35, 40, 35, 40]
        headers = ["Menge", "Haeufigk.", "Bestellkosten", "Lager (Stk)", "Lager (EUR)", "Lagerkosten", "Gesamtkosten"]

        for i, h in enumerate(headers):
            pdf.cell(cols[i], 10, h, border=1, align="C")
        pdf.ln()

        # Daten eintragen
        pdf.set_font("Arial", "", 10)
        for row in daten:
            pdf.cell(cols[0], 10, f"{row['m']:.0f}", border=1, align="C")
            pdf.cell(cols[1], 10, f"{row['h']:.1f}", border=1, align="C")
            pdf.cell(cols[2], 10, f"{row['bk']:,.2f} EUR".replace(',', 'X').replace('.', ',').replace('X', '.'),
                     border=1, align="C")
            pdf.cell(cols[3], 10, f"{row['dls']:.0f}", border=1, align="C")
            pdf.cell(cols[4], 10, f"{row['dle']:,.2f} EUR".replace(',', 'X').replace('.', ',').replace('X', '.'),
                     border=1, align="C")
            pdf.cell(cols[5], 10, f"{row['lk']:,.2f} EUR".replace(',', 'X').replace('.', ',').replace('X', '.'),
                     border=1, align="C")
            pdf.cell(cols[6], 10, f"{row['gk']:,.2f} EUR".replace(',', 'X').replace('.', ',').replace('X', '.'),
                     border=1, align="C")
            pdf.ln()

        # PDF sicher konvertieren (kompatibel mit FPDF 1 und 2)
        try:
            return pdf.output(dest="S").encode("latin-1")
        except TypeError:
            return bytes(pdf.output())


    pdf_daten = erstelle_pdf(st.session_state['uebungen_daten'])

    # --- BUTTONS (UNTEREINANDER) ---
    if st.button("Ergebnisse prüfen", type="primary"):
        st.session_state['geprueft'] = True
        st.rerun()

    if st.session_state['geprueft']:
        if st.button("Korrekturmodus aus"):
            st.session_state['geprueft'] = False
            st.rerun()

    st.download_button(
        label="📥 Als PDF exportieren",
        data=pdf_daten,
        file_name="bestellmenge_uebung.pdf",
        mime="application/pdf"
    )

# --- AUTOMATISCHES SPEICHERN ---
speicher_dict = {
    "uebungen_daten": st.session_state.get('uebungen_daten'),
    "sim_daten": st.session_state.get('sim_daten'),
    "jahresbedarf": st.session_state.get('jahresbedarf'),
    "bestellkosten": st.session_state.get('bestellkosten'),
    "einstandspreis": st.session_state.get('einstandspreis'),
    "lagerkostensatz": st.session_state.get('lagerkostensatz'),
    "mindestbestand": st.session_state.get('mindestbestand'),
    "app_modus": st.session_state.get('app_modus')
}

aktuelle_daten = json.dumps(speicher_dict)
if aktuelle_daten != gespeicherte_daten:
    localS.setItem("bestell_v5", aktuelle_daten)