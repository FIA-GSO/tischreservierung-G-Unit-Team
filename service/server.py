import traceback
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

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

def is_table_available(tischnummer, zeitpunkt):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reservierungen WHERE tischnummer = ? AND zeitpunkt = ? AND storniert = "False"', (tischnummer, zeitpunkt))
    reservierung = cursor.fetchone()
    conn.close()
    return reservierung is None

@app.route('/reservierung', methods=['POST'])
def create_reservierung():
    data = request.json
    tischnummer = data['tischnummer']
    zeitpunkt = data['zeitpunkt']

    # Überprüfen, ob der Zeitpunkt in der Zukunft liegt
    if datetime.strptime(zeitpunkt, '%Y-%m-%d %H:%M:%S') <= datetime.now():
        return jsonify({'error': 'Zeitpunkt muss in der Zukunft liegen'}), 400

    # Überprüfen, ob der Tisch verfügbar ist
    if not is_table_available(tischnummer, zeitpunkt):
        return jsonify({'error': 'Tisch ist zu diesem Zeitpunkt nicht verfügbar'}), 400

    # Fügen Sie die neue Reservierung hinzu
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO reservierungen (zeitpunkt, tischnummer, pin, storniert) VALUES (?, ?, ?, "False")', (zeitpunkt, tischnummer, data['pin']))
        conn.commit()
        reservierungsnummer = cursor.lastrowid
        conn.close()
        return jsonify({'message': 'Reservierung erfolgreich erstellt', 'reservierungsnummer': reservierungsnummer}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reservierung/stornieren', methods=['POST'])
def storniere_reservierung():
    data = request.json
    reservierungsnummer = data.get('reservierungsnummer')

    if not reservierungsnummer:
        return jsonify({'error': 'Reservierungsnummer muss angegeben werden'}), 400

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Überprüfen, ob die Reservierung existiert
        cursor.execute('SELECT * FROM reservierungen WHERE reservierungsnummer = ?', (reservierungsnummer,))
        reservierung = cursor.fetchone()
        if not reservierung:
            return jsonify({'error': 'Reservierung nicht gefunden'}), 404

        # Stornieren der Reservierung
        cursor.execute('UPDATE reservierungen SET storniert = "True" WHERE reservierungsnummer = ?', (reservierungsnummer,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Reservierung erfolgreich storniert'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tische/frei', methods=['GET'])
def get_freie_tische():
    zeitpunkt = request.args.get('zeitpunkt')

    # Überprüfen, ob der Zeitpunkt angegeben wurde
    if not zeitpunkt:
        return jsonify({'error': 'Zeitpunkt muss angegeben werden'}), 400

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Wählen Sie alle Tische, die zu diesem Zeitpunkt nicht reserviert sind
        query = '''
        SELECT * FROM tische 
        WHERE tischnummer NOT IN (
            SELECT tischnummer FROM reservierungen 
            WHERE zeitpunkt = ? AND storniert = "False"
        )
        '''
        cursor.execute(query, (zeitpunkt,))
        freie_tische = cursor.fetchall()
        conn.close()

        return jsonify({'freie_tische': freie_tische})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reservierungen/all', methods=['GET'])
def get_reservierungen():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reservierungen')
    reservierungen = cursor.fetchall()
    conn.close()
    return jsonify({'reservierungen': reservierungen})

@app.route('/tische/all', methods=['GET'])
def get_tische():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tische')
    tische = cursor.fetchall()
    conn.close()
    return jsonify({'tische': tische})

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

if __name__ == "__main__":
    app.run(debug=True)
