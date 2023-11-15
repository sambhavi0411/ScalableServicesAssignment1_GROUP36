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

if _name_ == '__main__':
    app.run(host='0.0.0.0', port=5002)
