import streamlit as st
import requests
import pandas as pd
import json

st.set_page_config(page_title="🗺️ Google Maps API", layout="wide")

st.title("🗺️ Google Maps")
st.write("Find places based on a query and display the results in a table.")

api_key = st.sidebar.text_input("Masukkan API Key Serper.dev kamu", type="password")
st.sidebar.write("🔗 [Dapatkan API Key di sini](https://serper.dev)")

query = st.text_input("🔍 Cari Tempat", placeholder="Contoh: wisata di Solo, cafe di Bandung")

if st.button("Cari Sekarang"):
    if not api_key:
        st.error("🚨 Enter the API Key first!")
        st.stop()
    if not query:
        st.error("🚨 Enter a search query!")
        st.stop()

    url = "https://google.serper.dev/maps"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    payload = {"q": query}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        st.error(f"Gagal mendapatkan hasil. Kode: {response.status_code}")
        st.stop()

    data = response.json()
    places = data.get("places", [])
    center_ll = data.get("ll", "Tidak tersedia")

    if not places:
        st.warning("Tidak ada tempat ditemukan.")
    else:
        st.success(f"{len(places)} tempat ditemukan. Lokasi peta tengah: `{center_ll}`")

        # Ekstraksi data jadi list of dicts
        rows = []
        for p in places:
            rows.append({
                "Position": p.get("position"),
                "Name": p.get("title"),
                "Address": p.get("address"),
                "Latitude": p.get("latitude"),
                "Longitude": p.get("longitude"),
                "Rating": p.get("rating"),
                "Rating Count": p.get("ratingCount"),
                "Type": p.get("type"),
                "All Types": ", ".join(p.get("types", [])),
                "Opening Hours": json.dumps(p.get("openingHours", {}), ensure_ascii=False),
                "Thumbnail": p.get("thumbnailUrl"),
                "CID": p.get("cid"),
                "FID": p.get("fid"),
                "Place ID": p.get("placeId")
            })

        df = pd.DataFrame(rows)

        st.dataframe(df, use_container_width=True)

        # Tombol download CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="maps_places.csv",
            mime="text/csv"
        )
