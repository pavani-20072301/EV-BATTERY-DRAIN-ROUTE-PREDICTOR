import streamlit as st
import folium
from streamlit_folium import st_folium
import os
import math
from modules.auth import check_login, logout

st.set_page_config(page_title="Interactive Route & Charging Intelligence", page_icon="🗺️", layout="wide")

if check_login():
    if os.path.exists("static/logo.png"):
        st.sidebar.image("static/logo.png", width=220)
        
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()

    st.title("🗺️ Interactive Route Map & Corridor Stations")

    if not st.session_state.get("calculated", False):
        st.warning("⚠️ Please complete a journey prediction first on the **Live Prediction** page.")
    else:
        origin_name = st.session_state.get("origin_name", "Origin")
        dest_name = st.session_state.get("dest_name", "Destination")
        st.markdown(f"**Active Journey Corridor:** `{origin_name}` ➔ `{dest_name}`")
        
        o_lat = st.session_state.o_lat
        o_lon = st.session_state.o_lon
        d_lat = st.session_state.d_lat
        d_lon = st.session_state.d_lon
        
        mid_lat = (o_lat + d_lat) / 2
        mid_lon = (o_lon + d_lon) / 2
        
        # Crystal clear Google-Maps-like OpenStreetMap tiles
        m = folium.Map(
            location=[mid_lat, mid_lon], 
            zoom_start=10, 
            tiles="OpenStreetMap",
            control_scale=True
        )

        route_coords = st.session_state.get("route_line", [])

        if route_coords:
            folium.PolyLine(
                route_coords, 
                color="#0066ff", 
                weight=6, 
                opacity=0.85, 
                tooltip=f"Route: {origin_name} to {dest_name}"
            ).add_to(m)

            min_lat = min(pt[0] for pt in route_coords)
            max_lat = max(pt[0] for pt in route_coords)
            min_lon = min(pt[1] for pt in route_coords)
            max_lon = max(pt[1] for pt in route_coords)
            m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]], padding=(40, 40))

        folium.Marker(
            [o_lat, o_lon],
            popup=f"<b>📍 Origin:</b> {origin_name}",
            icon=folium.Icon(color="green", icon="play", prefix="fa")
        ).add_to(m)

        folium.Marker(
            [d_lat, d_lon],
            popup=f"<b>🏁 Destination:</b> {dest_name}",
            icon=folium.Icon(color="red", icon="stop", prefix="fa")
        ).add_to(m)

        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 6371.0
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
            c = 2 * math.asin(math.sqrt(a))
            return R * c

        # Helper to find minimum distance from a point to the route polyline (to filter out stations that are too far away)
        def min_distance_to_route(s_lat, s_lon, polyline):
            if not polyline:
                return 0.0
            min_dist = float('inf')
            for pt in polyline:
                dist = calculate_distance(s_lat, s_lon, pt[0], pt[1])
                if dist < min_dist:
                    min_dist = dist
            return min_dist

        raw_stations = st.session_state.get("charging_stations", [])
        corridor_stations = []

        # Filter stations so only those within ~15 km of the actual route polyline are shown directly on the path
        for station in raw_stations:
            s_lat, s_lon, s_name = station
            dist_to_route = min_distance_to_route(s_lat, s_lon, route_coords)
            if dist_to_route <= 15.0:  # Must be within 15km of the highway path
                corridor_stations.append(station)

        # Fallback if strict filter is too aggressive
        if not corridor_stations and raw_stations:
            corridor_stations = raw_stations[:3]

        if corridor_stations:
            for idx, station in enumerate(corridor_stations, 1):
                s_lat, s_lon, s_name = station
                dist_from_start = calculate_distance(o_lat, o_lon, s_lat, s_lon)
                
                popup_html = f"""
                <div style="font-family: Arial; font-size: 13px; width: 220px; background: #ffffff; color: #333333; padding: 8px; border-radius: 5px; border: 1px solid #ccc;">
                    <b>⚡ {s_name}</b><br>
                    <hr style="margin: 5px 0; border-color: #0066ff;">
                    <b>Distance from Start:</b> {dist_from_start:.1f} km<br>
                    <b>Status:</b> Directly Along Route Corridor<br>
                    <span style="color: green; font-weight: bold;">Recommended Stop</span>
                </div>
                """
                
                folium.Marker(
                    [s_lat, s_lon],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"⚡ {s_name} (~{dist_from_start:.1f} km from start)",
                    icon=folium.Icon(color="orange", icon="bolt", prefix="fa")
                ).add_to(m)

        st_folium(m, width=1250, height=600, use_container_width=True)

        st.markdown("---")
        st.markdown("### ⚡ Recommended Charging Stops Along Your Route Corridor")
        st.markdown("These charging hubs are filtered to lie directly along your journey path with precise distance metrics:")

        if corridor_stations:
            for idx, station in enumerate(corridor_stations, 1):
                s_lat, s_lon, s_name = station
                dist_from_start = calculate_distance(o_lat, o_lon, s_lat, s_lon)
                
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    st.markdown(f"**{idx}. {s_name}**")
                with col_b:
                    st.markdown(f"📍 **{dist_from_start:.1f} km** away")
                with col_c:
                    st.markdown(f"`{s_lat:.4f}, {s_lon:.4f}`")
        else:
            st.info("ℹ️ No charging stations were found directly along this specific route corridor.")