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

# ✅ Corrected PDF export function
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

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)
