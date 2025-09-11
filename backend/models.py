from sqlalchemy import Column, String, Date, Float, Text, Integer, ForeignKey, DateTime
from database import Base
from datetime import datetime

class Tree(Base):
    __tablename__ = "trees"
    TreeID = Column(String(50), primary_key=True)
    KoboID = Column(Integer, unique=True)
    GPS = Column(String(100))
    ForestName = Column(String(100))
    TreeName = Column(String(100))
    TreeType = Column(String(100))
    Species = Column(String(100))
    DatePlanted = Column(Date)
    Notes = Column(Text)
    COLLECTOR_NAME = Column(String(100))
    DATE_OF_MOTHER_TREE_ID = Column(Date)
    DISTRICT_NAME = Column(String(100))
    FOREST_RESERVE_NAME = Column(String(100))
    SPECIES_NAME = Column(String(100))
    LOT_CODE = Column(String(100))
    DESCRIPTION_TREE_LOCATION = Column(Text)
    DBH_CM = Column(Float)
    TOTAL_TREE_HEIGHT_M = Column(Float)
    CONDITION_OF_TREE_CROWN = Column(Text)
    TRUNK_FORM_OF_TREE = Column(Text)
    HEALTH_STATUS_OF_MOTHER_TREE = Column(Text)
    EVIDENCE_OF_DISEASE_PEST = Column(Text)
    FLOWER_FRUITING_STATUS_OF_MOTH = Column(Text)
    ACCESSIBILITY_FOR_IDENTIFYING = Column(Text)
    MOTHER_TREE_BARCODE_SCAN = Column(Text)
    MOTHER_TREE_MAIN_PHOTO = Column(Text)
    MOTHER_TREE_NORTH_PHOTO = Column(Text)
    MOTHER_TREE_EAST_PHOTO = Column(Text)
    MOTHER_TREE_SOUTH_PHOTO = Column(Text)
    MOTHER_TREE_WEST_PHOTO = Column(Text)
    NUMER_SEEDS_COLLECTED = Column(Float)
    RegionCode = Column(String(100))
    ReserveCode = Column(String(100))
    SpeciesCode = Column(String(100))
    QRCodeURL = Column(Text)

class Seed(Base):
    __tablename__ = "seeds"
    SeedID = Column(String(100), primary_key=True)
    KoboID = Column(Integer, unique=True)
    ParentTreeID = Column(String(100), ForeignKey("trees.TreeID"))
    DateCollected = Column(Date)
    LocationFound = Column(String(100))
    Notes = Column(Text)
    LOT_CODE = Column(String(100))
    SEED_COLLECTOR_NAME = Column(String(100))
    FOREST_RESERVE = Column(String(100))
    SPECIES = Column(String(100))
    SEED_QUANTITY_COLLECTED = Column(Float)
    SpeciesCode = Column(String(100))
    QRCodeURL = Column(Text)

class SyncLog(Base):
    __tablename__ = "synclog"
    SyncID = Column(Integer, primary_key=True, autoincrement=True)
    TreeID = Column(String(50), ForeignKey("trees.TreeID"))
    Timestamp = Column(DateTime, default=datetime.utcnow)
    Status = Column(String(50))
