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


# ═══════════════════════════════════════════════════════════════
# COLD CHAIN & LOGISTICS
# ═══════════════════════════════════════════════════════════════
class VehicleCreate(BaseModel):
    vehicle_number: str = Field(min_length=3, max_length=20)
    vehicle_type: str = "tempo"
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    capacity_kg: float = 0
    refrigerated: bool = False
    temp_min_c: Optional[float] = None
    temp_max_c: Optional[float] = None
    insurance_expiry: Optional[datetime] = None
    last_service_date: Optional[datetime] = None
    notes: Optional[str] = None

class VehicleOut(OrmBase):
    id: int
    vehicle_number: str
    vehicle_type: str
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    capacity_kg: float
    refrigerated: bool
    temp_min_c: Optional[float] = None
    temp_max_c: Optional[float] = None
    insurance_expiry: Optional[datetime] = None
    last_service_date: Optional[datetime] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime

class ShipmentLotItem(BaseModel):
    lot_id: str
    product: str
    quantity_kg: float

class ColdChainShipmentCreate(BaseModel):
    vehicle_id: Optional[int] = None
    driver_employee_id: Optional[int] = None
    origin_city: str = "Rajapalayam Farm"
    destination_city: str
    delivery_address: Optional[str] = None
    product_category: str   # fish | vegetables | dairy | poultry_products | eggs | honey
    product_lots: Optional[List[ShipmentLotItem]] = None
    total_weight_kg: float = 0
    required_temp_min_c: Optional[float] = None
    required_temp_max_c: Optional[float] = None
    dispatch_time: Optional[datetime] = None
    eta: Optional[datetime] = None
    notes: Optional[str] = None

class ColdChainShipmentOut(OrmBase):
    id: int
    shipment_code: str
    vehicle_id: Optional[int] = None
    driver_employee_id: Optional[int] = None
    origin_city: str
    destination_city: str
    delivery_address: Optional[str] = None
    product_category: str
    product_lots: Optional[list] = None
    total_weight_kg: float
    required_temp_min_c: Optional[float] = None
    required_temp_max_c: Optional[float] = None
    dispatch_time: Optional[datetime] = None
    eta: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    status: str
    has_temperature_breach: bool
    notes: Optional[str] = None
    created_at: datetime

class TemperatureLogCreate(BaseModel):
    temperature_c: float
    humidity_pct: Optional[float] = None
    location: Optional[str] = None
    recorded_by: Optional[str] = None

class TemperatureLogOut(OrmBase):
    id: int
    shipment_id: int
    recorded_at: datetime
    temperature_c: float
    humidity_pct: Optional[float] = None
    location: Optional[str] = None
    is_breach: bool
    breach_threshold_c: Optional[float] = None
    recorded_by: Optional[str] = None

class DeliveryConfirmationCreate(BaseModel):
    recipient_name: str
    recipient_phone: Optional[str] = None
    photo_url: Optional[str] = None
    delivered_weight_kg: float
    temperature_at_delivery_c: Optional[float] = None
    notes: Optional[str] = None

class DeliveryConfirmationOut(OrmBase):
    id: int
    shipment_id: int
    confirmed_at: datetime
    recipient_name: str
    recipient_phone: Optional[str] = None
    photo_url: Optional[str] = None
    delivered_weight_kg: float
    temperature_at_delivery_c: Optional[float] = None
    is_temperature_compliant: bool
    notes: Optional[str] = None

class RejectionCreate(BaseModel):
    rejection_reason: str
    rejected_quantity_kg: float
    accepted_quantity_kg: float = 0
    credit_note_number: Optional[str] = None
    credit_note_amount: float = 0
    photo_url: Optional[str] = None
    customer_name: Optional[str] = None
    notes: Optional[str] = None

class RejectionOut(OrmBase):
    id: int
    shipment_id: int
    rejected_at: datetime
    rejection_reason: str
    rejected_quantity_kg: float
    accepted_quantity_kg: float
    credit_note_number: Optional[str] = None
    credit_note_amount: float
    photo_url: Optional[str] = None
    customer_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


# ── HR & Payroll ──────────────────────────────────────────────────────────────

class LeaveRequestCreate(BaseModel):
    employee_id: int
    leave_type: str  # casual | sick | earned | unpaid
    start_date: date
    end_date: date
    days: int
    reason: Optional[str] = None

class LeaveRequestOut(OrmBase):
    id: int
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    days: int
    reason: Optional[str] = None
    status: str
    approved_by: Optional[int] = None
    created_at: datetime

