import json
import os
import random

# Function to substitute characters and add wildcards
def substitute_and_add_wildcards(text, wildcard_chance):
    original_text = text
    text = text.replace('e', '&').replace('a', '@').replace('s', '$')
    
    words = text.split()
    for i in range(len(words)):
        if random.random() < wildcard_chance:  # Apply wildcard chance
            words[i] = words[i] + random.choice('#%^*!~')
    return ' '.join(words)

def load_statements(input_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def generate_perturbations(statements, output_dir, max_steps=10):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for step in range(max_steps + 1):
        wildcard_chance = step / (max_steps * 5)  # Start with a very low chance and increase gradually
        perturbed_data = []
        for entry in statements:
            perturbed_entry = entry.copy()
            perturbed_entry['question'] = substitute_and_add_wildcards(entry['question'], wildcard_chance)
            perturbed_data.append(perturbed_entry)
        
        output_file = os.path.join(output_dir, f'wildcard_perturbation_{int(wildcard_chance * 100)}.json')
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(perturbed_data, file, ensure_ascii=False, indent=4)
        print(f'Generated {output_file} with {int(wildcard_chance * 100)}% wildcard perturbation')

def main(input_file, output_dir, max_steps=10):
    statements = load_statements(input_file)
    generate_perturbations(statements, output_dir, max_steps)

if __name__ == '__main__':
    input_file = './data_ibm/italian/google-translate/spider_google_translations.json'  # Input JSON file with statements
    output_dir = './data_ibm/new perturbations italian/wildcard_increase'  # Directory to save perturbation files
    main(input_file, output_dir, max_steps=10)  # Adjust max_steps as needed
