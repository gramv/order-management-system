import os
import traceback
from datetime import datetime, timedelta

import pandas as pd

from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, desc, func
from sqlalchemy.orm import joinedload

from werkzeug.utils import secure_filename

from wtforms import StringField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from app import db
from app.main import bp

from app.main.forms import (ProductForm, WholesalerForm, OrderListForm,
                            BulkUploadForm, CustomerOrderForm, CustomerOrderItemForm)
from app.forms import DailySalesForm

from app.models import (User, Product, Wholesaler, OrderList, OrderListItem,
                        CustomerOrder, CustomerOrderItem, DailySales, SalesDocument)

from app.utils.storage import CloudinaryStorage
from flask import render_template
from flask_login import login_required, current_user
from app.main import bp
from app.models import DailySales, OrderList, CustomerOrder, Product, Wholesaler
from sqlalchemy import desc
from datetime import datetime, date
from datetime import datetime, timedelta, date
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, desc, and_, distinct
from sqlalchemy.orm import joinedload
from app import db
from app.main import bp
from app.models import (
    User, Product, Wholesaler, OrderList, OrderListItem, 
    CustomerOrder, CustomerOrderItem, DailySales, SalesDocument
)
from app.utils.storage import CloudinaryStorage
from app.utils.analytics import (
    calculate_sales_metrics,
    analyze_sales_patterns,
    calculate_order_metrics,
    analyze_top_products,
    analyze_wholesaler_performance,
    get_sales_trend_data,
    get_order_trend_data
)
# In app/main/routes.py

# app/main/routes.py

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    today = date.today()
    
    if current_user.role == 'owner':
        try:
            # Today's sales total
            today_sales = DailySales.query.filter_by(date=today).all()
            total_sales = sum(sale.total_actual for sale in today_sales) if today_sales else 0
            
            # Fetch pending orders counts
            daily_orders = OrderList.query.filter_by(type='daily', status='pending').count()
            monthly_orders = OrderList.query.filter_by(type='monthly', status='pending').count()
            pending_orders = f"{daily_orders} / {monthly_orders}"
            
            # Fetch pending customer orders
            customer_orders = CustomerOrder.query.filter_by(status='pending').count()
            
            # Fetch recent discrepancies (last 5 with significant discrepancies)
            recent_discrepancies = DailySales.query\
                .filter(
                    DailySales.date == today,  # Only today's discrepancies
                    DailySales.overall_discrepancy.notin_([-10, 10])
                )\
                .order_by(desc(DailySales.report_time))\
                .limit(5)\
                .all()
            
            # Fetch recent customer orders
            recent_customer_orders = CustomerOrder.query\
                .order_by(desc(CustomerOrder.order_date))\
                .limit(5)\
                .all()
            
            return render_template('main/owner_dashboard.html',
                                 datetime=datetime,
                                 total_sales=total_sales,
                                 pending_orders=pending_orders,
                                 customer_orders=customer_orders,
                                 recent_discrepancies=recent_discrepancies,
                                 recent_customer_orders=recent_customer_orders)
        
        except Exception as e:
            current_app.logger.error(f"Error in owner dashboard: {str(e)}")
            flash('An error occurred while loading the dashboard.', 'error')
            return render_template('main/owner_dashboard.html',
                                 datetime=datetime,
                                 total_sales=0,
                                 pending_orders="0 / 0",
                                 customer_orders=0,
                                 recent_discrepancies=[],
                                 recent_customer_orders=[])
    
    else:  # Employee dashboard
        try:
            # Fetch today's orders
            today_orders = OrderList.query\
                .filter_by(date=today, type='daily')\
                .order_by(desc(OrderList.id))\
                .options(joinedload(OrderList.wholesaler))\
                .limit(5)\
                .all()
            
            # Fetch recent customer orders
            recent_customer_orders = CustomerOrder.query\
                .order_by(desc(CustomerOrder.order_date))\
                .limit(5)\
                .all()
            
            return render_template('main/employee_dashboard.html',
                                 datetime=datetime,
                                 today_orders=today_orders,
                                 recent_customer_orders=recent_customer_orders)
        
        except Exception as e:
            current_app.logger.error(f"Error in employee dashboard: {str(e)}")
            flash('An error occurred while loading the dashboard.', 'error')
            return render_template('main/employee_dashboard.html',
                                 datetime=datetime,
                                 today_orders=[],
                                 recent_customer_orders=[])
        
@bp.route('/daily_orders')
@login_required
def daily_orders():
    orders = OrderList.query.filter_by(type='daily', status='pending').options(
        joinedload(OrderList.items).joinedload(OrderListItem.product)
    ).all()
    return render_template('daily_orders.html', title='Daily Orders', orders=orders)

@bp.route('/monthly_orders')
@login_required
def monthly_orders():
    orders = OrderList.query.filter_by(type='monthly', status='pending').options(
        joinedload(OrderList.items).joinedload(OrderListItem.product)
    ).all()
    return render_template('monthly_orders.html', title='Monthly Orders', orders=orders)

