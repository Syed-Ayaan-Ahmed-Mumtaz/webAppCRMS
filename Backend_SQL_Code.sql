CREATE DATABASE RECORDS;
USE RECORDS;

CREATE TABLE Users (
  UserID INT PRIMARY KEY IDENTITY,
  Username NVARCHAR(50) UNIQUE NOT NULL,
  Password NVARCHAR(50) NOT NULL
);

CREATE TABLE CriminalRecords (
  RecordID INT PRIMARY KEY IDENTITY,
  Name NVARCHAR(100) NOT NULL,           -- Entity Name
  Description NVARCHAR(MAX),             -- Description
  Status NVARCHAR(50),                   -- Status (e.g., Arrested, Under Investigation)
  CrimeDate DATE,                        -- Date of Crime
  Age INT,                               -- (Optional) More detail
  Gender NVARCHAR(10),                   -- (Optional)
  CrimeType NVARCHAR(100),               -- (Optional)
  OfficerName NVARCHAR(100)              -- (Optional)
);


-- Add a user for login testing
INSERT INTO Users (Username, Password) VALUES
('admin123', 'admin123');

-- Add sample criminal record
INSERT INTO CriminalRecords (Name, Age, Gender, CrimeType, ArrestDate, OfficerName, Description) VALUES
('John Doe', 30, 'Male', 'Robbery', '2025-06-05', 'Officer Ali', 'Caught stealing from a bank.');

SELECT * FROM Users 
WHERE Username = 'admin123' AND Password = 'admin123';

SELECT 
  RecordID AS [ID], 
  Name AS [Entity Name], 
  Description, 
  Status, 
  CrimeDate AS [Date]
FROM CriminalRecords;

UPDATE CriminalRecords
  SET 
    Status = 'Released',
    Description = 'Case resolved, person released'
  WHERE RecordID = 1;

DELETE FROM CriminalRecords 
WHERE RecordID = 1;

SELECT * FROM CriminalRecords 
WHERE RecordID = 1;



 