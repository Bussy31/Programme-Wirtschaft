import streamlit as st
import pandas as pd
from fpdf import FPDF

# --- Seiten-Setup ---
st.set_page_config(page_title="Nutzwertanalyse", layout="wide")

st.title("📊 Nutzwertanalyse")
st.markdown("""
Nutze dieses Tool, um eine strukturierte Entscheidung zu treffen. 
Lege zuerst die Rahmenbedingungen fest, verteile dann die prozentuale Gewichtung und bewerte die Optionen mit den Schiebereglern.
""")

# --- 0. Rahmenbedingungen ---
with st.container(border=True):
    st.subheader("1. Rahmenbedingungen & Optionen")

    col_setup1, col_setup2 = st.columns(2)
    with col_setup1:
        anzahl_optionen = st.number_input("Wie viele Optionen möchtest du vergleichen? (2 bis 5)", min_value=2,
                                          max_value=5, value=2)
    with col_setup2:
        max_punkte = st.number_input("Maximalpunktzahl der Skala (z. B. 5, 10 oder 100):", min_value=1, value=10)

    st.markdown("**Benenne deine Optionen:**")
    option_namen = []
    cols_namen = st.columns(anzahl_optionen)
    for i in range(anzahl_optionen):
        with cols_namen[i]:
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


# --- 1. Kriterien erfassen ---
st.subheader("2. Kriterien & Bewertung")
st.markdown("Lege deine Kriterien fest, bestimme ihre Wichtigkeit (in %) und vergib die Rohpunkte.")

gesamt_gewichtung = 0
echte_nutzwerte = [0.0] * anzahl_optionen

# Diese Liste sammelt alle Daten für den späteren PDF-Export
export_daten = []

for i in range(st.session_state.anzahl_kriterien):
    with st.container(border=True):
        col_krit, col_gew = st.columns([3, 1])
        with col_krit:
            krit_name = st.text_input(f"Kriterium {i + 1}:", value=f"Kriterium {i + 1}", key=f"name_{i}")
        with col_gew:
            gewicht = st.number_input("Gewichtung (%)", min_value=0, max_value=100, value=0, step=5, key=f"gew_{i}")
            gesamt_gewichtung += gewicht

        st.markdown(f"**Rohpunkte vergeben (1 bis {max_punkte}):**")

        cols_slider = st.columns(anzahl_optionen)
        punkte_aktuell = []  # Sammelt die Punkte dieses Kriteriums für den Export

        for opt_idx in range(anzahl_optionen):
            with cols_slider[opt_idx]:
                punkte = st.slider(f"{option_namen[opt_idx]}", min_value=1, max_value=max_punkte, value=max_punkte // 2,
                                   key=f"p_{i}_{opt_idx}")
                punkte_aktuell.append(punkte)

                # Hintergrundberechnung
                echte_nutzwerte[opt_idx] += (gewicht / 100) * punkte

        # Daten für PDF speichern
        export_daten.append({
            "kriterium": krit_name,
            "gewicht": gewicht,
            "punkte": punkte_aktuell
        })

# Buttons
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.button("➕ Kriterium hinzufügen", on_click=add_kriterium, use_container_width=True)
with col_btn2:
    st.button("➖ Kriterium entfernen", on_click=remove_kriterium, use_container_width=True)

st.divider()

# --- 2. Logik-Check: 100% Gewichtung ---
st.subheader("3. Gewichtungs-Check")

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

        schueler_eingaben = []
        cols_erg = st.columns(anzahl_optionen)
        for opt_idx in range(anzahl_optionen):
            with cols_erg[opt_idx]:
                eingabe = st.number_input(f"Ergebnis für {option_namen[opt_idx]}:", min_value=0.0, step=0.1,
                                          format="%.1f")
                schueler_eingaben.append(eingabe)

        # --- 4. Auswertung & PDF Export ---
        if any(eingabe > 0 for eingabe in schueler_eingaben):
            alle_korrekt = True
            for opt_idx in range(anzahl_optionen):
                if abs(schueler_eingaben[opt_idx] - echte_nutzwerte[opt_idx]) >= 0.05:
                    alle_korrekt = False
                    break

            if alle_korrekt:
                st.balloons()
                st.success("🎉 Hervorragend gerechnet! Alle Nutzwerte stimmen. Hier ist das Ergebnis:")

                # Buntes Diagramm (color="Optionen" sorgt für unterschiedliche Farben)
                diagramm_daten = pd.DataFrame({
                    "Optionen": option_namen,
                    "Finaler Nutzwert": echte_nutzwerte
                })
                st.bar_chart(data=diagramm_daten, x="Optionen", y="Finaler Nutzwert", color="Optionen")

                st.divider()


                # --- PDF GENERATOR ---
                def generiere_nutzwert_pdf():
                    pdf = FPDF()
                    pdf.add_page()

                    # Titel
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(0, 10, txt="Auswertung: Nutzwertanalyse", ln=True, align="C")
                    pdf.ln(5)

                    # Optionen & finale Punkte
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(0, 10, txt="Finale Ergebnisse:", ln=True)
                    pdf.set_font("Arial", size=11)
                    for idx, name in enumerate(option_namen):
                        pdf.cell(0, 7, txt=f"- {name}: {echte_nutzwerte[idx]:.1f} Punkte", ln=True)
                    pdf.ln(5)

                    # Detailübersicht der Kriterien
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(0, 10, txt="Bewertungsdetails:", ln=True)
                    pdf.set_font("Arial", size=10)

                    for daten in export_daten:
                        # Umlaute sicherheitshalber bereinigen (fpdf mag manchmal keine Sonderzeichen)
                        krit_text = daten['kriterium'].encode('latin-1', 'replace').decode('latin-1')
                        pdf.set_font("Arial", 'B', 10)
                        pdf.cell(0, 7, txt=f"Kriterium: {krit_text} ({daten['gewicht']}%)", ln=True)

                        pdf.set_font("Arial", size=10)
                        for idx, p in enumerate(daten['punkte']):
                            opt_text = option_namen[idx].encode('latin-1', 'replace').decode('latin-1')
                            pdf.cell(0, 6, txt=f"   -> {opt_text}: {p} Rohpunkte", ln=True)
                        pdf.ln(2)

                    return bytes(pdf.output(dest="S").encode("latin-1"))


                # Download Button
                st.write("Möchtest du deine Ergebnisse für den Unterricht sichern?")
                st.download_button(
                    label="📄 Ergebnisse als PDF herunterladen",
                    data=generiere_nutzwert_pdf(),
                    file_name="Nutzwertanalyse_Ergebnisse.pdf",
                    mime="application/pdf"
                )

            else:
                st.error("🧐 Das stimmt noch nicht ganz. Überprüfe deine Rechnung bei allen Optionen!")