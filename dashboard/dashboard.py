import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
import folium
from streamlit_folium import st_folium
import qrcode
from io import BytesIO
from PIL import Image
from fpdf import FPDF

# -------------------------------
# 🌳 TREE LOGGING DASHBOARD
# -------------------------------
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Connect to MySQL
def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# Fetch tree data
def fetch_tree_data():
    conn = get_connection()
    query = "SELECT * FROM trees"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Read log file
def read_log_file(log_path):
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Log file not found."

# Generate QR image
def generate_qr_image(tree_id):
    url = f"https://tree-tagging-gh.streamlit.app/?TreeID={tree_id}"
    qr = qrcode.make(url)
    return qr

# Export PDF with table layout and QR codes
def export_tree_tags_to_pdf(dataframe):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Tree & Seed Tagging Summary", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, "Tree ID", border=1)
    pdf.cell(50, 10, "Tree Name", border=1)
    pdf.cell(60, 10, "Species", border=1)
    pdf.cell(40, 10, "QR Code", border=1)
    pdf.ln()

    pdf.set_font("Arial", size=10)

    for _, row in dataframe.iterrows():
        tree_id = row.get('TreeID', '')
        tree_name = row.get('TreeName', '')
        species = row.get('SPECIES_NAME', '')

        pdf.cell(40, 30, str(tree_id), border=1)
        pdf.cell(50, 30, str(tree_name), border=1)
        pdf.cell(60, 30, str(species), border=1)

        qr_img = generate_qr_image(tree_id)
        qr_buf = BytesIO()
        qr_img.save(qr_buf, format="PNG")
        qr_buf.seek(0)

        with open("temp_qr.png", "wb") as f:
            f.write(qr_buf.read())
        pdf.image("temp_qr.png", x=pdf.get_x(), y=pdf.get_y(), w=20, h=20)
        pdf.cell(40, 30, "", border=1)
        pdf.ln(30)

    pdf_buf = BytesIO()
    pdf.output(pdf_buf)
    pdf_buf.seek(0)
    return pdf_buf

# Streamlit UI
st.set_page_config(page_title="Tree Logging Dashboard", layout="wide")
st.title("🌳 3T Tree & Seed Tagging Dashboard")

# Load data
try:
    df = fetch_tree_data()
    st.success(f"✅ Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    if df.empty:
        st.warning("⚠️ No data found in the database. Please check your sync or table.")
except Exception as e:
    st.error("❌ Could not connect to the database or load data.")
    st.exception(e)
    df = pd.DataFrame()

# Sidebar branding
with st.sidebar:
    st.markdown("https://3t.eco", unsafe_allow_html=True)
    st.markdown("### **3T Tree Tagging System**")
    st.markdown("*Built for smart forest monitoring 🌍*")
    st.markdown("---")

# Sidebar filters
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

tree_filters = {}
with st.sidebar.expander("🌳 Tree Filters", expanded=True):
    for col, label in tree_text_columns.items():
        if col in df.columns:
            options = df[col].dropna().unique()
            tree_filters[col] = st.selectbox(label, options=[""] + list(options), key=f"tree_{col}")

if st.sidebar.button("🔄 Reset All Filters"):
    st.experimental_rerun()

# Apply filters
filtered_df = df.copy()
for col, selected_value in tree_filters.items():
    if selected_value:
        filtered_df = filtered_df[filtered_df[col] == selected_value]

# Query param filter
query_params = st.query_params
tree_id_filter = query_params.get("TreeID")
if tree_id_filter and tree_id_filter in filtered_df["TreeID"].values:
    filtered_df = filtered_df[filtered_df["TreeID"] == tree_id_filter]

# Display data
st.subheader("📋 Tree Records")
st.dataframe(filtered_df, use_container_width=True)

# Log viewer
st.subheader("📜 Sync Logs")
log_choice = st.selectbox("Choose log file", ["kobo_sync_log.txt", "fastapi_log.txt"])
log_content = read_log_file(log_choice)
st.text_area("Log Output", log_content, height=300)

# Map display
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

# QR previews
st.subheader("🔳 QR Code Previews")
for _, row in filtered_df.iterrows():
    st.markdown(f"*TreeID:* {row.get('TreeID', '')} | *Tree Name:* {row.get('TreeName', '')} | *Species:* {row.get('SPECIES_NAME', '')}")
    img = generate_qr_image(row.get('TreeID', 'UNKNOWN'))
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), width=100)

# PDF export button
if not filtered_df.empty:
    pdf_data = export_tree_tags_to_pdf(filtered_df)
    st.download_button(
        label="📄 Download Tree Tags PDF",
        data=pdf_data,
        file_name="tree_tags.pdf",
        mime="application/pdf"
    )

st.markdown("---")
st.markdown("<small><center>Developed by Nannz for 3T</center></small>", unsafe_allow_html=True)
