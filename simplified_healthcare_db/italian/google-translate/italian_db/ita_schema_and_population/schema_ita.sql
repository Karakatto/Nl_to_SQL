CREATE TABLE Pazienti (
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
);

CREATE TABLE Medici (
    ID_medico VARCHAR(10) PRIMARY KEY,
    Nome VARCHAR(100),
    Data_di_nascita DATE,
    Genere VARCHAR(10),
    Telefono VARCHAR(15),
    Email VARCHAR(100),
    Specializzazione VARCHAR(100),
    Indirizzo VARCHAR(255)
);

CREATE TABLE Reparti (
    ID_reparto VARCHAR(10) PRIMARY KEY,
    nome_reparto VARCHAR(100),
    telefono VARCHAR(15),
    email VARCHAR(100),
    direttore_reparto VARCHAR(10),
    FOREIGN KEY (direttore_reparto) REFERENCES Medici(Id)
);

CREATE TABLE Ricoveri (
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
);

CREATE TABLE Procedure (
    ID_ricovero VARCHAR(10),
    Descrizione VARCHAR(255),
    FOREIGN KEY (ID_ricovero) REFERENCES Ricoveri(ID_ricovero)
);

CREATE TABLE Trattamenti (
    ID_ricovero VARCHAR(10),
    Descrizione VARCHAR(255),
    FOREIGN KEY (ID_ricovero) REFERENCES Ricoveri(ID_ricovero)
);

CREATE TABLE Farmaci (
    ID_ricovero VARCHAR(10),
    Descrizione VARCHAR(255),
    FOREIGN KEY (ID_ricovero) REFERENCES Ricoveri(ID_ricovero)
);
