import psycopg2
import csv

# Database connection parameters
conn = psycopg2.connect(
    dbname="llama",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Create table
cur.execute('''
CREATE TABLE IF NOT EXISTS world_happiness_report (
    country_name VARCHAR(255),
    year INT,
    life_ladder FLOAT,
    log_gdp_per_capita FLOAT,
    social_support FLOAT,
    healthy_life_expectancy_at_birth FLOAT,
    freedom_to_make_life_choices FLOAT,
    generosity FLOAT,
    perceptions_of_corruption FLOAT,
    positive_affect FLOAT,
    negative_affect FLOAT
)
''')

# Path to the CSV file
csv_file_path = 'C:\\Users\\Mohit Chaudhary\\Documents\\GitHub\\Sql-Assistant---Llama2\\database\\data\\World-happiness-reportcsv.csv'

# Function to convert empty strings to None
def convert_empty_to_none(value):
    return None if value == '' else value

# Load CSV data into the table
with open(csv_file_path, 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip the header row
    for row in reader:
        # Apply conversion to each element in the row
        row = [convert_empty_to_none(value) for value in row]
        cur.execute('''
        INSERT INTO world_happiness_report (country_name, year, life_ladder, log_gdp_per_capita, social_support, healthy_life_expectancy_at_birth, freedom_to_make_life_choices, generosity, perceptions_of_corruption, positive_affect, negative_affect)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', row)

conn.commit()
cur.close()
conn.close()
