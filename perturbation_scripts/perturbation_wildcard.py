import json
import random

# Function to substitute characters and add wildcards
def substitute_and_add_wildcards(text):
    text = text.replace('e', '&').replace('a', '@').replace('s', '$')
    words = text.split()
    for i in range(len(words)):
        if random.random() < 0.3:  # Approximately every third word gets a wildcard
            words[i] = words[i] + random.choice('#%^*!~')
    return ' '.join(words)

# Load the original JSON file
with open('./data_ibm/italian/google-translate/spider_google_translations.json', 'r', encoding='utf-8') as file:
    original_data = json.load(file)

# Apply the substitutions and wildcard additions to each question in the original data
for item in original_data:
    item['question'] = substitute_and_add_wildcards(item['question'])

# Save the new JSON file with character substitutions and wildcards
output_path = './data_ibm/new perturbations italian/GPT4.o_pert/rephrased_varied_wildcards_trans.json'
with open(output_path, 'w', encoding='utf-8') as file:
    json.dump(original_data, file, ensure_ascii=False, indent=4)

print(f"New JSON file saved to: {output_path}")
