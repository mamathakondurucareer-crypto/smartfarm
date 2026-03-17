"""Drone management router."""
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.drone import Drone, DroneFlightLog, DroneSprayLog

router = APIRouter(prefix="/api/drones", tags=["Drone Management"])
MGMT_ROLES = ("admin", "manager", "supervisor")

# ── Schemas ──────────────────────────────────────────────────────────────
class DroneCreate(BaseModel):
    drone_code: str
    name: str
    drone_type: str = "spray"
    battery_health_pct: float = 100.0
    last_maintenance: Optional[date] = None
    status: str = "ready"
    notes: Optional[str] = None

class DroneUpdate(BaseModel):
    name: Optional[str] = None
    drone_type: Optional[str] = None
    battery_health_pct: Optional[float] = None
    last_maintenance: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class DroneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    drone_code: str
    name: str
    drone_type: str
    battery_health_pct: float
    last_maintenance: Optional[date]
    total_flight_hours: float
    status: str
    notes: Optional[str]
    is_active: bool

class FlightLogCreate(BaseModel):
    drone_id: int
    flight_date: date
    mission_type: str
    area_covered_ha: float = 0.0
    duration_mins: int = 0
    pilot: str
    zone: Optional[str] = None
    ndvi_score: Optional[float] = None
    notes: Optional[str] = None

class FlightLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    drone_id: int
    flight_date: date
    mission_type: str
    area_covered_ha: float
    duration_mins: int
    pilot: str
    zone: Optional[str]
    ndvi_score: Optional[float]
    notes: Optional[str]

class SprayLogCreate(BaseModel):
    flight_id: int
    agent_name: str
    agent_type: str = "bio"
    dosage_per_ha: float = 0.0
    total_volume_l: float = 0.0
    gps_zone_coords: Optional[str] = None
    notes: Optional[str] = None

class SprayLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    flight_id: int
    agent_name: str
    agent_type: str
    dosage_per_ha: float
    total_volume_l: float
    gps_zone_coords: Optional[str]
    notes: Optional[str]

# ── Drones CRUD ──────────────────────────────────────────────────────────
@router.get("", response_model=List[DroneOut])
def list_drones(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Drone).filter(Drone.is_active == True).all()

@router.post("", response_model=DroneOut, status_code=201)
def create_drone(data: DroneCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in MGMT_ROLES:
        raise HTTPException(403, "Manager role required")
    if db.query(Drone).filter(Drone.drone_code == data.drone_code).first():
        raise HTTPException(400, "Drone code already exists")
    obj = Drone(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return DroneOut.model_validate(obj)

@router.put("/{drone_id}", response_model=DroneOut)
def update_drone(drone_id: int, data: DroneUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in MGMT_ROLES:
        raise HTTPException(403, "Manager role required")
    obj = db.query(Drone).filter(Drone.id == drone_id, Drone.is_active == True).first()
    if not obj:
        raise HTTPException(404, "Drone not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return DroneOut.model_validate(obj)

@router.delete("/{drone_id}", status_code=204)
def delete_drone(drone_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in ("admin", "manager"):
        raise HTTPException(403, "Admin/manager role required")
    obj = db.query(Drone).filter(Drone.id == drone_id).first()
    if not obj:
        raise HTTPException(404, "Drone not found")
    obj.is_active = False
    db.commit()

# ── Flight Logs ──────────────────────────────────────────────────────────
@router.get("/flights", response_model=List[FlightLogOut])
def list_flights(drone_id: Optional[int] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(DroneFlightLog)
    if drone_id:
        q = q.filter(DroneFlightLog.drone_id == drone_id)
    return q.order_by(DroneFlightLog.flight_date.desc()).all()

@router.post("/flights", response_model=FlightLogOut, status_code=201)
def create_flight(data: FlightLogCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    drone = db.query(Drone).filter(Drone.id == data.drone_id, Drone.is_active == True).first()
    if not drone:
        raise HTTPException(404, "Drone not found")
    obj = DroneFlightLog(**data.model_dump())
    drone.total_flight_hours += data.duration_mins / 60
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return FlightLogOut.model_validate(obj)

@router.delete("/flights/{flight_id}", status_code=204)
def delete_flight(flight_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in MGMT_ROLES:
        raise HTTPException(403, "Manager role required")
    obj = db.query(DroneFlightLog).filter(DroneFlightLog.id == flight_id).first()
    if not obj:
        raise HTTPException(404, "Flight log not found")
    db.delete(obj)
    db.commit()

# ── Spray Logs ──────────────────────────────────────────────────────────
@router.get("/sprays", response_model=List[SprayLogOut])
def list_sprays(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(DroneSprayLog).order_by(DroneSprayLog.id.desc()).all()

@router.post("/sprays", response_model=SprayLogOut, status_code=201)
def create_spray(data: SprayLogCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    flight = db.query(DroneFlightLog).filter(DroneFlightLog.id == data.flight_id).first()
    if not flight:
        raise HTTPException(404, "Flight log not found")
    if flight.spraying:
        raise HTTPException(400, "Spray log already exists for this flight")
    obj = DroneSprayLog(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return SprayLogOut.model_validate(obj)
