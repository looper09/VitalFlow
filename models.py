from database import get_db_connection

# ==========================================
# SUPER-AUDITOR & HELPER FUNCTIONS (POSTGRES READY)
# ==========================================
def execute_query(query, params=(), staff_id="System", table_affected="Unknown"):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if we are using PostgreSQL (Supabase) or SQLite (Local)
    is_postgres = hasattr(conn, 'get_dsn_parameters')
    
    # 🚨 Syntax Translation: PostgreSQL uses %s, SQLite uses ?
    if is_postgres:
        query = query.replace('?', '%s')
        
    cur.execute(query, params)
    
    # Audit Log Automation
    action_type = query.strip().split(' ')[0].upper()
    log_query = "INSERT INTO audit_logs (staff_id, action, table_affected) VALUES (?, ?, ?)"
    if is_postgres:
        log_query = log_query.replace('?', '%s')
    
    cur.execute(log_query, (str(staff_id), f"{action_type}: {query[:50]}...", table_affected))
    
    conn.commit()
    cur.close()
    conn.close()

def fetch_all(query, params=()):
    conn = get_db_connection()
    cur = conn.cursor()
    if hasattr(conn, 'get_dsn_parameters'):
        query = query.replace('?', '%s')
    cur.execute(query, params)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def fetch_one(query, params=()):
    conn = get_db_connection()
    cur = conn.cursor()
    if hasattr(conn, 'get_dsn_parameters'):
        query = query.replace('?', '%s')
    cur.execute(query, params)
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

# ==========================================
# 1. HOSPITALS
# ==========================================
def add_hospital(name, location, contact, staff_id):
    execute_query("INSERT INTO hospitals (name, location, contact) VALUES (?, ?, ?)", (name, location, contact), staff_id, "hospitals")

def get_all_hospitals(): 
    return fetch_all("SELECT * FROM hospitals")

def update_hospital(h_id, name, location, contact, staff_id):
    if name: execute_query("UPDATE hospitals SET name = ? WHERE hospital_id = ?", (name, h_id), staff_id, "hospitals")
    if location: execute_query("UPDATE hospitals SET location = ? WHERE hospital_id = ?", (location, h_id), staff_id, "hospitals")
    if contact: execute_query("UPDATE hospitals SET contact = ? WHERE hospital_id = ?", (contact, h_id), staff_id, "hospitals")

def delete_hospital(h_id, staff_id):
    execute_query("DELETE FROM hospitals WHERE hospital_id = ?", (h_id,), staff_id, "hospitals")

# ==========================================
# 2. INVENTORY ITEMS (GLOBAL CATALOG)
# ==========================================
def add_item(name, category, unit, staff_id):
    execute_query("INSERT INTO inventory_items (item_name, category, unit_type) VALUES (?, ?, ?)", (name, category, unit), staff_id, "inventory_items")

def get_all_items(): 
    return fetch_all("SELECT * FROM inventory_items")

def update_item(i_id, name, category, unit, staff_id):
    if name: execute_query("UPDATE inventory_items SET item_name = ? WHERE item_id = ?", (name, i_id), staff_id, "inventory_items")
    if category: execute_query("UPDATE inventory_items SET category = ? WHERE item_id = ?", (category, i_id), staff_id, "inventory_items")
    if unit: execute_query("UPDATE inventory_items SET unit_type = ? WHERE item_id = ?", (unit, i_id), staff_id, "inventory_items")

def delete_item(i_id, staff_id):
    execute_query("DELETE FROM inventory_items WHERE item_id = ?", (i_id,), staff_id, "inventory_items")

def consume_hospital_inventory(inv_id, qty_used, staff_id):
    execute_query("UPDATE hospital_inventory SET quantity = quantity - ? WHERE inventory_id = ? AND quantity >= ?", (qty_used, inv_id, qty_used), staff_id, "hospital_inventory")

# ==========================================
# 3. HOSPITAL INVENTORY (STOCK)
# ==========================================
def add_hospital_inventory(hosp_id, item_id, qty, expiry, staff_id):
    execute_query("INSERT INTO hospital_inventory (hospital_id, item_id, quantity, expiry_date) VALUES (?, ?, ?, ?)", (hosp_id, item_id, qty, expiry), staff_id, "hospital_inventory")

def get_inventory_by_hospital(hosp_id):
    return fetch_all("SELECT * FROM hospital_inventory WHERE hospital_id = ?", (hosp_id,))

def update_inventory_quantity(inv_id, new_quantity, staff_id): 
    if new_quantity:
        execute_query("UPDATE hospital_inventory SET quantity = ? WHERE inventory_id = ?", (new_quantity, inv_id), staff_id, "hospital_inventory")

def delete_hospital_inventory(inv_id, staff_id): 
    execute_query("DELETE FROM hospital_inventory WHERE inventory_id = ?", (inv_id,), staff_id, "hospital_inventory")

