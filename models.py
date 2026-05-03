from database import get_db_connection

# ==========================================
# SUPER-AUDITOR HELPER FUNCTION
# ==========================================
def execute_query(query, params=(), staff_id="System", table_affected="Unknown"):
    import sqlite3
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Execute the main operation
    cursor.execute(query, params)
    
    # 2. Automatically Log the Action using local time
    action_type = query.strip().split(' ')[0].upper() # Extracts INSERT, UPDATE, or DELETE
    log_query = """
        INSERT INTO Audit_Logs (Staff_ID, Action, Table_Affected, Timestamp) 
        VALUES (?, ?, ?, datetime('now', 'localtime'))
    """
    cursor.execute(log_query, (str(staff_id), f"{action_type}: {query[:50]}...", table_affected))
    
    conn.commit()
    conn.close()

def fetch_all(query, params=()):
    conn = get_db_connection()
    results = conn.execute(query, params).fetchall()
    conn.close()
    return results

def fetch_one(query, params=()):
    conn = get_db_connection()
    result = conn.execute(query, params).fetchone()
    conn.close()
    return result

# ==========================================
# 1. HOSPITALS
# ==========================================
def add_hospital(name, location, contact, staff_id):
    execute_query("INSERT INTO Hospitals (Name, Location, Contact) VALUES (?, ?, ?)", (name, location, contact), staff_id, "Hospitals")

def get_all_hospitals(): 
    return fetch_all("SELECT * FROM Hospitals")

def update_hospital(h_id, name, location, contact, staff_id):
    conn = get_db_connection()
    if name: conn.execute("UPDATE Hospitals SET Name = ? WHERE Hospital_ID = ?", (name, h_id))
    if location: conn.execute("UPDATE Hospitals SET Location = ? WHERE Hospital_ID = ?", (location, h_id))
    if contact: conn.execute("UPDATE Hospitals SET Contact = ? WHERE Hospital_ID = ?", (contact, h_id))
    conn.execute("INSERT INTO Audit_Logs (Staff_ID, Action, Table_Affected, Timestamp) VALUES (?, ?, ?, datetime('now', 'localtime'))", (str(staff_id), "UPDATE: Hospital Details", "Hospitals"))
    conn.commit()
    conn.close()

def delete_hospital(h_id, staff_id):
    execute_query("DELETE FROM Hospitals WHERE Hospital_ID = ?", (h_id,), staff_id, "Hospitals")

# ==========================================
# 2. INVENTORY ITEMS (GLOBAL CATALOG)
# ==========================================
def add_item(name, category, unit, staff_id):
    execute_query("INSERT INTO Inventory_Items (Item_Name, Category, Unit_Type) VALUES (?, ?, ?)", (name, category, unit), staff_id, "Inventory_Items")

def get_all_items(): 
    return fetch_all("SELECT * FROM Inventory_Items")

def update_item(i_id, name, category, unit, staff_id):
    conn = get_db_connection()
    if name: conn.execute("UPDATE Inventory_Items SET Item_Name = ? WHERE Item_ID = ?", (name, i_id))
    if category: conn.execute("UPDATE Inventory_Items SET Category = ? WHERE Item_ID = ?", (category, i_id))
    if unit: conn.execute("UPDATE Inventory_Items SET Unit_Type = ? WHERE Item_ID = ?", (unit, i_id))
    conn.execute("INSERT INTO Audit_Logs (Staff_ID, Action, Table_Affected, Timestamp) VALUES (?, ?, ?, datetime('now', 'localtime'))", (str(staff_id), "UPDATE: Catalog Item", "Inventory_Items"))
    conn.commit()
    conn.close()

def delete_item(i_id, staff_id):
    execute_query("DELETE FROM Inventory_Items WHERE Item_ID = ?", (i_id,), staff_id, "Inventory_Items")

def consume_hospital_inventory(inv_id, qty_used, staff_id):
    # Subtracts the used quantity from the current stock
    execute_query("UPDATE Hospital_Inventory SET Quantity = Quantity - ? WHERE Inventory_ID = ? AND Quantity >= ?", (qty_used, inv_id, qty_used), staff_id, "Hospital_Inventory")

# ==========================================
# 3. HOSPITAL INVENTORY (STOCK)
# ==========================================
def add_hospital_inventory(hosp_id, item_id, qty, expiry, staff_id):
    execute_query("INSERT INTO Hospital_Inventory (Hospital_ID, Item_ID, Quantity, Expiry_Date) VALUES (?, ?, ?, ?)", (hosp_id, item_id, qty, expiry), staff_id, "Hospital_Inventory")

