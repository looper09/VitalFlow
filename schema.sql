"-- ==========================================
-- VITALFLOW: MASTER DATABASE SCHEMA
-- ==========================================

-- 1. Roles
CREATE TABLE IF NOT EXISTS Roles (
    Role_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Role_Name TEXT NOT NULL
);

-- 2. Hospitals
CREATE TABLE IF NOT EXISTS Hospitals (
    Hospital_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Location TEXT NOT NULL,
    Contact TEXT NOT NULL
);

-- 3. Staff (Users)
CREATE TABLE IF NOT EXISTS Staff (
    Staff_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL,
    Role_ID INTEGER,
    Hospital_ID INTEGER,
    FOREIGN KEY (Role_ID) REFERENCES Roles(Role_ID),
    FOREIGN KEY (Hospital_ID) REFERENCES Hospitals(Hospital_ID)
);

-- 4. Inventory Items (Global Catalog)
CREATE TABLE IF NOT EXISTS Inventory_Items (
    Item_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Item_Name TEXT NOT NULL,
    Category TEXT NOT NULL,
    Unit_Type TEXT NOT NULL
);

-- 5. Hospital Inventory (Physical Stock)
CREATE TABLE IF NOT EXISTS Hospital_Inventory (
    Inventory_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Hospital_ID INTEGER,
    Item_ID INTEGER,
    Quantity INTEGER NOT NULL CHECK (Quantity >= 0), -- 🚨 ENFORCED INTEGRITY: Prevents negative stock
    Expiry_Date DATE,
    FOREIGN KEY (Hospital_ID) REFERENCES Hospitals(Hospital_ID),
    FOREIGN KEY (Item_ID) REFERENCES Inventory_Items(Item_ID)
);

-- 6. Donors
CREATE TABLE IF NOT EXISTS Donors (
    Donor_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Blood_Type TEXT NOT NULL CHECK(Blood_Type IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')), -- 🚨 ENFORCED INTEGRITY: Standardizes medical inputs
    Contact TEXT NOT NULL
);

-- 7. Donation Records
CREATE TABLE IF NOT EXISTS Donation_Records (
    Donation_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Donor_ID INTEGER,
    Hospital_ID INTEGER,
    Date DATE NOT NULL,
    Amount INTEGER NOT NULL CHECK (Amount > 0), -- 🚨 ENFORCED INTEGRITY: Prevents 0ml or negative donations
    FOREIGN KEY (Donor_ID) REFERENCES Donors(Donor_ID),
    FOREIGN KEY (Hospital_ID) REFERENCES Hospitals(Hospital_ID)
);

-- 8. Transfer Requests
CREATE TABLE IF NOT EXISTS Transfer_Requests (
    Request_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Origin_Hospital_ID INTEGER,
    Dest_Hospital_ID INTEGER,
    Item_ID INTEGER,
    Quantity INTEGER NOT NULL CHECK (Quantity > 0),
    CHECK (Origin_Hospital_ID != Dest_Hospital_ID), -- 🚨 ENFORCED INTEGRITY: A hospital cannot transfer to itself
    FOREIGN KEY (Origin_Hospital_ID) REFERENCES Hospitals(Hospital_ID),
    FOREIGN KEY (Dest_Hospital_ID) REFERENCES Hospitals(Hospital_ID),
    FOREIGN KEY (Item_ID) REFERENCES Inventory_Items(Item_ID)
);

-- 9. Transfer Status History
CREATE TABLE IF NOT EXISTS Transfer_Status (
    Status_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Request_ID INTEGER,
    Status TEXT NOT NULL CHECK(Status IN ('Pending', 'In Transit', 'Delivered', 'Cancelled')), -- 🚨 ENFORCED INTEGRITY: Strict logistics tracking
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Request_ID) REFERENCES Transfer_Requests(Request_ID) ON DELETE CASCADE
);

-- 10. System Audit Logs
CREATE TABLE IF NOT EXISTS Audit_Logs (
    Log_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Staff_ID TEXT, 
    Action TEXT NOT NULL,
    Table_Affected TEXT,
    Timestamp DATETIME DEFAULT (datetime('now', 'localtime'))
);

-- ==========================================
-- QUERY OPTIMIZATION: PERFORMANCE INDEXES
-- ==========================================

-- Speeds up the "Deep Audit Trail" report sorting by time
CREATE INDEX IF NOT EXISTS idx_audit_time ON Audit_Logs(Timestamp);

-- Speeds up Logistics Impact & Full Transfer History reports
CREATE INDEX IF NOT EXISTS idx_transfer_req ON Transfer_Status(Request_ID);
CREATE INDEX IF NOT EXISTS idx_transfer_status ON Transfer_Status(Status);

-- Speeds up Hospital Inventory lookups & Blood Bank Summaries
CREATE INDEX IF NOT EXISTS idx_hosp_inventory ON Hospital_Inventory(Hospital_ID, Item_ID);
CREATE INDEX IF NOT EXISTS idx_donation_hosp ON Donation_Records(Hospital_ID);"