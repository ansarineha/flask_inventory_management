from flask import Flask,flash, request,redirect,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import func
from datetime import datetime
import pandas as pd 
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///frappeInventory.db'
db = SQLAlchemy(app)

engine=create_engine('sqlite:///frappeInventory.db', echo=True)
conn=engine.connect()
Base=declarative_base()

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False)

    def __repr__(self):
        return '<Product %r>' %self.id

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer,primary_key=True)
    name= db.Column(db.String(50),nullable=False)

    def __repr__(self):
        return '<Location %r>' %self.id


# data = pd.read_csv("https://pkgstore.datahub.io/core/world-cities/world-cities_csv/data/6cc66692f0e82b18216a48443b6b95da/world-cities_csv.csv" ) 
  
# # dropping passed columns 
# data.drop(["country", "subcountry", "geonameid"], axis = 1, inplace = True) 

# listToWrite=data.to_dict(orient='records')


# metadata = sqlalchemy.schema.MetaData(bind=engine,reflect=True)
# table = sqlalchemy.Table('location', metadata, autoload=True)
  
# Session = sessionmaker(bind=engine)
# session = Session()

# # Inser the dataframe into the database in one bulk
# conn.execute(table.insert(), listToWrite)

# # Commit the changes
# session.commit()

# # Close the session
# session.close()

class Movement(db.Model):
    movement_id= db.Column(db.Integer,primary_key=True)
    product_id= db.Column(db.Integer,db.ForeignKey('product.id'))
    product = db.relationship("Product")
    to_location_id = db.Column(db.Integer,db.ForeignKey('location.id'))
    to_location =   db.relationship("Location",primaryjoin=to_location_id==Location.id)
    from_location_id = db.Column(db.Integer,db.ForeignKey('location.id'))
    from_location = db.relationship("Location",primaryjoin=from_location_id==Location.id)
    quantity = db.Column(db.Integer)

    def __repr__(self):
        return '<Movement %r>' %self.id


@app.route('/') 
def index():
    return render_template('index.html')


@app.route('/products',methods=["GET","POST"], defaults={"page" : 1})
@app.route('/products/<int:page>', methods=["GET","POST"])
def products(page):
    error=None
    page=page
    pages=5
    if request.method == "GET":
        products=Product.query.paginate(page,pages,error_out=False)
        return render_template('products.html',products=products)

    if request.method == 'POST' and 'tag' in request.form:
        tag = request.form["tag"]
        search="%{}%".format(tag)
        products = Product.query.filter(Product.name.like(search)).paginate(per_page=pages, error_out=False)
        return render_template('products.html', products=products, tag=tag)

    if request.method == "POST":
        products = Product.query.all()
        product_name = request.form["product-name"]
        if not product_name.strip():
            error ='Please Enter Valid Product!'
            return render_template('products.html',error=error , products=products)
        if db.session.query(Product).filter(func.lower(Product.name)==func.lower(product_name)).all():
            error='Product already exist!'
            return render_template('products.html',error=error , products=products)
            
        else:
            new_product = Product(name=product_name)
            try:
                db.session.add(new_product)
                db.session.commit()
                return redirect('/products')
            except:
                return "Database error"

@app.route('/products/<int:id>/update',methods=["GET","POST"])
def update_product(id):
    product = Product.query.get_or_404(id)
    if request.method == "GET":
        return render_template("update_product.html",product=product)
    if request.method == "POST":
        product_name = request.form['product-name']
        product = Product.query.get_or_404(id)
        if not product_name.strip():
            error ='Please Enter Valid Product!'
            return render_template('update_product.html',error=error ,product=product )
        if db.session.query(Product).filter(func.lower(Product.name)==func.lower(product_name)).all():
            error='Product already exist!'
            return render_template('update_product.html',error=error ,product=product )
        else:
            product.name=request.form['product-name']
            try:
                db.session.commit()
                return redirect('/products')
            except:
                return "Database error"

