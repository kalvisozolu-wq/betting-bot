import streamlit as st
import requests
import pandas as pd
from datetime import date

# --- 1. DROŠA KONFIGURĀCIJA ---
try:
    # Paņemam atslēgas un noņemam liekas atstarpes ar .strip()
    RAPID_API_KEY = st.secrets["RAPID_API_KEY"].strip()
    HUGGING_FACE_API_KEY = st.secrets["HUGGING_FACE_API_KEY"].strip()
except Exception:
    st.error("⚠️ Kļūda: Streamlit 'Secrets' sadaļā nav atrasti API kodi!")
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
        # Sūtam pieprasījumu
        response = requests.get(url, headers=headers, params={"date": today}, timeout=10)
        
        # Ja serveris liedz piekļuvi (403)
        if response.status_code == 403:
            st.error("🚫 RapidAPI joprojām liedz piekļuvi (403 Forbidden).")
            st.write("### Diagnostika:")
            st.json(response.json())
            st.info(f"Pārbaudi: Vai tava atslēga RapidAPI lapā sakrīt ar: **{RAPID_API_KEY[:6]}...{RAPID_API_KEY[-4:]}**?")
            return None, "403"
            
        if response.status_code == 200:
            res = response.json()
            if not res.get('response'):
                return None, f"Šodien ({today}) NBA spēles sarakstā vēl nav parādījušās."
            
            games_list = []
            for item in res['response']:
                games_list.append({
                    "Spēle": f"{item['teams']['visitors']['name']} vs {item['teams']['home']['name']}",
                    "Laiks": item['status']['long'],
                    "Arēna": item['arena']['name'],
                    "Kef_1": 1.95, 
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
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": f"AI kļūda: {response.status_code}"}
    except:
        return {"error": "AI serveris nav sasniedzams"}

# --- 4. VALUE BET APRĒĶINS ---
def calculate_value_score(kef, sentiment_impact=0):
    base_prob = 0.50
    adjusted_prob = base_prob + sentiment_impact
    return round(adjusted_prob * kef, 2)

# --- 5. INTERFEISS (UI) ---
st.set_page_config(page_title="NBA AI PRO", page_icon="🏀", layout="wide")

# Sānjoslas info kontrolei
st.sidebar.title("⚙️ Iestatījumi")
st.sidebar.write(f"📅 Datums: {date.today()}")
st.sidebar.write(f"🔑 Ielādētā atslēga: `{RAPID_API_KEY[:4]}...{RAPID_API_KEY[-4:]}`")

st.title("🏀 NBA Pro-Analītikas Bots")
st.markdown("---")

tab1, tab2 = st.tabs(["🔥 Spēļu Monitorings", "🧠 AI Ziņu Analīze"])

with tab1:
    if st.button("🚀 Skenēt NBA tirgu"):
        with st.spinner("Iegūstu datus no NBA serveriem..."):
            df, error = get_nba_games()
            
            if df is not None:
                df['Value_Score'] = df['Kef_1'].apply(calculate_value_score)
                st.write("### Šodienas spēles:")
                st.dataframe(df.style.highlight_max(axis=0, subset=['Value_Score'], color='#2E7D32'), use_container_width=True)
                st.success("Skenēšana pabeigta!")
            elif error != "403":
                st.warning(error)

with tab2:
    st.header("🧠 AI Baumu Analizators")
    news_input = st.text_area("Iekopē ziņu angliski:", height=150)
    
    if st.button("Analizēt ietekmi"):
        if news_input:
            with st.spinner("Mākslīgais intelekts domā..."):
                result = analyze_news(news_input)
                if "error" not in result:
                    label = result['labels'][0]
                    score = result['scores'][0]
                    st.subheader(f"Secinājums: {label.upper()}")
                    st.write(f"Ticamība: {round(score * 100, 1)}%")
                    
                    if label == "savainojums" and score > 0.6:
                        st.error("🚨 Brīdinājums: Ziņa liecina par sastāva problēmām!")
                    elif label == "pozitīvas ziņas":
                        st.success("✅ Pozitīvs signāls komandai.")
                else:
                    st.error(result["error"])
        else:
            st.warning("Lūdzu, ievadi tekstu.")

st.sidebar.markdown("---")
st.sidebar.info("📊 Mērķis: 5€ ➔ 100€ stratēģija")
