import json
import random
from datetime import datetime, timedelta

def generate_dob(age):
    current_year = datetime.now().year
    birth_year = current_year - age
    birth_date = datetime(birth_year, random.randint(1, 12), random.randint(1, 28))
    return birth_date.strftime('%Y-%m-%d')

def update_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    if isinstance(data, dict):
        data = data[next(iter(data))]

    for item in data:
        age = random.randint(3, 95)
        item['DateOfBirth'] = generate_dob(age)
        if 'Age' in item:
            del item['Age']
    
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Paths to the JSON files

patients_file = './data_ibm/healthcare_db/normalized_db/json files/patients.json'

# Update the JSON files
update_json_file(patients_file)


print("JSON files updated with date of birth.")
