import streamlit as st
import gpxpy
import pandas as pd
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="GPX Höhenmeter Analyse", layout="centered")
st.title("🚴‍♂️ GPX-Analyse: Gute vs. Böse Höhenmeter")

uploaded_file = st.file_uploader("Lade deine GPX-Datei hoch", type=["gpx"])

if uploaded_file:
    try:
        gpx = gpxpy.parse(uploaded_file)

        # === 1. Punkte extrahieren ===
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.elevation is not None:
                        points.append({
                            'latitude': point.latitude,
                            'longitude': point.longitude,
                            'elevation': point.elevation,
                            'time': point.time
                        })

        if len(points) < 2:
            st.error("Die GPX-Datei enthält zu wenige Punkte mit Höhenangabe.")
            st.stop()

        df = pd.DataFrame(points)

        # === 2. Berechnungen: Distanz, Steigung etc. ===
        distances, elevation_diffs, gradients = [], [], []
        for i in range(1, len(df)):
            coord1 = (df.loc[i-1, 'latitude'], df.loc[i-1, 'longitude'])
            coord2 = (df.loc[i, 'latitude'], df.loc[i, 'longitude'])
            distance = geodesic(coord1, coord2).meters
            elevation_diff = df.loc[i, 'elevation'] - df.loc[i-1, 'elevation']
            gradient = elevation_diff / distance if distance > 0 else 0
            distances.append(distance)
            elevation_diffs.append(elevation_diff)
            gradients.append(gradient)

        df = df.iloc[1:].copy().reset_index(drop=True)
        df['distance'] = distances
        df['elevation_diff'] = elevation_diffs
        df['gradient'] = gradients

        # === 3. Klassifikation mit 500 m Rückblickfenster ===
        def classify_gradient_advanced(index, df, window_m=500):
            if df.loc[index, 'gradient'] <= 0:
                return 'neutral'
            total_distance = 0
            grad_sum = 0
            grad_count = 0
            i = index - 1
            while i >= 0 and total_distance < window_m:
                total_distance += df.loc[i, 'distance']
                grad_sum += df.loc[i, 'gradient']
                grad_count += 1
                i -= 1
            if grad_count == 0:
                return 'neutral'
            avg_prev_gradient = grad_sum / grad_count
            if avg_prev_gradient < -0.01 and df.loc[index, 'gradient'] < 0.08:
                return 'gut'
            elif df.loc[index, 'gradient'] >= 0.08:
                return 'böse'
            else:
                return 'neutral'

        df['classification'] = [
            classify_gradient_advanced(idx, df) for idx in df.index
        ]

        # === 4. Vorschau + Höhenprofil ===
        st.success("Analyse abgeschlossen ✅")
        st.dataframe(df[['elevation', 'gradient', 'elevation_diff', 'classification']].head(50))

        colors = {'gut': 'green', 'böse': 'red', 'neutral': 'gray'}
        fig, ax = plt.subplots(figsize=(10, 4))
        for label in df['classification'].unique():
            subset = df[df['classification'] == label]
            ax.plot(subset.index, subset['elevation'], '.', color=colors[label], label=label)
        ax.set_title("Höhenprofil mit Klassifikation")
        ax.set_xlabel("Punkt")
        ax.set_ylabel("Höhe (m)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        # === 5. Zusammenfassung ===
        total_distance = df['distance'].sum()
        total_elevation_gain = df[df['elevation_diff'] > 0]['elevation_diff'].sum()
        good_elevation = df[(df['classification'] == 'gut') & (df['elevation_diff'] > 0)]['elevation_diff'].sum()
        bad_elevation = df[(df['classification'] == 'böse') & (df['elevation_diff'] > 0)]['elevation_diff'].sum()
        neutral_elevation = total_elevation_gain - (good_elevation + bad_elevation)

        st.markdown("## 📊 Zusammenfassung")
        st.markdown(f"- **Gesamtstrecke:** {total_distance/1000:.2f} km")
        st.markdown(f"- **Gesamte positive Höhenmeter:** {total_elevation_gain:.0f} m")
        st.markdown(f"- **Gute Höhenmeter:** {good_elevation:.0f} m ✅")
        st.markdown(f"- **Böse Höhenmeter:** {bad_elevation:.0f} m 😤")
        st.markdown(f"- **Neutrale Höhenmeter:** {neutral_elevation:.0f} m 😐")

        # === 6. Karte ===
        st.markdown("## 🗺️ Streckenverlauf")

        center = [df['latitude'].mean(), df['longitude'].mean()]
        m = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")

        # Strecken-Segmente farbig nach Klassifikation
        for i in range(1, len(df)):
            start = (df.loc[i-1, 'latitude'], df.loc[i-1, 'longitude'])
            end = (df.loc[i, 'latitude'], df.loc[i, 'longitude'])
            label = df.loc[i, 'classification']
            color = colors.get(label, 'gray')
            folium.PolyLine(locations=[start, end], color=color, weight=4).add_to(m)

        # Start- und Zielpunkt
        folium.Marker(location=[df.loc[0, 'latitude'], df.loc[0, 'longitude']],
                      popup="Start", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(location=[df.loc[len(df)-1, 'latitude'], df.loc[len(df)-1, 'longitude']],
                      popup="Ziel", icon=folium.Icon(color="red")).add_to(m)

        st_folium(m, width=700, height=500)

    except Exception as e:
        st.error(f"Fehler beim Verarbeiten der Datei: {e}")
