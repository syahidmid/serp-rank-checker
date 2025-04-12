import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="🌍 Google Maps with Reviews", layout="wide")
st.title("🌍 Google Maps with Reviews by Query")

st.sidebar.header("🔑 API Settings")
api_key = st.sidebar.text_input("Enter your Serper.dev API Key", type="password")
st.sidebar.write("🔗 [Get your API Key here](https://serper.dev)")

# Form input untuk query
query = st.text_input("🔍 Enter Search Query (e.g., wisata di Semarang)", placeholder="Tempat wisata di Semarang")
gl = st.selectbox("🌍 Country Code (gl)", ["id", "us", "sg"], index=0)
hl = st.selectbox("🗣️ Language Code (hl)", ["id", "en"], index=0)

if st.button("Search and Fetch Reviews"):
    if not api_key:
        st.error("🚨 Please enter your API Key first!")
        st.stop()
    if not query.strip():
        st.error("🚨 Please enter a search query!")
        st.stop()

    # Step 1: Fetch places based on query using the correct endpoint
    maps_url = "https://google.serper.dev/maps"
    maps_payload = {"q": query, "gl": gl, "hl": hl}
    maps_response = requests.post(maps_url, headers={"X-API-KEY": api_key, "Content-Type": "application/json"}, json=maps_payload)

    if maps_response.status_code != 200:
        st.error(f"❌ Failed to fetch places: {maps_response.status_code}")
        st.stop()

    places_data = maps_response.json()
    places = places_data.get("places", [])
    
    if not places:
        st.warning("No places found for the given query.")
        st.stop()

    # Step 2: Get reviews for each place (based on CID)
    all_data = []
    progress = st.progress(0, text="Fetching reviews...")

    for i, place in enumerate(places, start=1):
        cid = place.get("cid")
        place_name = place.get("title", "Unknown Place")
        address = place.get("address", "No Address Available")
        latitude = place.get("latitude")
        longitude = place.get("longitude")
        rating = place.get("rating")
        rating_count = place.get("ratingCount")
        price_level = place.get("priceLevel")
        types = ", ".join(place.get("types", []))
        website = place.get("website")
        phone_number = place.get("phoneNumber")
        opening_hours = place.get("openingHours", {})
        thumbnail_url = place.get("thumbnailUrl")
        place_id = place.get("placeId")

        # Fetch reviews based on CID
        reviews_url = "https://google.serper.dev/reviews"
        reviews_payload = {"cid": cid, "gl": gl, "hl": hl}
        reviews_response = requests.post(reviews_url, headers={"X-API-KEY": api_key, "Content-Type": "application/json"}, json=reviews_payload)

        if reviews_response.status_code == 200:
            reviews = reviews_response.json().get("reviews", [])[:5]  # Only take top 5 reviews
            reviews_text = "\n\n".join([f"⭐ {r.get('rating')} - {r.get('snippet')}" for r in reviews])
        else:
            reviews_text = "No reviews found."

        all_data.append({
            "CID": cid,
            "Place Name": place_name,
            "Address": address,
            "Latitude": latitude,
            "Longitude": longitude,
            "Rating": rating,
            "Rating Count": rating_count,
            "Price Level": price_level,
            "Types": types,
            "Website": website,
            "Phone Number": phone_number,
            "Opening Hours": str(opening_hours),
            "Thumbnail URL": thumbnail_url,
            "Place ID": place_id,
            "Reviews": reviews_text
        })
        
        time.sleep(1)
        progress.progress(i / len(places), text=f"{i} of {len(places)} places processed")

    if not all_data:
        st.warning("No reviews found.")
    else:
        df = pd.DataFrame(all_data)
        st.success(f"Successfully fetched data for {len(df)} places.")
        st.dataframe(df, use_container_width=True)

        # Download button for CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download All Data (.csv)",
            data=csv,
            file_name="google_maps_with_reviews.csv",
            mime="text/csv"
        )
