import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- 1. AUTOMATISCHER REFRESH & URL-CHECK ---
# Erneuert die Seite alle 5 Sekunden für Live-Updates auf dem Beamer
st.markdown("<meta http-equiv='refresh' content='5'>", unsafe_allow_html=True)

# Prüft, ob "?view=pres" in der URL steht
query_params = st.query_params
is_pres_mode = query_params.get("view") == "pres"

# --- 2. KONFIGURATION ---
KANDIDATEN_LISTE = ["Kandidat A", "Kandidat B"] # Hier deine 2 Namen eintragen
WAHLBERECHTIGTE = 242
SPEICHER_DATEI = "duell_ergebnisse.csv"

st.set_page_config(
    page_title="Wahl-Tool", 
    layout="wide", 
    initial_sidebar_state="collapsed" if is_pres_mode else "expanded"
)

# --- 3. FUNKTIONEN (Zuerst definieren!) ---
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

# Daten bei jedem Laden frisch aus der Datei holen
stimmen_dict, zettel_gezaehlt = lade_daten_aus_datei()

# --- 4. LAYOUT LOGIK ---

if is_pres_mode:
    # --- ANSICHT FÜR DEN ZWEITEN MONITOR (BEAMER) ---
    st.title("📊 Aktueller Stand der Auszählung")
    
    df_plot = pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen'])
    df_plot = df_plot.sort_values(by='Stimmen', ascending=False).reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    # Farben für 2 Kandidaten (Blau und Rot)
    colors = ['#3498db', '#e74c3c'] 
    bars = ax.barh(df_plot['Kandidat'], df_plot['Stimmen'], color=colors[:len(df_plot)])
    ax.invert_yaxis()
    
    # Große Schrift für das Publikum
    ax.bar_label(bars, padding=15, fontsize=30, fontweight='bold') 
    ax.tick_params(axis='y', labelsize=25)
    
    st.pyplot(fig)
    st.subheader(f"Fortschritt: {zettel_gezaehlt} von {WAHLBERECHTIGTE} Stimmen")

else:
    # --- ADMIN-ANSICHT FÜR DICH (LAPTOP) ---
    st.title("⚖️ Wahl-Administration")
    
    with st.sidebar:
        st.header("🗳️ Stimmen erfassen")
        with st.form("wahl_form", clear_on_submit=True):
            wahl = st.radio("Kandidat auswählen:", KANDIDATEN_LISTE)
            if st.form_submit_button("Stimme speichern"):
                if zettel_gezaehlt < WAHLBERECHTIGTE:
                    stimmen_dict[wahl] += 1
                    zettel_gezaehlt += 1
                    speichere_daten(stimmen_dict, zettel_gezaehlt)
                    st.rerun()
                else:
                    st.error("Limit von 242 Stimmzetteln erreicht!")
        
        st.markdown("---")
        if st.button("🗑️ Daten löschen / Reset"):
            if os.path.exists(SPEICHER_DATEI): 
                os.remove(SPEICHER_DATEI)
            st.rerun()
            
    st.info(f"Eingabemodus aktiv. Erfasste Zettel: {zettel_gezaehlt} / {WAHLBERECHTIGTE}")
    # Tabelle zur schnellen Kontrolle
    st.table(pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen']))
