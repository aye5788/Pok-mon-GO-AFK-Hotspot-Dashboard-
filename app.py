import streamlit as st
import pandas as pd
import folium
from folium import Popup
from streamlit_folium import st_folium

# --- CONFIG ---
st.set_page_config(page_title="Pokémon GO AFK Hotspots", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    return pd.read_csv("pogo_hotspot_analysis_complete.csv")

df = load_data()

# --- HEADER ---
st.title("📍 Pokémon GO AFK Hotspot Explorer")
st.markdown("Find the best towns in NH/VT to sit and spin multiple PokéStops while parked!")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filters")

min_stops = st.sidebar.slider("Minimum Visible Stops", 0, int(df['visible_stops'].max()), 5)
min_score = st.sidebar.slider("Minimum Cluster Score", 0.0, float(df['stationary_cluster_score'].max()), 2.0)
grades = st.sidebar.multiselect("Cluster Grade", options=['A', 'B', 'C', 'D'], default=['A', 'B'])

filtered = df[
    (df['visible_stops'] >= min_stops) &
    (df['stationary_cluster_score'] >= min_score) &
    (df['cluster_grade'].isin(grades))
].copy()

# --- MAIN TABLE ---
st.subheader("📊 Top AFK-Friendly Towns")
st.dataframe(
    filtered[['Place', 'State', 'visible_stops', 'estimated_gyms', 'stationary_cluster_score', 'cluster_grade']]
    .sort_values(by='stationary_cluster_score', ascending=False)
    .reset_index(drop=True),
    use_container_width=True
)

# --- MAP ---
st.subheader("🗺️ Map of Top AFK Towns")

m = folium.Map(location=[43.9, -72.5], zoom_start=7, tiles='cartodbpositron')

for _, row in filtered.iterrows():
    popup_html = (
        f"<b>{row['Place']}</b><br>"
        f"Stops: {row['visible_stops']}<br>"
        f"Gyms: {row['estimated_gyms']}<br>"
        f"Cluster Score: {round(row['stationary_cluster_score'], 2)}<br>"
        f"Grade: {row['cluster_grade']}"
    )
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=row['visible_stops'] * 0.6,
        color='purple' if row['estimated_gyms'] > 0 else 'blue',
        fill=True,
        fill_opacity=0.7,
        popup=Popup(popup_html, max_width=250)
    ).add_to(m)

st_folium(m, width=900, height=600)

# --- FOOTER ---
st.markdown("---")
st.caption("🚗 AFK cluster logic based on Overpass + OSM POIs + Niantic S2 approximations.")
