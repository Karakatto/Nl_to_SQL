import json
import random
from faker import Faker

fake = Faker()

# Load generated admissions data
with open('./data_ibm/healthcare_db/normalized_db/json files/admissions.json', 'r') as file:
    admissions_data = json.load(file)

# Load existing surgery and treatment data
with open('./data_ibm/healthcare_db/normalized_db/json files/surgery_patient.json', 'r') as file:
    surgery_patient_data = json.load(file)

with open('./data_ibm/healthcare_db/normalized_db/json files/patient_treatment.json', 'r') as file:
    patient_treatment_data = json.load(file)

with open('./data_ibm/healthcare_db/normalized_db/json files/departments.json', 'r') as file:
    departments_data = json.load(file)

with open('./data_ibm/healthcare_db/normalized_db/json files/diagnoses.json', 'r') as file:
    diagnoses_data = json.load(file)

with open('./data_ibm/healthcare_db/normalized_db/json files/medications.json', 'r') as file:
    medications_data = json.load(file)

# Extract relevant data
department_codes = [dept['dept_id'] for dept in departments_data]
diagnosis_codes = [(diagnosis['DiagnosisCode'], diagnosis['Description']) for diagnosis in diagnoses_data]
medication_codes = [med['MedicationCode'] for med in medications_data]

# Create a mapping of PatientID to AdmissionID
patient_admission_mapping = {}
admission_id_counter = max([int(adm['AdmissionID'][1:]) for adm in admissions_data]) + 1

for admission in admissions_data:
    patient_id = admission['PatientID']
    admission_id = admission['AdmissionID']
    if patient_id in patient_admission_mapping:
        patient_admission_mapping[patient_id].append(admission_id)
    else:
        patient_admission_mapping[patient_id] = [admission_id]

# Update SurgeryPatient table
for entry in surgery_patient_data:
    patient_id = entry['PatientID']
    if patient_id in patient_admission_mapping and patient_admission_mapping[patient_id]:
        entry['AdmissionID'] = patient_admission_mapping[patient_id].pop(0)
    else:
        # Assign new AdmissionID if not already present
        admission_id = f"A{admission_id_counter:04d}"
        entry['AdmissionID'] = admission_id
        admission_id_counter += 1
        admissions_data.append({
            "AdmissionID": admission_id,
            "PatientID": patient_id,
            "DoctorID": entry['DoctorCode'],
            "DepartmentID": random.choice(department_codes),
            "AdmissionDate": str(fake.date_between(start_date='-3y', end_date='-1d')),
            "DischargeDate": None,
            "DiagnosisCode": random.choice(diagnosis_codes)[0],
            "DiagnosisDescription": random.choice(diagnosis_codes)[1],
            "ProcedureIDs": entry['ProcedureID'],
            "TreatmentIDs": "",
            "MedicationIDs": ", ".join(random.sample(medication_codes, random.randint(1, 3)))
        })

# Update PatientTreatment table
for entry in patient_treatment_data:
    patient_id = entry['PatientID']
    if patient_id in patient_admission_mapping and patient_admission_mapping[patient_id]:
        entry['AdmissionID'] = patient_admission_mapping[patient_id].pop(0)
    else:
        # Assign new AdmissionID if not already present
        admission_id = f"A{admission_id_counter:04d}"
        entry['AdmissionID'] = admission_id
        admission_id_counter += 1
        admissions_data.append({
            "AdmissionID": admission_id,
            "PatientID": patient_id,
            "DoctorID": entry['DoctorCode'],
            "DepartmentID": random.choice(department_codes),
            "AdmissionDate": str(fake.date_between(start_date='-3y', end_date='-1d')),
            "DischargeDate": None,
            "DiagnosisCode": random.choice(diagnosis_codes)[0],
            "DiagnosisDescription": random.choice(diagnosis_codes)[1],
            "ProcedureIDs": "",
            "TreatmentIDs": entry['TreatmentCode'],
            "MedicationIDs": ", ".join(random.sample(medication_codes, random.randint(1, 3)))
        })

# Save the updated admissions data
with open('./data_ibm/healthcare_db/normalized_db/json files/admissions.json', 'w') as file:
    json.dump(admissions_data, file, indent=4)

# Save the updated data back to JSON files
with open('./data_ibm/healthcare_db/normalized_db/json files/surgery_patient.json', 'w') as file:
    json.dump(surgery_patient_data, file, indent=4)

with open('./data_ibm/healthcare_db/normalized_db/json files/patient_treatment.json', 'w') as file:
    json.dump(patient_treatment_data, file, indent=4)

print("SurgeryPatient and PatientTreatment tables have been updated with AdmissionIDs.")
