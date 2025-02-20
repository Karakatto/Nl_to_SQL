import json

# Paths to your files
txt_file_path = './data_ibm/healthcare_db/normalized_db/new_queries/all_queries.txt'
sql_file_path = './data_ibm/healthcare_db/normalized_db/new_queries/all_queries.sql'
output_json_path = 'combined_queries.json'

# Read the contents of the .txt file
with open(txt_file_path, 'r') as txt_file:
    questions = txt_file.readlines()

# Read the contents of the .sql file
with open(sql_file_path, 'r') as sql_file:
    queries = sql_file.readlines()

# Ensure both files have the same number of entries
assert len(questions) == len(queries), "The number of questions and queries do not match."

# Combine the questions and queries into a JSON structure
combined_data = []
for q_id, (question, query) in enumerate(zip(questions, queries), start=1):
    combined_data.append({
        "db_id": "hospital_management",
        "question": question.strip(),
        "query": query.strip(),
        "q_id": q_id
    })

# Write the combined data to a JSON file
with open(output_json_path, 'w') as json_file:
    json.dump(combined_data, json_file, indent=4)

print(f"Combined JSON file has been saved to {output_json_path}")
