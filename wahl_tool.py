import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import io

# --- 1. URL-CHECK ZUERST ---
query_params = st.query_params
is_pres_mode = query_params.get("view") == "pres"

# --- 2. KONFIGURATION ---
KANDIDATEN_LISTE = ["Nina D.", "Daniel H.", "Ungültig"] 
WAHLBERECHTIGTE = 15
SPEICHER_DATEI = "duell_ergebnisse.csv"

# --- 3. SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Wahl-Tool", 
    layout="wide", 
    page_icon="🗳️",
    initial_sidebar_state="collapsed" if is_pres_mode else "expanded"
)

# --- 4. FUNKTIONEN ---
def lade_daten_aus_datei():
    default_stimmen = {str(name): 0 for name in KANDIDATEN_LISTE}
    if os.path.exists(SPEICHER_DATEI):
        try:
            df = pd.read_csv(SPEICHER_DATEI)
            df['Kandidat'] = df['Kandidat'].astype(str)
            stimmen = dict(zip(df.Kandidat, df.Stimmen))
            for name in KANDIDATEN_LISTE:
                if str(name) not in stimmen: stimmen[str(name)] = 0
            zettel = int(df['Zettel_Gesamt'].iloc[0]) if 'Zettel_Gesamt' in df.columns else 0
            return stimmen, zettel
        except:
            return default_stimmen, 0
    return default_stimmen, 0

def speichere_daten(stimmen_dict, zettel_anzahl):
    df = pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen'])
    df['Zettel_Gesamt'] = zettel_anzahl
    df.to_csv(SPEICHER_DATEI, index=False)

stimmen_dict, zettel_gezaehlt = lade_daten_aus_datei()

# --- 5. AUTOMATISCHER REFRESH ---
if is_pres_mode and zettel_gezaehlt < WAHLBERECHTIGTE:
    st.markdown("<meta http-equiv='refresh' content='5'>", unsafe_allow_html=True)

# --- 6. DATENAUFBEREITUNG & GRAFIK ---
df_plot = pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen'])
df_plot['Kandidat'] = df_plot['Kandidat'].astype(str)
df_plot = df_plot.sort_values(by='Stimmen', ascending=False).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(10, 5))
colors = ['#3498db', '#e74c3c', '#95a5a6'] # Blau, Rot, Grau
bars = ax.barh(df_plot['Kandidat'], df_plot['Stimmen'], color=colors[:len(df_plot)])
ax.invert_yaxis()
ax.bar_label(bars, padding=10, fontsize=20, fontweight='bold') 
ax.tick_params(axis='y', labelsize=15)
plt.tight_layout()

# --- 7. LAYOUT LOGIK ---

if is_pres_mode:
    # --- ANSICHT FÜR DEN BEAMER (PUBLIKUM) ---
    if zettel_gezaehlt >= WAHLBERECHTIGTE:
        st.balloons()
        # Gewinner ermitteln (Platz 1 in der sortierten Liste)
        sieger = df_plot.iloc[0]['Kandidat']
        st.markdown(f"""
            <div style="background-color:#2ecc71; padding:20px; border-radius:10px; border: 5px solid #27ae60; text-align:center;">
                <h1 style="color:white; margin:0; font-size: 50px;">🎉 Herzlichen Glückwunsch 🎉</h1>
                <h2 style="color:white; margin:10px 0; font-size: 40px;">{sieger} ist gewählt!</h2>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align: center;'>📊 Aktueller Stand der Auszählung</h2>", unsafe_allow_html=True)
    
    st.pyplot(fig)
    
    c1, c2 = st.columns(2)
    with c1: st.metric("Stimmen erfasst", f"{zettel_gezaehlt} / {WAHLBERECHTIGTE}")
    with c2: 
        if zettel_gezaehlt < WAHLBERECHTIGTE:
            st.info(f"Fortschritt: {int(zettel_gezaehlt/WAHLBERECHTIGTE*100)}%")
        else:
            st.success("Ergebnis final bestätigt.")

else:
    # --- ADMIN-ANSICHT (DEIN LAPTOP) ---
    st.title("⚖️ Wahl-Administration")
    
    col_input, col_preview = st.columns([1, 2])
    
    with col_input:
        st.subheader("Eingabe")
        with st.form("wahl_form", clear_on_submit=True):
            wahl = st.radio("Kandidat:", KANDIDATEN_LISTE)
            if st.form_submit_button("Stimme speichern"):
                if zettel_gezaehlt < WAHLBERECHTIGTE:
                    stimmen_dict[str(wahl)] += 1
                    zettel_gezaehlt += 1
                    speichere_daten(stimmen_dict, zettel_gezaehlt)
                    st.rerun()
                else:
                    st.error("Limit erreicht!")
        
        if st.button("🗑️ Daten löschen / Reset"):
            if os.path.exists(SPEICHER_DATEI): os.remove(SPEICHER_DATEI)
            st.rerun()

    with col_preview:
        st.pyplot(fig)
        # Download Button nur am Ende
        if zettel_gezaehlt >= WAHLBERECHTIGTE:
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight')
            st.download_button("📸 Bild speichern", buf.getvalue(), "ergebnis.png", "image/png")

    st.table(df_plot)
