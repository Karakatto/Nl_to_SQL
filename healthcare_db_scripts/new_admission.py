import json
import random
from faker import Faker
from datetime import datetime

fake = Faker()

# Load existing data
with open('./data_ibm/healthcare_db/normalized_db/json files/patients.json', 'r') as file:
    patients_data = json.load(file)['patients']

with open('./data_ibm/healthcare_db/normalized_db/json files/doctors.json', 'r') as file:
    doctors_data = json.load(file)['doctors']

with open('./data_ibm/healthcare_db/normalized_db/json files/departments.json', 'r') as file:
    departments_data = json.load(file)

with open('./data_ibm/healthcare_db/normalized_db/json files/diagnoses.json', 'r') as file:
    diagnoses_data = json.load(file)

with open('./data_ibm/healthcare_db/normalized_db/json files/medications.json', 'r') as file:
    medications_data = json.load(file)

with open('./data_ibm/healthcare_db/normalized_db/json files/treatments.json', 'r') as file:
    treatments_data = json.load(file)

with open('./data_ibm/healthcare_db/normalized_db/json files/surgeries.json', 'r') as file:
    surgeries_data = json.load(file)['surgeries']

# Extract relevant data
patient_ids = [patient['PatientID'] for patient in patients_data]
doctor_ids = [doctor['Id'] for doctor in doctors_data]
department_ids = [dept['dept_id'] for dept in departments_data]
diagnosis_codes = [(diagnosis['DiagnosisCode'], diagnosis['Description']) for diagnosis in diagnoses_data]
medication_codes = [med['MedicationCode'] for med in medications_data]
treatment_codes = [(treatment['TreatmentCode'], treatment['Description']) for treatment in treatments_data]
surgery_codes = [(surgery['surgery_code'], surgery['description']) for surgery in surgeries_data]

# Initialize counters and mappings
admission_id_counter = 1

admissions_data = []

# Generate Admissions data
for _ in range(100):  # Adjust the number of admissions as needed
    patient_id = random.choice(patient_ids)
    doctor_id = random.choice(doctor_ids)
    department_id = random.choice(department_ids)
    admission_date = fake.date_between(start_date='-3y', end_date='-1d')
    discharge_date = fake.date_between(start_date=admission_date, end_date='today') if random.random() > 0.2 else None
    diagnosis_code, diagnosis_description = random.choice(diagnosis_codes)

    # Generate multiple treatments and surgeries for the admission
    treatments = random.sample(treatment_codes, random.randint(1, 5))
    surgeries = random.sample(surgery_codes, random.randint(1, 3))

    treatment_ids = [treatment[0] for treatment in treatments]
    procedure_ids = [surgery[0] for surgery in surgeries]
    medication_ids = random.sample(medication_codes, random.randint(1, 3))

    admission_data = {
        "AdmissionID": f"A{admission_id_counter:04d}",
        "PatientID": patient_id,
        "DoctorID": doctor_id,
        "DepartmentID": department_id,
        "AdmissionDate": str(admission_date),
        "DischargeDate": str(discharge_date) if discharge_date else None,
        "InitialDiagnosisCode": diagnosis_code,
        "InitialDiagnosisDescription": diagnosis_description,
        "ProcedureIDs": ",".join(procedure_ids),
        "TreatmentIDs": ",".join(treatment_ids),
        "MedicationIDs": ",".join(medication_ids),
        "Treatments": [
            {
                "TreatmentCode": treatment[0],
                "TreatmentDescription": treatment[1],
                "TreatmentDate": str(fake.date_between(start_date=admission_date, end_date=discharge_date or datetime.today()))
            }
            for treatment in treatments
        ],
        "Surgeries": [
            {
                "SurgeryCode": surgery[0],
                "SurgeryDescription": surgery[1],
                "SurgeryDate": str(fake.date_between(start_date=admission_date, end_date=discharge_date or datetime.today()))
            }
            for surgery in surgeries
        ]
    }

    admissions_data.append(admission_data)
    admission_id_counter += 1

# Save the generated data to JSON
with open('./data_ibm/healthcare_db/normalized_db/json files/new_admission.json', 'w') as file:
    json.dump(admissions_data, file, indent=4)

print("Generated new_admission.json")
