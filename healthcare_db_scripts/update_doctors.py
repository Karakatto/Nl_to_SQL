import json
import random

# Load the JSON files
with open('./data_ibm/healthcare_db/normalized_db/json files/departments.json') as dept_file:
    departments = json.load(dept_file)

with open('./data_ibm/healthcare_db/normalized_db/json files/doctors.json') as doc_file:
    doctors = json.load(doc_file)

# Mapping of departments to specializations
department_specialization_map = {
    "Emergency": "Emergency Medicine",
    "Cardiology": "Cardiology",
    "Orthopedics": "Orthopedics",
    "Radiology": "Radiology",
    "Neurology": "Neurology",
    "Oncology": "Oncology",
    "Pediatrics": "Pediatrics",
    "Gastroenterology": "Gastroenterology",
    "Urology": "Urology",
    "General Surgery": "General Surgery"
}

# Create a dictionary of doctors based on specialization
specialization_doctors_map = {}
for doctor in doctors["doctors"]:
    specialization = doctor["Specialization"]
    if specialization not in specialization_doctors_map:
        specialization_doctors_map[specialization] = []
    specialization_doctors_map[specialization].append(doctor["Id"])

# Assign a relevant doctor as HeadOfDepartment
for department in departments:
    dept_name = department["dept_name"]
    specialization = department_specialization_map.get(dept_name)
    if specialization in specialization_doctors_map:
        department["HeadOfDepartment"] = random.choice(specialization_doctors_map[specialization])
    else:
        department["HeadOfDepartment"] = None

# Save the updated departments.json
with open('./data_ibm/healthcare_db/normalized_db/json files/departments.json', 'w') as dept_file:
    json.dump(departments, dept_file, indent=4)

print("departments.json has been updated with HeadOfDepartment based on specialization.")
