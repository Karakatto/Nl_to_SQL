import sqlite3
import pandas as pd
import json
import time

# Function to execute schema with retry logic
def execute_with_retry(cursor, schema, retries=5, delay=1):
    for i in range(retries):
        try:
            cursor.executescript(schema)
            return
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                time.sleep(delay)
            else:
                raise
    raise Exception("Failed to execute script after multiple retries due to database lock.")

# Connect to SQLite database
conn = sqlite3.connect('./data_ibm/healthcare_db/normalized_db/new_healthcare.db')
cursor = conn.cursor()

# Function to load JSON and insert into table
def load_json_to_db(json_path, table_name, conn):
    with open(json_path, 'r') as file:
        data = json.load(file)
        if isinstance(data, dict):
            data = list(data.values())[0]
        df = pd.DataFrame(data)
        
        # Ensure the columns match the table schema
        if table_name == 'Patient':
            df = df[['PatientID', 'Name', 'Age', 'Gender', 'PhoneNumber', 'Address', 'Email', 'EmergencyContactName', 'EmergencyContactRelation', 'EmergencyContactPhone']]
        elif table_name == 'Department':
            df = df[['dept_id', 'dept_name', 'HeadOfDepartment']].rename(columns={
                'dept_id': 'DepartmentCode',
                'dept_name': 'DepartmentName'
            })
        elif table_name == 'Medication':
            df = df[['MedicationCode', 'Description']]
        elif table_name == 'Treatment':
            df = df[['TreatmentCode', 'Description']]
        elif table_name == 'Doctor':
            df = df.rename(columns={
                'Id': 'DoctorCode',
                'Name': 'Name',
                'Age': 'Age',
                'Gender': 'Gender',
                'Phone': 'Phone',
                'Specialization': 'Specialization',
                'Address': 'Address',
                'Email': 'Email'
            })
        elif table_name == 'Nurse':
            df = df[['NurseCode', 'Name', 'Age', 'Gender', 'Phone', 'Email', 'DepartmentCode']]
        elif table_name == 'Bed':
            df = df[['bed_id', 'Status', 'DepartmentCode']].rename(columns={
                'bed_id': 'BedCode'
            })
        elif table_name == 'Diagnosis':
            df = df[['DiagnosisCode', 'Description']]
        elif table_name == 'Surgery':
            df = df[['surgery_code', 'description']].rename(columns={
                'surgery_code': 'SurgeryCode',
                'description': 'Description'
            })
        elif table_name == 'AdministrativeStaff':
            df = df[['Code', 'Name', 'Age', 'Gender', 'Phone', 'Role', 'Address', 'Email']]
        elif table_name == 'EmployeeSalary':
            df = df[['employee_code', 'employee_id', 'role', 'hire_date', 'salary', 'promotion_date', 'salary_increase']].rename(columns={
                'employee_code': 'EmployeeCode',
                'employee_id': 'EmployeeID',
                'role': 'Role',
                'hire_date': 'HireDate',
                'salary': 'Salary',
                'promotion_date': 'PromotionDate',
                'salary_increase': 'SalaryIncrease'
            })
        elif table_name == 'SurgeryPatient':
            df = df[['ProcedureID', 'PatientID', 'AdmissionID', 'DoctorCode', 'SurgeryCode', 'SurgeryDescription', 'SurgeryDate']]
        elif table_name == 'Admission':
            df = df[['AdmissionID', 'PatientID', 'DoctorID', 'DepartmentID', 'AdmissionDate', 'DischargeDate', 'DiagnosisCode', 'DiagnosisDescription', 'ProcedureIDs', 'TreatmentIDs', 'MedicationIDs']]
        elif table_name == 'PatientTreatment':
            df = df[['PatientTreatmentID', 'PatientID', 'AdmissionID', 'DoctorCode', 'TreatmentCode', 'TreatmentDescription', 'TreatmentDate']]
        
        for index, row in df.iterrows():
            try:
                row.to_frame().T.to_sql(table_name, conn, if_exists='append', index=False)
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    pass
                else:
                    raise

