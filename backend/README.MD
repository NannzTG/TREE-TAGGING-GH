# 🌳 Tree Logging System Backend

This folder contains the FastAPI backend for the 3T Tree Logging System.

## 🚀 Features
- REST API for managing tree and seed records
- QR scan endpoint: `/scan/{tree_id}`
- KoboToolbox sync endpoint: `/sync-kobo`
- Sync logging via `synclog` table
- MySQL database integration
- HTML rendering via Jinja2 templates

## 📁 Folder Structure
```
backend/
├── main.py                  # FastAPI app entry point
├── models.py                # SQLAlchemy models
├── schemas.py               # Pydantic schemas
├── crud.py                  # Database operations
├── kobo_sync_script.py      # Kobo sync logic
├── database.py              # DB engine and session setup
├── requirements.txt         # Backend dependencies
├── templates/               # HTML templates
│   └── tree_detail.html     # Tree scan view
├── static/
│   └── qrcodes/             # QR code images
```

## ⚙️ Setup Instructions
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## 🔐 Environment Variables
Set these in Railway or a `.env` file:
```
KOBO_TOKEN=your_kobo_token
TREE_FORM_ID=tree_form_id
SEED_FORM_ID=seed_form_id
DB_HOST=your_db_host
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=railway
```

## ☁️ Deployment
- Hosted on Railway
- Cron job runs `kobo_sync_script.py` hourly
- Sync can also be triggered via `/sync-kobo`

## 📄 License
MIT License
