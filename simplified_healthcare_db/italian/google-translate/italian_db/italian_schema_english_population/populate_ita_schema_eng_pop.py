import json
import sqlite3

# Load the corrected JSON data from new directories
json_paths = {
    "patients": './data_ibm/healthcare_db/simplified_db/json_data/patients.json',
    "doctors": './data_ibm/healthcare_db/simplified_db/json_data/doctors.json',
    "departments": './data_ibm/healthcare_db/simplified_db/json_data/departments.json',
    "admissions": './data_ibm/healthcare_db/simplified_db/json_data/admissions.json',
    "treatments": './data_ibm/healthcare_db/simplified_db/json_data/treatments.json',
    "medications": './data_ibm/healthcare_db/simplified_db/json_data/medications.json',
    "surgeries": './data_ibm/healthcare_db/simplified_db/json_data/surgeries.json'
}

# Load data from JSON files
with open(json_paths["patients"]) as f:
    patients = json.load(f)

with open(json_paths["doctors"]) as f:
    doctors = json.load(f)

with open(json_paths["departments"]) as f:
    departments = json.load(f)

with open(json_paths["admissions"]) as f:
    admissions = json.load(f)

with open(json_paths["treatments"]) as f:
    treatments = json.load(f)

with open(json_paths["medications"]) as f:
    medications = json.load(f)

with open(json_paths["surgeries"]) as f:
    surgeries_data = json.load(f)

# Check if surgeries is a dictionary with a key like "surgeries" containing a list
if isinstance(surgeries_data, dict) and "surgeries" in surgeries_data:
    surgeries = surgeries_data["surgeries"]
else:
    surgeries = surgeries_data

# Create lookup dictionaries
treatment_dict = {t["TreatmentCode"]: t["Description"] for t in treatments}
medication_dict = {m["MedicationCode"]: m["Description"] for m in medications}
surgery_dict = {s["surgery_code"]: s["description"] for s in surgeries}

# Connect to SQLite database (or create it)
conn = sqlite3.connect('./data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_db/italian_schema_english_population/ita_schema_eng_pop_hospital_management_ita_schema.db')
cursor = conn.cursor()

