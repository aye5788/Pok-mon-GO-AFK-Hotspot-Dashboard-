import streamlit as st
import pandas as pd
import folium
from folium import Popup
from streamlit_folium import st_folium

# --- CONFIG ---
st.set_page_config(page_title="Pokémon GO AFK Hotspots", layout="wide")

# --- LOAD & CLEAN DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("pogo_hotspot_analysis_complete.csv")

    # Rename for clarity
    df.rename(columns={
        "Place": "Town",
        "State": "State",
        "visible_stops": "Visible Stops",
        "estimated_gyms": "Estimated Gyms",
        "stationary_cluster_score": "Stationary Cluster Score",
        "cluster_grade": "Cluster Grade",
        "lat": "Latitude",
        "lon": "Longitude"
    }, inplace=True)

    return df

df = load_data()

# --- HEADER ---
st.title("📍 Pokémon GO AFK Hotspot Explorer")
st.markdown("Find the best towns in NH/VT to sit and spin multiple PokéStops while parked!")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🎛️ Filter Hotspots")

visible_min = st.sidebar.slider("Minimum Visible Stops", 0, int(df["Visible Stops"].max()), 5)
score_min = st.sidebar.slider("Minimum Cluster Score", 0.0, float(df["Stationary Cluster Score"].max()), 2.0)
grade_filter = st.sidebar.multiselect("Cluster Grade", sorted(df["Cluster Grade"].unique()), default=["A", "B"])

# --- FILTERING ---
filtered_df = df[
    (df["Visible Stops"] >= visible_min) &
    (df["Stationary Cluster Score"] >= score_min) &
    (df["Cluster Grade"].isin(grade_filter))
].sort_values(by="Stationary Cluster Score", ascending=False)

# --- TABLE OUTPUT ---
st.subheader("📊 Top AFK-Friendly Towns")
st.dataframe(
    filtered_df[["Town", "State", "Visible Stops", "Estimated Gyms", "Stationary Cluster Score", "Cluster Grade"]],
    use_container_width=True
)

# --- MAP OUTPUT ---
st.subheader("🗺️ Map of Top AFK Towns")
if not filtered_df.empty:
    m = folium.Map(location=[filtered_df["Latitude"].mean(), filtered_df["Longitude"].mean()], zoom_start=7)

    for _, row in filtered_df.iterrows():
        popup_html = f"""
        <b>{row['Town']}, {row['State']}</b><br>
        Stops: {row['Visible Stops']}<br>
        Gyms: {row['Estimated Gyms']}<br>
        Cluster Score: {row['Stationary Cluster Score']:.2f}<br>
        Grade: {row['Cluster Grade']}
        """
        folium.CircleMarker(
            location=(row["Latitude"], row["Longitude"]),
            radius=8,
            color="#6c00ff",
            fill=True,
            fill_opacity=0.7,
            popup=Popup(popup_html, max_width=300)
        ).add_to(m)

    st_folium(m, width=900, height=500)
else:
    st.warning("No towns match the selected filters.")

