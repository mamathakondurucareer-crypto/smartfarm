"""Environmental Monitoring Models — Ops Manual Section 17.2."""

from datetime import date
from typing import Optional
from sqlalchemy import String, Float, Integer, Date, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import TimestampMixin


class WaterOutletLog(Base, TimestampMixin):
    """Weekly water quality at discharge outlets — BOD, TSS, pH."""

    __tablename__ = "water_outlet_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    outlet_id: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    bod_mg_l: Mapped[Optional[float]] = mapped_column(Float, comment="Biochemical Oxygen Demand mg/L")
    tss_mg_l: Mapped[Optional[float]] = mapped_column(Float, comment="Total Suspended Solids mg/L")
    ph: Mapped[Optional[float]] = mapped_column(Float)
    turbidity_ntu: Mapped[Optional[float]] = mapped_column(Float)
    do_mg_l: Mapped[Optional[float]] = mapped_column(Float, comment="Dissolved Oxygen mg/L")
    temperature_c: Mapped[Optional[float]] = mapped_column(Float)
    compliant: Mapped[Optional[bool]] = mapped_column(Boolean)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class SoilCarbonLog(Base, TimestampMixin):
    """Quarterly soil organic carbon measurements — target +0.2%/year."""

    __tablename__ = "soil_carbon_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    field_id: Mapped[str] = mapped_column(String(50), nullable=False)
    field_name: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    soc_pct: Mapped[float] = mapped_column(Float, nullable=False, comment="Soil Organic Carbon %")
    sampling_depth_cm: Mapped[Optional[int]] = mapped_column(Integer)
    bulk_density: Mapped[Optional[float]] = mapped_column(Float)
    lab_ref: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class PesticideApplicationLog(Base, TimestampMixin):
    """Per-application pesticide usage log — target <2 kg AI/ha/year."""

    __tablename__ = "pesticide_application_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    application_date: Mapped[date] = mapped_column(Date, nullable=False)
    field_id: Mapped[str] = mapped_column(String(50), nullable=False)
    field_name: Mapped[str] = mapped_column(String(200), nullable=False)
    active_ingredient: Mapped[str] = mapped_column(String(200), nullable=False)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    area_ha: Mapped[float] = mapped_column(Float, nullable=False)
    ai_per_ha: Mapped[Optional[float]] = mapped_column(Float, comment="Active ingredient kg/ha — computed")
    crop_type: Mapped[Optional[str]] = mapped_column(String(100))
    pest_target: Mapped[Optional[str]] = mapped_column(String(200))
    applied_by: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class WasteDiversionLog(Base, TimestampMixin):
    """Monthly waste diversion tracking — target >95%."""

    __tablename__ = "waste_diversion_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, comment="First day of the month")
    total_waste_kg: Mapped[float] = mapped_column(Float, nullable=False)
    diverted_kg: Mapped[float] = mapped_column(Float, nullable=False)
    landfill_kg: Mapped[float] = mapped_column(Float, nullable=False)
    compost_kg: Mapped[Optional[float]] = mapped_column(Float)
    biogas_kg: Mapped[Optional[float]] = mapped_column(Float)
    recycled_kg: Mapped[Optional[float]] = mapped_column(Float)
    reused_kg: Mapped[Optional[float]] = mapped_column(Float)
    diversion_rate_pct: Mapped[Optional[float]] = mapped_column(Float, comment="Computed: diverted/total*100")
    meets_target: Mapped[Optional[bool]] = mapped_column(Boolean)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class BiodiversityLog(Base, TimestampMixin):
    """Quarterly bird/pollinator count survey records."""

    __tablename__ = "biodiversity_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    survey_date: Mapped[date] = mapped_column(Date, nullable=False)
    survey_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="bird | pollinator | general"
    )
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    species_count: Mapped[Optional[int]] = mapped_column(Integer)
    individual_count: Mapped[Optional[int]] = mapped_column(Integer)
    indicator_species_present: Mapped[Optional[bool]] = mapped_column(Boolean)
    surveyor: Mapped[Optional[str]] = mapped_column(String(100))
    weather_conditions: Mapped[Optional[str]] = mapped_column(String(200))
    species_detail: Mapped[Optional[dict]] = mapped_column(JSON, comment="List of {name, count} dicts")
    notes: Mapped[Optional[str]] = mapped_column(Text)


class SolarNetSurplusLog(Base, TimestampMixin):
    """Daily solar generation vs consumption — feeds carbon surplus reporting."""

    __tablename__ = "solar_net_surplus_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    generation_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    consumption_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    net_surplus_kwh: Mapped[Optional[float]] = mapped_column(Float, comment="Computed: generation - consumption")
    grid_export_kwh: Mapped[Optional[float]] = mapped_column(Float)
    grid_import_kwh: Mapped[Optional[float]] = mapped_column(Float)
    # 0.82 kg CO2e/kWh (India grid emission factor, CEA 2023)
    carbon_offset_kg: Mapped[Optional[float]] = mapped_column(Float, comment="net_surplus * 0.82 kg CO2e")
    notes: Mapped[Optional[str]] = mapped_column(Text)
