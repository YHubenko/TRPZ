import psycopg2


def get_database_connection():
    try:
        connection = psycopg2.connect(
            dbname='trpz',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432'
        )
        print("Connected to the database successfully.")
        return connection
    except Exception as e:
        print("Error connecting to the database:", e)
        return None


# Виклик функції для отримання з'єднання
conn = get_database_connection()