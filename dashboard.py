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
# 🌳 TREE LOGGING DASHBOARD
# -------------------------------

# Hybrid environment loading: Streamlit secrets first, fallback to .env
try:
    DB_HOST = st.secrets["DB_HOST"]
    DB_PORT = int(st.secrets["DB_PORT"])
    DB_USER = st.secrets["DB_USER"]
    DB_PASSWORD = st.secrets["DB_PASSWORD"]
    DB_NAME = st.secrets["DB_NAME"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT"))
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
        pdf.cell(200, 10, txt=f"Tree Name: {row['TreeName']}", ln=True)
        pdf.cell(200, 10, txt=f"Species: {row['Species']}", ln=True)
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

st.sidebar.header("🔍 Filter Tree Records")
forest_filter = st.sidebar.multiselect("Forest Name", options=df["ForestName"].unique())
species_filter = st.sidebar.multiselect("Species", options=df["Species"].unique())
date_filter = st.sidebar.date_input("Date Planted (after)", value=None)

filtered_df = df.copy()
if forest_filter:
    filtered_df = filtered_df[filtered_df["ForestName"].isin(forest_filter)]
if species_filter:
    filtered_df = filtered_df[filtered_df["Species"].isin(species_filter)]
if date_filter:
    filtered_df = filtered_df[pd.to_datetime(filtered_df["DatePlanted"]) >= pd.to_datetime(date_filter)]

st.subheader("📋 Tree Records")
st.dataframe(filtered_df, use_container_width=True)

st.subheader("📜 Sync Logs")
log_choice = st.selectbox("Choose log file", ["kobo_sync_log.txt", "fastapi_log.txt"])
log_content = read_log_file(log_choice)
st.text_area("Log Output", log_content, height=300)

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
                popup=f"{row['TreeID']} - {row['TreeName']} ({row['Species']})",
                tooltip=row["ForestName"]
            ).add_to(m)
        except:
            continue
    st_folium(m, width=700, height=500)
else:
    st.info("No valid GPS data available to display on map.")

st.subheader("🔳 QR Code Previews")
for _, row in filtered_df.iterrows():
    st.markdown(f"*TreeID:* {row['TreeID']} | *Tree Name:* {row['TreeName']} | *Species:* {row['Species']}")
    img = generate_qr_image(row['TreeID'])
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), width=100)

if st.button("📄 Export Tree Tags to PDF"):
    export_tree_tags_to_pdf(filtered_df)
    st.success("Exported to tree_tags.pdf")
