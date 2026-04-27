import streamlit as st
import os

@st.cache_resource
def setup_playwright():
    os.system("playwright install chromium")

setup_playwright()

# ... (tālāk paliek viss vecais kods: import requests, smtplib utt.)
