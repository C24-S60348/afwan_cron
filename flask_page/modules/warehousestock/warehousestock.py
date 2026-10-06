import os
import io
import csv
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, Response, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import func
from .models import db, User, Customer, Item, ItemStock, ProductionPlan, StockMovement, DailyStockRecord, DeliverySchedule

_MODULE_DIR = os.path.dirname(__file__)
_STATIC_DIR = os.path.join(_MODULE_DIR, 'static')
_TEMPLATES_DIR = os.path.join(_MODULE_DIR, 'templates')
_DB_PATH = os.path.join(_MODULE_DIR, 'instance', 'warehouse.db')

warehousestock_bp = Blueprint(
    'warehousestock',
    __name__,
    url_prefix='/warehousestock',
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)

login_manager = LoginManager()
login_manager.login_view = 'warehousestock.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


def init_warehousestock(app):
    """
    Initializes SQLAlchemy, Flask-Login, Jinja helpers, and ensures tables are seeded.
    Called from afwanhaziqmy.py app context on startup.
    """
    os.makedirs(os.path.join(_MODULE_DIR, 'instance'), exist_ok=True)

    app.config.setdefault('SQLALCHEMY_DATABASE_URI', f'sqlite:///{_DB_PATH}')
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    # Initialize extensions
    if 'sqlalchemy' not in app.extensions:
        db.init_app(app)

    if not hasattr(app, 'login_manager'):
        login_manager.init_app(app)
        app.login_manager = login_manager

    # Jinja filter for number formatting
    if 'format_num' not in app.jinja_env.filters:
        @app.template_filter('format_num')
        def format_num(val):
            if val is None or val == '':
                return '-'
            try:
                f = float(val)
                if f.is_integer():
                    return f"{int(f):,}"
                return f"{f:,.2f}"
            except (ValueError, TypeError):
                return str(val)

    # Scoped Context Processor for warehouse pages
    @app.context_processor
    def inject_warehousestock_vars():
        if not (request.path.startswith('/warehousestock') or request.path.startswith('/warehouse')):
            return {}
        try:
            critical_count = ProductionPlan.query.filter_by(status='CRITICAL_SHORTAGE').count()
            total_items = ItemStock.query.count()
        except Exception:
            critical_count = 0
            total_items = 0
        return {
            'app_title': 'WIP Warehouse Management System',
            'critical_shortages_count': critical_count,
            'total_items_count': total_items,
            'current_year': 2026
        }

    # Redirect convenience route: /warehouse -> /warehousestock
    @app.route('/warehouse', methods=['GET'])
    @app.route('/warehouse/<path:subpath>', methods=['GET', 'POST'])
    def warehouse_redirect(subpath=''):
        target = '/warehousestock' + (f'/{subpath}' if subpath else '')
        if request.query_string:
            target += '?' + request.query_string.decode('utf-8')
        return redirect(target)

    # Ensure tables exist and default users are seeded
    with app.app_context():
        db.create_all()
        try:
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', email='admin@warehouse.local', role='Admin', full_name='System Admin')
                admin.set_password('adminpassword123')
                manager = User(username='manager', email='manager@warehouse.local', role='Manager', full_name='Operations Manager')
                manager.set_password('manager123')
                operator = User(username='operator', email='operator@warehouse.local', role='Operator', full_name='Floor Operator')
                operator.set_password('operator123')
                db.session.add_all([admin, manager, operator])
                db.session.commit()
                print("  ✅ [warehousestock] Default users created.")
        except Exception as e:
            app.logger.warning(f"  ⚠️ [warehousestock] User check error: {e}")

    print(f"  ✅ [warehousestock] Database ready at {_DB_PATH}")


# ─────────────────────────────────────────────────────────────────────────────
# Authentication Routes
# ─────────────────────────────────────────────────────────────────────────────

@warehousestock_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('warehousestock.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Contact an administrator.', 'danger')
                return render_template('warehousestock/auth/login.html')

            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username} ({user.role})!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('warehousestock.index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('warehousestock/auth/login.html')


@warehousestock_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('warehousestock.login'))


@warehousestock_bp.route('/profile')
@login_required
def profile():
    return render_template('warehousestock/auth/profile.html', user=current_user)


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard Routes
# ─────────────────────────────────────────────────────────────────────────────