def get_inventory_by_hospital(hosp_id):
    return fetch_all("SELECT * FROM Hospital_Inventory WHERE Hospital_ID = ?", (hosp_id,))

def update_inventory_quantity(inv_id, new_quantity, staff_id): 
    if new_quantity:
        execute_query("UPDATE Hospital_Inventory SET Quantity = ? WHERE Inventory_ID = ?", (new_quantity, inv_id), staff_id, "Hospital_Inventory")

def delete_hospital_inventory(inv_id, staff_id): 
    execute_query("DELETE FROM Hospital_Inventory WHERE Inventory_ID = ?", (inv_id,), staff_id, "Hospital_Inventory")

# ==========================================
# 4. DONORS
# ==========================================
def add_donor(name, blood, contact, staff_id):
    execute_query("INSERT INTO Donors (Name, Blood_Type, Contact) VALUES (?, ?, ?)", (name, blood, contact), staff_id, "Donors")

def get_all_donors(): 
    return fetch_all("SELECT * FROM Donors")

def update_donor(d_id, name, blood, contact, staff_id):
    conn = get_db_connection()
    if name: conn.execute("UPDATE Donors SET Name = ? WHERE Donor_ID = ?", (name, d_id))
    if blood: conn.execute("UPDATE Donors SET Blood_Type = ? WHERE Donor_ID = ?", (blood, d_id))
    if contact: conn.execute("UPDATE Donors SET Contact = ? WHERE Donor_ID = ?", (contact, d_id))
    conn.execute("INSERT INTO Audit_Logs (Staff_ID, Action, Table_Affected, Timestamp) VALUES (?, ?, ?, datetime('now', 'localtime'))", (str(staff_id), "UPDATE: Donor Info", "Donors"))
    conn.commit()
    conn.close()

def delete_donor(d_id, staff_id):
    execute_query("DELETE FROM Donors WHERE Donor_ID = ?", (d_id,), staff_id, "Donors")

# ==========================================
# 5. DONATION RECORDS
# ==========================================
def add_donation_record(donor_id, hosp_id, date, amount, staff_id):
    execute_query("INSERT INTO Donation_Records (Donor_ID, Hospital_ID, Date, Amount) VALUES (?, ?, ?, ?)", (donor_id, hosp_id, date, amount), staff_id, "Donation_Records")

def get_all_donations(): 
    return fetch_all("SELECT * FROM Donation_Records")

def get_donations_by_hospital(h_id): 
    return fetch_all("SELECT * FROM Donation_Records WHERE Hospital_ID = ?", (h_id,))

def update_donation_amount(don_id, amount, staff_id): 
    if amount:
        execute_query("UPDATE Donation_Records SET Amount = ? WHERE Donation_ID = ?", (amount, don_id), staff_id, "Donation_Records")

def delete_donation_record(don_id, staff_id): 
    execute_query("DELETE FROM Donation_Records WHERE Donation_ID = ?", (don_id,), staff_id, "Donation_Records")

# ==========================================
# 6. TRANSFER REQUESTS
# ==========================================
def create_transfer_request(o_id, d_id, i_id, qty, staff_id):
    execute_query("INSERT INTO Transfer_Requests (Origin_Hospital_ID, Dest_Hospital_ID, Item_ID, Quantity) VALUES (?, ?, ?, ?)", (o_id, d_id, i_id, qty), staff_id, "Transfer_Requests")

def get_all_transfer_requests(): 
    return fetch_all("SELECT * FROM Transfer_Requests")

def update_transfer_quantity(r_id, origin, dest, item, qty, staff_id):
    if qty: execute_query("UPDATE Transfer_Requests SET Quantity = ? WHERE Request_ID = ?", (qty, r_id), staff_id, "Transfer_Requests")

def delete_transfer_request(r_id, staff_id):
    execute_query("DELETE FROM Transfer_Requests WHERE Request_ID = ?", (r_id,), staff_id, "Transfer_Requests")

