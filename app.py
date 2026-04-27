import streamlit as st
import requests
import pandas as pd
from datetime import date

# --- 1. DROŠA KONFIGURĀCIJA ---
# Mēģinām ielādēt atslēgas no Streamlit Secrets
try:
    RAPID_API_KEY = st.secrets["RAPID_API_KEY"].strip()
    HUGGING_FACE_API_KEY = st.secrets["HUGGING_FACE_API_KEY"].strip()
except Exception:
    st.error("⚠️ Kļūda: Streamlit 'Secrets' nav atrasti! Pievieno tos Streamlit iestatījumos.")
    st.stop()

# --- 2. NBA DATU IEGŪŠANA ---
def get_nba_games():
    today = date.today().strftime("%Y-%m-%d")
    url = "https://api-nba-v1.p.rapidapi.com/games"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params={"date": today}, timeout=10)
        
        if response.status_code == 403:
            return None, "RapidAPI 403: Nav abonēts vai nepareiza atslēga."
            
        if response.status_code == 200:
            data = response.json()
            if not data.get('response'):
                return None, f"Šodien ({today}) spēles nav atrastas."
            
            games = []
            for item in data['response']:
                games.append({
                    "Spēle": f"{item['teams']['visitors']['name']} vs {item['teams']['home']['name']}",
                    "Statuss": item['status']['long'],
                    "Arēna": item['arena']['name'],
                    "Kef_1": 1.90, # Testa koeficients
                    "Kef_2": 1.90
                })
            return pd.DataFrame(games), None
            
        return None, f"Kļūda: {response.status_code}"
    except Exception as e:
        return None, f"Sistēmas kļūda: {str(e)}"

# --- 3. AI ANALĪZE ---
def analyze_news(text):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
    payload = {
        "inputs": text,
        "parameters": {"candidate_labels": ["savainojums", "pozitīvas ziņas", "nenozīmīgi"]}
    }
    try:
        res = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        return res.json() if res.status_code == 200 else {"error": "AI kļūda"}
    except:
        return {"error": "AI nav sasniedzams"}

# --- 4. INTERFEISS ---
st.set_page_config(page_title="NBA AI PRO", layout="wide")

st.title("🏀 NBA AI Analītikas Bots")
st.write(f"Šodienas datums: {date.today()}")

tab1, tab2 = st.tabs(["📊 NBA Spēles", "🧠 AI Analizators"])

with tab1:
    if st.button("🚀 Skenēt NBA"):
        with st.spinner("Meklēju spēles..."):
            df, error = get_nba_games()
            if df is not None:
                st.dataframe(df, use_container_width=True)
                st.success("Dati ielādēti!")
            else:
                st.error(error)

with tab2:
    txt = st.text_area("Iekopē ziņu angliski:")
    if st.button("Analizēt"):
        if txt:
            res = analyze_news(txt)
            if "error" not in res:
                st.write(f"### Rezultāts: {res['labels'][0].upper()}")
                st.write(f"Ticamība: {round(res['scores'][0]*100)}%")
            else:
                st.error(res["error"])

st.sidebar.write(f"🔑 Key status: `{RAPID_API_KEY[:4]}...{RAPID_API_KEY[-4:]}`")
