import json
import os
import random

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def apply_resembling_wildcards(text, percentage):
    substitutions = {
        'a': '@', 'e': '&', 'i': '!', 's': '$', 'o': '0', 't': '7', 'l': '1'
    }
    
    chars = list(text)
    num_changes = int(len(chars) * percentage)
    indices = random.sample(range(len(chars)), num_changes)

    for idx in indices:
        if chars[idx].lower() in substitutions:
            chars[idx] = substitutions[chars[idx].lower()]
    
    return ''.join(chars)

def perturb_statements(statements, percentage):
    return [{'db_id': item['db_id'], 'question': apply_resembling_wildcards(item['question'], percentage), 'q_id': item['q_id']} for item in statements]

def main():
    input_file = './data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_healthcare.json'
    output_dir = './data_ibm/healthcare_db/simplified_db/italian/google-translate/perturbations/resembling_wildcard_changes'
    percentages = [0.0, 0.25, 0.50, 0.75, 1.0]
    
    # Load the original JSON file
    original_data = load_json(input_file)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate perturbed files for each percentage
    for percentage in percentages:
        perturbed_data = perturb_statements(original_data, percentage)
        output_file = os.path.join(output_dir, f'statements_resembling_wildcards_{int(percentage * 100)}.json')
        save_json(perturbed_data, output_file)
        print(f'Saved perturbed file with {int(percentage * 100)}% resembling wildcards to: {output_file}')

if __name__ == '__main__':
    main()
