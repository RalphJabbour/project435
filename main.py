from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

def create_app():
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    CORS(app)
    
    from service1 import serv
    from service2 import serv2
    from service3 import serv3
    
    app.register_blueprint(serv)
    app.register_blueprint(serv2)
    app.register_blueprint(serv3)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug = True, port=5000, host='0.0.0.0')