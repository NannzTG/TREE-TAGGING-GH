
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Tree, SyncLog
from datetime import datetime
from sqlalchemy.exc import IntegrityError

# Load .env first
load_dotenv()

# Access environment variables after loading
KOBO_TOKEN = os.getenv("KOBO_TOKEN")
KOBO_FORM_ID = os.getenv("KOBO_FORM_ID")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

KOBO_API_URL = f"https://kf.kobotoolbox.org/api/v2/assets/{KOBO_FORM_ID}/data/"
headers = {
    "Authorization": f"Token {KOBO_TOKEN}",
    "Accept": "application/json"
}

log_entries = []
backup_data = []
session = SessionLocal()
try:
    response = requests.get(KOBO_API_URL, headers=headers)
    raw_response = response.text

    # Save raw response for debugging
    with open("kobo_raw_response.txt", "w", encoding="utf-8") as raw_file:
        raw_file.write(raw_response)

    response.raise_for_status()
    data = response.json()

    if "results" not in data or not data["results"]:
        log_entries.append(f"{datetime.now()} - No submissions found. Sync skipped.")
    else:
        submissions = data["results"]
        for record in submissions:
            try:
                tree = Tree(
                    TreeID=record.get("TreeID"),
                    GPS=record.get("GPS"),
                    ForestName=record.get("ForestName"),
                    TreeName=record.get("TreeName"),
                    TreeType=record.get("TreeType"),
                    Species=record.get("Species"),
                    DatePlanted=record.get("DatePlanted"),
                    Notes=record.get("Notes")
                )
                session.add(tree)
                session.commit()
                session.refresh(tree)
                status = "Success"
            except IntegrityError:
                session.rollback()
                status = "Duplicate or Error"

            sync_log = SyncLog(TreeID=record.get("TreeID"), Status=status)
            session.add(sync_log)
            session.commit()

            log_entries.append(f"{datetime.now()} - TreeID {record.get('TreeID')} - {status}")
            backup_data.append(record)

except Exception as e:
    log_entries.append(f"{datetime.now()} - Sync failed: {str(e)}")
finally:
    session.close()

with open("kobo_sync_log.txt", "w") as log_file:
    for entry in log_entries:
        log_file.write(entry + "\n")

if backup_data:
    df = pd.DataFrame(backup_data)
    df.to_csv("kobo_backup.csv", index=False)
    print(f"{len(backup_data)} records synced from KoboToolbox.")
else:
    print("No new records synced.")


