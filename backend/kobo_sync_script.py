import os
import requests
import qrcode
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Tree, Seed, SyncLog
from sqlalchemy.exc import IntegrityError
from database import Base
from datetime import datetime

# ✅ Setup logging
logging.basicConfig(filename="sync_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# ✅ Load environment variables
load_dotenv()

KOBO_TOKEN = os.getenv("KOBO_TOKEN")
TREE_FORM_ID = os.getenv("TREE_FORM_ID")
SEED_FORM_ID = os.getenv("SEED_FORM_ID")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

# ✅ Lookup maps
region_map = {"juaso": "JUA", "mampong": "MAM", "kumawu": "KUM"}
reserve_map = {"bobiri": "BOB", "dome": "DOM", "ofhe": "OFH"}

def generate_species_code(name):
    if not name:
        return "UNK"
    parts = name.split()
    return (parts[0][:3] + parts[-1][:1]).upper() if len(parts) > 1 else name[:4].upper()

def generate_qr(unique_id):
    url = f"https://tree-tagging-gh-production.up.railway.app/scan/{unique_id}"
    img = qrcode.make(url)
    path = f"static/qrcodes/{unique_id}.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return url

def filter_fields(record, model):
    valid_keys = set(c.name for c in model.__table__.columns)
    return {k: v for k, v in record.items() if k in valid_keys}

def sync_kobo(form_id, model, is_tree=True):
    print(f"🔄 Starting sync for {'Tree' if is_tree else 'Seed'} form...")
    url = f"https://kf.kobotoolbox.org/api/v2/assets/{form_id}/data/?format=json"
    headers = {"Authorization": f"Token {KOBO_TOKEN}"}
    session = SessionLocal()

    try:
        response = requests.get(url, headers=headers)
        raw_response = response.text
        with open("kobo_raw_response.txt", "w", encoding="utf-8") as f:
            f.write(raw_response)
        response.raise_for_status()
        data = response.json().get("results", [])
        print(f"✅ Fetched {len(data)} records from Kobo")

        for record in data:
            try:
                kobo_id = record.get("_id")
                if not kobo_id:
                    continue

                region = region_map.get(record.get("DISTRICT_NAME", "").lower(), "UNK")
                reserve = reserve_map.get(record.get("FOREST_RESERVE_NAME", "").lower(), "UNK")
                species = record.get("SPECIES_NAME") or record.get("SPECIES")
                species_code = generate_species_code(species)
                unique_id = f"TREE-{kobo_id}" if is_tree else f"SEED-{kobo_id}"
                qr_url = generate_qr(unique_id)

                print(f"📦 Processing record {unique_id}")
                logging.info(f"Processing record {unique_id}")

                # ✅ GPS extraction from separate lat/lon fields
                lat = record.get("_GPS location of Mother Tree_latitude")
                lon = record.get("_GPS location of Mother Tree_longitude")
                gps = f"{lat},{lon}" if lat and lon else None
                record["GPS"] = gps

                filtered = filter_fields(record, Tree if is_tree else Seed)
                filtered["GPS"] = gps  # Ensure GPS is included

                if is_tree:
                    tree = Tree(
                        **filtered,
                        TreeID=unique_id,
                        KoboID=kobo_id,
                        RegionCode=region,
                        ReserveCode=reserve,
                        SpeciesCode=species_code,
                        QRCodeURL=qr_url
                    )
                    session.add(tree)
                else:
                    seed = Seed(
                        **filtered,
                        SeedID=unique_id,
                        KoboID=kobo_id,
                        SpeciesCode=species_code,
                        QRCodeURL=qr_url
                    )
                    session.add(seed)

                session.commit()

                sync_log = SyncLog(TreeID=unique_id, Status="Success", Timestamp=datetime.utcnow())
                session.add(sync_log)
                session.commit()

            except IntegrityError:
                session.rollback()
                # ✅ Update GPS if record already exists
                if is_tree:
                    existing = session.query(Tree).filter_by(TreeID=unique_id).first()
                    if existing:
                        existing.GPS = gps
                        session.commit()
                sync_log = SyncLog(TreeID=unique_id, Status="Updated", Timestamp=datetime.utcnow())
                session.add(sync_log)
                session.commit()
                print(f"⚠️ Updated existing record {unique_id}")
                logging.warning(f"Updated existing record {unique_id}")
            except Exception as e:
                session.rollback()
                sync_log = SyncLog(TreeID=unique_id, Status=f"Error: {str(e)}", Timestamp=datetime.utcnow())
                session.add(sync_log)
                session.commit()
                print(f"❌ Error syncing {unique_id}: {str(e)}")
                logging.error(f"Error syncing {unique_id}: {str(e)}")

    except Exception as e:
        print(f"❌ Sync failed: {str(e)}")
        logging.critical(f"Sync failed: {str(e)}")
    finally:
        session.close()

# ✅ Run both syncs
sync_kobo(TREE_FORM_ID, Tree, is_tree=True)
sync_kobo(SEED_FORM_ID, Seed, is_tree=False)
