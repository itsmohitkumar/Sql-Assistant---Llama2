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
csv_file_path = 'database/data/World-happiness-reportcsv.csv'

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
        table_name = 'your_table_name'
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            country_name VARCHAR(255),
            year INT,
            life_ladder FLOAT,
            log_gdp_per_capita FLOAT,
            social_support FLOAT,
            healthy_life_expectancy FLOAT,
            freedom_to_make_life_choices FLOAT,
            generosity FLOAT,
            perceptions_of_corruption FLOAT,
            positive_affect FLOAT,
            negative_affect FLOAT
        )
        """
        cursor.execute(create_table_query)
        print(f"Table {table_name} created or already exists.")

        # Insert DataFrame into MySQL table using executemany for batch insertion
        insert_query = f"""
        INSERT INTO {table_name} (
            country_name, year, life_ladder, log_gdp_per_capita, social_support,
            healthy_life_expectancy, freedom_to_make_life_choices, generosity,
            perceptions_of_corruption, positive_affect, negative_affect
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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