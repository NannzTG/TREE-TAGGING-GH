
from pydantic import BaseModel
from datetime import date

class TreeCreate(BaseModel):
    TreeID: str
    GPS: str
    ForestName: str
    TreeName: str
    TreeType: str
    Species: str
    DatePlanted: date
    Notes: str

class SeedCreate(BaseModel):
    SeedID: str
    ParentTreeID: str
    DateCollected: date
    LocationFound: str
    Notes: str

class SyncLogCreate(BaseModel):
    TreeID: str
    Status: str
