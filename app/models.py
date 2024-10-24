from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        """Set password hash for the user"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

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
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))