# 🌳 Tree Logging System

This repository contains both the **FastAPI backend** and the **Streamlit dashboard** for a tree logging and tracking system.

## 📁 Folder Structure

---
tree-logging-system/ ├── backend/ # FastAPI backend ├── dashboard/ # Streamlit dashboard

## 🚀 FastAPI Backend (`backend/`)

### Features
- REST API for trees, seeds, and sync logs
- QR scan endpoint: `/scan/{tree_id}`
- KoboToolbox sync endpoint: `/sync-kobo`
- MySQL database integration

### Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

Environment Variables

KOBO_TOKEN=
KOBO_FORM_ID=
DB_HOST=
DB_PORT=3306
DB_USER=
DB_PASSWORD=
DB_NAME=

Streamlit Dashboard (dashboard/)
Features
Tree record viewer with filters
QR code previews
GPS map view
Sync log viewer
Export tree tags to PDF
Login system with role-based access

cd dashboard
streamlit run dashboard.py

☁️ Deployment
Dashboard: Hosted on Streamlit Cloud
Backend: Deploy to Railway via GitHub
Sync: Trigger manually via /sync-kobo or schedule with Railway cron job
📦 Requirements
Install dependencies from requirements.txt in each folder.

🛡️ Privacy & Security
GPS data is collected for tree location tracking
No personal data is stored unless added manually
Access control via login system
📄 License
MIT License (or your preferred license)

---

## ✅ Part 2: Can You Manually Upload to GitHub?

Yes — you can manually upload files via the GitHub website.

### 🛠 How to Do It

1. Go to your GitHub repo
2. Click **Add file → Upload files**
3. Drag and drop your `backend/` folder contents (not the folder itself)
4. Click **Commit changes**

✅ This works well for small updates or if you’re not using Git locally.

---

## ✅ Part 3: Detailed CMD Guide to Push via Git

If you prefer using CMD:

### 🧭 Step-by-Step

1. Open CMD
2. Navigate to your project folder:
   ```bash
   cd C:\Users\nanao\tree_data_backend
   

Initialize Git (if not already done):

git init


Link to your GitHub repo:
git remote add origin https://github.com/your-username/your-repo-name.git

git add .
git commit -m "Add backend folder and README"
git push origin main
   