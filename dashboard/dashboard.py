# [imports and environment setup remain unchanged]

st.set_page_config(page_title="Tree Logging Dashboard", layout="wide")
st.title("🌳 3T Tree & Seed Tagging Dashboard")

df = fetch_tree_data()

# -------------------------------
# 🖼 BRANDING & LOGO
# -------------------------------
with st.sidebar:
    try:
        st.markdown(
            """
            https://3t.eco
            """,
            unsafe_allow_html=True
        )
    except:
        st.warning("Logo failed to load.")
    st.markdown("### **3T Tree Tagging System**")
    st.markdown("*Built for smart forest monitoring 🌍*")
    st.markdown("---")

# -------------------------------
# 🔍 FILTER SIDEBAR — SPLIT BY TABLE
# -------------------------------
tree_text_columns = {
    "TreeID": "📌 TreeID",
    "GPS": "📍 GPS",
    "COLLECTOR_NAME": "🧑‍🌾 Collector Name",
    "DISTRICT_NAME": "🌍 District Name",
    "FOREST_RESERVE_NAME": "🌲 Forest Reserve Name",
    "SPECIES_NAME": "🧬 Species Name",
    "LOT_CODE": "📦 Lot Code",
    "RegionCode": "🗺 Region Code"
}

seed_text_columns = {
    "SeedID": "🌱 SeedID",
    "ParentTreeID": "🌳 ParentTreeID",
    "LocationFound": "📍 Location Found",
    "Notes": "📝 Notes",
    "LOT_CODE": "📦 Lot Code",
    "SEED_COLLECTOR_NAME": "🧑‍🌾 Seed Collector Name",
    "FOREST_RESERVE": "🌲 Forest Reserve",
    "SPECIES": "🧬 Species",
    "SpeciesCode": "🧬 Species Code"
}

tree_filters = {}
seed_filters = {}

with st.sidebar.expander("🌳 Tree Filters", expanded=True):
    for col, label in tree_text_columns.items():
        if col in df.columns:
            options = df[col].dropna().unique()
            tree_filters[col] = st.selectbox(label, options=[""] + list(options))

with st.sidebar.expander("🌱 Seed Filters", expanded=False):
    for col, label in seed_text_columns.items():
        if col in df.columns:
            options = df[col].dropna().unique()
            seed_filters[col] = st.selectbox(label, options=[""] + list(options))

# Reset button
if st.sidebar.button("🔄 Reset All Filters"):
    st.experimental_rerun()

# -------------------------------
# ✅ APPLY FILTERS
# -------------------------------
filtered_df = df.copy()

for col, selected_value in tree_filters.items():
    if selected_value:
        filtered_df = filtered_df[filtered_df[col] == selected_value]

for col, selected_value in seed_filters.items():
    if selected_value:
        filtered_df = filtered_df[filtered_df[col] == selected_value]

# -------------------------------
# 📋 FILTERED TREE RECORDS
# -------------------------------
st.subheader("📋 Tree Records")
st.dataframe(filtered_df, use_container_width=True)

# -------------------------------
# 📜 LOG VIEWER
# -------------------------------
st.subheader("📜 Sync Logs")
log_choice = st.selectbox("Choose log file", ["kobo_sync_log.txt", "fastapi_log.txt"])
log_content = read_log_file(log_choice)
st.text_area("Log Output", log_content, height=300)

# -------------------------------
# 🗺 GPS MAP VIEW
# -------------------------------
st.subheader("🗺 Tree Locations Map")
map_df = filtered_df.copy()
map_df = map_df[map_df.get("GPS", "").notnull() & map_df.get("GPS", "").str.contains(",")]
if not map_df.empty:
    lat, lon = map_df.iloc[0].get("GPS", "0,0").split(",")
    m = folium.Map(location=[float(lat), float(lon)], zoom_start=12)
    for _, row in map_df.iterrows():
        try:
            lat, lon = row.get("GPS", "0,0").split(",")
            popup = f"{row.get('TreeID', '')} - {row.get('TreeName', '')} ({row.get('SPECIES_NAME', '')})"
            tooltip = row.get("FOREST_RESERVE_NAME", "")
            folium.Marker(location=[float(lat), float(lon)], popup=popup, tooltip=tooltip).add_to(m)
        except:
            continue
    st_folium(m, width=700, height=500)
else:
    st.info("No valid GPS data available to display on map.")

# -------------------------------
# 🔳 QR CODE PREVIEWS
# -------------------------------
st.subheader("🔳 QR Code Previews")
for _, row in filtered_df.iterrows():
    st.markdown(f"*TreeID:* {row.get('TreeID', '')} | *Tree Name:* {row.get('TreeName', '')} | *Species:* {row.get('SPECIES_NAME', '')}")
    img = generate_qr_image(row.get('TreeID', 'UNKNOWN'))
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), width=100)

# -------------------------------
# 📄 PDF EXPORT
# -------------------------------
if st.button("📄 Export Tree Tags to PDF"):
    export_tree_tags_to_pdf(filtered_df)
    st.success("Exported to tree_tags.pdf")

# -------------------------------
# 🧾 FOOTER
# -------------------------------
st.markdown("---")
st.markdown("<small><center>Developed by Nannz for 3T</center></small>", unsafe_allow_html=True)
