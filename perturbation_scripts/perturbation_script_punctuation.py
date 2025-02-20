import json
import os
import random

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def add_punctuation(text, level):
    punctuations = ["?", ".", ",", ";", ":", "'", "!"]
    chars = list(text)
    num_punctuations = int(len(chars) * (level / 100.0))
    indices = random.sample(range(len(chars)), num_punctuations)
    
    for index in indices:
        if chars[index].isalpha():
            chars[index] += random.choice(punctuations)
    
    return ''.join(chars)

def apply_perturbation(data, level):
    perturbed_data = []
    for item in data:
        perturbed_question = add_punctuation(item['question'], level)
        perturbed_data.append({
            "db_id": item["db_id"],
            "question": perturbed_question,
            "q_id": item["q_id"]
        })
    return perturbed_data

def main(input_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    original_data = load_json(input_file)
    
    levels = [25, 50, 75, 100]
    for level in levels:
        perturbed_data = apply_perturbation(original_data, level)
        output_file = os.path.join(output_dir, f'perturbation_{level}.json')
        save_json(perturbed_data, output_file)
        print(f"Saved perturbation level {level}% to {output_file}")


if __name__ == '__main__':
    input_file = './data_ibm/italian/google-translate/spider_google_translations.json'  # Input JSON file with statements
    output_dir = './data_ibm/new perturbations italian/punctuation_increase'    # Directory to save perturbation files
    main(input_file, output_dir) # Adjust max_punctuations as needed
