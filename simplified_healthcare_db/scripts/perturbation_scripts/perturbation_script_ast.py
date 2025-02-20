import json
import os
import random

def load_statements(input_file):
    with open(input_file, 'r') as file:
        data = json.load(file)
    return data

def perturb_statement(statement, percentage):
    num_chars = len(statement)
    num_to_replace = int(num_chars * (percentage / 100))
    
    indices = [i for i, c in enumerate(statement) if c.isalpha()]
    random.shuffle(indices)
    indices_to_replace = indices[:num_to_replace]
    
    perturbed_chars = list(statement)
    for idx in indices_to_replace:
        perturbed_chars[idx] = '*'
    
    return ''.join(perturbed_chars)

def generate_perturbations(statements, output_dir, steps=10):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i in range(steps + 1):
        percentage = i * (98 / steps)
        perturbed_data = []
        for entry in statements:
            perturbed_entry = entry.copy()
            perturbed_entry['question'] = perturb_statement(entry['question'], percentage)
            perturbed_data.append(perturbed_entry)
        
        output_file = os.path.join(output_dir, f'perturbation_{int(percentage)}.json')
        with open(output_file, 'w') as file:
            json.dump(perturbed_data, file, indent=4, ensure_ascii=False)
        print(f'Generated {output_file} with {int(percentage)}% perturbation')

def main(input_file, output_dir, steps=10):
    statements = load_statements(input_file)
    generate_perturbations(statements, output_dir, steps)

if __name__ == '__main__':
    input_file = './data_ibm/italian/google-translate/spider_google_translations.json'  # Input JSON file with statements
    output_dir = './data_ibm/new perturbations italian/asterisk_increase'    # Directory to save perturbation files
    main(input_file, output_dir, steps=10)