class LeaveApprovalUpdate(BaseModel):
    status: str  # approved | rejected

class AttendanceCreate(BaseModel):
    employee_id: int
    date: date
    status: str  # present | absent | half_day | leave | holiday
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    overtime_hours: float = 0
    notes: Optional[str] = None

class AttendanceOut(OrmBase):
    id: int
    employee_id: int
    date: date
    status: str
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    overtime_hours: float
    notes: Optional[str] = None
    created_at: datetime

class LeaveBalanceOut(OrmBase):
    id: int
    employee_id: int
    year: int
    leave_type: str
    entitled_days: int
    taken_days: float
    remaining_days: float = 0

    @classmethod
    def from_orm_with_remaining(cls, obj):
        data = cls.model_validate(obj)
        data.remaining_days = max(0.0, obj.entitled_days - obj.taken_days)
        return data

class PayrollRunCreate(BaseModel):
    employee_id: int
    month: int
    year: int
    other_allowances: float = 0
    tds: float = 0
    other_deductions: float = 0
    notes: Optional[str] = None

class PayrollRunOut(OrmBase):
    id: int
    employee_id: int
    month: int
    year: int
    basic_salary: float
    hra: float
    other_allowances: float
    overtime_hours: float
    ot_pay: float
    gross_salary: float
    pf_employee: float
    pf_employer: float
    esi_employee: float
    esi_employer: float
    tds: float
    other_deductions: float
    total_deductions: float
    net_pay: float
    working_days: int
    present_days: float
    absent_days: float
    leave_days: float
    status: str
    payslip_url: Optional[str] = None
    processed_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class PerformanceReviewCreate(BaseModel):
    employee_id: int
    review_period: str  # e.g. Q1_2025
    review_date: date
    productivity_score: float
    quality_score: float
    punctuality_score: float
    teamwork_score: float
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    recommended_increment_pct: float = 0
    notes: Optional[str] = None

class PerformanceReviewOut(OrmBase):
    id: int
    employee_id: int
    review_period: str
    review_date: date
    productivity_score: float
    quality_score: float
    punctuality_score: float
    teamwork_score: float
    overall_score: float
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    recommended_increment_pct: float
    status: str
    reviewed_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class TrainingRecordCreate(BaseModel):
    employee_id: int
    training_name: str
    training_type: str  # safety | technical | compliance | soft_skills | on_the_job | external
    conducted_by: Optional[str] = None
    start_date: date
    end_date: date
    hours: float
    score: Optional[float] = None
    certificate_url: Optional[str] = None
    notes: Optional[str] = None

class TrainingRecordOut(OrmBase):
    id: int
    employee_id: int
    training_name: str
    training_type: str
    conducted_by: Optional[str] = None
    start_date: date
    end_date: date
    hours: float
    score: Optional[float] = None
    certificate_url: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime


# ── Vaccination & Disease Protocol ───────────────────────────────────────────

class VaccinationScheduleCreate(BaseModel):
    species: str
    vaccine_name: str
    disease_target: str
    dose_ml: float = 0
    route: Optional[str] = None
    age_days_start: Optional[int] = None
    repeat_interval_days: Optional[int] = None
    booster_required: bool = False
    withdrawal_period_days: int = 0
    notes: Optional[str] = None

class VaccinationScheduleOut(OrmBase):
    id: int
    species: str
    vaccine_name: str
    disease_target: str
    dose_ml: float
    route: Optional[str] = None
    age_days_start: Optional[int] = None
    repeat_interval_days: Optional[int] = None
    booster_required: bool
    withdrawal_period_days: int
    notes: Optional[str] = None
    created_at: datetime

class VaccinationRecordCreate(BaseModel):
    schedule_id: int
    species: str
    batch_or_flock_id: int
    batch_or_flock_ref: str
    vaccination_date: date
    dose_given_ml: float = 0
    animals_vaccinated: int
    lot_number: Optional[str] = None
    manufacturer: Optional[str] = None
    expiry_date: Optional[date] = None
    adverse_reactions: Optional[str] = None
    notes: Optional[str] = None

class VaccinationRecordOut(OrmBase):
    id: int
    schedule_id: int
    species: str
    batch_or_flock_id: int
    batch_or_flock_ref: str
    vaccination_date: date
    dose_given_ml: float
    animals_vaccinated: int
    vaccinated_by: Optional[int] = None
    next_due_date: Optional[date] = None
    lot_number: Optional[str] = None
    manufacturer: Optional[str] = None
    expiry_date: Optional[date] = None
    adverse_reactions: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

