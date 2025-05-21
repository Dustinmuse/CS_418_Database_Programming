from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
import time
from datetime import datetime
import requests

# Load environment variables from .env file
load_dotenv(dotenv_path='c:\\CS418_Python\\fullstack_airline_booking_system\\mysql.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

current_time = int(time.time())
start_time = current_time - 3600

# OpenSky API endpoint to get all flight states
OPEN_SKY_API_URL = "https://opensky-network.org/api/states/all?begin={}&end={}".format(start_time, current_time)

# Database connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            host=os.getenv('MYSQL_HOST'),
            database=os.getenv('MYSQL_DATABASE')
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None


# Home route
@app.route('/')
def home():
    return render_template('index.html')


# User registration route (new user)
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        date_of_birth = request.form['date_of_birth']

        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Passengers (first_name, last_name, email, phone_number, date_of_birth)
            VALUES (%s, %s, %s, %s, %s)
        """, (first_name, last_name, email, phone_number, date_of_birth))
        connection.commit()
        passenger_id = cursor.lastrowid
        cursor.close()
        connection.close()

        return jsonify({"passenger_id": passenger_id})


# View booking route (for existing users)
@app.route('/booking/<int:passenger_id>')
def view_booking(passenger_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT b.booking_id, f.flight_number, b.seat_number, b.booking_date
        FROM bookings b
        JOIN Flights f ON b.flight_id = f.flight_id
        WHERE b.passenger_id = %s
    """, (passenger_id,))
    bookings = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('view_booking.html', bookings=bookings, passenger_id=passenger_id)


# Booking a flight route
@app.route('/book', methods=['POST'])
def book_flight():
    passenger_id = session.get('passenger_id')
    if not passenger_id:
        return "Error: User not logged in.", 401
    flight_id = request.form['flight_id']
    seat_number = request.form['seat_number']

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE flight_id = %s AND seat_number = %s", (flight_id, seat_number))
    if cursor.fetchone()[0] > 0:
        cursor.close()
        connection.close()
        return "Error: Seat is already taken!"

    cursor.execute("""
        INSERT INTO bookings (passenger_id, flight_id, seat_number, booking_date)
        VALUES (%s, %s, %s, NOW())
    """, (passenger_id, flight_id, seat_number))
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('view_booking', passenger_id=passenger_id))


@app.route('/available_flights')
def available_flights():
    # Fetch flight data from OpenSky API
    response = requests.get(OPEN_SKY_API_URL)

    if response.status_code == 200:
        data = response.json()  # Parse the JSON data
        flights = data['states'][:100]  # Extract and limit to the first 100 flights

        return render_template('available_flights.html', flights=flights)  # Pass the flight data to the template
    else:
        return "Error: Unable to fetch flight data from OpenSky API", 500


def insert_flights_from_api(connection, flights_data):
    try:
        cursor = connection.cursor()

        # Insert airports first (to avoid FK constraint issues)
        for flight in flights_data:
            departure_airport = flight.get("departure_airport", "UNKNOWN")[:10]  # Truncate to 10 characters
            arrival_airport = flight.get("arrival_airport", "UNKNOWN")[:10]  # Truncate to 10 characters

            # Insert airports for both departure and arrival
            for airport_code in [departure_airport, arrival_airport]:
                cursor.execute("""
                    INSERT INTO Airports (airport_code)
                    SELECT * FROM (SELECT %s) AS temp
                    WHERE NOT EXISTS (
                        SELECT 1 FROM Airports WHERE airport_code = %s
                    ) LIMIT 1;
                """, (airport_code, airport_code))

        connection.commit()

        # Fetch airport IDs into a dict
        cursor.execute("SELECT airport_id, airport_code FROM Airports")
        airport_id_map = {code: id_ for id_, code in cursor.fetchall()}

        # Insert flights
        for flight in flights_data:
            departure_id = airport_id_map.get(flight["departure_airport"][:10])
            arrival_id = airport_id_map.get(flight["arrival_airport"][:10])

            if departure_id and arrival_id:
                cursor.execute("""
                    INSERT IGNORE INTO Flights (flight_number, departure_airport, arrival_airport, departure_time, arrival_time)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    flight["flight_number"],
                    departure_id,
                    arrival_id,
                    flight["departure_time"],
                    flight["arrival_time"]
                ))

        connection.commit()
        print("Flights and airports inserted successfully!")

    except Error as e:
        print(f"Error inserting flights: {e}")
    finally:
        cursor.close()

def get_flights_data():
    url = OPEN_SKY_API_URL
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch flight data")
        return []

    data = response.json()
    flights = []
    states = data.get("states", [])

    for flight in states:
        callsign = flight[1].strip() if flight[1] else "UNKNOWN"

        # Use the raw callsign as the airport code
        departure_airport = callsign
        arrival_airport = callsign

        first_seen = flight[4]  # last_contact (best guess for departure)
        last_seen = flight[3]   # time_position (optional guess for arrival)

        departure_time = datetime.fromtimestamp(first_seen).strftime('%Y-%m-%d %H:%M:%S') if first_seen else None
        arrival_time = datetime.fromtimestamp(last_seen).strftime('%Y-%m-%d %H:%M:%S') if last_seen else None

        flight_info = {
            "flight_number": callsign,
            "departure_airport": departure_airport,
            "arrival_airport": arrival_airport,
            "departure_time": departure_time,
            "arrival_time": arrival_time
        }
        flights.append(flight_info)

    return flights


@app.route('/signup')
def signup():
    return render_template('signup.html')
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        passenger_id = request.form['passenger_id']

        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Passengers WHERE passenger_id = %s", (passenger_id,))
        result = cursor.fetchone()
        cursor.close()
        if result[0] > 0:
            session['passenger_id'] = passenger_id
            return render_template('main_menu.html', passenger_id=passenger_id)
        
    return render_template('login.html')

@app.route('/booking_form')
def booking_form():
    return render_template('booking_form.html')

@app.route('/main_menu')
def main_menu():
    passenger_id = session.get('passenger_id')
    if not passenger_id:
        return render_template('index.html')
    return render_template('main_menu.html', passenger_id=passenger_id)


if __name__ == "__main__":
    insert_flights_from_api(create_connection(), get_flights_data())
    app.run()