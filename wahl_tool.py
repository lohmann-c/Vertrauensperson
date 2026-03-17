import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import time

# --- AUTOMATISCHER REFRESH ---
st.markdown("<meta http-equiv='refresh' content='5'>", unsafe_allow_html=True)

# --- NEU: PRÄSENTATIONSMODUS ÜBER URL PRÜFEN ---
# Wenn du die URL mit ?view=pres aufrufst, schaltet er um
query_params = st.query_params
is_pres_mode = query_params.get("view") == "pres"

# --- KONFIGURATION ---
KANDIDATEN_LISTE = ["Kandidat A", "Kandidat B"] 
GEWINNER_ANZAHL = 1
WAHLBERECHTIGTE = 242
MAX_STIMMEN_PRO_ZETTEL = 1
SPEICHER_DATEI = "duell_ergebnisse.csv"

# Seitenkonfiguration (Blendet im Pres-Mode die Sidebar fast ganz aus)
st.set_page_config(
    page_title="Wahl-Anzeige", 
    layout="wide", 
    initial_sidebar_state="collapsed" if is_pres_mode else "expanded"
)

# ... (Funktionen lade_daten und speichere_daten bleiben gleich) ...

# --- DATEN LADEN ---
stimmen_dict, zettel_gezaehlt = lade_daten_aus_datei()

# --- LAYOUT LOGIK ---

if is_pres_mode:
    # REINE ANZEIGE FÜR BEAMER
    st.title("📊 Aktueller Stand der Auszählung")
    
    # Diagramm-Daten
    df = pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen'])
    df = df.sort_values(by='Stimmen', ascending=False).reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['#3498db', '#e74c3c'] 
    bars = ax.barh(df['Kandidat'], df['Stimmen'], color=colors[:len(df)])
    ax.invert_yaxis()
    ax.bar_label(bars, padding=15, fontsize=25, fontweight='bold') # RIESIG für Zuschauer
    ax.tick_params(axis='y', labelsize=20)
    st.pyplot(fig)
    
    st.info(f"Fortschritt: {zettel_gezaehlt} von {WAHLBERECHTIGTE} Stimmen erfasst.")

else:
    # DEINE EINGABEMASKE
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
        
        if st.button("🗑️ Reset"):
            if os.path.exists(SPEICHER_DATEI): os.remove(SPEICHER_DATEI)
            st.rerun()
            
    # Vorschau für dich
    st.write(f"Zettel: {zettel_gezaehlt}/{WAHLBERECHTIGTE}")
    st.table(pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen']))
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import time

# --- AUTOMATISCHER REFRESH (alle 5 Sekunden) ---
st.markdown("<meta http-equiv='refresh' content='5'>", unsafe_allow_html=True)

# --- KONFIGURATION ---
KANDIDATEN_LISTE = ["Kandidat A", "Kandidat B"] 
GEWINNER_ANZAHL = 1
WAHLBERECHTIGTE = 242
MAX_STIMMEN_PRO_ZETTEL = 1
SPEICHER_DATEI = "duell_ergebnisse.csv"

# Seitenkonfiguration
st.set_page_config(page_title="Wahl-Duell Live", layout="wide", page_icon="⚖️")

# --- FUNKTIONEN ---
def lade_daten_aus_datei():
    if os.path.exists(SPEICHER_DATEI):
        df = pd.read_csv(SPEICHER_DATEI)
        gespeicherte_stimmen = dict(zip(df.Kandidat, df.Stimmen))
        for name in KANDIDATEN_LISTE:
            if name not in gespeicherte_stimmen:
                gespeicherte_stimmen[name] = 0
        zettel = int(df['Zettel_Gesamt'].iloc[0]) if 'Zettel_Gesamt' in df.columns else 0
        return gespeicherte_stimmen, zettel
    return {name: 0 for name in KANDIDATEN_LISTE}, 0

def speichere_daten(stimmen_dict, zettel_anzahl):
    df = pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen'])
    df['Zettel_Gesamt'] = zettel_anzahl
    df.to_csv(SPEICHER_DATEI, index=False)

# Daten laden
stimmen_dict, zettel_gezaehlt = lade_daten_aus_datei()

# --- SIDEBAR STEUERUNG ---
with st.sidebar:
    st.header("⚙️ Steuerung")
    
    # NEU: Der Präsentations-Modus Schalter
    pres_mode = st.checkbox("📺 Präsentations-Modus (Nur Diagramm)", value=False)
    
    st.markdown("---")
    
    if not pres_mode:
        st.subheader("🗳️ Stimmabgabe")
        with st.form("wahl_form", clear_on_submit=True):
            wahl = st.radio("Wähle einen Kandidaten:", KANDIDATEN_LISTE)
            submit = st.form_submit_button("Stimme speichern")
            
            if submit:
                if zettel_gezaehlt < WAHLBERECHTIGTE:
                    stimmen_dict[wahl] += 1
                    zettel_gezaehlt += 1
                    speichere_daten(stimmen_dict, zettel_gezaehlt)
                    st.success(f"Stimme gezählt!")
                    st.rerun()
                else:
                    st.error("Limit erreicht!")

        if st.button("🗑️ Alles zurücksetzen"):
            if os.path.exists(SPEICHER_DATEI):
                os.remove(SPEICHER_DATEI)
            st.rerun()
    else:
        st.info("Präsentations-Modus aktiv. Eingabefelder sind ausgeblendet.")

# --- HAUPTBEREICH ---

if not pres_mode:
    st.title("⚖️ Wahl-Duell Auszählung")
    progress = zettel_gezaehlt / WAHLBERECHTIGTE
    st.metric(label="Stimmen erfasst", value=f"{zettel_gezaehlt} / {WAHLBERECHTIGTE}")
    st.progress(min(progress, 1.0))
    st.markdown("---")

# Visualisierung (Wird immer angezeigt, aber im Pres-Mode größer)
df = pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen'])
df = df.sort_values(by='Stimmen', ascending=False).reset_index(drop=True)

# Diagramm erstellen
fig, ax = plt.subplots(figsize=(10, 5))
colors = ['#3498db', '#e74c3c'] 
bars = ax.barh(df['Kandidat'], df['Stimmen'], color=colors[:len(df)])
ax.invert_yaxis()
ax.bar_label(bars, padding=10, fontsize=16, fontweight='bold') # Größere Schrift für Zuschauer
ax.set_title("Aktueller Stand der Auszählung", fontsize=18)

st.pyplot(fig)

if not pres_mode:
    st.markdown("---")
    st.table(df)
