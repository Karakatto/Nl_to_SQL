import json
from datetime import datetime, timedelta
import random

# Load JSON data
with open('./data_ibm/healthcare_db/simplified_db/simplified_admissions.json') as f:
    admissions = json.load(f)

# Function to adjust discharge dates
def adjust_discharge_dates(admissions):
    for admission in admissions:
        admission_date = datetime.strptime(admission["AdmissionDate"], "%Y-%m-%d")
        
        # Generate a discharge date within 30 days, with a few outliers up to 90 days
        if random.random() < 0.95:
            discharge_date = admission_date + timedelta(days=random.randint(1, 30))
        else:
            discharge_date = admission_date + timedelta(days=random.randint(31, 90))
        
        admission["DischargeDate"] = discharge_date.strftime("%Y-%m-%d")
    
    return admissions

# Adjust the discharge dates in the JSON data
adjusted_admissions = adjust_discharge_dates(admissions)

# Save the modified JSON data
with open('./data_ibm/healthcare_db/simplified_db/simplified_admissions.json', 'w') as f:
    json.dump(adjusted_admissions, f, indent=4)

print("Discharge dates adjusted successfully.")
