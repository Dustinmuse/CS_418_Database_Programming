import mysql.connector
from mysql.connector import Error
import requests
import time
from datetime import datetime


def create_connection():
    """
    Establish a connection to the airline database on a remote server.
    :return: Connection object or None if the connection fails.
    """
    try:
        connection = mysql.connector.connect(
            user="root",
            password="",
            host="localhost",
            database="airline_booking"
        )
        print("Connected to the airline database successfully!")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None


def create_tables(connection):
    """
    Create all necessary tables for the airline booking system.
    """
    cursor = connection.cursor()

    queries = [
        """CREATE TABLE IF NOT EXISTS Passengers (
            passenger_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone_number VARCHAR(20) NOT NULL,
            date_of_birth DATE NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS Airports (
            airport_id INT AUTO_INCREMENT PRIMARY KEY,
            airport_name VARCHAR(100) NOT NULL,
            location VARCHAR(100) NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS Flights (
            flight_id INT AUTO_INCREMENT PRIMARY KEY,
            flight_number VARCHAR(10) UNIQUE NOT NULL,
            departure_airport INT NOT NULL,
            arrival_airport INT NOT NULL,
            departure_time DATETIME NOT NULL,
            arrival_time DATETIME NOT NULL,
            FOREIGN KEY (departure_airport) REFERENCES Airports(airport_id) ON DELETE CASCADE,
            FOREIGN KEY (arrival_airport) REFERENCES Airports(airport_id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS Bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            passenger_id INT NOT NULL,
            flight_id INT NOT NULL,
            booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            seat_number VARCHAR(10) NOT NULL,
            FOREIGN KEY (passenger_id) REFERENCES Passengers(passenger_id) ON DELETE CASCADE,
            FOREIGN KEY (flight_id) REFERENCES Flights(flight_id) ON DELETE CASCADE
        );"""
    ]

    try:
        for query in queries:
            cursor.execute(query)
        print("All tables created successfully!")
    except Error as e:
        print(f"Error creating tables: {e}")
    finally:
        cursor.close()


def insert_booking(connection, passenger_id, flight_id, seat_number):
    """
    Insert a new booking into the Bookings table.
    """
    try:
        cursor = connection.cursor()

        # Check if the seat is already booked
        cursor.execute("SELECT COUNT(*) FROM Bookings WHERE flight_id = %s AND seat_number = %s",
                       (flight_id, seat_number))
        if cursor.fetchone()[0] > 0:
            print("Error: Seat is already taken!")
            return

        # Insert the booking
        cursor.execute("""
            INSERT INTO Bookings (passenger_id, flight_id, seat_number, booking_date)
            VALUES (%s, %s, %s, NOW())
        """, (passenger_id, flight_id, seat_number))
        connection.commit()
        print("Booking successful!")

    except Error as e:
        print(f"Error: {e}")

    finally:
        cursor.close()


def view_booking(connection, passenger_id):
    """
    Retrieve and display bookings for a given passenger.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT b.booking_id, f.flight_number, b.seat_number, b.booking_date
            FROM Bookings b
            JOIN Flights f ON b.flight_id = f.flight_id
            WHERE b.passenger_id = %s
        """, (passenger_id,))

        bookings = cursor.fetchall()
        if not bookings:
            print("No bookings found for this passenger.")
        else:
            print("\nYour Reservations:")
            print("-" * 40)
            for booking in bookings:
                print(f"Booking ID: {booking[0]}, Flight: {booking[1]}, Seat: {booking[2]}, Date: {booking[3]}")
            print("-" * 40)

    except Error as e:
        print(f"Error: {e}")

    finally:
        cursor.close()


