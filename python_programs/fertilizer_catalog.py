from flask import Flask, request, jsonify
import json,sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    return '''<span style='text-align:center'>
                <h1>Welcome to Acme Fertilizer Supply!</h1>
                <h3>The Farmer's Choice for Quality Fertilizer</h3>
            </span>'''
            
@app.route('/type')
def get_type():
    f_type = request.args.get('ftype')
    if f_type:
        products = get_type(f_type)
        return products
    else:
        return jsonify({'error': 'Type parameter is missing'}), 400

@app.route('/brand')
def by_brand():
    brand_name = request.args.get('name')
    if brand_name:
        products = get_brand(brand_name)
        return products
    else:
        return jsonify({'error': 'brand name parameter is missing'}), 400
    
@app.route('/cost')
def by_cost():
    price = request.args.get('price')
    if price:
        products = get_products(price)
        return products
    else:
        return jsonify({'error': 'Type parameter is missing'}), 400  
      
def get_type(ftype):
    conn = sqlite3.Connection('supplies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fertilizers WHERE type = ?", (ftype,))
    products = cursor.fetchall()
    if products:
        product_list = []
        for product in products:
            item = {'fertilizer_id': product[0], 'brand': product[1], 'price': product[2], 'type': product[3]}
            product_list.append(item)
        return jsonify(product_list)
    else:
        return jsonify({'message': 'No fertilizer of type '+ ftype + ' found'}), 404
    
def get_products(_price):
    conn = sqlite3.Connection('supplies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fertilizers WHERE price <= ?", (_price,))
    products = cursor.fetchall()
    if products:
        product_list = []
        for product in products:
            item = {'fertilizer_id': product[0], 'brand': product[1], 'price': product[2], 'type': product[3]}
            product_list.append(item)
        return jsonify(product_list)
    else:
        return jsonify({'message': 'No products found at or below '+ _price}), 404
        
def get_brand(the_brand):
    conn = sqlite3.Connection('supplies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fertilizers WHERE brand = ?", (the_brand,))
    products = cursor.fetchall()
    if products:
        product_list = []
        for product in products:
            item = {'fertilizer_id': product[0], 'brand': product[1], 'price': product[2], 'type': product[3]}
            product_list.append(item)
        return jsonify(product_list)
    else:
        return jsonify({'message': 'No ' + the_brand + ' brand fertilizers found '}), 404 
    
if __name__ == '__main__':
    app.run(debug=True)
