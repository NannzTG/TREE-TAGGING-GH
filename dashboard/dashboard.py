import streamlit as st
import pandas as pd
import os
import mysql.connector
from datetime import datetime
import folium
from streamlit_folium import st_folium
import qrcode
from io import BytesIO
from PIL import Image
from fpdf import FPDF

# -------------------------------
# 🌳 3T TREE TAGGING DASHBOARD
# -------------------------------

# Hybrid environment loading
try:
    DB_HOST = st.secrets["DB_HOST"]
    DB_PORT = int(st.secrets.get("DB_PORT", 3306))
    DB_USER = st.secrets["DB_USER"]
    DB_PASSWORD = st.secrets["DB_PASSWORD"]
    DB_NAME = st.secrets["DB_NAME"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT") or 3306)
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def fetch_tree_data():
    conn = get_connection()
    query = "SELECT * FROM trees"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def read_log_file(log_path):
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Log file not found."

def generate_qr_image(tree_id):
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(tree_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def export_tree_tags_to_pdf(dataframe):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    for _, row in dataframe.iterrows():
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Tree ID: {row['TreeID']}", ln=True)
        pdf.cell(200, 10, txt=f"Tree Name: {row.get('TreeName', '')}", ln=True)
        pdf.cell(200, 10, txt=f"Species: {row.get('Species', '')}", ln=True)
        qr_img = generate_qr_image(row['TreeID'])
        qr_buf = BytesIO()
        qr_img.save(qr_buf, format="PNG")
        qr_buf.seek(0)
        qr_path = f"temp_qr_{row['TreeID']}.png"
        with open(qr_path, "wb") as f:
            f.write(qr_buf.read())
        pdf.image(qr_path, x=10, y=50, w=40, h=40)
    pdf.output("tree_tags.pdf")

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
map_df = map_df[map_df["GPS"].notnull() & map_df["GPS"].str.contains(",")]
if not map_df.empty:
    lat, lon = map_df.iloc[0]["GPS"].split(",")
    m = folium.Map(location=[float(lat), float(lon)], zoom_start=12)
    for _, row in map_df.iterrows():
        try:
            lat, lon = row["GPS"].split(",")
            folium.Marker(
                location=[float(lat), float(lon)],
                popup=f"{row['TreeID']} - {row.get('TreeName', '')} ({row.get('Species', '')})",
                tooltip=row.get("FOREST_RESERVE_NAME", "")
            ).add_to(m)
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
    st.markdown(f"*TreeID:* {row['TreeID']} | *Tree Name:* {row.get('TreeName', '')} | *Species:* {row.get('Species', '')}")
    img = generate_qr_image(row['TreeID'])
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), width=100)

# -------------------------------
# 📄 PDF EXPORT
# -------------------------------
if st.button("📄 Export Tree Tags to PDF"):
    export_tree_tags_to_pdf(filtered_df)
    st.success("Exported to tree_tags.pdf")