@app.route('/locations', methods=["GET","POST"] , defaults={"page" : 1})
@app.route('/locations/<int:page>', methods=["GET","POST"])
def locations(page):
    error=None
    page=page
    pages=5
    if request.method == "GET":
        print("inside get")
        #locations = Location.query.all()
        locations=Location.query.paginate(page,pages,error_out=False)
        return render_template('locations.html',locations=locations)
    if request.method == 'POST' and 'tag' in request.form:
        tag = request.form["tag"]
        search="%{}%".format(tag)
        locations = Location.query.filter(Location.name.like(search)).paginate(per_page=pages, error_out=False)
        return render_template('locations.html', locations=locations, tag=tag)

    if request.method == "POST": 
        locations = Location.query.all()
        location_name = request.form["location-name"]
        if not location_name.strip():
            error ='Please Enter Valid Location!'
            return render_template('locations.html',error=error , locations=locations)
        if db.session.query(Location).filter(func.lower(Location.name)==func.lower(location_name)).all():
            error='Location already exist!'
            return render_template('locations.html',error=error , locations=locations)
        else:
            new_location = Location(name=location_name)
            try:
                db.session.add(new_location)
                db.session.commit()
                return redirect('/locations')
            except:
                return "Database error"

@app.route('/locations/<int:id>/update',methods=["GET","POST"])
def update_locations(id):
    location = Location.query.get_or_404(id)
    if request.method == "GET":
        return render_template("update_location.html",location=location)
    if request.method == "POST":
        location_name = request.form['location-name']
        location = Location.query.get_or_404(id)
        if not location_name.strip():
            error ='Please Enter Valid Location!'
            return render_template('update_location.html',error=error ,location=location )
        if db.session.query(Location).filter(func.lower(Location.name)==func.lower(location_name)).all():
            error='Location already exist!'
            return render_template('update_location.html',error=error ,location=location )
        else:
            location.name=request.form['location-name']
            try:
                db.session.commit()
                return redirect('/locations')
            except:
                return "Database error"

@app.route('/movement',methods=["GET","POST"])
def movements():
    if request.method == "GET":
        products = Product.query.all()
        locations = Location.query.all()
        movements = Movement.query.all()
        return render_template('movement.html',products=products,locations=locations,movements=movements)
    if request.method == "POST":
        products = Product.query.all()
        locations = Location.query.all()
        movements = Movement.query.all()
        to_location = request.form['to-location']
        from_location = request.form['from-location']
        if from_location==to_location:
            error='From location and To location cant be same'
            return render_template('movement.html',error=error,products=products,locations=locations,movements=movements)
        product = request.form['product']
        quantity = request.form['quantity']
        if from_location == 'none':
            new_movement = Movement(to_location_id=to_location,from_location_id=from_location,product_id=product,quantity=quantity)
            try:
                db.session.add(new_movement)
                db.session.commit()
                return redirect('/movement')
            except:
                return "Database error"
        else:
            quantity_at_location = get_quantity(from_location,product)
            if quantity_at_location < int(quantity):
                error= "Not enough quantity is available"
                return render_template('movement.html',error=error,products=products,locations=locations,movements=movements)
            else:
                new_movement = Movement(to_location_id=to_location,from_location_id=from_location\
                ,product_id=product,quantity=quantity)
                try:
                    db.session.add(new_movement)
                    db.session.commit()
                    return redirect('/movement')
                except:
                    return "Database error"

@app.route('/report')
def report():
    locations = Location.query.all()
    products = Product.query.all()
    report = []

    for location in locations:
        for product in products:
            row = {}
            row["location"] = location.name
            row["product"] = product.name
            row["quantity"] = get_quantity(location.id,product.id)
            report.append(row)
    return render_template('report.html',report=report)

    

def get_quantity(location,product):
    added_products = Movement.query.\
        filter(Movement.to_location_id==location,Movement.product_id==product)\
            .from_self(func.sum(Movement.quantity,)).all()
    added_products = added_products[0][0]
    if added_products == None:
        added_products = 0
    removed_products = Movement.query.\
        filter(Movement.from_location_id==location,Movement.product_id==product)\
            .from_self(func.sum(Movement.quantity,name="removed")).all()
    removed_products = removed_products[0][0]
    if removed_products == None:
        removed_products = 0
    return added_products-removed_products

@app.route('/movements/<int:id>/update',methods=["GET","POST"])
def update_movements(id):
    movement_to_be_updated = Movement.query.get_or_404(id)
    if request.method == "GET":
        products = Product.query.all()
        locations = Location.query.all()
        movements = Movement.query.all()
        return render_template('update_movements.html',products=products,locations=locations,movement=movement_to_be_updated)
    if request.method == "POST":
        movement_to_be_updated.to_location_id = request.form["to-location"]
        movement_to_be_updated.from_location_id = request.form["from-location"]
        movement_to_be_updated.product_id = request.form["product"]
        movement_to_be_updated.quantity = request.form["quantity"] 
        try:
            db.session.commit()
            return redirect('/movements')
        except:
            return "Database error"

if __name__ == "__main__":
    app.run(debug=True)