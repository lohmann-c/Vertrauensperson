import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import io

# --- 1. URL-CHECK & REFRESH ---
query_params = st.query_params
is_pres_mode = query_params.get("view") == "pres"

# --- 2. KONFIGURATION ---
KANDIDATEN_LISTE = [
    "John - Patrick B.", "Mario B.", "Nina D.", "Pal D.", "Angelo H.",
    "Christian L.", "Steffen M.", "Saskia M.", "Marvin M.", "Nico N.",
    "Frank O.", "Andre S.", "Sven S.", "Oliver S.", "Thomas T.",
    "Udo Z.", "Daniel Z.-H.", "Dummy"
]
GEWINNER_ANZAHL = 12
WAHLBERECHTIGTE = 243
MAX_STIMMEN_PRO_ZETTEL = 12
SPEICHER_DATEI = "wahlergebnisse.csv"

st.set_page_config(
    page_title="Wahl-Tool Pro", 
    layout="wide", 
    page_icon="🗳️",
    initial_sidebar_state="collapsed" if is_pres_mode else "expanded"
)

# --- 3. FUNKTIONEN ---
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

if is_pres_mode and zettel_gezaehlt < WAHLBERECHTIGTE:
    st.markdown("<meta http-equiv='refresh' content='5'>", unsafe_allow_html=True)

if zettel_gezaehlt >= WAHLBERECHTIGTE:
    st.balloons()

# --- 4. DATENAUFBEREITUNG ---
df = pd.DataFrame(list(stimmen_dict.items()), columns=['Kandidat', 'Stimmen'])
df = df.sort_values(by=['Stimmen', 'Kandidat'], ascending=[False, True]).reset_index(drop=True)
df['Status'] = 'Nicht gewählt'
df.loc[df.index < GEWINNER_ANZAHL, 'Status'] = '✅ GEWÄHLT'

# --- 5. GRAFIK (SCHMAL & KOMPAKT) ---
# Höhe auf 5.0 für Beamer-Optimierung
fig, ax = plt.subplots(figsize=(10, 5.0))
colors = ['#2ecc71' if s == '✅ GEWÄHLT' else '#bdc3c7' for s in df['Status']]

# Balken schmaler (height=0.6) für weniger Platzverbrauch
bars = ax.barh(df['Kandidat'], df['Stimmen'], color=colors, height=0.6)
ax.invert_yaxis()

# Beschriftungen klein halten
ax.bar_label(bars, padding=5, fontsize=10, fontweight='bold')
ax.tick_params(axis='y', labelsize=9)
ax.set_xlabel("Stimmen", fontsize=9)
plt.tight_layout()

# --- 6. LAYOUT ---

if is_pres_mode:
    # --- BEAMER ANSICHT ---
    st.markdown("<h3 style='text-align: center; margin-top: -30px; margin-bottom: 5px;'>🗳️ Live-Auszählung</h3>", unsafe_allow_html=True)
    st.pyplot(fig)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(label="Stimmzettel", value=f"{zettel_gezaehlt} / {WAHLBERECHTIGTE}")
    with col_b:
        if zettel_gezaehlt >= WAHLBERECHTIGTE:
            st.success("Abgeschlossen!")
        else:
            prozent = int((zettel_gezaehlt / WAHLBERECHTIGTE) * 100)
            st.info(f"Fortschritt: {prozent}%")

else:
    # --- ADMIN ANSICHT ---
    st.title("⚙️ Wahl-Leitung Admin")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="Fortschritt", value=f"{zettel_gezaehlt} / {WAHLBERECHTIGTE}")
        st.progress(zettel_gezaehlt / WAHLBERECHTIGTE)
        
        with st.form("stimmzettel_form", clear_on_submit=True):
            st.subheader("Neuer Stimmzettel")
            selected = []
            for name in KANDIDATEN_LISTE:
                if st.checkbox(name, key=f"cb_{name}"):
                    selected.append(name)
            
            if st.form_submit_button("Stimmen verbuchen"):
                if len(selected) > MAX_STIMMEN_PRO_ZETTEL:
                    st.error(f"Zuviele Stimmen ({len(selected)})!")
                elif len(selected) == 0:
                    st.warning("Leer-Zettel?")
                elif zettel_gezaehlt >= WAHLBERECHTIGTE:
                    st.error("Maximum erreicht!")
                else:
                    for c in selected: stimmen_dict[c] += 1
                    zettel_gezaehlt += 1
                    speichere_daten(stimmen_dict, zettel_gezaehlt)
                    st.rerun()

    with col2:
        st.pyplot(fig)
        with st.sidebar:
            st.header("Optionen")
            # Bild Export
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight')
            st.download_button("📸 Bild speichern", buf.getvalue(), "ergebnis.png", "image/png")
            
            # CSV Export
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 CSV herunterladen", csv_data, "ergebnis.csv", "text/csv")
            
            st.markdown("---")
            if st.button("🗑️ DATEN LÖSCHEN"):
                if os.path.exists(SPEICHER_DATEI): os.remove(SPEICHER_DATEI)
                st.rerun()

    st.subheader("Detailübersicht")
    st.dataframe(df[['Kandidat', 'Stimmen', 'Status']], use_container_width=True)
Was ist hier anders als in deinem geposteten Code?
Checkboxen statt Radio: Du kannst jetzt bis zu 12 Kreuze gleichzeitig setzen (für die 18 Kandidaten).

Kompakte Grafik: figsize=(10, 5.0) und height=0.6 sorgen dafür, dass die 18 Balken untereinander passen, ohne dass der Browser Scrollbalken anzeigt.

Status-Check: Die Top 12 werden automatisch grün als "gewählt" markiert.

Soll ich noch etwas anpassen, oder bist du bereit für die Wahl?
