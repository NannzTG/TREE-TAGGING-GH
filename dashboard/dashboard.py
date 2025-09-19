import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import mysql.connector
from io import BytesIO
from fpdf import FPDF
import qrcode

# Load environment variables
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

# Generate QR image with dynamic URL
def generate_qr_image(tree_id):
    url = f"https://tree-tagging-gh.streamlit.app/?TreeID={tree_id}"
    qr = qrcode.make(url)
    return qr

# Export PDF in memory
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
        with open("temp_qr.png", "wb") as f:
            f.write(qr_buf.read())
        pdf.image("temp_qr.png", x=10, y=50, w=40, h=40)
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
    st.success(f"✅ Data loaded: {df.shape[0]} rows")
except Exception as e:
    st.error("❌ Could not connect to the database.")
    st.exception(e)
    df = pd.DataFrame()

# Apply query param filter
query_params = st.query_params
tree_id_filter = query_params.get("TreeID")
if tree_id_filter and tree_id_filter in df["TreeID"].values:
    df = df[df["TreeID"] == tree_id_filter]

# Display filtered data
st.subheader("📋 Tree Records")
st.dataframe(df, use_container_width=True)

# PDF export button
if not df.empty:
    pdf_data = export_tree_tags_to_pdf(df)
    st.download_button(
        label="📄 Download Tree Tags PDF",
        data=pdf_data,
        file_name="tree_tags.pdf",
        mime="application/pdf"
    )

st.markdown("---")
st.markdown("<small><center>Developed by Nannz for 3T</center></small>", unsafe_allow_html=True)
