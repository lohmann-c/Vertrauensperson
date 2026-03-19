import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import io

# --- 1. URL-CHECK ZUERST ---
query_params = st.query_params
is_pres_mode = query_params.get("view") == "pres"

# --- 2. KONFIGURATION ---
KANDIDATEN_LISTE = ["Nina D.", "Daniel H.", "Platzhalter"] 
WAHLBERECHTIGTE = 15
SPEICHER_DATEI = "duell_ergebnisse.csv"

# --- 3. SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Wahl-Tool", 
    layout="wide", 
    initial_sidebar_state="collapsed" if is_pres_mode else "expanded"
)

# --- 4. FUNKTIONEN ---
def lade_daten_aus_datei():
    if os.path.exists(SPEICHER_DATEI):
        try:
            df = pd.read_csv(SPEICHER_DATEI)
            stimmen = dict(zip(df.Kandidat, df.Stimmen))
            for name in KANDIDATEN_LISTE:
                if name not in stimmen: stimmen[name] = 0
            zettel = int(df['Zettel_Gesamt'].iloc[0]) if 'Zettel_Gesamt' in df.columns else 0
            return stimmen, zettel
        except:
            return {name: 0 for name in KANDIDATEN_LISTE}, 0
    return {name: 0 for name in KANDIDATEN_LISTE}, 0

def speichere_daten(stimmen_dict, zettel_anzahl):
    df = pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen'])
    df['Zettel_Gesamt'] = zettel_anzahl
    df.to_csv(SPEICHER_DATEI, index=False)

stimmen_dict, zettel_gezaehlt = lade_daten_aus_datei()

# --- 5. AUTOMATISCHER REFRESH (NUR FÜR BEAMER & WENN NICHT FERTIG) ---
if is_pres_mode and zettel_gezaehlt < WAHLBERECHTIGTE:
    st.markdown("<meta http-equiv='refresh' content='5'>", unsafe_allow_html=True)

# --- 6. KONFETTI-EFFEKT (WENN FERTIG) ---
if zettel_gezaehlt >= WAHLBERECHTIGTE:
    st.balloons() 

# --- 7. LAYOUT LOGIK ---

# Vorbereitung der Grafik für beide Ansichten
df_plot = pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen'])
df_plot = df_plot.sort_values(by='Stimmen', ascending=False).reset_index(drop=True)
fig, ax = plt.subplots(figsize=(12, 6))
colors = ['#3498db', '#e74c3c', '#2ecc71'] 
bars = ax.barh(df_plot['Kandidat'], df_plot['Stimmen'], color=colors[:len(df_plot)])
ax.invert_yaxis()
ax.bar_label(bars, padding=15, fontsize=30, fontweight='bold') 
ax.tick_params(axis='y', labelsize=25)

if is_pres_mode:
    # --- ANSICHT FÜR DEN BEAMER (PUBLIKUM) ---
    if zettel_gezaehlt >= WAHLBERECHTIGTE:
        st.title("🎉 Endergebnis der Auszählung 🎉")
    else:
        st.title("📊 Aktueller Stand der Auszählung")
    
    st.pyplot(fig)
    
    if zettel_gezaehlt >= WAHLBERECHTIGTE:
        st.success(f"Alle {WAHLBERECHTIGTE} Stimmen wurden erfolgreich erfasst.")
    else:
        st.subheader(f"Fortschritt: {zettel_gezaehlt} von {WAHLBERECHTIGTE} Stimmen")

else:
    # --- ADMIN-ANSICHT (DEIN LAPTOP) ---
    st.title("⚖️ Wahl-Administration")
    
    with st.sidebar:
        st.header("🗳️ Stimmen erfassen")
        with st.form("wahl_form", clear_on_submit=True):
            wahl = st.radio("Kandidat auswählen:", KANDIDATEN_LISTE)
            submit = st.form_submit_button("Stimme speichern")
            
            if submit:
                if zettel_gezaehlt < WAHLBERECHTIGTE:
                    stimmen_dict[wahl] += 1
                    zettel_gezaehlt += 1
                    speichere_daten(stimmen_dict, zettel_gezaehlt)
                    st.rerun()
                else:
                    st.error(f"Limit erreicht!")
        
        st.markdown("---")
        if st.button("🗑️ Daten löschen / Reset"):
            if os.path.exists(SPEICHER_DATEI): os.remove(SPEICHER_DATEI)
            st.rerun()
            
    # Status-Meldungen
    if zettel_gezaehlt >= WAHLBERECHTIGTE:
        st.warning(f"Wahlergebnis liegt vor ({zettel_gezaehlt}/{WAHLBERECHTIGTE})")
        
        # --- EXPORT FUNKTION ---
        # Speichert das aktuelle Diagramm in einen Buffer für den Download
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight')
        st.download_button(
            label="📸 Endergebnis als Bild (PNG) speichern",
            data=buf.getvalue(),
            file_name="wahlergebnis_final.png",
            mime="image/png"
        )
    else:
        st.info(f"Eingabemodus | Erfasste Zettel: {zettel_gezaehlt}/{WAHLBERECHTIGTE}")
    
    st.pyplot(fig) # Vorschau-Grafik für dich
    st.table(df_plot)
