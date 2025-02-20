import json

# Load existing data
with open('./data_ibm/healthcare_db/normalized_db/json files/treatments.json', 'r') as file:
    treatments = json.load(file)

with open('./data_ibm/healthcare_db/normalized_db/json files/surgeries.json', 'r') as file:
    surgeries = json.load(file)

# Debugging: Print the loaded data to check the structure
print("Treatments:", treatments)
print("Surgeries:", surgeries)

# Create dictionaries to map codes to descriptions
treatment_dict = {treatment['TreatmentCode']: treatment['Description'] for treatment in treatments}
surgery_dict = {surgery['surgery_code']: surgery['description'] for surgery in surgeries['surgeries']}

# Load surgery_patient and patient_treatment data
with open('./data_ibm/healthcare_db/normalized_db/json files/surgery_patient.json', 'r') as file:
    surgery_patient_data = json.load(file)

with open('./data_ibm/healthcare_db/normalized_db/json files/patient_treatment.json', 'r') as file:
    patient_treatment_data = json.load(file)

# Update descriptions in surgery_patient_data
for entry in surgery_patient_data:
    procedure_code = entry['SurgeryCode']
    if procedure_code in surgery_dict:
        entry['SurgeryDescription'] = surgery_dict[procedure_code]
    else:
        print(f"Warning: SurgeryCode {procedure_code} not found in surgery_dict")

# Update descriptions in patient_treatment_data
for entry in patient_treatment_data:
    treatment_code = entry['TreatmentCode']
    if treatment_code in treatment_dict:
        entry['TreatmentDescription'] = treatment_dict[treatment_code]
    else:
        print(f"Warning: TreatmentCode {treatment_code} not found in treatment_dict")

# Save the updated data back to JSON files
with open('./data_ibm/healthcare_db/normalized_db/json files/surgery_patient.json', 'w') as file:
    json.dump(surgery_patient_data, file, indent=4)

with open('./data_ibm/healthcare_db/normalized_db/json files/patient_treatment.json', 'w') as file:
    json.dump(patient_treatment_data, file, indent=4)

print("Updated descriptions in surgery_patient and patient_treatment.")
