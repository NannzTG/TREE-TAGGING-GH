# 🌳 Tree Logging System Dashboard

This folder contains the Streamlit dashboard for the 3T Tree Logging System.

## 📊 Features
- Tree and seed record viewer with filters
- QR code previews
- GPS map view of tree locations
- Sync log viewer
- Export tree tags to PDF

## 📁 Folder Structure
```
dashboard/
├── dashboard.py             # Streamlit app
├── requirements.txt         # Dashboard dependencies
├── logo.png                 # Sidebar branding
├── README.md                # This file
```

## ⚙️ Setup Instructions
```bash
cd dashboard
streamlit run dashboard.py
```

## 🔐 Secrets (Streamlit Cloud)
Set these in `.streamlit/secrets.toml`:
```
DB_HOST="your_db_host"
DB_PORT="3306"
DB_USER="root"
DB_PASSWORD="your_password"
DB_NAME="railway"
```

## ☁️ Deployment
- Hosted on Streamlit Cloud
- Connects to Railway-hosted MySQL database

## 📄 License
MIT License
