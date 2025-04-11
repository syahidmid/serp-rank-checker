import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="📝 Bulk Google Reviews by CID", layout="wide")
st.title("📝 Bulk Google Reviews by CID")

st.sidebar.header("🔑 API Settings")
api_key = st.sidebar.text_input("Masukkan API Key Serper.dev kamu", type="password")
st.sidebar.write("🔗 [Dapatkan API Key di sini](https://serper.dev)")

# Form input
cids_text = st.text_area("🆔 Masukkan Daftar CID (1 per baris)", placeholder="3075219648616366458\n1234567890123456789")
gl = st.selectbox("🌍 Country Code (gl)", ["id", "us", "sg"], index=0)
hl = st.selectbox("🗣️ Language Code (hl)", ["id", "en"], index=0)

if st.button("Ambil Semua Review"):
    if not api_key:
        st.error("🚨 Masukkan API Key terlebih dahulu!")
        st.stop()
    if not cids_text.strip():
        st.error("🚨 Masukkan minimal 1 CID!")
        st.stop()

    cid_list = [cid.strip() for cid in cids_text.splitlines() if cid.strip()]
    all_reviews = []

    progress = st.progress(0, text="Fetching reviews...")

    for i, cid in enumerate(cid_list, start=1):
        url = "https://google.serper.dev/reviews"
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "cid": cid,
            "gl": gl,
            "hl": hl
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            reviews = response.json().get("reviews", [])[:5]
            for r in reviews:
                user = r.get("user", {})
                response_owner = r.get("response", {})
                media = r.get("media", [])

                all_reviews.append({
                    "CID": cid,
                    "User Name": user.get("name"),
                    "User Link": user.get("link"),
                    "User Reviews": user.get("reviews"),
                    "User Photos": user.get("photos"),
                    "User Thumbnail": user.get("thumbnail"),
                    "Review Snippet": r.get("snippet"),
                    "Rating": r.get("rating"),
                    "Date": r.get("date"),
                    "ISO Date": r.get("isoDate"),
                    "Owner Response": response_owner.get("snippet"),
                    "Owner Response Date": response_owner.get("date"),
                    "Media Count": len(media),
                    "Review ID": r.get("id")
                })
        else:
            st.warning(f"❌ Gagal mengambil review untuk CID {cid}: {response.status_code}")
        
        # Optional: beri jeda agar tidak terlalu cepat (rate limit friendly)
        time.sleep(1)

        progress.progress(i / len(cid_list), text=f"{i} dari {len(cid_list)} CID diproses")

    if not all_reviews:
        st.warning("Tidak ada review ditemukan dari semua CID.")
    else:
        df = pd.DataFrame(all_reviews)
        st.success(f"Berhasil mengambil {len(df)} review dari {len(cid_list)} CID.")
        st.dataframe(df, use_container_width=True)

        # Tombol Download CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Semua Review (.csv)",
            data=csv,
            file_name="bulk_google_reviews.csv",
            mime="text/csv"
        )
