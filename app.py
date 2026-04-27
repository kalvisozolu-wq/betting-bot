import streamlit as st
import requests
import pandas as pd
from datetime import date

# --- 1. KONFIGURĀCIJA (DROŠA ATSLĒGU IEGŪŠANA) ---
try:
    RAPID_API_KEY = st.secrets["181c1c87ddmsh1dc01840c36bb61p11954ajsn613917400f0b"]
    HUGGING_FACE_API_KEY = st.secrets["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"]
except Exception:
    st.error("Kļūda: Streamlit iestatījumos (Secrets) nav atrastas API atslēgas!")
    st.info("Pievieno RAPID_API_KEY un HUGGING_FACE_API_KEY savā Streamlit panelī.")
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
            if res['results'] == 0:
                return None, f"Šodien ({today}) NBA spēles nav atrastas."
            
            games_list = []
            for item in res['response']:
                # Pievienojam fiktīvus koeficientus analīzei, ja API tos neiedod tieši
                # Profesionālā versijā šeit slēdzam klāt /odds endpointu
                games_list.append({
                    "Spēle": f"{item['teams']['visitors']['name']} @ {item['teams']['home']['name']}",
                    "Sākums": item['status']['long'],
                    "Arēna": item['arena']['name'],
                    "Kef_1": 1.95, # Bāzes koeficients testa nolūkiem
                    "Kef_2": 1.95
                })
            return pd.DataFrame(games_list), None
        else:
            return None, f"RapidAPI kļūda: {response.status_code}"
    except Exception as e:
        return None, str(e)

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
        return {"error": "AI serviss nav pieejams"}
    except:
        return {"error": "Savienojuma kļūda"}

# --- 4. FUNKCIJA: VALUE BET APRĒĶINS ---
def calculate_value_score(kef, sentiment_impact=0):
    # Matemātiskais modelis: (Varbūtība + AI ietekme) * Koeficients
    base_prob = 0.50 # 50% bāzes iespēja uzvarēt
    adjusted_prob = base_prob + sentiment_impact
    value_score = adjusted_prob * kef
    return round(value_score, 2)

# --- 5. STREAMLIT UI (INTERFEISS) ---
st.set_page_config(page_title="NBA AI PRO", page_icon="🏀", layout="wide")

st.title("🏀 NBA Pro-Analītikas Bots")
st.markdown("---")

tab1, tab2 = st.tabs(["🔥 Spēļu Monitorings", "🧠 AI Ziņu Analīze"])

with tab1:
    st.header("Šodienas NBA spēles")
    if st.button("Skenēt tirgu"):
        with st.spinner("Iegūstu datus no NBA serveriem..."):
            df, error = get_nba_games()
            
            if error:
                st.warning(error)
            elif df is not None:
                # Aprēķinām Value Score katrai spēlei
                df['Value_Score'] = df['Kef_1'].apply(calculate_value_score)
                
                # Vizualizācija
                st.write("Atrastās spēles:")
                st.dataframe(df.style.highlight_max(axis=0, subset=['Value_Score'], color='#2E7D32'), use_container_width=True)
                
                st.success("Analīze pabeigta. Meklē spēles ar Value Score virs 1.05!")
            else:
                st.info("Dati nav pieejami.")

with tab2:
    st.header("AI Ziņu un Baumu Analizators")
    st.write("Iekopē ziņu (angliski), lai bots saprastu tās ietekmi uz spēli.")
    
    news_input = st.text_area("Ziņas teksts (piemēram, no Twitter):", height=150)
    
    if st.button("Analizēt ziņas ietekmi"):
        if news_input:
            with st.spinner("Mākslīgais intelekts domā..."):
                result = analyze_news(news_input)
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    label = result['labels'][0]
                    score = result['scores'][0]
                    
                    st.write(f"### Galvenais secinājums: **{label.upper()}**")
                    st.write(f"Ticamība: {round(score * 100, 1)}%")
                    
                    # Ieteikums balstoties uz AI
                    if label == "savainojums" and score > 0.7:
                        st.error("⚠️ Brīdinājums: Šī ziņa būtiski pasliktina komandas izredzes. Meklē likmes pret šo komandu!")
                    elif label == "pozitīvas ziņas":
                        st.success("✅ Pozitīvs signāls: Komandas kapacitāte pieaug.")
        else:
            st.warning("Lūdzu, vispirms ievadi ziņas tekstu.")

st.sidebar.markdown("---")
st.sidebar.write("💰 **Bota statuss:** Aktīvs")
st.sidebar.write(f"📅 **Datums:** {date.today()}")
