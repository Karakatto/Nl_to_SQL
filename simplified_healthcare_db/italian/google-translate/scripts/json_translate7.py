import json
import os
from tqdm.auto import tqdm
from deep_translator import GoogleTranslator

def load_json_file(file_path):
    """Loads a JSON file from the specified path."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json_file(file_path, content):
    """Saves content to a JSON file at the specified path."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(content, file, ensure_ascii=False, indent=4)

def translate_text(text, src='en', dest='it'):
    """Translates text from the source language to the destination language."""
    try:
        result = GoogleTranslator(source=src, target=dest).translate(text)
        return result
    except Exception as e:
        print(f"Translation error for '{text}': {e}")
        return text  # Return the original text if translation fails

def translate_entries(data, src='en', dest='it'):
    """Translates entries in the provided data."""
    translated_data = []

    for entry in data:
        if isinstance(entry, dict):  # Ensure entry is a dictionary
            translated_entry = {}
            for key, value in entry.items():
                translated_key = translate_text(key, src, dest)
                
                # Skip translating specific codes and identifiers, translate only descriptions
                if key in ["SurgeryCode"]:
                    translated_value = value
                else:
                    if isinstance(value, str):
                        translated_value = translate_text(value, src, dest)
                    elif isinstance(value, list):
                        translated_value = [translate_text(v, src, dest) if isinstance(v, str) else v for v in value]
                    elif isinstance(value, dict):
                        translated_value = {
                            k: translate_text(v, src, dest) if isinstance(v, str) else v 
                            for k, v in value.items()
                        }
                    else:
                        translated_value = value
                translated_entry[translated_key] = translated_value
            translated_data.append(translated_entry)
        else:
            print(f"Skipping invalid entry: {entry}")
    return translated_data

def translate_surgeries():
    input_file = "./data_ibm/healthcare_db/simplified_db/italian/google-translate/json_files/surgeries.json"
    output_file = "./data_ibm/healthcare_db/simplified_db/italian/google-translate/translated_json_files/surgeries_translated.json"
    
    print(f"Translating surgeries from {input_file} to {output_file}...")
    
    # Load JSON data
    data = load_json_file(input_file)
    
    # Check if the top-level structure is a dictionary
    if isinstance(data, dict):
        # Assuming the actual list of surgeries is under a key like "surgeries"
        data = data.get("surgeries", [])
    
    if not isinstance(data, list):
        print(f"Expected list of entries, but got {type(data)}. Please check the file structure.")
        return
    
    translated_data = translate_entries(data)
    save_json_file(output_file, translated_data)

if __name__ == "__main__":
    translate_surgeries()
