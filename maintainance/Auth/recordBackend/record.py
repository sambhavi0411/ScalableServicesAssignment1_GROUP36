from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for the app

db_folder = 'db'  # Folder name
db_filename = 'orders.db'  # Database file name
database_path = os.path.join(db_folder, db_filename) 


# Database configuration function
def get_db_connection():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    return conn, cursor

# Create the "orders" and "order_status" tables and triggers
conn, cursor = get_db_connection()

cursor.execute('''
CREATE TRIGGER IF NOT EXISTS order_status_trigger
AFTER INSERT ON orders
FOR EACH ROW
BEGIN
    INSERT INTO order_status (order_id, status)
    VALUES (NEW.id, NEW.status);
END;
''')

cursor.execute('''
CREATE TRIGGER IF NOT EXISTS order_status_update_trigger
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
 UPDATE order_status
 SET status = NEW.status
 WHERE order_id = NEW.id;
END;
''')

cursor.execute('''
CREATE TRIGGER IF NOT EXISTS order_status_DELETE_trigger
BEFORE DELETE ON orders
FOR EACH ROW
BEGIN
    DELETE FROM order_status WHERE order_id = OLD.id;
END;
''')

conn.commit()
conn.close()

# Route for creating orders
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    conn, cursor = get_db_connection()
    cursor.execute('INSERT INTO orders (user_id, product_id, quantity, status) VALUES (?, ?, ?, ?)', (user_id, product_id, quantity, 'pending'))

    conn.commit()
    conn.close()

    return jsonify({"message": "Order created successfully"})

# Route for listing orders
@app.route('/orders', methods=['GET'])
def list_orders():
    conn, cursor = get_db_connection()
    cursor.execute('SELECT id, user_id, product_id, quantity, status FROM orders')
    orders = cursor.fetchall()
    conn.close()

    orders_data = [{'id': order[0], 'user_id': order[1], 'product_id': order[2], 'quantity': order[3], 'status': order[4] if len(order) > 4 else None} for order in orders]

    return jsonify({"orders": orders_data})

# Route for updating order status
@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order_status(order_id):
    data = request.get_json()
    status = data.get('status')

    conn, cursor = get_db_connection()
    cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Order status updated successfully"})

# Route for canceling orders
@app.route('/orders/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    conn, cursor = get_db_connection()
    cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Order canceled successfully"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
