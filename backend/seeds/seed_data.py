"""Seed the database with initial farm data for Nellore Smart Farm."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import date, datetime, timezone, timedelta
from backend.database import init_db, SessionLocal
from backend.models import *
from backend.services.auth_service import hash_password


def seed():
    init_db()
    db = SessionLocal()

    # Check if already seeded
    if db.query(Role).count() > 0:
        print("Database already seeded. Skipping.")
        db.close()
        return

    print("🌱 Seeding SmartFarm database...")

    # ── Roles ──
    roles = [
        Role(id=1, name="admin", description="Full system access"),
        Role(id=2, name="manager", description="Farm management access"),
        Role(id=3, name="supervisor", description="Department supervisor"),
        Role(id=4, name="worker", description="Field worker"),
        Role(id=5, name="viewer", description="Read-only access"),
        # New store roles
        Role(id=6,  name="store_manager", description="Store operations management"),
        Role(id=7,  name="cashier",       description="POS checkout operations"),
        Role(id=8,  name="packer",        description="Packaging and labeling"),
        Role(id=9,  name="driver",        description="Delivery and logistics"),
        Role(id=10, name="scanner",       description="Barcode scanning and stock intake"),
    ]
    db.add_all(roles)
    db.flush()

    # ── Users ──
    admin = User(username="admin", email="admin@smartfarm.in", hashed_password=hash_password("admin123"),
                 full_name="Farm Administrator", phone="9876543210", role_id=1)
    manager = User(username="manager", email="manager@smartfarm.in", hashed_password=hash_password("manager123"),
                   full_name="Ravi Kumar", phone="9876543211", role_id=2)
    db.add_all([admin, manager])
    db.flush()

    store_mgr = User(username="store_mgr", email="store@smartfarm.in",
                     hashed_password=hash_password("store123"),
                     full_name="Priya Store Manager", phone="9876543220", role_id=6)
    cashier1 = User(username="cashier1", email="cashier1@smartfarm.in",
                    hashed_password=hash_password("cashier123"),
                    full_name="Ramu Cashier", phone="9876543221", role_id=7)
    packer1 = User(username="packer1", email="packer1@smartfarm.in",
                   hashed_password=hash_password("packer123"),
                   full_name="Krishna Packer", phone="9876543222", role_id=8)
    driver1 = User(username="driver1", email="driver1@smartfarm.in",
                   hashed_password=hash_password("driver123"),
                   full_name="Ramesh Driver", phone="9876543223", role_id=9)
    scanner1 = User(username="scanner1", email="scanner1@smartfarm.in",
                    hashed_password=hash_password("scanner123"),
                    full_name="Sunil Scanner", phone="9876543224", role_id=10)
    supervisor1 = User(username="supervisor1", email="supervisor1@smartfarm.in",
                       hashed_password=hash_password("supervisor123"),
                       full_name="Anil Supervisor", phone="9876543225", role_id=3)
    worker1 = User(username="worker1", email="worker1@smartfarm.in",
                   hashed_password=hash_password("worker123"),
                   full_name="Gopal Worker", phone="9876543226", role_id=4)
    viewer1 = User(username="viewer1", email="viewer1@smartfarm.in",
                   hashed_password=hash_password("viewer123"),
                   full_name="Sita Viewer", phone="9876543227", role_id=5)
    db.add_all([store_mgr, cashier1, packer1, driver1, scanner1, supervisor1, worker1, viewer1])
    db.flush()

    # ── Employees ──
    employees = [
        Employee(employee_code="EMP-0001", full_name="Ravi Kumar", department="management", designation="Farm Manager",
                 date_of_joining=date(2025, 1, 1), phone="9876543211", base_salary=45000, hra=10000, user_id=manager.id),
        Employee(employee_code="EMP-0002", full_name="Suresh Reddy", department="aquaculture", designation="Aquaculture Supervisor",
                 date_of_joining=date(2025, 2, 1), phone="9876543212", base_salary=25000, hra=5000),
        Employee(employee_code="EMP-0003", full_name="Lakshmi Devi", department="greenhouse", designation="Crop Technician",
                 date_of_joining=date(2025, 2, 15), phone="9876543213", base_salary=18000, hra=3000),
        Employee(employee_code="EMP-0004", full_name="Venkat Rao", department="poultry", designation="Poultry Attendant",
                 date_of_joining=date(2025, 3, 1), phone="9876543214", base_salary=15000, hra=2500),
        Employee(employee_code="EMP-0005", full_name="Anjali Kumari", department="packhouse", designation="Packhouse Operator",
                 date_of_joining=date(2025, 3, 1), phone="9876543215", base_salary=15000, hra=2500),
    ]
    db.add_all(employees)
    db.flush()

    # ── Ponds ──
    ponds = [
        Pond(pond_code="P1", name="Murrel Pond 1", pond_type="murrel", length_m=25, width_m=15, depth_m=1.5,
             area_sqm=375, volume_liters=562500, lining_type="hdpe", num_aerators=2),
        Pond(pond_code="P2", name="Murrel Pond 2", pond_type="murrel", length_m=25, width_m=15, depth_m=1.5,
             area_sqm=375, volume_liters=562500, lining_type="hdpe", num_aerators=2),
        Pond(pond_code="P3", name="IMC Polyculture 1", pond_type="imc_polyculture", length_m=30, width_m=20, depth_m=1.8,
             area_sqm=600, volume_liters=1080000, num_aerators=3),
        Pond(pond_code="P4", name="IMC Polyculture 2", pond_type="imc_polyculture", length_m=30, width_m=20, depth_m=1.8,
             area_sqm=600, volume_liters=1080000, num_aerators=3),
        Pond(pond_code="P5", name="Nursery Pond", pond_type="nursery", length_m=15, width_m=10, depth_m=1.0,
             area_sqm=150, volume_liters=150000, num_aerators=1),
        Pond(pond_code="P6", name="Crab Fattening", pond_type="crab", length_m=15, width_m=10, depth_m=0.8,
             area_sqm=150, volume_liters=120000, num_aerators=1),
    ]
    db.add_all(ponds)
    db.flush()

    # ── Fish Batches ──
    today = date.today()
    batches = [
        FishBatch(pond_id=ponds[0].id, batch_code="FB-0001", species="murrel", stocking_date=today - timedelta(days=140),
                  initial_count=4000, current_count=3800, initial_avg_weight_g=5, current_avg_weight_g=620, target_weight_g=1000,
                  mortality_count=200, fcr=1.78, source_hatchery="AP Fish Seed", cost_per_fingerling=3,
                  total_cost=12000, expected_harvest_date=today + timedelta(days=60)),
        FishBatch(pond_id=ponds[1].id, batch_code="FB-0002", species="murrel", stocking_date=today - timedelta(days=130),
                  initial_count=4000, current_count=3750, initial_avg_weight_g=5, current_avg_weight_g=580, target_weight_g=1000,
                  mortality_count=250, fcr=1.82, source_hatchery="AP Fish Seed", cost_per_fingerling=3, total_cost=12000),
        FishBatch(pond_id=ponds[2].id, batch_code="FB-0003", species="rohu", stocking_date=today - timedelta(days=160),
                  initial_count=3000, current_count=2900, initial_avg_weight_g=10, current_avg_weight_g=450, target_weight_g=800,
                  mortality_count=100, fcr=2.1, cost_per_fingerling=2, total_cost=6000),
        FishBatch(pond_id=ponds[2].id, batch_code="FB-0004", species="catla", stocking_date=today - timedelta(days=160),
                  initial_count=2000, current_count=1950, initial_avg_weight_g=10, current_avg_weight_g=480, target_weight_g=900,
                  mortality_count=50, fcr=2.0, cost_per_fingerling=2, total_cost=4000),
        FishBatch(pond_id=ponds[2].id, batch_code="FB-0005", species="grass_carp", stocking_date=today - timedelta(days=160),
                  initial_count=1000, current_count=950, initial_avg_weight_g=10, current_avg_weight_g=420, target_weight_g=700,
                  mortality_count=50, fcr=2.3, cost_per_fingerling=2, total_cost=2000),
    ]
    db.add_all(batches)

    # ── Greenhouse Crops ──
    gh_crops = [
        GreenhouseCrop(crop_code="GH1-CH", greenhouse_id=1, crop_name="Green Chilli", variety="Teja", planting_date=today - timedelta(days=85),
                       area_sqm=200, plant_count=800, growth_stage="fruiting", health_score=92, target_yield_kg=9000, actual_yield_kg=2400),
        GreenhouseCrop(crop_code="GH1-TM", greenhouse_id=1, crop_name="Tomato", variety="Arka Rakshak", planting_date=today - timedelta(days=62),
                       area_sqm=200, plant_count=600, growth_stage="flowering", health_score=88, target_yield_kg=16000, actual_yield_kg=1800),
        GreenhouseCrop(crop_code="GH1-CU", greenhouse_id=1, crop_name="Cucumber", variety="Malini F1", planting_date=today - timedelta(days=48),
                       area_sqm=150, plant_count=500, growth_stage="harvesting", health_score=95, target_yield_kg=13000, actual_yield_kg=4200),
        GreenhouseCrop(crop_code="GH2-RG", greenhouse_id=2, crop_name="Ridge Gourd", planting_date=today - timedelta(days=28),
                       area_sqm=200, plant_count=400, growth_stage="vegetative", health_score=90, target_yield_kg=7000, actual_yield_kg=800),
        GreenhouseCrop(crop_code="GH2-BG", greenhouse_id=2, crop_name="Bitter Gourd", planting_date=today - timedelta(days=42),
                       area_sqm=150, plant_count=350, growth_stage="flowering", health_score=86, target_yield_kg=6000, actual_yield_kg=1200),
    ]
    db.add_all(gh_crops)

    # ── Vertical Farm ──
    vf_batches = [
        VerticalFarmBatch(batch_code="VF-0001", crop_name="Spinach", tier="1-2", seeding_date=today - timedelta(days=18),
                          cycle_days=28, current_day=18, tray_count=40, health_score=96, expected_yield_kg=120),
        VerticalFarmBatch(batch_code="VF-0002", crop_name="Coriander", tier="3-4", seeding_date=today - timedelta(days=22),
                          cycle_days=30, current_day=22, tray_count=30, health_score=94, expected_yield_kg=95),
        VerticalFarmBatch(batch_code="VF-0003", crop_name="Fenugreek", tier="5", seeding_date=today - timedelta(days=14),
                          cycle_days=25, current_day=14, tray_count=20, health_score=98, expected_yield_kg=85),
        VerticalFarmBatch(batch_code="VF-0004", crop_name="Amaranthus", tier="6", seeding_date=today - timedelta(days=20),
                          cycle_days=28, current_day=20, tray_count=25, health_score=92, expected_yield_kg=110),
    ]
    db.add_all(vf_batches)

    # ── Field Crops ──
    field_crops = [
        FieldCrop(crop_code="FC-TUR", crop_name="Turmeric", variety="Salem", planting_date=today - timedelta(days=180),
                  area_sqm=2000, area_acres=0.5, seed_quantity_kg=200, seed_cost=8000, growth_stage="maturation",
                  health_score=88, target_yield_kg=4000, expected_harvest_date=today + timedelta(days=60)),
        FieldCrop(crop_code="FC-GIN", crop_name="Ginger", variety="Maran", planting_date=today - timedelta(days=160),
                  area_sqm=2000, area_acres=0.5, seed_quantity_kg=300, seed_cost=15000, growth_stage="rhizome_development",
                  health_score=85, target_yield_kg=3500, expected_harvest_date=today + timedelta(days=40)),
    ]
    db.add_all(field_crops)

    # ── Poultry ──
    flock = PoultryFlock(flock_code="PLT-001", breed="BV-300", flock_type="layer", arrival_date=today - timedelta(days=200),
                         initial_count=800, current_count=792, age_weeks=28, avg_weight_g=1800,
                         lay_rate_pct=87.5, peak_lay_pct=92, total_eggs_produced=48000, total_mortality=8)
    db.add(flock)

    duck_flock = DuckFlock(flock_code="DCK-001", breed="Khaki Campbell", initial_count=400, current_count=395,
                           primary_purpose="pest_control", deployment_area="Pond P3-P4 perimeter",
                           daily_eggs_avg=310, eggs_today=310, total_eggs=18000)
    db.add(duck_flock)

    # ── Bee Hives ──
    for i in range(1, 21):
        hive = BeeHive(hive_code=f"BH-{str(i).zfill(3)}", installation_date=today - timedelta(days=120),
                       location_description=f"Zone {'A' if i <= 10 else 'B'}", colony_strength="strong" if i <= 15 else "moderate",
                       frames_with_brood=6, frames_with_honey=3, last_inspection_date=today - timedelta(days=3),
                       total_honey_harvested_kg=2.1 * i)
        db.add(hive)

    # ── Inventory Categories ──
    categories = [
        InventoryCategory(name="Fish Feed"), InventoryCategory(name="Poultry Feed"),
        InventoryCategory(name="Seeds & Seedlings"), InventoryCategory(name="Fertilizers"),
        InventoryCategory(name="Chemicals & Pesticides"), InventoryCategory(name="Packaging Materials"),
        InventoryCategory(name="Equipment Parts"), InventoryCategory(name="Fuel & Lubricants"),
        InventoryCategory(name="Safety Equipment"), InventoryCategory(name="Office Supplies"),
    ]
    db.add_all(categories)
    db.flush()

    # ── Inventory Items ──
    items = [
        InventoryItem(item_code="FF-001", name="Floating Pellet 32%", category_id=categories[0].id, unit="kg",
                      current_stock=2500, minimum_stock=500, maximum_stock=5000, reorder_point=800, reorder_quantity=2000,
                      unit_cost=45, total_value=112500, location="feed_store"),
        InventoryItem(item_code="FF-002", name="Sinking Pellet 36%", category_id=categories[0].id, unit="kg",
                      current_stock=1800, minimum_stock=300, maximum_stock=4000, reorder_point=600, reorder_quantity=1500,
                      unit_cost=52, total_value=93600, location="feed_store"),
        InventoryItem(item_code="PF-001", name="Layer Mash", category_id=categories[1].id, unit="kg",
                      current_stock=800, minimum_stock=200, maximum_stock=2000, reorder_point=400, reorder_quantity=1000,
                      unit_cost=28, total_value=22400, location="feed_store"),
        InventoryItem(item_code="SD-001", name="Tomato Seeds (Arka Rakshak)", category_id=categories[2].id, unit="g",
                      current_stock=500, minimum_stock=100, maximum_stock=2000, reorder_point=200, reorder_quantity=1000,
                      unit_cost=12, total_value=6000, location="seed_store"),
        InventoryItem(item_code="CH-001", name="Neem Oil", category_id=categories[4].id, unit="litres",
                      current_stock=50, minimum_stock=10, maximum_stock=100, reorder_point=20, reorder_quantity=50,
                      unit_cost=350, total_value=17500, location="chemical_store"),
        InventoryItem(item_code="PK-001", name="Egg Trays (30-count)", category_id=categories[5].id, unit="units",
                      current_stock=5000, minimum_stock=1000, maximum_stock=10000, reorder_point=2000, reorder_quantity=5000,
                      unit_cost=5, total_value=25000, location="packhouse"),
    ]
    db.add_all(items)

    # ── Suppliers ──
    suppliers = [
        Supplier(name="Andhra Pradesh Fish Seed Farm", supplier_type="seed", phone="9123456780", city="Vijayawada"),
        Supplier(name="Godrej Agrovet", supplier_type="feed", phone="9123456781", city="Hyderabad"),
        Supplier(name="Tata Solar Power", supplier_type="equipment", phone="9123456782", city="Chennai"),
        Supplier(name="Netafim India", supplier_type="equipment", phone="9123456783", city="Bangalore"),
        Supplier(name="DJI Agriculture India", supplier_type="drone", phone="9123456784", city="Mumbai"),
    ]
    db.add_all(suppliers)

    # ── Customers ──
    customers = [
        Customer(customer_code="C-0001", name="Hyderabad Fish Market (Bowenpally)", customer_type="wholesale",
                 phone="9111111001", city="Hyderabad", credit_limit=200000),
        Customer(customer_code="C-0002", name="Chennai Koyambedu Mandi", customer_type="wholesale",
                 phone="9111111002", city="Chennai", credit_limit=150000),
        Customer(customer_code="C-0003", name="FreshCart Online", customer_type="online_platform",
                 phone="9111111003", city="Hyderabad", credit_limit=100000),
        Customer(customer_code="C-0004", name="Vijayawada Rythu Bazaar", customer_type="wholesale",
                 phone="9111111004", city="Vijayawada"),
        Customer(customer_code="C-0005", name="Nellore Farm Gate Store", customer_type="retail",
                 phone="9111111005", city="Nellore"),
    ]
    db.add_all(customers)

    # ── Sensor Devices ──
    sensors = [
        SensorDevice(device_id="WQ-P1-01", name="P1 Water Quality", sensor_type="water_quality", location="Pond P1", zone="pond_p1", status="online"),
        SensorDevice(device_id="WQ-P2-01", name="P2 Water Quality", sensor_type="water_quality", location="Pond P2", zone="pond_p2", status="online"),
        SensorDevice(device_id="WQ-P3-01", name="P3 Water Quality", sensor_type="water_quality", location="Pond P3", zone="pond_p3", status="online"),
        SensorDevice(device_id="ENV-GH1-01", name="GH1 Environment", sensor_type="environmental", location="Greenhouse 1", zone="gh1", status="online"),
        SensorDevice(device_id="ENV-GH2-01", name="GH2 Environment", sensor_type="environmental", location="Greenhouse 2", zone="gh2", status="online"),
        SensorDevice(device_id="SOIL-GH1-01", name="GH1 Soil Sensor", sensor_type="soil", location="Greenhouse 1", zone="gh1", status="online"),
        SensorDevice(device_id="WX-01", name="Weather Station", sensor_type="weather", location="Main Office", zone="main", status="online"),
        SensorDevice(device_id="PLT-01", name="Poultry Monitor", sensor_type="poultry", location="Poultry Shed", zone="poultry", status="online"),
        SensorDevice(device_id="LVL-RES-01", name="Reservoir Level", sensor_type="level", location="Reservoir", zone="reservoir", status="online"),
        SensorDevice(device_id="SOL-01", name="Solar Monitor", sensor_type="environmental", location="Inverter Room", zone="solar", status="online"),
    ]
    db.add_all(sensors)

    # ── Automation Rules ──
    rules = [
        AutomationRule(name="Aeration on low DO", system="aeration", trigger_type="sensor", priority=1, enabled=True,
                       trigger_condition='{"sensor":"dissolved_oxygen","operator":"<","value":4.5}',
                       action='{"type":"relay","device":"aerator","command":"on","duration_min":60}'),
        AutomationRule(name="Irrigation Zone 1 Morning", system="irrigation", trigger_type="schedule", priority=3, enabled=True,
                       trigger_condition='{"schedule":"06:00","days":"daily"}',
                       action='{"type":"relay","device":"valve_zone1","command":"on","duration_min":30}'),
        AutomationRule(name="Fish Feeding 3x", system="fish_feeder", trigger_type="schedule", priority=2, enabled=True,
                       trigger_condition='{"schedule":"07:00,12:00,17:00","days":"daily"}',
                       action='{"type":"feeder","ponds":"P1,P2,P3,P4","quantity":"auto"}'),
        AutomationRule(name="GH Ventilation on High Temp", system="gh_climate", trigger_type="sensor", priority=1, enabled=True,
                       trigger_condition='{"sensor":"gh_temp","operator":">","value":35}',
                       action='{"type":"relay","device":"gh_fans","command":"on"}'),
        AutomationRule(name="Egg Belt Collection", system="egg_belt", trigger_type="schedule", priority=3, enabled=True,
                       trigger_condition='{"schedule":"08:00,14:00","days":"daily"}',
                       action='{"type":"belt","duration_min":45}'),
    ]
    db.add_all(rules)

    # ── Maintenance Schedules ──
    maint = [
        MaintenanceSchedule(equipment="Aerator P1-A", equipment_location="Pond P1", maintenance_type="preventive",
                            frequency="monthly", next_due=today + timedelta(days=12), assigned_to="Suresh Reddy",
                            estimated_duration_hours=2, estimated_cost=500),
        MaintenanceSchedule(equipment="Solar Inverter", equipment_location="Inverter Room", maintenance_type="preventive",
                            frequency="quarterly", next_due=today + timedelta(days=45), estimated_cost=2000),
        MaintenanceSchedule(equipment="Drip Lines GH1", equipment_location="Greenhouse 1", maintenance_type="cleaning",
                            frequency="monthly", next_due=today + timedelta(days=5), assigned_to="Lakshmi Devi",
                            estimated_duration_hours=3, estimated_cost=300),
    ]
    db.add_all(maint)

    # ── Store Config ──
    store_config = StoreConfig(
        store_name="SmartFarm Direct Store",
        store_code="SFN-001",
        address="SmartFarm, Nellore District, Andhra Pradesh - 524001",
        phone="9876543200",
        gstin="37AABCS1234A1Z5",
        currency="INR",
        tax_inclusive=False,
        receipt_header="SmartFarm — Farm Fresh, Direct to You",
        receipt_footer="Thank you for supporting sustainable farming!",
        default_payment_mode="cash",
        low_stock_threshold=10,
    )
    db.add(store_config)
    db.flush()

    # ── Product Catalog ──
    products = [
        ProductCatalog(product_code="PC-MURREL-KG", name="Murrel Fish (Live)", category="fish",
                       source_type="farm_produced", unit="kg", selling_price=350, mrp=380,
                       cost_price=220, gst_rate=5, hsn_code="0301", is_weighable=True, track_expiry=True,
                       description="Fresh live murrel from our aquaculture ponds"),
        ProductCatalog(product_code="PC-ROHU-KG", name="Rohu Fish (Fresh)", category="fish",
                       source_type="farm_produced", unit="kg", selling_price=180, mrp=200,
                       cost_price=100, gst_rate=5, hsn_code="0302", is_weighable=True, track_expiry=True,
                       description="Fresh rohu from IMC polyculture ponds"),
        ProductCatalog(product_code="PC-CATLA-KG", name="Catla Fish (Fresh)", category="fish",
                       source_type="farm_produced", unit="kg", selling_price=200, mrp=220,
                       cost_price=110, gst_rate=5, hsn_code="0302", is_weighable=True, track_expiry=True,
                       description="Fresh catla from IMC polyculture ponds"),
        ProductCatalog(product_code="PC-CHILLI-KG", name="Green Chilli (Teja)", category="vegetables",
                       source_type="farm_produced", unit="kg", selling_price=80, mrp=90,
                       cost_price=40, gst_rate=0, hsn_code="0904", is_weighable=True, track_expiry=True,
                       description="Teja variety green chilli from greenhouse GH1"),
        ProductCatalog(product_code="PC-TOMATO-KG", name="Tomato (Arka Rakshak)", category="vegetables",
                       source_type="farm_produced", unit="kg", selling_price=50, mrp=60,
                       cost_price=20, gst_rate=0, hsn_code="0702", is_weighable=True, track_expiry=True,
                       description="Hybrid tomato from greenhouse GH1"),
        ProductCatalog(product_code="PC-CUCUMBER-KG", name="Cucumber (Malini F1)", category="vegetables",
                       source_type="farm_produced", unit="kg", selling_price=40, mrp=50,
                       cost_price=18, gst_rate=0, hsn_code="0707", is_weighable=True, track_expiry=True,
                       description="Cucumber from greenhouse GH1"),
        ProductCatalog(product_code="PC-SPINACH-BU", name="Spinach (Vertical Farm)", category="vegetables",
                       source_type="farm_produced", unit="bunch", selling_price=30, mrp=35,
                       cost_price=12, gst_rate=0, hsn_code="0709", is_weighable=False, track_expiry=True,
                       description="Hydroponically grown spinach — pesticide free"),
        ProductCatalog(product_code="PC-CORIANDER-BU", name="Coriander (Vertical Farm)", category="vegetables",
                       source_type="farm_produced", unit="bunch", selling_price=20, mrp=25,
                       cost_price=8, gst_rate=0, hsn_code="0709", is_weighable=False, track_expiry=True,
                       description="Fresh coriander from vertical farm"),
        ProductCatalog(product_code="PC-EGGS-TRAY", name="Eggs (BV-300 Layer)", category="eggs",
                       source_type="farm_produced", unit="tray", selling_price=180, mrp=200,
                       cost_price=120, gst_rate=5, hsn_code="0407", is_weighable=False, track_expiry=True,
                       description="30-count tray of fresh eggs from our BV-300 layer flock"),
        ProductCatalog(product_code="PC-DUCK-EGG-6", name="Duck Eggs (pack of 6)", category="eggs",
                       source_type="farm_produced", unit="pack", selling_price=90, mrp=100,
                       cost_price=55, gst_rate=5, hsn_code="0407", is_weighable=False, track_expiry=True,
                       description="Duck eggs from Khaki Campbell flock — rich & nutritious"),
        ProductCatalog(product_code="PC-HONEY-500G", name="Farm Honey (500g jar)", category="honey",
                       source_type="farm_produced", unit="jar", selling_price=350, mrp=380,
                       cost_price=200, gst_rate=5, hsn_code="0409", is_weighable=False, track_expiry=True,
                       description="Pure raw honey from our 20 bee hives"),
        ProductCatalog(product_code="PC-TURMERIC-100G", name="Turmeric Powder (100g)", category="spices",
                       source_type="farm_produced", unit="pack", selling_price=60, mrp=70,
                       cost_price=25, gst_rate=5, hsn_code="0910", is_weighable=False, track_expiry=True,
                       description="Salem variety turmeric — sun-dried and ground"),
        ProductCatalog(product_code="PC-GINGER-KG", name="Fresh Ginger", category="spices",
                       source_type="farm_produced", unit="kg", selling_price=120, mrp=140,
                       cost_price=60, gst_rate=5, hsn_code="0910", is_weighable=True, track_expiry=True,
                       description="Maran variety fresh ginger from field crops"),
        ProductCatalog(product_code="PC-COMPOST-5KG", name="Farm Compost (5 kg bag)", category="inputs",
                       source_type="farm_produced", unit="bag", selling_price=100, mrp=120,
                       cost_price=30, gst_rate=5, hsn_code="3101", is_weighable=False, track_expiry=False,
                       description="Organic compost from our vermicompost unit"),
        ProductCatalog(product_code="PC-SEEDLING-TRAY", name="Vegetable Seedling Tray", category="nursery",
                       source_type="farm_produced", unit="tray", selling_price=150, mrp=175,
                       cost_price=60, gst_rate=5, hsn_code="0601", is_weighable=False, track_expiry=True,
                       description="Mixed vegetable seedlings — 50 per tray"),
    ]
    db.add_all(products)
    db.flush()

    # ── Store Stock (initial levels) ──
    initial_stocks = [
        (products[0],  25.0,   "cold_room"),   # Murrel 25 kg
        (products[1],  40.0,   "cold_room"),   # Rohu   40 kg
        (products[2],  30.0,   "cold_room"),   # Catla  30 kg
        (products[3],  15.0,   "floor"),       # Green chilli
        (products[4],  50.0,   "floor"),       # Tomato
        (products[5],  60.0,   "floor"),       # Cucumber
        (products[6],  80.0,   "floor"),       # Spinach (bunches)
        (products[7], 100.0,   "floor"),       # Coriander (bunches)
        (products[8],  20.0,   "floor"),       # Eggs trays
        (products[9],  30.0,   "floor"),       # Duck eggs packs
        (products[10], 15.0,   "floor"),       # Honey jars
        (products[11], 50.0,   "backstore"),   # Turmeric packs
        (products[12], 10.0,   "floor"),       # Ginger kg
        (products[13], 40.0,   "backstore"),   # Compost bags
        (products[14],  8.0,   "floor"),       # Seedling trays
    ]
    now_utc = datetime.now(timezone.utc)
    store_stocks = []
    for prod, qty, loc in initial_stocks:
        store_stocks.append(
            StoreStock(
                product_id=prod.id,
                current_qty=qty,
                reserved_qty=0,
                unit=prod.unit,
                avg_cost_per_unit=prod.cost_price,
                last_received_at=now_utc,
                location=loc,
                updated_at=now_utc,
            )
        )
    db.add_all(store_stocks)

    db.commit()
    db.close()
    print("✅ Database seeded successfully with:")
    print("   • 10 roles, 12 users (admin, manager, supervisor1, worker1, viewer1, store_mgr, cashier1, packer1, driver1, scanner1), 5 employees")
    print("   • 6 ponds, 5 fish batches")
    print("   • 5 greenhouse crops, 4 VF batches, 2 field crops")
    print("   • 1 poultry flock (800 hens), 1 duck flock (400), 20 bee hives")
    print("   • 10 inventory categories, 6 items, 5 suppliers, 5 customers")
    print("   • 10 sensor devices, 5 automation rules, 3 maintenance schedules")
    print("   • 1 store config, 15 product catalog entries, 15 store stock records")


if __name__ == "__main__":
    seed()
