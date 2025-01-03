from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='employee')  # 'employee', 'owner'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_owner(self):
        return self.role == 'owner'

class DailySales(db.Model):
    __tablename__ = 'daily_sales'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    report_time = db.Column(db.DateTime, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Register readings
    front_register_amount = db.Column(db.Float, nullable=False)
    back_register_amount = db.Column(db.Float, nullable=False)
    credit_card_amount = db.Column(db.Float, nullable=False)
    otc1_amount = db.Column(db.Float, nullable=False)
    otc2_amount = db.Column(db.Float, nullable=False)
    
    # Actual collections
    front_register_cash = db.Column(db.Float, nullable=False)
    back_register_cash = db.Column(db.Float, nullable=False)
    credit_card_total = db.Column(db.Float, nullable=False)
    otc1_total = db.Column(db.Float, nullable=False)
    otc2_total = db.Column(db.Float, nullable=False)
    
    # Calculated fields
    total_expected = db.Column(db.Float, nullable=False)
    total_actual = db.Column(db.Float, nullable=False)
    front_register_discrepancy = db.Column(db.Float, nullable=False)
    back_register_discrepancy = db.Column(db.Float, nullable=False)
    overall_discrepancy = db.Column(db.Float, nullable=False)
    
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    
    # Relationships
    employee = db.relationship('User', backref=db.backref('sales_records', lazy=True))
    documents = db.relationship('SalesDocument', backref='sales_report', cascade='all, delete-orphan')

    def calculate_discrepancies(self):
        """
        Calculate all discrepancy amounts
        Discrepancy = Actual - Expected
        Negative (-) means we have LESS than expected (MISSING money)
        Positive (+) means we have MORE than expected (EXTRA money)
        """
        # Individual register discrepancies
        self.front_register_discrepancy = self.front_register_cash - self.front_register_amount
        self.back_register_discrepancy = self.back_register_cash - self.back_register_amount
        
        # Calculate totals
        self.total_expected = (
            self.front_register_amount +
            self.back_register_amount +
            self.credit_card_amount +
            self.otc1_amount +
            self.otc2_amount
        )
        
        self.total_actual = (
            self.front_register_cash +
            self.back_register_cash +
            self.credit_card_total +
            self.otc1_total +
            self.otc2_total
        )
        
        # Overall discrepancy
        self.overall_discrepancy = self.total_actual - self.total_expected

    @property
    def has_significant_discrepancy(self):
        """Check if there's a significant discrepancy (more than $10 either way)"""
        return abs(self.overall_discrepancy) > 10

    def get_status(self):
        """Get the status based on discrepancy"""
        if abs(self.overall_discrepancy) <= 10:
            return "Balanced"
        return "Discrepancy"
class SalesDocument(db.Model):
    __tablename__ = 'sales_documents'  # Note the plural form
    id = db.Column(db.Integer, primary_key=True)
    sales_id = db.Column(db.Integer, db.ForeignKey('daily_sales.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    cloudinary_public_id = db.Column(db.String(255), nullable=False)
    secure_url = db.Column(db.String(512), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)

# Include your other existing models here...

class Wholesaler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_daily = db.Column(db.Boolean, default=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    products = db.relationship('Product', back_populates='wholesaler')
    order_lists = db.relationship('OrderList', back_populates='wholesaler')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(50))
    price = db.Column(db.Float, nullable=False)
    wholesaler_id = db.Column(db.Integer, db.ForeignKey('wholesaler.id'), nullable=False)
    wholesaler = db.relationship('Wholesaler', back_populates='products')
    available_in_store = db.Column(db.Boolean, default=True)

class OrderList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    wholesaler_id = db.Column(db.Integer, db.ForeignKey('wholesaler.id'), nullable=False)
    wholesaler = db.relationship('Wholesaler', back_populates='order_lists')
    items = db.relationship('OrderListItem', back_populates='order_list', cascade='all, delete-orphan')
    status = db.Column(db.String(20), default='pending')  # 'pending', 'finalized'
    type = db.Column(db.String(10), nullable=False)  # 'daily' or 'monthly'
    finalized_date = db.Column(db.DateTime)
    def total_value(self):
        return sum(item.quantity * item.product.price for item in self.items)

class OrderListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_list_id = db.Column(db.Integer, db.ForeignKey('order_list.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    order_list = db.relationship('OrderList', back_populates='items')
    product = db.relationship('Product', backref='order_items')

class CustomerOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_contact = db.Column(db.String(100), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # New field
    is_paid = db.Column(db.Boolean, default=False)
    total_amount = db.Column(db.Float, default=0.0)
    items = db.relationship('CustomerOrderItem', backref='customer_order', lazy='dynamic')

class CustomerOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_order_id = db.Column(db.Integer, db.ForeignKey('customer_order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)  # Can be null for custom products
    custom_product_name = db.Column(db.String(100))  # For products not in stock
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # New field
    product = db.relationship('Product', backref='customer_order_items')

