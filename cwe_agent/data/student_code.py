from flask import Flask, jsonify, request
import requests
import os


app = Flask(__name__)


# Simulating user carts stored in memory
cart = {}


# Use the environment variable for Product Service URL
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'https://product-service-niod.onrender.com/products')


# Endpoint to get the cart for a specific user
@app.route('/cart/<user_id>', methods=['GET'])
def get_cart(user_id):
    return jsonify(cart.get(user_id, {}))


# Endpoint to add a product to the cart for a specific user
@app.route('/cart/<user_id>/add/<int:product_id>', methods=['POST'])
def add_to_cart(user_id, product_id):
    logging.debug(f"Adding product {product_id} to cart for user {user_id}")
   
    # Get the quantity from the request body, default is 1 if not provided
    quantity = request.json.get('quantity', 1)


    # Fetch product details from Product Service
    product_response = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}")


    if product_response.status_code != 200:
        logging.error(f"Product {product_id} not found, received status code {product_response.status_code}")
        return jsonify({'message': 'Product not found'}), 404


    product = product_response.json()


    # Initialize cart for the user if not present
    cart.setdefault(user_id, {})


    # Add product to cart or update the quantity
    cart[user_id][product['name']] = cart[user_id].get(product['name'], 0) + quantity


    return jsonify(cart[user_id]), 201


# Endpoint to remove a product from the cart for a specific user
@app.route('/cart/<user_id>/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(user_id, product_id):
    # Get the quantity from the request body, default is 1 if not provided
    quantity = request.json.get('quantity', 1)


    # Fetch product details from Product Service
    product_response = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}")


    if product_response.status_code != 200:
        return jsonify({'message': 'Product not found'}), 404


    product = product_response.json()


    # Initialize cart for the user if not present
    cart.setdefault(user_id, {})


    # Check if the product exists in the user's cart
    if product['name'] in cart[user_id]:
        # Reduce the quantity or remove the product if the quantity goes to zero or below
        cart[user_id][product['name']] -= quantity
        if cart[user_id][product['name']] <= 0:
            del cart[user_id][product['name']]


    return jsonify(cart[user_id]), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)