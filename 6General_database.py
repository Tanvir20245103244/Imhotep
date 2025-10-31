import mysql.connector

# === Connection details ===
DB_NAME = "imhotep"
HOST = "localhost"
USER = "root"         # change if needed
PASSWORD = ""         # your MySQL root password (if any)
# ===========================

# Connect to MySQL
conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD)
conn.autocommit = True
cur = conn.cursor()

# 1) Create Database
cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4;")
cur.execute(f"USE `{DB_NAME}`;")

# Helper function to execute table creation
def create_table(label, sql):
    print(f"--- Creating {label} ---")
    cur.execute(sql)

# 2) Create Tables (independent, no foreign keys)

# A) User table
create_table("User", """
CREATE TABLE IF NOT EXISTS `User` (
  `User_ID` INT PRIMARY KEY,
  `User_Name` VARCHAR(100) NOT NULL,
  `Password` VARCHAR(100) NOT NULL
) ENGINE=InnoDB;
""")

# B) Patient_Portal table
create_table("Patient_Portal", """
CREATE TABLE IF NOT EXISTS `Patient_Portal` (
  `Patient_ID` INT PRIMARY KEY,
  `User_ID` INT,
  `User_Name` VARCHAR(100),
  `Doctor_sugg` TEXT,
  `Pr_ID` INT
) ENGINE=InnoDB;
""")

# C) Prescription table
create_table("Prescription", """
CREATE TABLE IF NOT EXISTS `Prescription` (
  `Pr_ID` INT PRIMARY KEY,
  `Patient_ID` INT,
  `Doctor_Sugg` TEXT,
  `Prescription` TEXT,
  `Visit_Date` DATE,
  `Dispense` TINYINT DEFAULT 1 COMMENT '1 = active, 0 = dispensed'
) ENGINE=InnoDB;
""")

# D) Doctor_Portal table
create_table("Doctor_Portal", """
CREATE TABLE IF NOT EXISTS `Doctor_Portal` (
  `User_ID` INT,
  `Doctor_ID` INT PRIMARY KEY,
  `Patient_ID` INT,
  `Doctor_Name` VARCHAR(100),
  `Pr_ID` INT
) ENGINE=InnoDB;
""")

# E) Pharmacist_Portal table
create_table("Pharmacist_Portal", """
CREATE TABLE IF NOT EXISTS `Pharmacist_Portal` (
  `User_ID` INT,
  `Pharma_ID` INT PRIMARY KEY,
  `Patient_UID` INT,
  `Pr_ID` INT
) ENGINE=InnoDB;
""")

print("\n✅ Database and tables created successfully!")

# Close connection
cur.close()
conn.close()
