import mysql.connector

# --- Update these if needed ---
DB_NAME = "Imhotep"
HOST = "localhost"
USER = "root"        # change if needed
PASSWORD = ""        # set your root password if you have one
# ------------------------------

conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD)
conn.autocommit = True  # convenient for CREATE DATABASE
cur = conn.cursor()

# 1) Create database (if not exists)
cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4;")
cur.execute(f"USE `{DB_NAME}`;")

# Helper to run multiple statements cleanly
def run(sql, label=None):
    if label:
        print(f"--- {label} ---")
    for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
        cur.execute(stmt + ";")

# 2) Create tables in dependency-friendly order
# Note: backticks used because names like User can collide with keywords.

# A) User
run("""
CREATE TABLE IF NOT EXISTS `User` (
  `User_ID` INT PRIMARY KEY,
  `User_Name` VARCHAR(100) NOT NULL,
  `Password` VARCHAR(100) NOT NULL
) ENGINE=InnoDB
""", "Create `User`")

# B) Patient_Portal (create column Pr_ID now, add FK later to avoid cycle)
run("""
CREATE TABLE IF NOT EXISTS `Patient_Portal` (
  `Patient_ID` INT PRIMARY KEY,
  `User_ID` INT NOT NULL,
  `User_Name` VARCHAR(100) NOT NULL,
  `Doctor_sugg` TEXT,
  `Pr_ID` INT NULL,
  INDEX `idx_pp_user_id` (`User_ID`),
  INDEX `idx_pp_pr_id` (`Pr_ID`),
  CONSTRAINT `fk_pp_user` FOREIGN KEY (`User_ID`) REFERENCES `User`(`User_ID`)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB
""", "Create `Patient_Portal`")

# C) Prescription (references Patient_Portal)
run("""
CREATE TABLE IF NOT EXISTS `Prescription` (
  `Pr_ID` INT PRIMARY KEY,
  `Patient_ID` INT NOT NULL,
  `Doctor_Sugg` TEXT,
  `Prescription` TEXT,
  `Visit_Date` DATE,
  `Dispense` TINYINT DEFAULT 1,  -- 1 = active, 0 = dispensed
  INDEX `idx_presc_patient_id` (`Patient_ID`),
  CONSTRAINT `fk_presc_patient` FOREIGN KEY (`Patient_ID`) REFERENCES `Patient_Portal`(`Patient_ID`)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB
""", "Create `Prescription`")

# D) Doctor_Portal
run("""
CREATE TABLE IF NOT EXISTS `Doctor_Portal` (
  `User_ID` INT NOT NULL,
  `Doctor_ID` INT PRIMARY KEY,
  `Patient_ID` INT NOT NULL,
  `Doctor_Name` VARCHAR(100) NOT NULL,
  `Pr_ID` INT NULL,
  INDEX `idx_dp_user_id` (`User_ID`),
  INDEX `idx_dp_patient_id` (`Patient_ID`),
  INDEX `idx_dp_pr_id` (`Pr_ID`),
  CONSTRAINT `fk_dp_user` FOREIGN KEY (`User_ID`) REFERENCES `User`(`User_ID`)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT `fk_dp_patient` FOREIGN KEY (`Patient_ID`) REFERENCES `Patient_Portal`(`Patient_ID`)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT `fk_dp_pr` FOREIGN KEY (`Pr_ID`) REFERENCES `Prescription`(`Pr_ID`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB
""", "Create `Doctor_Portal`")

# E) Pharmacist_Portal
run("""
CREATE TABLE IF NOT EXISTS `Pharmacist_Portal` (
  `User_ID` INT NOT NULL,
  `User_Name` VARCHAR(100) NOT NULL,
  `Pharma_ID` INT PRIMARY KEY,
  `Patient_UID` INT NOT NULL,
  `Pr_ID` INT NULL,
  INDEX `idx_ph_user_id` (`User_ID`),
  INDEX `idx_ph_patient_uid` (`Patient_UID`),
  INDEX `idx_ph_pr_id` (`Pr_ID`),
  CONSTRAINT `fk_ph_user` FOREIGN KEY (`User_ID`) REFERENCES `User`(`User_ID`)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT `fk_ph_patient` FOREIGN KEY (`Patient_UID`) REFERENCES `Patient_Portal`(`Patient_ID`)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT `fk_ph_pr` FOREIGN KEY (`Pr_ID`) REFERENCES `Prescription`(`Pr_ID`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB
""", "Create `Pharmacist_Portal`")

# 3) Close the cycle: add FK Patient_Portal.Pr_ID -> Prescription.Pr_ID
# Only add if it doesn't already exist.
cur.execute("""
SELECT CONSTRAINT_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA=%s AND TABLE_NAME='Patient_Portal' AND COLUMN_NAME='Pr_ID' AND REFERENCED_TABLE_NAME='Prescription'
""", (DB_NAME,))
exists = cur.fetchone()

if not exists:
    run("""
    ALTER TABLE `Patient_Portal`
      ADD CONSTRAINT `fk_pp_pr`
      FOREIGN KEY (`Pr_ID`) REFERENCES `Prescription`(`Pr_ID`)
      ON UPDATE CASCADE ON DELETE SET NULL
    """, "Add FK `Patient_Portal`.`Pr_ID` → `Prescription`.`Pr_ID`")
else:
    print("--- FK `Patient_Portal`.`Pr_ID` already present ---")

print("\nSchema created/verified successfully.")

# (Optional) quick sanity read
for t in ["User", "Patient_Portal", "Prescription", "Doctor_Portal", "Pharmacist_Portal"]:
    cur.execute(f"SELECT COUNT(*) FROM `{t}`;")
    print(f"{t}: {cur.fetchone()[0]} rows")

cur.close()
conn.close()
