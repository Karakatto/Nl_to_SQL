# Define the input and output file paths
input_file_path = './predictions/healthcare/meta-llama/llama-3-8b-instruct/english/pred_250tok.sql'
output_file_path = './predictions/healthcare/meta-llama/llama-3-8b-instruct/english/pred_250tok2.sql'

# Read the SQL statements from the input file
with open(input_file_path, 'r') as input_file:
    sql_statements = input_file.readlines()

# Add a semicolon to the end of each statement
sql_statements_with_semicolon = [statement.strip() + ";" for statement in sql_statements]

# Write the modified statements to the output file
with open(output_file_path, 'w') as output_file:
    for statement in sql_statements_with_semicolon:
        output_file.write(statement + '\n')

print(f"Modified SQL statements have been written to {output_file_path}")
