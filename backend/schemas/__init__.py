"""Pydantic v2 schemas for request/response validation across all modules."""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ═══════════════════════════════════════════════════════════════
# BASE
# ═══════════════════════════════════════════════════════════════
class OrmBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    per_page: int
    pages: int


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# AUTH / USER
# ═══════════════════════════════════════════════════════════════
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=6)
    full_name: str
    phone: Optional[str] = None
    role_id: int = 5  # default viewer

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str

class UserOut(OrmBase):
    id: int
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role_id: int
    is_active: bool
    created_at: datetime

class RoleOut(OrmBase):
    id: int
    name: str
    description: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# EMPLOYEE / HR
# ═══════════════════════════════════════════════════════════════
class EmployeeCreate(BaseModel):
    employee_code: str
    full_name: str
    department: str
    designation: str
    date_of_joining: date
    phone: str
    base_salary: float
    employment_type: str = "permanent"
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    aadhar_number: Optional[str] = None
    bank_account: Optional[str] = None
    bank_ifsc: Optional[str] = None
    hra: float = 0
    shift: Optional[str] = None

class EmployeeOut(OrmBase):
    id: int
    employee_code: str
    full_name: str
    department: str
    designation: str
    date_of_joining: date
    phone: str
    base_salary: float
    hra: float
    employment_type: str
    is_active: bool

class AttendanceCreate(BaseModel):
    employee_id: int
    date: date
    status: str  # present, absent, half_day, leave
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    overtime_hours: float = 0
    notes: Optional[str] = None

class AttendanceOut(OrmBase):
    id: int
    employee_id: int
    date: date
    status: str
    overtime_hours: float

class LeaveRequestCreate(BaseModel):
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    days: int
    reason: Optional[str] = None

class SalaryRecordCreate(BaseModel):
    employee_id: int
    month: int
    year: int
    working_days: int
    present_days: int
    overtime_hours: float = 0
    bonus: float = 0
    allowances: float = 0
    other_deductions: float = 0
    advance_recovery: float = 0

class SalaryRecordOut(OrmBase):
    id: int
    employee_id: int
    month: int
    year: int
    gross_salary: float
    total_deductions: float
    net_salary: float
    status: str


# ═══════════════════════════════════════════════════════════════
# AQUACULTURE
# ═══════════════════════════════════════════════════════════════
class PondCreate(BaseModel):
    pond_code: str
    name: str
    pond_type: str
    length_m: float
    width_m: float
    depth_m: float
    lining_type: str = "earthen"
    num_aerators: int = 2
    has_auto_feeder: bool = True

class PondOut(OrmBase):
    id: int
    pond_code: str
    name: str
    pond_type: str
    area_sqm: float
    volume_liters: float
    num_aerators: int
    has_auto_feeder: bool
    status: str

class FishBatchCreate(BaseModel):
    pond_id: int
    batch_code: str
    species: str
    stocking_date: date
    initial_count: int
    initial_avg_weight_g: float
    target_weight_g: float = 1000
    source_hatchery: Optional[str] = None
    cost_per_fingerling: float = 0
    expected_harvest_date: Optional[date] = None

class FishBatchOut(OrmBase):
    id: int
    pond_id: int
    batch_code: str
    species: str
    stocking_date: date
    initial_count: int
    current_count: int
    current_avg_weight_g: float
    fcr: float
    mortality_count: int
    status: str

class FeedLogCreate(BaseModel):
    pond_id: int
    feed_date: date
    feed_time: str
    feed_type: str
    quantity_kg: float
    cost_per_kg: float = 0
    method: str = "auto"
    brand: Optional[str] = None
    notes: Optional[str] = None

class WaterQualityCreate(BaseModel):
    pond_id: int
    recorded_at: datetime
    dissolved_oxygen: Optional[float] = None
    ph: Optional[float] = None
    water_temperature: Optional[float] = None
    ammonia: Optional[float] = None
    nitrite: Optional[float] = None
    turbidity: Optional[float] = None
    source: str = "sensor"

