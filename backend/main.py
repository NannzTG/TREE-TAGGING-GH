from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas, crud
import subprocess
import os

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# Mount static folder (optional, for QR codes or images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST: Add Tree
@app.post("/trees")
def add_tree(tree: schemas.TreeCreate, db: Session = Depends(get_db)):
    return crud.create_tree(db, tree)

# POST: Add Seed
@app.post("/seeds")
def add_seed(seed: schemas.SeedCreate, db: Session = Depends(get_db)):
    return crud.create_seed(db, seed)

# POST: Log Sync
@app.post("/sync")
def log_sync(sync: schemas.SyncLogCreate, db: Session = Depends(get_db)):
    return crud.log_sync(db, sync)

# GET: Scan Tree (HTML page with details + photos)
@app.get("/scan/{tree_id}")
def scan_tree(tree_id: str, request: Request, db: Session = Depends(get_db)):
    tree = db.query(models.Tree).filter(models.Tree.TreeID == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    photos = [
        tree.MOTHER_TREE_MAIN_PHOTO,
        tree.MOTHER_TREE_NORTH_PHOTO,
        tree.MOTHER_TREE_EAST_PHOTO,
        tree.MOTHER_TREE_SOUTH_PHOTO,
        tree.MOTHER_TREE_WEST_PHOTO
    ]

    return templates.TemplateResponse("tree_detail.html", {
        "request": request,
        "tree": tree,
        "photos": photos
    })

# GET: Trigger Kobo Sync Script
@app.get("/sync-kobo")
def sync_kobo_data():
    try:
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

# DELETE: Tree by TreeID
@app.delete("/trees/{tree_id}")
def delete_tree(tree_id: str, db: Session = Depends(get_db)):
    tree = db.query(models.Tree).filter(models.Tree.TreeID == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")
    db.delete(tree)
    db.commit()
    return {"message": f"Tree {tree_id} deleted successfully"}

# DELETE: Seed by SeedID
@app.delete("/seeds/{seed_id}")
def delete_seed(seed_id: str, db: Session = Depends(get_db)):
    seed = db.query(models.Seed).filter(models.Seed.SeedID == seed_id).first()
    if not seed:
        raise HTTPException(status_code=404, detail="Seed not found")
    db.delete(seed)
    db.commit()
    return {"message": f"Seed {seed_id} deleted successfully"}
