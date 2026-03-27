import streamlit as st
import pandas as pd

# --- Seiten-Setup ---
st.set_page_config(page_title="Nutzwertanalyse", layout="wide")

st.title("📊 Nutzwertanalyse")
st.markdown("""
Nutze dieses Tool, um eine strukturierte Entscheidung zu treffen. 
Lege zuerst die Rahmenbedingungen fest, verteile dann die prozentuale Gewichtung und bewerte die Optionen mit den Schiebereglern.
""")

# --- 0. Rahmenbedingungen (NEU: Dynamisch) ---
with st.container(border=True):
    st.subheader("1. Rahmenbedingungen & Optionen")

    col_setup1, col_setup2 = st.columns(2)
    with col_setup1:
        anzahl_optionen = st.number_input("Wie viele Optionen möchtest du vergleichen? (2 bis 5)", min_value=2,
                                          max_value=5, value=2)
    with col_setup2:
        max_punkte = st.number_input("Maximalpunktzahl der Skala (z. B. 5, 10 oder 100):", min_value=1, value=10)

    st.markdown("**Benenne deine Optionen:**")
    # Dynamische Spalten für die Namen generieren
    option_namen = []
    cols_namen = st.columns(anzahl_optionen)
    for i in range(anzahl_optionen):
        with cols_namen[i]:
            # Standardnamen wie "Option A", "Option B" etc. vergeben (chr(65) = 'A')
            name = st.text_input(f"Name Option {i + 1}:", value=f"Option {chr(65 + i)}", max_chars=20)
            option_namen.append(name)

# --- Session State für dynamische Kriterienanzahl ---
if 'anzahl_kriterien' not in st.session_state:
    st.session_state.anzahl_kriterien = 3


def add_kriterium():
    st.session_state.anzahl_kriterien += 1


def remove_kriterium():
    if st.session_state.anzahl_kriterien > 1:
        st.session_state.anzahl_kriterien -= 1


# --- 1. Kriterien erfassen (Die Karten-Ansicht) ---
st.subheader("2. Kriterien & Bewertung")
st.markdown("Lege deine Kriterien fest, bestimme ihre Wichtigkeit (in %) und vergib die Rohpunkte.")

gesamt_gewichtung = 0
# Liste für die berechneten Nutzwerte (startet bei 0 für jede Option)
echte_nutzwerte = [0.0] * anzahl_optionen

# Schleife baut für jedes Kriterium eine eigene visuelle Karte (Rahmen)
for i in range(st.session_state.anzahl_kriterien):
    with st.container(border=True):
        col_krit, col_gew = st.columns([3, 1])
        with col_krit:
            krit_name = st.text_input(f"Kriterium {i + 1}:", value=f"Kriterium {i + 1}", key=f"name_{i}")
        with col_gew:
            gewicht = st.number_input("Gewichtung (%)", min_value=0, max_value=100, value=0, step=5, key=f"gew_{i}")
            gesamt_gewichtung += gewicht

        st.markdown(f"**Rohpunkte vergeben (1 bis {max_punkte}):**")

        # Dynamische Slider je nach Anzahl der Optionen
        cols_slider = st.columns(anzahl_optionen)
        for opt_idx in range(anzahl_optionen):
            with cols_slider[opt_idx]:
                punkte = st.slider(f"{option_namen[opt_idx]}", min_value=1, max_value=max_punkte, value=max_punkte // 2,
                                   key=f"p_{i}_{opt_idx}")

                # Hintergrundberechnung für dieses Kriterium und diese Option
                echte_nutzwerte[opt_idx] += (gewicht / 100) * punkte

# Buttons zum Hinzufügen/Entfernen von Kriterien
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.button("➕ Kriterium hinzufügen", on_click=add_kriterium, use_container_width=True)
with col_btn2:
    st.button("➖ Kriterium entfernen", on_click=remove_kriterium, use_container_width=True)

st.divider()

# --- 2. Logik-Check: 100% Gewichtung ---
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

    # --- 3. Der Schüler-Arbeitsauftrag ---
    with st.container(border=True):
        st.subheader("4. Deine Berechnung")
        st.markdown(f"""
        Rechne nun die finalen Nutzwerte selbst aus! 
        *(Rechnung pro Kriterium: Gewichtung als Dezimalzahl × Rohpunkte. Am Ende alles addieren.)*
        """)

        # Dynamische Eingabefelder für die Schüler
        schueler_eingaben = []
        cols_erg = st.columns(anzahl_optionen)
        for opt_idx in range(anzahl_optionen):
            with cols_erg[opt_idx]:
                eingabe = st.number_input(f"Ergebnis für {option_namen[opt_idx]}:", min_value=0.0, step=0.1,
                                          format="%.1f")
                schueler_eingaben.append(eingabe)

        # --- 4. Auswertung ---
        # Prüfen, ob überhaupt schon etwas eingegeben wurde (nicht nur 0.0 überall)
        if any(eingabe > 0 for eingabe in schueler_eingaben):

            # Alle Eingaben auf Richtigkeit prüfen
            alle_korrekt = True
            for opt_idx in range(anzahl_optionen):
                if abs(schueler_eingaben[opt_idx] - echte_nutzwerte[opt_idx]) >= 0.05:
                    alle_korrekt = False
                    break  # Sobald ein Fehler drin ist, Schleife abbrechen

            if alle_korrekt:
                st.balloons()
                st.success("🎉 Hervorragend gerechnet! Alle Nutzwerte stimmen. Hier ist deine visuelle Auswertung:")

                # Sieger ermitteln
                max_nutzwert = max(echte_nutzwerte)
                # Prüfen, ob es mehrere Sieger gibt (Unentschieden)
                sieger_indices = [i for i, x in enumerate(echte_nutzwerte) if x == max_nutzwert]

                if len(sieger_indices) == 1:
                    sieger_name = option_namen[sieger_indices[0]]
                    st.info(
                        f"🏆 **Entscheidungsempfehlung:** {sieger_name} gewinnt die Nutzwertanalyse mit {max_nutzwert:.1f} Punkten!")
                else:
                    sieger_namen = [option_namen[i] for i in sieger_indices]
                    st.info(
                        f"⚖️ **Unentschieden:** {', '.join(sieger_namen)} liegen mit exakt {max_nutzwert:.1f} Punkten gleichauf!")

                # Diagramm zeichnen
                diagramm_daten = pd.DataFrame({
                    "Optionen": option_namen,
                    "Finaler Nutzwert": echte_nutzwerte
                })
                st.bar_chart(data=diagramm_daten, x="Optionen", y="Finaler Nutzwert", color="#2563eb")

            else:
                st.error("🧐 Das stimmt noch nicht ganz. Überprüfe deine Rechnung bei allen Optionen!")