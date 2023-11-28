import traceback

from flask import Flask

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'buchungssystem.sqlite'


def init_db():
    print("Initializing database")
    try:

        with sqlite3.connect(DATABASE) as con:

            with open("create_buchungssystem.sql", "r") as f:
                con.executescript(f.read())

    except Exception as e:

        print(f"Error initializing database: {e}")
        traceback.print_exc()


@app.route('/reservierungen/all', methods=['GET'])
def get_reservierungen():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reservierungen')
    reservierungen = cursor.fetchall()
    conn.close()
    return jsonify({'reservierungen': reservierungen})


# get all tische from database
@app.route('/tische/all', methods=['GET'])
def get_tische():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tische')
    tische = cursor.fetchall()
    conn.close()
    return jsonify({'tische': tische})


# show all reserved tables ordered by time
@app.route('/reservierungen/reserved', methods=['GET'])
def get_reserved_tische():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT tischnummer, zeitpunkt FROM reservierungen ORDER BY zeitpunkt ASC')
    tische = cursor.fetchall()
    conn.close()
    return jsonify({'tische': tische}), 200


@app.route("/")
def hello_world():
    init_db()
    app.logger.info("Database connection successful")
    print("App started")
    return "Database connection successful", 200