class DiseaseAlertCreate(BaseModel):
    species: str
    batch_or_flock_ref: str
    alert_date: date
    disease_name: str
    symptoms: Optional[str] = None
    affected_count: int = 0
    severity: str = "moderate"
    lab_test_requested: bool = False
    notes: Optional[str] = None

class DiseaseAlertOut(OrmBase):
    id: int
    species: str
    batch_or_flock_ref: str
    alert_date: date
    disease_name: str
    symptoms: Optional[str] = None
    affected_count: int
    mortality_count: int
    severity: str
    status: str
    lab_test_requested: bool
    lab_result: Optional[str] = None
    quarantine_applied: bool
    reported_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class DiseaseAlertUpdate(BaseModel):
    status: Optional[str] = None
    lab_result: Optional[str] = None
    quarantine_applied: Optional[bool] = None
    mortality_count: Optional[int] = None

class TreatmentLogCreate(BaseModel):
    disease_alert_id: int
    treatment_date: date
    drug_name: str
    dosage: str
    route: Optional[str] = None
    animals_treated: int
    duration_days: int = 1
    withdrawal_period_days: int = 0
    cost: float = 0
    vet_name: Optional[str] = None
    notes: Optional[str] = None

class TreatmentLogOut(OrmBase):
    id: int
    disease_alert_id: int
    treatment_date: date
    drug_name: str
    dosage: str
    route: Optional[str] = None
    animals_treated: int
    duration_days: int
    withdrawal_period_days: int
    withdrawal_end_date: Optional[date] = None
    cost: float
    outcome: Optional[str] = None
    administered_by: Optional[int] = None
    vet_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

class MortalityLogCreate(BaseModel):
    species: str
    batch_or_flock_ref: str
    log_date: date
    count: int
    cause: Optional[str] = None
    disease_alert_id: Optional[int] = None
    disposed_by: Optional[str] = None
    notes: Optional[str] = None

class MortalityLogOut(OrmBase):
    id: int
    species: str
    batch_or_flock_ref: str
    log_date: date
    count: int
    cause: Optional[str] = None
    disease_alert_id: Optional[int] = None
    disposed_by: Optional[str] = None
    recorded_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime


# ── Water System ─────────────────────────────────────────────────────────────

class WaterSourceCreate(BaseModel):
    name: str
    source_type: str
    capacity_liters: Optional[float] = None
    depth_meters: Optional[float] = None
    pump_hp: Optional[float] = None
    location_description: Optional[str] = None
    notes: Optional[str] = None

class WaterSourceOut(OrmBase):
    id: int
    name: str
    source_type: str
    capacity_liters: Optional[float] = None
    depth_meters: Optional[float] = None
    pump_hp: Optional[float] = None
    location_description: Optional[str] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime

class WaterStorageTankCreate(BaseModel):
    name: str
    tank_type: Optional[str] = None
    capacity_liters: float
    current_level_liters: float = 0
    source_id: Optional[int] = None
    location: Optional[str] = None
    has_sensor: bool = False
    sensor_device_id: Optional[int] = None
    notes: Optional[str] = None

class WaterStorageTankOut(OrmBase):
    id: int
    name: str
    tank_type: Optional[str] = None
    capacity_liters: float
    current_level_liters: float
    source_id: Optional[int] = None
    location: Optional[str] = None
    has_sensor: bool
    sensor_device_id: Optional[int] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime

class IrrigationZoneCreate(BaseModel):
    name: str
    zone_type: Optional[str] = None
    area_sq_meters: Optional[float] = None
    crop_or_section: Optional[str] = None
    tank_id: Optional[int] = None
    flow_rate_lpm: Optional[float] = None
    is_automated: bool = False
    notes: Optional[str] = None

class IrrigationZoneOut(OrmBase):
    id: int
    name: str
    zone_type: Optional[str] = None
    area_sq_meters: Optional[float] = None
    crop_or_section: Optional[str] = None
    tank_id: Optional[int] = None
    flow_rate_lpm: Optional[float] = None
    is_automated: bool
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime

class IrrigationLogCreate(BaseModel):
    zone_id: int
    irrigation_date: date
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: float = 0
    volume_liters: float = 0
    method: Optional[str] = None
    trigger: str = "manual"
    fertilizer_injected: bool = False
    fertilizer_type: Optional[str] = None
    fertilizer_dose_ml: Optional[float] = None
    notes: Optional[str] = None

