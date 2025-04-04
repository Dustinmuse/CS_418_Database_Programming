import mysql.connector

try:
    testConnection = mysql.connector.connect(
    user = "root",
    password = "Password",
    host = "localhost",
    database = "testDB")

    if testConnection.is_connected():
        print("Connected to MySQL database")

except mysql.connector.Error as err:
    print("Cannot connect to database:", err)
else:
    # Execute database operations...
    testConnection.close()