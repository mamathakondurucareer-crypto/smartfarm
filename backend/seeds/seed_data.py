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


def seed_new_modules():
    """Seed extended modules: cold chain, HR, vaccination, water, energy, audit, subsidies, contracts, agritourism, expansion, seasonal, sensors, environmental, compliance."""
    init_db()
    db = SessionLocal()

    try:
        # Guard: skip if subsidy schemes already seeded
        if db.query(SubsidyScheme).count() > 0:
            print("New modules already seeded. Skipping.")
            db.close()
            return

        today = date.today()

        # ─────────────────────────────────────────────────────────────
        # 1. COLD CHAIN SHIPMENTS
        # ─────────────────────────────────────────────────────────────
        cold_chain_shipments = [
            ColdChainShipment(
                shipment_code="CCS-001",
                origin_city="Nellore Farm",
                destination_city="Hyderabad Central Market",
                delivery_address="Bowenpally Wholesale Market, Hyderabad",
                product_category="fish",
                product_lots=[{"lot_id": "LOT-001", "product": "Murrel Fish", "quantity_kg": 120}],
                total_weight_kg=120,
                required_temp_min_c=2.0,
                required_temp_max_c=8.0,
                status="pending",
                notes="Fresh murrel shipment to Hyderabad market"
            ),
            ColdChainShipment(
                shipment_code="CCS-002",
                origin_city="Nellore Farm",
                destination_city="Chennai Koyambedu Market",
                delivery_address="Koyambedu Mandi, Chennai",
                product_category="fish",
                product_lots=[{"lot_id": "LOT-002", "product": "Murrel Fish", "quantity_kg": 150}],
                total_weight_kg=150,
                required_temp_min_c=2.0,
                required_temp_max_c=8.0,
                status="pending",
                notes="Premium murrel batch for Chennai"
            ),
        ]
        db.add_all(cold_chain_shipments)
        db.flush()

        # ─────────────────────────────────────────────────────────────
        # 2. EMPLOYEES (additional, linked to users)
        # ─────────────────────────────────────────────────────────────
        # Get existing users (admin=1, manager=2)
        additional_employees = [
            Employee(
                employee_code="EMP-006",
                full_name="Meera Kumar",
                department="aquaculture",
                designation="Aquaculture Technician",
                date_of_joining=today - timedelta(days=200),
                phone="9876543228",
                base_salary=20000,
                hra=3500,
            ),
            Employee(
                employee_code="EMP-007",
                full_name="Pradeep Singh",
                department="crops",
                designation="Field Manager",
                date_of_joining=today - timedelta(days=150),
                phone="9876543229",
                base_salary=28000,
                hra=5000,
            ),
            Employee(
                employee_code="EMP-008",
                full_name="Divya Sharma",
                department="poultry",
                designation="Poultry Manager",
                date_of_joining=today - timedelta(days=120),
                phone="9876543230",
                base_salary=26000,
                hra=4500,
            ),
            Employee(
                employee_code="EMP-009",
                full_name="Ramakrishna",
                department="logistics",
                designation="Logistics Coordinator",
                date_of_joining=today - timedelta(days=100),
                phone="9876543231",
                base_salary=18000,
                hra=3000,
            ),
        ]
        db.add_all(additional_employees)
        db.flush()

        # ─────────────────────────────────────────────────────────────
        # 3. VACCINATION SCHEDULES & RECORDS
        # ─────────────────────────────────────────────────────────────
        vax_schedules = [
            VaccinationSchedule(
                species="hen",
                vaccine_name="Newcastle Disease Vaccine",
                disease_target="Newcastle",
                dose_ml=0.5,
                route="ocular",
                age_days_start=7,
                repeat_interval_days=180,
                withdrawal_period_days=0,
                notes="Live attenuated vaccine, cool chain required"
            ),
            VaccinationSchedule(
                species="duck",
                vaccine_name="Duck Plague Vaccine",
                disease_target="Duck Plague",
                dose_ml=0.5,
                route="injectable",
                age_days_start=14,
                repeat_interval_days=365,
                withdrawal_period_days=0,
                notes="Inactivated oil adjuvant vaccine"
            ),
            VaccinationSchedule(
                species="hen",
                vaccine_name="Ranikhet Disease Vaccine",
                disease_target="Ranikhet",
                dose_ml=0.5,
                route="nasal",
                age_days_start=21,
                repeat_interval_days=365,
                withdrawal_period_days=0,
                notes="Protective against viral infection"
            ),
        ]
        db.add_all(vax_schedules)
        db.flush()

        vax_records = [
            VaccinationRecord(
                schedule_id=vax_schedules[0].id,
                species="hen",
                batch_or_flock_id=db.query(PoultryFlock).first().id,
                batch_or_flock_ref="PLT-001",
                vaccination_date=today - timedelta(days=40),
                dose_given_ml=400.0,
                animals_vaccinated=800,
                next_due_date=today + timedelta(days=140),
                lot_number="ND-001-2025",
                manufacturer="VPCI Hyderabad",
                expiry_date=today + timedelta(days=120),
                notes="Successful vaccination, no adverse reactions"
            ),
            VaccinationRecord(
                schedule_id=vax_schedules[1].id,
                species="duck",
                batch_or_flock_id=db.query(DuckFlock).first().id,
                batch_or_flock_ref="DCK-001",
                vaccination_date=today - timedelta(days=180),
                dose_given_ml=200.0,
                animals_vaccinated=400,
                next_due_date=today + timedelta(days=185),
                lot_number="DP-002-2024",
                manufacturer="Indian Immunologicals",
                expiry_date=today + timedelta(days=250),
                notes="Annual booster scheduled"
            ),
        ]
        db.add_all(vax_records)
        db.flush()

        # ─────────────────────────────────────────────────────────────
        # 4. WATER SYSTEM
        # ─────────────────────────────────────────────────────────────
        water_sources = [
            WaterSource(
                name="Borewell-01",
                source_type="borewell",
                capacity_liters=100000,
                depth_meters=45,
                pump_hp=2,
                location_description="Near main office",
                is_active=True
            ),
            WaterSource(
                name="Canal-East",
                source_type="canal",
                capacity_liters=500000,
                depth_meters=3,
                pump_hp=5,
                location_description="Eastern field boundary",
                is_active=True
            ),
        ]
        db.add_all(water_sources)
        db.flush()

        water_tanks = [
            WaterStorageTank(
                name="Overhead Tank-1",
                tank_type="overhead",
                capacity_liters=50000,
                current_level_liters=45000,
                source_id=water_sources[0].id,
                location="Main office rooftop",
                has_sensor=True
            ),
            WaterStorageTank(
                name="Field Sump-1",
                tank_type="field_reservoir",
                capacity_liters=100000,
                current_level_liters=80000,
                source_id=water_sources[1].id,
                location="Field crop zone",
                has_sensor=False
            ),
        ]
        db.add_all(water_tanks)
        db.flush()

        irrigation_zones = [
            IrrigationZone(
                name="Greenhouse Zone-1",
                zone_type="drip",
                area_sq_meters=2000,
                crop_or_section="Greenhouse 1 & 2",
                tank_id=water_tanks[0].id,
                flow_rate_lpm=150,
                is_automated=True
            ),
            IrrigationZone(
                name="Field Crop Zone-1",
                zone_type="drip",
                area_sq_meters=3000,
                crop_or_section="Turmeric & Ginger",
                tank_id=water_tanks[1].id,
                flow_rate_lpm=200,
                is_automated=False
            ),
            IrrigationZone(
                name="Field Crop Zone-2",
                zone_type="sprinkler",
                area_sq_meters=2500,
                crop_or_section="Seasonal crops",
                tank_id=water_tanks[1].id,
                flow_rate_lpm=180,
                is_automated=True
            ),
        ]
        db.add_all(irrigation_zones)

        # ─────────────────────────────────────────────────────────────
        # 5. ENERGY / SOLAR
        # ─────────────────────────────────────────────────────────────
        solar_array = SolarArray(
            name="Main Rooftop Array",
            location="Main Roof",
            panel_count=150,
            panel_wattage_wp=400,
            total_capacity_kwp=60,
            tilt_degrees=15,
            azimuth_degrees=180,
            commissioned_date=today - timedelta(days=500),
            is_active=True
        )
        db.add(solar_array)
        db.flush()

        inverter = Inverter(
            name="Main Inverter-1",
            solar_array_id=solar_array.id,
            make="Sungrow",
            model="SG50KTL",
            rated_kva=50,
            inverter_type="grid_tie",
            installation_date=today - timedelta(days=500),
            is_active=True
        )
        db.add(inverter)
        db.flush()

        energy_gen_logs = []
        for i in range(5):
            log_date = today - timedelta(days=i)
            energy_gen_logs.append(
                EnergyGenerationLog(
                    solar_array_id=solar_array.id,
                    log_date=log_date,
                    units_generated_kwh=48 + random.uniform(-5, 5),
                    peak_power_kw=52,
                    sunshine_hours=6.5 + random.uniform(-1, 1),
                    inverter_efficiency_pct=96.5
                )
            )
        db.add_all(energy_gen_logs)

        energy_cons_logs = []
        sections = ["greenhouse", "aquaculture", "packhouse", "irrigation", "total"]
        for i in range(5):
            log_date = today - timedelta(days=i)
            for section in sections:
                energy_cons_logs.append(
                    EnergyConsumptionLog(
                        log_date=log_date,
                        section=section,
                        units_consumed_kwh=random.uniform(28, 42) if section != "total" else random.uniform(140, 180),
                        source="solar",
                        tariff_per_kwh=5.5,
                        cost=random.uniform(150, 250)
                    )
                )
        db.add_all(energy_cons_logs)

        # ─────────────────────────────────────────────────────────────
        # 6. AUDIT / REPORT SCHEDULES
        # ─────────────────────────────────────────────────────────────
        report_schedules = [
            ReportSchedule(
                name="Monthly Farm Financial Report",
                report_type="financial_monthly",
                frequency="monthly",
                next_run_date=today.replace(day=1),
                output_format="pdf",
                is_active=True
            ),
            ReportSchedule(
                name="Monthly Water Usage Report",
                report_type="water_monthly",
                frequency="monthly",
                next_run_date=today.replace(day=5),
                output_format="pdf",
                is_active=True
            ),
            ReportSchedule(
                name="Monthly Energy Report",
                report_type="energy_monthly",
                frequency="monthly",
                next_run_date=today.replace(day=5),
                output_format="xlsx",
                is_active=True
            ),
            ReportSchedule(
                name="Quarterly Compliance Audit",
                report_type="compliance_quarterly",
                frequency="quarterly",
                next_run_date=today + timedelta(days=45),
                output_format="pdf",
                is_active=True
            ),
            ReportSchedule(
                name="Quarterly Investor Report",
                report_type="investor_quarterly",
                frequency="quarterly",
                next_run_date=today + timedelta(days=30),
                output_format="pdf",
                is_active=True
            ),
            ReportSchedule(
                name="Annual Environmental Audit",
                report_type="environmental_annual",
                frequency="quarterly",
                next_run_date=today + timedelta(days=200),
                output_format="pdf",
                is_active=True
            ),
            ReportSchedule(
                name="Annual Licence Renewal Check",
                report_type="compliance_annual",
                frequency="quarterly",
                next_run_date=today + timedelta(days=180),
                output_format="pdf",
                is_active=True
            ),
            ReportSchedule(
                name="Production Report",
                report_type="production_monthly",
                frequency="monthly",
                next_run_date=today.replace(day=10),
                output_format="xlsx",
                is_active=True
            ),
            ReportSchedule(
                name="Harvest Summary",
                report_type="harvest_monthly",
                frequency="monthly",
                next_run_date=today.replace(day=15),
                output_format="pdf",
                is_active=True
            ),
            ReportSchedule(
                name="Safety & Incident Report",
                report_type="safety_monthly",
                frequency="monthly",
                next_run_date=today.replace(day=20),
                output_format="pdf",
                is_active=True
            ),
            ReportSchedule(
                name="Disease & Health Alert",
                report_type="health_weekly",
                frequency="monthly",
                next_run_date=today + timedelta(days=7),
                output_format="pdf",
                is_active=True
            ),
            ReportSchedule(
                name="Marketing & Sales Report",
                report_type="sales_monthly",
                frequency="monthly",
                next_run_date=today.replace(day=25),
                output_format="xlsx",
                is_active=True
            ),
        ]
        db.add_all(report_schedules)

        # ─────────────────────────────────────────────────────────────
        # 7. SUBSIDIES
        # ─────────────────────────────────────────────────────────────
        subsidy_schemes = [
            SubsidyScheme(
                scheme_code="PMKSY",
                name="Pradhan Mantri Krishi Sinchai Yojana",
                ministry="Department of Agriculture & Cooperation",
                category="irrigation",
                subsidy_pct=55.0,
                max_amount=2500000,
                description="Micro-irrigation and water conservation",
                eligibility="Farm size 0.5-50 hectares",
                apply_url="https://pmksy.gov.in"
            ),
            SubsidyScheme(
                scheme_code="RKVY",
                name="Rashtriya Krishi Vikas Yojana",
                ministry="Department of Agriculture & Cooperation",
                category="general",
                subsidy_pct=50.0,
                max_amount=5000000,
                description="Agricultural infrastructure development",
                eligibility="All farmers including tenant farmers"
            ),
            SubsidyScheme(
                scheme_code="NABARD",
                name="NABARD Rural Infrastructure Development",
                ministry="Department of Rural Development",
                category="infrastructure",
                subsidy_pct=40.0,
                max_amount=10000000,
                description="Rural infrastructure creation",
                eligibility="Community, NGO, SHG"
            ),
            SubsidyScheme(
                scheme_code="NLM",
                name="National Livestock Mission",
                ministry="Department of Animal Husbandry",
                category="poultry",
                subsidy_pct=50.0,
                max_amount=2500000,
                description="Livestock rearing and dairy",
                eligibility="Individual and group farmers"
            ),
            SubsidyScheme(
                scheme_code="MNRE",
                name="MNRE Solar Rooftop Initiative",
                ministry="Ministry of New and Renewable Energy",
                category="solar",
                subsidy_pct=30.0,
                max_amount=1500000,
                description="Grid-connected rooftop solar",
                eligibility="Agriculture, residential consumers"
            ),
        ]
        db.add_all(subsidy_schemes)
        db.flush()

        subsidy_apps = [
            SubsidyApplication(
                scheme_id=subsidy_schemes[0].id,
                application_number="PMKSY-2025-001",
                applied_date=today - timedelta(days=60),
                project_description="Drip irrigation for greenhouse and field crops",
                project_cost=3000000,
                claimed_subsidy_amount=1650000,
                status="approved",
                approved_amount=1650000,
                approval_date=today - timedelta(days=15),
                documents_submitted="Project report, land documents, quotations"
            ),
            SubsidyApplication(
                scheme_id=subsidy_schemes[1].id,
                application_number="RKVY-2025-002",
                applied_date=today - timedelta(days=30),
                project_description="Cold chain development for fish logistics",
                project_cost=5000000,
                claimed_subsidy_amount=2500000,
                status="submitted",
                documents_submitted="Feasibility report, technical drawings"
            ),
        ]
        db.add_all(subsidy_apps)

        # ─────────────────────────────────────────────────────────────
        # 8. CONTRACT FARMING
        # ─────────────────────────────────────────────────────────────
        neighbouring_farms = [
            NeighbouringFarm(
                farm_name="Raju Farm",
                owner_name="Raju Reddy",
                contact_phone="9876543240",
                contact_email="raju@farm.in",
                village="Sullurpet",
                district="Nellore",
                land_acres=5,
                current_crops="Paddy, Cotton"
            ),
            NeighbouringFarm(
                farm_name="Venkat Agro",
                owner_name="Venkat Rao",
                contact_phone="9876543241",
                contact_email="venkat@agro.in",
                village="Kaviti",
                district="Nellore",
                land_acres=8,
                current_crops="Sugarcane, Turmeric"
            ),
        ]
        db.add_all(neighbouring_farms)
        db.flush()

        consulting_contracts = [
            ConsultingContract(
                contract_number="CC-001-2025",
                neighbouring_farm_id=neighbouring_farms[0].id,
                client_name="Raju Reddy",
                contract_type="agri_consulting",
                scope="Paddy crop optimization and soil health",
                start_date=today - timedelta(days=90),
                end_date=today + timedelta(days=270),
                contract_value=150000,
                payment_terms="Monthly ₹12,500",
                status="active",
                total_billed=75000,
                total_received=75000
            ),
            ConsultingContract(
                contract_number="CC-002-2024",
                neighbouring_farm_id=neighbouring_farms[1].id,
                client_name="Venkat Rao",
                contract_type="contract_farming",
                scope="Organic turmeric production contract",
                start_date=today - timedelta(days=300),
                end_date=today - timedelta(days=30),
                contract_value=200000,
                payment_terms="On harvest completion",
                status="completed",
                total_billed=200000,
                total_received=200000
            ),
        ]
        db.add_all(consulting_contracts)

        # ─────────────────────────────────────────────────────────────
        # 9. AGRI-TOURISM
        # ─────────────────────────────────────────────────────────────
        visit_packages = [
            VisitPackage(
                name="Half Day Farm Tour",
                description="Morning or afternoon visit with guide, farm walk, product sampling",
                package_type="farm_tour",
                duration_hours=4,
                max_group_size=20,
                price_per_person=500,
                includes_meal=False,
                includes_activity="Farm walk, fish feeding, poultry shed visit",
                available_days="Mon,Tue,Wed,Thu,Fri,Sat,Sun",
                slots_per_day=2
            ),
            VisitPackage(
                name="Full Day Farm Experience",
                description="Complete farm tour with lunch and hands-on activities",
                package_type="farm_tour",
                duration_hours=8,
                max_group_size=25,
                price_per_person=1200,
                includes_meal=True,
                includes_activity="Aquaculture training, greenhouse work, organic farming",
                available_days="Sat,Sun",
                slots_per_day=1
            ),
            VisitPackage(
                name="Overnight Stay Package",
                description="Farm stay with meals, training, night nature walk",
                package_type="agri_camp",
                duration_hours=24,
                max_group_size=15,
                price_per_person=3500,
                includes_meal=True,
                includes_activity="Hands-on farming, solar power workshop, sustainability talk",
                available_days="Fri,Sat",
                slots_per_day=1
            ),
        ]
        db.add_all(visit_packages)
        db.flush()

        visitor_groups = [
            VisitorGroup(
                group_name="Nellore Agricultural College",
                group_type="college",
                contact_person="Dr. Ramesh Kumar",
                contact_phone="9876543250",
                contact_email="agri@nac.edu",
                city="Nellore"
            ),
            VisitorGroup(
                group_name="Eco-tourism SHG",
                group_type="ngo",
                contact_person="Lakshmi Reddy",
                contact_phone="9876543251",
                contact_email="eco@ngo.in",
                city="Hyderabad"
            ),
        ]
        db.add_all(visitor_groups)
        db.flush()

        visit_bookings = [
            VisitBooking(
                package_id=visit_packages[0].id,
                visitor_group_id=visitor_groups[0].id,
                visit_date=today + timedelta(days=10),
                time_slot="09:00",
                pax_count=18,
                guide_assigned="Meera Kumar",
                price_per_person=500,
                total_amount=9000,
                advance_paid=4500,
                balance_due=4500,
                payment_mode="bank_transfer",
                status="confirmed"
            ),
            VisitBooking(
                package_id=visit_packages[1].id,
                visitor_group_id=visitor_groups[1].id,
                visit_date=today - timedelta(days=5),
                time_slot="08:00",
                pax_count=15,
                guide_assigned="Pradeep Singh",
                price_per_person=1200,
                total_amount=18000,
                advance_paid=18000,
                balance_due=0,
                payment_mode="cash",
                status="completed"
            ),
            VisitBooking(
                package_id=visit_packages[2].id,
                visitor_group_id=None,
                visit_date=today + timedelta(days=20),
                time_slot="15:00",
                pax_count=12,
                price_per_person=3500,
                total_amount=42000,
                advance_paid=21000,
                balance_due=21000,
                payment_mode="upi",
                status="pending"
            ),
        ]
        db.add_all(visit_bookings)

        # ─────────────────────────────────────────────────────────────
        # 10. EXPANSION PLANNING
        # ─────────────────────────────────────────────────────────────
        expansion_phase = ExpansionPhase(
            name="Phase 5 - Scale to 50 Acres",
            year=2028,
            description="Doubling farm size with GH3, additional aquaculture, poultry expansion",
            planned_start=date(2027, 6, 1),
            planned_end=date(2028, 12, 31),
            total_budget=15000000,
            total_spent=0,
            status="planned"
        )
        db.add(expansion_phase)
        db.flush()

        expansion_milestones = [
            ExpansionMilestone(
                phase_id=expansion_phase.id,
                title="Land Acquisition",
                description="Purchase additional 15 acres adjacent land",
                due_date=date(2027, 9, 30),
                owner="Ravi Kumar",
                priority="high",
                sort_order=1
            ),
            ExpansionMilestone(
                phase_id=expansion_phase.id,
                title="Infrastructure Build",
                description="Construct GH3, water systems, solar array 2, cold storage",
                due_date=date(2028, 6, 30),
                owner="Pradeep Singh",
                priority="high",
                sort_order=2
            ),
            ExpansionMilestone(
                phase_id=expansion_phase.id,
                title="Operations Launch",
                description="Recruit staff, train team, start operations",
                due_date=date(2028, 9, 30),
                owner="Ravi Kumar",
                priority="medium",
                sort_order=3
            ),
        ]
        db.add_all(expansion_milestones)
        db.flush()

        expansion_capex = [
            ExpansionCapex(
                phase_id=expansion_phase.id,
                item_name="Land Purchase",
                category="land",
                budgeted_amount=7500000,
                actual_amount=0,
                subsidy_applied=False,
                subsidy_amount=0
            ),
            ExpansionCapex(
                phase_id=expansion_phase.id,
                item_name="Greenhouse 3 Construction",
                category="civil_works",
                budgeted_amount=4500000,
                actual_amount=0,
                subsidy_applied=True,
                subsidy_amount=1350000
            ),
            ExpansionCapex(
                phase_id=expansion_phase.id,
                item_name="Solar Array 2 (40 kW)",
                category="solar",
                budgeted_amount=2400000,
                actual_amount=0,
                subsidy_applied=True,
                subsidy_amount=720000
            ),
        ]
        db.add_all(expansion_capex)

        # ─────────────────────────────────────────────────────────────
        # 11. SEASONAL CALENDAR (12 TASKS)
        # ─────────────────────────────────────────────────────────────
        seasonal_tasks = [
            SeasonalTask(month=1, category="aquaculture", title="Stocking fingerlings", description="Pond preparation and fish stocking season"),
            SeasonalTask(month=2, category="soil_prep", title="Soil preparation Field 1", description="Ploughing and composting"),
            SeasonalTask(month=3, category="crops", title="Kharif crop sowing", description="Monsoon crop planning and sowing"),
            SeasonalTask(month=4, category="poultry", title="Q1 vaccination checks", description="Quarterly poultry health review"),
            SeasonalTask(month=5, category="irrigation", title="Drip system maintenance", description="Seasonal irrigation system maintenance"),
            SeasonalTask(month=6, category="aquaculture", title="Monsoon pond management", description="Water level and aeration management"),
            SeasonalTask(month=7, category="crops", title="Paddy transplanting", description="Rice crop transplanting in field zones"),
            SeasonalTask(month=8, category="harvest", title="Murrel batch harvest", description="Harvesting first aquaculture batch"),
            SeasonalTask(month=9, category="marketing", title="Market price survey", description="Weekly market analysis and pricing"),
            SeasonalTask(month=10, category="compliance", title="Licence renewals", description="Government licence compliance checks"),
            SeasonalTask(month=11, category="crops", title="Rabi crop sowing", description="Winter crop sowing and planning"),
            SeasonalTask(month=12, category="maintenance", title="Annual inventory audit", description="Year-end stock and asset verification"),
        ]
        db.add_all(seasonal_tasks)

        # ─────────────────────────────────────────────────────────────
        # 12. SENSOR CALIBRATION & MAINTENANCE
        # ─────────────────────────────────────────────────────────────
        sensor_count = db.query(SensorDevice).count()
        if sensor_count > 0:
            # Get first two sensors
            sensors = db.query(SensorDevice).limit(2).all()

            if len(sensors) >= 1:
                calib_logs = [
                    SensorCalibrationLog(
                        sensor_id=sensors[0].id,
                        calibration_date=datetime.now(timezone.utc) - timedelta(days=15),
                        next_calibration_due=datetime.now(timezone.utc) + timedelta(days=75),
                        variance_before=0.8,
                        variance_after=0.1,
                        calibration_standard="pH 7.0 buffer solution",
                        technician="Suresh Reddy",
                        passed=True,
                        notes="Successfully calibrated, within tolerance"
                    ),
                ]
                if len(sensors) >= 2:
                    calib_logs.append(
                        SensorCalibrationLog(
                            sensor_id=sensors[1].id,
                            calibration_date=datetime.now(timezone.utc) - timedelta(days=5),
                            next_calibration_due=datetime.now(timezone.utc) + timedelta(days=85),
                            variance_before=1.5,
                            variance_after=1.2,
                            calibration_standard="Standard solution 1000 ppm",
                            technician="Lakshmi Devi",
                            passed=False,
                            notes="Drift detected, recalibration needed"
                        )
                    )
                db.add_all(calib_logs)

                battery_logs = [
                    BatteryReplacementLog(
                        sensor_id=sensors[0].id,
                        replacement_date=datetime.now(timezone.utc) - timedelta(days=30),
                        battery_type="AA Lithium 3.6V",
                        next_replacement_due=datetime.now(timezone.utc) + timedelta(days=330),
                        replaced_by="Suresh Reddy",
                        notes="Low battery alert, proactive replacement"
                    ),
                ]
                if len(sensors) >= 2:
                    battery_logs.append(
                        BatteryReplacementLog(
                            sensor_id=sensors[1].id,
                            replacement_date=datetime.now(timezone.utc) - timedelta(days=60),
                            battery_type="AA Lithium 3.6V",
                            next_replacement_due=datetime.now(timezone.utc) + timedelta(days=300),
                            replaced_by="Lakshmi Devi"
                        )
                    )
                db.add_all(battery_logs)

                if len(sensors) >= 1:
                    firmware_log = CameraFirmwareLog(
                        sensor_id=sensors[0].id,
                        update_date=datetime.now(timezone.utc) - timedelta(days=10),
                        previous_version="2.3.1",
                        new_version="2.4.0",
                        update_method="OTA",
                        updated_by="Pradeep Singh",
                        notes="Firmware update successful, improved stability"
                    )
                    db.add(firmware_log)

        # ─────────────────────────────────────────────────────────────
        # 13. ENVIRONMENTAL MONITORING
        # ─────────────────────────────────────────────────────────────
        water_outlet_logs = []
        for i in range(4):
            log_date = today - timedelta(weeks=i)
            water_outlet_logs.append(
                WaterOutletLog(
                    log_date=log_date,
                    outlet_id="OUT-001",
                    location="Main discharge point",
                    bod_mg_l=30 + random.uniform(-5, 5),
                    tss_mg_l=45 + random.uniform(-10, 10),
                    ph=7.2 + random.uniform(-0.3, 0.3),
                    turbidity_ntu=8 + random.uniform(-2, 2),
                    do_mg_l=6.5 + random.uniform(-1, 1),
                    temperature_c=28 + random.uniform(-2, 2),
                    compliant=True,
                    notes="Within regulatory compliance"
                )
            )
        db.add_all(water_outlet_logs)

        soil_carbon_logs = [
            SoilCarbonLog(
                log_date=today - timedelta(days=60),
                field_id="F-001",
                field_name="Main Field 1",
                location="North zone",
                soc_pct=1.8,
                sampling_depth_cm=30,
                lab_ref="LAB-2024-156"
            ),
            SoilCarbonLog(
                log_date=today - timedelta(days=30),
                field_id="F-001",
                field_name="Main Field 1",
                location="North zone",
                soc_pct=1.95,
                sampling_depth_cm=30,
                lab_ref="LAB-2025-045"
            ),
            SoilCarbonLog(
                log_date=today,
                field_id="F-001",
                field_name="Main Field 1",
                location="North zone",
                soc_pct=2.1,
                sampling_depth_cm=30,
                lab_ref="LAB-2025-089"
            ),
        ]
        db.add_all(soil_carbon_logs)

        pesticide_logs = [
            PesticideApplicationLog(
                application_date=today - timedelta(days=45),
                field_id="GH1",
                field_name="Greenhouse 1",
                active_ingredient="Neem Oil",
                product_name="PureNeem 3% EC",
                quantity_kg=2.5,
                area_ha=0.2,
                ai_per_ha=12.5,
                crop_type="Green Chilli",
                pest_target="Mites, Whiteflies",
                applied_by="Lakshmi Devi"
            ),
            PesticideApplicationLog(
                application_date=today - timedelta(days=20),
                field_id="FC-TUR",
                field_name="Turmeric Field",
                active_ingredient="Carbendazim",
                product_name="Bavistin 50% WP",
                quantity_kg=1.0,
                area_ha=0.5,
                ai_per_ha=2.0,
                crop_type="Turmeric",
                pest_target="Leaf Spot",
                applied_by="Pradeep Singh"
            ),
            PesticideApplicationLog(
                application_date=today - timedelta(days=5),
                field_id="P1",
                field_name="Aquaculture P1",
                active_ingredient="Potassium Permanganate",
                product_name="KMnO4",
                quantity_kg=0.5,
                area_ha=0.0375,
                ai_per_ha=13.3,
                crop_type="Murrel Fish",
                pest_target="Water disinfection",
                applied_by="Suresh Reddy"
            ),
        ]
        db.add_all(pesticide_logs)

        waste_diversion_logs = []
        for month_offset in range(3):
            log_date = today.replace(day=1) - timedelta(days=month_offset*30)
            waste_diversion_logs.append(
                WasteDiversionLog(
                    log_date=log_date,
                    total_waste_kg=500,
                    diverted_kg=490,
                    landfill_kg=10,
                    compost_kg=300,
                    biogas_kg=150,
                    recycled_kg=40,
                    reused_kg=0,
                    diversion_rate_pct=98.0,
                    meets_target=True,
                    notes="Excellent waste management, >95% target met"
                )
            )
        db.add_all(waste_diversion_logs)

        biodiversity_logs = [
            BiodiversityLog(
                survey_date=today - timedelta(days=30),
                survey_type="bird",
                location="Farm perimeter",
                species_count=12,
                individual_count=45,
                indicator_species_present=True,
                surveyor="Ramakrishna",
                weather_conditions="Partly cloudy, 28°C",
                species_detail=[
                    {"name": "Spotted Dove", "count": 8},
                    {"name": "Indian Roller", "count": 6},
                    {"name": "White Wagtail", "count": 12}
                ],
                notes="Healthy bird populations, good habitat"
            ),
            BiodiversityLog(
                survey_date=today - timedelta(days=15),
                survey_type="pollinator",
                location="Flowering zones",
                species_count=8,
                individual_count=120,
                indicator_species_present=True,
                surveyor="Lakshmi Devi",
                weather_conditions="Sunny, 32°C",
                species_detail=[
                    {"name": "Honey Bee", "count": 80},
                    {"name": "Butterfly (Mixed)", "count": 30},
                    {"name": "Beetle", "count": 10}
                ]
            ),
        ]
        db.add_all(biodiversity_logs)

        solar_net_surplus_logs = []
        for i in range(30):
            log_date = today - timedelta(days=i)
            solar_net_surplus_logs.append(
                SolarNetSurplusLog(
                    log_date=log_date,
                    generation_kwh=48 + random.uniform(-5, 5),
                    consumption_kwh=35 + random.uniform(-5, 5),
                    net_surplus_kwh=max(0, (48 - 35) + random.uniform(-3, 3)),
                    grid_export_kwh=random.uniform(8, 15),
                    grid_import_kwh=random.uniform(0, 5),
                    carbon_offset_kg=(max(0, (48 - 35) + random.uniform(-3, 3))) * 0.82,
                    notes="Daily renewable energy surplus tracking"
                )
            )
        db.add_all(solar_net_surplus_logs)

        # ─────────────────────────────────────────────────────────────
        # 14. COMPLIANCE LICENCES (18 records)
        # ─────────────────────────────────────────────────────────────
        licence_data = [
            ("PCB Consent to Operate", "environmental", "Andhra Pradesh Pollution Control Board", "PCB/2023/001", today + timedelta(days=200)),
            ("FSSAI Food Business", "food_safety", "Food Safety Authority of India", "FSSAI/2024/789", today + timedelta(days=100)),
            ("Weights & Measures", "financial", "Department of Weights & Measures", "WM/2024/456", today + timedelta(days=300)),
            ("Pesticide Dealer Registration", "environmental", "Agricultural Department", "PEST/2023/234", today - timedelta(days=30)),
            ("Poultry Farm Registration", "aquaculture", "Animal Husbandry Department", "POULTRY/2023/567", today + timedelta(days=150)),
            ("Fish Farm Registration (State)", "aquaculture", "State Fisheries Department", "FISH-S/2023/890", today + timedelta(days=250)),
            ("Fish Farm Registration (Central)", "aquaculture", "Central Government Ministry", "FISH-C/2023/012", today + timedelta(days=280)),
            ("Groundwater Extraction", "environmental", "Groundwater Board", "GW/2023/345", today + timedelta(days=200)),
            ("Electricity Connection", "financial", "Distribution Company", "ELEC/2023/678", today + timedelta(days=400)),
            ("Fire Safety NOC", "environmental", "Fire Department", "FIRE/2024/901", today + timedelta(days=120)),
            ("Labour Department Registration", "financial", "Department of Labour", "LABOUR/2023/234", today + timedelta(days=180)),
            ("ESIC Registration", "financial", "Employees State Insurance", "ESIC/2023/567", today + timedelta(days=350)),
            ("Provident Fund Registration", "financial", "EPFO", "PF/2023/890", today + timedelta(days=320)),
            ("GST Registration", "financial", "GST Department", "GSTIN/37ABC123", today + timedelta(days=600)),
            ("APEDA Export Certificate", "food_safety", "Agricultural Products Export Agency", "APEDA/2024/012", today + timedelta(days=80)),
            ("Organic Certification", "food_safety", "Organic Certification Body", "ORGANIC/2023/345", today + timedelta(days=250)),
            ("Biosafety Certificate", "environmental", "Institutional Biosafety Committee", "BIO/2024/678", today + timedelta(days=90)),
            ("Environmental Clearance", "environmental", "Ministry of Environment", "ENV/2023/901", today + timedelta(days=500)),
        ]

        licences = []
        for name, category, authority, lic_num, expiry in licence_data:
            licences.append(
                Licence(
                    name=name,
                    category=category,
                    issuing_authority=authority,
                    licence_number=lic_num,
                    cost_inr=random.uniform(5000, 50000),
                    issue_date=expiry - timedelta(days=365),
                    expiry_date=expiry,
                    renewal_date=expiry + timedelta(days=30),
                    status="active" if expiry > today else ("expiring" if (expiry - today).days < 90 else "active"),
                    responsible_person="Ravi Kumar",
                    notes=f"Annual renewal required, expires {expiry.strftime('%Y-%m-%d')}"
                )
            )
        db.add_all(licences)

        db.commit()

        print("\n✅ New modules seeded successfully:")
        print("   • 2 ColdChainShipments (Nellore to Hyderabad/Chennai)")
        print("   • 4 additional Employees (aquaculture, crops, poultry, logistics)")
        print("   • 3 VaccinationSchedules + 2 VaccinationRecords")
        print("   • 2 WaterSources + 2 WaterStorageTanks + 3 IrrigationZones")
        print("   • 1 SolarArray + 1 Inverter + 10 EnergyGenerationLogs + 25 EnergyConsumptionLogs")
        print("   • 12 ReportSchedules (monthly/quarterly/annual mix)")
        print("   • 5 SubsidySchemes + 2 SubsidyApplications")
        print("   • 2 NeighbouringFarms + 2 ConsultingContracts")
        print("   • 3 VisitPackages + 2 VisitorGroups + 3 VisitBookings")
        print("   • 1 ExpansionPhase + 3 ExpansionMilestones + 3 ExpansionCapex")
        print("   • 12 SeasonalTasks (monthly schedule)")
        print("   • 2 SensorCalibrationLogs + 2 BatteryReplacementLogs + 1 CameraFirmwareLog")
        print("   • 4 WaterOutletLogs + 3 SoilCarbonLogs + 3 PesticideApplicationLogs")
        print("   • 3 WasteDiversionLogs + 2 BiodiversityLogs + 30 SolarNetSurplusLogs")
        print("   • 18 Licences (environmental, food safety, labour, financial, organic, compliance)")

    except Exception as e:
        print(f"❌ Error seeding new modules: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    seed_new_modules()
