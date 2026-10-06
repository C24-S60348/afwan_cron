from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), default='Manager')  # Admin, Manager, Operator, QA
    full_name = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    code = db.Column(db.String(32), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('Item', backref='customer', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Customer {self.name}>'


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    part_no = db.Column(db.String(100), nullable=False, index=True)
    delivery_part_no = db.Column(db.String(100), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    std_pkg = db.Column(db.Float, default=1.0)
    mc_number = db.Column(db.String(64), nullable=True, index=True)
    material_size = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    stock = db.relationship('ItemStock', backref='item', uselist=False, cascade='all, delete-orphan')
    production_plan = db.relationship('ProductionPlan', backref='item', uselist=False, cascade='all, delete-orphan')
    daily_records = db.relationship('DailyStockRecord', backref='item', lazy='dynamic', cascade='all, delete-orphan')
    movements = db.relationship('StockMovement', backref='item', lazy='dynamic', cascade='all, delete-orphan')
    delivery_schedules = db.relationship('DeliverySchedule', backref='item', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Item {self.part_no}>'


class ItemStock(db.Model):
    __tablename__ = 'item_stocks'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, unique=True, index=True)
    
    # Cartons in different WIP / Warehouse channels
    warehouse_ctn = db.Column(db.Float, default=0.0)
    heating_ctn = db.Column(db.Float, default=0.0)
    qa_transit_ctn = db.Column(db.Float, default=0.0)
    return_qa_ctn = db.Column(db.Float, default=0.0)
    wash_area_ctn = db.Column(db.Float, default=0.0)
    qa_area_ctn = db.Column(db.Float, default=0.0)
    production_ctn = db.Column(db.Float, default=0.0)
    delivery_ctn = db.Column(db.Float, default=0.0)
    ng_disposed_ctn = db.Column(db.Float, default=0.0)
    finished_goods_ctn = db.Column(db.Float, default=0.0)
    
    # Aggregates
    total_ctn = db.Column(db.Float, default=0.0)
    total_kpcs = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def recalculate(self, std_pkg=None):
        if std_pkg is None:
            std_pkg = self.item.std_pkg if self.item else 1.0
        self.total_ctn = (
            (self.warehouse_ctn or 0) +
            (self.heating_ctn or 0) +
            (self.qa_transit_ctn or 0) +
            (self.wash_area_ctn or 0) +
            (self.qa_area_ctn or 0) +
            (self.production_ctn or 0) +
            (self.finished_goods_ctn or 0)
        )
        self.total_kpcs = round(self.total_ctn * (std_pkg or 1.0), 2)


class ProductionPlan(db.Model):
    __tablename__ = 'production_plans'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, unique=True, index=True)
    
    closing_ctn = db.Column(db.Float, default=0.0)
    closing_kpcs = db.Column(db.Float, default=0.0)
    forecast_month1 = db.Column(db.Float, default=0.0)
    forecast_month2 = db.Column(db.Float, default=0.0)
    shortage_kpcs = db.Column(db.Float, default=0.0)
    shortage_ctn = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(32), default='NORMAL')  # 'NORMAL', 'LOW', 'CRITICAL_SHORTAGE'
    notes = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_shortage(self, std_pkg=None):
        if std_pkg is None:
            std_pkg = self.item.std_pkg if self.item else 1.0
        target = self.forecast_month1 or 0.0
        available = self.closing_kpcs or 0.0
        self.shortage_kpcs = round(available - target, 2)
        if std_pkg and std_pkg > 0:
            self.shortage_ctn = round(self.shortage_kpcs / std_pkg, 2)
        else:
            self.shortage_ctn = 0.0

        if self.shortage_kpcs < 0:
            self.status = 'CRITICAL_SHORTAGE'
        elif self.shortage_kpcs < (target * 0.2):
            self.status = 'LOW'
        else:
            self.status = 'NORMAL'


class StockMovement(db.Model):
    __tablename__ = 'stock_movements'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    movement_type = db.Column(db.String(32), nullable=False)  # IN, OUT, TRANSFER, ADJUSTMENT
    source_stage = db.Column(db.String(64), nullable=True)
    dest_stage = db.Column(db.String(64), nullable=True)
    ctn_qty = db.Column(db.Float, nullable=False, default=0.0)
    kpcs_qty = db.Column(db.Float, nullable=False, default=0.0)
    reference_no = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', backref='movements')


class DailyStockRecord(db.Model):
    __tablename__ = 'daily_stock_records'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, index=True)
    record_date = db.Column(db.String(32), nullable=False, index=True)  # e.g. "29.04.15" or "2024-06-24"
    wh_stock = db.Column(db.Float, default=0.0)
    in_qty = db.Column(db.Float, default=0.0)
    out_qty = db.Column(db.Float, default=0.0)
    qty_per_ctn = db.Column(db.Float, default=0.0)
    heating_ctn = db.Column(db.Float, default=0.0)
    qa_ctn = db.Column(db.Float, default=0.0)
    wh_ctn = db.Column(db.Float, default=0.0)
    total_ctn = db.Column(db.Float, default=0.0)
    kpcs = db.Column(db.Float, default=0.0)
    notes = db.Column(db.String(255), nullable=True)


class DeliverySchedule(db.Model):
    __tablename__ = 'delivery_schedules'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, index=True)
    delivery_date = db.Column(db.String(32), nullable=False)
    delivery_label = db.Column(db.String(64), nullable=True)  # e.g. "delivery 1 (Monday)"
    pedma_part_no = db.Column(db.String(64), nullable=True)
    stock_qty = db.Column(db.Float, default=0.0)
    deliver_qty = db.Column(db.Float, default=0.0)
    balance_qty = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(32), default='Scheduled')
