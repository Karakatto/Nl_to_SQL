import json
import random
from datetime import datetime, timedelta

# Load JSON data
with open('./data_ibm/healthcare_db/simplified_db/simplified_admissions.json') as f:
    admissions = json.load(f)

with open('./data_ibm/healthcare_db/normalized_db/database_json_files/treatments.json') as f:
    treatments = json.load(f)

with open('./data_ibm/healthcare_db/normalized_db/database_json_files/medications.json') as f:
    medications = json.load(f)

with open('./data_ibm/healthcare_db/normalized_db/database_json_files/surgeries.json') as f:
    surgeries_data = json.load(f)

with open('./data_ibm/healthcare_db/normalized_db/database_json_files/diagnoses.json') as f:
    diagnoses = json.load(f)

with open('./data_ibm/healthcare_db/normalized_db/database_json_files/patients.json') as f:
    patients = json.load(f)

with open('./data_ibm/healthcare_db/normalized_db/database_json_files/doctors.json') as f:
    doctors = json.load(f)

with open('./data_ibm/healthcare_db/normalized_db/database_json_files/departments.json') as f:
    departments = json.load(f)

# Check if surgeries is a dictionary with a key like "surgeries" containing a list
if isinstance(surgeries_data, dict) and "surgeries" in surgeries_data:
    surgeries = surgeries_data["surgeries"]
else:
    surgeries = surgeries_data

# Create lookup dictionaries
treatment_dict = {t["TreatmentCode"]: t["Description"] for t in treatments}
medication_dict = {m["MedicationCode"]: m["Description"] for m in medications}
surgery_dict = {s["surgery_code"]: s["description"] for s in surgeries}
diagnosis_dict = {d["DiagnosisCode"]: d["Description"] for d in diagnoses}

# Function to generate a random date within a range
def random_date(start, end):
    return start + timedelta(days=random.randint(0, int((end - start).days)))

# Function to generate a unique AdmissionID
def generate_unique_admission_id(existing_ids):
    while True:
        new_id = f"A{random.randint(1000, 9999)}"
        if new_id not in existing_ids:
            existing_ids.add(new_id)
            return new_id

# Track existing AdmissionIDs to ensure uniqueness
existing_admission_ids = {admission["AdmissionID"] for admission in admissions}

# Track existing PatientIDs with admissions
existing_patient_ids = {admission["PatientID"] for admission in admissions}

# Add missing patients with random admissions
for patient in patients:
    if patient["PatientID"] not in existing_patient_ids:
        # Create a random admission for this patient
        random_doctor = random.choice(doctors)["Id"]
        random_department = random.choice(departments)["dept_id"]
        admission_date = random_date(datetime(2022, 1, 1), datetime(2023, 12, 31))
        discharge_date = admission_date + timedelta(days=random.randint(1, 30))
        random_diagnosis = random.choice(list(diagnosis_dict.values()))
        random_treatments = random.choices(list(treatment_dict.values()), k=random.randint(1, 3))
        random_procedures = random.choices(list(surgery_dict.values()), k=random.randint(1, 2))
        random_medications = random.choices(list(medication_dict.values()), k=random.randint(1, 3))

        new_admission = {
            "AdmissionID": generate_unique_admission_id(existing_admission_ids),
            "PatientID": patient["PatientID"],
            "DoctorID": random_doctor,
            "DepartmentID": random_department,
            "AdmissionDate": admission_date.strftime('%Y-%m-%d'),
            "DischargeDate": discharge_date.strftime('%Y-%m-%d'),
            "InitialDiagnosisDescription": random_diagnosis,
            "Treatments": random_treatments,
            "Surgeries": [],
            "Procedures": random_procedures,
            "Medications": random_medications,
            "Diagnosis": random_diagnosis
        }

        admissions.append(new_admission)

# Ensure all fields are lists
for admission in admissions:
    if isinstance(admission["Treatments"], str):
        admission["Treatments"] = admission["Treatments"].split(", ")
    if isinstance(admission["Procedures"], str):
        admission["Procedures"] = admission["Procedures"].split(", ")
    if isinstance(admission["Medications"], str):
        admission["Medications"] = admission["Medications"].split(", ")

# Save the updated admissions to a new file
with open('./data_ibm/healthcare_db/simplified_db/simplified_admissions.json', 'w') as f:
    json.dump(admissions, f, indent=4)

print("Updated admissions JSON saved to 'updated_admission.json'.")
