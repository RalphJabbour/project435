from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS
import service1, service2
import sqlite3

service3 = Blueprint('service3', __name__)

# CORS(service3, resources={r"/*": {"origins": "*"}})

def connect_to_db():
    return sqlite3.connect("purchase_history.db")

def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''
                     CREATE TABLE purchase_history (
                     purchase_id INTEGER PRIMARY KEY NOT NULL,
                     username TEXT NOT NULL,
                     name TEXT NOT NULL,
                     quantity INTEGER NOT NULL,
                     price REAL NOT NULL,
                     );
                ''')
        conn.commit()
        print("Purchase History Table created successfully")
    except:
        print("Purchase History Table creation failed - Maybe table exists")
    finally:
        conn.close()

def get_good_by_name(name):
    good = {}
    try:
        conn = service2.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM inventory WHERE name = ?", (name,))
        row = cur.fetchone()
        if row:
            good = dict(row)
    except:
        good = {}
        print("Good retrieval failed")
    finally:
        conn.close()
    return good

def get_goods():
    goods = []
    try:
        conn = service2.connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM inventory")
        rows = cur.fetchall()
        for row in rows:
            item = {}
            item['name'] = row['name']
            item['price'] = row['price']
            goods.append(item)
        print("Goods retrieved successfully")
    except:
        goods = []
    finally:
        conn.close()
    return goods

def deduct_good_amount(good, quantity=1):
    try:
        conn = service2.connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE inventory SET quantity = quantity - ? WHERE name = ?", (quantity, good['name']))
        conn.commit()
        print("Good amount deducted successfully")
    except:
        conn.rollback()
        print("Good amount deduction failed")
    finally:
        conn.close()
