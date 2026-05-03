import models
import random
from datetime import datetime, timedelta

print("🌱 Starting VitalFlow MASSIVE Data Seed Process (Twin Cities Edition)...")
admin_user = "System_Auto_Seed"

try:
    # ==========================================
    # 0. SEED ROLES (CRITICAL FIX FOR FOREIGN KEYS)
    # ==========================================
    models.add_role("System Administrator", admin_user) # Automatically gets Role_ID 1
    models.add_role("Medical Staff", admin_user)        # Automatically gets Role_ID 2
    print("✅ System Roles initialized.")

    # ==========================================
    # 1. SEED HOSPITALS (Islamabad & Rawalpindi Major Hubs)
    # ==========================================
    hospitals = [
        ("PIMS (Pakistan Institute of Medical Sciences)", "G-8/3, Islamabad", "051-9261170"),
        ("Shifa International Hospital", "H-8/4, Islamabad", "051-8463666"),
        ("Holy Family Hospital", "Satellite Town, Rawalpindi", "051-9290321"),
        ("Benazir Bhutto Hospital (BBH)", "Murree Road, Rawalpindi", "051-9290301"),
        ("CMH (Combined Military Hospital)", "Tamizuddin Rd, Rawalpindi", "051-5176412"),
        ("Quaid-e-Azam International Hospital", "Golra Mor, Islamabad", "051-8449100"),
        ("Polyclinic Hospital", "G-6/2, Islamabad", "051-9218300"),
        ("Kulsum International Hospital", "Blue Area, Islamabad", "051-8446666")
    ]
    for h_name, h_loc, h_contact in hospitals:
        models.add_hospital(h_name, h_loc, h_contact, admin_user)
    print(f"✅ {len(hospitals)} Major Twin City Hospitals added.")

    # ==========================================
    # 2. SEED STAFF (Your Group + Regional Medics)
    # ==========================================
    models.add_staff("asad_admin", "pass123", 1, 1, admin_user)  # Asad (Admin @ PIMS)
    models.add_staff("dr_abdullah", "pass123", 2, 2, admin_user) # Abdullah (Staff @ Shifa)
    models.add_staff("dr_afnan", "pass123", 2, 3, admin_user)    # Afnan (Staff @ Holy Family)
    models.add_staff("dr_daniyal", "pass123", 2, 1, admin_user)  # Daniyal (Staff @ PIMS)
    
    # Generate 20 random medics for other facilities
    first_names = ["Ali", "Ayesha", "Usman", "Fatima", "Hassan", "Zainab", "Omar", "Sara", "Bilal", "Sana"]
    for i in range(20):
        uname = f"dr_{random.choice(first_names).lower()}_{i}"
        models.add_staff(uname, "pass123", 2, random.randint(1, len(hospitals)), admin_user)
    print("✅ Project Team & 20 Regional Medical Staff registered.")

    # ==========================================
    # 3. SEED GLOBAL CATALOG
    # ==========================================
    items = [
        ("N95 Respirator Masks", "PPE", "Box of 50"),
        ("Surgical Gloves", "PPE", "Box of 100"),
        ("O- Blood (Universal)", "Blood", "500ml Bag"),
        ("A+ Blood", "Blood", "500ml Bag"),
        ("B+ Blood", "Blood", "500ml Bag"),
        ("Paracetamol 500mg", "Medicine", "Pack of 100"),
        ("Portable Ventilator", "Equipment", "Unit"),
        ("Defibrillator (AED)", "Equipment", "Unit"),
        ("IV Fluids (Saline)", "Consumables", "1L Bag")
    ]
    for i_name, i_cat, i_unit in items:
        models.add_item(i_name, i_cat, i_unit, admin_user)
    print("✅ Global Catalog populated.")

    # ==========================================
    # 4. SEED BLOOD DONORS (60+ Local Donors)
    # ==========================================
    last_names = ["Khan", "Ahmed", "Ali", "Tariq", "Malik", "Shah", "Chaudhry", "Raza", "Hussain", "Javed"]
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    for i in range(60):
        d_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        d_blood = random.choice(blood_types)
        d_contact = f"03{random.randint(0, 4)}{random.randint(1, 9)}-{random.randint(1000000, 9999999)}" 
        models.add_donor(d_name, d_blood, d_contact, admin_user)
    print("✅ 60 Regional Blood Donors registered.")

    # ==========================================
    # 5. SEED HOSPITAL WAREHOUSES (150+ Allocations)
    # ==========================================
    for _ in range(150):
        hosp_id = random.randint(1, len(hospitals))
        item_id = random.randint(1, len(items))
        qty = random.randint(10, 800)
        exp_date = (datetime.now() + timedelta(days=random.randint(365, 1800))).strftime('%Y-%m-%d')
        models.add_hospital_inventory(hosp_id, item_id, qty, exp_date, admin_user)
    print("✅ 150 Regional Stock Allocations completed.")

    # ==========================================
    # 6. SEED DONATION LOGS (120+ Records)
    # ==========================================
    for _ in range(120):
        donor_id = random.randint(1, 60)
        hosp_id = random.randint(1, len(hospitals))
        amount = random.choice([250, 450, 500])
        don_date = (datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d')
        models.add_donation_record(donor_id, hosp_id, don_date, amount, admin_user)
    print("✅ 120 Historical Blood Drive records logged.")

  # ==========================================
    # 7. SEED LOGISTICS & TRANSFERS (100+ Shipments)
    # ==========================================
    successful_transfers = 0
    for req_id in range(1, 101):
        origin = random.randint(1, len(hospitals))
        dest = random.randint(1, len(hospitals))
        while origin == dest: dest = random.randint(1, len(hospitals))
        
        item_id = random.randint(1, len(items))
        qty = random.randint(5, 150)
        
        try:
            # Attempt to create and process the random transfer
            models.create_transfer_request(origin, dest, item_id, qty, admin_user)
            models.add_transfer_status(req_id, "Pending", admin_user)
            
            if random.random() > 0.3:
                models.add_transfer_status(req_id, "In Transit", admin_user)
                if random.random() > 0.4:
                    # This is the step that might trigger your strict security rules!
                    models.add_transfer_status(req_id, "Delivered", admin_user)
            
            successful_transfers += 1
        except Exception:
            # If your strict DB rules block the random transfer (e.g., Insufficient Stock), 
            # the script simply ignores it and moves to the next random generation.
            pass

    print(f"\n🚀 TWIN CITIES SEED COMPLETE!")
    print(f"Total Hospitals: {len(hospitals)}")
    print(f"Total Logistics Operations: {successful_transfers} valid requests generated.")

except Exception as e:
    print(f"\n❌ ERROR: {e}")