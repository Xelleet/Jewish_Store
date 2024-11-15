import json
import os.path
import secrets

import flask
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask import Flask, render_template, request, redirect, url_for, flash, session as flask_session
from werkzeug.utils import secure_filename, send_from_directory

app = Flask(__name__)
app.secret_key = '4f6b89def1878fc36f41258ac7dd77d9'

DATABASE_URL = 'sqlite:///database.db'
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)

class CartProduct(Base):
    __tablename__ = 'cart_products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    product_id = Column(Integer, nullable=False)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.route('/')
def index():
    session = Session()
    products = session.query(Product).all()
    session.close()
    return render_template('index.html', products=products)

@app.route('/add_product/<int:cart_product_id>')
def add_product(cart_product_id):
    session = Session()
    product = session.query(Product).filter_by(id=cart_product_id).first()

    new_product = CartProduct(name=product.name, price=product.price, product_id=cart_product_id)

    if session.query(CartProduct).filter(CartProduct.name == product.name).first():
        session.close()
        return redirect(url_for('index'))

    if new_product:
        session.add(new_product)
        session.commit()
        session.close()
        return redirect(url_for('cart'))

    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/cart')
def cart():
    session = Session()
    products = session.query(CartProduct).all()
    session.close()

    return render_template('cart.html', products=products)

@app.route('/admin', methods=['GET', 'POST'])
def add_new_product():
    session = Session()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        if session.query(Product).filter(Product.name == name).first():
            flash('Дважды выставлять продукты - признак дурачинства')
            session.close()
            return redirect(url_for('admin'))

        new_product = Product(name=name, description=description, price=price)
        session.add(new_product)
        session.commit()
        session.close()
        flash('Вы успешно добавили свою фигню')
        return redirect(url_for('index'))

    return render_template('admin.html')

if __name__ == "__main__":
    app.run(debug=True)
