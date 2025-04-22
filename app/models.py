from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
db = SQLAlchemy()

def indtime():
    ind = pytz.timezone('Asia/Kolkata')
    return datetime.now(ind)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False) 
    role = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    stock = db.Column(db.Integer)
    price = db.Column(db.Float)
    supplier = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=indtime)
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    change_type = db.Column(db.String(50), nullable=False) 
    date = db.Column(db.DateTime, default=indtime)
    product = db.relationship('Product', backref=db.backref('stock_history', lazy=True))
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    invoice_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    supplier = db.Column(db.String(100), nullable=False)        
    pinvoice_id = db.Column(db.String(20), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

