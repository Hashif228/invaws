from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import random
from .models import db, User,Product,Purchase,Sale
from flask_mail import Message
from flask import send_file
from app import mail  
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime, date,timedelta
from sqlalchemy import func,extract
import os
import calendar
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
from io import BytesIO

main_bp = Blueprint("main_bp", __name__)

from functools import wraps
######################################
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            session['next'] = request.url 
            return redirect(url_for('main_bp.login'))  
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ser=session.get('role')
        if ser!= 'admin':
            return redirect(url_for('main_bp.dashboard')) 
        return f(*args, **kwargs)
    return decorated_function

#######################################################################
@main_bp.route("/login", methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        flash("You are already logged in.", "info")
        return redirect(url_for('main_bp.dashboard'))

    if request.method == 'POST':
        form_check = request.form.get('form_check')

        if form_check == 'register': 
            email = request.form['ruusername']
            password = request.form['registerupassword']
            confirm_password = request.form['registeruconfirmpassword']
            if password != confirm_password:
                flash("Passwords do not match")
                return redirect(url_for('main_bp.login'))

            otp = str(random.randint(100000, 999999))
            session['reg_email'] = email
            session['reg_password'] = password
            session['otp'] = otp
            msg = Message("Your OTP for Smart Inventory", sender=email, recipients=[email])
            msg.body = f"Your OTP is: {otp}"
            mail.send(msg)

            return render_template('login.html', otp_available=True)

        elif form_check == 'otp': 
            entered_otp = request.form['otp']
            if entered_otp == session.get('otp'):
                email = session.get('reg_email')
                password = session.get('reg_password')
                username = email.split('@')[0] 

                hashed_password = generate_password_hash(password)

                new_user = User(
                    username=username,
                    password_hash=hashed_password,
                    role='user',
                    email=email
                )
                db.session.add(new_user)
                db.session.commit()

                flash("Registered successfully! You can now log in.")
                session.pop('otp', None)
                return redirect(url_for('main_bp.login'))

            else:
                flash("Invalid OTP. Please try again.")
                return render_template('login.html', otp_available=True)

        elif form_check == 'user_login':
            username = request.form['uusername']
            password = request.form['upassword']

            user = User.query.filter_by(email=username).first()
            
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['role']=user.role
              

                next_page = session.pop('next', None)
                return redirect(next_page or url_for('main_bp.dashboard'))  

            flash("Invalid username or password", "danger")

    return render_template('login.html')

#######################################################################
@main_bp.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main_bp.login')) 
    

    # products=Product.query.all()
    # purchase=Purchase.query.all()
    # sales=Sale.query.all()
    low_stock_count = db.session.query(Product).filter(Product.stock.between(1, 10)).count()
    total_stock = db.session.query(func.sum(Product.stock)).scalar()
    total_categories = db.session.query(func.count(func.distinct(Product.category))).scalar()
    total_sales = db.session.query(func.sum(Sale.total)).scalar() or 0
    total_purchases = db.session.query(func.sum(Purchase.total)).scalar() or 0
    role=session.get('role')
    admin=False
    if role=='admin':
        admin=True
    return render_template('dashboard.html',low_stock_count=low_stock_count,total_stock=total_stock,total_categories=total_categories,total_sales=total_sales,total_purchases=total_purchases,admin=admin)


#######################################################

@main_bp.route('/logout')
def logout():
    session.pop('user_id', None)  

    return redirect(url_for('main_bp.login'))  

##################################################

@main_bp.route('/sales')
@login_required
def sales():
    products = Product.query.all()
    sales = Sale.query.all()
    total_sale = db.session.query(func.sum(Sale.total)).scalar()
    current_year = datetime.now().year
    current_month = datetime.now().month
    month_sale = db.session.query(func.sum(Sale.total)) \
                          .filter(func.extract('year', Sale.date) == current_year) \
                          .filter(func.extract('month', Sale.date) == current_month) \
                          .scalar()

    if month_sale is None:
        month_sale = 0.0

    today = date.today()

    daily_sale = db.session.query(func.sum(Sale.total)) \
                          .filter(func.date(Sale.date) == today) \
                          .scalar()

    if daily_sale is None:
        daily_sale = 0.0

    return render_template('sales.html', products=products,sales=sales,total_sale=total_sale,month_sale=month_sale,daily_sale=daily_sale)


#######################################################
@main_bp.route('/stock')
@login_required
def stock():
    products = Product.query.all()
    return render_template('stock.html', products=products)

####################################################################


@main_bp.route('/update_stock', methods=['POST'])
@login_required
def update_stock():
    product_id = request.form.get('product_id')
    new_stock = request.form.get('new_stock')

    product = Product.query.get(product_id)
    
    if product:
        current=product.stock
        product.stock= int(new_stock)+current
        product.date=datetime.now()
        db.session.commit()
    else:
        pass

    return redirect(url_for('main_bp.stock'))

##############################################################################



@main_bp.route('/manage')
@admin_required
def manage():
    users = User.query.all()
    return render_template('manage.html', users=users)

@main_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.role = request.form['role']
        db.session.commit()
        return redirect(url_for('main_bp.manage'))
    return render_template('edit_user.html', user=user)

@main_bp.route('/manage/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('main_bp.manage'))





@main_bp.route('/register_by_admin', methods=['GET', 'POST'])
@admin_required
def register_by_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        username =email.split('@')[0] 

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main_bp.manage'))

    return render_template('register_by_admin.html')




############################################################################################







@main_bp.route('/purchase')
@login_required
def purchase():
    products = Product.query.all()
    purchases = Purchase.query.all()
    total_sum = db.session.query(func.sum(Purchase.total)).scalar()
    current_year = datetime.now().year
    current_month = datetime.now().month

    month_sum = db.session.query(func.sum(Purchase.total)) \
                          .filter(func.extract('year', Purchase.date) == current_year) \
                          .filter(func.extract('month', Purchase.date) == current_month) \
                          .scalar()

    if month_sum is None:
        month_sum = 0.0

    today = date.today()

    daily_sum = db.session.query(func.sum(Purchase.total)) \
                          .filter(func.date(Purchase.date) == today) \
                          .scalar()

    if daily_sum is None:
        daily_sum = 0.0

    return render_template('purchase.html', products=products,purchases=purchases,total_sum=total_sum,month_sum=month_sum,daily_sum=daily_sum)



#############################################################################

@main_bp.route('/sell_item',methods=['POST'])
@login_required
def sell_item():
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])
    total = float(request.form['total'])
    # status = request.form['status']
    product = Product.query.get(product_id)

    current_quantity = product.stock
    new_quantity = current_quantity - quantity 
    product.stock = new_quantity

    current_total=product.price
    new_total=current_total-total
    product.price=new_total

    seller_email=session.get('reg_email')
    seller_name=seller_email.split('@')[0] 
    item=product.name
    new_sale = Sale(
        quantity=quantity,
        total=total,
        date=datetime.now(),
        name=item,
        seller=seller_name
    
    )
    last_sale = Sale.query.order_by(Sale.id.desc()).first()
    invoice_id = f"#SA{last_sale.id + 1 if last_sale else 1:03d}"
    new_sale.invoice_id = invoice_id
    db.session.add(new_sale)
    db.session.commit()
    return redirect(url_for('main_bp.sales'))
