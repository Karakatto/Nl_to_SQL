import json
import os
from tqdm.auto import tqdm
from deep_translator import GoogleTranslator

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json_file(file_path, content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(content, file, ensure_ascii=False, indent=4)

def translate_text(text, src='en', dest='it'):
    try:
        result = GoogleTranslator(source=src, target=dest).translate(text)
        return result
    except Exception as e:
        print(f"Translation error for '{text}': {e}")
        return text  # Return the original text if translation fails

def translate_entries(data, src='en', dest='it'):
    translated_data = []

    for entry in data:
        if isinstance(entry, dict):  # Ensure entry is a dictionary
            translated_entry = {}
            for key, value in entry.items():
                translated_key = translate_text(key, src, dest)
                if key in ["DiagnosisCode", "MedicationCode", "SurgeryCode", "TreatmentCode"]:
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

def translate_json_files():
    files_to_translate = {
        "surgeries": {
            "input": "./data_ibm/healthcare_db/simplified_db/italian/google-translate/json_files/surgeries.json",
            "output": "./data_ibm/healthcare_db/simplified_db/italian/google-translate/translated_json_files/surgeries_translated.json"
        },
        "treatments": {
            "input": "./data_ibm/healthcare_db/simplified_db/italian/google-translate/json_files/treatments.json",
            "output": "./data_ibm/healthcare_db/simplified_db/italian/google-translate/translated_json_files/treatments_translated.json"
        }
    }

    for category, paths in files_to_translate.items():
        input_file = paths["input"]
        output_file = paths["output"]
        print(f"Translating {category} from {input_file} to {output_file}...")
        
        # Load, translate, and save
        data = load_json_file(input_file)
        if not isinstance(data, list):
            print(f"Expected list of entries, but got {type(data)}. Please check the file structure.")
            continue
        translated_data = translate_entries(data)
        save_json_file(output_file, translated_data)

if __name__ == "__main__":
    translate_json_files()
