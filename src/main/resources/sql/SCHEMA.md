###Schools
Full data about any particular school, including its web address, name, and
any common abbreviation.

#####Relations
none


    |-------------------------------------------------|
    | ID | School Name  | School Abbrev | Web Address |
    | ID | Name         | Abbreviation  | Web         |
    |-------------------------------------------------|
    | 0  | George Mason | gmu           | gmu.edu     |
    | 1  | Portland St. | pdx           | pdx.edu     |
    |-------------------------------------------------|


###Departments
Full data about any department at a specific school

#####Relations
SchoolID -> Schools.ID  


    |-------------------------------------------------------------------|
    | ID | SchoolID | Department Name | Department Abbrev | Web Address |
    | ID | SchoolID | Name            | Abbreviation      | Web         |
    |-------------------------------------------------------------------|
    | 0  | 0        | Computer Sci.   | CS                | cs.gmu.edu  |
    | 1  | 0        | Statistics      | STAT              | -           |
    | 2  | 1        | Computer Sci.   | CS                | cs.pdx.edu  |
    |-------------------------------------------------------------------|


###Programs
A program of study (eg. the requirements of a degree offered by a
department).

#####Relations
SchoolID -> Schools.ID  


    |---------------------------------------------|
    | ID | SchoolID | Program Name | Abbreviation |
    | ID | SchoolID | Name         | Abbreviation |
    |---------------------------------------------|
    | 0  | 0        | GMU CS       | gmu_cs       |
    | 1  | 1        | PDX CS       | pdx_cs       |
    |---------------------------------------------|


###Courses
A course offering. Belongs to a department at a school.

#####Relations
DepartmentID -> Departments.ID  


    |-----------------------------------------------------------------------|
    | ID | DepartmentID | Course Number | Course Title | Course Description |
    | ID | DepartmentID | Num           | Title        | Description        |
    |-----------------------------------------------------------------------|
    | 0  | 0            | 101           | Intro to ... | This is a course.  |
    | 1  | 1            | 344           | Foobar       | fubar barfu        |
    | 2  | 0            | 450           | Databases    | orcle orcle orcle  |
    |-----------------------------------------------------------------------|


###Program Requirements
A course requirement for a particular program of study.

#####Relations
Program -> Programs.ID  
Course -> Courses.ID  


    |------------------|
    | Program | Course |
    | Program | Course |
    |------------------|
    | 0       | 0      |
    | 0       | 1      |
    | 0       | 2      |
    |------------------|


###Prerequisites
This table maps courses to their prerequisites.

#####Relations
Course -> Courses.ID  
Prerequisite -> Courses.ID  


    |-----------------------|
    | Course | Prerequisite |
    | Course | Prerequisite |
    |-----------------------|
    | 1      | 0            |
    |-----------------------|
