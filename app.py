import streamlit as st
import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText

# --- KONFIGURĀCIJA (IEVADI SAVUS DATUS ŠEIT) ---
RAPID_API_KEY = "181c1c87ddmsh1dc01840c36bb61p11954ajsn613917400f0b"
HUGGING_FACE_API_KEY = "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"
# E-pasta dati (pēc izvēles, ja gribi paziņojumus)
SENDER_EMAIL = "kalvis.ozolu@gmail.com"
SENDER_PASSWORD = "tava_app_parole"
RECEIVER_EMAIL = "kalvis.ozolu@gmail.com"

# --- 1. FUNKCIJA: IEGŪT ĪSTOS NBA KOEFICIENTUS ---
def get_nba_odds():
    url = "https://api-nba-v1.p.rapidapi.com/odds"
    # Šeit mēs norādām parametrus. NBA id parasti ir 12.
    querystring = {"league": "12", "season": "2023"} 
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()['response']
            # Izvelkam svarīgāko: Spēli un koeficientus
            games = []
            for item in data[:10]: # Apskatām pirmās 10 spēles
                game_name = f"{item['game']['teams']['home']['name']} vs {item['game']['teams']['visitors']['name']}"
                # Pieņemam, ka skatāmies pirmo pieejamo bukmeikeru
                odds = item['bookmakers'][0]['bets'][0]['values']
                games.append({
                    "Spēle": game_name,
                    "Kef_1": float(odds[0]['odd']),
                    "Kef_2": float(odds[1]['odd']),
                    "Sākums": item['game']['date']['start']
                })
            return pd.DataFrame(games)
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- 2. FUNKCIJA: VALUE BET MATEMĀTIKA ---
def calculate_value(row, ai_sentiment):
    # Vienkāršots modelis: 
    # 1. Bukmeikera varbūtība = 1 / koeficients
    prob_1 = 1 / row['Kef_1']
    
    # 2. Mūsu "Gudrā" varbūtība (šeit var pievienot vairāk statistikas)
    # Pieņemsim, ka bāzes varbūtība ir 50% (0.50)
    our_prob = 0.50
    
    # 3. Pieliekam AI ietekmi (sentimentu)
    if ai_sentiment == "pozitīvi": our_prob += 0.10
    if ai_sentiment == "savainojums": our_prob -= 0.15
    
    # 4. Aprēķinām Value: ja mūsu varbūtība * koeficients > 1, tā ir vērtība
    value_score = our_prob * row['Kef_1']
    
    return round(value_score, 2)

# --- 3. UI IZSTRĀDE ---
st.set_page_config(page_title="NBA AI PRO", layout="wide")
st.title("🏀 NBA Pro-Analītikas Bots")

tab1, tab2 = st.tabs(["🔥 Value Bet Meklētājs", "🧠 Ziņu Analīze"])

with tab1:
    if st.button("Skenēt NBA tirgu un meklēt izdevību"):
        with st.spinner("Savienojos ar RapidAPI..."):
            df = get_nba_odds()
            if not df.empty:
                # Pievienojam aprēķinu kolonnu (pagaidām bez aktīvas ziņas)
                df['Value_Score'] = df.apply(lambda x: calculate_value(x, "neitrāls"), axis=1)
                
                # Izceļam izdevīgās likmes
                st.write("### Atrastās spēles un Value Score")
                st.write("*(Value Score > 1.05 nozīmē potenciālu peļņu)*")
                
                # Formatējam tabulu, lai redzētu vērtīgāko augšgalā
                st.dataframe(df.sort_values(by='Value_Score', ascending=False), use_container_width=True)
            else:
                st.error("Neizdevās iegūt datus. Pārbaudi RapidAPI atslēgu!")

with tab2:
    st.header("Ziņu un baumu ietekme")
    news_text = st.text_area("Iekopē pēdējo ziņu no Twitter/ESPN:")
    if st.button("Analizēt ietekmi uz likmi"):
        # Šeit izsaucam Hugging Face (kā iepriekšējā kodā)
        st.info("AI modelis analizē spēlētāju traumas...")
        # ... (šeit būs tavs Hugging Face rezultāts)
