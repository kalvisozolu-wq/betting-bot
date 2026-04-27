import streamlit as st
import requests
import pandas as pd
from datetime import date

# --- KONFIGURĀCIJA NO SECRETS ---
try:
    # .strip() noņem nejaušas atstarpes, kas var sabojāt atslēgu
    RAPID_KEY = st.secrets["RAPID_API_KEY"].strip()
    HF_KEY = st.secrets["HUGGING_FACE_API_KEY"].strip()
except Exception:
    st.error("Kļūda: Streamlit Secrets nav pareizi iestatīti!")
    st.stop()

# --- FUNKCIJA DATU IEGŪŠANAI (TIEŠI KĀ TAVĀ BILDĒ) ---
def get_nba_games():
    today = date.today().strftime("%Y-%m-%d")
    url = "https://api-nba-v1.p.rapidapi.com/games"
    
    # Šīs ir galvenās rindiņas no tava ekrānuzņēmuma
    headers = {
        "x-rapidapi-key": RAPID_KEY,
        "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
    }
    querystring = {"date": today}
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        return response
    except Exception as e:
        return str(e)

# --- BOTA INTERFEISS ---
st.set_page_config(page_title="NBA AI PRO", page_icon="🏀", layout="wide")

st.title("🏀 NBA Pro-Analītikas Bots")
st.sidebar.markdown(f"**Sistēmas statuss:** Online")
st.sidebar.markdown(f"**Atslēga:** `{RAPID_KEY[:5]}...{RAPID_KEY[-5:]}`")

tab1, tab2 = st.tabs(["📊 Šodienas Spēles", "🧠 AI Analīze"])

with tab1:
    if st.button("🚀 Skenēt NBA tirgu"):
        with st.spinner("Sazinoties ar NBA serveri..."):
            res = get_nba_games()
            
            if isinstance(res, str):
                st.error(f"Sistēmas kļūda: {res}")
            elif res.status_code == 200:
                data = res.json()
                if data.get('response'):
                    st.success("✅ Savienojums izveidots!")
                    # Izveidojam tabulu
                    games = []
                    for g in data['response']:
                        games.append({
                            "Spēle": f"{g['teams']['visitors']['name']} @ {g['teams']['home']['name']}",
                            "Laiks": g['status']['long'],
                            "Arēna": g['arena']['name'],
                            "Value Score": 1.05 # Provizorisks
                        })
                    st.dataframe(pd.DataFrame(games), use_container_width=True)
                else:
                    st.info(f"Šodien ({today}) NBA spēles vēl nav sākušās vai nav sarakstā.")
            elif res.status_code == 403:
                st.error("🚫 Piekļuve liegta (403 Forbidden)")
                st.write("Serveris nepieņem tavu atslēgu. Pārbaudi 'Pricing' sadaļu RapidAPI lapā.")
                st.json(res.json()) # Parāda detaļas
            else:
                st.error(f"Kļūda {res.status_code}: {res.text}")

with tab2:
    st.info("Ielādē NBA spēles, lai aktivizētu AI analīzi.")
