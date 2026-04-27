import streamlit as st
import requests
import pandas as pd
from datetime import date

# --- 1. DROŠA KONFIGURĀCIJA ---
try:
    # Paņemam atslēgas no Streamlit Secrets seifa
    RAPID_API_KEY = st.secrets["RAPID_API_KEY"]
    HUGGING_FACE_API_KEY = st.secrets["HUGGING_FACE_API_KEY"]
except Exception:
    st.error("⚠️ Kļūda: Streamlit 'Secrets' sadaļā nav atrasti API kodi!")
    st.info("Pārliecinies, ka iestatījumos esi ievadījis RAPID_API_KEY un HUGGING_FACE_API_KEY.")
    st.stop()

# --- 2. NBA DATU IEGŪŠANA AR DIAGNOSTIKU ---
def get_nba_games():
    today = date.today().strftime("%Y-%m-%d")
    url = "https://api-nba-v1.p.rapidapi.com/games"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }
    
    try:
        # Veicam pieprasījumu šodienas spēlēm
        response = requests.get(url, headers=headers, params={"date": today})
        
        # Ja serveris atsaka piekļuvi (403)
        if response.status_code == 403:
            st.error("🚫 RapidAPI joprojām liedz piekļuvi (Kļūda 403).")
            st.write("---")
            st.write("**Servera paskaidrojums:**", response.json())
            st.write(f"**Izmantotā atslēga:** `{RAPID_API_KEY[:5]}***{RAPID_API_KEY[-5:]}`")
            st.info("Padoms: Pārbaudi RapidAPI 'Endpoints' sadaļā, vai tava atslēga sakrīt ar šo.")
            return None, "Forbidden"
            
        if response.status_code == 200:
            res = response.json()
            if res.get('results', 0) == 0:
                return None, f"Šodien ({today}) NBA spēles sarakstā vēl nav parādījušās."
            
            games_list = []
            for item in res['response']:
                games_list.append({
                    "Spēle": f"{item['teams']['visitors']['name']} vs {item['teams']['home']['name']}",
                    "Laiks": item['status']['long'],
                    "Arēna": item['arena']['name'],
                    "Kef_1": 1.95, # Bāzes koeficients (analīzes modelēšanai)
                    "Kef_2": 1.95
                })
            return pd.DataFrame(games_list), None
        
        return None, f"Servera kļūda: {response.status_code}"
        
    except Exception as e:
        return None, f"Sistēmas kļūda: {str(e)}"

# --- 3. AI ZIŅU ANALĪZE ---
def analyze_news(text):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
    payload = {
        "inputs": text,
        "parameters": {"candidate_labels": ["savainojums", "pozitīvas ziņas", "nenozīmīgi"]}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        return {"error": f"AI servisa kļūda: {response.status_code}"}
    except:
        return {"error": "Nevarēja sasniegt AI serveri"}

# --- 4. VALUE BET MATEMĀTIKA ---
def calculate_value_score(kef, sentiment_impact=0):
    # Vienkāršots profesionālais modelis
    base_prob = 0.50 # Bāzes varbūtība 50/50
    adjusted_prob = base_prob + sentiment_impact
    value_score = adjusted_prob * kef
    return round(value_score, 2)

# --- 5. INTERFEISS (UI) ---
st.set_page_config(page_title="NBA AI PRO", page_icon="🏀", layout="wide")

st.title("🏀 NBA Pro-Analītikas Bots")
st.markdown(f"**Statuss:** Tiešsaistē | **Datums:** {date.today()}")

tab1, tab2 = st.tabs(["🔥 Spēļu Monitorings", "🧠 AI Ziņu Analīze"])

with tab1:
    if st.button("🚀 Skenēt NBA tirgu un meklēt izdevību"):
        with st.spinner("Savienojos ar NBA datu bāzi..."):
            df, error = get_nba_games()
            
            if df is not None:
                # Pievienojam Value Score aprēķinu
                df['Value_Score'] = df['Kef_1'].apply(calculate_value_score)
                
                st.write("### Aktuālās NBA spēles:")
                # Izceļam tabulā labāko vērtību
                st.dataframe(df.style.highlight_max(axis=0, subset=['Value_Score'], color='#2E7D32'), use_container_width=True)
                
                st.success("Skenēšana pabeigta! Meklē spēles ar zaļu fonu (Value > 1.05).")
            elif