# Drop existing tables if they exist
cursor.execute("DROP TABLE IF EXISTS Pazienti")
cursor.execute("DROP TABLE IF EXISTS Medici")
cursor.execute("DROP TABLE IF EXISTS Reparti")
cursor.execute("DROP TABLE IF EXISTS Ricoveri")
cursor.execute("DROP TABLE IF EXISTS Procedure")
cursor.execute("DROP TABLE IF EXISTS Trattamenti")
cursor.execute("DROP TABLE IF EXISTS Farmaci")

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS Pazienti (
    ID_paziente VARCHAR(10) PRIMARY KEY,
    Nome VARCHAR(100),
    Data_nascita DATE,
    Genere VARCHAR(10),
    Numero_di_telefono VARCHAR(15),
    Indirizzo VARCHAR(255),
    Email VARCHAR(100),
    NominativoContattoEmergenza VARCHAR(100),
    RelazioneContattoEmergenza VARCHAR(50),
    TelefonoContattoEmergenza VARCHAR(15)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Medici (
    ID_medico VARCHAR(10) PRIMARY KEY,
    Nome VARCHAR(100),
    Data_di_nascita DATE,
    Genere VARCHAR(10),
    Telefono VARCHAR(15),
    Email VARCHAR(100),
    Specializzazione VARCHAR(100),
    Indirizzo VARCHAR(255)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Reparti (
    ID_reparto VARCHAR(10) PRIMARY KEY,
    nome_reparto VARCHAR(100),
    telefono VARCHAR(15),
    email VARCHAR(100),
    direttore_reparto VARCHAR(10),
    FOREIGN KEY (direttore_reparto) REFERENCES Medici(ID_medico)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Ricoveri (
    ID_ricovero VARCHAR(10) PRIMARY KEY,
    ID_paziente VARCHAR(10),
    ID_medico VARCHAR(10),
    ID_reparto VARCHAR(10),
    Data_ricovero DATE,
    Data_dimissione DATE,
    Diagnosi VARCHAR(255),
    Trattamenti TEXT,
    Procedure TEXT,
    Farmaci TEXT,
    FOREIGN KEY (ID_paziente) REFERENCES Pazienti(ID_paziente),
    FOREIGN KEY (ID_medico) REFERENCES Medici(ID_medico),
    FOREIGN KEY (ID_reparto) REFERENCES Reparti(ID_reparto)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Procedure (
    ID_ricovero VARCHAR(10),
    Descrizione VARCHAR(255),
    FOREIGN KEY (ID_ricovero) REFERENCES Ricoveri(ID_ricovero)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Trattamenti (
    ID_ricovero VARCHAR(10),
    Descrizione VARCHAR(255),
    FOREIGN KEY (ID_ricovero) REFERENCES Ricoveri(ID_ricovero)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Farmaci (
    ID_ricovero VARCHAR(10),
    Descrizione VARCHAR(255),
    FOREIGN KEY (ID_ricovero) REFERENCES Ricoveri(ID_ricovero)
)
""")

# Function to insert or ignore a record if it exists
def insert_or_ignore_patient(patient):
    cursor.execute("""
    INSERT OR IGNORE INTO Pazienti (ID_paziente, Nome, Data_nascita, Genere, Numero_di_telefono, Indirizzo, Email, NominativoContattoEmergenza, RelazioneContattoEmergenza, TelefonoContattoEmergenza)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (patient["PatientID"], patient["Name"], patient["DateOfBirth"], patient["Gender"], patient["PhoneNumber"], patient["Address"], patient["Email"], patient["EmergencyContactName"], patient["EmergencyContactRelation"], patient["EmergencyContactPhone"]))

def insert_or_ignore_doctor(doctor):
    cursor.execute("""
    INSERT OR IGNORE INTO Medici (ID_medico, Nome, Data_di_nascita, Genere, Telefono, Email, Specializzazione, Indirizzo)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (doctor["Id"], doctor["Name"], doctor["DateOfBirth"], doctor["Gender"], doctor["Phone"], doctor["Email"], doctor["Specialization"], doctor["Address"]))

def insert_or_ignore_department(department):
    cursor.execute("""
    INSERT OR IGNORE INTO Reparti (ID_reparto, nome_reparto, telefono, email, direttore_reparto)
    VALUES (?, ?, ?, ?, ?)
    """, (department["dept_id"], department["dept_name"], department["phone"], department["email"], department["HeadOfDepartment"]))

# Populate Pazienti table
for patient in patients:
    insert_or_ignore_patient(patient)

# Populate Medici table
for doctor in doctors:
    insert_or_ignore_doctor(doctor)

# Populate Reparti table
for department in departments:
    insert_or_ignore_department(department)

# Function to replace codes with descriptions and populate related tables
def replace_codes_and_insert(admission):
    procedures = ", ".join(admission.get("Procedures", []))
    treatments = ", ".join(admission.get("Treatments", []))
    medications = ", ".join(admission.get("Medications", []))
    diagnosis = admission.get("Diagnosis", "")

    # Insert the admission record
    cursor.execute("""
    INSERT INTO Ricoveri (ID_ricovero, ID_paziente, ID_medico, ID_reparto, Data_ricovero, Data_dimissione, Diagnosi, Trattamenti, Procedure, Farmaci)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (admission["AdmissionID"], admission["PatientID"], admission["DoctorID"], admission["DepartmentID"], admission["AdmissionDate"], admission["DischargeDate"], diagnosis, treatments, procedures, medications))

    for procedure in admission.get("Procedures", []):
        cursor.execute("""
        INSERT INTO Procedure (ID_ricovero, Descrizione)
        VALUES (?, ?)
        """, (admission["AdmissionID"], procedure))

    for treatment in admission.get("Treatments", []):
        cursor.execute("""
        INSERT INTO Trattamenti (ID_ricovero, Descrizione)
        VALUES (?, ?)
        """, (admission["AdmissionID"], treatment))

    for medication in admission.get("Medications", []):
        cursor.execute("""
        INSERT INTO Farmaci (ID_ricovero, Descrizione)
        VALUES (?, ?)
        """, (admission["AdmissionID"], medication))

# Transform and populate admissions data
for admission in admissions:
    replace_codes_and_insert(admission)

# Commit changes and close connection
conn.commit()
conn.close()

print("Database populated successfully.")
