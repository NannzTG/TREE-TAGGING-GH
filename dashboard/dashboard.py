# ... [imports and environment setup remain unchanged]

st.set_page_config(page_title="Tree Logging Dashboard", layout="wide")
st.title("🌳 Tree Logging Dashboard")

df = fetch_tree_data()

# -------------------------------
# 🖼 BRANDING & LOGO
# -------------------------------
with st.sidebar:
    try:
        st.markdown(
            """
            <a href="https://3t.eco" target="_blank">
                <img src="logo.png
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
st.dataframe(filtered_df, use