#############################################################################
@main_bp.route('/analytics')
@login_required
def analytics():
    top_products = db.session.query(
        Sale.name,
        func.sum(Sale.quantity).label('total_sold')
    ).group_by(Sale.name).order_by(func.sum(Sale.quantity).desc()).limit(5).all()

    names = [item[0] for item in top_products]
    sales = [item[1] for item in top_products]

    plt.figure()
    plt.bar(names, sales, color='skyblue')
    plt.title('Top Selling Products')
    plt.ylabel('Units Sold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/images/top_selling.png')
    plt.close()

    daily_sales = db.session.query(Sale.date, func.sum(Sale.total))\
        .filter(Sale.date >= datetime.utcnow() - timedelta(days=7))\
        .group_by(Sale.date).all()

    dates = [d[0].strftime('%d-%b') for d in daily_sales]
    amounts = [d[1] for d in daily_sales]

    plt.figure()
    plt.plot(dates, amounts, marker='o')
    plt.title('Daily Sales (Last 7 Days)')
    plt.xlabel('Date'); plt.ylabel('Amount')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/images/daily_sales.png')
    plt.close()

    monthly_sales = db.session.query(
        extract('month', Sale.date), func.sum(Sale.total)
    ).filter(extract('year', Sale.date) == datetime.utcnow().year)\
     .group_by(extract('month', Sale.date)).all()

    months = [calendar.month_abbr[int(m[0])] for m in monthly_sales]
    monthly_amounts = [m[1] for m in monthly_sales]

    plt.figure()
    plt.bar(months, monthly_amounts, color='lightseagreen')
    plt.title('Monthly Sales (Current Year)')
    plt.tight_layout()
    plt.savefig('static/images/monthly_sales.png')
    plt.close()

    yearly_sales = db.session.query(
        extract('year', Sale.date), func.sum(Sale.total)
    ).group_by(extract('year', Sale.date)).order_by(extract('year', Sale.date)).all()

    years = [str(int(y[0])) for y in yearly_sales]
    year_values = [y[1] for y in yearly_sales]

    plt.figure()
    plt.plot(years, year_values, marker='s', linestyle='--', color='orange')
    plt.title('Yearly Sales Overview')
    plt.tight_layout()
    plt.savefig('static/images/yearly_sales.png')
    plt.close()

    category_stock = db.session.query(Product.category, func.sum(Product.stock))\
        .group_by(Product.category).all()

    categories = [c[0] for c in category_stock]
    stock_levels = [c[1] for c in category_stock]

    plt.figure(figsize=(6, 4))
    plt.barh(categories, stock_levels, color='salmon')
    plt.title('Inventory Heatmap by Category')
    plt.xlabel('Stock Units')
    plt.tight_layout()
    plt.savefig('static/images/inventory_heatmap.png')
    plt.close()
    total_products = Product.query.count()
    low_stock = Product.query.filter(Product.stock <= 10).count()

    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    todays_sales = db.session.query(db.func.sum(Sale.total))\
        .filter(db.func.date(Sale.date) == today).scalar() or 0

    monthly_revenue = db.session.query(db.func.sum(Sale.total))\
        .filter(Sale.date >= month_start).scalar() or 0
    

    category_counts = db.session.query(Product.category, func.count(Product.id))\
        .group_by(Product.category).all()

    categoriespie = [c[0] for c in category_counts]
    countspie = [c[1] for c in category_counts]

    plt.figure(figsize=(8, 6))
    plt.pie(countspie, labels=categoriespie, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title('Inventory Breakdown by Category', fontsize=16, weight='bold')
    plt.axis('equal')  

    plt.savefig('static/images/category_pie_chart.png', bbox_inches='tight')
    plt.close()



    return render_template('analytics.html',total_products=total_products,todays_sales=todays_sales,monthly_revenue=monthly_revenue,low_stock=low_stock)

#############################################################################################

@main_bp.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    search_query = request.args.get('search', '')  
    
    try:
        if search_query:
            products = Product.query.filter(Product.name.like(f'%{search_query}%')).all()
        else:
            products = Product.query.all()
        
        return render_template('products.html', products=products, search_query=search_query)
    except Exception as e:
        return f"An error occurred: {str(e)}"


@main_bp.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        quantity = request.form['quantity']
        price = request.form['price']
        supplier = request.form['supplier']

        new_product = Product(
            name=name, 
            category=category, 
            stock=quantity, 
            price=price, 
            supplier=supplier
        )

        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('main_bp.products'))  

    return render_template('products.html')








