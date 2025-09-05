
from sqlalchemy import Column, String, Date, Integer, Text, ForeignKey, DateTime
from database import Base
from datetime import datetime

class Tree(Base):
    __tablename__ = "trees"
    TreeID = Column(String(50), primary_key=True)
    GPS = Column(String(100))
    ForestName = Column(String(100))
    TreeName = Column(String(100))
    TreeType = Column(String(50))
    Species = Column(String(100))
    DatePlanted = Column(Date)
    Notes = Column(Text)

class Seed(Base):
    __tablename__ = "seeds"
    SeedID = Column(String(50), primary_key=True)
    ParentTreeID = Column(String(50), ForeignKey("trees.TreeID"))
    DateCollected = Column(Date)
    LocationFound = Column(String(100))
    Notes = Column(Text)

class SyncLog(Base):
    __tablename__ = "synclog"
    SyncID = Column(Integer, primary_key=True, autoincrement=True)
    TreeID = Column(String(50), ForeignKey("trees.TreeID"))
    Timestamp = Column(DateTime, default=datetime.utcnow)
    Status = Column(String(50))
