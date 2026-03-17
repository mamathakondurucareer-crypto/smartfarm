"""Model registry — importing here ensures all tables are known to SQLAlchemy."""

from backend.models.user import (
    User, Role, Employee, Attendance, LeaveRequest,
    LeaveBalance, PayrollRun, PerformanceReview, TrainingRecord,
)
from backend.models.aquaculture import (
    Pond, FishBatch, FeedLog, WaterQualityLog, FishHarvest, CrabBatch,
)
from backend.models.crop import (
    GreenhouseCrop, VerticalFarmBatch, FieldCrop, CropActivity,
    CropHarvest, CropDisease,
)
from backend.models.poultry import (
    PoultryFlock, EggCollection, DuckFlock, BeeHive, HoneyHarvest,
    PoultryFeedLog, PoultryHealthLog,
)
from backend.models.inventory import (
    InventoryCategory, InventoryItem, InventoryTransaction,
    PurchaseOrder, PurchaseOrderItem, Supplier,
)
from backend.models.sensor import (
    SensorDevice, SensorReading, Alert,
    SensorCalibrationLog, BatteryReplacementLog, CameraFirmwareLog,
)
from backend.models.automation import AutomationRule, AutomationLog
from backend.models.drone import Drone, DroneFlightLog, DroneSprayLog
from backend.models.financial import (
    RevenueEntry, ExpenseEntry, SalaryRecord, Invoice, InvoiceItem,
    BankTransaction, Budget, CostCenter,
)
from backend.models.market import (
    MarketPrice, CustomerOrder, OrderItem, Shipment, ShipmentItem, Customer,
)
from backend.models.incident import Incident, IncidentAction, MaintenanceSchedule
from backend.models.production import (
    ProductionBatch, ProcessingLog, PackagingLog, QualityCheck,
    StockLedger, StockMovement,
)
from backend.models.store import StoreConfig, ProductCatalog, PriceRule
from backend.models.supply_chain import FarmSupplyTransfer, StoreStock
from backend.models.retail import POSSession, POSTransaction, POSTransactionItem
from backend.models.packing import PackingOrder, PackingOrderItem, BarcodeRegistry
from backend.models.logistics import (
    DeliveryRoute, DeliveryTrip, DeliveryTripOrder,
    Vehicle, ColdChainShipment, ShipmentTemperatureLog,
    ShipmentDeliveryConfirmation, ShipmentRejection,
)
from backend.models.service_request import ServiceRequest
from backend.models.activity_log import ActivityLog
from backend.models.feed_production import BSFColony, AzollaLog, DuckweedLog, FeedMillBatch, FeedInventory
from backend.models.qa_traceability import ProductLot, QualityTest, QAQuarantine
from backend.models.compliance import Licence, ComplianceTask
from backend.models.nursery import NurseryBatch, NurseryOrder
from backend.models.vaccination import (
    VaccinationSchedule, VaccinationRecord,
    DiseaseAlert, TreatmentLog, MortalityLog,
)
from backend.models.water import (
    WaterSource, WaterStorageTank, IrrigationZone,
    IrrigationLog, WaterUsageLog, WaterQualityTest,
)
from backend.models.energy import (
    SolarArray, Inverter, EnergyGenerationLog,
    EnergyConsumptionLog, BatteryBank, GridEvent,
)
from backend.models.audit import AuditLog, ReportSchedule, ReportExecution
from backend.models.agritourism import VisitPackage, VisitorGroup, VisitBooking, TourRevenueEntry
from backend.models.contracts import NeighbouringFarm, ConsultingContract, ServiceDeliveryLog, ConsultingInvoice
from backend.models.subsidies import SubsidyScheme, SubsidyApplication, DisbursementRecord
from backend.models.expansion import ExpansionPhase, ExpansionMilestone, ExpansionCapex
from backend.models.seasonal_calendar import SeasonalTask, SeasonalTaskCompletion, CropRotationPlan
from backend.models.environmental import (
    WaterOutletLog, SoilCarbonLog, PesticideApplicationLog,
    WasteDiversionLog, BiodiversityLog, SolarNetSurplusLog,
)

__all__ = [
    "User", "Role", "Employee", "Attendance", "LeaveRequest",
    "LeaveBalance", "PayrollRun", "PerformanceReview", "TrainingRecord",
    "Pond", "FishBatch", "FeedLog", "WaterQualityLog", "FishHarvest", "CrabBatch",
    "GreenhouseCrop", "VerticalFarmBatch", "FieldCrop", "CropActivity",
    "CropHarvest", "CropDisease",
    "PoultryFlock", "EggCollection", "DuckFlock", "BeeHive", "HoneyHarvest",
    "PoultryFeedLog", "PoultryHealthLog",
    "InventoryCategory", "InventoryItem", "InventoryTransaction",
    "PurchaseOrder", "PurchaseOrderItem", "Supplier",
    "SensorDevice", "SensorReading", "Alert",
    "SensorCalibrationLog", "BatteryReplacementLog", "CameraFirmwareLog",
    "AutomationRule", "AutomationLog", "DroneFlightLog",
    "RevenueEntry", "ExpenseEntry", "SalaryRecord", "Invoice", "InvoiceItem",
    "BankTransaction", "Budget", "CostCenter",
    "MarketPrice", "CustomerOrder", "OrderItem", "Shipment", "ShipmentItem", "Customer",
    "Incident", "IncidentAction", "MaintenanceSchedule",
    "ProductionBatch", "ProcessingLog", "PackagingLog", "QualityCheck",
    "StockLedger", "StockMovement",
    "StoreConfig", "ProductCatalog", "PriceRule",
    "FarmSupplyTransfer", "StoreStock",
    "POSSession", "POSTransaction", "POSTransactionItem",
    "PackingOrder", "PackingOrderItem", "BarcodeRegistry",
    "DeliveryRoute", "DeliveryTrip", "DeliveryTripOrder",
    "Vehicle", "ColdChainShipment", "ShipmentTemperatureLog",
    "ShipmentDeliveryConfirmation", "ShipmentRejection",
    "ServiceRequest",
    "ActivityLog",
    "Drone", "DroneFlightLog", "DroneSprayLog",
    "BSFColony", "AzollaLog", "DuckweedLog", "FeedMillBatch", "FeedInventory",
    "ProductLot", "QualityTest", "QAQuarantine",
    "Licence", "ComplianceTask",
    "NurseryBatch", "NurseryOrder",
    "VaccinationSchedule", "VaccinationRecord",
    "DiseaseAlert", "TreatmentLog", "MortalityLog",
    "WaterSource", "WaterStorageTank", "IrrigationZone",
    "IrrigationLog", "WaterUsageLog", "WaterQualityTest",
    "SolarArray", "Inverter", "EnergyGenerationLog",
    "EnergyConsumptionLog", "BatteryBank", "GridEvent",
    "AuditLog", "ReportSchedule", "ReportExecution",
    "VisitPackage", "VisitorGroup", "VisitBooking", "TourRevenueEntry",
    "NeighbouringFarm", "ConsultingContract", "ServiceDeliveryLog", "ConsultingInvoice",
    "SubsidyScheme", "SubsidyApplication", "DisbursementRecord",
    "ExpansionPhase", "ExpansionMilestone", "ExpansionCapex",
    "SeasonalTask", "SeasonalTaskCompletion", "CropRotationPlan",
    "WaterOutletLog", "SoilCarbonLog", "PesticideApplicationLog",
    "WasteDiversionLog", "BiodiversityLog", "SolarNetSurplusLog",
]
