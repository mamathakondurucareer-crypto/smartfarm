"""Market prices, customers, orders, and shipment endpoints."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.market import MarketPrice, Customer, CustomerOrder, OrderItem, Shipment, ShipmentItem
from backend.schemas import MarketPriceCreate, CustomerCreate, OrderCreate, ShipmentCreate
from backend.utils.helpers import generate_code

router = APIRouter(prefix="/api/market", tags=["Market & Sales"])


# ── Market Prices ──
@router.post("/prices", status_code=201)
def record_price(data: MarketPriceCreate, db: Session = Depends(get_db)):
    price = MarketPrice(**data.model_dump())
    db.add(price)
    db.commit()
    return {"id": price.id}


@router.get("/prices")
def list_prices(
    market_city: Optional[str] = None,
    product: Optional[str] = None,
    start_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    q = db.query(MarketPrice)
    if market_city:
        q = q.filter(MarketPrice.market_city == market_city)
    if product:
        q = q.filter(MarketPrice.product == product)
    if start_date:
        q = q.filter(MarketPrice.recorded_date >= start_date)
    return q.order_by(MarketPrice.recorded_date.desc()).limit(200).all()


@router.get("/prices/latest")
def latest_prices(db: Session = Depends(get_db)):
    """Get latest price per product per city."""
    subq = db.query(
        MarketPrice.market_city, MarketPrice.product,
        func.max(MarketPrice.recorded_date).label("max_date")
    ).group_by(MarketPrice.market_city, MarketPrice.product).subquery()

    results = db.query(MarketPrice).join(
        subq,
        (MarketPrice.market_city == subq.c.market_city) &
        (MarketPrice.product == subq.c.product) &
        (MarketPrice.recorded_date == subq.c.max_date)
    ).all()
    return results


# ── Customers ──
@router.get("/customers")
def list_customers(city: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Customer).filter(Customer.is_active == True)
    if city:
        q = q.filter(Customer.city == city)
    return q.order_by(Customer.name).all()


@router.post("/customers", status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    c = Customer(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


# ── Orders ──
@router.post("/orders", status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    count = db.query(func.count(CustomerOrder.id)).scalar()
    order = CustomerOrder(
        order_number=generate_code("ORD", count + 1),
        customer_id=data.customer_id,
        order_date=data.order_date,
        delivery_date=data.delivery_date,
        delivery_city=data.delivery_city,
        total_amount=0,
    )
    db.add(order)
    db.flush()

    subtotal = 0
    gst_total = 0
    for item_data in data.items:
        total = item_data.quantity * item_data.unit_price
        gst = total * item_data.gst_rate / 100
        oi = OrderItem(
            order_id=order.id, product=item_data.product,
            category=item_data.category, quantity=item_data.quantity,
            unit=item_data.unit, unit_price=item_data.unit_price,
            gst_rate=item_data.gst_rate, total=total + gst,
        )
        db.add(oi)
        subtotal += total
        gst_total += gst

    order.subtotal = subtotal
    order.gst_amount = gst_total
    order.total_amount = subtotal + gst_total
    db.commit()
    db.refresh(order)
    return {"order_number": order.order_number, "total_amount": order.total_amount}


@router.get("/orders")
def list_orders(status: Optional[str] = None, city: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(CustomerOrder)
    if status:
        q = q.filter(CustomerOrder.order_status == status)
    if city:
        q = q.filter(CustomerOrder.delivery_city == city)
    return q.order_by(CustomerOrder.order_date.desc()).limit(100).all()


@router.put("/orders/{order_id}/status")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(CustomerOrder).filter(CustomerOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    order.order_status = status
    db.commit()
    return {"message": f"Order {order.order_number} updated to {status}"}


# ── Shipments ──
@router.post("/shipments", status_code=201)
def create_shipment(data: ShipmentCreate, db: Session = Depends(get_db)):
    from backend.utils.constants import MARKETS
    count = db.query(func.count(Shipment.id)).scalar()
    distance = MARKETS.get(data.destination_city.lower(), {}).get("distance_km", 0)
    shipment = Shipment(
        shipment_number=generate_code("SHP", count + 1),
        order_id=data.order_id,
        dispatch_date=data.dispatch_date,
        destination_city=data.destination_city,
        vehicle_number=data.vehicle_number,
        driver_name=data.driver_name,
        driver_phone=data.driver_phone,
        transport_mode=data.transport_mode,
        cold_chain=data.cold_chain,
        distance_km=distance,
    )
    db.add(shipment)
    db.flush()

    total_weight = 0
    for si_data in data.items:
        si = ShipmentItem(
            shipment_id=shipment.id, product=si_data.product,
            quantity=si_data.quantity, unit=si_data.unit,
            weight_kg=si_data.weight_kg, packaging=si_data.packaging,
        )
        db.add(si)
        total_weight += si_data.weight_kg

    shipment.total_weight_kg = total_weight
    # Update order status
    order = db.query(CustomerOrder).filter(CustomerOrder.id == data.order_id).first()
    if order:
        order.order_status = "shipped"
    db.commit()
    db.refresh(shipment)
    return {"shipment_number": shipment.shipment_number, "total_weight_kg": total_weight}


@router.get("/shipments")
def list_shipments(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Shipment)
    if status:
        q = q.filter(Shipment.status == status)
    return q.order_by(Shipment.dispatch_date.desc()).limit(50).all()


@router.put("/shipments/{shipment_id}/deliver")
def mark_delivered(shipment_id: int, db: Session = Depends(get_db)):
    from datetime import datetime, timezone
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(404, "Shipment not found")
    shipment.status = "delivered"
    shipment.actual_delivery = datetime.now(timezone.utc)
    order = db.query(CustomerOrder).filter(CustomerOrder.id == shipment.order_id).first()
    if order:
        order.order_status = "delivered"
    db.commit()
    return {"message": "Shipment marked as delivered"}
