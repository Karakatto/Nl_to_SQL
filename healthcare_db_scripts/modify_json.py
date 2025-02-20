import json
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Load existing data
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        if isinstance(data, dict):
            data = list(data.values())[0]
        return data

# Save JSON data
def save_json_data(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

patient_treatment_data = load_json_data('./data_ibm/healthcare_db/normalized_db/json files/patient_treatment.json')
surgery_patient_data = load_json_data('./data_ibm/healthcare_db/normalized_db/json files/surgery_patient.json')

# Add multiple treatments for some patients
for _ in range(10):
    patient_id = random.choice([entry['PatientID'] for entry in patient_treatment_data])
    existing_treatment_dates = [entry['TreatmentDate'] for entry in patient_treatment_data if entry['PatientID'] == patient_id]
    new_treatment_date = (datetime.strptime(random.choice(existing_treatment_dates), '%Y-%m-%d') + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
    
    patient_treatment_data.append({
        "PatientTreatmentID": f"TRT{len(patient_treatment_data) + 1:04d}",
        "PatientID": patient_id,
        "AdmissionID": None,  # This will be updated later
        "DoctorCode": random.choice([entry['DoctorCode'] for entry in patient_treatment_data]),
        "TreatmentCode": random.choice([entry['TreatmentCode'] for entry in patient_treatment_data]),
        "TreatmentDescription": random.choice([entry['TreatmentDescription'] for entry in patient_treatment_data]),
        "TreatmentDate": new_treatment_date
    })

# Add multiple surgeries for some patients
for _ in range(10):
    patient_id = random.choice([entry['PatientID'] for entry in surgery_patient_data])
    existing_surgery_dates = [entry['SurgeryDate'] for entry in surgery_patient_data if entry['PatientID'] == patient_id]
    new_surgery_date = (datetime.strptime(random.choice(existing_surgery_dates), '%Y-%m-%d') + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
    
    surgery_patient_data.append({
        "ProcedureID": f"PROC{len(surgery_patient_data) + 1:04d}",
        "PatientID": patient_id,
        "AdmissionID": None,  # This will be updated later
        "DoctorCode": random.choice([entry['DoctorCode'] for entry in surgery_patient_data]),
        "SurgeryCode": random.choice([entry['SurgeryCode'] for entry in surgery_patient_data]),
        "SurgeryDescription": random.choice([entry['SurgeryDescription'] for entry in surgery_patient_data]),
        "SurgeryDate": new_surgery_date
    })

# Save the updated data back to JSON
save_json_data(patient_treatment_data, './data_ibm/healthcare_db/normalized_db/json files/patient_treatment.json')
save_json_data(surgery_patient_data, './data_ibm/healthcare_db/normalized_db/json files/surgery_patient.json')

print("Updated patient_treatment.json and surgery_patient.json with multiple treatments and surgeries.")
