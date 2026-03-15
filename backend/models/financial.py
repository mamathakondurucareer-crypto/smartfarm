"""Financial management: revenue, expenses, salary, invoices, banking, budgets, cost centers."""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.base import TimestampMixin


class CostCenter(Base, TimestampMixin):
    __tablename__ = "cost_centers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    department: Mapped[str] = mapped_column(String(30), nullable=False)
    budget_annual: Mapped[float] = mapped_column(Float, default=0)
    budget_used: Mapped[float] = mapped_column(Float, default=0)


class RevenueEntry(Base, TimestampMixin):
    __tablename__ = "revenue_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    stream: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    # Streams: aquaculture, greenhouse, vertical_farm, field_crops, poultry_eggs, duck_eggs,
    #          honey, nursery, solar_export, compost, direct_marketing, consulting, agri_tourism
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=0)
    unit: Mapped[Optional[str]] = mapped_column(String(20))
    unit_price: Mapped[float] = mapped_column(Float, default=0)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    gst_amount: Mapped[float] = mapped_column(Float, default=0)
    net_amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_mode: Mapped[str] = mapped_column(String(20), default="bank")  # cash, bank, upi, credit
    payment_status: Mapped[str] = mapped_column(String(20), default="received")
    customer_name: Mapped[Optional[str]] = mapped_column(String(100))
    market: Mapped[Optional[str]] = mapped_column(String(30))
    invoice_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("invoices.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class ExpenseEntry(Base, TimestampMixin):
    __tablename__ = "expense_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    # Categories: feed, seed, fertilizer, chemical, fuel, electricity, water, labour, salary,
    #             maintenance, logistics, packaging, rent, insurance, professional_fees,
    #             office, marketing, technology, miscellaneous
    subcategory: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    gst_amount: Mapped[float] = mapped_column(Float, default=0)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    cost_center_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("cost_centers.id"))
    department: Mapped[str] = mapped_column(String(30), nullable=False)
    vendor: Mapped[Optional[str]] = mapped_column(String(100))
    payment_mode: Mapped[str] = mapped_column(String(20), default="bank")
    payment_status: Mapped[str] = mapped_column(String(20), default="paid")
    bill_number: Mapped[Optional[str]] = mapped_column(String(30))
    po_number: Mapped[Optional[str]] = mapped_column(String(20))
    approved_by: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class SalaryRecord(Base, TimestampMixin):
    __tablename__ = "salary_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    working_days: Mapped[int] = mapped_column(Integer, nullable=False)
    present_days: Mapped[int] = mapped_column(Integer, nullable=False)
    overtime_hours: Mapped[float] = mapped_column(Float, default=0)
    basic_salary: Mapped[float] = mapped_column(Float, nullable=False)
    hra: Mapped[float] = mapped_column(Float, default=0)
    overtime_pay: Mapped[float] = mapped_column(Float, default=0)
    bonus: Mapped[float] = mapped_column(Float, default=0)
    allowances: Mapped[float] = mapped_column(Float, default=0)
    gross_salary: Mapped[float] = mapped_column(Float, nullable=False)
    pf_deduction: Mapped[float] = mapped_column(Float, default=0)
    esi_deduction: Mapped[float] = mapped_column(Float, default=0)
    tds: Mapped[float] = mapped_column(Float, default=0)
    other_deductions: Mapped[float] = mapped_column(Float, default=0)
    advance_recovery: Mapped[float] = mapped_column(Float, default=0)
    total_deductions: Mapped[float] = mapped_column(Float, default=0)
    net_salary: Mapped[float] = mapped_column(Float, nullable=False)
    payment_date: Mapped[Optional[date]] = mapped_column(Date)
    payment_mode: Mapped[str] = mapped_column(String(20), default="bank_transfer")
    transaction_ref: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, processed, paid


class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    invoice_type: Mapped[str] = mapped_column(String(20), nullable=False)  # sales, purchase
    customer_id: Mapped[Optional[int]] = mapped_column(Integer)
    supplier_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("suppliers.id"))
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    cgst: Mapped[float] = mapped_column(Float, default=0)
    sgst: Mapped[float] = mapped_column(Float, default=0)
    igst: Mapped[float] = mapped_column(Float, default=0)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    amount_paid: Mapped[float] = mapped_column(Float, default=0)
    balance_due: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, sent, paid, overdue, cancelled
    notes: Mapped[Optional[str]] = mapped_column(Text)

    items: Mapped[List["InvoiceItem"]] = relationship("InvoiceItem", back_populates="invoice")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    hsn_code: Mapped[Optional[str]] = mapped_column(String(10))
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    gst_rate: Mapped[float] = mapped_column(Float, default=0)
    total: Mapped[float] = mapped_column(Float, nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")


class BankTransaction(Base, TimestampMixin):
    __tablename__ = "bank_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)  # credit, debit
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    balance_after: Mapped[float] = mapped_column(Float, nullable=False)
    reference_number: Mapped[Optional[str]] = mapped_column(String(50))
    counterparty: Mapped[Optional[str]] = mapped_column(String(100))
    reconciled: Mapped[bool] = mapped_column(Boolean, default=False)
    revenue_entry_id: Mapped[Optional[int]] = mapped_column(Integer)
    expense_entry_id: Mapped[Optional[int]] = mapped_column(Integer)


class Budget(Base, TimestampMixin):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False)  # 2026-27
    department: Mapped[str] = mapped_column(String(30), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    budgeted_amount: Mapped[float] = mapped_column(Float, nullable=False)
    actual_amount: Mapped[float] = mapped_column(Float, default=0)
    variance: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text)
