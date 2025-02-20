import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect('./data_ibm/healthcare_db/simplified_db/simplified_healthcare.db')
cursor = conn.cursor()

# Drop tables if they exist for a fresh start
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

# Commit changes and close connection temporarily
conn.commit()
conn.close()

# Reopen connection to verify schema
conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()

# Print schema for verification
cursor.execute("PRAGMA table_info(Admission)")
columns = cursor.fetchall()
print("Admission table schema:")
for column in columns:
    print(column)

# Close connection
conn.close()
