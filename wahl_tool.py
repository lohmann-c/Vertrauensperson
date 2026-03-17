import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- 1. URL-CHECK ZUERST ---
query_params = st.query_params
is_pres_mode = query_params.get("view") == "pres"

# --- 2. KONFIGURATION ---
KANDIDATEN_LISTE = ["Kandidat A", "Kandidat B"] # Hier deine 2 Namen eintragen
WAHLBERECHTIGTE = 242
SPEICHER_DATEI = "duell_ergebnisse.csv"

# --- 3. SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Wahl-Tool", 
    layout="wide", 
    initial_sidebar_state="collapsed" if is_pres_mode else "expanded"
)

# --- 4. FUNKTIONEN ---
def lade_daten_aus_datei():
    """Lädt die Daten bei jedem Durchlauf frisch aus der Datei."""
    if os.path.exists(SPEICHER_DATEI):
        try:
            df = pd.read_csv(SPEICHER_DATEI)
            stimmen = dict(zip(df.Kandidat, df.Stimmen))
            for name in KANDIDATEN_LISTE:
                if name not in stimmen: stimmen[name] = 0
            zettel = int(df['Zettel_Gesamt'].iloc[0]) if 'Zettel_Gesamt' in df.columns else 0
            return stimmen, zettel
        except:
            # Fehler beim Lesen: Leere Daten zurückgeben
            return {name: 0 for name in KANDIDATEN_LISTE}, 0
    return {name: 0 for name in KANDIDATEN_LISTE}, 0

def speichere_daten(stimmen_dict, zettel_anzahl):
    """Speichert den aktuellen Stand in eine CSV-Datei."""
    df = pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen'])
    df['Zettel_Gesamt'] = zettel_anzahl
    df.to_csv(SPEICHER_DATEI, index=False)

# Daten laden
stimmen_dict, zettel_gezaehlt = lade_daten_aus_datei()

# --- 5. AUTOMATISCHER REFRESH (NUR FÜR BEAMER & WENN NICHT FERTIG) ---
# Wichtig: Wir stoppen den Refresh, sobald die Wahl vorbei ist,
# damit das Konfetti nicht alle 5 Sekunden neu startet.
if is_pres_mode and zettel_gezaehlt < WAHLBERECHTIGTE:
    st.markdown("<meta http-equiv='refresh' content='5'>", unsafe_allow_html=True)

# --- 6. KONFETTI-EFFEKT (WENN FERTIG) ---
if zettel_gezaehlt >= WAHLBERECHTIGTE:
    st.balloons() # Eingebauter Streamlit Konfetti-Effekt

# --- 7. LAYOUT LOGIK ---

if is_pres_mode:
    # --- ANSICHT FÜR DEN BEAMER (PUBLIKUM) ---
    if zettel_gezaehlt >= WAHLBERECHTIGTE:
        st.title("🎉 Endergebnis der Auszählung 🎉")
    else:
        st.title("📊 Aktueller Stand der Auszählung")
    
    df_plot = pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen'])
    df_plot = df_plot.sort_values(by='Stimmen', ascending=False).reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['#3498db', '#e74c3c'] 
    bars = ax.barh(df_plot['Kandidat'], df_plot['Stimmen'], color=colors[:len(df_plot)])
    ax.invert_yaxis()
    
    # Riesige Schrift für das Publikum
    ax.bar_label(bars, padding=15, fontsize=30, fontweight='bold') 
    ax.tick_params(axis='y', labelsize=25)
    
    st.pyplot(fig)
    
    # Fortschritts-Anzeige
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
                    # Seite neu laden, um Stand zu aktualisieren
                    st.rerun()
                else:
                    st.error(f"Limit erreicht! Alle {WAHLBERECHTIGTE} Zettel sind erfasst.")
        
        st.markdown("---")
        if st.button("🗑️ Daten löschen / Reset"):
            if os.path.exists(SPEICHER_DATEI): 
                os.remove(SPEICHER_DATEI)
            st.rerun()
            
    # Vorschau für dich
    if zettel_gezaehlt >= WAHLBERECHTIGTE:
        st.warning(f"Modus: Beendet | Alle {zettel_gezaehlt}/{WAHLBERECHTIGTE} Zettel sind erfasst.")
    else:
        st.info(f"Eingabemodus (Stabil) | Erfasste Zettel: {zettel_gezaehlt}/{WAHLBERECHTIGTE}")
    
    # Kleine Tabelle zur Kontrolle
    st.table(pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen']))
