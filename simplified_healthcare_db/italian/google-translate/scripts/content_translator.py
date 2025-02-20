import json
import os
from deep_translator import GoogleTranslator

# Define paths for input and output
base_path = "data_ibm/healthcare_db/simplified_db/italian/google-translate/json_files"
output_folder = os.path.join(base_path, "field_translation")
input_file = "admissions.json"
output_file = "admissions.json"

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

def translate_admissions(data, src='en', dest='it'):
    for entry in data:
        # Translate the 'InitialDiagnosisDescription' field
        if "InitialDiagnosisDescription" in entry:
            entry["InitialDiagnosisDescription"] = translate_text(entry["InitialDiagnosisDescription"], src, dest)
        
        # Translate the 'Diagnosis' field
        if "Diagnosis" in entry:
            entry["Diagnosis"] = translate_text(entry["Diagnosis"], src, dest)
        
        # Translate each item in the 'Treatments' list
        if "Treatments" in entry and isinstance(entry["Treatments"], list):
            entry["Treatments"] = [translate_text(item, src, dest) for item in entry["Treatments"]]

        # Translate each item in the 'Medications' list
        if "Medications" in entry and isinstance(entry["Medications"], list):
            entry["Medications"] = [translate_text(item, src, dest) for item in entry["Medications"]]

        # Translate each item in the 'Procedures' list
        if "Procedures" in entry and isinstance(entry["Procedures"], list):
            entry["Procedures"] = [translate_text(item, src, dest) for item in entry["Procedures"]]

        # Translate each dictionary in the 'Surgeries' list
        if "Surgeries" in entry and isinstance(entry["Surgeries"], list):
            for surgery in entry["Surgeries"]:
                if "SurgeryDescription" in surgery:
                    surgery["SurgeryDescription"] = translate_text(surgery["SurgeryDescription"], src, dest)

    return data

def main():
    # Load the data
    input_path = os.path.join(base_path, input_file)
    data = load_json(input_path)

    # Translate the relevant fields
    translated_data = translate_admissions(data)

    # Save the translated data
    output_path = os.path.join(output_folder, output_file)
    save_json(translated_data, output_path)
    print(f"Translated file saved to {output_path}")

if __name__ == "__main__":
    main()
