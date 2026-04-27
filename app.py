import streamlit as st
import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText

# --- KONFIGURĀCIJA ---
HUGGING_FACE_API_KEY = "TAVA_HUGGING_FACE_TOKEN_ATSLĒGA"
SENDER_EMAIL = "tavsbots@gmail.com"
SENDER_PASSWORD = "tava_gmail_app_parole"
RECEIVER_EMAIL = "tavs.istais.epasts@gmail.com"

# --- 1. VIENKĀRŠOTA DATU IEGŪŠANA (Bez Playwright) ---
def get_mock_data():
    # Kamēr sakārtojam piekļuvi Olybet caur API, izmantojam struktūru
    data = [
        {"Spēle": "Žalgiris vs Real Madrid", "Kef 1": 2.15, "Kef 2": 1.72, "Tips": "Euroleague"},
        {"Spēle": "Monaco vs Barcelona", "Kef 1": 1.85, "Kef 2": 1.95, "Tips": "Euroleague"},
        {"Spēle": "Lakers vs Celtics", "Kef 1": 2.05, "Kef 2": 1.80, "Tips": "NBA"}
    ]
    return pd.DataFrame(data)

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
