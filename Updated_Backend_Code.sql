CREATE DATABASE RECORDS;
GO

USE RECORDS;
GO

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

-- Case table (renamed safely using brackets since 'Case' is a reserved keyword)
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

-- Insert initial admin user
INSERT INTO Users (Username, Password)
VALUES ('admin', 'admin123');
GO