class FishHarvestCreate(BaseModel):
    pond_id: int
    batch_id: int
    harvest_date: date
    harvest_type: str
    species: str
    quantity_kg: float
    count: int
    avg_weight_g: float
    grade: str = "A"
    sale_price_per_kg: float = 0
    buyer: Optional[str] = None
    destination_market: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# CROPS
# ═══════════════════════════════════════════════════════════════
class GreenhouseCropCreate(BaseModel):
    crop_code: str
    greenhouse_id: int
    crop_name: str
    planting_date: date
    area_sqm: float
    plant_count: int = 0
    target_yield_kg: float = 0
    variety: Optional[str] = None
    substrate: str = "soil"

class GreenhouseCropOut(OrmBase):
    id: int
    crop_code: str
    greenhouse_id: int
    crop_name: str
    growth_stage: str
    health_score: float
    target_yield_kg: float
    actual_yield_kg: float
    status: str

class VerticalFarmBatchCreate(BaseModel):
    batch_code: str
    crop_name: str
    tier: str
    seeding_date: date
    cycle_days: int
    tray_count: int
    expected_yield_kg: float = 0

class CropActivityCreate(BaseModel):
    greenhouse_crop_id: Optional[int] = None
    field_crop_id: Optional[int] = None
    activity_date: date
    activity_type: str
    description: str
    labour_hours: float = 0
    cost: float = 0
    chemical_used: Optional[str] = None
    chemical_quantity: Optional[float] = None
    method: str = "manual"

class CropHarvestCreate(BaseModel):
    greenhouse_crop_id: Optional[int] = None
    field_crop_id: Optional[int] = None
    vf_batch_id: Optional[int] = None
    harvest_date: date
    crop_name: str
    quantity_kg: float
    grade: str = "A"
    wastage_kg: float = 0
    sale_price_per_kg: float = 0
    destination: Optional[str] = None

class CropDiseaseCreate(BaseModel):
    greenhouse_crop_id: Optional[int] = None
    field_crop_id: Optional[int] = None
    detected_date: date
    disease_name: str
    pathogen_type: str
    severity: str
    affected_area_pct: float = 0
    detection_method: str = "ai_camera"
    ai_confidence: Optional[float] = None


# ═══════════════════════════════════════════════════════════════
# POULTRY
# ═══════════════════════════════════════════════════════════════
class EggCollectionCreate(BaseModel):
    flock_id: int
    collection_date: date
    total_eggs: int
    broken_eggs: int = 0
    dirty_eggs: int = 0
    grade_a: int = 0
    grade_b: int = 0
    grade_c: int = 0
    sale_price_per_egg: float = 8.0
    collection_method: str = "auto_belt"

class PoultryFeedLogCreate(BaseModel):
    flock_id: int
    feed_date: date
    feed_type: str
    quantity_kg: float
    cost_per_kg: float = 0
    water_consumed_liters: float = 0

class PoultryHealthLogCreate(BaseModel):
    flock_id: int
    log_date: date
    mortality_count: int = 0
    mortality_cause: Optional[str] = None
    sick_count: int = 0
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    vet_visit: bool = False
    shed_temp: Optional[float] = None
    ammonia_ppm: Optional[float] = None


# ═══════════════════════════════════════════════════════════════
# INVENTORY
# ═══════════════════════════════════════════════════════════════
class InventoryItemCreate(BaseModel):
    item_code: str
    name: str
    category_id: int
    unit: str
    current_stock: float = 0
    minimum_stock: float = 0
    maximum_stock: float = 0
    reorder_point: float = 0
    reorder_quantity: float = 0
    unit_cost: float = 0
    location: str = "main_store"
    shelf_life_days: Optional[int] = None

class InventoryItemOut(OrmBase):
    id: int
    item_code: str
    name: str
    category_id: int
    unit: str
    current_stock: float
    reorder_point: float
    unit_cost: float
    total_value: float
    location: str

class InventoryTransactionCreate(BaseModel):
    item_id: int
    transaction_type: str
    quantity: float
    unit_cost: float = 0
    department: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None
    transaction_date: date

class SupplierCreate(BaseModel):
    name: str
    supplier_type: str
    phone: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    gstin: Optional[str] = None
    payment_terms: str = "net_30"

class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    order_date: date
    expected_delivery: Optional[date] = None
    items: List["POItemCreate"]
    notes: Optional[str] = None

