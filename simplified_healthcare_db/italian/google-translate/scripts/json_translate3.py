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

def should_translate_field(key, value):
    """
    Determine if a value should be translated based on the key and the type of the value.
    """
    # Skip translating certain fields, especially those with specific personal data
    if key in ["PatientID", "Name", "Email", "PhoneNumber", "EmergencyContactName", "EmergencyContactPhone", "DateOfBirth"]:
        return False
    return True

def translate_patient_json(input_file, output_file, src='en', dest='it'):
    data = load_json_file(input_file)
    translated_data = []

    for entry in tqdm(data, desc=f"Translating {os.path.basename(input_file)}"):
        translated_entry = {}
        for key, value in entry.items():
            # Translate the key (field name)
            translated_key = translate_text(key, src, dest)

            if should_translate_field(key, value):
                # Translate the value if it's a string and should be translated
                translated_value = translate_text(value, src, dest) if isinstance(value, str) else value
            else:
                # Preserve the original value
                translated_value = value

            translated_entry[translated_key] = translated_value

        translated_data.append(translated_entry)

    save_json_file(output_file, translated_data)
    print(f"Translated file saved to {output_file}")

if __name__ == "__main__":
    input_file = "./data_ibm/healthcare_db/simplified_db/italian/google-translate/json_files/patients.json"
    output_file = "./data_ibm/healthcare_db/simplified_db/italian/google-translate/translated_json_files/patient_translated.json"

    translate_patient_json(input_file, output_file)