@warehousestock_bp.route('/')
@warehousestock_bp.route('/dashboard')
@login_required
def index():
    # Overall KPI metrics
    total_items = Item.query.count()
    total_customers = Customer.query.count()

    # Aggregates from ItemStock
    stock_totals = db.session.query(
        func.coalesce(func.sum(ItemStock.total_ctn), 0).label('total_ctn'),
        func.coalesce(func.sum(ItemStock.total_kpcs), 0).label('total_kpcs'),
        func.coalesce(func.sum(ItemStock.warehouse_ctn), 0).label('warehouse'),
        func.coalesce(func.sum(ItemStock.heating_ctn), 0).label('heating'),
        func.coalesce(func.sum(ItemStock.qa_transit_ctn), 0).label('qa_transit'),
        func.coalesce(func.sum(ItemStock.return_qa_ctn), 0).label('return_qa'),
        func.coalesce(func.sum(ItemStock.wash_area_ctn), 0).label('wash_area'),
        func.coalesce(func.sum(ItemStock.qa_area_ctn), 0).label('qa_area'),
        func.coalesce(func.sum(ItemStock.production_ctn), 0).label('production'),
        func.coalesce(func.sum(ItemStock.finished_goods_ctn), 0).label('finished_goods'),
        func.coalesce(func.sum(ItemStock.ng_disposed_ctn), 0).label('ng_disposed'),
    ).first()

    # Shortage stats
    critical_shortages = ProductionPlan.query.filter_by(status='CRITICAL_SHORTAGE')\
        .join(Item).order_by(ProductionPlan.shortage_kpcs.asc()).limit(8).all()
    critical_count = ProductionPlan.query.filter_by(status='CRITICAL_SHORTAGE').count()
    low_count = ProductionPlan.query.filter_by(status='LOW').count()

    # Customer breakdown
    customer_stocks = db.session.query(
        Customer.name,
        func.count(Item.id).label('item_count'),
        func.coalesce(func.sum(ItemStock.total_ctn), 0).label('ctn_sum'),
        func.coalesce(func.sum(ItemStock.total_kpcs), 0).label('kpcs_sum')
    ).join(Item, Customer.id == Item.customer_id)\
     .outerjoin(ItemStock, Item.id == ItemStock.item_id)\
     .group_by(Customer.id, Customer.name).all()

    # Recent transactions
    recent_movements = StockMovement.query.order_by(StockMovement.created_at.desc()).limit(10).all()

    return render_template(
        'warehousestock/dashboard/index.html',
        total_items=total_items,
        total_customers=total_customers,
        stock_totals=stock_totals,
        critical_shortages=critical_shortages,
        critical_count=critical_count,
        low_count=low_count,
        customer_stocks=customer_stocks,
        recent_movements=recent_movements
    )


# ─────────────────────────────────────────────────────────────────────────────
# Stock Control Matrix Routes
# ─────────────────────────────────────────────────────────────────────────────