def delete_booking(connection, booking_id):
    """
    Cancel a booking by deleting it from the database.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Bookings WHERE booking_id = %s", (booking_id,))
        connection.commit()

        if cursor.rowcount > 0:
            print("Booking canceled successfully!")
        else:
            print("Error: Booking not found.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        cursor.close()


def insert_default_flights(connection):
    """
    Insert default airports and flights into the database if they do not already exist.
    """
    airports = [
        ("JFK International", "New York, USA"),
        ("LAX International", "Los Angeles, USA"),
        ("O'Hare International", "Chicago, USA"),
        ("Spaxial International", "Indianapolis, USA")
    ]

    try:
        cursor = connection.cursor()

        # Insert default airports (if they don’t exist)
        for airport in airports:
            cursor.execute("""
                INSERT INTO Airports (airport_name, location)
                SELECT * FROM (SELECT %s AS airport_name, %s AS location) AS temp
                WHERE NOT EXISTS (
                    SELECT 1 FROM Airports WHERE airport_name = %s AND location = %s
                ) LIMIT 1
            """, (airport[0], airport[1], airport[0], airport[1]))

        connection.commit()
        print("Default airports inserted successfully!")

        # Fetch airport IDs
        cursor.execute("SELECT airport_id, airport_name FROM Airports")
        airport_dict = {name: airport_id for airport_id, name in cursor.fetchall()}

        # Define flights using actual airport IDs
        flights = [
            ("FL1001", airport_dict["JFK International"], airport_dict["LAX International"], "2025-04-01 08:00:00",
             "2025-04-01 12:00:00"),
            ("FL1002", airport_dict["LAX International"], airport_dict["O'Hare International"], "2025-04-02 10:00:00",
             "2025-04-02 14:00:00"),
            ("FL1003", airport_dict["O'Hare International"], airport_dict["JFK International"], "2025-04-03 15:00:00",
             "2025-04-03 19:00:00"),
            ("FL1004", airport_dict["Spaxial International"], airport_dict["JFK International"], "2025-04-04 19:00:00",
             "2025-04-04 23:00:00")
        ]

        # Insert default flights
        for flight in flights:
            cursor.execute("""
                INSERT IGNORE INTO Flights (flight_number, departure_airport, arrival_airport, departure_time, arrival_time)
                VALUES (%s, %s, %s, %s, %s)
            """, flight)

        connection.commit()
        print("Default flights inserted successfully!")

    except Error as e:
        print(f"Error inserting default airports or flights: {e}")
    finally:
        cursor.close()


def view_available_flights(connection):
    """
    Retrieve and display available flights that are not fully booked.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT f.flight_id, f.flight_number, f.departure_time, f.arrival_time
            FROM Flights f
            LEFT JOIN Bookings b ON f.flight_id = b.flight_id
            GROUP BY f.flight_id, f.flight_number, f.departure_time, f.arrival_time
        """)

        flights = cursor.fetchall()
        if not flights:
            print("No available flights at the moment.")
        else:
            print("\nAvailable Flights:")
            print("-" * 50)
            for flight in flights:
                print(
                    f"Flight ID: {flight[0]}, Flight Number: {flight[1]}, Departure: {flight[2]}, Arrival: {flight[3]}")
            print("-" * 50)
    except Error as e:
        print(f"Error retrieving available flights: {e}")
    finally:
        cursor.close()

def get_flights_data():

    # Define time range (last hour)
    end_time = int(time.time())  # Current timestamp
    start_time = end_time - 3600  # One hour ago

    # OpenSky API URL for flights
    url = f"https://opensky-network.org/api/flights/all?begin={start_time}&end={end_time}"

    response = requests.get(url)
    data = response.json()

    flights = []  # List to store flight details

    for flight in data:
        if flight["callsign"]:  # Ensure flight number exists
            flight_info = {
                "flight_number": flight["callsign"].strip(),
                "departure_time": datetime.fromtimestamp(flight["firstSeen"]).strftime('%Y-%m-%d %H:%M:%S'),
                "arrival_time": datetime.fromtimestamp(flight["lastSeen"]).strftime('%Y-%m-%d %H:%M:%S')
            }
            flights.append(flight_info)

    print(flights)


def main():
    """
    Main function that displays a menu for users to interact with the airline booking system.
    """
    connection = create_connection()

    if not connection:
        print("Connection failed. Exiting program.")
        return

    create_tables(connection)
    insert_default_flights(connection)  # Ensure default flights exist

    while True:
        user_type = input("Are you a new or existing user? (new/existing): ").strip().lower()

        if user_type == "new":
            print("Please register as a new passenger.")
            first_name = input("Enter First Name: ")
            last_name = input("Enter Last Name: ")
            email = input("Enter Email: ")
            phone_number = input("Enter Phone Number: ")
            date_of_birth = input("Enter Date of Birth (YYYY-MM-DD): ")

            try:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO Passengers (first_name, last_name, email, phone_number, date_of_birth)
                    VALUES (%s, %s, %s, %s, %s)
                """, (first_name, last_name, email, phone_number, date_of_birth))
                connection.commit()
                passenger_id = cursor.lastrowid
                print(f"Registration successful! Your Passenger ID is {passenger_id}")
                cursor.close()
            except Error as e:
                print(f"Error: {e}")
                return

            break

        elif user_type == "existing":
            try:
                passenger_id = int(input("Enter your Passenger ID: "))
                break
            except ValueError:
                print("Invalid Passenger ID. Please enter a valid number.")

        else:
            print("Invalid choice. Please enter 'new' or 'existing'.")

    while True:
        print("\nAirline Booking System")
        print("1: Book a Flight")
        print("2: View Your Reservation")
        print("3: Cancel a Reservation")
        print("4: View Available Flights")
        print("5: Exit")

        choice = input("Select an option (1-5): ")

        match choice:
            case "1":
                try:
                    flight_id = int(input("Enter Flight ID: "))
                    seat_number = input("Enter Seat Number (e.g., 12A): ")
                    insert_booking(connection, passenger_id, flight_id, seat_number)
                except ValueError:
                    print("Invalid input. Please enter numeric values where required.")

            case "2":
                view_booking(connection, passenger_id)

            case "3":
                try:
                    booking_id = int(input("Enter Booking ID to cancel: "))
                    delete_booking(connection, booking_id)
                except ValueError:
                    print("Invalid input. Please enter a valid Booking ID.")

            case "4":
                view_available_flights(connection)

            case "5":
                print("Thank you for using the Airline Booking System. Goodbye!")
                break

            case _:
                print("Invalid choice. Please enter a number between 1 and 5.")

    connection.close()


if __name__ == "__main__":
    get_flights_data()
