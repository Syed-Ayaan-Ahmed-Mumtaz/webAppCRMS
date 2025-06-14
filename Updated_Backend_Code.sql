CREATE DATABASE RECORDS;
USE RECORDS;

-- Create tables in proper order

CREATE TABLE Users (
  UserID INT PRIMARY KEY IDENTITY,
  Username NVARCHAR(50) UNIQUE NOT NULL,
  Password NVARCHAR(50) NOT NULL
);

CREATE TABLE Criminal(
  CriminalID INT PRIMARY KEY,
  Name VARCHAR(100) NOT NULL,
  Age INT,
  Crime_Type VARCHAR(50) NOT NULL
);

CREATE TABLE Officer(
  OfficerID INT PRIMARY KEY,
  Name VARCHAR(100) NOT NULL,
  Rank VARCHAR(20) NOT NULL,
  Department VARCHAR(30) NOT NULL,
  CaseID INT UNIQUE,  -- UNIQUE constraint enforces 1:1 relationship
  FOREIGN KEY(CaseID) REFERENCES Case(CaseID)
);

CREATE TABLE Case(
  CaseID INT PRIMARY KEY,
  CriminalID INT,
  Victim_Name VARCHAR(100) NOT NULL,
  Status VARCHAR(20) NOT NULL,
  FOREIGN KEY(CriminalID) REFERENCES Criminal(CriminalID)
);

CREATE TABLE Report(
  ReportID INT PRIMARY KEY,
  CaseID INT UNIQUE,
  Report_Date DATE NOT NULL,
  FOREIGN KEY(CaseID) REFERENCES Case(CaseID)
);

CREATE TABLE Suspect(
  SuspectID INT PRIMARY KEY,
  ReportID INT,
  CaseID INT,
  Name VARCHAR(100) NOT NULL,
  Age INT NOT NULL,
  FOREIGN KEY(ReportID) REFERENCES Report(ReportID),
  FOREIGN KEY(CaseID) REFERENCES Case(CaseID)
);

INSERT INTO Users (Username, Password)
VALUES ('admin', 'admin123');