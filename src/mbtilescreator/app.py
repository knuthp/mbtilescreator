import streamlit as st
import osmium
import tempfile
import subprocess
import os
import json

# Define tags for filtering
FEATURE_TAGS = {
    "Roads": "highway",
    "Buildings": "building",
    "Railways": "railway",
    "Water": "waterway",
    "Landuse": "landuse"
}

class OSMFilterHandler(osmium.SimpleHandler):
    def __init__(self, selected_tags):
        super().__init__()
        self.selected_tags = selected_tags
        self.features = []

    def way(self, w):
        try:
            for tag in self.selected_tags:
                if tag in w.tags:
                    self.features.append({
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [(n.lon, n.lat) for n in w.nodes]
                        },
                        "properties": dict(w.tags)
                    })
                    break
        except osmium.InvalidLocationError:
            print(f"Warning: Node {w.id} has an invalid location. Skipping.")

def save_geojson(features, path):
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    with open(path, "w") as f:
        json.dump(geojson, f)

st.title("🗺️ OSM to MBTiles Converter")

uploaded_file = st.file_uploader("Upload .osm.pbf file", type=["pbf"])
selected_features = st.multiselect("Select features to include", list(FEATURE_TAGS.keys()))

if uploaded_file and selected_features:
    with tempfile.TemporaryDirectory() as tmpdir:
        osm_path = os.path.join(tmpdir, "input.osm.pbf")
        geojson_path = os.path.join(tmpdir, "filtered.geojson")
        mbtiles_path = os.path.join(tmpdir, "output.mbtiles")

        with open(osm_path, "wb") as f:
            f.write(uploaded_file.read())

        st.info("Filtering OSM data...")
        selected_tags = [FEATURE_TAGS[f] for f in selected_features]
        handler = OSMFilterHandler(selected_tags)
        handler.apply_file(osm_path, locations=True)
        save_geojson(handler.features, geojson_path)

        st.info("Generating MBTiles with tippecanoe ...")
        result = subprocess.run([
            "tippecanoe",
            "-o", mbtiles_path,
            geojson_path
        ], capture_output=True)

        if result.returncode == 0:
            st.success("MBTiles generated successfully!")
            with open(mbtiles_path, "rb") as f:
                st.download_button("Download MBTiles", f, file_name="map.mbtiles")
        else:
            st.error("Error generating MBTiles")
            st.text(result.stderr.decode())