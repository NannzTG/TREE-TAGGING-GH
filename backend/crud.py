
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
import models, schemas

def create_tree(db: Session, tree: schemas.TreeCreate):
    try:
        db_tree = models.Tree(**tree.dict())
        db.add(db_tree)
        db.commit()
        db.refresh(db_tree)
        return db_tree
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="TreeID already exists.")

def create_seed(db: Session, seed: schemas.SeedCreate):
    try:
        db_seed = models.Seed(**seed.dict())
        db.add(db_seed)
        db.commit()
        db.refresh(db_seed)
        return db_seed
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="SeedID already exists or ParentTreeID is invalid.")

def log_sync(db: Session, sync: schemas.SyncLogCreate):
    try:
        db_sync = models.SyncLog(TreeID=sync.TreeID, Status=sync.Status)
        db.add(db_sync)
        db.commit()
        db.refresh(db_sync)
        return db_sync
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Sync failed. TreeID may not exist or duplicate SyncID.")
