import json

# Load JSON data
with open('./data_ibm/healthcare_db/normalized_db/database_json_files/new_admission.json') as f:
    admissions = json.load(f)

with open('./data_ibm/healthcare_db/normalized_db/database_json_files/treatments.json') as f:
    treatments = json.load(f)

with open('./data_ibm/healthcare_db/normalized_db/database_json_files/medications.json') as f:
    medications = json.load(f)

with open('./data_ibm/healthcare_db/normalized_db/database_json_files/surgeries.json') as f:
    surgeries_data = json.load(f)

with open('./data_ibm/healthcare_db/normalized_db/database_json_files/diagnoses.json') as f:
    diagnoses = json.load(f)

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

# Function to replace codes with descriptions
def replace_codes(admission):
    admission["Procedures"] = [surgery_dict.get(code.strip(), code) for code in admission["ProcedureIDs"].split(",")]
    admission["Treatments"] = [treatment_dict.get(code.strip(), code) for code in admission["TreatmentIDs"].split(",")]
    admission["Medications"] = [medication_dict.get(code.strip(), code) for code in admission["MedicationIDs"].split(",")]
    admission["Diagnosis"] = diagnosis_dict.get(admission["InitialDiagnosisCode"], admission["InitialDiagnosisCode"])
    
    # Remove old fields
    del admission["ProcedureIDs"]
    del admission["TreatmentIDs"]
    del admission["MedicationIDs"]
    del admission["InitialDiagnosisCode"]
    
    return admission

# Transform admissions data
transformed_admissions = [replace_codes(admission) for admission in admissions]

# Save the transformed JSON data
with open('./data_ibm/healthcare_db/simplified_db/simplified_admissions.json', 'w') as f:
    json.dump(transformed_admissions, f, indent=4)

print("Transformation complete. The updated admissions data has been saved to 'simplified_admissions.json'.")
