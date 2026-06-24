"""
VitalFlow Data Seeder - Islamabad & Rawalpindi Edition
Populates the database with real-time localized data for presentation.
"""
import random
from datetime import datetime, timedelta
from db_manager import get_db_connection
from logger_config import logger
from security import PasswordSecurity

# Real-world Hospital Data for Islamabad & Rawalpindi
HOSPITALS = [
    ("Capital General Hospital", "G-10/4, Islamabad", "051-9101000"),
    ("LifeCare Medical Center", "H-11, Islamabad", "051-9900112"),
    ("RiverView Hospital", "Committee Chowk, Rawalpindi", "051-5552211"),
    ("Metro Health Complex", "Murree Road, Rawalpindi", "051-4447788"),
    ("Crescent Military Hospital", "Saddar, Rawalpindi", "051-5176300"),
    ("NorthView International Hospital", "Golra Mor, Islamabad", "051-8459101"),
    ("Civic Polyclinic", "G-7/1, Islamabad", "051-9218305"),
    ("BlueLine Surgical Center", "Blue Area, Islamabad", "051-8447777"),
]

# Production Staff Seed
STAFF_SEED = [
    ("asad_admin", 1, 1),
    ("sana_admin", 1, 2),
    ("dr_abdullah", 2, 3),
    ("dr_afnan", 2, 4),
    ("dr_daniyal", 2, 5),
    ("nurse_hira", 2, 6),
    ("tech_waseem", 2, 7),
]

# Medical Inventory Catalog
INVENTORY_ITEMS = [
    ("Portable Ventilator", "Equipment", "Unit"),
    ("Oxygen Cylinder 40L", "Equipment", "Unit"),
    ("Surgical Mask N95", "Medical Supplies", "Box (50 units)"),
    ("Sterile Gloves", "Medical Supplies", "Box (100 pairs)"),
    ("ICU Monitor Pro", "Equipment", "Unit"),
    ("Defibrillator X2", "Equipment", "Unit"),
    ("IV Pump", "Equipment", "Unit"),
    ("Antibiotics - Amoxicillin", "Medications", "Box (100 tablets)"),
    ("Saline Solution 500ml", "IV Fluids", "Box (10 bottles)"),
    ("Syringe 10ml", "Medical Supplies", "Box (100 units)"),
]

# Localized Donor Names
DONOR_NAMES = [
    "Ahmed Hassan", "Fatima Khan", "Usman Ali", "Aisha Malik", "Hassan Raza",
    "Sara Bibi", "Bilal Ahmed", "Zainab Mirza", "Omar Farooq", "Hina Nawaz",
    "Karim Anwar", "Leila Rizvi", "Mustafa Qazi", "Nadia Hussain", "Qadir Khan",
    "Ibrahim Saeed", "Mariam Yousaf", "Saad Qureshi", "Noor Iqbal", "Rida Noor"
]

BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

def _exec(cursor, sql: str, params: tuple = None) -> None:
    """Helper to handle Postgres placeholder conversion."""
    cursor.execute(sql.replace("?", "%s"), params or ())

def seed_database() -> None:
    """Master function to populate localized production data."""
    connection = get_db_connection()
    if not connection:
        print("❌ Error: Could not connect to Supabase.")
        return

    try:
        cursor = connection.cursor()
        print("🚀 Initializing Live Seed for Islamabad/Rawalpindi...")
        
        # 1. Clean existing data
        tables = [
            "public.blood_donations_override",
            "public.blood_bank",
            "public.donation_records",
            "public.hospital_inventory",
            "public.transfer_status",
            "public.transfer_requests",
            "public.staff",
            "public.donors",
            "public.inventory_items",
            "public.hospitals",
            "public.roles",
        ]
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table} CASCADE")

        # 2. Seed Roles
        for role_name in ("System Administrator", "Medical Staff"):
            _exec(cursor, "INSERT INTO public.roles (role_name) VALUES (?)", (role_name,))
        
        # 3. Seed Hospitals
        for name, loc, contact in HOSPITALS:
            _exec(cursor, "INSERT INTO public.hospitals (name, location, contact) VALUES (?, ?, ?)", (name, loc, contact))

        # 4. Seed Staff (Shared Password for Presentation)
        hashed_pwd = PasswordSecurity.hash_password("SecurePass123!")
        for user, role, hosp in STAFF_SEED:
            _exec(cursor, "INSERT INTO public.staff (username, password, role_id, hospital_id, created_by) VALUES (?, ?, ?, ?, ?)", 
                  (user, hashed_pwd, role, hosp, "System_Init"))

        # 5. Seed Catalog & Inventory
        for name, cat, unit in INVENTORY_ITEMS:
            _exec(cursor, "INSERT INTO public.inventory_items (item_name, category, unit_type) VALUES (?, ?, ?)", (name, cat, unit))

        for h_id in range(1, len(HOSPITALS) + 1):
            for i_id in range(1, len(INVENTORY_ITEMS) + 1):
                qty = random.randint(5, 45)
                expiry = (datetime.now() + timedelta(days=random.randint(30, 365))).date().isoformat()
                _exec(cursor, "INSERT INTO public.hospital_inventory (hospital_id, item_id, quantity, expiry_date) VALUES (?, ?, ?, ?)",
                      (h_id, i_id, qty, expiry))

        # 6. Seed Donors & Historical Records
        for name in DONOR_NAMES:
            blood = random.choice(BLOOD_TYPES)
            contact = f"03{random.randint(10, 45)}-{random.randint(1000000, 9999999)}"
            # Randomize last donation: some eligible (>90 days), some not
            days_ago = random.choice([20, 45, 110, 150]) 
            last_date = (datetime.now() - timedelta(days=days_ago)).date().isoformat()
            
            _exec(cursor, "INSERT INTO public.donors (name, blood_type, contact, last_donation_date) VALUES (?, ?, ?, ?)", 
                  (name, blood, contact, last_date))

        # 7. Seed Blood Bank Units (Standard 42-day expiry)
        for h_id in range(1, len(HOSPITALS) + 1):
            for b_type in BLOOD_TYPES:
                qty = random.randint(300, 950)
                rec_date = datetime.now().date().isoformat()
                exp_date = (datetime.now() + timedelta(days=42)).date().isoformat()
                _exec(cursor, "INSERT INTO public.blood_bank (hospital_id, blood_type, quantity_ml, received_date, expiry_date, status) VALUES (?, ?, ?, ?, ?, 'Active')",
                      (h_id, b_type, qty, rec_date, exp_date))

        connection.commit()
        print("\n" + "="*50)
        print("✅ SUCCESS: Islamabad/Rawalpindi Network is Live!")
        print(f"📊 Facilities Seeded: {len(HOSPITALS)}")
        print(f"👥 Staff Authorized: {len(STAFF_SEED)}")
        print(f"🩸 Registered Donors: {len(DONOR_NAMES)}")
        print("="*50)
        print("\nSample credential: asad_admin / SecurePass123! (change after first login)")
        
    except Exception as e:
        connection.rollback()
        print(f"❌ Seed Error: {e}")
        logger.error(f"Database seeding failed: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    seed_database()
