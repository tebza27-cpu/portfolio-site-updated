from flask import Flask, request, jsonify
import json,sqlite3

app = Flask(__name__)

@app.route('/')  # The root/Index of the server
def home():
    return '''<span style='text-align:center'>
                <h1>Acme Fertilizer Supply: Database Management</h1>
                <h3>Authorized Users Only</h3><hr/>
            </span>'''
            
@app.route('/revise')    # domain/revise route
def edit_request():
    brand = request.args.get('brand') #URL is of form http://domain/revise?brand=x&type=y 
    _type = request.args.get('type') 
    price = request.args.get('price') #URL is of form http://domain/revise?brand=x&type=y&price=value 
    if (not brand): # missing brand=name
        return jsonify({'error': 'Please provide fertilizer brand.'}), 400
    elif(not _type): # missing type=kind
        return jsonify({'error': 'Please provide fertilizer type.'}), 400
    elif(not price): # price=value not present if only getting price
        product = access_row(brand,_type)
        if(product):
            return jsonify(product)
        else:
            return jsonify({'Product not found': brand +":" + _type}), 400
    else:  # price=value  present if changing price
        product = access_row(brand,_type)  # get product with this brand and type
        if(product):
            price = float(price)   # change string from URL to decimal
            update_price(brand,_type,price) # Call SQL update method
            product = access_row(brand,_type)  # Get updated version (version in table)
            return jsonify(product)
        else:
           return jsonify({'Product not found': brand+"  :" + _type}), 400 

def access_row(which,chem):
    conn = sqlite3.Connection('supplies.db')  # Connect
    cursor = conn.cursor()   # Get cursor
    cursor.execute("SELECT * FROM fertilizers WHERE brand = ? and type=?", (which,chem))  #Read SQL
    product = cursor.fetchone()  #Get row
    conn.close() # release resources
    if product:
        return product  #Got a record
    else:
         return False 
    
def update_price(brand,_type,price):   # Delegate the updating to this function (decomposition)
    conn = sqlite3.connect('supplies.db') # Connect
    cursor = conn.cursor() # Get cursor
    result = cursor.execute('''UPDATE fertilizers SET price=? WHERE brand = ? and type=?''', (price,brand,_type))
    conn.commit() # Make changes permanent
    conn.close()  # release resources
    return result  
  
if __name__ == '__main__':
    app.run(debug=True)
