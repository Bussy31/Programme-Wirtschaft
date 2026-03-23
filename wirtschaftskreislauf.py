import streamlit as st
import plotly.graph_objects as go

st.title("Baue den Wirtschaftskreislauf!")

# --- 1. Die Bau-Phase (Das Puzzle) ---
st.subheader("Schritt 1: Leitungen legen")
st.markdown("Wer zahlt an wen? Verbinde die Akteure richtig, um den Geldfluss zu starten.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Konsumausgaben**")
    konsum_von = st.selectbox("Geld fließt von...", ["Bitte wählen", "Haushalte", "Unternehmen"], key="k_von")
    konsum_zu = st.selectbox("...zu", ["Bitte wählen", "Haushalte", "Unternehmen"], key="k_zu")

with col2:
    st.markdown("**Löhne / Einkommen**")
    lohn_von = st.selectbox("Geld fließt von...", ["Bitte wählen", "Haushalte", "Unternehmen"], key="l_von")
    lohn_zu = st.selectbox("...zu", ["Bitte wählen", "Haushalte", "Unternehmen"], key="l_zu")

# --- 2. Prüfen, ob die Schüler es richtig gemacht haben ---
konsum_richtig = (konsum_von == "Haushalte" and konsum_zu == "Unternehmen")
lohn_richtig = (lohn_von == "Unternehmen" and lohn_zu == "Haushalte")

if konsum_richtig and lohn_richtig:
    st.success("🎉 Perfekt! Der Kreislauf ist geschlossen. Das Geld beginnt zu fließen!")

    # --- 3. Die Belohnung: Das Geld fließt (Sankey Diagramm) ---
    st.subheader("Schritt 2: Schau auf das Geld")

    # Regler einblenden, nachdem richtig gebaut wurde
    konsum_menge = st.slider("Wie viel konsumieren die Haushalte?", 100, 1000, 500)

    # Sankey Diagramm wie vorhin, aber nur sichtbar, wenn das Puzzle gelöst ist!
    fig = go.Figure(data=[go.Sankey(
        node=dict(label=["Unternehmen", "Haushalte"], color=["#2CA02C", "#1F77B4"]),
        link=dict(
            source=[1, 0],  # 1=Haushalte, 0=Unternehmen
            target=[0, 1],  # 0=Unternehmen, 1=Haushalte
            value=[konsum_menge, konsum_menge],  # Hier fließt das Geld!
            label=["Konsum", "Löhne"]
        )
    )])
    st.plotly_chart(fig, use_container_width=True)

elif (konsum_von != "Bitte wählen" or lohn_von != "Bitte wählen"):
    st.warning(
        "Noch nicht ganz richtig. Überlege nochmal: Wer bekommt Lohn für seine Arbeit? Und wer kauft im Supermarkt ein?")