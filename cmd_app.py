import models
import os
import datetime

# ==========================================
# UI HELPERS & INPUT VALIDATION ENGINE
# ==========================================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nPress Enter to return...")

def get_int_input(prompt):
    """Forces the user to enter a valid positive integer."""
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("❌ Value cannot be negative. Try again.")
                continue
            return value
        except ValueError:
            print("❌ Invalid input. Please enter numbers only.")

def get_string_input(prompt, allow_empty=False):
    """Forces the user to enter text. Allows empty if specified (for updates)."""
    while True:
        value = input(prompt).strip()
        if value == "" and not allow_empty:
            print("❌ Input cannot be empty. Try again.")
        else:
            return value

def get_date_input(prompt):
    """Forces the user to enter a strictly formatted date."""
    while True:
        date_str = input(prompt + " (YYYY-MM-DD): ").strip()
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            print("❌ Invalid format. Please use exactly YYYY-MM-DD.")

def print_hospital_choices():
    print("\n--- Available Hospitals ---")
    hospitals = models.get_all_hospitals()
    if hospitals:
        for h in hospitals: print(f"[{h[0]}] {h[1]} ({h[2]})")
    else: print("No hospitals found.")

def print_item_choices():
    print("\n--- Available Catalog Items ---")
    items = models.get_all_items()
    if items:
        for i in items: print(f"[{i[0]}] {i[1]} ({i[2]})")
    else: print("No items found.")

def print_donor_choices():
    print("\n--- Registered Donors ---")
    donors = models.get_all_donors()
    if donors:
        for d in donors: print(f"[{d[0]}] {d[1]} (Blood: {d[2]})")
    else: print("No donors found.")

# ==========================================
# 1. HOSPITAL MANAGEMENT (ADMIN)
# ==========================================
def manage_hospitals(username):
    while True:
        clear_screen()
        print("="*35 + "\n 🏥 HOSPITAL MANAGEMENT \n" + "="*35)
        print("1. View Directory\n2. Add Hospital\n3. Update Hospital\n4. Delete Hospital\n5. Back")
        choice = input("\nEnter choice (1-5): ")
        
        if choice == '1':
            clear_screen(); print("--- REGISTERED HOSPITALS ---\n")
            for h in models.get_all_hospitals(): print(f"[{h[0]}] {h[1]} | {h[2]} | {h[3]}")
            pause()
        elif choice == '2':
            clear_screen()
            name = get_string_input("Name: ")
            loc = get_string_input("Location: ")
            contact = get_string_input("Contact Number: ")
            models.add_hospital(name, loc, contact, username)
            print(f"\n✅ {name} added!")
            pause()
        elif choice == '3':
            clear_screen()
            print_hospital_choices()
            h_id = get_int_input("\nEnter Hospital ID to update: ")
            print("(Leave fields blank to keep existing data)")
            name = get_string_input("New Name: ", allow_empty=True)
            loc = get_string_input("New Location: ", allow_empty=True)
            contact = get_string_input("New Contact: ", allow_empty=True)
            models.update_hospital(h_id, name, loc, contact, username)
            print("\n✅ Hospital updated!")
            pause()
        elif choice == '4':
            clear_screen()
            print_hospital_choices()
            h_id = get_int_input("\nEnter Hospital ID to delete: ")
            confirm = input("Confirm permanent deletion? (y/n): ")
            if confirm.lower() == 'y':
                models.delete_hospital(h_id, username)
                print(f"\n🗑️ Hospital ID {h_id} deleted.")
            pause()
        elif choice == '5': break

