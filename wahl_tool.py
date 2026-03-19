import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import io

# --- 1. URL-CHECK ZUERST ---
query_params = st.query_params
is_pres_mode = query_params.get("view") == "pres"

# --- 2. KONFIGURATION ---
KANDIDATEN_LISTE = ["Nina", "Daniel", "Ungültig"] 
WAHLBERECHTIGTE = 163
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

# --- 5. AUTOMATISCHER REFRESH (BEAMER) ---
if is_pres_mode and zettel_gezaehlt < WAHLBERECHTIGTE:
    st.markdown("<meta http-equiv='refresh' content='5'>", unsafe_allow_html=True)

# --- 6. DATENAUFBEREITUNG & GRAFIK ---
df_plot = pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen'])
df_plot['Kandidat'] = df_plot['Kandidat'].astype(str)
df_plot = df_plot.sort_values(by='Stimmen', ascending=False).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(10, 4.5))
colors = ['#3498db', '#e74c3c', '#95a5a6'] 
bars = ax.barh(df_plot['Kandidat'], df_plot['Stimmen'], color=colors[:len(df_plot)])
ax.invert_yaxis()
ax.bar_label(bars, padding=10, fontsize=18, fontweight='bold') 
ax.tick_params(axis='y', labelsize=14)
plt.tight_layout()

# --- 7. LAYOUT LOGIK ---

if is_pres_mode:
    # --- ANSICHT FÜR DEN BEAMER ---
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("📊 Erfasste Stimmzettel", f"{zettel_gezaehlt} / {WAHLBERECHTIGTE}")
    with col_b:
        if zettel_gezaehlt >= WAHLBERECHTIGTE:
            st.success("Auszählung beendet")
        else:
            st.info(f"Fortschritt: {int(zettel_gezaehlt/WAHLBERECHTIGTE*100)}%")

    if zettel_gezaehlt >= WAHLBERECHTIGTE:
        st.balloons()
        sieger = df_plot.iloc[0]['Kandidat']
        st.markdown(f"<div style='background-color:#2ecc71; padding:15px; border-radius:10px; text-align:center; border: 4px solid #27ae60;'><h1 style='color:white; margin:0;'>🎉 Glückwunsch, {sieger}! 🎉</h1></div>", unsafe_allow_html=True)
    
    st.pyplot(fig)

else:
    # --- ADMIN-ANSICHT (DEIN LAPTOP) ---
    st.title("⚖️ Wahl-Leitung")
    
    col_input, col_preview = st.columns([1, 2])
    
    with col_input:
        st.subheader("📝 Eingabe")
        
        # WICHTIG: Anzeige direkt über/im Formular
        st.info(f"Aktueller Zettel: **{zettel_gezaehlt + 1}** von {WAHLBERECHTIGTE}")
        
        with st.form("wahl_form", clear_on_submit=True):
            wahl = st.radio("Wer wurde gewählt?", KANDIDATEN_LISTE)
            
            # Button Text zeigt auch den Fortschritt
            btn_label = f"Stimme {zettel_gezaehlt + 1} speichern" if zettel_gezaehlt < WAHLBERECHTIGTE else "Limit erreicht"
            
            if st.form_submit_button(btn_label):
                if zettel_gezaehlt < WAHLBERECHTIGTE:
                    stimmen_dict[str(wahl)] += 1
                    zettel_gezaehlt += 1
                    speichere_daten(stimmen_dict, zettel_gezaehlt)
                    st.rerun()
                else:
                    st.error("Alle Stimmzettel wurden bereits erfasst!")
        
        st.markdown("---")
        if st.button("🗑️ Komplett-Reset"):
            if os.path.exists(SPEICHER_DATEI): os.remove(SPEICHER_DATEI)
            st.rerun()

    with col_preview:
        st.subheader("Vorschau (Beamer)")
        st.pyplot(fig)
        
        if zettel_gezaehlt >= WAHLBERECHTIGTE:
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight')
            st.download_button("📸 Endergebnis-Bild speichern", buf.getvalue(), "wahl_ergebnis.png")

    # Tabelle für die genauen Zahlen
    st.table(df_plot)
