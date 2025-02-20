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
        translated_entry = {}
        for key, value in entry.items():
            translated_key = translate_text(key, src, dest)
            # Do not translate codes, only translate descriptions
            if key in ["DiagnosisCode", "MedicationCode", "surgery_code", "TreatmentCode"]:
                translated_value = value
            else:
                translated_value = translate_text(value, src, dest) if isinstance(value, str) else value
            translated_entry[translated_key] = translated_value
        translated_data.append(translated_entry)

    return translated_data

def translate_json_files():
    files_to_translate = {
        "diagnoses": {
            "input": "./data_ibm/healthcare_db/simplified_db/italian/google-translate/json_files/diagnoses.json",
            "output": "./data_ibm/healthcare_db/simplified_db/italian/google-translate/translated_json_files/diagnoses_translated.json"
        },
        "medications": {
            "input": "./data_ibm/healthcare_db/simplified_db/italian/google-translate/json_files/medications.json",
            "output": "./data_ibm/healthcare_db/simplified_db/italian/google-translate/translated_json_files/medications_translated.json"
        },
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
        translated_data = translate_entries(data)
        save_json_file(output_file, translated_data)

if __name__ == "__main__":
    translate_json_files()