class IrrigationLogOut(OrmBase):
    id: int
    zone_id: int
    irrigation_date: date
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: float
    volume_liters: float
    method: Optional[str] = None
    trigger: str
    fertilizer_injected: bool
    fertilizer_type: Optional[str] = None
    fertilizer_dose_ml: Optional[float] = None
    recorded_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class WaterUsageLogCreate(BaseModel):
    source_id: int
    log_date: date
    volume_liters: float
    purpose: Optional[str] = None
    energy_kwh: Optional[float] = None
    notes: Optional[str] = None

class WaterUsageLogOut(OrmBase):
    id: int
    source_id: int
    log_date: date
    volume_liters: float
    purpose: Optional[str] = None
    energy_kwh: Optional[float] = None
    recorded_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class WaterQualityTestCreate(BaseModel):
    source_id: int
    test_date: date
    ph: Optional[float] = None
    tds_ppm: Optional[float] = None
    ec_ms_cm: Optional[float] = None
    turbidity_ntu: Optional[float] = None
    hardness_ppm: Optional[float] = None
    chlorine_ppm: Optional[float] = None
    nitrate_ppm: Optional[float] = None
    coliform_detected: Optional[bool] = None
    is_potable: Optional[bool] = None
    lab_name: Optional[str] = None
    notes: Optional[str] = None

class WaterQualityTestOut(OrmBase):
    id: int
    source_id: int
    test_date: date
    ph: Optional[float] = None
    tds_ppm: Optional[float] = None
    ec_ms_cm: Optional[float] = None
    turbidity_ntu: Optional[float] = None
    hardness_ppm: Optional[float] = None
    chlorine_ppm: Optional[float] = None
    nitrate_ppm: Optional[float] = None
    coliform_detected: Optional[bool] = None
    is_potable: Optional[bool] = None
    lab_name: Optional[str] = None
    tested_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime


# ── Solar & Energy ────────────────────────────────────────────────────────────

class SolarArrayCreate(BaseModel):
    name: str
    location: Optional[str] = None
    panel_count: int = 0
    panel_wattage_wp: float = 0
    total_capacity_kwp: float = 0
    tilt_degrees: Optional[float] = None
    azimuth_degrees: Optional[float] = None
    commissioned_date: Optional[date] = None
    notes: Optional[str] = None

class SolarArrayOut(OrmBase):
    id: int
    name: str
    location: Optional[str] = None
    panel_count: int
    panel_wattage_wp: float
    total_capacity_kwp: float
    tilt_degrees: Optional[float] = None
    azimuth_degrees: Optional[float] = None
    commissioned_date: Optional[date] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime

class InverterCreate(BaseModel):
    name: str
    solar_array_id: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    rated_kva: float = 0
    inverter_type: str = "grid_tie"
    installation_date: Optional[date] = None
    notes: Optional[str] = None

class InverterOut(OrmBase):
    id: int
    name: str
    solar_array_id: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    rated_kva: float
    inverter_type: str
    installation_date: Optional[date] = None
    last_service_date: Optional[date] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime

class EnergyGenerationLogCreate(BaseModel):
    solar_array_id: int
    log_date: date
    units_generated_kwh: float
    peak_power_kw: Optional[float] = None
    sunshine_hours: Optional[float] = None
    inverter_efficiency_pct: Optional[float] = None
    notes: Optional[str] = None

class EnergyGenerationLogOut(OrmBase):
    id: int
    solar_array_id: int
    log_date: date
    units_generated_kwh: float
    peak_power_kw: Optional[float] = None
    sunshine_hours: Optional[float] = None
    inverter_efficiency_pct: Optional[float] = None
    recorded_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class EnergyConsumptionLogCreate(BaseModel):
    log_date: date
    section: str
    units_consumed_kwh: float
    source: str = "solar"
    tariff_per_kwh: Optional[float] = None
    cost: Optional[float] = None
    meter_reading_start: Optional[float] = None
    meter_reading_end: Optional[float] = None
    notes: Optional[str] = None

class EnergyConsumptionLogOut(OrmBase):
    id: int
    log_date: date
    section: str
    units_consumed_kwh: float
    source: str
    tariff_per_kwh: Optional[float] = None
    cost: Optional[float] = None
    meter_reading_start: Optional[float] = None
    meter_reading_end: Optional[float] = None
    recorded_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class BatteryBankCreate(BaseModel):
    name: str
    battery_type: Optional[str] = None
    capacity_kwh: float
    commissioned_date: Optional[date] = None
    notes: Optional[str] = None

