import mysql.connector
from mysql.connector import Error
import json

with open(r'C:/Users/Mever/OneDrive/Рабочий стол/programs/nerostat_parsers/player_table_parser/config.json') as c:
    config = json.load(c)


def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database_name']
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_read_query(query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        cursor.close()


connection = create_connection()
cursor = connection.cursor()