# ==========================================
# 4. DONORS
# ==========================================
def add_donor(name, blood, contact, staff_id):
    execute_query("INSERT INTO donors (name, blood_type, contact) VALUES (?, ?, ?)", (name, blood, contact), staff_id, "donors")

def get_all_donors(): 
    return fetch_all("SELECT * FROM donors")

def update_donor(d_id, name, blood, contact, staff_id):
    if name: execute_query("UPDATE donors SET name = ? WHERE donor_id = ?", (name, d_id), staff_id, "donors")
    if blood: execute_query("UPDATE donors SET blood_type = ? WHERE donor_id = ?", (blood, d_id), staff_id, "donors")
    if contact: execute_query("UPDATE donors SET contact = ? WHERE donor_id = ?", (contact, d_id), staff_id, "donors")

def delete_donor(d_id, staff_id):
    execute_query("DELETE FROM donors WHERE donor_id = ?", (d_id,), staff_id, "donors")

# ==========================================
# 5. DONATION RECORDS
# ==========================================
def add_donation_record(donor_id, hosp_id, date, amount, staff_id):
    execute_query("INSERT INTO donation_records (donor_id, hospital_id, date, amount) VALUES (?, ?, ?, ?)", (donor_id, hosp_id, date, amount), staff_id, "donation_records")

def get_all_donations(): 
    return fetch_all("SELECT * FROM donation_records")

def get_donations_by_hospital(h_id): 
    return fetch_all("SELECT * FROM donation_records WHERE hospital_id = ?", (h_id,))

def update_donation_amount(don_id, amount, staff_id): 
    execute_query("UPDATE donation_records SET amount = ? WHERE donation_id = ?", (amount, don_id), staff_id, "donation_records")

def delete_donation_record(don_id, staff_id): 
    execute_query("DELETE FROM donation_records WHERE donation_id = ?", (don_id,), staff_id, "donation_records")

# ==========================================
# 6. TRANSFER REQUESTS
# ==========================================
def create_transfer_request(o_id, d_id, i_id, qty, staff_id):
    execute_query("INSERT INTO transfer_requests (origin_hospital_id, dest_hospital_id, item_id, quantity) VALUES (?, ?, ?, ?)", (o_id, d_id, i_id, qty), staff_id, "transfer_requests")

def get_all_transfer_requests(): 
    return fetch_all("SELECT * FROM transfer_requests")

def update_transfer_quantity(r_id, qty, staff_id):
    if qty: execute_query("UPDATE transfer_requests SET quantity = ? WHERE request_id = ?", (qty, r_id), staff_id, "transfer_requests")

def delete_transfer_request(r_id, staff_id):
    execute_query("DELETE FROM transfer_requests WHERE request_id = ?", (r_id,), staff_id, "transfer_requests")

# ==========================================
# 7. TRANSFER STATUS
# ==========================================
def add_transfer_status(r_id, status, staff_id):
    # For complex logic involving status-based updates, we use a separate connection but within the hybrid pattern
    conn = get_db_connection()
    cur = conn.cursor()
    is_postgres = hasattr(conn, 'get_dsn_parameters')
    
    try:
        # 1. Insert Status Log
        status_q = "INSERT INTO transfer_status (request_id, status) VALUES (?, ?)"
        if is_postgres: status_q = status_q.replace('?', '%s')
        cur.execute(status_q, (r_id, status))
        
        # 2. Add Audit Log
        audit_q = "INSERT INTO audit_logs (staff_id, action, table_affected) VALUES (?, ?, ?)"
        if is_postgres: audit_q = audit_q.replace('?', '%s')
        cur.execute(audit_q, (str(staff_id), f"INSERT: Transfer {r_id} to {status}", "transfer_status"))
        
        if status == "Delivered":
            # Select details
            select_q = "SELECT origin_hospital_id, dest_hospital_id, item_id, quantity FROM transfer_requests WHERE request_id = ?"
            if is_postgres: select_q = select_q.replace('?', '%s')
            cur.execute(select_q, (r_id,))
            request_data = cur.fetchone()
            
            if request_data:
                o_id, d_id, item_id, qty = request_data
                
                # Subtract from Origin
                sub_q = "UPDATE hospital_inventory SET quantity = quantity - ? WHERE hospital_id = ? AND item_id = ? AND quantity >= ?"
                if is_postgres: sub_q = sub_q.replace('?', '%s')
                cur.execute(sub_q, (qty, o_id, item_id, qty))
                
                # Add to Destination
                check_q = "SELECT inventory_id FROM hospital_inventory WHERE hospital_id = ? AND item_id = ?"
                if is_postgres: check_q = check_q.replace('?', '%s')
                cur.execute(check_q, (d_id, item_id))
                dest_stock = cur.fetchone()
                
                if dest_stock:
                    upd_q = "UPDATE hospital_inventory SET quantity = quantity + ? WHERE hospital_id = ? AND item_id = ?"
                    if is_postgres: upd_q = upd_q.replace('?', '%s')
                    cur.execute(upd_q, (qty, d_id, item_id))
                else:
                    ins_q = "INSERT INTO hospital_inventory (hospital_id, item_id, quantity, expiry_date) VALUES (?, ?, ?, CURRENT_DATE)"
                    if is_postgres: ins_q = ins_q.replace('?', '%s')
                    cur.execute(ins_q, (d_id, item_id, qty))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_all_transfer_statuses(): 
    return fetch_all("SELECT * FROM transfer_status")

