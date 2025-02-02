import streamlit as st
import pandas as pd
import requests
import time
import pycountry 

countries = [country.name for country in pycountry.countries]
languages = [f"{lang.alpha_2} - {lang.name}" for lang in pycountry.languages if hasattr(lang, 'alpha_2')]


def run_serperdev(api_key, keyword, location="Indonesia", lang="id", site=""):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    for num in range(10, 110, 10):  # Search in steps: 10, 20, ..., 100
        payload = {
            "q": keyword,
            "location": location,
            "gl": lang,
            "hl": lang,
            "num": num
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            filtered_result = next((item for item in result.get("organic", []) if site in item.get("link", "")), None)

            if filtered_result:
                return {"Keyword": keyword, "Position": filtered_result["position"], "URL": filtered_result["link"]}

        time.sleep(1)  # Delay to avoid rate limit

    return {"Keyword": keyword, "Position": "Not Found", "URL": "N/A"}


def fetch_top_10(api_key, keyword, location="Indonesia", lang="id"):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "q": keyword,
        "location": location,
        "gl": lang,
        "hl": lang,
        "num": 10  # Only fetch Top 10
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json().get("organic", [])  # Return only organic results

    return [{"error": "Failed to fetch data"}]

# Streamlit UI
st.set_page_config(page_title="SERP Rank Checker", layout="wide")

# Sidebar for API Key
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

# Process search if form is submitted
if submitted and api_key:
    keyword_list = [kw.strip() for kw in keywords.split("\n") if kw.strip()]
    
    if not keyword_list:
        st.error("Please enter at least one keyword.")
    elif not site:
        st.error("Please enter a domain to track.")
    else:
        st.info(f"Fetching SERP rankings for {len(keyword_list)} keywords...")

        results = []
        top_10_results = {}

        for keyword in keyword_list:
            result = run_serperdev(api_key, keyword, location, lang.split(" - ")[0], site)
            results.append(result)
            top_10_results[keyword] = fetch_top_10(api_key, keyword, location, lang.split(" - ")[0])  # Fetch Top 10 data

        df = pd.DataFrame(results)

        # Create Tabs
        tab1, tab2 = st.tabs(["📊 SERP Table", "🔍 Top 10 Results"])

        with tab1:
            st.write("### 📊 SERP Results")
            st.dataframe(df, use_container_width=True)

            # CSV Download Option
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
