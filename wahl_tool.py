import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import time

# --- AUTOMATISCHER REFRESH (alle 5 Sekunden) ---
st.markdown("<meta http-equiv='refresh' content='5'>", unsafe_allow_html=True)

# --- KONFIGURATION ---
KANDIDATEN_LISTE = ["Kandidat A", "Kandidat B"] # Hier einfach die echten Namen eintragen
GEWINNER_ANZAHL = 1
WAHLBERECHTIGTE = 242
MAX_STIMMEN_PRO_ZETTEL = 1 # Bei 2 Personen meist nur 1 Stimme erlaubt
SPEICHER_DATEI = "duell_ergebnisse.csv"

# Seitenkonfiguration
st.set_page_config(page_title="Wahl-Duell", layout="wide", page_icon="⚖️")

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

# --- UI ---
st.title("⚖️ Wahl-Duell Auszählung")
st.markdown("---")

# Fortschritt
progress = zettel_gezaehlt / WAHLBERECHTIGTE
st.metric(label="Abgegebene Stimmen", value=f"{zettel_gezaehlt} / {WAHLBERECHTIGTE}")
st.progress(min(progress, 1.0))

# Visualisierung
st.subheader("📊 Aktueller Stand")
df = pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen'])
df = df.sort_values(by='Stimmen', ascending=False).reset_index(drop=True)

# Grafik
fig, ax = plt.subplots(figsize=(10, 4))
colors = ['#3498db', '#e74c3c'] # Blau für Platz 1, Rot für Platz 2
bars = ax.barh(df['Kandidat'], df['Stimmen'], color=colors[:len(df)])
ax.invert_yaxis()
ax.bar_label(bars, padding=10, fontsize=12, fontweight='bold')
st.pyplot(fig)

# Tabelle & Export
st.markdown("---")
st.table(df)

# SIDEBAR STEUERUNG
with st.sidebar:
    st.header("🗳️ Stimmabgabe")
    with st.form("wahl_form", clear_on_submit=True):
        wahl = st.radio("Wähle einen Kandidaten:", KANDIDATEN_LISTE)
        submit = st.form_submit_button("Stimme speichern")
        
        if submit:
            if zettel_gezaehlt < WAHLBERECHTIGTE:
                stimmen_dict[wahl] += 1
                zettel_gezaehlt += 1
                speichere_daten(stimmen_dict, zettel_gezaehlt)
                st.success(f"Stimme für {wahl} gezählt!")
                st.rerun()
            else:
                st.error("Maximale Anzahl an Stimmzetteln erreicht!")

    if st.button("🗑️ Alles zurücksetzen"):
        if os.path.exists(SPEICHER_DATEI):
            os.remove(SPEICHER_DATEI)
        st.rerun()