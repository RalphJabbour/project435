from flask import Flask, Blueprint, jsonify, request
from flask_cors import CORS
import sqlite3

service2 = Blueprint('service2', __name__)
# CORS(service2, resources={r"/*": {"origins": "*"}})

def connect_to_db():
    return sqlite3.connect("inventory_database.db")

def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''
                     CREATE TABLE inventory (
                     item_id INTEGER PRIMARY KEY NOT NULL,
                     name TEXT NOT NULL,
                     category TEXT NOT NULL,
                     price REAL NOT NULL,
                     quantity INTEGER NOT NULL,
                     description TEXT NOT NULL,
                     );
                ''')
        conn.commit()
        print("Inventory Table created successfully")
    except:
        print("Inventory Table creation failed - Maybe table exists")
    finally:
        conn.close()

def get_good_by_name(name):
    good = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM inventory WHERE name = ?", (name,))
        row = cur.fetchone()
        if row:
            good = dict(row)
        print("Good retrieved successfully")
    except:
        good = {}
        print("Good retrieval failed")
    finally:
        conn.close()
    return good    

def add_good(good): #remove dictionary
    if get_good_by_name(good['name']):
        raise sqlite3.IntegrityError
    
    inserted_good = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO inventory (name, category, price, quantity, description) VALUES (?, ?, ?, ?, ?)", (good['name'], good['category'], good['price'], good['quantity'], good['description']))
        conn.commit()
        inserted_good = get_good_by_name(cur.lastrowid)
        print("Good added Successfully")
    except sqlite3.IntegrityError:
        conn.rollback()
        print("Good already exists")
    finally:
        conn.close()
    return inserted_good

def update_good(good):
    updated_good = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE inventory SET name = ?, category = ?, price = ?, quantity = ?, description = ? WHERE item_id = ?", (good['name'], good['category'], good['price'], good['quantity'], good['description'], good['item_id']))
        conn.commit()
        updated_good = get_good_by_name(good['name'])
        print("Good updated Successfully")
    except:
        conn.rollback()
        print("Good update failed")
    finally:
        conn.close()
    return updated_good

def deduct_good(name):
    message = {}
    try:
        with connect_to_db() as conn:
            conn.execute('''
                UPDATE inventory SET quantity = quantity - 1 WHERE name = ?;
            ''', (name['name'],))
            conn.commit()
            cursor = conn.execute('''
                SELECT quantity FROM inventory WHERE name = ?;
            ''', (name['name'],))
            quantity = cursor.fetchone()
            print("Good deducted successfully")
            message['quantity'] = quantity[0]
            message['status'] = "Good deducted successfully"
    except:
        print("Good deduction failed")
        message['status'] = "Good deduction failed"
    finally:
        conn.close()
    return message

def delete_good(name):
    message = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM inventory WHERE name = ?", (name['name'],))
        conn.commit()
        print("Good deleted successfully")
        message['status'] = "Good deleted successfully"
    except:
        print("Good deletion failed")
        message['status'] = "Good deletion failed"
    finally:
        conn.close()
    return message


@service2.route('/api/add_good', methods=['POST'])
def api_add_good():
    good = request.get_json()
    try:
        return jsonify(add_good(good))
    except:
        return jsonify({"status": "Good addition failed"})
    
@service2.route('/api/update_good', methods=['PUT'])
def api_update_good():
    good = request.get_json()
    return jsonify(update_good(good))

@service2.route('/api/deduct_good', methods=['PUT'])
def api_deduct_good():
    good = request.get_json()
    return jsonify(deduct_good(good))

@service2.route('/api/delete_good', methods=['DELETE'])
def api_delete_good():
    good = request.get_json()
    return jsonify(delete_good(good))
