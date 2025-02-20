import json

# Load the existing mock data from the provided JSON file
mock_data_path = './data_ibm/healthcare_db/normalized_db/mock_data_with_unique_codes.json'
with open(mock_data_path, 'r') as file:
    mock_data = json.load(file)

# Add unique codes to doctors, nurses, and patients
for i, doctor in enumerate(mock_data['doctors']):
    doctor['DoctorCode'] = f'MD{i+1:03d}'

for i, nurse in enumerate(mock_data['nurses']):
    nurse['NurseCode'] = f'N{i+1:03d}'

for i, patient in enumerate(mock_data['patients']):
    patient['PatientID'] = f'P{i+1:03d}'

# Generate mock data for Medications
medications = [
    {"MedicationCode": f"MED{i+1:03d}", "Description": desc}
    for i, desc in enumerate([
        "Aspirin", "Ibuprofen", "Paracetamol", "Amoxicillin", "Ciprofloxacin", "Metformin",
        "Omeprazole", "Lisinopril", "Amlodipine", "Metoprolol", "Atorvastatin", "Simvastatin",
        "Clopidogrel", "Warfarin", "Heparin", "Enoxaparin", "Insulin", "Albuterol", "Prednisone",
        "Hydrocortisone", "Morphine", "Vitamin-D", "Tramadol", "Diazepam", "Lorazepam", "Sertraline",
        "Fluoxetine", "Ketorolac", "Escitalopram", "Bupropion"
    ])
]

# Generate mock data for Treatments
treatments = [
    {"TreatmentCode": f"TR{i+1:03d}", "Description": desc}
    for i, desc in enumerate([
        "Blood Transfusion", "Physical Therapy", "Chemotherapy", "Radiation Therapy", "Dialysis",
        "Electrocardiogram", "MRI Scan", "CT Scan", "Ultrasound", "X-ray", "Vaccination",
        "Allergy Testing", "Wound Care", "Pain Management", "Surgical Procedure", "Cardiac Catheterization",
        "Endoscopy", "Colonoscopy", "Pulmonary Function Test", "Bone Density Test"
    ])
]

# Save the updated mock data with unique codes and the new medications and treatments to JSON files
mock_data_file_path = './data_ibm/healthcare_db/normalized_db/mock_data_with_unique_codes.json'
with open(mock_data_file_path, 'w') as file:
    json.dump(mock_data, file, indent=4)

medications_file_path = './data_ibm/healthcare_db/normalized_db/medications.json'
with open(medications_file_path, 'w') as file:
    json.dump(medications, file, indent=4)

treatments_file_path = './data_ibm/healthcare_db/normalized_db/treatments.json'
with open(treatments_file_path, 'w') as file:
    json.dump(treatments, file, indent=4)

print(f"Mock data saved to: {mock_data_file_path}")
print(f"Medications data saved to: {medications_file_path}")
print(f"Treatments data saved to: {treatments_file_path}")