# ==========================================
# 7. TRANSFER STATUS
# ==========================================
def add_transfer_status(r_id, status, staff_id):
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Insert the paperwork (The Status Log)
        cursor.execute("INSERT INTO Transfer_Status (Request_ID, Status) VALUES (?, ?)", (r_id, status))
        cursor.execute("INSERT INTO Audit_Logs (Staff_ID, Action, Table_Affected, Timestamp) VALUES (?, ?, ?, datetime('now', 'localtime'))", 
                       (str(staff_id), f"INSERT: Transfer {r_id} status to {status}", "Transfer_Status"))
        
        if status == "Delivered":
            # A. Find out exactly what is being moved
            cursor.execute("SELECT Origin_Hospital_ID, Dest_Hospital_ID, Item_ID, Quantity FROM Transfer_Requests WHERE Request_ID = ?", (r_id,))
            request_data = cursor.fetchone()
            
            if request_data:
                o_id, d_id, item_id, qty = request_data
                
                # B. Subtract from Origin Hospital (Ensuring they don't go below 0)
                cursor.execute("UPDATE Hospital_Inventory SET Quantity = Quantity - ? WHERE Hospital_ID = ? AND Item_ID = ? AND Quantity >= ?", (qty, o_id, item_id, qty))
                
                # 🚨 SECURITY FIX: Check if the origin actually had the stock to give!
                if cursor.rowcount == 0:
                    raise ValueError(f"Insufficient stock at Origin Hospital. Transfer of {qty} units failed.")
                
                # C. Check if Destination Hospital already has this item on their shelves
                cursor.execute("SELECT Inventory_ID FROM Hospital_Inventory WHERE Hospital_ID = ? AND Item_ID = ?", (d_id, item_id))
                dest_stock = cursor.fetchone()
                
                if dest_stock:
                    # Update existing shelf space
                    cursor.execute("UPDATE Hospital_Inventory SET Quantity = Quantity + ? WHERE Hospital_ID = ? AND Item_ID = ?", (qty, d_id, item_id))
                else:
                    # Create new shelf space
                    cursor.execute("INSERT INTO Hospital_Inventory (Hospital_ID, Item_ID, Quantity, Expiry_Date) VALUES (?, ?, ?, date('now', '+1 year'))", (d_id, item_id, qty))
                
                # D. Log the physical system automation
                cursor.execute("INSERT INTO Audit_Logs (Staff_ID, Action, Table_Affected, Timestamp) VALUES (?, ?, ?, datetime('now', 'localtime'))", 
                               (str(staff_id), f"AUTO-LOGISTICS: Moved {qty} units of Item {item_id}", "Hospital_Inventory"))
                
        conn.commit()
    except Exception as e:
        conn.rollback() # Cancels all database changes if the glitch is detected
        raise e # Passes the error to the GUI/CMD to alert the user
    finally:
        conn.close()

def get_all_transfer_statuses(): 
    return fetch_all("SELECT * FROM Transfer_Status")

def update_status_text(s_id, status, staff_id): 
    if status:
        execute_query("UPDATE Transfer_Status SET Status = ? WHERE Status_ID = ?", (status, s_id), staff_id, "Transfer_Status")

def delete_transfer_status(s_id, staff_id): 
    execute_query("DELETE FROM Transfer_Status WHERE Status_ID = ?", (s_id,), staff_id, "Transfer_Status")

# ==========================================
# 8. ROLES
# ==========================================
def add_role(role_name, staff_id): 
    execute_query("INSERT INTO Roles (Role_Name) VALUES (?)", (role_name,), staff_id, "Roles")

def get_all_roles(): 
    return fetch_all("SELECT * FROM Roles")

def get_role_by_id(role_id): 
    return fetch_one("SELECT * FROM Roles WHERE Role_ID = ?", (role_id,))

def update_role(role_id, role_name, staff_id): 
    if role_name:
        execute_query("UPDATE Roles SET Role_Name = ? WHERE Role_ID = ?", (role_name, role_id), staff_id, "Roles")

def delete_role(role_id, staff_id): 
    execute_query("DELETE FROM Roles WHERE Role_ID = ?", (role_id,), staff_id, "Roles")

# ==========================================
# 9. STAFF & LOGS
# ==========================================

def add_staff(username, password, role_id, hospital_id, staff_id):
    execute_query("INSERT INTO Staff (Username, Password, Role_ID, Hospital_ID) VALUES (?, ?, ?, ?)", (username, password, role_id, hospital_id), staff_id, "Staff")

def get_all_staff(): 
    return fetch_all("SELECT * FROM Staff")

def get_staff_by_username(username): 
    return fetch_one("SELECT * FROM Staff WHERE Username = ?", (username,))

def update_staff(s_id, new_password, new_role_id, new_hosp_id, staff_id): 
    conn = get_db_connection()
    if new_password: conn.execute("UPDATE Staff SET Password = ? WHERE Staff_ID = ?", (new_password, s_id))
    if new_role_id: conn.execute("UPDATE Staff SET Role_ID = ? WHERE Staff_ID = ?", (new_role_id, s_id))
    if new_hosp_id: conn.execute("UPDATE Staff SET Hospital_ID = ? WHERE Staff_ID = ?", (new_hosp_id, s_id))
    
    # Trigger the Super-Auditor
    conn.execute("INSERT INTO Audit_Logs (Staff_ID, Action, Table_Affected, Timestamp) VALUES (?, ?, ?, datetime('now', 'localtime'))", (str(staff_id), "UPDATE: Staff Authorization", "Staff"))
    conn.commit()
    conn.close()

