import json
import random

# Load the JSON files
with open('./data_ibm/healthcare_db/normalized_db/json files/nurses.json') as nurses_file:
    nurses = json.load(nurses_file)

with open('./data_ibm/healthcare_db/normalized_db/json files/departments.json') as departments_file:
    departments = json.load(departments_file)

# Extract department codes
department_codes = [department["dept_id"] for department in departments]

# Assign a random department code to each nurse
for nurse in nurses["nurses"]:
    nurse["DepartmentCode"] = random.choice(department_codes)

# Save the updated nurses.json
with open('./data_ibm/healthcare_db/normalized_db/json files/nurses.json', 'w') as nurses_file:
    json.dump(nurses, nurses_file, indent=4)

print("nurses.json has been updated with DepartmentCode.")
