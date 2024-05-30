import pandas as pd
import mysql.connector
from mysql.connector import Error

# MySQL connection details
hostname = "qy1.h.filess.io"
database = "Chatbot_mouthtask"
port = 3307
username = "Chatbot_mouthtask"
password = "2ac46addfbe24acab97420c6aff9f01e57d63821"

# CSV file path
csv_file_path = 'data/pizza_sales.csv'  # Update with the actual path

try:
    # Establish the connection
    connection = mysql.connector.connect(
        host=hostname,
        database=database,
        user=username,
        password=password,
        port=port
    )
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file_path)
        
        # Create table based on CSV columns
        table_name = 'pizzas'
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            pizza_id FLOAT,
            order_id FLOAT,
            pizza_name_id VARCHAR(255),
            quantity FLOAT,
            order_date VARCHAR(255),
            order_time VARCHAR(255),
            unit_price FLOAT,
            total_price FLOAT,
            pizza_size VARCHAR(5),
            pizza_category VARCHAR(50),
            pizza_ingredients TEXT,
            pizza_name VARCHAR(255)
        )
        """
        cursor.execute(create_table_query)
        print(f"Table {table_name} created or already exists.")

        # Insert DataFrame into MySQL table using executemany for batch insertion
        insert_query = f"""
        INSERT INTO {table_name} (
            pizza_id, order_id, pizza_name_id, quantity, order_date, order_time, 
            unit_price, total_price, pizza_size, pizza_category, pizza_ingredients, pizza_name
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = [tuple(row) for row in df.values]
        cursor.executemany(insert_query, data)
        
        connection.commit()
        print(f"Data from {csv_file_path} has been inserted into {table_name} table.")

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    # Close the connection in the finally block to ensure it's closed even if an exception occurs
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
