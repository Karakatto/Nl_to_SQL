import json
import random
from faker import Faker

fake = Faker()

# Load existing data
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

# Initialize counters and mappings
admission_id_counter = 1

admissions_data = []

# Create mappings of patient to their procedures and treatments by date
patient_surgeries_by_date = {}
for entry in surgery_patient_data:
    patient_id = entry['PatientID']
    if patient_id not in patient_surgeries_by_date:
        patient_surgeries_by_date[patient_id] = {}
    surgery_date = entry['SurgeryDate']
    if surgery_date not in patient_surgeries_by_date[patient_id]:
        patient_surgeries_by_date[patient_id][surgery_date] = []
    patient_surgeries_by_date[patient_id][surgery_date].append(entry['ProcedureID'])

patient_treatments_by_date = {}
for entry in patient_treatment_data:
    patient_id = entry['PatientID']
    if patient_id not in patient_treatments_by_date:
        patient_treatments_by_date[patient_id] = {}
    treatment_date = entry['TreatmentDate']
    if treatment_date not in patient_treatments_by_date[patient_id]:
        patient_treatments_by_date[patient_id][treatment_date] = []
    patient_treatments_by_date[patient_id][treatment_date].append(entry['TreatmentCode'])

# Generate Admissions data
for patient_id in set(entry['PatientID'] for entry in surgery_patient_data + patient_treatment_data):
    for date in set(list(patient_surgeries_by_date.get(patient_id, {}).keys()) + list(patient_treatments_by_date.get(patient_id, {}).keys())):
        admission_id = f"A{admission_id_counter:04d}"
        admission_date = fake.date_between(start_date='-3y', end_date='-1d')
        discharge_date = admission_date if random.random() > 0.2 else None
        diagnosis_code, diagnosis_description = random.choice(diagnosis_codes)
        procedure_ids = ",".join(patient_surgeries_by_date.get(patient_id, {}).get(date, []))
        treatment_ids = ",".join(patient_treatments_by_date.get(patient_id, {}).get(date, []))
        medication_ids = ",".join(random.sample(medication_codes, random.randint(1, 3)))

        admissions_data.append({
            "AdmissionID": admission_id,
            "PatientID": patient_id,
            "DoctorID": random.choice(surgery_patient_data)['DoctorCode'],
            "DepartmentID": random.choice(department_codes),
            "AdmissionDate": str(admission_date),
            "DischargeDate": str(discharge_date) if discharge_date else None,
            "DiagnosisCode": diagnosis_code,
            "DiagnosisDescription": diagnosis_description,
            "ProcedureIDs": procedure_ids,
            "TreatmentIDs": treatment_ids,
            "MedicationIDs": medication_ids
        })

        admission_id_counter += 1

# Save the generated data to JSON
with open('./data_ibm/healthcare_db/normalized_db/json files/admissions.json', 'w') as file:
    json.dump(admissions_data, file, indent=4)

print("Generated admissions.json")
