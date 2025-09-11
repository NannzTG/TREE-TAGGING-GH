from pydantic import BaseModel
from typing import Optional
from datetime import date

class TreeCreate(BaseModel):
    TreeID: str
    KoboID: Optional[int]
    GPS: Optional[str]
    ForestName: Optional[str]
    TreeName: Optional[str]
    TreeType: Optional[str]
    Species: Optional[str]
    DatePlanted: Optional[date]
    Notes: Optional[str]
    COLLECTOR_NAME: Optional[str]
    DATE_OF_MOTHER_TREE_ID: Optional[date]
    DISTRICT_NAME: Optional[str]
    FOREST_RESERVE_NAME: Optional[str]
    SPECIES_NAME: Optional[str]
    LOT_CODE: Optional[str]
    DESCRIPTION_TREE_LOCATION: Optional[str]
    DBH_CM: Optional[float]
    TOTAL_TREE_HEIGHT_M: Optional[float]
    CONDITION_OF_TREE_CROWN: Optional[str]
    TRUNK_FORM_OF_TREE: Optional[str]
    HEALTH_STATUS_OF_MOTHER_TREE: Optional[str]
    EVIDENCE_OF_DISEASE_PEST: Optional[str]
    FLOWER_FRUITING_STATUS_OF_MOTH: Optional[str]
    ACCESSIBILITY_FOR_IDENTIFYING: Optional[str]
    MOTHER_TREE_BARCODE_SCAN: Optional[str]
    MOTHER_TREE_MAIN_PHOTO: Optional[str]
    MOTHER_TREE_NORTH_PHOTO: Optional[str]
    MOTHER_TREE_EAST_PHOTO: Optional[str]
    MOTHER_TREE_SOUTH_PHOTO: Optional[str]
    MOTHER_TREE_WEST_PHOTO: Optional[str]
    NUMER_SEEDS_COLLECTED: Optional[float]
    RegionCode: Optional[str]
    ReserveCode: Optional[str]
    SpeciesCode: Optional[str]
    QRCodeURL: Optional[str]

class SeedCreate(BaseModel):
    SeedID: str
    KoboID: Optional[int]
    ParentTreeID: Optional[str]
    DateCollected: Optional[date]
    LocationFound: Optional[str]
    Notes: Optional[str]
    LOT_CODE: Optional[str]
    SEED_COLLECTOR_NAME: Optional[str]
    FOREST_RESERVE: Optional[str]
    SPECIES: Optional[str]
    SEED_QUANTITY_COLLECTED: Optional[float]
    SpeciesCode: Optional[str]
    QRCodeURL: Optional[str]

class SyncLogCreate(BaseModel):
    TreeID: str
    Status: str
