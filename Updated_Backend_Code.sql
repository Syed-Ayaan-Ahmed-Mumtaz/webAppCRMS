-- === CREATE DATABASE ===
CREATE DATABASE RECORDS;
GO

USE RECORDS;
GO

-- === CREATE TABLES ===

-- Users table
CREATE TABLE Users (
  UserID INT PRIMARY KEY IDENTITY,
  Username NVARCHAR(50) UNIQUE NOT NULL,
  Password NVARCHAR(50) NOT NULL
);
GO

-- Criminal table
CREATE TABLE Criminal(
  CriminalID INT PRIMARY KEY IDENTITY,
  Name VARCHAR(100) NOT NULL,
  Age INT,
  Crime_Type VARCHAR(50) NOT NULL
);
GO

-- Case table (reserved keyword handled safely)
CREATE TABLE [Case](
  CaseID INT PRIMARY KEY IDENTITY,
  CriminalID INT,
  Name VARCHAR(255),
  Description NVARCHAR(MAX),
  Victim_Name VARCHAR(100) NOT NULL,
  Status VARCHAR(20) NOT NULL,
  Crime_Date DATE,
  FOREIGN KEY(CriminalID) REFERENCES Criminal(CriminalID)
);
GO

-- Officer table
CREATE TABLE Officer(
  OfficerID INT PRIMARY KEY IDENTITY,
  Name VARCHAR(100) NOT NULL,
  Rank VARCHAR(20) NOT NULL,
  Department VARCHAR(30) NOT NULL,
  CaseID INT UNIQUE,
  FOREIGN KEY(CaseID) REFERENCES [Case](CaseID)
);
GO

-- Report table
CREATE TABLE Report(
  ReportID INT PRIMARY KEY IDENTITY,
  CaseID INT UNIQUE,
  Report_Date DATE NOT NULL,
  FOREIGN KEY(CaseID) REFERENCES [Case](CaseID)
);
GO

-- Suspect table
CREATE TABLE Suspect(
  SuspectID INT PRIMARY KEY IDENTITY,
  ReportID INT,
  CaseID INT,
  Name VARCHAR(100) NOT NULL,
  Age INT NOT NULL,
  FOREIGN KEY(ReportID) REFERENCES Report(ReportID),
  FOREIGN KEY(CaseID) REFERENCES [Case](CaseID)
);
GO

-- === INSERT TEST DATA ===

-- Insert 10 Criminals
INSERT INTO Criminal (Name, Age, Crime_Type) VALUES
('John Doe', 34, 'Robbery'),
('Jane Smith', 29, 'Fraud'),
('Mike Johnson', 42, 'Murder'),
('Sarah Lee', 25, 'Arson'),
('David Kim', 37, 'Burglary'),
('Emily Davis', 31, 'Kidnapping'),
('Robert Brown', 45, 'Assault'),
('Laura Wilson', 28, 'Cybercrime'),
('Daniel Thomas', 39, 'Extortion'),
('Olivia Martinez', 33, 'Bribery');
GO

-- Insert 10 Cases linked to Criminals
INSERT INTO [Case] (CriminalID, Name, Description, Victim_Name, Status, Crime_Date) VALUES
(1, 'Bank Robbery Case', 'Robbery at City Bank downtown.', 'Paul Miller', 'Open', '2024-02-10'),
(2, 'Corporate Fraud', 'Embezzlement of company funds.', 'CEO CorpX', 'Closed', '2023-11-05'),
(3, 'Homicide Downtown', 'Stabbing reported near central park.', 'Lisa Ray', 'Open', '2024-04-22'),
(4, 'Warehouse Arson', 'Suspicious fire at storage facility.', 'Warehouse Owner', 'Under Investigation', '2024-03-15'),
(5, 'Residential Burglary', 'Break-in reported in uptown area.', 'Steve Parker', 'Closed', '2023-10-01'),
(6, 'Child Kidnapping', 'Missing child reported in school area.', 'Parents', 'Open', '2024-01-09'),
(7, 'Bar Assault Case', 'Physical fight at local bar.', 'Victim A', 'Under Investigation', '2024-02-28'),
(8, 'Data Breach', 'Unauthorized system breach.', 'IT Company', 'Open', '2024-05-11'),
(9, 'Extortion Call', 'Threats demanding money.', 'Businessman B', 'Closed', '2023-09-12'),
(10, 'Government Bribery', 'Politician caught accepting bribe.', 'Public Prosecutor', 'Closed', '2023-08-03');
GO

-- Insert 10 Officers linked to Cases
INSERT INTO Officer (Name, Rank, Department, CaseID) VALUES
('Officer Mark', 'Detective', 'Robbery Unit', 1),
('Officer Kelly', 'Inspector', 'Financial Crimes', 2),
('Officer Alan', 'Lieutenant', 'Homicide Unit', 3),
('Officer Susan', 'Captain', 'Fire Dept', 4),
('Officer Brian', 'Detective', 'Burglary Unit', 5),
('Officer Diana', 'Sergeant', 'Special Victims Unit', 6),
('Officer Luke', 'Inspector', 'Assault Unit', 7),
('Officer Emma', 'Lieutenant', 'Cybercrime Unit', 8),
('Officer Steve', 'Captain', 'Organized Crime', 9),
('Officer Olivia', 'Detective', 'Anti-Corruption Unit', 10);
GO

-- Insert 10 Reports linked to Cases
INSERT INTO Report (CaseID, Report_Date) VALUES
(1, '2024-02-12'),
(2, '2023-11-06'),
(3, '2024-04-25'),
(4, '2024-03-16'),
(5, '2023-10-02'),
(6, '2024-01-10'),
(7, '2024-03-01'),
(8, '2024-05-12'),
(9, '2023-09-13'),
(10, '2023-08-04');
GO

-- Insert 10 Suspects linked to Reports and Cases
INSERT INTO Suspect (ReportID, CaseID, Name, Age) VALUES
(1, 1, 'James Brown', 40),
(2, 2, 'Patricia White', 35),
(3, 3, 'Henry Green', 30),
(4, 4, 'Victoria Adams', 27),
(5, 5, 'Edward Scott', 50),
(6, 6, 'Samantha Turner', 32),
(7, 7, 'Anthony Lewis', 29),
(8, 8, 'Natalie Hall', 26),
(9, 9, 'Jason Young', 41),
(10, 10, 'Rachel Walker', 38);
GO

-- (Optional: Insert Admin User — only if you want)
-- INSERT INTO Users (Username, Password) VALUES ('admin', 'admin123');
-- GO