class BatteryBankOut(OrmBase):
    id: int
    name: str
    battery_type: Optional[str] = None
    capacity_kwh: float
    current_soc_pct: float
    cycles_completed: int
    commissioned_date: Optional[date] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime

class GridEventCreate(BaseModel):
    event_date: date
    event_type: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    affected_sections: Optional[str] = None
    backup_used: bool = False
    backup_type: Optional[str] = None
    notes: Optional[str] = None

class GridEventOut(OrmBase):
    id: int
    event_date: date
    event_type: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    affected_sections: Optional[str] = None
    backup_used: bool
    backup_type: Optional[str] = None
    reported_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime


# ── Audit & Reporting Calendar ────────────────────────────────────────────────

class AuditLogOut(OrmBase):
    id: int
    timestamp: datetime
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    resource: str
    resource_id: Optional[str] = None
    detail: Optional[str] = None
    ip_address: Optional[str] = None

class ReportScheduleCreate(BaseModel):
    name: str
    report_type: str
    frequency: str
    next_run_date: date
    recipients: Optional[str] = None
    output_format: str = "pdf"
    notes: Optional[str] = None

class ReportScheduleOut(OrmBase):
    id: int
    name: str
    report_type: str
    frequency: str
    next_run_date: date
    recipients: Optional[str] = None
    output_format: str
    is_active: bool
    created_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class ReportExecutionCreate(BaseModel):
    schedule_id: Optional[int] = None
    report_type: str
    parameters: Optional[str] = None  # JSON string

class ReportExecutionOut(OrmBase):
    id: int
    schedule_id: Optional[int] = None
    report_type: str
    triggered_by: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    file_url: Optional[str] = None
    error_message: Optional[str] = None
    requested_by: Optional[int] = None
    parameters: Optional[str] = None
    created_at: datetime


# ── Agri-Tourism ──────────────────────────────────────────────────────────────

class VisitPackageCreate(BaseModel):
    name: str
    description: Optional[str] = None
    package_type: str
    duration_hours: float
    max_group_size: int = 20
    price_per_person: float
    min_age_years: Optional[int] = None
    includes_meal: bool = False
    includes_activity: Optional[str] = None
    available_days: Optional[str] = None
    slots_per_day: int = 2
    is_active: bool = True
    notes: Optional[str] = None

class VisitPackageOut(OrmBase):
    id: int
    name: str
    description: Optional[str] = None
    package_type: str
    duration_hours: float
    max_group_size: int
    price_per_person: float
    min_age_years: Optional[int] = None
    includes_meal: bool
    includes_activity: Optional[str] = None
    available_days: Optional[str] = None
    slots_per_day: int
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime

class VisitorGroupCreate(BaseModel):
    group_name: str
    group_type: str
    contact_person: str
    contact_phone: str
    contact_email: Optional[str] = None
    city: Optional[str] = None
    notes: Optional[str] = None

class VisitorGroupOut(OrmBase):
    id: int
    group_name: str
    group_type: str
    contact_person: str
    contact_phone: str
    contact_email: Optional[str] = None
    city: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

class VisitBookingCreate(BaseModel):
    package_id: int
    visitor_group_id: Optional[int] = None
    visit_date: date
    time_slot: Optional[str] = None
    pax_count: int
    guide_assigned: Optional[str] = None
    advance_paid: float = 0.0
    payment_mode: Optional[str] = None
    notes: Optional[str] = None

class VisitBookingOut(OrmBase):
    id: int
    package_id: int
    visitor_group_id: Optional[int] = None
    visit_date: date
    time_slot: Optional[str] = None
    pax_count: int
    guide_assigned: Optional[str] = None
    price_per_person: float
    total_amount: float
    advance_paid: float
    balance_due: float
    payment_mode: Optional[str] = None
    status: str
    feedback_rating: Optional[int] = None
    feedback_comment: Optional[str] = None
    confirmed_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class TourRevenueEntryCreate(BaseModel):
    booking_id: int
    entry_date: date
    amount_received: float
    payment_mode: str
    notes: Optional[str] = None

class TourRevenueEntryOut(OrmBase):
    id: int
    booking_id: int
    entry_date: date
    amount_received: float
    payment_mode: str
    received_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime


# ── Contract Farming & Consulting ─────────────────────────────────────────────

