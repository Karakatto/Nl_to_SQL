import json
import os
import random

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def apply_wildcards(text, percentage):
    chars = list(text)
    num_changes = int(len(chars) * percentage)
    indices = random.sample(range(len(chars)), num_changes)
    wildcards = ['*', '#', '%', '!', '@', '$']

    for idx in indices:
        if chars[idx].isalnum():  # Replace only alphanumeric characters
            chars[idx] = random.choice(wildcards)
    
    return ''.join(chars)

def perturb_statements(statements, percentage):
    return [{'db_id': item['db_id'], 'question': apply_wildcards(item['question'], percentage), 'q_id': item['q_id']} for item in statements]

def main():
    input_file = './data_ibm/italian/google-translate/spider_google_translations.json'
    output_dir = './data_ibm/new perturbations italian/wildcard_changes'
    percentages = [0.0, 0.25, 0.50, 0.75, 1.0]
    
    # Load the original JSON file
    original_data = load_json(input_file)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate perturbed files for each percentage
    for percentage in percentages:
        perturbed_data = perturb_statements(original_data, percentage)
        output_file = os.path.join(output_dir, f'statements_wildcard_changes_{int(percentage * 100)}.json')
        save_json(perturbed_data, output_file)
        print(f'Saved perturbed file with {int(percentage * 100)}% wildcard changes to: {output_file}')

if __name__ == '__main__':
    main()