class POItemCreate(BaseModel):
    item_id: int
    quantity_ordered: float
    unit_price: float
    gst_rate: float = 0


# ═══════════════════════════════════════════════════════════════
# SENSOR
# ═══════════════════════════════════════════════════════════════
class SensorReadingCreate(BaseModel):
    device_id: int
    recorded_at: datetime
    parameter: str
    value: float
    unit: str

class SensorReadingBulk(BaseModel):
    readings: List[SensorReadingCreate]

class SensorDeviceOut(OrmBase):
    id: int
    device_id: str
    name: str
    sensor_type: str
    location: str
    zone: str
    status: str
    battery_level: Optional[float] = None
    last_reading_at: Optional[datetime] = None

class AlertOut(OrmBase):
    id: int
    alert_type: str
    category: str
    title: str
    message: str
    zone: Optional[str] = None
    acknowledged: bool
    resolved: bool
    created_at: datetime


# ═══════════════════════════════════════════════════════════════
# FINANCIAL
# ═══════════════════════════════════════════════════════════════
class RevenueCreate(BaseModel):
    entry_date: date
    stream: str
    category: str
    description: str
    quantity: float = 0
    unit: Optional[str] = None
    unit_price: float = 0
    total_amount: float
    gst_amount: float = 0
    net_amount: float
    payment_mode: str = "bank"
    customer_name: Optional[str] = None
    market: Optional[str] = None

class ExpenseCreate(BaseModel):
    entry_date: date
    category: str
    description: str
    amount: float
    gst_amount: float = 0
    total_amount: float
    department: str
    subcategory: Optional[str] = None
    vendor: Optional[str] = None
    payment_mode: str = "bank"
    bill_number: Optional[str] = None

class InvoiceCreate(BaseModel):
    invoice_type: str
    invoice_date: date
    due_date: date
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    items: List["InvoiceItemCreate"]

class InvoiceItemCreate(BaseModel):
    description: str
    quantity: float
    unit: str
    unit_price: float
    gst_rate: float = 0


# ═══════════════════════════════════════════════════════════════
# MARKET
# ═══════════════════════════════════════════════════════════════
class MarketPriceCreate(BaseModel):
    recorded_date: date
    market_city: str
    product: str
    category: str
    min_price: float
    max_price: float
    avg_price: float
    unit: str = "kg"

class CustomerCreate(BaseModel):
    customer_code: str
    name: str
    customer_type: str
    phone: str
    city: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    credit_limit: float = 0
    payment_terms: str = "cod"

class OrderCreate(BaseModel):
    customer_id: int
    order_date: date
    delivery_city: str
    items: List["OrderItemCreate"]
    delivery_date: Optional[date] = None

class OrderItemCreate(BaseModel):
    product: str
    category: str
    quantity: float
    unit: str
    unit_price: float
    gst_rate: float = 0

class ShipmentCreate(BaseModel):
    order_id: int
    dispatch_date: datetime
    destination_city: str
    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    transport_mode: str = "truck"
    cold_chain: bool = False
    items: List["ShipmentItemCreate"]

class ShipmentItemCreate(BaseModel):
    product: str
    quantity: float
    unit: str
    weight_kg: float
    packaging: str = "crate"


# ═══════════════════════════════════════════════════════════════
# INCIDENT
# ═══════════════════════════════════════════════════════════════
class IncidentCreate(BaseModel):
    incident_type: str
    severity: str
    reported_by: str
    zone: str
    title: str
    description: str
    affected_system: str
    estimated_loss: float = 0
    detection_method: str = "manual"

class IncidentActionCreate(BaseModel):
    incident_id: int
    action_date: datetime
    action_type: str
    description: str
    performed_by: str
    cost: float = 0
    materials_used: Optional[str] = None

class MaintenanceCreate(BaseModel):
    equipment: str
    equipment_location: str
    maintenance_type: str
    frequency: str
    next_due: date
    assigned_to: Optional[str] = None
    estimated_duration_hours: float = 1
    estimated_cost: float = 0


