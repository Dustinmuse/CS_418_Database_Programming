# Airline Booking System

This project is a simple airline booking system that allows users to book flights, view their reservations, and cancel bookings using a MySQL database.

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- MySQL Server
- MySQL Connector for Python

### Setup
1. Clone this repository or download the script.
2. Install the required Python library:
   ```sh
   pip install mysql-connector-python
   ```
3. Set up your MySQL database and update the `create_connection()` function in the script with your MySQL credentials.
4. Run the script:
   ```sh
   python airline_booking_system.py
   ```

## Usage

Upon running the script, the system will:
1. Connect to the MySQL database.
2. Create necessary tables if they do not exist.
3. Insert default airport and flight data.
4. Prompt the user to register or log in.

### Features
- **Book a Flight:** Users can select a flight and book a seat.
- **View Reservation:** Users can see their bookings.
- **Cancel a Reservation:** Users can cancel their bookings.
- **View Available Flights:** Users can check for flights that are not fully booked.

### Exiting the Program
To exit the program, enter `5` in the option menu. (5 is the exit command)

## Database Schema
The database includes the following tables:
- `Passengers`: Stores passenger details.
- `Airports`: Stores airport information.
- `Flights`: Stores flight details including departure and arrival airports.
- `Bookings`: Stores flight reservations with passenger and flight references.

## Notes
- Ensure the MySQL server is running before executing the script.
- Provide valid MySQL credentials in `create_connection()`.