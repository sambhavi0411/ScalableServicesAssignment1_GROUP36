from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for the app

db_folder = 'db'  # Folder name
db_filename = 'orders.db'  # Database file name
database_path = os.path.join(db_folder, db_filename) 

# Route for listing order statuses
@app.route('/order_statuses', methods=['GET'])
def list_order_statuses():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute('select order_id, status from order_status')

    order_statuses = cursor.fetchall()
    conn.close()

    order_statuses_data = [{'id': order[0], 'status': order[1] if len(order) > 1 else None} for order in order_statuses]

    return jsonify({"order_statuses": order_statuses_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
