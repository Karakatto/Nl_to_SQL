CREATE TABLE Patient (
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
);

CREATE TABLE Doctor (
    DoctorCode VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(100),
    DateOfBirth DATE,
    Gender VARCHAR(10),
    Phone VARCHAR(15),
    Email VARCHAR(100),
    Specialization VARCHAR(100),
    Address VARCHAR(255)
);

CREATE TABLE Department (
    DepartmentCode VARCHAR(10) PRIMARY KEY,
    DepartmentName VARCHAR(100),
    Phone VARCHAR(15),
    Email VARCHAR(100),
    HeadOfDepartment VARCHAR(10),
    FOREIGN KEY (HeadOfDepartment) REFERENCES Doctor(DoctorCode)
);

CREATE TABLE Admission (
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
);

CREATE TABLE Procedure (
    AdmissionID VARCHAR(10),
    ProcedureDescription VARCHAR(255),
    FOREIGN KEY (AdmissionID) REFERENCES Admission(AdmissionID)
);

CREATE TABLE Treatment (
    AdmissionID VARCHAR(10),
    TreatmentDescription VARCHAR(255),
    FOREIGN KEY (AdmissionID) REFERENCES Admission(AdmissionID)
);

CREATE TABLE Medication (
    AdmissionID VARCHAR(10),
    MedicationDescription VARCHAR(255),
    FOREIGN KEY (AdmissionID) REFERENCES Admission(AdmissionID)
);
