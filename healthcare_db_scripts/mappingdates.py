import json
from datetime import datetime

# Function to load JSON data
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        if isinstance(data, dict):
            data = list(data.values())[0]
        return data

# Load existing data
admissions_data = load_json_data('./data_ibm/healthcare_db/normalized_db/json files/admissions.json')
patient_treatment_data = load_json_data('./data_ibm/healthcare_db/normalized_db/json files/patient_treatment.json')
surgery_patient_data = load_json_data('./data_ibm/healthcare_db/normalized_db/json files/surgery_patient.json')

# Create a mapping of AdmissionID to Admission details
admission_map = {}
for admission in admissions_data:
    admission_date = admission['AdmissionDate']
    discharge_date = admission['DischargeDate'] or "9999-12-31"
    admission_map[(admission['PatientID'], admission_date)] = admission['AdmissionID']

# Update treatments with AdmissionID
for treatment in patient_treatment_data:
    treatment_date = treatment['TreatmentDate']
    admission_id = admission_map.get((treatment['PatientID'], treatment_date))
    treatment['AdmissionID'] = admission_id

# Save the updated treatments back to JSON
with open('./data_ibm/healthcare_db/normalized_db/json files/patient_treatment.json', 'w') as file:
    json.dump(patient_treatment_data, file, indent=4)

print("Updated patient_treatment.json with AdmissionID.")

# Update surgeries with AdmissionID
for surgery in surgery_patient_data:
    surgery_date = surgery['SurgeryDate']
    admission_id = admission_map.get((surgery['PatientID'], surgery_date))
    surgery['AdmissionID'] = admission_id

# Save the updated surgeries back to JSON
with open('./data_ibm/healthcare_db/normalized_db/json files/surgery_patient.json', 'w') as file:
    json.dump(surgery_patient_data, file, indent=4)

print("Updated surgery_patient.json with AdmissionID.")
