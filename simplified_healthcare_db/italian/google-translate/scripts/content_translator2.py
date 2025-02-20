import json
from deep_translator import GoogleTranslator
import os

# Define the base path and output folder
base_path = "data_ibm/healthcare_db/simplified_db/italian/google-translate/json_files"
output_folder = os.path.join(base_path, "field_translation")
input_file = "surgeries.json"
output_file = "surgeries.json"

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def translate_text(text, src='en', dest='it'):
    try:
        translated = GoogleTranslator(source=src, target=dest).translate(text)
        return translated
    except Exception as e:
        print(f"Translation error for '{text}': {e}")
        return text

def translate_surgeries(data, src='en', dest='it'):
    for entry in data.get("surgeries", []):
        # Translate the 'description' field
        if "description" in entry:
            translated_description = translate_text(entry["description"], src, dest)
            print(f"Translating description '{entry['description']}' to '{translated_description}'")
            entry["description"] = translated_description
    return data

def main():
    # Load the data
    input_path = os.path.join(base_path, input_file)
    data = load_json(input_path)

    # Translate the relevant fields
    translated_data = translate_surgeries(data)

    # Save the translated data
    output_path = os.path.join(output_folder, output_file)
    save_json(translated_data, output_path)
    print(f"Translated file saved to {output_path}")

if __name__ == "__main__":
    main()
