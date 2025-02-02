import streamlit as st
import pandas as pd
import requests
import pycountry 

# Ambil daftar negara dan bahasa dari pycountry
countries = [country.name for country in pycountry.countries]
languages = [f"{lang.alpha_2} - {lang.name}" for lang in pycountry.languages if hasattr(lang, 'alpha_2')]

# Cache untuk menyimpan hasil pencarian selama 5 jam (18000 detik)
@st.cache_data(ttl=18000)
def get_serp_results(api_key, keyword, location, lang, site):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    # Langsung ambil 100 results karena lebih hemat (2 credits saja)
    payload = {
        "q": keyword,
        "location": location,
        "gl": lang,
        "hl": lang,
        "num": 100  
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        filtered_result = next((item for item in result.get("organic", []) if site in item.get("link", "")), None)

        return {
            "Keyword": keyword,
            "Position": filtered_result["position"] if filtered_result else "Not Found",
            "URL": filtered_result["link"] if filtered_result else "N/A",
            "Top_100": result.get("organic", [])  # Simpan seluruh 100 hasil pencarian
        }

    return {"Keyword": keyword, "Position": "Not Found", "URL": "N/A", "Top_100": []}

# Fungsi ini hanya mengambil Top 10 dari hasil `get_serp_results`
def fetch_top_10(results):
    return results["Top_100"][:10]  # Ambil 10 hasil pertama dari Top 100

# Streamlit UI
st.set_page_config(page_title="SERP Rank Checker", layout="wide")

# Sidebar untuk API Key
st.sidebar.header("🔑 API Settings")
api_key = st.sidebar.text_input("Enter your Serper.dev API Key", type="password")
st.sidebar.write("**[Get your API key at Serper.dev](https://serper.dev/)**")

st.sidebar.markdown("---")
st.sidebar.write("### 🔍 About Serper.dev")
st.sidebar.write("""
Serper.dev is a powerful **Google Search API** that allows you to retrieve real-time search results efficiently.
It offers **2,500 free queries** without requiring a credit card.
""")

st.sidebar.markdown("---")
st.sidebar.write("👤 **Connect with Me:**")
st.sidebar.markdown("🔗[Syahid Muhammad](http://syahid.super.site/)")

# Form input
st.title("🕷️ SERP Rank Checker")
st.write("A free and simple SERP checker—no ads, no CAPTCHA, just results.🚀")

with st.form("serp_form"):
    keywords = st.text_area("Keywords (one per line)", placeholder="Enter keywords here...")

    # Dropdown searchable untuk negara dan bahasa
    location = st.selectbox("Select Country", options=countries, index=countries.index("Indonesia"))
    lang = st.selectbox("Select Language", options=languages, index=languages.index("id - Indonesian"))

    site = st.text_input("Domain (e.g., example.com)", placeholder="Enter domain to track")
    
    submitted = st.form_submit_button("Check Rankings")

# Jika tombol diklik tanpa API Key, tampilkan error
if submitted:
    if not api_key:
        st.error("🚨 API Key is required! Please enter your Serper.dev API key in the sidebar.")
        st.stop()  # Hentikan eksekusi jika API Key kosong

    keyword_list = [kw.strip() for kw in keywords.split("\n") if kw.strip()]
    
    if not keyword_list:
        st.error("❌ Please enter at least one keyword.")
    elif not site:
        st.error("❌ Please enter a domain to track.")
    else:
        st.info(f"Fetching SERP rankings for {len(keyword_list)} keywords...")

        results = []
        top_10_results = {}

        for keyword in keyword_list:
            result = get_serp_results(api_key, keyword, location, lang.split(" - ")[0], site)
            results.append(result)
            top_10_results[keyword] = fetch_top_10(result)  # 🔥 Mengambil Top 10 tanpa request ulang

        # Hapus kolom "Top_100" dari tampilan tabel utama
        df = pd.DataFrame(results).drop(columns=["Top_100"])

        # Buat Tabs untuk hasil
        tab1, tab2 = st.tabs(["📊 SERP Table", "🔍 Top 10 Results"])

        with tab1:
            st.write("### 📊 SERP Results")
            st.dataframe(df, use_container_width=True)

            # Opsi Download CSV
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="serp_results.csv",
                mime="text/csv"
            )

        with tab2:
            st.write("### 🔍 Top 10 Search Results for Each Keyword")

            for keyword, results in top_10_results.items():
                with st.expander(f"{keyword}"):
                    for idx, entry in enumerate(results, start=1):
                        title = entry.get("title", "No Title")
                        link = entry.get("link", "No Link")
                        snippet = entry.get("snippet", "No Snippet Available")
                        date = entry.get("date", "Unknown Date")

                        st.write(f"**{idx}. {title}**")  
                        st.markdown(f"🔗 [{link}]({link})")  
                        st.write(f"📅 {date} | {snippet}")  
                        st.write("---")  
