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
        pdf.cell(200, 10, txt=f"Tree ID: {row.get('TreeID', '')}", ln=True)
        pdf.cell(200, 10, txt=f"Tree Name: {row.get('TreeName', '')}", ln=True)
        pdf.cell(200, 10, txt=f"Species: {row.get('SPECIES_NAME', '')}", ln=True)
        qr_img = generate_qr_image(row.get('TreeID', 'UNKNOWN'))
        qr_buf = BytesIO()
        qr_img.save(qr_buf, format="PNG")
        qr_buf.seek(0)
        qr_path = f"temp_qr_{row.get('TreeID', '')}.png"
        with open(qr_path, "wb") as f:
            f.write(qr_buf.read())
        pdf.image(qr_path, x=10, y=50, w=40, h=40)
    pdf.output("tree_tags.pdf")

st.set_page_config(page_title="Tree Logging Dashboard", layout="wide")
st.title("🌳 3T Tree & Seed Tagging Dashboard")

df = fetch_tree_data()

# -------------------------------
# 🖼 BRANDING & LOGO
# -------------------------------
with st.sidebar:
    try:
        st.markdown("https://3t.eco", unsafe_allow_html=True)
    except:
        st.warning("Logo failed to load.")
    st.markdown("### **3T Tree Tagging System**")
    st.markdown("*Built for smart forest monitoring 🌍*")
    st.markdown("---")

#