# ═══════════════════════════════════════════════════════════════
# PRODUCTION
# ═══════════════════════════════════════════════════════════════
class ProductionBatchCreate(BaseModel):
    batch_code: str
    production_date: date
    product: str
    category: str
    source: str
    raw_quantity: float
    raw_unit: str
    final_unit: str
    grade: str = "A"

class ProcessingLogCreate(BaseModel):
    batch_id: int
    process_type: str
    start_time: datetime
    input_quantity: float
    equipment_used: Optional[str] = None

class PackagingLogCreate(BaseModel):
    batch_id: int
    packaging_date: date
    packaging_type: str
    quantity_packed: float
    units_packed: int
    cold_stored: bool = False

class QualityCheckCreate(BaseModel):
    batch_id: int
    check_date: date
    check_type: str
    parameter: str
    expected_value: Optional[str] = None
    actual_value: str
    result: str
    checked_by: str

class StockMovementCreate(BaseModel):
    product: str
    movement_date: date
    movement_type: str
    quantity: float
    unit: str
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    batch_code: Optional[str] = None
    unit_cost: float = 0

class AIQueryRequest(BaseModel):
    query: str
    context_modules: List[str] = Field(default_factory=lambda: ["all"])

class AIQueryResponse(BaseModel):
    query: str
    response: str
    modules_analyzed: List[str]
    timestamp: datetime


# ═══════════════════════════════════════════════════════════════
# STORE CONFIG
# ═══════════════════════════════════════════════════════════════
class StoreConfigOut(OrmBase):
    id: int
    store_name: str
    store_code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    gstin: Optional[str] = None
    currency: str
    tax_inclusive: bool
    receipt_header: Optional[str] = None
    receipt_footer: Optional[str] = None
    default_payment_mode: str
    low_stock_threshold: int
    created_at: datetime
    updated_at: datetime

class StoreConfigUpdate(BaseModel):
    store_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    gstin: Optional[str] = None
    currency: Optional[str] = None
    tax_inclusive: Optional[bool] = None
    receipt_header: Optional[str] = None
    receipt_footer: Optional[str] = None
    default_payment_mode: Optional[str] = None
    low_stock_threshold: Optional[int] = None


# ═══════════════════════════════════════════════════════════════
# PRODUCT CATALOG
# ═══════════════════════════════════════════════════════════════
class ProductCatalogCreate(BaseModel):
    product_code: str
    name: str
    category: str
    source_type: str = "farm_produced"
    unit: str
    selling_price: float = 0
    mrp: float = 0
    cost_price: float = 0
    gst_rate: float = 0
    hsn_code: Optional[str] = None
    barcode: Optional[str] = None
    is_weighable: bool = False
    track_expiry: bool = False
    description: Optional[str] = None

class ProductCatalogOut(OrmBase):
    id: int
    product_code: str
    name: str
    category: str
    source_type: str
    unit: str
    selling_price: float
    mrp: float
    cost_price: float
    gst_rate: float
    hsn_code: Optional[str] = None
    barcode: Optional[str] = None
    is_weighable: bool
    track_expiry: bool
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ProductCatalogUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    source_type: Optional[str] = None
    unit: Optional[str] = None
    selling_price: Optional[float] = None
    mrp: Optional[float] = None
    cost_price: Optional[float] = None
    gst_rate: Optional[float] = None
    hsn_code: Optional[str] = None
    barcode: Optional[str] = None
    is_weighable: Optional[bool] = None
    track_expiry: Optional[bool] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# ═══════════════════════════════════════════════════════════════
# PRICE RULES
# ═══════════════════════════════════════════════════════════════
class PriceRuleCreate(BaseModel):
    product_id: int
    rule_type: str
    customer_type: Optional[str] = None
    min_quantity: float = 0
    discount_pct: float = 0
    fixed_price: Optional[float] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True

class PriceRuleOut(OrmBase):
    id: int
    product_id: int
    rule_type: str
    customer_type: Optional[str] = None
    min_quantity: float
    discount_pct: float
    fixed_price: Optional[float] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool
    created_at: datetime


# ═══════════════════════════════════════════════════════════════
# STORE STOCK
# ═══════════════════════════════════════════════════════════════
class StoreStockOut(OrmBase):
    id: int
    product_id: int
    current_qty: float
    reserved_qty: float
    unit: str
    avg_cost_per_unit: float
    last_received_at: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    location: str
    updated_at: Optional[datetime] = None