def delete_staff(s_id, staff_id): 
    execute_query("DELETE FROM Staff WHERE Staff_ID = ?", (s_id,), staff_id, "Staff")

def get_all_logs(): 
    return fetch_all("SELECT * FROM Audit_Logs ORDER BY Timestamp DESC")


# ==========================================
# 10. ADVANCED REPORTING (COMPLEX & AGGREGATE JOINS)
# ==========================================
def get_staff_report():
    query = """
        SELECT s.Staff_ID, s.Username, r.Role_Name, h.Name AS Assigned_Hospital
        FROM Staff s
        LEFT JOIN Roles r ON s.Role_ID = r.Role_ID
        LEFT JOIN Hospitals h ON s.Hospital_ID = h.Hospital_ID
    """
    return fetch_all(query)

def get_inventory_report():
    query = """
        SELECT hi.Inventory_ID, h.Name AS Facility_Name, ii.Item_Name, ii.Category, hi.Quantity, hi.Expiry_Date
        FROM Hospital_Inventory hi
        JOIN Hospitals h ON hi.Hospital_ID = h.Hospital_ID
        JOIN Inventory_Items ii ON hi.Item_ID = ii.Item_ID
        ORDER BY h.Name, ii.Category
    """
    return fetch_all(query)

def get_donation_report():
    query = """
        SELECT dr.Donation_ID, d.Name AS Donor_Name, d.Blood_Type, h.Name AS Receiving_Hospital, dr.Date, dr.Amount
        FROM Donation_Records dr
        JOIN Donors d ON dr.Donor_ID = d.Donor_ID
        JOIN Hospitals h ON dr.Hospital_ID = h.Hospital_ID
        ORDER BY dr.Date DESC
    """
    return fetch_all(query)

def get_full_transfer_history():
    query = """
        SELECT ts.Status_ID, orig.Name AS From_Hospital, dest.Name AS To_Hospital, item.Item_Name AS Supply, tr.Quantity, ts.Status, ts.Timestamp
        FROM Transfer_Status ts
        JOIN Transfer_Requests tr ON ts.Request_ID = tr.Request_ID
        JOIN Hospitals orig ON tr.Origin_Hospital_ID = orig.Hospital_ID
        JOIN Hospitals dest ON tr.Dest_Hospital_ID = dest.Hospital_ID
        JOIN Inventory_Items item ON tr.Item_ID = item.Item_ID
        ORDER BY ts.Timestamp DESC
    """
    return fetch_all(query)

def get_deep_audit_report():
    query = """
        SELECT a.Log_ID, a.Timestamp, a.Staff_ID AS Username, r.Role_Name, a.Action, a.Table_Affected
        FROM Audit_Logs a
        LEFT JOIN Staff s ON a.Staff_ID = s.Username
        LEFT JOIN Roles r ON s.Role_ID = r.Role_ID
        ORDER BY a.Timestamp DESC
    """
    return fetch_all(query)

# --- NEW MATHEMATICAL AGGREGATE REPORTS ---

def get_blood_bank_summary():
    query = """
        SELECT 
            h.Name AS Hospital_Name, 
            d.Blood_Type, 
            COUNT(dr.Donation_ID) AS Number_of_Donors,
            SUM(dr.Amount) AS Total_Volume_ml
        FROM Donation_Records dr
        JOIN Donors d ON dr.Donor_ID = d.Donor_ID
        JOIN Hospitals h ON dr.Hospital_ID = h.Hospital_ID
        GROUP BY h.Name, d.Blood_Type
        ORDER BY h.Name, d.Blood_Type
    """
    return fetch_all(query)

def get_logistics_impact():
    query = """
        SELECT 
            orig.Name AS Supplying_Hospital, 
            item.Category, 
            SUM(tr.Quantity) AS Total_Items_Delivered,
            COUNT(tr.Request_ID) AS Number_of_Shipments
        FROM Transfer_Requests tr
        JOIN Hospitals orig ON tr.Origin_Hospital_ID = orig.Hospital_ID
        JOIN Inventory_Items item ON tr.Item_ID = item.Item_ID
        JOIN Transfer_Status ts ON tr.Request_ID = ts.Request_ID
        WHERE ts.Status = 'Delivered'
        GROUP BY orig.Name, item.Category
        ORDER BY Total_Items_Delivered DESC
    """
    return fetch_all(query)