import json
import sqlite3

# Load the corrected JSON data
with open('./data_ibm/healthcare_db/simplified_db/json_data/simplified_admissions.json') as f:
    admissions = json.load(f)

with open('./data_ibm/healthcare_db/simplified_db/json_data/treatments.json') as f:
    treatments = json.load(f)

with open('./data_ibm/healthcare_db/simplified_db/json_data/medications.json') as f:
    medications = json.load(f)

with open('./data_ibm/healthcare_db/simplified_db/json_data/surgeries.json') as f:
    surgeries_data = json.load(f)

with open('./data_ibm/healthcare_db/simplified_db/json_data/diagnoses.json') as f:
    diagnoses = json.load(f)

with open('./data_ibm/healthcare_db/simplified_db/json_data/patients.json') as f:
    patients = json.load(f)

with open('./data_ibm/healthcare_db/simplified_db/json_data/doctors.json') as f:
    doctors = json.load(f)

with open('./data_ibm/healthcare_db/simplified_db/json_data/departments.json') as f:
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

# Connect to SQLite database (or create it)
conn = sqlite3.connect('./data_ibm/healthcare_db/simplified_db/simplified_healthcare.db')
cursor = conn.cursor()

# Drop existing tables if they exist
cursor.execute("DROP TABLE IF EXISTS Patient")
cursor.execute("DROP TABLE IF EXISTS Doctor")
cursor.execute("DROP TABLE IF EXISTS Department")
cursor.execute("DROP TABLE IF EXISTS Admission")
cursor.execute("DROP TABLE IF EXISTS Procedure")
cursor.execute("DROP TABLE IF EXISTS Treatment")
cursor.execute("DROP TABLE IF EXISTS Medication")

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS Patient (
    PatientID VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(100),
    DateOfBirth DATE,
    Gender VARCHAR(10),
    PhoneNumber VARCHAR(15),
    Address VARCHAR(255),
    Email VARCHAR(100),
    EmergencyContactName VARCHAR(100),
    EmergencyContactRelation VARCHAR(50),
    EmergencyContactPhone VARCHAR(15)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Doctor (
    DoctorCode VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(100),
    DateOfBirth DATE,
    Gender VARCHAR(10),
    Phone VARCHAR(15),
    Email VARCHAR(100),
    Specialization VARCHAR(100),
    Address VARCHAR(255)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Department (
    DepartmentCode VARCHAR(10) PRIMARY KEY,
    DepartmentName VARCHAR(100),
    Phone VARCHAR(15),
    Email VARCHAR(100),
    HeadOfDepartment VARCHAR(10),
    FOREIGN KEY (HeadOfDepartment) REFERENCES Doctor(DoctorCode)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Admission (
    AdmissionID VARCHAR(10) PRIMARY KEY,
    PatientID VARCHAR(10),
    DoctorID VARCHAR(10),
    DepartmentID VARCHAR(10),
    AdmissionDate DATE,
    DischargeDate DATE,
    Diagnosis VARCHAR(255),
    Treatments TEXT,
    Procedures TEXT,
    Medications TEXT,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorCode),
    FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentCode)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Procedure (
    AdmissionID VARCHAR(10),
    ProcedureDescription VARCHAR(255),
    FOREIGN KEY (AdmissionID) REFERENCES Admission(AdmissionID)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Treatment (
    AdmissionID VARCHAR(10),
    TreatmentDescription VARCHAR(255),
    FOREIGN KEY (AdmissionID) REFERENCES Admission(AdmissionID)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Medication (
    AdmissionID VARCHAR(10),
    MedicationDescription VARCHAR(255),
    FOREIGN KEY (AdmissionID) REFERENCES Admission(AdmissionID)
)
""")

# Function to insert or ignore a record if it exists
def insert_or_ignore_patient(patient):
    cursor.execute("""
    INSERT OR IGNORE INTO Patient (PatientID, Name, DateOfBirth, Gender, PhoneNumber, Address, Email, EmergencyContactName, EmergencyContactRelation, EmergencyContactPhone)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (patient["PatientID"], patient["Name"], patient["DateOfBirth"], patient["Gender"], patient["PhoneNumber"], patient["Address"], patient["Email"], patient["EmergencyContactName"], patient["EmergencyContactRelation"], patient["EmergencyContactPhone"]))

def insert_or_ignore_doctor(doctor):
    cursor.execute("""
    INSERT OR IGNORE INTO Doctor (DoctorCode, Name, DateOfBirth, Gender, Phone, Email, Specialization, Address)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (doctor["Id"], doctor["Name"], doctor["DateOfBirth"], doctor["Gender"], doctor["Phone"], doctor["Email"], doctor["Specialization"], doctor["Address"]))

def insert_or_ignore_department(department):
    cursor.execute("""
    INSERT OR IGNORE INTO Department (DepartmentCode, DepartmentName, Phone, Email, HeadOfDepartment)
    VALUES (?, ?, ?, ?, ?)
    """, (department["dept_id"], department["dept_name"], department["phone"], department["email"], department["HeadOfDepartment"]))

# Populate Patient table
for patient in patients:
    insert_or_ignore_patient(patient)

# Populate Doctor table
for doctor in doctors:
    insert_or_ignore_doctor(doctor)

# Populate Department table
for department in departments:
    insert_or_ignore_department(department)

# Function to replace codes with descriptions and populate related tables
def replace_codes_and_insert(admission):
    procedures = ", ".join(admission["Procedures"])
    treatments = ", ".join(admission["Treatments"])
    medications = ", ".join(admission["Medications"])
    diagnosis = admission["Diagnosis"]

    # Debug prints to see the data being processed
    print(f"Inserting Admission: {admission['AdmissionID']}")
    print(f"PatientID: {admission['PatientID']}, DoctorID: {admission['DoctorID']}, DepartmentID: {admission['DepartmentID']}")
    print(f"AdmissionDate: {admission['AdmissionDate']}, DischargeDate: {admission['DischargeDate']}, Diagnosis: {diagnosis}")
    print(f"Treatments: {treatments}, Procedures: {procedures}, Medications: {medications}")

    # Insert the admission record
    cursor.execute("""
    INSERT INTO Admission (AdmissionID, PatientID, DoctorID, DepartmentID, AdmissionDate, DischargeDate, Diagnosis, Treatments, Procedures, Medications)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (admission["AdmissionID"], admission["PatientID"], admission["DoctorID"], admission["DepartmentID"], admission["AdmissionDate"], admission["DischargeDate"], diagnosis, treatments, procedures, medications))

    for procedure in admission["Procedures"]:
        cursor.execute("""
        INSERT INTO Procedure (AdmissionID, ProcedureDescription)
        VALUES (?, ?)
        """, (admission["AdmissionID"], procedure))

    for treatment in admission["Treatments"]:
        cursor.execute("""
        INSERT INTO Treatment (AdmissionID, TreatmentDescription)
        VALUES (?, ?)
        """, (admission["AdmissionID"], treatment))

    for medication in admission["Medications"]:
        cursor.execute("""
        INSERT INTO Medication (AdmissionID, MedicationDescription)
        VALUES (?, ?)
        """, (admission["AdmissionID"], medication))

# Transform and populate admissions data
for admission in admissions:
    replace_codes_and_insert(admission)

# Commit changes and close connection
conn.commit()
conn.close()

print("Database populated successfully.")
