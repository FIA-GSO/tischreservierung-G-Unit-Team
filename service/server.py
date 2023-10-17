from flask import Flask

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'buchungssystem.sqlite'


@app.route('/reservierungen', methods=['GET'])
def get_reservierungen():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reservierungen')
    reservierungen = cursor.fetchall()
    conn.close()
    return jsonify({'reservierungen': reservierungen})

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
