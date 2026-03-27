import streamlit as st
import pandas as pd

# --- Seiten-Setup ---
st.set_page_config(page_title="Nutzwertanalyse", layout="centered")

st.title("📊 Nutzwertanalyse")
st.markdown("""
Nutze dieses Tool, um eine strukturierte Entscheidung zu treffen. 
Verteile die prozentuale Gewichtung und bewerte die Optionen mit den Schiebereglern.
""")

# --- 1. Optionen benennen ---
with st.container(border=True):
    st.subheader("1. Was vergleichen wir?")
    col1, col2 = st.columns(2)
    with col1:
        name_a = st.text_input("Name der 1. Option:", value="Option A", max_chars=20)
    with col2:
        name_b = st.text_input("Name der 2. Option:", value="Option B", max_chars=20)

# --- Session State für dynamische Kriterienanzahl ---
if 'anzahl_kriterien' not in st.session_state:
    st.session_state.anzahl_kriterien = 3


def add_kriterium():
    st.session_state.anzahl_kriterien += 1


def remove_kriterium():
    if st.session_state.anzahl_kriterien > 1:
        st.session_state.anzahl_kriterien -= 1


# --- 2. Kriterien erfassen (Die Karten-Ansicht) ---
st.subheader("2. Kriterien & Bewertung")
st.markdown("Lege deine Kriterien fest, bestimme ihre Wichtigkeit (in %) und vergib die Rohpunkte von 1 bis 10.")

gesamt_gewichtung = 0
echter_nutzwert_a = 0.0
echter_nutzwert_b = 0.0

# Schleife baut für jedes Kriterium eine eigene visuelle Karte (Rahmen)
for i in range(st.session_state.anzahl_kriterien):
    with st.container(border=True):
        col_krit, col_gew = st.columns([3, 1])
        with col_krit:
            krit_name = st.text_input(f"Kriterium {i + 1}:", value=f"Kriterium {i + 1}", key=f"name_{i}")
        with col_gew:
            gewicht = st.number_input("Gewichtung (%)", min_value=0, max_value=100, value=0, step=5, key=f"gew_{i}")
            gesamt_gewichtung += gewicht

        st.markdown("**Rohpunkte vergeben:**")
        col_slider1, col_slider2 = st.columns(2)
        with col_slider1:
            punkte_a = st.slider(f"Punkte für {name_a}", min_value=1, max_value=10, value=5, key=f"pa_{i}")
        with col_slider2:
            punkte_b = st.slider(f"Punkte für {name_b}", min_value=1, max_value=10, value=5, key=f"pb_{i}")

        # Hintergrundberechnung für dieses Kriterium
        echter_nutzwert_a += (gewicht / 100) * punkte_a
        echter_nutzwert_b += (gewicht / 100) * punkte_b

# Buttons zum Hinzufügen/Entfernen von Kriterien
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.button("➕ Kriterium hinzufügen", on_click=add_kriterium, use_container_width=True)
with col_btn2:
    st.button("➖ Kriterium entfernen", on_click=remove_kriterium, use_container_width=True)

st.divider()

# --- 3. Logik-Check: 100% Gewichtung ---
st.subheader("3. Gewichtungs-Check")

# Optischer Fortschrittsbalken
progress_val = min(gesamt_gewichtung / 100.0, 1.0)
st.progress(progress_val)

if gesamt_gewichtung < 100:
    st.warning(f"⏳ Du hast erst **{gesamt_gewichtung} %** verteilt. Es fehlen noch {100 - gesamt_gewichtung} %.")
elif gesamt_gewichtung > 100:
    st.error(f"🛑 Achtung! Du hast **{gesamt_gewichtung} %** verteilt. Das sind {gesamt_gewichtung - 100} % zu viel!")
else:
    st.success("✅ Perfekt! Du hast exakt 100 % verteilt.")

    # --- 4. Der Schüler-Arbeitsauftrag ---
    with st.container(border=True):
        st.subheader("4. Deine Berechnung")
        st.markdown(f"""
        Rechne nun die finalen Nutzwerte selbst aus! 
        *(Rechnung pro Kriterium: Gewichtung als Dezimalzahl × Rohpunkte. Am Ende alles addieren.)*
        """)

        col_erg1, col_erg2 = st.columns(2)
        with col_erg1:
            schueler_eingabe_a = st.number_input(f"Ergebnis für {name_a}:", min_value=0.0, step=0.1, format="%.1f")
        with col_erg2:
            schueler_eingabe_b = st.number_input(f"Ergebnis für {name_b}:", min_value=0.0, step=0.1, format="%.1f")

        # --- 5. Auswertung ---
        if schueler_eingabe_a > 0 or schueler_eingabe_b > 0:
            a_korrekt = abs(schueler_eingabe_a - echter_nutzwert_a) < 0.05
            b_korrekt = abs(schueler_eingabe_b - echter_nutzwert_b) < 0.05

            if a_korrekt and b_korrekt:
                st.balloons()
                st.success("🎉 Hervorragend gerechnet! Hier ist deine visuelle Auswertung:")

                # Diagramm zeichnen
                diagramm_daten = pd.DataFrame({
                    "Optionen": [name_a, name_b],
                    "Finaler Nutzwert": [echter_nutzwert_a, echter_nutzwert_b]
                })
                st.bar_chart(data=diagramm_daten, x="Optionen", y="Finaler Nutzwert", color="#2563eb")

            else:
                st.error("🧐 Das stimmt noch nicht ganz. Überprüfe deine Rechnung!")