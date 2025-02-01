# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     greeting = "World"
#     return f'Hello, {greeting}'

# if __name__ == "__main__":
#     app.run()

##-------------v2

# from flask import Flask
# from flask import render_template

# app = Flask(__name__)

# @app.route("/") # when there is a request / ends in / flask will go to def index
# def index():
#     greeting = "Hello World - resistance is persistance, persistance is winning"
#     return render_template("index.html", greeting=greeting)

# if __name__ == "__main__":
#     app.run()

##------------ v3 run /host the Meat_store locally

from flask import Flask, render_template, request, redirect, url_for
import json
import uuid
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

class Product(ABC):
    def __init__(self, name_of_product, category_of_product, date_of_manufacture, expiration_date, price, discount=0, _id=None):
        self._name_of_product = name_of_product
        self._category_of_product = category_of_product
        self._date_of_manufacture = date_of_manufacture
        self._expiration_date = expiration_date
        self._id = _id or str(uuid.uuid4())
        self._price = price
        self._discount = discount

    @property
    def name_of_product(self):
        return self._name_of_product

    @property
    def category_of_product(self):
        return self._category_of_product

    @property
    def date_of_manufacture(self):
        return self._date_of_manufacture

    @property
    def expiration_date(self):
        return self._expiration_date

    @property
    def id(self):
        return self._id

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    @property
    def discount(self):
        return self._discount

    @discount.setter
    def discount(self, value):
        self._discount = value

    def __eq__(self, other):
        return (self._name_of_product == other._name_of_product and
                self._category_of_product == other._category_of_product and
                self._price == other._price and
                self._discount == other._discount)

class MeatFrozen(Product):
    def __init__(self, name_of_product, date_of_manufacture, expiration_date, price, discount=0, _id=None):
        super().__init__(name_of_product, 'meat_frozen', date_of_manufacture, expiration_date, price, discount, _id)

class MeatFresh(Product):
    def __init__(self, name_of_product, date_of_manufacture, expiration_date, price, discount=0, _id=None):
        super().__init__(name_of_product, 'meat_fresh', date_of_manufacture, expiration_date, price, discount, _id)

class MeatProducts(Product):
    def __init__(self, name_of_product, date_of_manufacture, expiration_date, price, discount=0, _id=None):
        super().__init__(name_of_product, 'meat_products', date_of_manufacture, expiration_date, price, discount, _id)

class Stock:
    def __init__(self):
        self.products = {}

    def add_product(self, product):
        if product.id not in self.products:
            self.products[product.id] = {'product': product, 'quantity': 0}
        self.products[product.id]['quantity'] += 1
        result = f"Added {product.name_of_product} to stock."
        print(result)
        return result

    def product_sold(self, product_id):
        if product_id in self.products:
            self.products[product_id]['quantity'] -= 1
            if self.products[product_id]['quantity'] == 0:
                del self.products[product_id]
            print(f"Product with ID {product_id} sold.")
        else:
            print(f"Product with ID {product_id} not found in stock.")

    def update_stock(self):
        self.products = {pid: pdata for pid, pdata in self.products.items() if pdata['quantity'] > 0}
        print("Updated stock, removed products with quantity 0.")

    def apply_discount(self):
        today = datetime.now().date()
        for product_data in self.products.values():
            product = product_data['product']
            if product.expiration_date == today + timedelta(days=1):
                product.discount = 0.5  # 50% discount
                product.price *= 0.5
                print(f"Applied discount to {product.name_of_product}.")

    def display_stock(self):
        if not self.products:
            print("No products in stock.")
        else:
            for product_data in self.products.values():
                product = product_data['product']
                quantity = product_data['quantity']
                print(f"ID: {product.id}, Name: {product.name_of_product}, Category: {product.category_of_product}, "
                      f"Price: {product.price}, Discount: {product.discount}, Quantity: {quantity}")

    def search_product(self, product_name):
        found = False
        for product_data in self.products.values():
            product = product_data['product']
            if product.name_of_product.lower() == product_name.lower():
                print(f"ID: {product.id}, Name: {product.name_of_product}, Category: {product.category_of_product}, "
                      f"Price: {product.price}, Discount: {product.discount}, Quantity: {product_data['quantity']}")
                found = True
        if not found:
            print(f"No product found with the name '{product_name}'.")

    def save_stock(self, filename):
        with open(filename, 'w') as file:
            data = {'products': [
                {'product': vars(product_data['product']),
                 'quantity': product_data['quantity']}
                for product_data in self.products.values()
            ]}
            json.dump(data, file, indent=4, default=str)
        print(f"Stock saved to {filename}")

    def load_stock(self, filename='Meat_store.txt'):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                self.products = {
                    item['product']['_id']: {'product': self._deserialize_product(item['product']),
                                             'quantity': item['quantity']}
                    for item in data['products']
                }
            print(f"Stock loaded from {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found.")

    def _deserialize_product(self, data):
        if data['_category_of_product'] == 'meat_frozen':
            return MeatFrozen(data['_name_of_product'], data['_date_of_manufacture'], data['_expiration_date'], data['_price'], data['_discount'], data['_id'])
        elif data['_category_of_product'] == 'meat_fresh':
            return MeatFresh(data['_name_of_product'], data['_date_of_manufacture'], data['_expiration_date'], data['_price'], data['_discount'], data['_id'])
        elif data['_category_of_product'] == 'meat_products':
            return MeatProducts(data['_name_of_product'], data['_date_of_manufacture'], data['_expiration_date'], data['_price'], data['_discount'], data['_id'])

app = Flask(__name__)
stock = Stock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/import_stock', methods=['POST'])
def import_stock():
    filename = request.form['filename']
    stock.load_stock(filename)
    return redirect(url_for('index'))

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    category = request.form['category']
    date_of_manufacture = request.form['date_of_manufacture']
    expiration_date = request.form['expiration_date']
    price = float(request.form['price'])
    discount = float(request.form.get('discount', 0))

    if category == 'meat_frozen':
        product = MeatFrozen(name, date_of_manufacture, expiration_date, price, discount)
    elif category == 'meat_fresh':
        product = MeatFresh(name, date_of_manufacture, expiration_date, price, discount)
    elif category == 'meat_products':
        product = MeatProducts(name, date_of_manufacture, expiration_date, price, discount)
    else:
        return "Invalid category"

    stock.add_product(product)
    return redirect(url_for('index'))

@app.route('/sell_product', methods=['POST'])
def sell_product():
    product_id = request.form['product_id']
    stock.product_sold(product_id)
    return redirect(url_for('index'))

@app.route('/update_stock', methods=['POST'])
def update_stock():
    stock.update_stock()
    return redirect(url_for('index'))

@app.route('/apply_discount', methods=['POST'])
def apply_discount():
    stock.apply_discount()
    return redirect(url_for('index'))

@app.route('/display_stock')
def display_stock():
    return render_template('display_stock.html', products=stock.products.values())

@app.route('/search_product', methods=['POST'])
def search_product():
    product_name = request.form['product_name']
    found_products = [product_data for product_data in stock.products.values() if product_data['product'].name_of_product.lower() == product_name.lower()]
    return render_template('search_results.html', products=found_products, product_name=product_name)

@app.route('/save_stock', methods=['POST'])
def save_stock():
    filename = request.form['filename']
    stock.save_stock(filename)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
