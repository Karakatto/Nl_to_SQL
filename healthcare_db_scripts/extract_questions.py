import json

# Function to load JSON data from a file
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function to extract questions and write them to a text file
def extract_questions(json_data, output_file):
    questions = [item["question"] for item in json_data]
    with open(output_file, 'w') as file:
        for question in questions:
            file.write(question + '\n')

# Define the input and output file paths
input_file = './data_ibm/healthcare_db/simplified_db/perturbation_questions/resembling_wildcard_changes/statements_resembling_wildcards_75.json'
output_file = './data_ibm/healthcare_db/simplified_db/perturbation_questions/resembling_wildcard_changes/statements_resembling_wildcards_75.txt'

# Load the JSON data
json_data = load_json(input_file)

# Extract the questions and write them to the text file
extract_questions(json_data, output_file)

print(f"Questions have been extracted to {output_file}")
