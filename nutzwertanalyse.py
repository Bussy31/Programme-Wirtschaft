import streamlit as st
import pandas as pd
from fpdf import FPDF

# --- Seiten-Setup ---
st.set_page_config(page_title="Nutzwertanalyse", layout="wide")

# --- CSS HACK: Diagramm starr machen ---
st.markdown("""
    <style>
    /* Blockiert alle Maus-Interaktionen (Zoomen, Klicken, Verschieben) für das Diagramm */
    [data-testid="stVegaLiteChart"] {
        pointer-events: none;
    }
    </style>
""", unsafe_allow_html=True)


# --- PDF GENERATOR FUNKTION ---
def generiere_nutzwert_pdf(option_namen, echte_nutzwerte, export_daten, max_punkte):
    pdf = FPDF()
    pdf.add_page()

    # Titel
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Auswertung: Nutzwertanalyse", ln=True, align="C")
    pdf.ln(2)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, txt=f"Bewertungsskala: 1 bis {max_punkte} Rohpunkte", ln=True, align="C")
    pdf.ln(8)

    # 1. Abschnitt: Finale Ergebnisse
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt="1. Gesamtergebnis", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.ln(2)

    # Tabellenkopf für Ergebnisse
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(90, 8, txt="Option / Produkt", border=1, align="C")
    pdf.cell(60, 8, txt="Finaler Nutzwert", border=1, align="C")
    pdf.ln()

    # Datenzeilen
    pdf.set_font("Arial", size=11)
    for idx, name in enumerate(option_namen):
        sicherer_name = name.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(90, 8, txt=f" {sicherer_name}", border=1)
        pdf.cell(60, 8, txt=f" {echte_nutzwerte[idx]:.2f} Punkte", border=1, align="C")
        pdf.ln()

    pdf.ln(10)

    # 2. Abschnitt: Detaillierter Rechenweg pro Option
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt="2. Detaillierter Rechenweg (Nachvollziehbarkeit)", ln=True)
    pdf.ln(2)

    # Formel-Erklärung
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 5, txt="Formel pro Kriterium: Rohpunkte * (Gewichtung / 100) = Teilnutzwert", ln=True)
    pdf.ln(5)

    # Iterieren durch die Optionen (Blöcke pro Produkt)
    for opt_idx, opt_name in enumerate(option_namen):
        sicherer_name = opt_name.encode('latin-1', 'replace').decode('latin-1')

        # Header für die jeweilige Option
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 8, txt=f"Berechnung für: {sicherer_name}", ln=True, fill=True)
        pdf.set_font("Arial", size=10)
        pdf.ln(2)

        # Alle Kriterien für diese Option auflisten
        kontroll_summe = 0.0
        for daten in export_daten:
            krit_text = daten['kriterium'].encode('latin-1', 'replace').decode('latin-1')
            gewicht_dezimal = daten['gewicht'] / 100.0
            roh_punkte = daten['punkte'][opt_idx]

            # Die Rechnung
            teilnutzwert = roh_punkte * gewicht_dezimal
            kontroll_summe += teilnutzwert

            # Zeile drucken
            rechenweg_txt = f"   -> {krit_text} ({daten['gewicht']}%): {roh_punkte} Rohpunkte * {gewicht_dezimal:.2f} = {teilnutzwert:.2f} Punkte"
            pdf.cell(0, 6, txt=rechenweg_txt, ln=True)

        # Abschließende Summe für den Block
        pdf.ln(1)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 6, txt=f"   => Summe (Finaler Nutzwert): {kontroll_summe:.2f} Punkte", ln=True)
        pdf.ln(6)

    return bytes(pdf.output(dest="S").encode("latin-1"))


# ==========================================
# --- START DER APP ---
# ==========================================

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
            # Fester Key für die Namensfelder
            name = st.text_input(f"Name Option {i + 1}:", value=f"Option {chr(65 + i)}", max_chars=20,
                                 key=f"opt_name_{i}")
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
st.markdown(f"Lege deine Kriterien fest (Gewichtung in %) und vergib die Rohpunkte (1 bis {max_punkte}).")

gesamt_gewichtung = 0
echte_nutzwerte = [0.0] * anzahl_optionen

export_daten = []

for i in range(st.session_state.anzahl_kriterien):
    with st.container(border=True):
        col_krit, col_gew = st.columns([3, 1])
        with col_krit:
            krit_name = st.text_input(f"Kriterium {i + 1}:", value=f"Kriterium {i + 1}", key=f"name_{i}")
        with col_gew:
            gewicht = st.number_input("Gewichtung (%)", min_value=0, max_value=100, value=0, step=5, key=f"gew_{i}")
            gesamt_gewichtung += gewicht

        st.markdown(f"**Rohpunkte vergeben:**")

        cols_slider = st.columns(anzahl_optionen)
        punkte_aktuell = []

        for opt_idx in range(anzahl_optionen):
            with cols_slider[opt_idx]:
                punkte = st.slider(f"{option_namen[opt_idx]}", min_value=1, max_value=max_punkte, value=max_punkte // 2,
                                   key=f"p_{i}_{opt_idx}")
                punkte_aktuell.append(punkte)

                # Hintergrundberechnung
                echte_nutzwerte[opt_idx] += (gewicht / 100.0) * punkte

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
                eingabe = st.number_input(f"Ergebnis für {option_namen[opt_idx]}:", min_value=0.0, step=0.01,
                                          format="%.2f", key=f"erg_eingabe_{opt_idx}")
                schueler_eingaben.append(eingabe)

        # --- 4. Auswertung & PDF Export ---
        if any(eingabe > 0 for eingabe in schueler_eingaben):
            alle_korrekt = True
            for opt_idx in range(anzahl_optionen):
                if abs(schueler_eingaben[opt_idx] - echte_nutzwerte[opt_idx]) >= 0.05:
                    alle_korrekt = False
                    break

            if alle_korrekt:
                st.success("🎉 Hervorragend gerechnet! Alle Nutzwerte stimmen. Hier ist das Ergebnis:")

                # --- TRICK: Zwangssortierung für das Diagramm ---
                # Wir hängen eine unsichtbare Nummerierung an, z.B. "1. Option A", "2. Option B"
                diagramm_namen = [f"{i + 1}. {name}" for i, name in enumerate(option_namen)]

                # Buntes Diagramm
                diagramm_daten = pd.DataFrame({
                    "Optionen": diagramm_namen,
                    "Finaler Nutzwert": echte_nutzwerte
                })

                st.bar_chart(data=diagramm_daten, x="Optionen", y="Finaler Nutzwert", color="Optionen", height=700)

                st.divider()

                # Download Button
                st.write("Möchtest du deine Ergebnisse und Rechenwege für den Unterricht sichern?")
                st.download_button(
                    label="📄 Ergebnisse & Rechenwege als PDF herunterladen",
                    data=generiere_nutzwert_pdf(option_namen, echte_nutzwerte, export_daten, max_punkte),
                    file_name="Nutzwertanalyse_Rechenweg.pdf",
                    mime="application/pdf"
                )

            else:
                st.error(
                    "🧐 Das stimmt noch nicht ganz. Überprüfe deine Rechnung bei allen Optionen! Achte auf die Dezimalstellen.")