class NeighbouringFarmCreate(BaseModel):
    farm_name: str
    owner_name: str
    contact_phone: str
    contact_email: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    land_acres: Optional[float] = None
    current_crops: Optional[str] = None
    notes: Optional[str] = None

class NeighbouringFarmOut(OrmBase):
    id: int
    farm_name: str
    owner_name: str
    contact_phone: str
    contact_email: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    land_acres: Optional[float] = None
    current_crops: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

class ConsultingContractCreate(BaseModel):
    contract_number: str
    neighbouring_farm_id: Optional[int] = None
    client_name: str
    contract_type: str
    scope: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    contract_value: float
    payment_terms: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None

class ConsultingContractOut(OrmBase):
    id: int
    contract_number: str
    neighbouring_farm_id: Optional[int] = None
    client_name: str
    contract_type: str
    scope: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    contract_value: float
    payment_terms: Optional[str] = None
    status: str
    total_billed: float
    total_received: float
    created_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class ServiceDeliveryLogCreate(BaseModel):
    contract_id: int
    service_date: date
    service_type: str
    description: Optional[str] = None
    hours_spent: Optional[float] = None
    materials_cost: float = 0.0
    service_charge: float = 0.0
    outcome: Optional[str] = None
    notes: Optional[str] = None

class ServiceDeliveryLogOut(OrmBase):
    id: int
    contract_id: int
    service_date: date
    service_type: str
    description: Optional[str] = None
    hours_spent: Optional[float] = None
    materials_cost: float
    service_charge: float
    outcome: Optional[str] = None
    delivered_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class ConsultingInvoiceCreate(BaseModel):
    invoice_number: str
    contract_id: int
    invoice_date: date
    due_date: Optional[date] = None
    amount: float
    tax_amount: float = 0.0
    total_amount: float
    description: Optional[str] = None
    notes: Optional[str] = None

class ConsultingInvoiceOut(OrmBase):
    id: int
    invoice_number: str
    contract_id: int
    invoice_date: date
    due_date: Optional[date] = None
    amount: float
    tax_amount: float
    total_amount: float
    status: str
    amount_received: float
    payment_date: Optional[date] = None
    payment_mode: Optional[str] = None
    description: Optional[str] = None
    created_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime


# ── Government Subsidies ──────────────────────────────────────────────────────

class SubsidySchemeCreate(BaseModel):
    scheme_code: str
    name: str
    ministry: str
    category: str
    subsidy_pct: Optional[float] = None
    max_amount: Optional[float] = None
    description: Optional[str] = None
    eligibility: Optional[str] = None
    apply_url: Optional[str] = None
    is_active: bool = True
    valid_till: Optional[date] = None
    notes: Optional[str] = None

class SubsidySchemeOut(OrmBase):
    id: int
    scheme_code: str
    name: str
    ministry: str
    category: str
    subsidy_pct: Optional[float] = None
    max_amount: Optional[float] = None
    description: Optional[str] = None
    eligibility: Optional[str] = None
    apply_url: Optional[str] = None
    is_active: bool
    valid_till: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime

class SubsidyApplicationCreate(BaseModel):
    scheme_id: int
    application_number: Optional[str] = None
    applied_date: date
    project_description: Optional[str] = None
    project_cost: float
    claimed_subsidy_amount: float
    documents_submitted: Optional[str] = None
    notes: Optional[str] = None

class SubsidyApplicationOut(OrmBase):
    id: int
    scheme_id: int
    application_number: Optional[str] = None
    applied_date: date
    project_description: Optional[str] = None
    project_cost: float
    claimed_subsidy_amount: float
    status: str
    approved_amount: Optional[float] = None
    approval_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    documents_submitted: Optional[str] = None
    submitted_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class DisbursementRecordCreate(BaseModel):
    application_id: int
    disbursement_date: date
    amount_received: float
    payment_mode: Optional[str] = None
    reference_number: Optional[str] = None
    bank_account: Optional[str] = None
    notes: Optional[str] = None

class DisbursementRecordOut(OrmBase):
    id: int
    application_id: int
    disbursement_date: date
    amount_received: float
    payment_mode: Optional[str] = None
    reference_number: Optional[str] = None
    bank_account: Optional[str] = None
    recorded_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime


# ── Expansion Planning ────────────────────────────────────────────────────────

class ExpansionPhaseCreate(BaseModel):
    name: str
    year: int
    description: Optional[str] = None
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    total_budget: float = 0.0
    notes: Optional[str] = None