# ==========================================
# 8. ROLES & STAFF
# ==========================================
def add_role(role_name, staff_id): 
    execute_query("INSERT INTO roles (role_name) VALUES (?)", (role_name,), staff_id, "roles")

def get_all_roles(): 
    return fetch_all("SELECT * FROM roles")

def add_staff(username, password, role_id, hospital_id, staff_id):
    execute_query("INSERT INTO staff (username, password, role_id, hospital_id) VALUES (?, ?, ?, ?)", (username, password, role_id, hospital_id), staff_id, "staff")

def get_all_staff(): 
    return fetch_all("SELECT * FROM staff")

def get_staff_by_username(username): 
    return fetch_one("SELECT * FROM staff WHERE username = ?", (username,))

def update_staff(s_id, new_password, new_role_id, new_hosp_id, staff_id): 
    if new_password: execute_query("UPDATE staff SET password = ? WHERE staff_id = ?", (new_password, s_id), staff_id, "staff")
    if new_role_id: execute_query("UPDATE staff SET role_id = ? WHERE staff_id = ?", (new_role_id, s_id), staff_id, "staff")
    if new_hosp_id: execute_query("UPDATE staff SET hospital_id = ? WHERE staff_id = ?", (new_hosp_id, s_id), staff_id, "staff")

def delete_staff(s_id, staff_id): 
    execute_query("DELETE FROM staff WHERE staff_id = ?", (s_id,), staff_id, "staff")

def get_all_logs(): 
    return fetch_all("SELECT * FROM audit_logs ORDER BY timestamp DESC")

# ==========================================
# 9. ADVANCED REPORTS (JOINS)
# ==========================================
def get_staff_report():
    query = """
        SELECT s.staff_id, s.username, r.role_name, h.name AS assigned_hospital
        FROM staff s
        LEFT JOIN roles r ON s.role_id = r.role_id
        LEFT JOIN hospitals h ON s.hospital_id = h.hospital_id
    """
    return fetch_all(query)

def get_inventory_report():
    query = """
        SELECT hi.inventory_id, h.name AS facility_name, ii.item_name, ii.category, hi.quantity, hi.expiry_date
        FROM hospital_inventory hi
        JOIN hospitals h ON hi.hospital_id = h.hospital_id
        JOIN inventory_items ii ON hi.item_id = ii.item_id
        ORDER BY h.name, ii.category
    """
    return fetch_all(query)

def get_donation_report():
    query = """
        SELECT dr.donation_id, d.name AS donor_name, d.blood_type, h.name AS receiving_hospital, dr.date, dr.amount
        FROM donation_records dr
        JOIN donors d ON dr.donor_id = d.donor_id
        JOIN hospitals h ON dr.hospital_id = h.hospital_id
        ORDER BY dr.date DESC
    """
    return fetch_all(query)

def get_full_transfer_history():
    query = """
        SELECT ts.status_id, orig.name AS from_hospital, dest.name AS to_hospital, item.item_name AS supply, tr.quantity, ts.status, ts.timestamp
        FROM transfer_status ts
        JOIN transfer_requests tr ON ts.request_id = tr.request_id
        JOIN hospitals orig ON tr.origin_hospital_id = orig.hospital_id
        JOIN hospitals dest ON tr.dest_hospital_id = dest.hospital_id
        JOIN inventory_items item ON tr.item_id = item.item_id
        ORDER BY ts.timestamp DESC
    """
    return fetch_all(query)

def get_blood_bank_summary():
    query = """
        SELECT h.name AS hospital_name, d.blood_type, COUNT(dr.donation_id) AS number_of_donors, SUM(dr.amount) AS total_volume_ml
        FROM donation_records dr
        JOIN donors d ON dr.donor_id = d.donor_id
        JOIN hospitals h ON dr.hospital_id = h.hospital_id
        GROUP BY h.name, d.blood_type
        ORDER BY h.name, d.blood_type
    """
    return fetch_all(query)

def get_logistics_impact():
    query = """
        SELECT orig.name AS supplying_hospital, item.category, SUM(tr.quantity) AS total_items_delivered, COUNT(tr.request_id) AS number_of_shipments
        FROM transfer_requests tr
        JOIN hospitals orig ON tr.origin_hospital_id = orig.hospital_id
        JOIN inventory_items item ON tr.item_id = item.item_id
        JOIN transfer_status ts ON tr.request_id = ts.request_id
        WHERE ts.status = 'Delivered'
        GROUP BY orig.name, item.category
        ORDER BY total_items_delivered DESC
    """
    return fetch_all(query)