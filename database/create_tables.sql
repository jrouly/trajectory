-- Create Schools table.
CREATE TABLE IF NOT EXISTS Schools
 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
  Name TEXT NOT NULL UNIQUE,
  Abbreviation TEXT NOT NULL UNIQUE,
  Web TEXT);


-- Create Departments table.
CREATE TABLE IF NOT EXISTS Departments
 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
  SchoolID INTEGER NOT NULL,
  Name TEXT NOT NULL,
  Abbreviation TEXT NOT NULL,
  Web TEXT,
  FOREIGN KEY(SchoolID) REFERENCES Schools(ID));


-- Create Programs table.
CREATE TABLE IF NOT EXISTS Programs
 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
  SchoolID INTEGER NOT NULL,
  Name TEXT NOT NULL,
  Abbreviation TEXT NOT NULL,
  FOREIGN KEY(SchoolID) REFERENCES Schools(ID));


-- Create Courses table.
CREATE TABLE IF NOT EXISTS Courses
 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
  DepartmentID INTEGER NOT NULL,
  Num TEXT NOT NULL,
  Title TEXT NOT NULL,
  Description TEXT NOT NULL,
  FOREIGN KEY(DepartmentID) REFERENCES Departments(ID));


-- Create ProgramRequirements table.
CREATE TABLE IF NOT EXISTS ProgramRequirements
 (Program INTEGER NOT NULL,
  Course INTEGER NOT NULL,
  PRIMARY KEY(Program, Course),
  FOREIGN KEY(Program) REFERENCES Programs(ID),
  FOREIGN KEY(Course) REFERENCES Courses(ID));


--- Create Prerequisites table.
CREATE TABLE IF NOT EXISTS Prerequisites
 (Course INTEGER NOT NULL,
  Prerequisite INTEGER NOT NULL,
  PRIMARY KEY(Course, Prerequisite),
  FOREIGN KEY(Course) REFERENCES Courses(ID)
  FOREIGN KEY(Prerequisite) REFERENCES Courses(ID));

