import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Seitenkonfiguration ---
st.set_page_config(page_title="Break-Even-Point Simulator", layout="wide")

# --- Titel und Einleitung ---
st.title("Break-Even-Point Simulator")
st.markdown("""
Willkommen im Simulator! Hier kannst du ausprobieren, ab welcher Verkaufsmenge ein Unternehmen Gewinn macht. 
Verändere die Parameter in der Seitenleiste und beobachte, wie sich die Gewinnschwelle verschiebt.
""")

# --- Seitenleiste (Eingabefelder) ---
st.sidebar.header("⚙️ Stellschrauben")

fixkosten = st.sidebar.number_input("Fixkosten (in €)", min_value=0.0, value=5000.0, step=100.0)
var_kosten = st.sidebar.number_input("Variable Kosten je Stück (in €)", min_value=0.0, value=15.0, step=1.0)
preis = st.sidebar.number_input("Verkaufspreis je Stück (in €)", min_value=0.0, value=25.0, step=1.0)

st.sidebar.markdown("---")
max_menge = st.sidebar.slider("Betrachtete Maximalmenge (Kapazitätsgrenze)", min_value=100, max_value=5000, value=1000,
                              step=100)

# --- Berechnungen (BWL Logik) ---
deckungsbeitrag = preis - var_kosten

# Wir prüfen, ob überhaupt ein Gewinn möglich ist (Preis muss höher als var. Kosten sein)
if deckungsbeitrag > 0:
    bep_menge = fixkosten / deckungsbeitrag
    bep_umsatz = bep_menge * preis

    # --- Kennzahlen (KPIs) anzeigen ---
    st.markdown("### Deine Ergebnisse")
    col1, col2, col3 = st.columns(3)
    col1.metric("Deckungsbeitrag je Stück", f"{deckungsbeitrag:.2f} €")
    col2.metric("Break-Even-Menge", f"{bep_menge:.0f} Stück")
    col3.metric("Break-Even-Umsatz", f"{bep_umsatz:.2f} €")

    # --- Daten für das Diagramm generieren ---
    # Wir erstellen eine Liste von Mengen (X-Achse)
    mengen = list(range(0, max_menge + 1, max(1, max_menge // 50)))

    df = pd.DataFrame({
        "Menge": mengen,
        "Umsatz": [m * preis for m in mengen],
        "Gesamtkosten": [fixkosten + (m * var_kosten) for m in mengen],
        "Fixkosten": [fixkosten for m in mengen]
    })

    # --- Interaktives Diagramm mit Plotly ---
    fig = go.Figure()

    # Umsatzlinie (Grün)
    fig.add_trace(
        go.Scatter(x=df["Menge"], y=df["Umsatz"], mode='lines', name='Umsatz', line=dict(color='green', width=3)))

    # Gesamtkostenlinie (Rot)
    fig.add_trace(go.Scatter(x=df["Menge"], y=df["Gesamtkosten"], mode='lines', name='Gesamtkosten',
                             line=dict(color='red', width=3)))

    # Fixkostenlinie (Grau, gestrichelt)
    fig.add_trace(go.Scatter(x=df["Menge"], y=df["Fixkosten"], mode='lines', name='Fixkosten',
                             line=dict(color='gray', dash='dash')))

    # Break-Even-Point als Punkt markieren
    if bep_menge <= max_menge:
        fig.add_trace(go.Scatter(x=[bep_menge], y=[bep_umsatz], mode='markers', name='Break-Even-Point',
                                 marker=dict(color='black', size=12, symbol='star')))

    # Layout des Diagramms anpassen
    fig.update_layout(
        title="Umsatz- und Kostenverlauf",
        xaxis_title="Menge (Stück)",
        yaxis_title="Betrag (in €)",
        hovermode="x unified",  # Zeigt alle Werte an, wenn man mit der Maus drüberfährt
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    # Warnung, falls Preis < Variable Kosten
    st.error(
        "⚠️ **Achtung:** Der Verkaufspreis muss höher sein als die variablen Kosten, da sonst ein negativer Deckungsbeitrag entsteht. Der Break-Even-Point kann so niemals erreicht werden!")