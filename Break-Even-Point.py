import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Seitenkonfiguration ---
st.set_page_config(page_title="Break-Even-Point Simulator", layout="wide")

# --- Titel und Einleitung ---
st.title("📈 Break-Even-Point Simulator")
st.markdown("""
Willkommen im Simulator! Hier kannst du ausprobieren, ab welcher Verkaufsmenge ein Unternehmen Gewinn macht. 
Verändere die Parameter in der Seitenleiste und beobachte, wie sich die Gewinnschwelle verschiebt.
""")

# --- Seitenleiste (Eingabefelder) ---
st.sidebar.header("⚙️ Basis-Stellschrauben")

fixkosten = st.sidebar.number_input("Fixkosten (in €)", min_value=0.0, value=5000.0, step=100.0)
var_kosten = st.sidebar.number_input("Variable Kosten je Stück (in €)", min_value=0.0, value=15.0, step=1.0)
preis = st.sidebar.number_input("Regulärer Verkaufspreis je Stück (in €)", min_value=0.0, value=25.0, step=1.0)

st.sidebar.markdown("---")

# --- Erweiterte Optionen ---
st.sidebar.header("🚀 Erweiterte Optionen")
rabatt = st.sidebar.slider("Kundenrabatt (in %)", min_value=0, max_value=80, value=0, step=1)
zielgewinn = st.sidebar.number_input("Wunsch-Zielgewinn (in €)", min_value=0.0, value=0.0, step=500.0)

st.sidebar.markdown("---")

# NEU: number_input statt slider, damit keine Grenze mehr existiert!
max_menge = st.sidebar.number_input("Betrachtete Maximalmenge (Kapazitätsgrenze)", min_value=100, value=1000, step=100)

# --- Berechnungen (BWL Logik) ---
# Rabatt abziehen
effektiver_preis = preis * (1 - (rabatt / 100))
deckungsbeitrag = effektiver_preis - var_kosten

# Wir prüfen, ob überhaupt ein Gewinn möglich ist
if deckungsbeitrag > 0:
    # Break-Even-Berechnung (Gewinn = 0)
    bep_menge = fixkosten / deckungsbeitrag
    bep_umsatz = bep_menge * effektiver_preis

    # Zielgewinn-Berechnung
    ziel_menge = (fixkosten + zielgewinn) / deckungsbeitrag
    ziel_umsatz = ziel_menge * effektiver_preis

    # --- Kennzahlen (KPIs) anzeigen ---
    st.markdown("### 📊 Deine Ergebnisse")

    # Optischer Hinweis, wenn Rabatt gewährt wird
    if rabatt > 0:
        st.info(
            f"💡 **Rabatt aktiv!** Der tatsächliche Verkaufspreis sinkt auf **{effektiver_preis:.2f} €**. Dadurch schrumpft der Deckungsbeitrag!")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Effektiver DB je Stück", f"{deckungsbeitrag:.2f} €")
    col2.metric("Break-Even-Menge", f"{bep_menge:.0f} Stück")

    if zielgewinn > 0:
        col3.metric("Menge für Zielgewinn", f"{ziel_menge:.0f} Stück")
    else:
        col3.metric("Break-Even-Umsatz", f"{bep_umsatz:.2f} €")

    # --- Daten für das Diagramm generieren ---
    # Wir passen die Schrittweite dynamisch an, damit das Programm bei riesigen Zahlen (z.B. 1 Million) nicht abstürzt
    schrittweite = max(1, int(max_menge // 50))
    mengen = list(range(0, int(max_menge) + 1, schrittweite))

    df = pd.DataFrame({
        "Menge": mengen,
        "Umsatz": [m * effektiver_preis for m in mengen],
        "Gesamtkosten": [fixkosten + (m * var_kosten) for m in mengen],
        "Fixkosten": [fixkosten for m in mengen]
    })

    # --- Interaktives Diagramm mit Plotly ---
    fig = go.Figure()

    # Umsatzlinie (Grün)
    fig.add_trace(go.Scatter(x=df["Menge"], y=df["Umsatz"], mode='lines', name='Umsatz (inkl. Rabatt)',
                             line=dict(color='green', width=3)))

    # Gesamtkostenlinie (Rot)
    fig.add_trace(go.Scatter(x=df["Menge"], y=df["Gesamtkosten"], mode='lines', name='Gesamtkosten',
                             line=dict(color='red', width=3)))

    # Fixkostenlinie (Grau, gestrichelt)
    fig.add_trace(go.Scatter(x=df["Menge"], y=df["Fixkosten"], mode='lines', name='Fixkosten',
                             line=dict(color='gray', dash='dash')))

    # Break-Even-Point als Punkt markieren
    if bep_menge <= max_menge:
        fig.add_trace(go.Scatter(x=[bep_menge], y=[bep_umsatz], mode='markers', name='Break-Even-Point (Gewinn=0)',
                                 marker=dict(color='black', size=14, symbol='x')))

    # Zielgewinn als Punkt markieren (falls angegeben)
    if zielgewinn > 0 and ziel_menge <= max_menge:
        fig.add_trace(
            go.Scatter(x=[ziel_menge], y=[ziel_umsatz], mode='markers', name=f'Zielgewinn erreicht (+{zielgewinn} €)',
                       marker=dict(color='gold', size=16, symbol='star', line=dict(color='black', width=1))))

    # Layout des Diagramms anpassen
    fig.update_layout(
        title="Umsatz- und Kostenverlauf",
        xaxis_title="Menge (Stück)",
        yaxis_title="Betrag (in €)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)  # Legende nach links oben verschieben
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    # Warnung, falls Preis (nach Rabatt) < Variable Kosten
    st.error(
        f"⚠️ **Achtung:** Durch den Rabatt sinkt der Preis auf {effektiver_preis:.2f} €. Dieser liegt unterhalb oder genau auf den variablen Kosten ({var_kosten:.2f} €). Ein Gewinn ist mathematisch unmöglich!")