class StoreStockAdjust(BaseModel):
    product_id: int
    adjustment_qty: float   # positive = add, negative = remove
    reason: str
    location: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# FARM SUPPLY TRANSFER
# ═══════════════════════════════════════════════════════════════
class FarmSupplyTransferCreate(BaseModel):
    transfer_date: datetime
    source_type: str
    source_id: Optional[int] = None
    product_id: int
    product_name: str
    quantity_transferred: float
    unit: str
    quality_grade: str = "A"
    cost_per_unit: float = 0
    notes: Optional[str] = None

class FarmSupplyTransferOut(OrmBase):
    id: int
    transfer_code: str
    transfer_date: datetime
    source_type: str
    source_id: Optional[int] = None
    product_id: int
    product_name: str
    quantity_transferred: float
    unit: str
    quality_grade: str
    cost_per_unit: float
    total_cost: float
    transferred_by: int
    received_by: Optional[int] = None
    received_at: Optional[datetime] = None
    status: str
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

class TransferReceive(BaseModel):
    received_qty: Optional[float] = None  # if None, uses quantity_transferred
    notes: Optional[str] = None

class TransferReject(BaseModel):
    rejection_reason: str


# ═══════════════════════════════════════════════════════════════
# POS SESSION
# ═══════════════════════════════════════════════════════════════
class POSSessionCreate(BaseModel):
    opening_cash: float = 0
    notes: Optional[str] = None

class POSSessionOut(OrmBase):
    id: int
    session_code: str
    cashier_id: int
    opened_at: datetime
    closed_at: Optional[datetime] = None
    opening_cash: float
    closing_cash: Optional[float] = None
    total_sales: float
    total_transactions: int
    status: str
    notes: Optional[str] = None
    created_at: datetime

class POSSessionClose(BaseModel):
    closing_cash: float
    notes: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# POS CHECKOUT / TRANSACTION
# ═══════════════════════════════════════════════════════════════
class POSItemIn(BaseModel):
    product_id: int
    quantity: float
    unit_price: Optional[float] = None   # override if None, uses catalog price
    discount_pct: float = 0

class POSCheckoutIn(BaseModel):
    session_id: int
    items: List[POSItemIn]
    customer_id: Optional[int] = None
    payment_mode: str = "cash"
    payment_reference: Optional[str] = None
    amount_tendered: float = 0
    notes: Optional[str] = None

class POSTransactionItemOut(OrmBase):
    id: int
    product_id: int
    product_name: str
    barcode: Optional[str] = None
    quantity: float
    unit: str
    unit_price: float
    discount_pct: float
    tax_rate: float
    total: float

class POSTransactionOut(OrmBase):
    id: int
    transaction_code: str
    session_id: int
    customer_id: Optional[int] = None
    cashier_id: int
    transaction_time: datetime
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    amount_tendered: float
    change_given: float
    payment_mode: str
    payment_reference: Optional[str] = None
    status: str
    invoice_id: Optional[int] = None
    notes: Optional[str] = None
    items: List[POSTransactionItemOut] = []
    created_at: datetime


# ═══════════════════════════════════════════════════════════════
# PACKING ORDERS
# ═══════════════════════════════════════════════════════════════
class PackingItemCreate(BaseModel):
    product_id: int
    product_name: Optional[str] = None
    quantity_required: float
    packaging_type: Optional[str] = None
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None

class PackingOrderCreate(BaseModel):
    order_ref_type: str
    order_ref_id: Optional[int] = None
    assigned_to: Optional[int] = None
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[PackingItemCreate]

class PackingItemOut(OrmBase):
    id: int
    product_id: int
    product_name: str
    quantity_required: float
    quantity_packed: float
    packaging_type: Optional[str] = None
    label_printed: bool
    barcode_generated: bool
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None

class PackingOrderOut(OrmBase):
    id: int
    packing_order_code: str
    order_ref_type: str
    order_ref_id: Optional[int] = None
    assigned_to: Optional[int] = None
    scheduled_date: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str
    total_items: int
    notes: Optional[str] = None
    items: List[PackingItemOut] = []
    created_at: datetime