@main_bp.route('/edit_product/<int:id>', methods=['POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    product.name = request.form['name']
    product.category = request.form['category']
    product.supplier = request.form['supplier']
    product.stock = request.form['quantity']
    product.price = request.form['price']

    db.session.commit()

    return redirect(url_for('main_bp.products'))



@main_bp.route('/delete_product/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('main_bp.products'))


#############################################################################################################


@main_bp.route('/add_purchase', methods=['POST'])
def add_purchase():
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])
    total = float(request.form['total'])
    product = Product.query.get(product_id)

    current_quantity = product.stock
    new_quantity = current_quantity + quantity 
    product.stock = new_quantity

    current_total=product.price
    new_total=current_total+total
    product.price=new_total



    supplier=product.supplier
    item=product.name
    new_purchase = Purchase(
        quantity=quantity,
        total=total,
        date=datetime.now(),
        supplier=supplier,
        name=item
    )

    last_purchase = Sale.query.order_by(Sale.id.desc()).first()
    invoice_id = f"#PU{last_purchase.id + 1 if last_purchase else 1:03d}"
    new_purchase.pinvoice_id = invoice_id

    db.session.add(new_purchase)
    db.session.commit()
    return redirect(url_for('main_bp.purchase'))

########################################################################################


@main_bp.route('/search')
@login_required
def search():
    search = request.args.get('search', None)
    category = request.args.get('category', None)
    status = request.args.get('status', None)

    query = Product.query

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category:
        query = query.filter_by(category=category)
    if status:
        if status == 'in-stock':
            query = query.filter(Product.stock > 10)
        elif status == 'low-stock':
            query = query.filter(Product.stock.between(1, 10))
        elif status == 'out-of-stock':
            query = query.filter(Product.stock == 0)

    products = query.all()
    return render_template('search.html', products=products)


#############################################################################



@main_bp.route('/export_sales_report')
@login_required
def export_sales_report():
    sales_data = Sale.query.all()

    from io import StringIO
    text_stream = StringIO()
    writer = csv.writer(text_stream)
    writer.writerow(['Invoice ID', 'Product Name', 'Quantity', 'Total', 'Date', 'Seller']) 

    for sale in sales_data:
        writer.writerow([sale.invoice_id, sale.name, sale.quantity, sale.total, sale.date, sale.seller])

    binary_stream = BytesIO()
    binary_stream.write(text_stream.getvalue().encode('utf-8')) 
    binary_stream.seek(0)

    return send_file(binary_stream, as_attachment=True, download_name='sales_report.csv', mimetype='text/csv')





@main_bp.route('/export_purchase_report')
@login_required
def export_purchase_report():
    purchase_data = Purchase.query.all()

    from io import StringIO
    text_stream = StringIO()
    writer = csv.writer(text_stream)
    writer.writerow(['Invoice ID', 'Product Name', 'Quantity', 'Total', 'Date', 'Seller']) 

    for purchase in purchase_data:
        writer.writerow([purchase.pinvoice_id, purchase.name, purchase.quantity, purchase.total, purchase.date,purchase.supplier])

    binary_stream = BytesIO()
    binary_stream.write(text_stream.getvalue().encode('utf-8'))  
    binary_stream.seek(0)

    return send_file(binary_stream, as_attachment=True, download_name='purchase_report.csv', mimetype='text/csv')


###########################################################################################