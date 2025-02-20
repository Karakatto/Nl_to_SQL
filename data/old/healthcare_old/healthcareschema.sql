PRAGMA foreign_keys = ON;

CREATE TABLE "patient" (
    "id" INTEGER PRIMARY KEY,
    "name" TEXT,
    "dob" TEXT,
    "gender" TEXT,
    "address" TEXT,
    "phone" TEXT,
    "email" TEXT
);

CREATE TABLE "doctor" (
    "id" INTEGER PRIMARY KEY,
    "name" TEXT,
    "specialization" TEXT,
    "department" TEXT,
    "phone" TEXT,
    "email" TEXT
);

CREATE TABLE "appointment" (
    "id" INTEGER PRIMARY KEY,
    "patient_id" INTEGER,
    "doctor_id" INTEGER,
    "date" TEXT,
    "time" TEXT,
    "reason" TEXT,
    FOREIGN KEY ("patient_id") REFERENCES "patient" ("id"),
    FOREIGN KEY ("doctor_id") REFERENCES "doctor" ("id")
);

CREATE TABLE "treatment" (
    "id" INTEGER PRIMARY KEY,
    "appointment_id" INTEGER,
    "treatment_description" TEXT,
    "medication" TEXT,
    "dosage" TEXT,
    "notes" TEXT,
    FOREIGN KEY ("appointment_id") REFERENCES "appointment" ("id")
);

CREATE TABLE "billing" (
    "id" INTEGER PRIMARY KEY,
    "patient_id" INTEGER,
    "amount" REAL,
    "date" TEXT,
    "status" TEXT,
    FOREIGN KEY ("patient_id") REFERENCES "patient" ("id")
);

INSERT INTO "patient" VALUES (1, 'John Doe', '1980-01-01', 'M', '123 Main St', '555-1234', 'john.doe@example.com');
INSERT INTO "patient" VALUES (2, 'Jane Smith', '1990-02-02', 'F', '456 Oak St', '555-5678', 'jane.smith@example.com');
INSERT INTO "patient" VALUES (3, 'Jim Brown', '1975-03-03', 'M', '789 Pine St', '555-8765', 'jim.brown@example.com');
INSERT INTO "patient" VALUES (4, 'Emily Davis', '1985-04-04', 'F', '321 Elm St', '555-4321', 'emily.davis@example.com');
INSERT INTO "patient" VALUES (5, 'Michael Johnson', '1965-05-05', 'M', '654 Spruce St', '555-6789', 'michael.johnson@example.com');

INSERT INTO "doctor" VALUES (1, 'Dr. Alice Johnson', 'Cardiology', 'Cardiology', '555-1122', 'alice.johnson@example.com');
INSERT INTO "doctor" VALUES (2, 'Dr. Bob Lee', 'Neurology', 'Neurology', '555-3344', 'bob.lee@example.com');
INSERT INTO "doctor" VALUES (3, 'Dr. Carol White', 'Orthopedics', 'Orthopedics', '555-5566', 'carol.white@example.com');
INSERT INTO "doctor" VALUES (4, 'Dr. David Green', 'Pediatrics', 'Pediatrics', '555-7788', 'david.green@example.com');
INSERT INTO "doctor" VALUES (5, 'Dr. Eva Martinez', 'Dermatology', 'Dermatology', '555-9900', 'eva.martinez@example.com');

INSERT INTO "appointment" VALUES (1, 1, 1, '2023-01-01', '10:00', 'Routine Checkup');
INSERT INTO "appointment" VALUES (2, 2, 2, '2023-02-01', '11:00', 'Headache');
INSERT INTO "appointment" VALUES (3, 3, 3, '2023-03-01', '09:00', 'Knee Pain');
INSERT INTO "appointment" VALUES (4, 4, 4, '2023-04-01', '14:00', 'Fever');
INSERT INTO "appointment" VALUES (5, 5, 5, '2023-05-01', '13:00', 'Skin Rash');
INSERT INTO "appointment" VALUES (6, 1, 1, '2023-06-01', '10:00', 'Follow-up Checkup');
INSERT INTO "appointment" VALUES (7, 2, 2, '2023-07-01', '11:00', 'Migraine');
INSERT INTO "appointment" VALUES (8, 3, 3, '2023-08-01', '09:00', 'Back Pain');
INSERT INTO "appointment" VALUES (9, 4, 4, '2023-09-01', '14:00', 'Cough');
INSERT INTO "appointment" VALUES (10, 5, 5, '2023-10-01', '13:00', 'Skin Allergy');

INSERT INTO "treatment" VALUES (1, 1, 'Blood Test and ECG', 'Aspirin', '100 mg', 'Take one daily');
INSERT INTO "treatment" VALUES (2, 2, 'MRI Scan', 'Ibuprofen', '200 mg', 'Take one after meals');
INSERT INTO "treatment" VALUES (3, 3, 'X-Ray and Physical Therapy', 'Paracetamol', '500 mg', 'Take two daily');
INSERT INTO "treatment" VALUES (4, 4, 'Physical Examination', 'Paracetamol', '500 mg', 'Take two daily');
INSERT INTO "treatment" VALUES (5, 5, 'Topical Ointment', 'Hydrocortisone', 'Apply twice daily', 'Apply to affected area');
INSERT INTO "treatment" VALUES (6, 6, 'Blood Pressure Monitoring', 'Aspirin', '100 mg', 'Take one daily');
INSERT INTO "treatment" VALUES (7, 7, 'CT Scan', 'Sumatriptan', '50 mg', 'Take one during migraine');
INSERT INTO "treatment" VALUES (8, 8, 'Physical Therapy', 'Paracetamol', '500 mg', 'Take two daily');
INSERT INTO "treatment" VALUES (9, 9, 'Chest X-Ray', 'Cough Syrup', '10 ml', 'Take three times daily');
INSERT INTO "treatment" VALUES (10, 10, 'Allergy Test', 'Antihistamine', '10 mg', 'Take one daily');

INSERT INTO "billing" VALUES (1, 1, 200.00, '2023-01-02', 'Paid');
INSERT INTO "billing" VALUES (2, 2, 150.00, '2023-02-02', 'Pending');
INSERT INTO "billing" VALUES (3, 3, 300.00, '2023-03-02', 'Paid');
INSERT INTO "billing" VALUES (4, 4, 100.00, '2023-04-02', 'Pending');
INSERT INTO "billing" VALUES (5, 5, 250.00, '2023-05-02', 'Paid');
INSERT INTO "billing" VALUES (6, 1, 200.00, '2023-06-02', 'Pending');
INSERT INTO "billing" VALUES (7, 2, 150.00, '2023-07-02', 'Paid');
INSERT INTO "billing" VALUES (8, 3, 300.00, '2023-08-02', 'Pending');
INSERT INTO "billing" VALUES (9, 4, 100.00, '2023-09-02', 'Paid');
INSERT INTO "billing" VALUES (10, 5, 250.00, '2023-10-02', 'Pending');
