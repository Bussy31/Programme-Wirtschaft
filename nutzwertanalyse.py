import streamlit as st
import pandas as pd

# --- Seiten-Setup ---
st.set_page_config(page_title="Nutzwertanalyse", layout="centered")

st.title("📊 Nutzwertanalyse")
st.markdown("""
Welche Alternative ist die beste? Nutze diese Tabelle, um deine Entscheidung zu strukturieren.
1. Lege deine **Kriterien** fest.
2. Bestimme die prozentuale **Gewichtung** (Wie wichtig ist dir das Kriterium?).
3. Vergib die **Rohpunkte / das Ranking** für jede Option (z. B. auf einer Skala von 1 bis 10, wobei 10 das Beste ist).

**Wichtig:** Die Gewichtung aller Kriterien muss zusammen exakt 100 % ergeben!
""")
st.divider()

# --- 1. Interaktive Tabelle (Data Editor) ---
st.subheader("1. Daten erfassen")

# Standard-Werte für den Start (können von den Schülern überschrieben/erweitert werden)
start_daten = pd.DataFrame({
    "Kriterium": ["Anschaffungspreis", "Qualität", "Lieferzeit", ""],
    "Gewichtung (%)": [50, 30, 20, 0],
    "Rohpunkte / Ranking (Option A)": [8, 6, 4, 0],
    "Rohpunkte / Ranking (Option B)": [5, 9, 8, 0]
})

# Tabelle anzeigen und bearbeitbar machen (Nutzer können auch Zeilen hinzufügen)
df_eingabe = st.data_editor(
    start_daten,
    num_rows="dynamic",
    hide_index=True,
    use_container_width=True
)

# --- 2. Logik-Check: Ergibt die Gewichtung 100%? ---
summe_gewichtung = df_eingabe["Gewichtung (%)"].sum()

if summe_gewichtung != 100:
    st.error(
        f"⚠️ Achtung: Die Gewichtung liegt aktuell bei **{summe_gewichtung} %**. Sie muss exakt 100 % ergeben, bevor du weiterrechnen kannst.")
else:
    st.success("✅ Die Gewichtung ergibt exakt 100 %. Sehr gut! Du kannst jetzt mit der Auswertung beginnen.")
    st.divider()

    # --- 3. Der Schüler-Arbeitsauftrag (Selber rechnen!) ---
    st.subheader("2. Nutzwerte berechnen")
    st.markdown("""
    Berechne nun den finalen Nutzwert für beide Optionen selbstständig auf deinem Block. 
    *(Tipp: Gewichtung als Dezimalzahl × vergebene Rohpunkte, z. B. 50 % von 8 Punkten = 0.5 × 8 = 4)*

    Trage deine berechneten Endergebnisse (die Summe aller Teilnutzwerte) hier ein, um die visuelle Auswertung freizuschalten:
    """)

    # Das Programm berechnet heimlich die echten Werte im Hintergrund
    # (Gewichtung / 100) * Punkte
    echter_nutzwert_a = ((df_eingabe["Gewichtung (%)"] / 100) * df_eingabe["Rohpunkte / Ranking (Option A)"]).sum()
    echter_nutzwert_b = ((df_eingabe["Gewichtung (%)"] / 100) * df_eingabe["Rohpunkte / Ranking (Option B)"]).sum()

    # Eingabefelder für die Schüler
    col1, col2 = st.columns(2)
    with col1:
        schueler_eingabe_a = st.number_input("Dein Ergebnis für Option A:", min_value=0.0, step=0.1, format="%.1f")
    with col2:
        schueler_eingabe_b = st.number_input("Dein Ergebnis für Option B:", min_value=0.0, step=0.1, format="%.1f")

    # --- 4. Auswertung und Visualisierung (Belohnung) ---
    # Wir erlauben eine minimale Abweichung (0.05) wegen Rundungsfehlern bei Computern
    if schueler_eingabe_a > 0 or schueler_eingabe_b > 0:  # Erst prüfen, wenn sie was eingetippt haben

        a_korrekt = abs(schueler_eingabe_a - echter_nutzwert_a) < 0.05
        b_korrekt = abs(schueler_eingabe_b - echter_nutzwert_b) < 0.05

        if a_korrekt and b_korrekt:
            st.balloons()
            st.success("🎉 Beide Nutzwerte sind absolut korrekt berechnet! Hier ist deine Auswertung:")

            # Sieger ermitteln
            if echter_nutzwert_a > echter_nutzwert_b:
                sieger = "Option A"
            elif echter_nutzwert_b > echter_nutzwert_a:
                sieger = "Option B"
            else:
                sieger = "Beide Optionen sind exakt gleich auf (Unentschieden)"

            st.info(f"🏆 **Entscheidungsempfehlung:** {sieger} gewinnt die Nutzwertanalyse!")

            # Diagramm zeichnen
            diagramm_daten = pd.DataFrame({
                "Optionen": ["Option A", "Option B"],
                "Finaler Nutzwert": [echter_nutzwert_a, echter_nutzwert_b]
            })
            # Streamlit Bar Chart
            st.bar_chart(data=diagramm_daten, x="Optionen", y="Finaler Nutzwert", color="#2563eb")

        else:
            st.warning(
                "🧐 Das stimmt noch nicht ganz. Rechne noch einmal nach! Hast du die prozentuale Gewichtung richtig mit den Rohpunkten multipliziert und am Ende alles addiert?")