import json
import random
from faker import Faker

fake = Faker()

# Load existing employee data
with open('./data_ibm/healthcare_db/normalized_db/json files/employee.json', 'r') as file:
    employee_data = json.load(file)

# Load existing doctors, nurses, and administrative staff data
with open('./data_ibm/healthcare_db/normalized_db/json files/doctors.json', 'r') as file:
    doctors_data = json.load(file)

with open('./data_ibm/healthcare_db/normalized_db/json files/nurses.json', 'r') as file:
    nurses_data = json.load(file)

with open('./data_ibm/healthcare_db/normalized_db/json files/administratives.json', 'r') as file:
    administrative_data = json.load(file)

# Combine all employees into one list with unique codes
all_employees = (
    [{'EmployeeCode': doc['Id'], 'Role': 'Doctor'} for doc in doctors_data['doctors']] +
    [{'EmployeeCode': nur['NurseCode'], 'Role': 'Nurse'} for nur in nurses_data['nurses']] +
    [{'EmployeeCode': adm['Code'], 'Role': 'AdministrativeStaff'} for adm in administrative_data['administrative_staff']]
)

# Existing employee codes in employee.json
existing_employee_codes = [emp['employee_code'] for emp in employee_data]

# Update employee data
for employee in all_employees:
    if employee['EmployeeCode'] not in existing_employee_codes:
        hire_date = fake.date_between(start_date='-10y', end_date='today')
        promotion_date = hire_date if random.random() > 0.3 else fake.date_between(start_date=hire_date, end_date='today')
        salary = round(random.uniform(50000, 200000), 2)
        salary_increase = round(salary * random.uniform(1.05, 1.30), 2) if promotion_date != hire_date else None
        
        new_employee = {
            'employee_code': employee['EmployeeCode'],
            'hire_date': str(hire_date),
            'salary': salary,
            'promotion_date': str(promotion_date) if promotion_date != hire_date else None,
            'salary_increase': salary_increase,
            'employee_id': employee['EmployeeCode'],
            'role': employee['Role']
        }
        
        employee_data.append(new_employee)

# Save the updated employee data
with open('./data_ibm/healthcare_db/normalized_db/json files/employee.json', 'w') as file:
    json.dump(employee_data, file, indent=4)

print("Employee data has been updated.")
