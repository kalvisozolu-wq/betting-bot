import streamlit as st
import requests
import pandas as pd
from datetime import date

# --- 1. KONFIGURĀCIJA (ATSAVINĀTA NO KODA DROŠĪBAI) ---
try:
    RAPID_API_KEY = st.secrets["RAPID_API_KEY"]
    HUGGING_FACE_API_KEY = st.secrets["HUGGING_FACE_API_KEY"]
except Exception:
    st.error("⚠️ Kļūda: Secrets sadaļā nav atrasti API kodi!")
    st.stop()

# --- 2. FUNKCIJA: NBA DATU IEGŪŠANA NO RAPIDAPI ---
def get_nba_games():
    today = date.today().strftime("%Y-%m-%d")
    url = "https://api-nba-v1.p.rapidapi.com/games"
    
    querystring = {"date": today}
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            res = response.json()
            if res.get('results', 0) == 0:
                return None, f"Šodien ({today}) NBA spēles vēl nav ieplānotas vai atrastas."
            
            games_list = []
            for item in res['response']:
                games_list.append({
                    "Spēle": f"{item['teams']['visitors']['name']} vs {item['teams']['home']['name']}",
                    "Status": item['status']['long'],
                    "Arēna": item['arena']['name'],
                    "Kef_1": 1.95, # Bāzes koeficients (bukmeikeru API ir maksas, šis ir modelēšanai)
                    "Kef_2": 1.95
                })
            return pd.DataFrame(games_list), None
        else:
            return None, f"RapidAPI Kļūda: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"Sistēmas kļūda: {str(e)}"

# --- 3. FUNKCIJA: AI ZIŅU ANALĪZE (HUGGING FACE) ---
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
        return {"error": f"AI Kļūda: {response.status_code}"}
    except:
        return {"error": "Nevarēja sasniegt AI serveri"}

# --- 4. FUNKCIJA: VALUE BET APRĒĶINS ---
def calculate_value_score(kef, sentiment_impact=0):
    base_prob = 0.50
    adjusted_prob = base_prob + sentiment_impact
    value_score = adjusted_prob * kef
    return round(value_score, 2)

# --- 5. STREAMLIT UI ---
st.set_page_config(page_title="NBA AI PRO", page_icon="🏀", layout="wide")

st.title("🏀 NBA Pro-Analītikas Bots")
st.info("Bots ir savienots ar NBA RapidAPI un HuggingFace AI.")

tab1, tab2 = st.tabs(["🔥 Spēļu Monitorings", "🧠 AI Ziņu Analīze"])

with tab1:
    if st.button("🚀 Skenēt NBA tirgu un meklēt izdevību"):
        with st.spinner("Savienojos ar NBA serveriem..."):
            df, error = get_nba_games()
            
            if error:
                st.warning(error)
            elif df is not None:
                # Pievienojam Value Score
                df['Value_Score'] = df['Kef_1'].apply(calculate_value_score)
                
                st.write("### Šodienas NBA saraksts:")
                # Izceļam augstāko Value Score
                st.dataframe(df.style.highlight_max(axis=0, subset=['Value_Score'], color='#2E7D32'), use_container_width=True)
                st.success("Skenēšana pabeigta!")
            else:
                st.info("Šobrīd dati nav pieejami.")

with tab2:
    st.header("🧠 AI Baumu Analizators")
    news_input = st.text_area("Iekopē ziņu (piem. no Twitter):", height=100)
    
    if st.button("Analizēt ziņas ietekmi"):
        if news_input:
            with st.spinner("AI analizē kontekstu..."):
                result = analyze_news(news_input)
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    label = result['labels'][0]
                    score = result['scores'][0]
                    
                    st.subheader(f"Secinājums: {label.upper()}")
                    st.write(f"Ticamība: {round(score * 100, 1)}%")
                    
                    if label == "savainojums" and score > 0.6:
                        st.error("🚨 KRITISKI: Šī ziņa norāda uz sastāva problēmām! Ieteicams izvērtēt likmes pret šo komandu.")
                    elif label == "pozitīvas ziņas":
                        st.success("✅ POZITĪVI: Komandas kapacitāte pieaug.")
        else:
            st.warning("Lūdzu ievadi ziņu.")

st.sidebar.write(f"📅 Bots ir tiešsaistē: {date.today()}")
st.sidebar.write("✅ API statuss: Aktīvs")