# ==========================================
# 2. INVENTORY & STOCK MANAGEMENT (ADMIN)
# ==========================================
def manage_inventory(username):
    while True:
        clear_screen()
        print("="*35 + "\n 📦 INVENTORY MANAGEMENT \n" + "="*35)
        print("1. View Global Catalog\n2. Add Catalog Item\n3. View Specific Hospital Stock")
        print("4. Allocate Stock\n5. Log Medical Usage (Dispense)\n6. Back")
        choice = input("\nEnter choice (1-6): ")
        
        if choice == '1':
            clear_screen(); print_item_choices(); pause()
        elif choice == '2':
            clear_screen()
            name = get_string_input("Item Name (e.g., O- Blood): ")
            cat = get_string_input("Category (e.g., Blood, PPE): ")
            unit = get_string_input("Unit Type (e.g., Bags, Boxes): ")
            models.add_item(name, cat, unit, username)
            print(f"\n✅ {name} added to catalog!")
            pause()
        elif choice == '3':
            clear_screen()
            print_hospital_choices()
            h_id = get_int_input("\nEnter Hospital ID to view stock: ")
            stock = models.get_inventory_by_hospital(h_id)
            print(f"\n--- STOCK FOR HOSPITAL {h_id} ---\n")
            if not stock: print("No stock found.")
            for s in stock: print(f"Inv ID (Barcode): {s[0]} | Item ID: {s[2]} | Qty: {s[3]} | Exp: {s[4]}")
            pause()
        elif choice == '4':
            clear_screen()
            print_hospital_choices()
            h_id = get_int_input("\nTarget Hospital ID: ")
            print_item_choices()
            i_id = get_int_input("\nItem ID to Allocate: ")
            qty = get_int_input("Quantity: ")
            exp = get_date_input("Expiry Date")
            models.add_hospital_inventory(h_id, i_id, qty, exp, username)
            print("\n✅ Stock Allocated!")
            pause()
        elif choice == '5':
            clear_screen()
            print("--- LOG MEDICAL USAGE ---")
            inv_id = get_int_input("Inventory ID (Barcode): ")
            qty = get_int_input("Quantity Used: ")
            models.consume_hospital_inventory(inv_id, qty, username)
            print("\n✅ Usage Logged!")
            pause()
        elif choice == '6': break

# ==========================================
# 3. DONOR MANAGEMENT (ADMIN)
# ==========================================
def manage_donors(username):
    while True:
        clear_screen()
        print("="*35 + "\n 🩸 DONOR MANAGEMENT \n" + "="*35)
        print("1. View Donors\n2. Register Donor\n3. Log Donation\n4. Update/Fix Donation Amount\n5. Back")
        choice = input("\nEnter choice (1-5): ")
        
        if choice == '1':
            clear_screen(); print_donor_choices(); pause()
        elif choice == '2':
            clear_screen()
            name = get_string_input("Donor Name: ")
            blood = get_string_input("Blood Type (e.g., O-, A+): ")
            contact = get_string_input("Contact Number: ")
            models.add_donor(name, blood, contact, username)
            print(f"\n✅ Donor {name} registered!")
            pause()
        elif choice == '3':
            clear_screen()
            print_donor_choices()
            d_id = get_int_input("\nDonor ID: ")
            print_hospital_choices()
            h_id = get_int_input("\nHospital ID receiving donation: ")
            date = get_date_input("Donation Date")
            amt = get_int_input("Amount (ml): ")
            models.add_donation_record(d_id, h_id, date, amt, username)
            print("\n✅ Donation logged!")
            pause()
        elif choice == '4':
            clear_screen()
            dons = models.get_all_donations()
            for d in dons: print(f"Log ID [{d[0]}] | Donor ID: {d[1]} | Hosp ID: {d[2]} | Amount: {d[4]}ml")
            log_id = get_int_input("\nEnter Log ID to fix: ")
            new_amt = get_int_input("Corrected Amount (ml): ")
            models.update_donation_amount(log_id, new_amt, username)
            print("\n✅ Donation amount updated!")
            pause()
        elif choice == '5': break

# ==========================================
# 4. TRANSFER MANAGEMENT (ADMIN)
# ==========================================
def manage_transfers(username):
    while True:
        clear_screen()
        print("="*35 + "\n 🚑 RESOURCE TRANSFERS \n" + "="*35)
        print("1. View Active Requests\n2. Create Request\n3. Update Logistics Status\n4. Cancel Request\n5. Back")
        choice = input("\nEnter choice (1-5): ")
        
        if choice == '1':
            clear_screen(); print("--- TRANSFER REQUESTS ---\n")
            for r in models.get_all_transfer_requests(): 
                print(f"Req [{r[0]}] | Hosp {r[1]} -> Hosp {r[2]} | Item: {r[3]} | Qty: {r[4]}")
            pause()
        elif choice == '2':
            clear_screen()
            print_hospital_choices()
            orig = get_int_input("\nOrigin Hospital ID (Sender): ")
            dest = get_int_input("Destination Hospital ID (Receiver): ")
            print_item_choices()
            item = get_int_input("\nItem ID to transfer: ")
            qty = get_int_input("Quantity: ")
            models.create_transfer_request(orig, dest, item, qty, username)
            print("\n✅ Request created!")
            pause()
        elif choice == '3':
            clear_screen()
            for r in models.get_all_transfer_requests(): 
                print(f"Req [{r[0]}] | Hosp {r[1]} -> Hosp {r[2]} | Qty: {r[4]}")
            r_id = get_int_input("\nRequest ID to update: ")
            print("Statuses: Pending, In Transit, Delivered, Cancelled")
            status = get_string_input("New Status: ")
            models.add_transfer_status(r_id, status, username)
            print("\n✅ Status updated!")
            pause()
        elif choice == '4':
            clear_screen()
            r_id = get_int_input("\nRequest ID to delete/cancel: ")
            confirm = input("Confirm permanent deletion? (y/n): ")
            if confirm.lower() == 'y':
                models.delete_transfer_request(r_id, username)
                print("\n🗑️ Request Deleted!")
            pause()
        elif choice == '5': break

