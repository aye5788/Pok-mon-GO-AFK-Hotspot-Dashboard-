import streamlit as st
import pandas as pd
import folium
from folium import Popup
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- CONFIG ---
st.set_page_config(page_title="Pokémon GO AFK Hotspots", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("pogo_hotspot_analysis_complete.csv")
    df = df.rename(columns={
        "Place": "Town",
        "State": "State",
        "visible_stops": "Visible Stops",
        "estimated_gyms": "Estimated Gyms",
        "stationary_cluster_score": "Stationary Cluster Score",
        "cluster_grade": "Cluster Grade",
        "lat": "Lat",
        "lon": "Lon"
    })
    return df

df = load_data()

# --- HEADER ---
st.title("📍 Pokémon GO AFK Hotspot Explorer")
st.markdown("Find the best towns in NH/VT to sit and spin multiple PokéStops while parked!")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🎯 Filter Hotspots")

visible_min = st.sidebar.slider("Minimum Visible Stops", 0, int(df["Visible Stops"].max()), 5)
score_min = st.sidebar.slider("Minimum Cluster Score", 0.0, float(df["Stationary Cluster Score"].max()), 2.0)

# --- ZIP FOCUS ---
zip_input = st.sidebar.text_input("Focus Map on ZIP Code (optional)")
geolocator = Nominatim(user_agent="pogo-hotspot-locator")
map_center = [44.0, -72.7]  # default = VT/NH center

if zip_input:
    try:
        location = geolocator.geocode({"postalcode": zip_input, "country": "United States"})
        if location:
            map_center = [location.latitude, location.longitude]
        else:
            st.sidebar.warning("❌ ZIP code not found.")
    except:
        st.sidebar.warning("❌ Geocoding failed.")

# --- FILTER DATA ---
filtered_df = df[
    (df["Visible Stops"] >= visible_min) &
    (df["Stationary Cluster Score"] >= score_min)
]

# --- DISPLAY TABLE ---
st.subheader("📊 Top AFK-Friendly Towns")
st.dataframe(
    filtered_df[["Town", "State", "Visible Stops", "Estimated Gyms", "Stationary Cluster Score", "Cluster Grade"]],
    use_container_width=True
)

# --- MAP ---
st.subheader("🗺️ Map of Top AFK Towns")
m = folium.Map(location=map_center, zoom_start=8)

for _, row in filtered_df.iterrows():
    popup_text = f"""
    <b>{row['Town']}</b><br>
    Stops: {row['Visible Stops']}<br>
    Gyms: {row['Estimated Gyms']}<br>
    Cluster Score: {row['Stationary Cluster Score']:.2f}<br>
    Grade: {row['Cluster Grade']}
    """
    folium.CircleMarker(
        location=[row["Lat"], row["Lon"]],
        radius=8,
        color="purple",
        fill=True,
        fill_opacity=0.7,
        popup=Popup(popup_text, max_width=250)
    ).add_to(m)

st_folium(m, width=1000, height=600)

