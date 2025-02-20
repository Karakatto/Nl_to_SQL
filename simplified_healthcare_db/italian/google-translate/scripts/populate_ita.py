import json
import sqlite3

# Paths to the translated JSON data
json_paths = {
    "patients": './data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_db/ita_schema_and_population/translated_json_files/patients_translated.json',
    "doctors": './data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_db/ita_schema_and_population/translated_json_files/doctors_translated.json',
    "departments": './data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_db/ita_schema_and_population/translated_json_files/departments_translated.json',
    "admissions": './data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_db/ita_schema_and_population/translated_json_files/admissions_translated.json',
    "treatments": './data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_db/ita_schema_and_population/translated_json_files/treatments_translated.json',
    "medications": './data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_db/ita_schema_and_population/translated_json_files/medications_translated.json',
    "surgeries": './data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_db/ita_schema_and_population/translated_json_files/surgeries_translated.json'
}

# Load the translated JSON data
with open(json_paths["patients"]) as f:
    patients = json.load(f)

with open(json_paths["doctors"]) as f:
    doctors = json.load(f)

# Load the translated JSON data for departments
with open(json_paths["departments"]) as f:
    departments = json.load(f)

# Load the translated JSON data for admissions
with open(json_paths["admissions"]) as f:
    admissions = json.load(f)

with open(json_paths["treatments"]) as f:
    treatments = json.load(f)

with open(json_paths["medications"]) as f:
    medications = json.load(f)

with open(json_paths["surgeries"]) as f:
    surgeries = json.load(f)

# Connect to SQLite database (or create it)
conn = sqlite3.connect('./data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_db/ita_schema_and_population/hospital_management_ita.db')
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
    """, (
        patient["ID_paziente"], 
        patient["Nome"], 
        patient["Data_nascita"], 
        patient["Genere"], 
        patient["Numero_di_telefono"], 
        patient["Indirizzo"], 
        patient["Email"], 
        patient["NominativoContattoEmergenza"], 
        patient["RelazioneContattoEmergenza"], 
        patient["TelefonoContattoEmergenza"]
    ))

def insert_or_ignore_doctor(doctor):
    cursor.execute("""
    INSERT OR IGNORE INTO Medici (ID_medico, Nome, Data_di_nascita, Genere, Telefono, Email, Specializzazione, Indirizzo)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        doctor["ID_medico"], 
        doctor["Nome"], 
        doctor.get("Data_di_nascita"), 
        doctor["Genere"], 
        doctor["Telefono"], 
        doctor["Email"], 
        doctor["Specializzazione"], 
        doctor["Indirizzo"]
    ))

def insert_or_ignore_department(department):
    # Debug print to verify the structure of each department entry
    print("Department Entry:", department)
    cursor.execute("""
    INSERT OR IGNORE INTO Reparti (ID_reparto, nome_reparto, telefono, email, direttore_reparto)
    VALUES (?, ?, ?, ?, ?)
    """, (
        department.get("ID_reparto"), 
        department.get("nome_reparto"), 
        department.get("telefono"), 
        department.get("email"), 
        department.get("direttore_reparto")
    ))


# Populate Pazienti table
for patient in patients:
    insert_or_ignore_patient(patient)

# Populate Medici table
for doctor in doctors:
    insert_or_ignore_doctor(doctor)

# Populate Reparti table
for department in departments:
    insert_or_ignore_department(department)

def replace_codes_and_insert(admission):
    # Debug print to verify the structure of each admission entry
    print("Admission Entry:", admission)
    
    # Safely retrieve values using .get() to avoid KeyError
    procedures = ", ".join(admission.get("Procedure", []))
    treatments = ", ".join(admission.get("Trattamenti", []))
    medications = ", ".join(admission.get("Farmaci", []))
    diagnosis = admission.get("Diagnosi", "")
    
    cursor.execute("""
    INSERT INTO Ricoveri (ID_ricovero, ID_paziente, ID_medico, ID_reparto, Data_ricovero, Data_dimissione, Diagnosi, Trattamenti, Procedure, Farmaci)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        admission.get("ID_ricovero"), 
        admission.get("ID_paziente"), 
        admission.get("ID_medico"), 
        admission.get("ID_reparto"), 
        admission.get("Data_ricovero"), 
        admission.get("Data_dimissione"), 
        diagnosis, 
        treatments, 
        procedures, 
        medications
    ))

    # Insert individual procedures, treatments, and medications into their respective tables
    for procedure in admission.get("Procedure", []):
        cursor.execute("""
        INSERT INTO Procedure (ID_ricovero, Descrizione)
        VALUES (?, ?)
        """, (admission.get("ID_ricovero"), procedure))

    for treatment in admission.get("Trattamenti", []):
        cursor.execute("""
        INSERT INTO Trattamenti (ID_ricovero, Descrizione)
        VALUES (?, ?)
        """, (admission.get("ID_ricovero"), treatment))

    for medication in admission.get("Farmaci", []):
        cursor.execute("""
        INSERT INTO Farmaci (ID_ricovero, Descrizione)
        VALUES (?, ?)
        """, (admission.get("ID_ricovero"), medication))


# Transform and populate Ricoveri data
for admission in admissions:
    replace_codes_and_insert(admission)

# Commit changes and close connection
conn.commit()
conn.close()

print("Database populated successfully.")