# ==========================================
# 5. STAFF & SYSTEM ADMIN (ADMIN)
# ==========================================
def manage_staff(username):
    while True:
        clear_screen()
        print("="*35 + "\n 🔐 STAFF & SYSTEM ADMIN \n" + "="*35)
        print("1. View Staff Roster\n2. Authorize Employee\n3. Revoke Access\n4. View Security Audit Logs\n5. Back")
        choice = input("\nEnter choice (1-5): ")
        
        if choice == '1':
            clear_screen(); print("--- STAFF ROSTER ---\n")
            for s in models.get_all_staff(): print(f"[{s[0]}] User: {s[1]} | Role: {s[3]} | Hosp ID: {s[4]}")
            pause()
        elif choice == '2':
            clear_screen(); print("--- AUTHORIZE NEW EMPLOYEE ---")
            user = get_string_input("New Username: ")
            pwd = get_string_input("Password: ")
            print("Role IDs: [1] Admin, [2] Staff")
            role = get_int_input("Role ID: ")
            print_hospital_choices()
            hosp = get_int_input("\nHospital ID assigned to: ")
            models.add_staff(user, pwd, role, hosp, username)
            print(f"\n✅ Employee '{user}' authorized!")
            pause()
        elif choice == '3':
            clear_screen()
            target_id = get_int_input("Enter Staff ID to revoke: ")
            confirm = input("Confirm revocation? (y/n): ")
            if confirm.lower() == 'y':
                models.delete_staff(target_id, username)
                print("\n🗑️ Access Revoked!")
            pause()
        elif choice == '4':
            clear_screen(); print("--- SECURITY AUDIT LOGS ---\n")
            logs = models.get_all_logs()
            if not logs: print("No logs found.")
            for l in logs: print(f"Log [{l[0]}] | User: {l[1]} | Action: {l[2]} | Table: {l[3]} | Time: {l[4]}")
            pause()
        elif choice == '5': break

# ==========================================
# 6. ADVANCED REPORTS (ADMIN)
# ==========================================
def view_advanced_reports():
    while True:
        clear_screen()
        print("="*35 + "\n 📈 ADVANCED SQL REPORTS \n" + "="*35)
        print("1. Personnel Roster JOIN\n2. Comprehensive Inventory JOIN\n3. Blood Drive Metrics JOIN")
        print("4. Deep Audit Trail JOIN\n5. Blood Bank Aggregate Summary\n6. Logistics Impact Aggregate\n7. Back")
        choice = input("\nEnter choice (1-7): ")
        
        if choice == '1':
            clear_screen(); print("--- STAFF DIRECTORY (JOINS) ---\n")
            for r in models.get_staff_report(): print(f"ID:{r[0]} | User:{r[1]} | Role:{r[2]} | Facility:{r[3]}")
            pause()
        elif choice == '2':
            clear_screen(); print("--- COMPREHENSIVE STOCK (JOINS) ---\n")
            for r in models.get_inventory_report(): print(f"Barcode:{r[0]} | Hosp:{r[1]} | Item:{r[2]} | Qty:{r[4]}")
            pause()
        elif choice == '3':
            clear_screen(); print("--- BLOOD DRIVE METRICS (JOINS) ---\n")
            for r in models.get_donation_report(): print(f"Donor:{r[1]} | Blood:{r[2]} | Hosp:{r[3]} | {r[5]}ml")
            pause()
        elif choice == '4':
            clear_screen(); print("--- DEEP AUDIT TRAIL (JOINS) ---\n")
            for r in models.get_deep_audit_report(): print(f"Time:{r[1]} | User:{r[2]} | Role:{r[3]} | Action:{r[4]}")
            pause()
        elif choice == '5':
            clear_screen(); print("--- BLOOD BANK SUMMARY (AGGREGATE) ---\n")
            for r in models.get_blood_bank_summary(): print(f"Hosp:{r[0]} | Blood:{r[1]} | Total Donors:{r[2]} | Total ml:{r[3]}")
            pause()
        elif choice == '6':
            clear_screen(); print("--- LOGISTICS IMPACT (AGGREGATE) ---\n")
            for r in models.get_logistics_impact(): print(f"Supplier:{r[0]} | Cat:{r[1]} | Total Items Shipped:{r[2]} | Shipments:{r[3]}")
            pause()
        elif choice == '7': break

