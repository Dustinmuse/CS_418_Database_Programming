import os
import mysql.connector
from mysql.connector import Error
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path='c:\\CS418_Python\\fullstack_airline_booking_system\\mysql.env')

def create_connection():
    """
    Establish a connection to the airline database on a remote server.
    :return: Connection object or None if the connection fails.
    """
    try:
        connection = mysql.connector.connect(
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            host=os.getenv('MYSQL_HOST'),
            database=os.getenv('MYSQL_DATABASE')
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
            airport_name VARCHAR(100),
            airport_code VARCHAR(10) UNIQUE NOT NULL,
            location VARCHAR(100)
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


def insert_flights_from_api(connection, flights_data):
    try:
        cursor = connection.cursor()

        # Insert airports first (to avoid FK constraint issues)
        for flight in flights_data:
            departure_airport = flight.get("departure_airport")
            arrival_airport = flight.get("arrival_airport")

            # Handle missing airport codes
            if not departure_airport:
                # If missing departure airport, skip logging it here to avoid excessive output
                departure_airport = "UNKNOWN"  # Or some default value
            if not arrival_airport:
                # If missing arrival airport, skip logging it here to avoid excessive output
                arrival_airport = "UNKNOWN"  # Or some default value

            # Insert airports for both departure and arrival (even if they are "UNKNOWN")
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
            departure_id = airport_id_map.get(flight["departure_airport"])
            arrival_id = airport_id_map.get(flight["arrival_airport"])

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
    #current_time = int(time.time())
    #start_time = current_time - 3600
    url = f"https://opensky-network.org/api/states/all"

    response = requests.get(url)
    data = response.json()

    flights = []

    if isinstance(data, list):
        for flight in data:
            callsign = flight.get("callsign")
            first_seen = flight.get("firstSeen")
            last_seen = flight.get("lastSeen")
            departure_airport = flight.get("estDepartureAirport")
            arrival_airport = flight.get("estArrivalAirport")

            # Comment out or remove the print statement below to stop printing airport details
            # print(f"Departure Airport: {departure_airport}, Arrival Airport: {arrival_airport}")

            flight_info = {
                "flight_number": callsign.strip(),
                "departure_airport": departure_airport,
                "arrival_airport": arrival_airport,
                "departure_time": datetime.fromtimestamp(first_seen).strftime('%Y-%m-%d %H:%M:%S'),
                "arrival_time": datetime.fromtimestamp(last_seen).strftime('%Y-%m-%d %H:%M:%S') if last_seen else "N/A"
            }
            flights.append(flight_info)
    else:
        print("Data is not in the expected format!")

    return flights

def main():
    """
    Main function that displays a menu for users to interact with the airline booking system.
    """
    connection = create_connection()

    if not connection:
        print("Connection failed. Exiting program.")
        return

    create_tables(connection)
    # Get live flights from the API
    flights_data = get_flights_data()

    # Insert fetched flights into the database
    insert_flights_from_api(connection, flights_data)

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
    main()
