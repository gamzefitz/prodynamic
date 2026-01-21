BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Department" (
	"department_id"	INTEGER,
	"department_name"	nvarchar(100),
	PRIMARY KEY("department_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Employee" (
	"employee_id"	INTEGER,
	"first_name"	nvarchar(50),
	"last_name"	nvarchar(50),
	"email"	nvarchar(200) UNIQUE,
	"hire_date"	datetime,
	"department_id"	INTEGER,
	"job_id"	INTEGER,
	"is_manager"	Boolean,
	"weekly_hours"	DECIMAL(4, 1),
	PRIMARY KEY("employee_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Job" (
	"job_id"	INTEGER,
	"job_title"	nvarchar(100),
	"department_id"	INTEGER,
	PRIMARY KEY("job_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Salary" (
	"salary_id"	INTEGER,
	"employee_id"	INTEGER,
	"salary_amount"	INTEGER,
	PRIMARY KEY("salary_id" AUTOINCREMENT)
);
INSERT INTO "Department" VALUES (1,'IT');
INSERT INTO "Department" VALUES (2,'Finance');
INSERT INTO "Department" VALUES (3,'Human Resources');
INSERT INTO "Department" VALUES (4,'Sales');
INSERT INTO "Department" VALUES (5,'Operations');
INSERT INTO "Employee" VALUES (1,'John','Doe','john.doe@company.com','2022-01-15',1,1,'False',37.5);
INSERT INTO "Employee" VALUES (2,'Jane','Smith','jane.smith@company.com','2023-03-10',1,1,'False',37.5);
INSERT INTO "Employee" VALUES (3,'Mark','Taylor','mark.taylor@company.com','2021-06-20',1,2,'False',37.5);
INSERT INTO "Employee" VALUES (4,'Lucy','Brown','lucy.brown@company.com','2022-09-05',1,2,'False',37.5);
INSERT INTO "Employee" VALUES (5,'Alan','Green','alan.green@company.com','2023-02-12',1,3,'False',37.5);
INSERT INTO "Employee" VALUES (6,'Nina','White','nina.white@company.com','2024-01-08',1,3,'False',35);
INSERT INTO "Employee" VALUES (7,'Paul','Adams','paul.adams@company.com','2020-04-18',2,4,'False',37.5);
INSERT INTO "Employee" VALUES (8,'Emma','Clark','emma.clark@company.com','2021-11-22',2,4,'False',37.5);
INSERT INTO "Employee" VALUES (9,'Brian','Hill','brian.hill@company.com','2019-07-30',2,5,'False',37.5);
INSERT INTO "Employee" VALUES (10,'Sophia','Lewis','sophia.lewis@company.com','2022-05-14',2,5,'False',37.5);
INSERT INTO "Employee" VALUES (11,'Kevin','Scott','kevin.scott@company.com','2021-09-01',2,6,'False',37.5);
INSERT INTO "Employee" VALUES (12,'Olivia','Turner','olivia.turner@company.com','2023-06-19',2,6,'False',37.5);
INSERT INTO "Employee" VALUES (13,'Daniel','Walker','daniel.walker@company.com','2018-03-25',5,7,'True',40);
INSERT INTO "Employee" VALUES (14,'Rachel','Hall','rachel.hall@company.com','2020-10-11',5,7,'True',40);
INSERT INTO "Employee" VALUES (15,'Tom','Young','tom.young@company.com','2021-01-17',5,8,'False',37.5);
INSERT INTO "Employee" VALUES (16,'Laura','King','laura.king@company.com','2022-08-03',5,8,'False',37.5);
INSERT INTO "Employee" VALUES (17,'Chris','Wright','chris.wright@company.com','2023-04-27',5,9,'False',37.5);
INSERT INTO "Employee" VALUES (18,'Megan','Lopez','megan.lopez@company.com','2024-02-14',5,9,'False',35);
INSERT INTO "Employee" VALUES (19,'Hannah','Baker','hannah.baker@company.com','2019-12-02',3,10,'False',37.5);
INSERT INTO "Employee" VALUES (20,'Eric','Nelson','eric.nelson@company.com','2021-06-09',3,10,'False',37.5);
INSERT INTO "Employee" VALUES (21,'Amy','Carter','amy.carter@company.com','2022-02-21',3,11,'False',37.5);
INSERT INTO "Employee" VALUES (22,'Jason','Mitchell','jason.mitchell@company.com','2023-07-16',3,11,'False',37.5);
INSERT INTO "Employee" VALUES (23,'Rebecca','Perez','rebecca.perez@company.com','2020-05-28',3,12,'False',37.5);
INSERT INTO "Employee" VALUES (24,'David','Roberts','david.roberts@company.com','2024-01-05',3,12,'False',35);
INSERT INTO "Employee" VALUES (25,'Steven','Collins','steven.collins@company.com','2018-08-13',4,13,'False',37.5);
INSERT INTO "Employee" VALUES (26,'Angela','Reed','angela.reed@company.com','2021-03-19',4,13,'False',37.5);
INSERT INTO "Employee" VALUES (27,'Michael','Cook','michael.cook@company.com','2020-11-07',4,14,'True',40);
INSERT INTO "Employee" VALUES (28,'Karen','Morgan','karen.morgan@company.com','2022-09-26',4,14,'True',40);
INSERT INTO "Employee" VALUES (29,'Justin','Bell','justin.bell@company.com','2023-05-04',4,15,'False',37.5);
INSERT INTO "Job" VALUES (1,'Software Developer',1);
INSERT INTO "Job" VALUES (2,'Systems Administrator',1);
INSERT INTO "Job" VALUES (3,'IT Support Specialist',1);
INSERT INTO "Job" VALUES (4,'Financial Analyst',2);
INSERT INTO "Job" VALUES (5,'Accountant',2);
INSERT INTO "Job" VALUES (6,'Budget Officer',2);
INSERT INTO "Job" VALUES (7,'Operations Manager',5);
INSERT INTO "Job" VALUES (8,'Process Improvement Analyst',5);
INSERT INTO "Job" VALUES (9,'Supply Chain Coordinator',5);
INSERT INTO "Job" VALUES (10,'HR Generalist',3);
INSERT INTO "Job" VALUES (11,'Talent Acquisition Specialist',3);
INSERT INTO "Job" VALUES (12,'Training and Development Officer',3);
INSERT INTO "Job" VALUES (13,'Sales Executive',4);
INSERT INTO "Job" VALUES (14,'Account Manager',4);
INSERT INTO "Job" VALUES (15,'Business Development Representative',4);
INSERT INTO "Job" VALUES (105,'Data Quality Analyst',3);
INSERT INTO "Salary" VALUES (1,1,45000);
INSERT INTO "Salary" VALUES (2,2,45000);
INSERT INTO "Salary" VALUES (3,3,50000);
INSERT INTO "Salary" VALUES (4,4,50000);
INSERT INTO "Salary" VALUES (5,5,60000);
INSERT INTO "Salary" VALUES (6,6,55000);
INSERT INTO "Salary" VALUES (7,7,48000);
INSERT INTO "Salary" VALUES (8,8,48000);
INSERT INTO "Salary" VALUES (9,9,52000);
INSERT INTO "Salary" VALUES (10,10,52000);
INSERT INTO "Salary" VALUES (11,12,58000);
INSERT INTO "Salary" VALUES (12,13,78000);
INSERT INTO "Salary" VALUES (13,14,78000);
INSERT INTO "Salary" VALUES (14,15,46000);
INSERT INTO "Salary" VALUES (15,16,46000);
INSERT INTO "Salary" VALUES (16,17,54000);
INSERT INTO "Salary" VALUES (17,18,48000);
INSERT INTO "Salary" VALUES (18,19,44000);
INSERT INTO "Salary" VALUES (19,20,44000);
INSERT INTO "Salary" VALUES (20,21,47000);
INSERT INTO "Salary" VALUES (21,22,47000);
INSERT INTO "Salary" VALUES (22,23,50000);
INSERT INTO "Salary" VALUES (23,24,45000);
INSERT INTO "Salary" VALUES (24,25,42000);
INSERT INTO "Salary" VALUES (25,26,42000);
INSERT INTO "Salary" VALUES (26,27,75000);
INSERT INTO "Salary" VALUES (27,28,75000);
INSERT INTO "Salary" VALUES (28,29,45000);
INSERT INTO "Salary" VALUES (29,30,40000);
COMMIT;
