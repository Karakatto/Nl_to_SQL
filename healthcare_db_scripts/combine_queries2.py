import json

# File paths
txt_file_path = './data_ibm/healthcare_db/simplified_db/italian/google-translate/questions_translated.txt'
output_json_path = './data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_healthcare.json'

# Read NL questions
with open(txt_file_path, 'r') as txt_file:
    nl_questions = txt_file.readlines()

# Combine NL questions into JSON format
combined_data = []
for i, question in enumerate(nl_questions, start=1):
    combined_data.append({
        "db_id": "healthcare_simplified",
        "question": question.strip(),
        "q_id": i
    })

# Write the combined data to a JSON file
with open(output_json_path, 'w') as json_file:
    json.dump(combined_data, json_file, indent=4)

print(f"Combined JSON file created successfully at {output_json_path}")