# ==========================================
# ROLE-BASED DASHBOARDS
# ==========================================
def admin_dashboard(username):
    while True:
        clear_screen()
        print("="*45)
        print(f" 👑 COMMAND CENTER (ADMIN) | User: {username}")
        print("="*45)
        print("1. Hospitals\n2. Inventory & Stock\n3. Donors")
        print("4. Transfers\n5. Staff & Security\n6. Advanced Analytics\n7. Logout")
        print("="*45)
        
        choice = input("\nEnter choice (1-7): ")
        if choice == '1': manage_hospitals(username)
        elif choice == '2': manage_inventory(username)
        elif choice == '3': manage_donors(username)
        elif choice == '4': manage_transfers(username)
        elif choice == '5': manage_staff(username)
        elif choice == '6': view_advanced_reports()
        elif choice == '7': break
        else:
            print("❌ Invalid choice."); pause()

def staff_dashboard(username, hosp_id):
    while True:
        clear_screen()
        print("="*45)
        print(f" 🩺 MEDICAL STAFF PORTAL | User: {username} | Hosp ID: {hosp_id}")
        print("="*45)
        print("1. View Global Catalog\n2. View Our Stock\n3. Log Medical Usage (Dispense)")
        print("4. View Donors\n5. Register Walk-In Donor\n6. Log Blood Donation")
        print("7. Request Emergency Transfer\n8. Logout")
        print("="*45)
        
        choice = input("\nEnter choice (1-8): ")
        
        if choice == '1':
            clear_screen(); print_item_choices(); pause()
        elif choice == '2':
            clear_screen(); stock = models.get_inventory_by_hospital(hosp_id)
            print(f"\n--- STOCK FOR HOSPITAL {hosp_id} ---\n")
            if not stock: print("No stock found.")
            for s in stock: print(f"Inv ID (Barcode): {s[0]} | Item: ID {s[2]} | Qty: {s[3]}")
            pause()
        elif choice == '3':
            clear_screen()
            inv_id = get_int_input("Inventory ID (Barcode) used: ")
            qty = get_int_input("Quantity used: ")
            models.consume_hospital_inventory(inv_id, qty, username)
            print("\n✅ Medical usage logged!")
            pause()
        elif choice == '4':
            clear_screen(); print_donor_choices(); pause()
        elif choice == '5':
            clear_screen()
            name = get_string_input("Donor Name: ")
            blood = get_string_input("Blood Type: ")
            contact = get_string_input("Contact: ")
            models.add_donor(name, blood, contact, username)
            print("\n✅ Walk-In Registered!")
            pause()
        elif choice == '6':
            clear_screen()
            print_donor_choices()
            d_id = get_int_input("\nDonor ID: ")
            date = get_date_input("Date")
            amt = get_int_input("Amount (ml): ")
            models.add_donation_record(d_id, hosp_id, date, amt, username)
            print("\n✅ Donation logged at our facility!")
            pause()
        elif choice == '7':
            clear_screen()
            print_hospital_choices()
            dest = get_int_input("\nRequesting FROM (Hospital ID): ")
            print_item_choices()
            item = get_int_input("\nRequired Item ID: ")
            qty = get_int_input("Quantity needed: ")
            models.create_transfer_request(hosp_id, dest, item, qty, username)
            print("\n✅ Emergency request submitted to logistics!")
            pause()
        elif choice == '8': break
        else:
            print("❌ Invalid choice."); pause()

# ==========================================
# LOGIN SYSTEM
# ==========================================
def login_screen():
    while True:
        clear_screen()
        print("="*40)
        print(" 🏥 WELCOME TO VITALFLOW SECURE LOGIN 🏥")
        print("="*40)
        
        username = input("Username: ")
        password = input("Password: ")
        
        user_record = models.get_staff_by_username(username)
        
        # Checking against tuple index: 1 is Username, 2 is Password, 3 is Role, 4 is Hosp ID
        if user_record and str(user_record[2]) == password:
            print(f"\n✅ Login successful! Welcome, {username}.")
            pause()
            
            if user_record[3] == 1:
                admin_dashboard(username)
            else:
                staff_dashboard(username, user_record[4])
        else:
            print("\n❌ Invalid credentials. Access Denied.")
            retry = input("Try again? (y/n): ")
            if retry.lower() != 'y':
                break

if __name__ == '__main__':
    login_screen()
    clear_screen()
    print("System Shutdown. Goodbye!")