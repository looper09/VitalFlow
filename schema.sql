-- ==========================================
-- VITALFLOW: MASTER DATABASE SCHEMA
-- ==========================================

-- 1. Roles
CREATE TABLE IF NOT EXISTS public.roles (
    Role_ID SERIAL PRIMARY KEY,
    Role_Name TEXT NOT NULL
);

-- 2. Hospitals
CREATE TABLE IF NOT EXISTS public.hospitals (
    Hospital_ID SERIAL PRIMARY KEY,
    Name TEXT NOT NULL,
    Location TEXT NOT NULL,
    Contact TEXT NOT NULL
);

-- 3. Staff
CREATE TABLE IF NOT EXISTS public.staff (
    Staff_ID SERIAL PRIMARY KEY,
    Username TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL,
    Role_ID INTEGER NOT NULL,
    Hospital_ID INTEGER,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Created_By TEXT,
    CONSTRAINT fk_staff_role FOREIGN KEY (Role_ID) REFERENCES public.roles(Role_ID) ON DELETE CASCADE,
    CONSTRAINT fk_staff_hospital FOREIGN KEY (Hospital_ID) REFERENCES public.hospitals(Hospital_ID) ON DELETE SET NULL
);

-- 4. Inventory Items
CREATE TABLE IF NOT EXISTS public.inventory_items (
    Item_ID SERIAL PRIMARY KEY,
    Item_Name TEXT NOT NULL,
    Category TEXT NOT NULL,
    Unit_Type TEXT NOT NULL
);

-- 5. Hospital Inventory
CREATE TABLE IF NOT EXISTS public.hospital_inventory (
    Inventory_ID SERIAL PRIMARY KEY,
    Hospital_ID INTEGER NOT NULL,
    Item_ID INTEGER NOT NULL,
    Quantity INTEGER NOT NULL CHECK (Quantity >= 0),
    Expiry_Date DATE,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_inv_hosp FOREIGN KEY (Hospital_ID) REFERENCES public.hospitals(Hospital_ID) ON DELETE CASCADE,
    CONSTRAINT fk_inv_item FOREIGN KEY (Item_ID) REFERENCES public.inventory_items(Item_ID) ON DELETE CASCADE
);

-- 6. Donors
CREATE TABLE IF NOT EXISTS public.donors (
    Donor_ID SERIAL PRIMARY KEY,
    Name TEXT NOT NULL,
    Blood_Type TEXT NOT NULL CHECK(Blood_Type IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    Contact TEXT NOT NULL,
    last_donation_date DATE DEFAULT NULL
);

-- 7. Blood Bank
CREATE TABLE IF NOT EXISTS public.blood_bank (
    blood_id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL,
    blood_type TEXT NOT NULL CHECK(blood_type IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    quantity_ml INTEGER NOT NULL CHECK(quantity_ml >= 0),
    received_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Expired', 'Used')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_blood_hosp FOREIGN KEY (hospital_id) REFERENCES public.hospitals(Hospital_ID) ON DELETE CASCADE
);

-- 8. Blood Donation Overrides
CREATE TABLE IF NOT EXISTS public.blood_donations_override (
    override_id SERIAL PRIMARY KEY,
    donor_id INTEGER NOT NULL,
    staff_id INTEGER NOT NULL,
    override_reason TEXT NOT NULL,
    override_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_override_donor FOREIGN KEY (donor_id) REFERENCES public.donors(Donor_ID) ON DELETE CASCADE,
    CONSTRAINT fk_override_staff FOREIGN KEY (staff_id) REFERENCES public.staff(Staff_ID) ON DELETE CASCADE
);

-- 9. Donation Records
CREATE TABLE IF NOT EXISTS public.donation_records (
    Donation_ID SERIAL PRIMARY KEY,
    Donor_ID INTEGER NOT NULL,
    Hospital_ID INTEGER NOT NULL,
    Date DATE NOT NULL,
    Amount INTEGER NOT NULL CHECK (Amount > 0),
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_don_donor FOREIGN KEY (Donor_ID) REFERENCES public.donors(Donor_ID) ON DELETE CASCADE,
    CONSTRAINT fk_don_hosp FOREIGN KEY (Hospital_ID) REFERENCES public.hospitals(Hospital_ID) ON DELETE CASCADE
);

-- 10. Transfer Requests
CREATE TABLE IF NOT EXISTS public.transfer_requests (
    Request_ID SERIAL PRIMARY KEY,
    Origin_Hospital_ID INTEGER NOT NULL,
    Dest_Hospital_ID INTEGER NOT NULL,
    Item_ID INTEGER NOT NULL,
    Quantity INTEGER NOT NULL CHECK (Quantity > 0),
    CHECK (Origin_Hospital_ID != Dest_Hospital_ID),
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_trans_origin FOREIGN KEY (Origin_Hospital_ID) REFERENCES public.hospitals(Hospital_ID) ON DELETE CASCADE,
    CONSTRAINT fk_trans_dest FOREIGN KEY (Dest_Hospital_ID) REFERENCES public.hospitals(Hospital_ID) ON DELETE CASCADE,
    CONSTRAINT fk_trans_item FOREIGN KEY (Item_ID) REFERENCES public.inventory_items(Item_ID) ON DELETE CASCADE
);

-- 11. Transfer Status History
CREATE TABLE IF NOT EXISTS public.transfer_status (
    Status_ID SERIAL PRIMARY KEY,
    Request_ID INTEGER,
    Status TEXT NOT NULL CHECK(Status IN ('Pending', 'In Transit', 'Delivered', 'Cancelled')),
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_stat_req FOREIGN KEY (Request_ID) REFERENCES public.transfer_requests(Request_ID) ON DELETE CASCADE
);

-- 12. System Audit Logs
CREATE TABLE IF NOT EXISTS public.audit_logs (
    Log_ID SERIAL PRIMARY KEY,
    Staff_ID INTEGER, 
    Action TEXT NOT NULL,
    Table_Affected TEXT,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_staff FOREIGN KEY (Staff_ID) REFERENCES public.staff(Staff_ID) ON DELETE SET NULL
);

-- PERFORMANCE INDEXES
CREATE INDEX IF NOT EXISTS idx_staff_username ON public.staff(Username);
CREATE INDEX IF NOT EXISTS idx_staff_hospital ON public.staff(Hospital_ID);
CREATE INDEX IF NOT EXISTS idx_audit_time ON public.audit_logs(Timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_staff ON public.audit_logs(Staff_ID);
CREATE INDEX IF NOT EXISTS idx_hosp_inventory ON public.hospital_inventory(Hospital_ID, Item_ID);
CREATE INDEX IF NOT EXISTS idx_blood_hospital ON public.blood_bank(hospital_id);
CREATE INDEX IF NOT EXISTS idx_blood_type ON public.blood_bank(blood_type);
CREATE INDEX IF NOT EXISTS idx_blood_status_expiry ON public.blood_bank(status, expiry_date);
CREATE INDEX IF NOT EXISTS idx_blood_hosp_type_status ON public.blood_bank(hospital_id, blood_type, status);
CREATE INDEX IF NOT EXISTS idx_donor_last_donation ON public.donors(last_donation_date);
CREATE INDEX IF NOT EXISTS idx_donation_date ON public.donation_records(Date);