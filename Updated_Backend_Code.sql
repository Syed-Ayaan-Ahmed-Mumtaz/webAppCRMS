-- Updated_Backend_Codes.sql
-- If you are running this script for the first time or recreating the DB:

CREATE DATABASE RECORDS;
USE RECORDS;

-- Create tables in proper order
-- Users table first (no foreign keys)
CREATE TABLE Users (
  UserID INT PRIMARY KEY IDENTITY,
  Username NVARCHAR(50) UNIQUE NOT NULL,
  Password NVARCHAR(50) NOT NULL
);

-- Criminal table (no foreign keys)
CREATE TABLE Criminal(
  CriminalID INT PRIMARY KEY IDENTITY,
  Name VARCHAR(100) NOT NULL, -- This is the Criminal's Name
  Age INT,
  Crime_Type VARCHAR(50) NOT NULL
);

-- Case table - MODIFIED to include Name, Description, Crime_Date
CREATE TABLE Case(
  CaseID INT PRIMARY KEY IDENTITY,
  CriminalID INT,
  Name VARCHAR(255),          -- New: A specific name for the Case (e.g., "Robbery at Bank X")
  Description NVARCHAR(MAX),  -- New: Detailed description of the case
  Victim_Name VARCHAR(100) NOT NULL,
  Status VARCHAR(20) NOT NULL,
  Crime_Date DATE,            -- New: Date the crime occurred
  FOREIGN KEY(CriminalID) REFERENCES Criminal(CriminalID)
);

-- Officer table (depends on Case)
-- Note: The UNIQUE constraint on CaseID here implies 1 Officer per Case.
-- If multiple officers can be on a case, remove UNIQUE.
CREATE TABLE Officer(
  OfficerID INT PRIMARY KEY IDENTITY,
  Name VARCHAR(100) NOT NULL,
  Rank VARCHAR(20) NOT NULL,
  Department VARCHAR(30) NOT NULL,
  CaseID INT UNIQUE, -- UNIQUE constraint enforces 1:1 relationship
  FOREIGN KEY(CaseID) REFERENCES Case(CaseID)
);

-- Report table (depends on Case)
-- Note: The UNIQUE constraint on CaseID here implies 1 Report per Case.
-- If multiple reports can be on a case, remove UNIQUE.
CREATE TABLE Report(
  ReportID INT PRIMARY KEY IDENTITY,
  CaseID INT UNIQUE,
  Report_Date DATE NOT NULL,
  FOREIGN KEY(CaseID) REFERENCES Case(CaseID)
);

-- Suspect table (depends on Report and Case)
CREATE TABLE Suspect(
  SuspectID INT PRIMARY KEY IDENTITY,
  ReportID INT,
  CaseID INT,
  Name VARCHAR(100) NOT NULL,
  Age INT NOT NULL,
  FOREIGN KEY(ReportID) REFERENCES Report(ReportID),
  FOREIGN KEY(CaseID) REFERENCES Case(CaseID)
);

INSERT INTO Users (Username, Password)
VALUES ('admin', 'admin123');

-- IF YOUR DATABASE AND TABLES ALREADY EXIST, JUST RUN THESE ALTER COMMANDS:
-- USE RECORDS;
-- ALTER TABLE Case ADD Name VARCHAR(255);
-- ALTER TABLE Case ADD Description NVARCHAR(MAX);
-- ALTER TABLE Case ADD Crime_Date DATE;