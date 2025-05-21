import mysql.connector # type: ignore

def create_connection():
    try:
        connection = mysql.connector.connect(
        user = "",
        password = "",
        host = "",
        database = "")

        if connection.is_connected():
            print("Connected to MySQL database")

    except mysql.connector.Error as err:
        print("Cannot connect to database:", err)

    return connection

def create_table(connection):
    cursor = connection.cursor() # must match name at top when connecting
    table = ('create table Students ('
            'ID int primary key not null,'
            'Name varchar(50),'
            'Email varchar(100),'
            'Age int,'
            'Year varchar(30) )')
    
    cursor.execute(table)
    
    connection.commit()
    connection.close()
    
def insert_student(connection):
    print('ID? ', end = '')
    id = input()
    print('Name? ', end = '')
    name = input()
    print('Email? ', end = '')
    email = input()
    print('Age? ', end = '')
    age = input()
    print('Year? ', end = '')
    year = input()

    cursor = connection.cursor()
    data_to_insert = ('insert into Students'
                      '(ID, Name, Email, Age, Year)'
                      'values (%s, %s, %s, %s, %s)')
    
    student_data = (id, name, email, age, year)
    cursor.execute(data_to_insert, student_data)

    connection.commit()
    connection.close()

def select_all_students(connection):
    cursor = connection.cursor()
    cursor.execute('select * from Students')
    for row in cursor.fetchall():
        print(row)

    connection.commit()
    connection.close()

def __main__():
    create_connection()
    create_table(create_connection())
    insert_student(create_connection())
    select_all_students(create_connection())

__main__()