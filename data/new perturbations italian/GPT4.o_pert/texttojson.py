import json

# Define the paths to the files
questions_file_path = './data_ibm/new perturbations italian/GPT4.o_pert/rephrasing_ita_chatgpt.txt'
template_json_path = './data_ibm/italian/google-translate/spider_google_translations.json'
output_json_path = './data_ibm/new perturbations italian/GPT4.o_pert/rephrased_italian_gpt4.json'

# Load the questions from the text file
with open(questions_file_path, 'r', encoding='utf-8') as file:
    questions = file.read().strip().split('\n')

# Load the template JSON to get the correct db_id mappings
with open(template_json_path, 'r', encoding='utf-8') as file:
    template_json_data = json.load(file)

# Initialize a list to hold the new JSON structure
new_json_data = []

# Iterate over the questions and match with the template JSON for db_id
for idx, question in enumerate(questions):
    # Determine the db_id by cycling through the template JSON structure
    db_id = template_json_data[idx % len(template_json_data)]['db_id']
    
    # Create a new entry for the question
    new_entry = {
        "db_id": db_id,
        "question": question,
        "q_id": idx
    }
    new_json_data.append(new_entry)

# Save the new JSON structure
with open(output_json_path, 'w', encoding='utf-8') as file:
    json.dump(new_json_data, file, ensure_ascii=False, indent=4)

print(f"New JSON file saved to {output_json_path}")