# Schema to drop existing tables
drop_schema = '''
DROP TABLE IF EXISTS Patient;
DROP TABLE IF EXISTS Department;
DROP TABLE IF EXISTS Medication;
DROP TABLE IF EXISTS Treatment;
DROP TABLE IF EXISTS Doctor;
DROP TABLE IF EXISTS Nurse;
DROP TABLE IF EXISTS EmployeeSalary;
DROP TABLE IF EXISTS Diagnosis;
DROP TABLE IF EXISTS Bed;
DROP TABLE IF EXISTS Surgery;
DROP TABLE IF EXISTS SurgeryPatient;
DROP TABLE IF EXISTS Admission;
DROP TABLE IF EXISTS AdministrativeStaff;
DROP TABLE IF EXISTS PatientTreatment;
'''

# Schema to create new tables
create_schema = '''
-- Create Patient table
CREATE TABLE IF NOT EXISTS Patient (
    PatientID VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(100),
    Age INT,
    Gender VARCHAR(10),
    PhoneNumber VARCHAR(15),
    Address VARCHAR(255),
    Email VARCHAR(100),
    EmergencyContactName VARCHAR(100),
    EmergencyContactRelation VARCHAR(50),
    EmergencyContactPhone VARCHAR(15)
);

-- Create Department table
CREATE TABLE IF NOT EXISTS Department (
    DepartmentCode VARCHAR(10) PRIMARY KEY,
    DepartmentName VARCHAR(100),
    HeadOfDepartment INT,
    FOREIGN KEY (HeadOfDepartment) REFERENCES Doctor(DoctorCode)
);

-- Create Medication table
CREATE TABLE IF NOT EXISTS Medication (
    MedicationCode VARCHAR(10) PRIMARY KEY,
    Description VARCHAR(255)
);

-- Create Treatment table
CREATE TABLE IF NOT EXISTS Treatment (
    TreatmentCode VARCHAR(10) PRIMARY KEY,
    Description VARCHAR(255)
);

-- Create Doctor table
CREATE TABLE IF NOT EXISTS Doctor (
    DoctorCode INT PRIMARY KEY,
    Name VARCHAR(100),
    Age INT,
    Gender VARCHAR(10),
    Phone VARCHAR(15),
    Email VARCHAR(100),
    Specialization VARCHAR(100),
    Address VARCHAR(255)
);

-- Create Nurse table
CREATE TABLE IF NOT EXISTS Nurse (
    NurseCode INT PRIMARY KEY,
    Name VARCHAR(100),
    Age INT,
    Gender VARCHAR(10),
    Phone VARCHAR(15),
    Email VARCHAR(100),
    DepartmentCode VARCHAR(10),
    FOREIGN KEY (DepartmentCode) REFERENCES Department(DepartmentCode)
);

-- Create EmployeeSalary table
CREATE TABLE IF NOT EXISTS EmployeeSalary (
    EmployeeCode VARCHAR(10) PRIMARY KEY,
    EmployeeID VARCHAR(10),
    Role VARCHAR(20),
    HireDate DATE,
    Salary DECIMAL(10, 2),
    PromotionDate DATE,
    SalaryIncrease DECIMAL(10, 2),
    FOREIGN KEY (EmployeeID) REFERENCES Doctor(DoctorCode)
    ON DELETE CASCADE,
    FOREIGN KEY (EmployeeID) REFERENCES Nurse(NurseCode)
    ON DELETE CASCADE,
    FOREIGN KEY (EmployeeID) REFERENCES AdministrativeStaff(Code)
    ON DELETE CASCADE
);

-- Create Diagnosis table
CREATE TABLE IF NOT EXISTS Diagnosis (
    DiagnosisCode VARCHAR(10) PRIMARY KEY,
    Description VARCHAR(255)
);

-- Create Bed table
CREATE TABLE IF NOT EXISTS Bed (
    BedCode VARCHAR(10) PRIMARY KEY,
    Status BOOLEAN,
    DepartmentCode VARCHAR(10),
    FOREIGN KEY (DepartmentCode) REFERENCES Department(DepartmentCode)
);

-- Create Surgery table
CREATE TABLE IF NOT EXISTS Surgery (
    SurgeryCode VARCHAR(10) PRIMARY KEY,
    Description VARCHAR(255)
);

-- Create SurgeryPatient table
CREATE TABLE IF NOT EXISTS SurgeryPatient (
    ProcedureID VARCHAR(10) PRIMARY KEY,
    PatientID VARCHAR(10),
    AdmissionID VARCHAR(10),
    DoctorCode VARCHAR(10),
    SurgeryCode VARCHAR(10),
    SurgeryDescription VARCHAR(255),
    SurgeryDate DATE,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (AdmissionID) REFERENCES Admission(AdmissionID),
    FOREIGN KEY (DoctorCode) REFERENCES Doctor(DoctorCode),
    FOREIGN KEY (SurgeryCode) REFERENCES Surgery(SurgeryCode)
);

-- Create Admission table
CREATE TABLE IF NOT EXISTS Admission (
    AdmissionID VARCHAR(10) PRIMARY KEY,
    PatientID VARCHAR(10),
    DoctorID VARCHAR(10),
    DepartmentID VARCHAR(10),
    AdmissionDate DATE,
    DischargeDate DATE,
    DiagnosisCode VARCHAR(10),
    DiagnosisDescription VARCHAR(255),
    ProcedureIDs TEXT,
    TreatmentIDs TEXT,
    MedicationIDs TEXT,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorCode),
    FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentCode),
    FOREIGN KEY (DiagnosisCode) REFERENCES Diagnosis(DiagnosisCode)
);

-- Create PatientTreatment table
CREATE TABLE IF NOT EXISTS PatientTreatment (
    PatientTreatmentID VARCHAR(10) PRIMARY KEY,
    PatientID VARCHAR(10),
    AdmissionID VARCHAR(10),
    DoctorCode VARCHAR(10),
    TreatmentCode VARCHAR(10),
    TreatmentDescription VARCHAR(255),
    TreatmentDate DATE,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (AdmissionID) REFERENCES Admission(AdmissionID),
    FOREIGN KEY (DoctorCode) REFERENCES Doctor(DoctorCode),
    FOREIGN KEY (TreatmentCode) REFERENCES Treatment(TreatmentCode)
);

-- Create AdministrativeStaff table
CREATE TABLE IF NOT EXISTS AdministrativeStaff (
    Code VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(100),
    Age INT,
    Gender VARCHAR(10),
    Phone VARCHAR(15),
    Role VARCHAR(100),
    Address VARCHAR(255),
    Email VARCHAR(100)
);
'''

