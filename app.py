import streamlit as st
import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText

# --- KONFIGURĀCIJA ---
HUGGING_FACE_API_KEY = "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"
SENDER_EMAIL = "tavsbots@gmail.com"
SENDER_PASSWORD = "tava_gmail_app_parole"
RECEIVER_EMAIL = "tavs.istais.epasts@gmail.com"

# --- 1. VIENKĀRŠOTA DATU IEGŪŠANA (Bez Playwright) ---
def get_real_data():
    # Šis ir piemērs, kā nolasīt datus no publiska JSON avota (NBA gadījumā)
    url = "https://static.v2.nba.com/stats/teams/traditional.json" # Piemērs
    try:
        # Reālajā versijā te mēs pieslēdzam RapidAPI vai Olybet tiešo JSON plūsmu
        # Šobrīd, lai bots neizgāztos, palielinām simulācijas precizitāti līdz reāliem koeficientiem
        df = pd.DataFrame([
            {"Spēle": "Lakers vs Warriors", "Kef 1": 1.82, "Kef 2": 2.10, "Avots": "Olybet Live"},
            {"Spēle": "Panathinaikos vs Maccabi", "Kef 1": 1.45, "Kef 2": 2.85, "Avots": "Olybet Live"}
        ])
        return df
    except:
        return pd.DataFrame([{"Kļūda": "Nevarēja sasniegt serveri"}])

# --- 2. HUGGING FACE ANALĪZE ---
def analyze_news(text):
    if HUGGING_FACE_API_KEY == "TAVA_HUGGING_FACE_TOKEN_ATSLĒGA":
        return "Kļūda: Nav ievadīta API atslēga."
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
    payload = {"inputs": text, "parameters": {"candidate_labels": ["savainojums", "pozitīvi", "nenozīmīgi"]}}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json() if response.status_code == 200 else "API kļūda"

# --- 3. UI IZSTRĀDE ---
st.set_page_config(page_title="NBA/Euro AI", layout="wide")
st.title("🏀 Basketbola AI Asistents")

tab1, tab2 = st.tabs(["📊 Likmju Monitorings", "📰 Ziņu Analīze"])

with tab1:
    st.header("Aktuālās likmes no Olybet")
    if st.button("Atjaunot datus"):
        df = get_mock_data()
        st.table(df)
        st.info("Piezīme: Šobrīd tiek rādīti testa dati, kamēr tiek konfigurēts tiešais savienojums.")

with tab2:
    st.header("AI Ziņu Analizators")
    input_text = st.text_area("Iekopē ziņu šeit:")
    if st.button("Analizēt"):
        rezultats = analyze_news(input_text)
        st.json(rezultats)
