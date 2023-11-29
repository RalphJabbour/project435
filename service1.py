from flask import Blueprint, jsonify, request
from flask_cors import CORS
import sqlite3


service1 = Blueprint('service1', __name__)
# CORS(service1, resources={r"/*": {"origins": "*"}})




def connect_to_db():
    return sqlite3.connect("customer_database.db")

def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''
                     CREATE TABLE customers (
                     customer_id INTEGER PRIMARY KEY NOT NULL,
                     full_name TEXT NOT NULL,
                     username TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL,
                     age TEXT NOT NULL,
                     address TEXT NOT NULL,
                     gender TEXT NOT NULL,
                     marital_status TEXT NOT NULL,
                     wallet_balance REAL DEFAULT 0.0,
                     );
                ''')
        conn.commit()
        print("Customer Table created successfully")
    except:
        print("User Table creation failed - Maybe table exists")
    finally:
        conn.close()

def add_customer(customer):
    if get_customer_by_username(customer['username']):
        raise sqlite3.IntegrityError
    
    inserted_customer = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO customers (full_name, username, password, age, address, gender, marital_status) VALUES (?, ?, ?, ?, ?, ?, ?)", (customer['full_name'], customer['username'], customer['password'], customer['age'], customer['address'], customer['gender'], customer['marital_status']))
        conn.commit()
        inserted_customer = get_customer_by_id(cur.lastrowid)
    except sqlite3.IntegrityError:
        conn.rollback()
        print("User already exists")
    finally:
        conn.close()
    return inserted_customer

def get_customers():
    customers = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers")
        rows = cur.fetchall()

        #convert row objects to dictionary
        for row in rows:
            customer = dict(row)
            customers.append(customer)
    except:
        customers = []
    finally:
        conn.close()
    return customers

def get_customer_by_id(customer_id):
    customer = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
        row = cur.fetchone()
        if row:
            customer = dict(row)
    except:
        customer = {}
    finally:
        conn.close()
    return customer

def get_customer_by_username(username):
    customer = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers WHERE username = ?", (username,))
        row = cur.fetchone()
        if row:
            customer = dict(row)
    except:
        customer = {}
    finally:
        conn.close()
    return customer

def update_customer(customer):
    updated_customer = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE customers SET full_name = ?, password = ?, age = ?, address = ?, gender = ?, marital_status = ? WHERE username = ?",
                    (customer["full_name"], customer["password"], customer["age"], customer["address"], customer["gender"], customer["marital_status"], customer["username"]))
        conn.commit()
        updated_customer = get_customer_by_username(customer["username"])
    except:
        conn.rollback()
        updated_customer = {}
    finally:
        conn.close()
    return updated_customer

def delete_customer(username):
    message = {}
    try:
        conn = connect_to_db()
        conn.execute("DELETE FROM customers WHERE username = ?", (username,))
        conn.commit()
        message["status"] = "Customer deleted successfully"
    except:
        conn.rollback()
        message["status"] = "Cannot delete customer"
    finally:
        conn.close()
    return message

def charge_customer_wallet(username, value):
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE customers SET wallet_balance = wallet_balance + ? WHERE username = ?", (value, username))
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

def deduct_customer_wallet(username, value):
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE customers SET wallet_balance = wallet_balance - ? WHERE username = ?", (value, username))
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

create_db_table()

@service1.route('/api/customers', methods=['GET'])
def api_get_customers():
    return jsonify(get_customers())

@service1.route('/api/customers/<customer_id>', methods=['GET'])
def api_get_customer(customer_id):
    return jsonify(get_customer_by_id(customer_id))

@service1.route('/api/customers/add', methods=['POST'])
def api_add_customer():
    customer = request.get_json()
    try:
        return jsonify(add_customer(customer))
    except:
        return jsonify({"status": "Customer addition failed"})
    
@service1.route('/api/customers/update', methods=['PUT'])
def api_update_customer():
    customer = request.get_json()
    return jsonify(update_customer(customer))

@service1.route('/api/customers/delete/<username>', methods=['DELETE'])
def api_delete_customer(username):
    return jsonify(delete_customer(username))

@service1.route('/api/customers/charge', methods=['PUT'])
def api_charge_customer():
    customer = request.get_json()
    charge_customer_wallet(customer["username"], customer["value"])
    return jsonify(get_customer_by_username(customer["username"]))

@service1.route('/api/customers/deduct', methods=['PUT'])
def api_deduct_customer():
    customer = request.get_json()
    deduct_customer_wallet(customer["username"], customer["value"])
    return jsonify(get_customer_by_username(customer["username"]))