class ExpansionPhaseOut(OrmBase):
    id: int
    name: str
    year: int
    description: Optional[str] = None
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    total_budget: float
    total_spent: float
    status: str
    notes: Optional[str] = None
    created_at: datetime

class ExpansionMilestoneCreate(BaseModel):
    phase_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    owner: Optional[str] = None
    priority: str = "medium"
    sort_order: int = 0

class ExpansionMilestoneOut(OrmBase):
    id: int
    phase_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    is_completed: bool
    completion_notes: Optional[str] = None
    owner: Optional[str] = None
    priority: str
    sort_order: int
    completed_by: Optional[int] = None
    created_at: datetime

class ExpansionCapexCreate(BaseModel):
    phase_id: int
    item_name: str
    category: str
    budgeted_amount: float
    actual_amount: float = 0.0
    vendor: Optional[str] = None
    purchase_date: Optional[date] = None
    invoice_ref: Optional[str] = None
    subsidy_applied: bool = False
    subsidy_amount: float = 0.0
    notes: Optional[str] = None

class ExpansionCapexOut(OrmBase):
    id: int
    phase_id: int
    item_name: str
    category: str
    budgeted_amount: float
    actual_amount: float
    vendor: Optional[str] = None
    purchase_date: Optional[date] = None
    invoice_ref: Optional[str] = None
    subsidy_applied: bool
    subsidy_amount: float
    net_cost: float
    notes: Optional[str] = None
    created_at: datetime


# ── Seasonal Calendar ─────────────────────────────────────────────────────────

class SeasonalTaskCreate(BaseModel):
    month: int
    week: Optional[int] = None
    category: str
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None

class SeasonalTaskOut(OrmBase):
    id: int
    month: int
    week: Optional[int] = None
    category: str
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime

class SeasonalTaskCompletionCreate(BaseModel):
    task_id: int
    year: int
    completion_date: date
    outcome: Optional[str] = None
    notes: Optional[str] = None

class SeasonalTaskCompletionOut(OrmBase):
    id: int
    task_id: int
    year: int
    completion_date: date
    outcome: Optional[str] = None
    completed_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

class CropRotationPlanCreate(BaseModel):
    field_or_zone: str
    year: int
    crop_name: str
    variety: Optional[str] = None
    sowing_month: int
    harvest_month: int
    area_sq_meters: Optional[float] = None
    expected_yield_kg: Optional[float] = None
    notes: Optional[str] = None

class CropRotationPlanOut(OrmBase):
    id: int
    field_or_zone: str
    year: int
    crop_name: str
    variety: Optional[str] = None
    sowing_month: int
    harvest_month: int
    area_sq_meters: Optional[float] = None
    expected_yield_kg: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime


# ── Sensor Calibration ────────────────────────────────────────────────────────

class SensorCalibrationLogCreate(BaseModel):
    sensor_id: int
    calibration_date: datetime
    next_calibration_due: Optional[datetime] = None
    variance_before: Optional[float] = None
    variance_after: Optional[float] = None
    calibration_standard: Optional[str] = None
    technician: str
    passed: bool = True
    notes: Optional[str] = None

class SensorCalibrationLogOut(OrmBase):
    id: int
    sensor_id: int
    calibration_date: datetime
    next_calibration_due: Optional[datetime] = None
    variance_before: Optional[float] = None
    variance_after: Optional[float] = None
    calibration_standard: Optional[str] = None
    technician: str
    passed: bool
    notes: Optional[str] = None
    created_at: datetime

class BatteryReplacementLogCreate(BaseModel):
    sensor_id: int
    replacement_date: datetime
    battery_type: Optional[str] = None
    next_replacement_due: Optional[datetime] = None
    replaced_by: str
    notes: Optional[str] = None

class BatteryReplacementLogOut(OrmBase):
    id: int
    sensor_id: int
    replacement_date: datetime
    battery_type: Optional[str] = None
    next_replacement_due: Optional[datetime] = None
    replaced_by: str
    notes: Optional[str] = None
    created_at: datetime

class CameraFirmwareLogCreate(BaseModel):
    sensor_id: int
    update_date: datetime
    previous_version: Optional[str] = None
    new_version: str
    update_method: Optional[str] = None
    updated_by: str
    notes: Optional[str] = None

class CameraFirmwareLogOut(OrmBase):
    id: int
    sensor_id: int
    update_date: datetime
    previous_version: Optional[str] = None
    new_version: str
    update_method: Optional[str] = None
    updated_by: str
    notes: Optional[str] = None
    created_at: datetime

