import sqlite3
import os

# Path to your SQLite database
db_path = './data_ibm/healthcare_db/simplified_db/simplified_healthcare.db'

# Path to the SQL queries file
sql_file_path = './data_ibm/healthcare_db/simplified_db/new_gold_queries.sql'

# Verify paths
print(f"Database path: {os.path.abspath(db_path)}")
print(f"SQL file path: {os.path.abspath(sql_file_path)}")

# Read queries from the .sql file
try:
    with open(sql_file_path, 'r') as file:
        sql_script = file.read()
    print("SQL file read successfully.")
except Exception as e:
    print(f"Failed to read SQL file: {e}")
    sql_script = ""

# Function to execute queries and log results
def execute_queries(conn, sql_script):
    cursor = conn.cursor()
    queries = sql_script.split(';')  # Changed to split by ';' to separate SQL queries
    log_lines = []
    for i, query in enumerate(queries):
        query = query.strip()
        if query:
            print(f"Executing Query {i+1}:\n{query}\n")  # Debugging print statement
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    log_lines.append(f"Query {i+1}: Success\nResults: {results}\n")
                else:
                    log_lines.append(f"Query {i+1}: Success\nNo results found.\n")
                print(f"Query {i+1}: Success\nResults: {results}\n")  # Debugging print statement
            except sqlite3.Error as e:
                log_lines.append(f"Query {i+1}: Failed - {e}\n")
                print(f"Query {i+1}: Failed - {e}\n")  # Debugging print statement
    return log_lines

# Connect to SQLite database and execute queries
try:
    conn = sqlite3.connect(db_path)
    print("Database connected successfully.")
    log_lines = execute_queries(conn, sql_script)
    conn.close()
    print("Database connection closed.")
except Exception as e:
    print(f"Failed to connect to the database: {e}")
    log_lines = []

# Write the log to a file
log_file_path = './data_ibm/healthcare_db/simplified_db/new_queries_results_gold.log'
try:
    with open(log_file_path, 'w') as log_file:
        for line in log_lines:
            log_file.write(line)
            print(line)  # Debugging print statement
    print(f"Query execution completed. Results are logged in {log_file_path}")
except Exception as e:
    print(f"Failed to write to log file: {e}")
