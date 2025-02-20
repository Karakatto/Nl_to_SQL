def format_sql_query(sql_query):
    """
    Ensures the SQL query starts with "SELECT" and removes any trailing semicolon.

    Args:
    sql_query (str): The original SQL query.

    Returns:
    str: The formatted SQL query.
    """
    sql_query = sql_query.strip()
    
    # Add "SELECT" at the beginning if it doesn't already start with it
    if not sql_query.lower().startswith("select"):
        sql_query = "SELECT " + sql_query
    
    # Remove trailing semicolon
    if sql_query.endswith(";"):
        sql_query = sql_query[:-1]
    
    return sql_query

def process_sql_file(input_file, output_file):
    """
    Processes each SQL query in the input file and writes the formatted queries to the output file.

    Args:
    input_file (str): Path to the input file containing SQL queries.
    output_file (str): Path to the output file to save formatted SQL queries.
    """
    with open(input_file, 'r') as infile:
        sql_queries = infile.readlines()

    formatted_queries = [format_sql_query(query) for query in sql_queries]

    with open(output_file, 'w') as outfile:
        for query in formatted_queries:
            outfile.write(query + "\n")

# Example usage
input_file = './data_ibm/gpt-4/pred_gpt4.sql'
output_file = './data_ibm/gpt-4/pred_gpt4_formatted.sql'

process_sql_file(input_file, output_file)