# ── Environmental Monitoring (Ops Manual §17.2) ───────────────────────────────

class WaterOutletLogCreate(BaseModel):
    log_date: date
    outlet_id: str
    location: str
    bod_mg_l: Optional[float] = None
    tss_mg_l: Optional[float] = None
    ph: Optional[float] = None
    turbidity_ntu: Optional[float] = None
    do_mg_l: Optional[float] = None
    temperature_c: Optional[float] = None
    compliant: Optional[bool] = None
    notes: Optional[str] = None

class WaterOutletLogOut(OrmBase):
    id: int
    log_date: date
    outlet_id: str
    location: str
    bod_mg_l: Optional[float] = None
    tss_mg_l: Optional[float] = None
    ph: Optional[float] = None
    turbidity_ntu: Optional[float] = None
    do_mg_l: Optional[float] = None
    temperature_c: Optional[float] = None
    compliant: Optional[bool] = None
    notes: Optional[str] = None
    created_at: datetime

class SoilCarbonLogCreate(BaseModel):
    log_date: date
    field_id: str
    field_name: str
    location: Optional[str] = None
    soc_pct: float
    sampling_depth_cm: Optional[int] = None
    bulk_density: Optional[float] = None
    lab_ref: Optional[str] = None
    notes: Optional[str] = None

class SoilCarbonLogOut(OrmBase):
    id: int
    log_date: date
    field_id: str
    field_name: str
    location: Optional[str] = None
    soc_pct: float
    sampling_depth_cm: Optional[int] = None
    bulk_density: Optional[float] = None
    lab_ref: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

class PesticideApplicationLogCreate(BaseModel):
    application_date: date
    field_id: str
    field_name: str
    active_ingredient: str
    product_name: str
    quantity_kg: float
    area_ha: float
    crop_type: Optional[str] = None
    pest_target: Optional[str] = None
    applied_by: Optional[str] = None
    notes: Optional[str] = None

class PesticideApplicationLogOut(OrmBase):
    id: int
    application_date: date
    field_id: str
    field_name: str
    active_ingredient: str
    product_name: str
    quantity_kg: float
    area_ha: float
    ai_per_ha: Optional[float] = None
    crop_type: Optional[str] = None
    pest_target: Optional[str] = None
    applied_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

class WasteDiversionLogCreate(BaseModel):
    log_date: date
    total_waste_kg: float
    diverted_kg: float
    landfill_kg: float
    compost_kg: Optional[float] = None
    biogas_kg: Optional[float] = None
    recycled_kg: Optional[float] = None
    reused_kg: Optional[float] = None
    notes: Optional[str] = None

class WasteDiversionLogOut(OrmBase):
    id: int
    log_date: date
    total_waste_kg: float
    diverted_kg: float
    landfill_kg: float
    compost_kg: Optional[float] = None
    biogas_kg: Optional[float] = None
    recycled_kg: Optional[float] = None
    reused_kg: Optional[float] = None
    diversion_rate_pct: Optional[float] = None
    meets_target: Optional[bool] = None
    notes: Optional[str] = None
    created_at: datetime

class BiodiversityLogCreate(BaseModel):
    survey_date: date
    survey_type: str
    location: str
    species_count: Optional[int] = None
    individual_count: Optional[int] = None
    indicator_species_present: Optional[bool] = None
    surveyor: Optional[str] = None
    weather_conditions: Optional[str] = None
    species_detail: Optional[dict] = None
    notes: Optional[str] = None

class BiodiversityLogOut(OrmBase):
    id: int
    survey_date: date
    survey_type: str
    location: str
    species_count: Optional[int] = None
    individual_count: Optional[int] = None
    indicator_species_present: Optional[bool] = None
    surveyor: Optional[str] = None
    weather_conditions: Optional[str] = None
    species_detail: Optional[dict] = None
    notes: Optional[str] = None
    created_at: datetime

class SolarNetSurplusLogCreate(BaseModel):
    log_date: date
    generation_kwh: float
    consumption_kwh: float
    grid_export_kwh: Optional[float] = None
    grid_import_kwh: Optional[float] = None
    notes: Optional[str] = None

class SolarNetSurplusLogOut(OrmBase):
    id: int
    log_date: date
    generation_kwh: float
    consumption_kwh: float
    net_surplus_kwh: Optional[float] = None
    grid_export_kwh: Optional[float] = None
    grid_import_kwh: Optional[float] = None
    carbon_offset_kg: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
