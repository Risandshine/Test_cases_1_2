import logging
import mysql.connector
from mysql.connector import Error

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("car_rental_system.log"),
        logging.StreamHandler()
    ]
)

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='car_rental_system',
            user='root',  # replace with your MySQL username
            password='jekjek123'  # replace with your MySQL password
        )
        if connection.is_connected():
            logging.info("Database connection established successfully.")
            return connection
    except Error as e:
        logging.error(f"Error while connecting to MySQL: {e}")
    return None

def close_connection(connection, cursor):
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()
        logging.info("Database connection closed.")

def create_user(name, address, email, phone, password_hash):
    connection = create_connection()
    if not connection:
        logging.error("Database connection failed, user not created.")
        return False
    cursor = connection.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (name, address, email, phone, password_hash) VALUES (%s, %s, %s, %s, %s)',
            (name, address, email, phone, password_hash)
        )
        connection.commit()
        logging.info(f"User created successfully: {email}")
        return True
    except mysql.connector.Error as err:
        logging.error(f"Failed to create user {email}: {err}")
        return False
    finally:
        close_connection(connection, cursor)

def find_user_by_email(email):
    connection = create_connection()
    if not connection:
        logging.error("Database connection failed, user not found.")
        return None
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
    user = cursor.fetchone()
    close_connection(connection, cursor)
    if user:
        logging.info(f"User found: {email}")
    else:
        logging.warning(f"No user found for email: {email}")
    return user

def fetch_available_cars():
    connection = create_connection()
    if not connection:
        logging.error("Database connection failed, no cars fetched.")
        return []
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM cars WHERE available=TRUE')
    cars = cursor.fetchall()
    close_connection(connection, cursor)
    logging.info(f"Fetched {len(cars)} available cars.")
    return cars

def create_reservation(user_id, car_id, start_date, end_date, confirmation_number):
    connection = create_connection()
    if not connection:
        logging.error("Database connection failed, reservation not created.")
        return False
    cursor = connection.cursor()
    try:
        cursor.execute(
            'INSERT INTO reservations (user_id, car_id, start_date, end_date, confirmation_number) VALUES (%s, %s, %s, %s, %s)',
            (user_id, car_id, start_date, end_date, confirmation_number)
        )
        connection.commit()
        cursor.execute('UPDATE cars SET available=FALSE WHERE id=%s', (car_id,))
        connection.commit()
        logging.info(f"Reservation created successfully for user {user_id} and car {car_id}. Confirmation number: {confirmation_number}")
        return True
    except mysql.connector.Error as err:
        logging.error(f"Failed to create reservation for user {user_id} and car {car_id}: {err}")
        return False
    finally:
        close_connection(connection, cursor)

def fetch_car_by_id(car_id):
    connection = create_connection()
    if not connection:
        logging.error("Database connection failed, no car found.")
        return None
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM cars WHERE id=%s', (car_id,))
    car = cursor.fetchone()
    close_connection(connection, cursor)
    if car:
        logging.info(f"Car found: {car[1]}")
    else:
        logging.warning(f"No car found for ID: {car_id}")
    return car

def cancel_reservation_from_db(reservation_id):
    connection = create_connection()
    if not connection:
        logging.error("Database connection failed, reservation not canceled.")
        return False
    cursor = connection.cursor()
    try:
        # Mark the car as available again
        cursor.execute('SELECT car_id FROM reservations WHERE reservation_id = %s', (reservation_id,))
        car_id = cursor.fetchone()[0]
        cursor.execute('UPDATE cars SET available = TRUE WHERE id = %s', (car_id,))
        connection.commit()

        # Delete the reservation
        cursor.execute('DELETE FROM reservations WHERE reservation_id = %s', (reservation_id,))
        connection.commit()

        logging.info(f"Reservation {reservation_id} canceled successfully.")
        return True
    except mysql.connector.Error as err:
        logging.error(f"Failed to cancel reservation {reservation_id}: {err}")
        return False
    finally:
        close_connection(connection, cursor)


if __name__ == "__main__":
    connection = create_connection()
    if connection:
        print("Connection successful!")
    else:
        print("Failed to connect.")
