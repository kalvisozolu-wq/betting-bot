import streamlit as st
import requests
import pandas as pd
from datetime import date

# --- 1. DROŠA ATSLĒGU IELĀDE ---
if "RAPID_API_KEY" not in st.secrets:
    st.error("❌ Kļūda: Streamlit 'Secrets' sadaļā nav atrasta RAPID_API_KEY!")
    st.stop()

# Noņemam liekas atstarpes, ja tādas gadījušās kopējot
RAPID_API_KEY = st.secrets["RAPID_API_KEY"].strip()
HUGGING_FACE_API_KEY = st.secrets["HUGGING_FACE_API_KEY"].strip()

# --- 2. NBA DATU IEGŪŠANA ---
def get_nba_games_live():
    today = date.today().strftime("%Y-%m-%d")
    url = "https://api-nba-v1.p.rapidapi.com/games"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params={"date": today}, timeout=15)
        
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 403:
            # Šis ir tas, ko mēs šobrīd redzam
            return None, "FORBIDDEN"
        else:
            return None, f"Kļūda {response.status_code}: {response.text}"
    except Exception as e:
        return None, str(e)

# --- 3. UI (INTERFEISS) ---
st.set_page_config(page_title="NBA AI Bots", layout="wide")

st.title("🏀 NBA Pro-Analītikas Bots")

# Sānjoslas diagnostika
st.sidebar.title("⚙️ Diagnostika")
st.sidebar.write(f"Ielādētā atslēga: `{RAPID_API_KEY[:4]}...{RAPID_API_KEY[-4:]}`")

tab1, tab2 = st.tabs(["📊 Šodienas Spēles", "🧠 AI Analīze"])

with tab1:
    if st.button("🚀 Skenēt NBA tirgu"):
        with st.spinner("Sazinoties ar NBA datubāzi..."):
            data, err = get_nba_games_live()
            
            if err == "FORBIDDEN":
                st.error("🚫 RapidAPI liedz piekļuvi! (403 Forbidden)")
                st.warning("Tava atslēga ir ielādēta, bet RapidAPI saka, ka neesi abonējis šo API.")
                st.markdown(f"""
                ### Kā to atrisināt tagad:
                1. Iej šajā lapā: [API-NBA Endpoints](https://rapidapi.com/api-sports/api/api-nba/endpoints)
                2. Labajā pusē (Code Snippets) izvēlies **Python -> Requests**.
                3. Pārbaudi, vai tur redzamā atslēga sakrīt ar tavējo: `{RAPID_API_KEY[:8]}...`
                4. Ja atslēga atšķiras, nokopē JAUNO un ieliec Streamlit Secrets.
                """)
            elif err:
                st.error(f"Sistēmas kļūda: {err}")
            elif data and data.get('response'):
                df = pd.DataFrame([
                    {
                        "Spēle": f"{g['teams']['visitors']['name']} vs {g['teams']['home']['name']}",
                        "Statuss": g['status']['long'],
                        "Arēna": g['arena']['name'],
                        "Kef 1": 1.95,
                        "Kef 2": 1.95
                    } for g in data['response']
                ])
                st.table(df)
                st.success("Dati ielādēti!")
            else:
                st.info("Šodienas NBA spēles vēl nav atrastas.")

with tab2:
    st.write("Šeit parādīsies AI analīze, kad būs ielādēti spēļu dati.")
