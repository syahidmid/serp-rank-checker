import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from urllib.parse import urlparse 

# Fungsi untuk mengambil hasil pencarian dengan serper.dev API
def get_serp_results(api_key, query, num_results=20, location="US", lang="en"):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "q": query,  
        "num": num_results,  
        "location": location,  
        "hl": lang,
        "gl": location
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        st.error(f"❌ Error: {response.status_code} - {response.text}")
        return []

    result = response.json()
    urls = [item['link'] for item in result.get('organic', [])]
    return urls

# Fungsi untuk mencari email di halaman web
def extract_emails_from_url(url, target_domain=None):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return [], []  # Mengembalikan list kosong jika tidak ada hasil

        soup = BeautifulSoup(response.text, 'html.parser')
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b', soup.get_text())
        valid_emails = clean_email_data(emails, target_domain)
        return valid_emails, [url] * len(valid_emails)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return [], [] 

# Fungsi untuk membersihkan dan memverifikasi email
def clean_email_data(emails, target_domain=None):
    valid_emails = []
    
    for email in emails:
        if target_domain:
            # Memotong apapun setelah domain yang dimasukkan pengguna
            cleaned_email = re.sub(r'(@' + re.escape(target_domain) + r').*', r'\1', email)
            
            # Verifikasi bahwa email sudah dalam format yang benar menggunakan regex
            if re.match(r'^[a-zA-Z0-9._%+-]+@' + re.escape(target_domain) + r'$', cleaned_email):
                valid_emails.append(cleaned_email)
        else:
            # Jika tidak ada target domain, masukkan email apa adanya
            valid_emails.append(email)
    
    return valid_emails

# Streamlit UI setup
st.set_page_config(page_title="Email Finder", layout="wide")

# Sidebar untuk input API Key
st.sidebar.header("🔑 API Settings")
api_key = st.sidebar.text_input("Enter your Serper.dev API Key", type="password")
st.sidebar.write("**[Get your API key from Serper.dev](https://serper.dev)**")

# Form input untuk mencari email
st.title("Email Finder")
st.subheader("Find Emails Anywhere on the Internet")

# Pilih opsi pencarian
search_option = st.selectbox("Choose search option", ["Domain-based Search", "Enter Service Name"])

if search_option == "Domain-based Search":
    with st.form("domain_search_form"):
        target_domain = st.text_input("Enter target domain (e.g., cermati.com)", placeholder="e.g., cermati.com")
        location = st.text_input("Enter location (e.g., US, Indonesia)", placeholder="e.g., US", value="Indonesia")
        language = st.text_input("Enter language code (e.g., en, id)", placeholder="e.g., en",value="id")
        
        # Tambahkan slider untuk jumlah hasil pencarian
        num_results = st.slider("Select number of search results", min_value=1, max_value=50, value=20, step=1)
        
        submitted = st.form_submit_button("Search Emails Based on Domain")

elif search_option == "Enter Service Name":
    with st.form("service_search_form"):
        service_name = st.text_input("Enter Service Name (e.g., Jasa SEO Jogja)", placeholder="e.g., Jasa SEO Jogja")
        location = st.text_input("Enter location (e.g., US, Indonesia)", placeholder="e.g., US")
        language = st.text_input("Enter language code (e.g., en, id)", placeholder="e.g., en")
        
        # Tambahkan slider untuk jumlah hasil pencarian
        num_results = st.slider("Select number of search results", min_value=1, max_value=50, value=20, step=1)
        
        submitted = st.form_submit_button("Search Emails Based on Service Name")

# Ketika form disubmit
if submitted:
    if not api_key:
        st.error("🚨 Please enter your API Key!")
        st.stop()

    st.info(f"Fetching search results for query...")

    # Ambil hasil pencarian dari serper.dev API berdasarkan pilihan opsi
    if search_option == "Domain-based Search":
        if not target_domain:
            st.error("❌ Please enter a target domain!")
            st.stop()

        # Dork query untuk domain-based search
        dork_query = f'\"@{target_domain}\" -site:{target_domain}'  # Dork query to exclude the site itself
        urls = get_serp_results(api_key, dork_query, num_results=num_results, location=location, lang=language)

    elif search_option == "Enter Service Name":
        if not service_name:
            st.error("❌ Please enter a service name!")
            st.stop()

        # Membuat query pencarian berdasarkan nama layanan yang dimasukkan oleh pengguna
        search_query = f'"{service_name}" "contact" "email"'
        urls = get_serp_results(api_key, search_query, num_results=num_results, location=location, lang=language)

    if not urls:
        st.error("No websites found!")
    else:
        # Menampilkan hasil pencarian dan scraping email
        emails_found = []
        urls_found = []
        domains_found = []
        
        for url in urls:
            if search_option == "Domain-based Search":
                emails, urls_for_email = extract_emails_from_url(url, target_domain)
            else:
                emails, urls_for_email = extract_emails_from_url(url)

            emails_found.extend(emails)
            urls_found.extend(urls_for_email)
            domains_found.extend([urlparse(u).netloc for u in urls_for_email])


        if emails_found:
            st.write("### Found Emails:")

            # Menghapus duplikat berdasarkan kolom 'Emails'
            data = {'Emails': emails_found, 'URLs': urls_found, 'Domain': domains_found}
            email_df = pd.DataFrame(data)

            # Hapus duplikat berdasarkan kolom 'Emails'
            email_df = email_df.drop_duplicates(subset="Emails", keep="first", inplace=False)

            # Menampilkan hasil email dan URL dalam DataFrame
            st.dataframe(email_df, use_container_width=True)
        else:
            st.write("No emails found in the results.")