# Execute schema drop and creation with retry logic
execute_with_retry(cursor, drop_schema)
execute_with_retry(cursor, create_schema)

# Load JSON data into tables
base_path = './data_ibm/healthcare_db/normalized_db/json files/'

load_json_to_db(base_path + 'patients.json', 'Patient', conn)
load_json_to_db(base_path + 'departments.json', 'Department', conn)
load_json_to_db(base_path + 'medications.json', 'Medication', conn)
load_json_to_db(base_path + 'treatments.json', 'Treatment', conn)
load_json_to_db(base_path + 'doctors.json', 'Doctor', conn)
load_json_to_db(base_path + 'nurses.json', 'Nurse', conn)
load_json_to_db(base_path + 'bed.json', 'Bed', conn)
load_json_to_db(base_path + 'diagnoses.json', 'Diagnosis', conn)
load_json_to_db(base_path + 'surgeries.json', 'Surgery', conn)
load_json_to_db(base_path + 'administratives.json', 'AdministrativeStaff', conn)
load_json_to_db(base_path + 'employee.json', 'EmployeeSalary', conn)
load_json_to_db(base_path + 'surgery_patient.json', 'SurgeryPatient', conn)
load_json_to_db(base_path + 'patient_treatment.json', 'PatientTreatment', conn)
load_json_to_db(base_path + 'admissions.json', 'Admission', conn)

# Commit and close the connection
conn.commit()
conn.close()

print("Database has been populated with the provided JSON data.")