class PackItemRequest(BaseModel):
    quantity_packed: float
    label_printed: bool = False
    barcode_generated: bool = False


# ═══════════════════════════════════════════════════════════════
# BARCODE
# ═══════════════════════════════════════════════════════════════
class BarcodeOut(OrmBase):
    id: int
    barcode: str
    entity_type: str
    entity_id: int
    product_id: Optional[int] = None
    generated_at: datetime
    generated_by: int
    is_active: bool
    last_scanned_at: Optional[datetime] = None
    scan_count: int

class BarcodeScanResult(BaseModel):
    barcode: str
    found: bool
    result: Optional[dict] = None
    message: Optional[str] = None

class BarcodeGenerateRequest(BaseModel):
    product_id: int
    entity_type: str = "product"
    entity_id: Optional[int] = None  # defaults to product_id
    prefix: str = "SFN"


# ═══════════════════════════════════════════════════════════════
# DELIVERY ROUTES & TRIPS
# ═══════════════════════════════════════════════════════════════
class DeliveryRouteCreate(BaseModel):
    route_code: str
    route_name: str
    origin: str
    destination: str
    waypoints: Optional[str] = None  # JSON string
    distance_km: float = 0
    estimated_duration_min: int = 0

class DeliveryRouteOut(OrmBase):
    id: int
    route_code: str
    route_name: str
    origin: str
    destination: str
    waypoints: Optional[str] = None
    distance_km: float
    estimated_duration_min: int
    is_active: bool
    created_at: datetime

class DeliveryTripCreate(BaseModel):
    route_id: Optional[int] = None
    driver_id: int
    vehicle_number: str
    vehicle_type: str = "tempo"
    planned_departure: Optional[datetime] = None
    notes: Optional[str] = None

class DeliveryTripOut(OrmBase):
    id: int
    trip_code: str
    route_id: Optional[int] = None
    driver_id: int
    vehicle_number: str
    vehicle_type: str
    planned_departure: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    total_distance_km: float
    fuel_used_litres: float
    fuel_cost: float
    status: str
    notes: Optional[str] = None
    created_at: datetime

class TripStatusUpdate(BaseModel):
    status: str
    actual_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    total_distance_km: Optional[float] = None
    fuel_used_litres: Optional[float] = None
    fuel_cost: Optional[float] = None
    notes: Optional[str] = None

class DeliveryConfirm(BaseModel):
    recipient_name: Optional[str] = None
    notes: Optional[str] = None

class TripOrderAdd(BaseModel):
    order_id: int
    sequence_no: int = 1
    delivery_address: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# SERVICE REQUESTS
# ═══════════════════════════════════════════════════════════════
class ServiceRequestCreate(BaseModel):
    title: str
    description: str
    department: str
    location: Optional[str] = None
    priority: str = "medium"
    category: str
    affected_equipment: Optional[str] = None
    estimated_cost: float = 0
    scheduled_date: Optional[datetime] = None

class ServiceRequestOut(OrmBase):
    id: int
    request_code: str
    title: str
    description: str
    requested_by: int
    assigned_to: Optional[int] = None
    department: str
    location: Optional[str] = None
    priority: str
    category: str
    affected_equipment: Optional[str] = None
    estimated_cost: float
    actual_cost: float
    scheduled_date: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ServiceRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    affected_equipment: Optional[str] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    scheduled_date: Optional[datetime] = None
    status: Optional[str] = None
    resolution_notes: Optional[str] = None

class ServiceRequestAssign(BaseModel):
    assigned_to: int
    scheduled_date: Optional[datetime] = None

class ServiceRequestResolve(BaseModel):
    resolution_notes: str
    actual_cost: float = 0


# ═══════════════════════════════════════════════════════════════
# ACTIVITY LOG
# ═══════════════════════════════════════════════════════════════
class ActivityLogOut(OrmBase):
    id: int
    timestamp: datetime
    user_id: Optional[int] = None
    username: str
    action: str
    module: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    description: str
    ip_address: Optional[str] = None
    status: str
    error_message: Optional[str] = None