@bp.route('/add_to_order_list', methods=['POST'])
@login_required
def add_to_order_list():
    data = request.json
    try:
        product = Product.query.get(data['product_id'])
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        order_list = OrderList.query.filter_by(
            wholesaler_id=product.wholesaler_id,
            status='pending',
            type=data['order_type']
        ).first()
        
        if not order_list:
            order_list = OrderList(wholesaler_id=product.wholesaler_id, type=data['order_type'])
            db.session.add(order_list)
        
        order_item = OrderListItem(
            order_list=order_list,
            product_id=product.id,
            quantity=data['quantity']
        )
        db.session.add(order_item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Item added to order list'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in add_to_order_list: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while adding the item to the order list'}), 500

@bp.route('/get_daily_orders')
@login_required
def get_daily_orders():
    try:
        daily_orders = OrderList.query.filter_by(type='daily', status='pending').all()
        orders_dict = {}
        for order in daily_orders:
            if order.wholesaler.name not in orders_dict:
                orders_dict[order.wholesaler.name] = []
            for item in order.items:
                orders_dict[order.wholesaler.name].append({
                    'id': item.id,
                    'product_name': item.product.name,
                    'quantity': item.quantity
                })
        return jsonify(orders_dict)
    except Exception as e:
        current_app.logger.error(f"Error in get_daily_orders: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching daily orders'}), 500

@bp.route('/update_order_item', methods=['PUT'])
@login_required
def update_order_item():
    data = request.json
    try:
        item = OrderListItem.query.get(data['item_id'])
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        item.quantity = data['quantity']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item updated successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_order_item: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while updating the item'}), 500

@bp.route('/remove_order_item/<int:item_id>', methods=['DELETE'])
@login_required
def remove_order_item(item_id):
    try:
        item = OrderListItem.query.get(item_id)
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item removed successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in remove_order_item: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while removing the item'}), 500




@bp.route('/get_monthly_orders')
@login_required
def get_monthly_orders():
    try:
        monthly_orders = OrderList.query.filter_by(type='monthly', status='pending').all()
        orders_dict = {}
        for order in monthly_orders:
            if order.wholesaler.name not in orders_dict:
                orders_dict[order.wholesaler.name] = []
            for item in order.items:
                orders_dict[order.wholesaler.name].append({
                    'id': item.id,
                    'product_name': item.product.name,
                    'quantity': item.quantity
                })
        return jsonify(orders_dict)
    except Exception as e:
        current_app.logger.error(f"Error in get_monthly_orders: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching monthly orders'}), 500

from app.main.forms import BulkUploadForm

@bp.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    bulk_form = BulkUploadForm()
    if bulk_form.validate_on_submit():
        file = bulk_form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            products = process_excel_file(file_path)
            for product_data in products:
                product = Product(**product_data)
                db.session.add(product)
            db.session.commit()
            flash(f'{len(products)} products added successfully!', 'success')
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
        finally:
            os.remove(file_path)  # Remove the uploaded file after processing
        
        return redirect(url_for('main.products'))

    try:
        products = Product.query.all()
        return render_template('products.html', title='Products', products=products, bulk_form=bulk_form)
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error in products route: {str(e)}")
        flash(f"An error occurred while retrieving products: {str(e)}")
        return render_template('products.html', title='Products', products=[], bulk_form=bulk_form)


import tempfile
import os
from werkzeug.utils import secure_filename
import pandas as pd

@bp.route('/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    bulk_form = BulkUploadForm()
    
    # Populate the wholesaler choices
    form.wholesaler.choices = [(w.id, w.name) for w in Wholesaler.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            product_id=form.product_id.data,
            name=form.name.data,
            size=form.size.data,
            price=form.price.data,
            wholesaler_id=form.wholesaler.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!')
        return redirect(url_for('main.products'))
    
    if bulk_form.validate_on_submit():
        file = bulk_form.file.data
        if file:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                try:
                    # Save uploaded file to temporary location
                    file.save(temp_file.name)
                    
                    # Process the Excel file
                    products = process_excel_file(temp_file.name)
                    
                    # Add products to database
                    for product_data in products:
                        product = Product(**product_data)
                        db.session.add(product)
                    
                    db.session.commit()
                    flash(f'{len(products)} products added successfully!', 'success')
                    
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f"Error processing file: {str(e)}")
                    flash(f'Error processing file: {str(e)}', 'error')
                finally:
                    # Clean up - remove temporary file
                    os.unlink(temp_file.name)
            
            return redirect(url_for('main.products'))
    
    return render_template('product_form.html', 
                         title='Add Product', 
                         form=form, 
                         bulk_form=bulk_form)

def process_excel_file(file_path):
    try:
        df = pd.read_excel(file_path)
        required_columns = ['product_id', 'name', 'size', 'price', 'wholesaler_id']
        
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Excel file must contain columns: " + ", ".join(required_columns))
        
        products = []
        for _, row in df.iterrows():
            try:
                wholesaler = Wholesaler.query.get(int(row['wholesaler_id']))
                if not wholesaler:
                    raise ValueError(f"Wholesaler with ID {row['wholesaler_id']} not found")
                
                product_data = {
                    'product_id': str(row['product_id']),
                    'name': str(row['name']),
                    'size': str(row['size']),
                    'price': float(row['price']),
                    'wholesaler_id': wholesaler.id
                }
                products.append(product_data)
            except Exception as e:
                current_app.logger.error(f"Error processing row: {row}. Error: {str(e)}")
                raise
        
        return products
    except Exception as e:
        current_app.logger.error(f"Error processing Excel file: {str(e)}")
        raise

@bp.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    # Populate the wholesaler choices
    form.wholesaler.choices = [(w.id, w.name) for w in Wholesaler.query.all()]
    
    if form.validate_on_submit():
        product.product_id = form.product_id.data
        product.name = form.name.data
        product.size = form.size.data
        product.price = form.price.data
        product.wholesaler_id = form.wholesaler.data
        db.session.commit()
        flash('Product updated successfully!')
        return redirect(url_for('main.products'))
    
    # Set the current wholesaler as selected
    form.wholesaler.data = product.wholesaler_id
    return render_template('product_form.html', title='Edit Product', form=form)

@bp.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.options(joinedload(Product.order_items)).get_or_404(product_id)
    
    # Delete associated order list items
    for order_item in product.order_items:
        db.session.delete(order_item)
    
    db.session.delete(product)
    
    try:
        db.session.commit()
        flash('Product deleted successfully!')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the product: {str(e)}', 'error')
    
    return redirect(url_for('main.products'))

@bp.route('/products/delete', methods=['POST'])
@login_required
def delete_multiple_products():
    product_ids = request.form.getlist('product_ids[]')
    
    products = Product.query.filter(Product.id.in_(product_ids)).options(joinedload(Product.order_items)).all()
    
    for product in products:
        for order_item in product.order_items:
            db.session.delete(order_item)
        db.session.delete(product)
    
    try:
        db.session.commit()
        flash(f'{len(products)} products deleted successfully!')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting products: {str(e)}', 'error')
    
    return redirect(url_for('main.products'))


@bp.route('/list_order_lists')
@login_required
def list_order_lists():
    daily_order_lists = OrderList.query.join(Wholesaler).filter(Wholesaler.is_daily == True).all()
    monthly_order_lists = OrderList.query.join(Wholesaler).filter(Wholesaler.is_daily == False).all()
    return render_template('list_order_lists.html', title='Order Lists',
                           daily_order_lists=daily_order_lists, monthly_order_lists=monthly_order_lists)

@bp.route('/wholesalers')
@login_required
def list_wholesalers():
    try:
        wholesalers = Wholesaler.query.all()
        current_app.logger.info(f"Retrieved {len(wholesalers)} wholesalers")
        return render_template('wholesalers.html', wholesalers=wholesalers, title='Wholesalers')
    except Exception as e:
        current_app.logger.error(f"Error in list_wholesalers: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        flash('An error occurred while retrieving wholesalers. Please try again.', 'error')
        return render_template('wholesalers.html', wholesalers=[], title='Wholesalers')

@bp.route('/wholesaler/<int:id>/delete', methods=['POST'])
@login_required
def delete_wholesaler(id):
    try:
        wholesaler = Wholesaler.query.get_or_404(id)
        db.session.delete(wholesaler)
        db.session.commit()
        flash('Wholesaler deleted successfully!')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting wholesaler: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        flash('An error occurred while deleting the wholesaler. Please try again.', 'error')
    return redirect(url_for('main.list_wholesalers'))





@bp.route('/create_order_list', methods=['GET', 'POST'])
@login_required
def create_order_list():
    form = OrderListForm()
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        if product:
            order_type = 'daily' if product.wholesaler.is_daily else 'monthly'
            order_list = OrderList.query.filter_by(
                wholesaler_id=product.wholesaler_id,
                type=order_type,
                status='pending'
            ).first()
            
            if not order_list:
                order_list = OrderList(
                    wholesaler_id=product.wholesaler_id,
                    type=order_type,
                    status='pending',
                    date=datetime.utcnow().date()
                )
                db.session.add(order_list)
            
            order_item = OrderListItem(
                order_list=order_list,
                product_id=product.id,
                quantity=form.quantity.data
            )
            db.session.add(order_item)
            
            try:
                db.session.commit()
                flash(f'Added {form.quantity.data} of {product.name} to the {order_type} order list.', 'success')
            except SQLAlchemyError as e:
                db.session.rollback()
                current_app.logger.error(f"Error adding item to order list: {str(e)}")
                flash('An error occurred while adding the item to the order list.', 'error')
        else:
            flash('Product not found.', 'error')
        return redirect(url_for('main.create_order_list'))
    
    return render_template('create_order_list.html', title='Create Order List', form=form)

@bp.route('/finalize_order_list/<string:list_type>', methods=['POST'])
@login_required
def finalize_order_list(list_type):
    if list_type not in ['daily', 'monthly']:
        return jsonify({'success': False, 'message': 'Invalid list type'}), 400
    
    orders = OrderList.query.filter_by(type=list_type, status='pending').all()
    for order in orders:
        order.status = 'finalized'
        order.finalized_date = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'{list_type.capitalize()} orders finalized'})


@bp.route('/order_history')
@login_required
def order_history():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of orders per page
    
    # Filtering
    order_type = request.args.get('type', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query
    query = OrderList.query.options(
        joinedload(OrderList.items).joinedload(OrderListItem.product)
    )
    if order_type != 'all':
        query = query.filter(OrderList.type == order_type)
    if start_date:
        query = query.filter(OrderList.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(OrderList.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    # Sorting
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')
    
    if sort_by == 'date':
        query = query.order_by(desc(OrderList.date) if sort_order == 'desc' else OrderList.date)
    elif sort_by == 'wholesaler':
        query = query.join(Wholesaler).order_by(desc(Wholesaler.name) if sort_order == 'desc' else Wholesaler.name)
    
    # Pagination
    orders = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('order_history.html', title='Order History', orders=orders,
                           order_type=order_type, start_date=start_date, end_date=end_date,
                           sort_by=sort_by, sort_order=sort_order)

@bp.route('/get_order_lists')
@login_required
def get_order_lists():
    try:
        daily_orders = OrderList.query.filter_by(type='daily', status='pending').all()
        monthly_orders = OrderList.query.filter_by(type='monthly', status='pending').all()
        
        def format_order(order):
            return {
                'id': order.id,
                'wholesaler_name': order.wholesaler.name,
                'items': [{
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'comment': item.comment
                } for item in order.items]
            }
        
        return jsonify({
            'daily': [format_order(order) for order in daily_orders],
            'monthly': [format_order(order) for order in monthly_orders]
        })
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error in get_order_lists: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching order lists'}), 500
    

@bp.route('/wholesaler/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_wholesaler(id):
    wholesaler = Wholesaler.query.get_or_404(id)
    form = WholesalerForm(obj=wholesaler)
    if form.validate_on_submit():
        try:
            wholesaler.name = form.name.data
            wholesaler.is_daily = form.is_daily.data
            wholesaler.contact_person = form.contact_person.data
            wholesaler.email = form.email.data
            wholesaler.phone = form.phone.data
            db.session.commit()
            flash('Wholesaler updated successfully!')
            return redirect(url_for('main.list_wholesalers'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating wholesaler: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            flash('An error occurred while updating the wholesaler. Please try again.', 'error')
    return render_template('wholesaler_form.html', form=form, title="Edit Wholesaler")

@bp.route('/wholesaler/add', methods=['GET', 'POST'])
@login_required
def add_wholesaler():
    form = WholesalerForm()
    if form.validate_on_submit():
        try:
            wholesaler = Wholesaler(
                name=form.name.data,
                is_daily=form.is_daily.data,
                contact_person=form.contact_person.data,
                email=form.email.data,
                phone=form.phone.data
            )
            db.session.add(wholesaler)
            db.session.commit()
            flash('Wholesaler added successfully!')
            return redirect(url_for('main.list_wholesalers'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding wholesaler: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            flash('An error occurred while adding the wholesaler. Please try again.', 'error')
    return render_template('wholesaler_form.html', form=form, title="Add Wholesaler")

@bp.route('/finalize_order/<int:order_id>', methods=['POST'])
@login_required
def finalize_order(order_id):
    order = OrderList.query.get_or_404(order_id)
    order.status = 'finalized'
    db.session.commit()
    flash('Order finalized successfully.', 'success')
    return redirect(url_for('main.daily_orders' if order.type == 'daily' else 'main.monthly_orders'))

@bp.route('/view_order/<int:order_id>')
@login_required
def view_order(order_id):
    order = OrderList.query.get_or_404(order_id)
    return render_template('view_order.html', title='Order Details', order=order)
@bp.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = OrderList.query.get_or_404(order_id)
    if request.method == 'POST':
        # Update order details
        order.status = request.form.get('status')
        db.session.commit()
        flash('Order updated successfully.', 'success')
        return redirect(url_for('main.view_order', order_id=order.id))
    return render_template('edit_order.html', order=order)

@bp.route('/delete_order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    order = OrderList.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Order deleted successfully.', 'success')
    return redirect(url_for('main.order_history'))

@bp.route('/edit_order_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_order_item(item_id):
    item = OrderListItem.query.get_or_404(item_id)
    if request.method == 'POST':
        item.quantity = int(request.form.get('quantity'))
        db.session.commit()
        flash('Order item updated successfully.', 'success')
        return redirect(url_for('main.view_order', order_id=item.order_list.id))
    return render_template('edit_order_item.html', item=item)

@bp.route('/delete_order_item/<int:item_id>', methods=['POST'])
@login_required
def delete_order_item(item_id):
    item = OrderListItem.query.get_or_404(item_id)
    order_id = item.order_list.id
    db.session.delete(item)
    db.session.commit()
    flash('Order item deleted successfully.', 'success')
    return redirect(url_for('main.view_order', order_id=order_id))

# In app/main/routes.py
# app/main/routes.py


# app/main/routes.py

@bp.route('/analytics/sales')
@login_required
def sales_analytics():
    if not current_user.role == 'owner':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))

    try:
        # Default date range (current month)
        today = datetime.now().date()
        start_date = today.replace(day=1)  # First day of current month
        end_date = today

        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()

        # Get overall summary
        summary = db.session.query(
            func.sum(DailySales.total_actual).label('total_sales'),
            func.avg(DailySales.total_actual).label('avg_daily_sales'),
            func.count(DailySales.id).label('transaction_count'),
            func.sum(DailySales.overall_discrepancy).label('total_discrepancy'),
            func.sum(DailySales.front_register_cash + DailySales.back_register_cash).label('total_cash'),
            func.sum(DailySales.credit_card_total).label('total_card'),
            func.sum(DailySales.otc1_total + DailySales.otc2_total).label('total_otc')
        ).filter(
            DailySales.date.between(start_date, end_date)
        ).first()

        # Day of week analysis
        day_of_week = db.session.query(
            func.extract('dow', DailySales.date).label('day_of_week'),
            func.sum(DailySales.total_actual).label('total_sales'),
            func.count(DailySales.id).label('transaction_count')
        ).filter(
            DailySales.date.between(start_date, end_date)
        ).group_by(
            func.extract('dow', DailySales.date)
        ).order_by(
            'day_of_week'
        ).all()

        # Monthly analysis
        monthly = db.session.query(
            func.extract('month', DailySales.date).label('month'),
            func.sum(DailySales.total_actual).label('total_sales'),
            func.avg(DailySales.total_actual).label('avg_daily_sales'),
            func.count(DailySales.id).label('transaction_count')
        ).group_by(
            func.extract('month', DailySales.date)
        ).order_by(
            'month'
        ).all()

        # Format data for charts
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        months = ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']

        weekday_data = {
            'labels': days,
            'sales': [0] * 7,
            'transactions': [0] * 7
        }

        for day in day_of_week:
            idx = int(day.day_of_week)
            weekday_data['sales'][idx] = float(day.total_sales)
            weekday_data['transactions'][idx] = int(day.transaction_count)

        monthly_data = {
            'labels': months,
            'sales': [0] * 12,
            'avg_sales': [0] * 12,
            'transactions': [0] * 12
        }

        for month in monthly:
            idx = int(month.month) - 1  # Convert 1-based month to 0-based index
            monthly_data['sales'][idx] = float(month.total_sales)
            monthly_data['avg_sales'][idx] = float(month.avg_daily_sales)
            monthly_data['transactions'][idx] = int(month.transaction_count)

        return render_template(
            'analytics/sales_analytics.html',
            summary={
                'total_sales': float(summary.total_sales) if summary.total_sales else 0,
                'avg_daily_sales': float(summary.avg_daily_sales) if summary.avg_daily_sales else 0,
                'transaction_count': int(summary.transaction_count) if summary.transaction_count else 0,
                'total_discrepancy': float(summary.total_discrepancy) if summary.total_discrepancy else 0,
                'payment_methods': {
                    'cash': float(summary.total_cash) if summary.total_cash else 0,
                    'card': float(summary.total_card) if summary.total_card else 0,
                    'otc': float(summary.total_otc) if summary.total_otc else 0
                }
            },
            weekday_data=weekday_data,
            monthly_data=monthly_data,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

    except Exception as e:
        current_app.logger.error(f"Error in sales analytics: {str(e)}")
        flash('An error occurred while loading analytics.', 'error')
        return redirect(url_for('main.index'))

# Add this to the imports at the top of routes.py
from datetime import datetime, timedelta, date
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, desc, case, extract
from sqlalchemy.orm import joinedload
from app import db
from app.main import bp
from app.models import (
    User, Product, Wholesaler, OrderList, OrderListItem, 
    CustomerOrder, CustomerOrderItem, DailySales
)
# app/main/routes.py

@bp.route('/analytics/orders')
@login_required
def order_analytics():
    if not current_user.role == 'owner':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))

    try:
        today = datetime.now().date()
        start_date = today.replace(day=1)
        end_date = today

        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()

        # Get all orders for the period
        orders = db.session.query(OrderList).filter(
            OrderList.date.between(start_date, end_date)
        ).options(
            joinedload(OrderList.items).joinedload(OrderListItem.product)
        ).all()

        # Calculate basic metrics
        total_orders = len(orders)
        total_value = sum(
            item.quantity * item.product.price
            for order in orders
            for item in order.items
        )
        pending_orders = sum(1 for order in orders if order.status == 'pending')

        # Prepare summary
        summary = {
            'total_orders': total_orders,
            'total_value': total_value,
            'pending_orders': pending_orders,
            'avg_order_value': total_value / total_orders if total_orders > 0 else 0
        }

        # Initialize weekday counters
        weekday_values = [0] * 7
        weekday_counts = [0] * 7

        # Calculate weekday statistics
        for order in orders:
            weekday = order.date.weekday()
            order_value = sum(item.quantity * item.product.price for item in order.items)
            weekday_values[weekday] += order_value
            weekday_counts[weekday] += 1

        # Prepare chart data
        chart_data = {
            'labels': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'values': weekday_values,
            'orders': weekday_counts
        }

        # Calculate top products
        product_totals = {}
        for order in orders:
            for item in order.items:
                if item.product_id not in product_totals:
                    product_totals[item.product_id] = {
                        'name': item.product.name,
                        'quantity': 0,
                        'value': 0
                    }
                product_totals[item.product_id]['quantity'] += item.quantity
                product_totals[item.product_id]['value'] += item.quantity * item.product.price

        # Sort and format top products
        top_products = sorted(
            product_totals.values(),
            key=lambda x: x['value'],
            reverse=True
        )[:5]

        # Add profit calculation
        products = [{
            'name': p['name'],
            'quantity': p['quantity'],
            'value': p['value'],
            'profit': p['value'] * 0.4
        } for p in top_products]

        return render_template(
            'analytics/order_analytics.html',
            summary=summary,
            chart_data=chart_data,
            products=products,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

    except Exception as e:
        current_app.logger.error(f"Error in order analytics: {str(e)}")
        flash('An error occurred while loading analytics.', 'error')
        return redirect(url_for('main.index'))
@bp.route('/customer_orders')
@login_required
def customer_orders():
    try:
        # Get filter parameters from request
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')

        # Base query
        query = CustomerOrder.query

        # Apply filters
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(CustomerOrder.order_date >= start_date_obj)
        
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            # Add a day to include the entire end date
            query = query.filter(CustomerOrder.order_date <= end_date_obj)
        
        if status:
            query = query.filter(CustomerOrder.status == status)

        # Order by latest first
        orders = query.order_by(CustomerOrder.order_date.desc()).all()

        return render_template('customer_orders.html',
                            orders=orders,
                            start_date=start_date,
                            end_date=end_date,
                            status=status)

    except ValueError as e:
        flash('Invalid date format. Please use YYYY-MM-DD format.', 'error')
        return redirect(url_for('main.customer_orders'))
    
    
@bp.route('/create_customer_order', methods=['GET', 'POST'])
@login_required
def create_customer_order():
    form = CustomerOrderForm()
    if form.validate_on_submit():
        order = CustomerOrder(
            customer_name=form.customer_name.data,
            customer_contact=form.customer_contact.data,
            is_paid=form.is_paid.data,
            status=form.status.data
        )
        db.session.add(order)
        db.session.commit()
        flash('Customer order created successfully.')
        return redirect(url_for('main.add_customer_order_item', order_id=order.id))
    return render_template('create_customer_order.html', form=form)

@bp.route('/edit_customer_order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_customer_order(order_id):
    order = CustomerOrder.query.get_or_404(order_id)
    form = CustomerOrderForm(obj=order)
    if form.validate_on_submit():
        order.customer_name = form.customer_name.data
        order.customer_contact = form.customer_contact.data
        order.is_paid = form.is_paid.data
        order.status = form.status.data
        db.session.commit()
        flash('Order updated successfully.')
        return redirect(url_for('main.view_customer_order', order_id=order.id))
    return render_template('edit_customer_order.html', form=form, order=order)

@bp.route('/delete_customer_order/<int:order_id>', methods=['POST'])
@login_required
def delete_customer_order(order_id):
    order = CustomerOrder.query.get_or_404(order_id)
    # First, delete all related order items
    for item in order.items:
        db.session.delete(item)
    # Then, delete the order itself
    db.session.delete(order)
    try:
        db.session.commit()
        flash('Order deleted successfully.')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the order: {str(e)}', 'error')
    return redirect(url_for('main.customer_orders'))



@bp.route('/edit_customer_order_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_customer_order_item(item_id):
    item = CustomerOrderItem.query.get_or_404(item_id)
    form = CustomerOrderItemForm(obj=item)
    if form.validate_on_submit():
        item.quantity = form.quantity.data
        item.price = form.price.data
        item.status = form.status.data
        db.session.commit()
        flash('Order item updated successfully.')
        return redirect(url_for('main.view_customer_order', order_id=item.customer_order_id))
    return render_template('edit_customer_order_item.html', form=form, item=item)

@bp.route('/delete_customer_order_item/<int:item_id>', methods=['POST'])
@login_required
def delete_customer_order_item(item_id):
    item = CustomerOrderItem.query.get_or_404(item_id)
    order = item.customer_order
    order.total_amount -= item.quantity * item.price
    db.session.delete(item)
    db.session.commit()
    flash('Order item deleted successfully.')
    return redirect(url_for('main.view_customer_order', order_id=order.id))

@bp.route('/view_customer_order/<int:order_id>')
@login_required
def view_customer_order(order_id):
    order = CustomerOrder.query.get_or_404(order_id)
    return render_template('view_customer_order.html', order=order)



from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db
from app.main import bp
from app.main.forms import CustomerOrderItemForm, ProductForm
from app.models import CustomerOrder, CustomerOrderItem, Product, Wholesaler
from flask_login import login_required

@bp.route('/search_products')
@login_required
def search_products():
    query = request.args.get('query', '')
    products = Product.query.filter(Product.name.ilike(f'%{query}%')).limit(10).all()
    return jsonify([{'id': p.id, 'name': p.name, 'price': p.price} for p in products])

@bp.route('/add_customer_order_item/<int:order_id>', methods=['GET', 'POST'])
@login_required
def add_customer_order_item(order_id):
    order = CustomerOrder.query.get_or_404(order_id)
    form = CustomerOrderItemForm()
    if form.validate_on_submit():
        product = Product.query.filter(Product.name.ilike(f"%{form.product_name.data}%")).first()
        if product:
            item = CustomerOrderItem(
                customer_order_id=order.id,
                product_id=product.id,
                quantity=form.quantity.data,
                price=form.price.data or product.price,
                status=form.status.data
            )
            db.session.add(item)
            order.total_amount += item.quantity * item.price
            db.session.commit()
            flash('Item added to the order.', 'success')
            return redirect(url_for('main.add_customer_order_item', order_id=order.id))
        else:
            flash(f'Product "{form.product_name.data}" not found in database. Would you like to add it?', 'warning')
            return render_template('add_customer_order_item.html', form=form, order=order, show_add_product=True)
    
    return render_template('add_customer_order_item.html', form=form, order=order, show_add_product=False)

@bp.route('/add_product_to_order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def add_product_to_order(order_id):
    form = ProductForm()
    form.wholesaler.choices = [(w.id, w.name) for w in Wholesaler.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            product_id=form.product_id.data,
            name=form.name.data,
            size=form.size.data,
            price=form.price.data,
            wholesaler_id=form.wholesaler.data
        )
        db.session.add(product)
        db.session.commit()
        flash('New product added successfully.', 'success')
        return redirect(url_for('main.add_customer_order_item', order_id=order_id))
    
    return render_template('add_product_to_order.html', form=form, title="Add New Product", order_id=order_id)
    

    # In app/main/routes.py

from flask import current_app, jsonify
from supabase import create_client

@bp.route('/test-supabase')
def test_supabase():
    try:
        supabase = create_client(
            current_app.config['SUPABASE_URL'],
            current_app.config['SUPABASE_ANON_KEY']
        )
        # Try a simple query
        response = supabase.table('user').select("*").execute()
        return jsonify({
            'status': 'success',
            'message': 'Supabase connection successful',
            'config': {
                'url_configured': bool(current_app.config['SUPABASE_URL']),
                'key_configured': bool(current_app.config['SUPABASE_ANON_KEY'])
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'config': {
                'url_configured': bool(current_app.config['SUPABASE_URL']),
                'key_configured': bool(current_app.config['SUPABASE_ANON_KEY'])
            }
        })
    
@bp.route('/sales/upload_document', methods=['POST'])
@login_required
def upload_sales_document():
    """Handle document upload for sales reports"""
    try:
        sales_id = request.form.get('sales_id')
        document_type = request.form.get('document_type')
        file = request.files.get('file')
        
        if not all([sales_id, document_type, file]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
        # Upload to Cloudinary
        result = CloudinaryStorage.upload_file(
            file,
            folder=f"sales_reports/{document_type}",
            public_id_prefix=f"sales_{sales_id}_{document_type}"
        )
        
        if not result['success']:
            return jsonify({'success': False, 'error': result['error']}), 500
            
        # Save document record
        document = SalesDocument(
            sales_id=sales_id,
            document_type=document_type,
            filename=file.filename,
            cloudinary_public_id=result['public_id'],
            secure_url=result['secure_url']
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'document_id': document.id,
            'url': document.secure_url
        })
        
    except Exception as e:
        current_app.logger.error(f"Document upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/sales/document/<int:document_id>/delete', methods=['POST'])
@login_required
def delete_sales_document(document_id):
    """Delete a sales document"""
    try:
        document = SalesDocument.query.get_or_404(document_id)
        
        # Delete from Cloudinary
        if CloudinaryStorage.delete_file(document.cloudinary_public_id):
            db.session.delete(document)
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to delete from storage'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    # app/main/routes.py


# Make sure these imports are at the top of routes.py
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from app.utils.storage import CloudinaryStorage

@bp.route('/sales/record', methods=['GET', 'POST'])
@login_required
def record_daily_sales():
    """Record daily sales entry"""
    form = DailySalesForm()
    if form.validate_on_submit():
        try:
            # Create sales record
            sales = DailySales(
                date=datetime.utcnow().date(),
                report_time=form.report_time.data,
                employee_id=current_user.id,
                front_register_amount=form.front_register_amount.data,
                back_register_amount=form.back_register_amount.data,
                credit_card_amount=form.credit_card_amount.data,
                otc1_amount=form.otc1_amount.data,
                otc2_amount=form.otc2_amount.data,
                front_register_cash=form.front_register_cash.data,
                back_register_cash=form.back_register_cash.data,
                credit_card_total=form.credit_card_total.data,
                otc1_total=form.otc1_total.data,
                otc2_total=form.otc2_total.data,
                notes=form.notes.data
            )
            
            sales.calculate_discrepancies()
            db.session.add(sales)
            db.session.commit()  # Commit first to get sales.id

            # Initialize CloudinaryStorage
            storage = CloudinaryStorage()
            
            # Handle file uploads
            if form.register_reports.data:
                result = storage.upload_file(
                    form.register_reports.data,
                    folder="register_reports",
                    public_id_prefix=f"sales_{sales.id}_register"
                )
                if result['success']:
                    doc = SalesDocument(
                        sales_id=sales.id,
                        document_type='register_report',
                        filename=form.register_reports.data.filename,
                        cloudinary_public_id=result['public_id'],
                        secure_url=result['secure_url']
                    )
                    db.session.add(doc)

            if form.credit_card_statement.data:
                result = storage.upload_file(
                    form.credit_card_statement.data,
                    folder="credit_card_statements",
                    public_id_prefix=f"sales_{sales.id}_cc"
                )
                if result['success']:
                    doc = SalesDocument(
                        sales_id=sales.id,
                        document_type='credit_card_statement',
                        filename=form.credit_card_statement.data.filename,
                        cloudinary_public_id=result['public_id'],
                        secure_url=result['secure_url']
                    )
                    db.session.add(doc)

            if form.otc_statements.data:
                result = storage.upload_file(
                    form.otc_statements.data,
                    folder="otc_statements",
                    public_id_prefix=f"sales_{sales.id}_otc"
                )
                if result['success']:
                    doc = SalesDocument(
                        sales_id=sales.id,
                        document_type='otc_statement',
                        filename=form.otc_statements.data.filename,
                        cloudinary_public_id=result['public_id'],
                        secure_url=result['secure_url']
                    )
                    db.session.add(doc)

            db.session.commit()
            flash('Sales record saved successfully!', 'success')
            return redirect(url_for('main.list_sales'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving sales record: {str(e)}")
            flash('An error occurred while saving the sales record.', 'error')

    return render_template('sales/record_sales.html', form=form, title='Record Daily Sales')

@bp.route('/sales/list')
@login_required
def list_sales():
    """List all sales records"""
    if not current_user.role == 'owner':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    
    # Handle show today
    show_today = request.args.get('show_today', False, type=bool)
    start_date = end_date = None
    
    if show_today:
        start_date = end_date = date.today()
    else:
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
    
    # Base query with joins
    query = DailySales.query.join(User, DailySales.employee_id == User.id)
    
    # Apply date filters
    if start_date:
        query = query.filter(DailySales.date >= start_date)
    if end_date:
        query = query.filter(DailySales.date <= end_date)
    
    # Calculate summary statistics
    summary = query.with_entities(
        func.sum(DailySales.total_actual).label('total_sales'),
        func.sum(DailySales.front_register_cash + DailySales.back_register_cash).label('total_cash'),
        func.sum(DailySales.front_register_cash).label('total_front_cash'),
        func.sum(DailySales.back_register_cash).label('total_back_cash'),
        func.sum(DailySales.credit_card_total).label('total_card'),
        func.sum(DailySales.otc1_total + DailySales.otc2_total).label('total_otc'),
        func.sum(DailySales.overall_discrepancy).label('total_discrepancy')
    ).first()

    # Get paginated results
    sales = query.order_by(DailySales.date.desc(), DailySales.report_time.desc()) \
        .paginate(page=page, per_page=10)

    return render_template('sales/list_sales.html', 
                         sales=sales,
                         total_sales=summary.total_sales or 0,
                         total_cash=summary.total_cash or 0,
                         total_front_cash=summary.total_front_cash or 0,
                         total_back_cash=summary.total_back_cash or 0,
                         total_card=summary.total_card or 0,
                         total_otc=summary.total_otc or 0,
                         total_discrepancy=summary.total_discrepancy or 0,
                         start_date=start_date,
                         end_date=end_date,
                         abs=abs,  # Pass abs function
                         is_today=show_today)

@bp.route('/sales/<int:sales_id>/delete', methods=['POST'])
@login_required
def delete_sales(sales_id):
    """Delete a sales record"""
    if not current_user.role == 'owner':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
        
    try:
        sales = DailySales.query.get_or_404(sales_id)
        
        # Delete associated documents from Cloudinary
        for document in sales.documents:
            if document.cloudinary_public_id:  # Check if document exists
                CloudinaryStorage.delete_file(document.cloudinary_public_id)
        
        # Delete the sales record and its documents
        db.session.delete(sales)
        db.session.commit()
        
        flash('Sales record deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting sales record: {str(e)}")
        flash('Error deleting sales record.', 'error')
        
    return redirect(url_for('main.list_sales'))

@bp.route('/sales/view/<int:sales_id>')
@login_required
def view_sales(sales_id):
    """View a specific sales record"""
    sales = DailySales.query.options(
        joinedload(DailySales.employee),
        joinedload(DailySales.documents)
    ).get_or_404(sales_id)
    
    # Calculate totals for quick reference
    totals = {
        'cash': sales.front_register_cash + sales.back_register_cash,
        'card': sales.credit_card_total,
        'otc': sales.otc1_total + sales.otc2_total,
    }
    
    return render_template('sales/view_sales.html', 
                         sales=sales, 
                         totals=totals,
                         abs=abs,  # Pass the abs function to template
                         title='Sales Record Details')