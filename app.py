def get_nba_games():
    today = date.today().strftime("%Y-%m-%d")
    url = "https://api-nba-v1.p.rapidapi.com/games"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY.strip(), # .strip() noņem liekas atstarpes
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, params={"date": today})
    
    if response.status_code == 403:
        st.error("❌ RapidAPI joprojām saka: NAV ABONĒTS")
        st.write("---")
        st.write(f"**Tava atslēga beidzas ar:** `...{RAPID_API_KEY[-5:]}`")
        st.write("**Servera pilnā atbilde:**", response.json())
        st.info("Pārbaudi: RapidAPI lapā pie 'Endpoints' nospied 'Test Endpoint'. Vai tur rāda zaļu 200 vai sarkanu 403?")
        return None, "403"
    
    # Ja viss kārtībā
    if response.status_code == 200:
        return pd.DataFrame(response.json()['response']), None
    return None, f"Kļūda: {response.status_code}"