@warehousestock_bp.route('/stock-control')
@login_required
def stock_control():
    customer_id = request.args.get('customer_id', type=int)
    search = request.args.get('search', '').strip()
    channel_filter = request.args.get('channel', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 25

    query = Item.query.join(ItemStock)

    if customer_id:
        query = query.filter(Item.customer_id == customer_id)
    if search:
        query = query.filter(Item.part_no.ilike(f'%{search}%'))

    if channel_filter == 'warehouse':
        query = query.filter(ItemStock.warehouse_ctn > 0)
    elif channel_filter == 'qa_transit':
        query = query.filter(ItemStock.qa_transit_ctn > 0)
    elif channel_filter == 'wash_area':
        query = query.filter(ItemStock.wash_area_ctn > 0)
    elif channel_filter == 'qa_area':
        query = query.filter(ItemStock.qa_area_ctn > 0)
    elif channel_filter == 'production':
        query = query.filter(ItemStock.production_ctn > 0)
    elif channel_filter == 'finished_goods':
        query = query.filter(ItemStock.finished_goods_ctn > 0)
    elif channel_filter == 'ng_disposed':
        query = query.filter(ItemStock.ng_disposed_ctn > 0)

    pagination = query.order_by(Item.part_no.asc()).paginate(page=page, per_page=per_page, error_out=False)
    customers = Customer.query.order_by(Customer.name).all()

    return render_template(
        'warehousestock/stock_control/index.html',
        pagination=pagination,
        items=pagination.items,
        customers=customers,
        selected_customer_id=customer_id,
        search=search,
        channel_filter=channel_filter
    )


@warehousestock_bp.route('/stock-control/transfer', methods=['POST'])
@login_required
def stock_transfer():
    item_id = request.form.get('item_id', type=int)
    source_stage = request.form.get('source_stage')
    dest_stage = request.form.get('dest_stage')
    qty = request.form.get('qty', type=float)
    reference = request.form.get('reference', '')
    notes = request.form.get('notes', '')

    if not item_id or not source_stage or not dest_stage or not qty or qty <= 0:
        flash('Invalid transfer details provided. Please check all fields.', 'warning')
        return redirect(url_for('warehousestock.stock_control'))

    item = Item.query.get_or_404(item_id)
    stock = item.stock

    stage_attr_map = {
        'Warehouse': 'warehouse_ctn',
        'QA transit': 'qa_transit_ctn',
        'Return QA': 'return_qa_ctn',
        'Wash area': 'wash_area_ctn',
        'QA area': 'qa_area_ctn',
        'Production': 'production_ctn',
        'Finished Goods': 'finished_goods_ctn',
        'Delivery': 'delivery_ctn',
        'NG - disposed': 'ng_disposed_ctn'
    }

    src_attr = stage_attr_map.get(source_stage)
    dst_attr = stage_attr_map.get(dest_stage)

    if not src_attr or not dst_attr:
        flash('Unknown stage channel selected.', 'danger')
        return redirect(url_for('warehousestock.stock_control'))

    src_val = getattr(stock, src_attr, 0.0) or 0.0
    if src_val < qty and source_stage != 'Production':
        flash(f'Insufficient stock in {source_stage}! Current: {src_val} ctn, Requested: {qty} ctn.', 'danger')
        return redirect(url_for('warehousestock.stock_control'))

    # Update stocks
    setattr(stock, src_attr, max(0.0, src_val - qty))
    dst_val = getattr(stock, dst_attr, 0.0) or 0.0
    setattr(stock, dst_attr, dst_val + qty)
    stock.recalculate(item.std_pkg)

    # Log movement
    movement = StockMovement(
        item_id=item.id,
        user_id=current_user.id,
        movement_type='TRANSFER',
        source_stage=source_stage,
        dest_stage=dest_stage,
        ctn_qty=qty,
        kpcs_qty=round(qty * (item.std_pkg or 1.0), 2),
        reference_no=reference,
        notes=notes
    )
    db.session.add(movement)
    db.session.commit()

    flash(f'Successfully transferred {qty} ctn of {item.part_no} from {source_stage} to {dest_stage}.', 'success')
    return redirect(url_for('warehousestock.stock_control'))


# ─────────────────────────────────────────────────────────────────────────────
# Master Stock Catalogue Routes
# ─────────────────────────────────────────────────────────────────────────────

@warehousestock_bp.route('/master-stock')
@login_required
def master_stock():
    customer_id = request.args.get('customer_id', type=int)
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 25

    query = Item.query.join(ItemStock).outerjoin(Customer)

    if customer_id:
        query = query.filter(Item.customer_id == customer_id)
    if search:
        query = query.filter(
            (Item.part_no.ilike(f'%{search}%')) |
            (Item.delivery_part_no.ilike(f'%{search}%')) |
            (Item.mc_number.ilike(f'%{search}%'))
        )

    pagination = query.order_by(Item.part_no.asc()).paginate(page=page, per_page=per_page, error_out=False)
    customers = Customer.query.order_by(Customer.name).all()

    return render_template(
        'warehousestock/master_stock/index.html',
        pagination=pagination,
        items=pagination.items,
        customers=customers,
        selected_customer_id=customer_id,
        search=search
    )


@warehousestock_bp.route('/master-stock/add-item', methods=['POST'])
@login_required
def add_item():
    part_no = request.form.get('part_no', '').strip()
    delivery_part_no = request.form.get('delivery_part_no', '').strip()
    customer_id = request.form.get('customer_id', type=int)
    std_pkg = request.form.get('std_pkg', type=float) or 1.0
    mc_number = request.form.get('mc_number', '').strip()
    material_size = request.form.get('material_size', '').strip()
    initial_ctn = request.form.get('initial_ctn', type=float) or 0.0

    if not part_no or not customer_id:
        flash('Part Number and Customer are required.', 'danger')
        return redirect(url_for('warehousestock.master_stock'))

    existing = Item.query.filter_by(part_no=part_no).first()
    if existing:
        flash(f'Item with Part No "{part_no}" already exists!', 'warning')
        return redirect(url_for('warehousestock.master_stock'))

    item = Item(
        part_no=part_no,
        delivery_part_no=delivery_part_no,
        customer_id=customer_id,
        std_pkg=std_pkg,
        mc_number=mc_number,
        material_size=material_size
    )
    db.session.add(item)
    db.session.flush()

    stock = ItemStock(
        item_id=item.id,
        warehouse_ctn=initial_ctn,
        total_ctn=initial_ctn,
        total_kpcs=round(initial_ctn * std_pkg, 2)
    )
    db.session.add(stock)

    plan = ProductionPlan(
        item_id=item.id,
        closing_ctn=initial_ctn,
        closing_kpcs=round(initial_ctn * std_pkg, 2)
    )
    db.session.add(plan)
    db.session.commit()

    flash(f'New item {part_no} created successfully.', 'success')
    return redirect(url_for('warehousestock.master_stock'))


@warehousestock_bp.route('/master-stock/adjust-stock', methods=['POST'])
@login_required
def adjust_stock():
    item_id = request.form.get('item_id', type=int)
    warehouse_ctn = request.form.get('warehouse_ctn', type=float)
    notes = request.form.get('notes', 'Manual Stock Adjustment')

    item = Item.query.get_or_404(item_id)
    stock = item.stock

    old_wh = stock.warehouse_ctn
    stock.warehouse_ctn = max(0.0, warehouse_ctn or 0.0)
    stock.recalculate(item.std_pkg)

    diff = stock.warehouse_ctn - old_wh
    movement = StockMovement(
        item_id=item.id,
        user_id=current_user.id,
        movement_type='ADJUSTMENT',
        source_stage='Audit',
        dest_stage='Warehouse',
        ctn_qty=diff,
        kpcs_qty=round(diff * (item.std_pkg or 1.0), 2),
        reference_no='AUDIT-ADJ',
        notes=notes
    )
    db.session.add(movement)
    db.session.commit()

    flash(f'Stock adjusted for {item.part_no}. Warehouse cartons now: {stock.warehouse_ctn}.', 'success')
    return redirect(url_for('warehousestock.master_stock'))


@warehousestock_bp.route('/master-stock/export')
@login_required
def export_csv():
    items = Item.query.join(ItemStock).outerjoin(Customer).order_by(Item.part_no.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Customer', 'Part No', 'Delivery Part No', 'STD PKG', 'Machine No',
        'Material Size', 'Warehouse (ctn)', 'Total (ctn)', 'Total (kpcs)'
    ])

    for it in items:
        writer.writerow([
            it.customer.name if it.customer else '',
            it.part_no,
            it.delivery_part_no or '',
            it.std_pkg,
            it.mc_number or '',
            it.material_size or '',
            it.stock.warehouse_ctn if it.stock else 0,
            it.stock.total_ctn if it.stock else 0,
            it.stock.total_kpcs if it.stock else 0,
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=master_stock_export.csv'}
    )


# ─────────────────────────────────────────────────────────────────────────────
# Machine Planning & Shortages Routes
# ─────────────────────────────────────────────────────────────────────────────

@warehousestock_bp.route('/mc-plan')
@login_required
def mc_plan():
    customer_id = request.args.get('customer_id', type=int)
    mc_number = request.args.get('mc_number', '').strip()
    status_filter = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 25

    query = ProductionPlan.query.join(Item).outerjoin(Customer)

    if customer_id:
        query = query.filter(Item.customer_id == customer_id)
    if mc_number:
        query = query.filter(Item.mc_number == mc_number)
    if status_filter:
        query = query.filter(ProductionPlan.status == status_filter)
    if search:
        query = query.filter(
            (Item.part_no.ilike(f'%{search}%')) |
            (Item.material_size.ilike(f'%{search}%'))
        )

    pagination = query.order_by(ProductionPlan.shortage_kpcs.asc()).paginate(page=page, per_page=per_page, error_out=False)

    customers = Customer.query.order_by(Customer.name).all()
    machine_numbers = [m[0] for m in db.session.query(Item.mc_number).filter(Item.mc_number.isnot(None), Item.mc_number != '').distinct().order_by(Item.mc_number).all()]

    total_planned = ProductionPlan.query.count()
    critical_count = ProductionPlan.query.filter_by(status='CRITICAL_SHORTAGE').count()
    low_count = ProductionPlan.query.filter_by(status='LOW').count()
    normal_count = ProductionPlan.query.filter_by(status='NORMAL').count()

    return render_template(
        'warehousestock/mc_plan/index.html',
        pagination=pagination,
        plans=pagination.items,
        customers=customers,
        machine_numbers=machine_numbers,
        selected_customer_id=customer_id,
        selected_mc=mc_number,
        selected_status=status_filter,
        search=search,
        total_planned=total_planned,
        critical_count=critical_count,
        low_count=low_count,
        normal_count=normal_count
    )


@warehousestock_bp.route('/mc-plan/update', methods=['POST'])
@login_required
def update_plan():
    plan_id = request.form.get('plan_id', type=int)
    closing_ctn = request.form.get('closing_ctn', type=float)
    forecast_m1 = request.form.get('forecast_m1', type=float)
    forecast_m2 = request.form.get('forecast_m2', type=float)
    notes = request.form.get('notes', '')

    plan = ProductionPlan.query.get_or_404(plan_id)
    item = plan.item

    if closing_ctn is not None:
        plan.closing_ctn = closing_ctn
        plan.closing_kpcs = round(closing_ctn * (item.std_pkg or 1.0), 2)
    if forecast_m1 is not None:
        plan.forecast_month1 = forecast_m1
    if forecast_m2 is not None:
        plan.forecast_month2 = forecast_m2
    if notes:
        plan.notes = notes

    plan.calculate_shortage(item.std_pkg)
    db.session.commit()

    flash(f'Production plan updated for {item.part_no}. Shortage status: {plan.status}.', 'success')
    return redirect(url_for('warehousestock.mc_plan'))


# ─────────────────────────────────────────────────────────────────────────────
# Washing & QA Management Routes
# ─────────────────────────────────────────────────────────────────────────────

@warehousestock_bp.route('/washing-qa')
@login_required
def washing_qa():
    customer_id = request.args.get('customer_id', type=int)
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 25

    query = Item.query.join(ItemStock)

    if customer_id:
        query = query.filter(Item.customer_id == customer_id)
    if search:
        query = query.filter(Item.part_no.ilike(f'%{search}%'))

    pagination = query.order_by(Item.part_no.asc()).paginate(page=page, per_page=per_page, error_out=False)
    customers = Customer.query.order_by(Customer.name).all()

    wash_total = db.session.query(db.func.sum(ItemStock.wash_area_ctn)).scalar() or 0
    qa_total = db.session.query(db.func.sum(ItemStock.qa_area_ctn)).scalar() or 0
    transit_total = db.session.query(db.func.sum(ItemStock.qa_transit_ctn)).scalar() or 0
    return_qa_total = db.session.query(db.func.sum(ItemStock.return_qa_ctn)).scalar() or 0
    ng_total = db.session.query(db.func.sum(ItemStock.ng_disposed_ctn)).scalar() or 0

    return render_template(
        'warehousestock/washing_qa/index.html',
        pagination=pagination,
        items=pagination.items,
        customers=customers,
        selected_customer_id=customer_id,
        search=search,
        wash_total=wash_total,
        qa_total=qa_total,
        transit_total=transit_total,
        return_qa_total=return_qa_total,
        ng_total=ng_total
    )


@warehousestock_bp.route('/washing-qa/action', methods=['POST'])
@login_required
def washing_qa_action():
    item_id = request.form.get('item_id', type=int)
    action_type = request.form.get('action_type')
    qty = request.form.get('qty', type=float)
    notes = request.form.get('notes', '')

    if not item_id or not qty or qty <= 0:
        flash('Invalid quantity or item.', 'warning')
        return redirect(url_for('warehousestock.washing_qa'))

    item = Item.query.get_or_404(item_id)
    stock = item.stock

    if action_type == 'to_qa':
        if stock.wash_area_ctn < qty:
            flash(f'Insufficient wash area cartons ({stock.wash_area_ctn} available).', 'danger')
            return redirect(url_for('warehousestock.washing_qa'))
        stock.wash_area_ctn -= qty
        stock.qa_area_ctn += qty
        src, dst = 'Wash area', 'QA area'

    elif action_type == 'approve_qa':
        dest_choice = request.form.get('dest_choice', 'QA transit')
        if stock.qa_area_ctn < qty:
            flash(f'Insufficient QA area cartons ({stock.qa_area_ctn} available).', 'danger')
            return redirect(url_for('warehousestock.washing_qa'))
        stock.qa_area_ctn -= qty
        if dest_choice == 'Warehouse':
            stock.warehouse_ctn += qty
            src, dst = 'QA area', 'Warehouse'
        else:
            stock.qa_transit_ctn += qty
            src, dst = 'QA area', 'QA transit'

    elif action_type == 'reject_to_wash':
        if stock.qa_area_ctn < qty:
            flash(f'Insufficient QA area cartons ({stock.qa_area_ctn} available).', 'danger')
            return redirect(url_for('warehousestock.washing_qa'))
        stock.qa_area_ctn -= qty
        stock.return_qa_ctn += qty
        src, dst = 'QA area', 'Return QA'

    elif action_type == 'dispose_ng':
        if stock.qa_area_ctn < qty:
            flash(f'Insufficient QA area cartons ({stock.qa_area_ctn} available).', 'danger')
            return redirect(url_for('warehousestock.washing_qa'))
        stock.qa_area_ctn -= qty
        stock.ng_disposed_ctn += qty
        src, dst = 'QA area', 'NG - disposed'
    else:
        flash('Unknown QA action.', 'danger')
        return redirect(url_for('warehousestock.washing_qa'))

    stock.recalculate(item.std_pkg)
    movement = StockMovement(
        item_id=item.id,
        user_id=current_user.id,
        movement_type='TRANSFER',
        source_stage=src,
        dest_stage=dst,
        ctn_qty=qty,
        kpcs_qty=round(qty * (item.std_pkg or 1.0), 2),
        reference_no='QA-ACTION',
        notes=notes
    )
    db.session.add(movement)
    db.session.commit()

    flash(f'Action completed: {qty} ctn of {item.part_no} moved from {src} to {dst}.', 'success')
    return redirect(url_for('warehousestock.washing_qa'))


# ─────────────────────────────────────────────────────────────────────────────
# Daily Movements Routes
# ─────────────────────────────────────────────────────────────────────────────

@warehousestock_bp.route('/daily-stock')
@login_required
def daily_stock():
    selected_date = request.args.get('date', '').strip()
    customer_id = request.args.get('customer_id', type=int)
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 25

    available_dates = [d[0] for d in db.session.query(DailyStockRecord.record_date).distinct().order_by(DailyStockRecord.record_date.desc()).all()]

    if not selected_date and available_dates:
        selected_date = available_dates[0]

    query = DailyStockRecord.query.join(Item).outerjoin(Customer)

    if selected_date:
        query = query.filter(DailyStockRecord.record_date == selected_date)
    if customer_id:
        query = query.filter(Item.customer_id == customer_id)
    if search:
        query = query.filter(
            (Item.part_no.ilike(f'%{search}%')) |
            (Item.delivery_part_no.ilike(f'%{search}%'))
        )

    pagination = query.order_by(DailyStockRecord.id.asc()).paginate(page=page, per_page=per_page, error_out=False)
    customers = Customer.query.order_by(Customer.name).all()

    deliveries = DeliverySchedule.query.filter(DeliverySchedule.delivery_date.ilike(f'%{selected_date}%')).limit(20).all()

    return render_template(
        'warehousestock/daily_stock/index.html',
        pagination=pagination,
        records=pagination.items,
        available_dates=available_dates,
        selected_date=selected_date,
        customers=customers,
        selected_customer_id=customer_id,
        search=search,
        deliveries=deliveries
    )


@warehousestock_bp.route('/daily-stock/add-movement', methods=['POST'])
@login_required
def daily_stock_add_movement():
    item_id = request.form.get('item_id', type=int)
    movement_type = request.form.get('movement_type')
    qty = request.form.get('qty', type=float)
    target_location = request.form.get('target_location', 'Warehouse')
    date_str = request.form.get('date', datetime.utcnow().strftime('%d.%m.%y'))
    reference = request.form.get('reference', '')
    notes = request.form.get('notes', '')

    if not item_id or not qty or qty <= 0:
        flash('Invalid transaction details.', 'danger')
        return redirect(url_for('warehousestock.daily_stock', date=date_str))

    item = Item.query.get_or_404(item_id)
    stock = item.stock

    loc_map = {
        'HEATING': 'heating_ctn',
        'QA': 'qa_transit_ctn',
        'Warehouse': 'warehouse_ctn'
    }
    field = loc_map.get(target_location, 'warehouse_ctn')
    current_loc_val = getattr(stock, field, 0.0) or 0.0

    if movement_type == 'IN':
        setattr(stock, field, current_loc_val + qty)
        src = 'Vendor / Receiving'
        dst = target_location
    elif movement_type == 'OUT':
        if current_loc_val < qty:
            flash(f'Insufficient stock in {target_location}! Available: {current_loc_val}, Requested: {qty}', 'danger')
            return redirect(url_for('warehousestock.daily_stock', date=date_str))
        setattr(stock, field, current_loc_val - qty)
        src = target_location
        dst = 'Customer Delivery / Outbound'
    else:
        flash('Unknown movement type.', 'danger')
        return redirect(url_for('warehousestock.daily_stock', date=date_str))

    stock.recalculate(item.std_pkg)

    daily_rec = DailyStockRecord(
        item_id=item.id,
        record_date=date_str,
        wh_stock=stock.warehouse_ctn,
        in_qty=qty if movement_type == 'IN' else 0,
        out_qty=qty if movement_type == 'OUT' else 0,
        qty_per_ctn=item.std_pkg,
        heating_ctn=stock.heating_ctn,
        qa_ctn=stock.qa_transit_ctn,
        wh_ctn=stock.warehouse_ctn,
        total_ctn=stock.total_ctn,
        kpcs=stock.total_kpcs,
        notes=f"{movement_type} {qty} ctn: {notes}"
    )
    db.session.add(daily_rec)

    mov = StockMovement(
        item_id=item.id,
        user_id=current_user.id,
        movement_type=movement_type,
        source_stage=src,
        dest_stage=dst,
        ctn_qty=qty,
        kpcs_qty=round(qty * (item.std_pkg or 1.0), 2),
        reference_no=reference,
        notes=notes
    )
    db.session.add(mov)
    db.session.commit()

    flash(f'Logged {movement_type} of {qty} ctn for {item.part_no} on {date_str}.', 'success')
    return redirect(url_for('warehousestock.daily_stock', date=date_str))


# ─────────────────────────────────────────────────────────────────────────────
# JSON APIs
# ─────────────────────────────────────────────────────────────────────────────

@warehousestock_bp.route('/api/stats')
@login_required
def api_stats():
    stock_totals = db.session.query(
        db.func.coalesce(db.func.sum(ItemStock.warehouse_ctn), 0),
        db.func.coalesce(db.func.sum(ItemStock.heating_ctn), 0),
        db.func.coalesce(db.func.sum(ItemStock.qa_transit_ctn), 0),
        db.func.coalesce(db.func.sum(ItemStock.return_qa_ctn), 0),
        db.func.coalesce(db.func.sum(ItemStock.wash_area_ctn), 0),
        db.func.coalesce(db.func.sum(ItemStock.qa_area_ctn), 0),
        db.func.coalesce(db.func.sum(ItemStock.production_ctn), 0),
        db.func.coalesce(db.func.sum(ItemStock.finished_goods_ctn), 0),
    ).first()

    labels = ['Warehouse', 'Heating', 'QA Transit', 'Return QA', 'Wash Area', 'QA Area', 'Production', 'Finished Goods']
    data = [float(v) for v in stock_totals]

    return jsonify({
        'labels': labels,
        'data': data
    })


@warehousestock_bp.route('/api/items/search')
@login_required
def api_search_items():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    items = Item.query.filter(
        (Item.part_no.ilike(f'%{q}%')) |
        (Item.delivery_part_no.ilike(f'%{q}%'))
    ).limit(20).all()

    return jsonify([{
        'id': it.id,
        'part_no': it.part_no,
        'customer': it.customer.name if it.customer else '',
        'std_pkg': it.std_pkg,
        'mc_number': it.mc_number or '',
        'warehouse_ctn': it.stock.warehouse_ctn if it.stock else 0,
        'total_ctn': it.stock.total_ctn if it.stock else 0
    } for it in items])


# ─────────────────────────────────────────────────────────────────────────────
# Reference Guide / Documentation
# ─────────────────────────────────────────────────────────────────────────────

@warehousestock_bp.route('/instructions')
@warehousestock_bp.route('/mysecretinstructions')
def secret_instructions():
    return render_template('warehousestock/secret_instructions.html')
