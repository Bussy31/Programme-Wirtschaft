import math
import uuid
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- HILFSFUNKTIONEN ---
def formatiere_waehrung(wert):
    formatiert = f"{wert:,.2f}"
    return formatiert.replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def formatiere_zahl(wert, dezimalstellen=0):
    formatiert = f"{wert:,.{dezimalstellen}f}"
    return formatiert.replace(",", "X").replace(".", ",").replace("X", ".")


# --- 1. INITIALISIERUNG (UNZERSTÖRBARER DATENSPEICHER) ---
st.set_page_config(page_title="Bestellmengen-Profi", layout="wide")

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
    default_mengen = [15000.0, 10000.0, 5000.0]
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
jahresbedarf = st.sidebar.number_input("Jahresbedarf (Stück)", min_value=1, value=240000, step=1000)
bestellkosten = st.sidebar.number_input("Kosten je Bestellvorgang (€)", min_value=1.0, value=500.0, step=10.0)
einstandspreis = st.sidebar.number_input("Bezugspreis/Stück (€)", min_value=0.1, value=40.0, step=1.0)
lagerkostensatz = st.sidebar.number_input("Lagerkostensatz (%)", min_value=0.1, value=8.0, step=0.5)
mindestbestand = st.sidebar.number_input("Mindestbestand (Stück)", min_value=0, value=2000, step=100)

st.sidebar.divider()
app_modus = st.sidebar.radio("Haupt-Modus:", ["🚀 Simulator (Automatik)", "📝 Übungsmodus (Manuell)"])

# Basisberechnung für Startwerte
opt_menge_theorie = math.sqrt((200 * jahresbedarf * bestellkosten) / (einstandspreis * lagerkostensatz))

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
    c1.metric("📦 Menge", f"{formatiere_zahl(akt_menge)} Stk.", f"{formatiere_zahl(akt_bestellungen, 1)} x p.a.")
    c2.metric("⏱️ Rhythmus", f"Alle {rhythmus} Tage")
    opt_k_ges = (jahresbedarf / opt_menge_theorie) * bestellkosten + (
                mindestbestand + (opt_menge_theorie / 2)) * einstandspreis * (lagerkostensatz / 100)
    c3.metric("💶 Gesamtkosten", formatiere_waehrung(k_ges),
              delta=f"{formatiere_waehrung(k_ges - opt_k_ges)} Abweichung", delta_color="inverse")

    tab_grafik, tab_tabelle, tab_formel = st.tabs(["📉 Grafik", "🧮 Tabelle", "📝 Berechnung"])

    with tab_grafik:
        # Daten für das Diagramm berechnen (Bereich eingrenzen auf 2x die Optimalmenge)
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

        # Layout-Anpassungen (Achsenbeschriftung & Deutsch-Format)
        fig.update_layout(
            hovermode="x unified",
            separators=",.",  # HIER GEHÖRT ES HIN (Komma für Dezimal, Punkt für Tausender)
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(title="Bestellmenge (Stück)", tickformat=","),
            yaxis=dict(title="Gesamtkosten (€)", tickformat=",")
        )
        st.plotly_chart(fig, use_container_width=True)
# ==========================================
# MODUS 2: ÜBUNGSMODUS
# ==========================================
else:
    st.subheader("📝 Übungsmodus")

    with st.expander("➕ Neue Zeile hinzufügen"):
        n_menge = st.number_input("Start-Menge:", min_value=1.0, value=9000.0, step=500.0)
        if st.button("Hinzufügen"):
            st.session_state['uebungen_daten'].append({
                'id': str(uuid.uuid4()), 'm': float(n_menge), 'h': 0.0, 'bk': 0.0,
                'dls': 0.0, 'dle': 0.0, 'lk': 0.0, 'gk': 0.0
            })
            st.rerun()

    cols = st.columns([1.2, 0.9, 1.1, 1.1, 1.1, 1.1, 1.1, 2.0])
    labels = ["Menge", "Häufigk.", "Bestellk.", "Ø Lager(Stk)", "Ø Lager(€)", "Lagerk.", "Gesamtk.", "Aktionen"]
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

            if b1.button("⬆️", key=f"up_{row['id']}") and i > 0:
                st.session_state['uebungen_daten'][i], st.session_state['uebungen_daten'][i - 1] = \
                st.session_state['uebungen_daten'][i - 1], st.session_state['uebungen_daten'][i]
                st.rerun()
            if b2.button("⬇️", key=f"dn_{row['id']}") and i < len(st.session_state['uebungen_daten']) - 1:
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
    if st.button("Ergebnisse prüfen", type="primary"):
        st.session_state['geprueft'] = True
        st.rerun()
    if st.session_state['geprueft']:
        if st.button("Korrekturmodus aus"):
            st.session_state['geprueft'] = False
            st.rerun()