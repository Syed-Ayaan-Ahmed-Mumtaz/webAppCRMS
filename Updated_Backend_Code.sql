CREATE DATABASE RECORDS;
GO

USE RECORDS;
GO

CREATE TABLE Users (
    UserID INT IDENTITY PRIMARY KEY,
    Username NVARCHAR(50) UNIQUE NOT NULL,
    Password NVARCHAR(50) NOT NULL
);
GO

CREATE TABLE Criminal (
    CriminalID INT IDENTITY PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Age INT,
    Crime_Type VARCHAR(50) NOT NULL
);
GO

CREATE TABLE [Case] (
    CaseID INT IDENTITY PRIMARY KEY,
    CriminalID INT,
    Name VARCHAR(255),
    Description NVARCHAR(MAX),
    Victim_Name VARCHAR(100) NOT NULL,
    Status VARCHAR(30) NOT NULL,
    Crime_Date DATE,
    FOREIGN KEY (CriminalID) REFERENCES Criminal(CriminalID)
);
GO

CREATE TABLE Officer (
    OfficerID INT IDENTITY PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Rank VARCHAR(30) NOT NULL,
    Department VARCHAR(50) NOT NULL,
    CaseID INT UNIQUE,
    FOREIGN KEY (CaseID) REFERENCES [Case](CaseID)
);
GO

CREATE TABLE Report (
    ReportID INT IDENTITY PRIMARY KEY,
    CaseID INT UNIQUE,
    Report_Date DATE NOT NULL,
    FOREIGN KEY (CaseID) REFERENCES [Case](CaseID)
);
GO

CREATE TABLE Suspect (
    SuspectID INT IDENTITY PRIMARY KEY,
    ReportID INT,
    CaseID INT,
    Name VARCHAR(100) NOT NULL,
    Age INT NOT NULL,
    FOREIGN KEY (ReportID) REFERENCES Report(ReportID),
    FOREIGN KEY (CaseID) REFERENCES [Case](CaseID)
);
GO

INSERT INTO Users (Username, Password)
VALUES ('admin', 'admin123');
GO

INSERT INTO Criminal (Name, Age, Crime_Type) VALUES
('Ahmed Khan', 35, 'Robbery'),
('Sara Ali', 28, 'Fraud'),
('Bilal Hussain', 40, 'Assault'),
('Ayesha Noor', 22, 'Burglary'),
('Zain Malik', 50, 'Murder'),
('Nida Kamal', 30, 'Arson'),
('Faisal Mehmood', 45, 'Kidnapping'),
('Hira Naveed', 33, 'Cybercrime'),
('Kamran Sheikh', 38, 'Smuggling'),
('Sana Iqbal', 27, 'Drug Trafficking');
GO

INSERT INTO [Case] (CriminalID, Name, Description, Victim_Name, Status, Crime_Date) VALUES
(1, 'Bank Robbery Case', 'Robbery at main bank branch', 'Ali Raza', 'Open', '2023-04-01'),
(2, 'Corporate Fraud Case', 'Embezzlement in firm', 'Fatima Bano', 'Closed', '2023-03-15'),
(3, 'Assault Incident', 'Physical assault during argument', 'Imran Shah', 'Under Investigation', '2023-05-10'),
(4, 'Burglary Case', 'Break-in reported at residence', 'Sadia Anwar', 'Open', '2023-06-25'),
(5, 'Murder Case', 'Homicide reported in park', 'Omar Siddiqui', 'Closed', '2023-02-12'),
(6, 'Arson Case', 'Factory set on fire deliberately', 'Waqas Ahmed', 'Open', '2023-01-08'),
(7, 'Kidnapping Case', 'Abduction of minor', 'Sajida Hussain', 'Under Investigation', '2023-07-04'),
(8, 'Cybercrime Case', 'Unauthorized hacking and fraud', 'Nasir Iqbal', 'Open', '2023-09-20'),
(9, 'Smuggling Case', 'Illegal imports seized', 'Amina Javed', 'Closed', '2023-08-11'),
(10, 'Drug Trafficking Case', 'Major drug cartel busted', 'Adnan Saleem', 'Under Investigation', '2023-10-30');
GO

INSERT INTO Officer (Name, Rank, Department, CaseID) VALUES
('Officer Aslam', 'Sergeant', 'Robbery', 1),
('Officer Nadeem', 'Lieutenant', 'Fraud', 2),
('Officer Salman', 'Inspector', 'Assault', 3),
('Officer Yasir', 'Detective', 'Burglary', 4),
('Officer Zeeshan', 'Captain', 'Homicide', 5),
('Officer Farhan', 'Detective', 'Arson', 6),
('Officer Rashid', 'Sergeant', 'Kidnapping', 7),
('Officer Irfan', 'Lieutenant', 'Cybercrime', 8),
('Officer Jamil', 'Inspector', 'Smuggling', 9),
('Officer Khalid', 'Captain', 'Narcotics', 10);
GO

INSERT INTO Report (CaseID, Report_Date) VALUES
(1, '2023-04-02'),
(2, '2023-03-16'),
(3, '2023-05-11'),
(4, '2023-06-26'),
(5, '2023-02-13'),
(6, '2023-01-09'),
(7, '2023-07-05'),
(8, '2023-09-21'),
(9, '2023-08-12'),
(10, '2023-10-31');
GO

INSERT INTO Suspect (ReportID, CaseID, Name, Age) VALUES
(1, 1, 'Hamza Tariq', 34),
(2, 2, 'Rabia Anwar', 29),
(3, 3, 'Zubair Latif', 41),
(4, 4, 'Maria Waheed', 26),
(5, 5, 'Kashif Rauf', 52),
(6, 6, 'Sadia Jamil', 35),
(7, 7, 'Fahad Bashir', 45),
(8, 8, 'Shazia Shabbir', 37),
(9, 9, 'Talha Irfan', 58),
(10, 10, 'Samina Khalid', 32);
GO
