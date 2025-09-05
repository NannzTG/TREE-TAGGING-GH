from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas, crud
import subprocess
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/trees")
def add_tree(tree: schemas.TreeCreate, db: Session = Depends(get_db)):
    return crud.create_tree(db, tree)

@app.post("/seeds")
def add_seed(seed: schemas.SeedCreate, db: Session = Depends(get_db)):
    return crud.create_seed(db, seed)

@app.post("/sync")
def log_sync(sync: schemas.SyncLogCreate, db: Session = Depends(get_db)):
    return crud.log_sync(db, sync)

@app.get("/scan/{tree_id}")
def scan_tree(tree_id: str, db: Session = Depends(get_db)):
    tree = db.query(models.Tree).filter(models.Tree.TreeID == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")
    return {
        "TreeID": tree.TreeID,
        "GPS": tree.GPS,
        "ForestName": tree.ForestName,
        "TreeName": tree.TreeName,
        "TreeType": tree.TreeType,
        "Species": tree.Species,
        "DatePlanted": str(tree.DatePlanted),
        "Notes": tree.Notes
    }

@app.get("/sync-kobo")
def sync_kobo_data():
    try:
        # Use the Python interpreter from the virtual environment
        python_path = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
        result = subprocess.run(
            [python_path, "kobo_sync_script.py"],
            capture_output=True,
            text=True,
            check=True
        )
        return JSONResponse(content={
            "status": "success",
            "message": result.stdout
        })
    except subprocess.CalledProcessError as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": e.stderr
        })
