"""Model registry — importing here ensures all tables are known to SQLAlchemy."""

from backend.models.user import User, Role, Employee, Attendance, LeaveRequest
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
from backend.models.sensor import SensorDevice, SensorReading, Alert
from backend.models.automation import AutomationRule, AutomationLog, DroneFlightLog
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
from backend.models.logistics import DeliveryRoute, DeliveryTrip, DeliveryTripOrder
from backend.models.service_request import ServiceRequest
from backend.models.activity_log import ActivityLog

__all__ = [
    "User", "Role", "Employee", "Attendance", "LeaveRequest",
    "Pond", "FishBatch", "FeedLog", "WaterQualityLog", "FishHarvest", "CrabBatch",
    "GreenhouseCrop", "VerticalFarmBatch", "FieldCrop", "CropActivity",
    "CropHarvest", "CropDisease",
    "PoultryFlock", "EggCollection", "DuckFlock", "BeeHive", "HoneyHarvest",
    "PoultryFeedLog", "PoultryHealthLog",
    "InventoryCategory", "InventoryItem", "InventoryTransaction",
    "PurchaseOrder", "PurchaseOrderItem", "Supplier",
    "SensorDevice", "SensorReading", "Alert",
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
    "ServiceRequest",
    "ActivityLog",
]
