import streamlit as st
import pandas as pd
import models

# ==========================================
# PAGE CONFIGURATION & PREMIUM THEME
# ==========================================
st.set_page_config(page_title="VitalFlow Secure Dashboard", page_icon="🩺", layout="wide")

st.markdown("""
    <style>
    /* Upgraded KPI Cards with Gradients and Hover Effects */
    .kpi-card { 
        padding: 20px; 
        border-radius: 12px; 
        color: white; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.25); 
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.4);
    }
    .kpi-title { font-size: 15px; font-weight: 600; margin-bottom: 10px; letter-spacing: 0.5px; opacity: 0.9; text-transform: uppercase;}
    .kpi-value { font-size: 40px; font-weight: 700; margin: 0; line-height: 1;}
    
    /* Modern UI Gradients */
    .bg-red { background: linear-gradient(135deg, #e53935 0%, #c62828 100%); }
    .bg-blue { background: linear-gradient(135deg, #29b6f6 0%, #0277bd 100%); }
    .bg-green { background: linear-gradient(135deg, #66bb6a 0%, #2e7d32 100%); }
    
    /* Clean Sidebar Styling */
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-of-type { display: none; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 10px 15px; margin-bottom: 5px; border-radius: 5px; transition: background-color 0.3s; cursor: pointer;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background-color: rgba(255,255,255,0.1); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE (LOGIN ENGINE)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role_id' not in st.session_state:
    st.session_state.role_id = None
if 'hospital_id' not in st.session_state:
    st.session_state.hospital_id = None

# ==========================================
# OOP UI FACTORY COMPONENT
# ==========================================

def render_crud_tabs(tab_read, tab_create, tab_manage, item_label, columns, get_func, add_func, update_func, delete_func):
    """Dynamically renders full CRUD interfaces and tracks the active user."""
    
    with tab_read:
        data = get_func()
        if data:
            df = pd.DataFrame(data, columns=columns)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(f"No {item_label}s found in the database.")
            
    # RBAC Enforcement: Only draw Create/Manage if the tabs were generated for Admin
    if st.session_state.role_id == 1 and tab_create and tab_manage:
        with tab_create:
            with st.form(f"add_{item_label}_form", clear_on_submit=True):
                st.subheader(f"Register New {item_label}")
                inputs = [st.text_input(col) for col in columns[1:]]
                if st.form_submit_button(f"Add {item_label}"):
                    if all(inputs):
                        add_func(*inputs, st.session_state.username) 
                        st.success(f"✅ {item_label} added successfully!")
                        st.rerun()
                    else:
                        st.error("All fields are required.")
                
        with tab_manage:
            data = get_func()
            if data:
                mapping = {f"ID: {row[0]} - {row[1]}": row[0] for row in data}
                selected = st.selectbox(f"Select {item_label} to Manage:", options=list(mapping.keys()))
                target_id = mapping[selected]
                
                colA, colB = st.columns(2)
                with colA:
                    with st.form(f"update_{item_label}_form"):
                        st.write("#### ✏️ Update Details")
                        st.caption("Leave blank to keep existing data.")
                        upd_inputs = [target_id] + [st.text_input(f"New {col}") for col in columns[1:]]
                        if st.form_submit_button("Update Record"):
                            update_func(*upd_inputs, st.session_state.username)
                            st.success("✅ Record Updated!")
                            st.rerun()
                            
                with colB:
                    with st.form(f"delete_{item_label}_form"):
                        st.write("#### ⚠️ Danger Zone")
                        confirm = st.checkbox("I confirm permanent deletion.")
                        if st.form_submit_button("Delete Record"):
                            if confirm:
                                delete_func(target_id, st.session_state.username)
                                st.success("🗑️ Record Deleted!")
                                st.rerun()
                            else:
                                st.warning("Check the confirmation box to proceed.")
            else:
                st.info(f"No {item_label}s available to manage.")
# ==========================================
# LOGIN SCREEN
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        st.markdown("""<div class="kpi-card bg-blue" style="text-align: center;">
            <h1 style="margin:0; color:white;">🩺 VitalFlow Portal</h1>
            <p style="margin:0; opacity:0.8;">Authorized Personnel Only</p>
            </div><br>""", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username_input = st.text_input("Username")
            password_input = st.text_input("Password", type="password")
            if st.form_submit_button("Authenticate Access", use_container_width=True):
                user_record = models.get_staff_by_username(username_input)
                if user_record and str(user_record[2]) == password_input:  
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    st.session_state.role_id = user_record[3] 
                    st.session_state.hospital_id = user_record[4] 
                    st.rerun()
                else:
                    st.error("❌ Access Denied. Invalid credentials.")

# ==========================================
# MAIN DASHBOARD (LOCKED)
# ==========================================
else:
    # --- NEW BRANDED SIDEBAR LOGO ---
    st.sidebar.markdown("""
        <div style="text-align: center; margin-top: -20px; padding-bottom: 10px;">
            <h1 style="font-size: 44px; font-weight: 900; margin: 0; line-height: 1.2; font-family: sans-serif;">
                🩺 <span style="color: #0288d1;">Vital</span><span style="color: #e53935;">Flow</span>
            </h1>
            <div style="font-size: 13px; color: gray; letter-spacing: 1.5px; text-transform: uppercase; font-weight: bold;">
                Secure Medical Network
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown(f"**User:** `{st.session_state.username}`")
    role_text = "Admin" if st.session_state.role_id == 1 else "Staff"
    st.sidebar.markdown(f"**Role:** `{role_text}`")
    st.sidebar.markdown("---")
    
    # RBAC Enforcement: Dynamic Menu Logic
    if st.session_state.role_id == 1:
        menu = ["📊 Dashboard", "🏥 Hospitals", "📦 Inventory", "🩸 Donors", "🚑 Transfers", "⚙️ System Admin", "📈 Advanced Reports"]
    else:
        # Staff version: No System Admin, No Advanced Reports
        menu = ["📊 Dashboard", "🏥 Hospitals", "📦 Inventory", "🩸 Donors", "🚑 Transfers"]
    
    choice = st.sidebar.radio("Navigation", menu)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Log Out", type="primary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role_id = None
        st.session_state.hospital_id = None
        st.rerun()

    # --- PAGE 1: DASHBOARD (Vertical Flow Layout) ---
    if choice == "📊 Dashboard":
        # Upgraded Header with Live Status Pulse
        st.markdown("""
            <div style="display: flex; align-items: center; margin-bottom: 20px;">
                <h1 style="margin: 0;">Network Dashboard</h1>
                <div style="margin-left: 15px; width: 12px; height: 12px; background-color: #2e7d32; border-radius: 50%; box-shadow: 0 0 10px #66bb6a; animation: pulse 1.5s infinite;"></div>
                <span style="margin-left: 8px; font-size: 14px; color: #66bb6a; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Live System Status</span>
            </div>
            <style>
                @keyframes pulse {
                    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(102, 187, 106, 0.7); }
                    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(102, 187, 106, 0); }
                    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(102, 187, 106, 0); }
                }
            </style>
        """, unsafe_allow_html=True)
        
        # 1. DYNAMIC KPI ENGINE (Descriptive Titles)
        inv_data = models.get_inventory_report() 
        total_o_minus = sum([row[4] for row in inv_data if 'O-' in str(row[2])]) if inv_data else 0
        total_ppe = sum([row[4] for row in inv_data if row[3] == 'PPE']) if inv_data else 0
        active_transfers = len(models.get_all_transfer_requests())

        col1, col2, col3 = st.columns(3)
        with col1: st.markdown(f"""<div class="kpi-card bg-red"><div class="kpi-title">🩸 Critical Blood (O-)</div><div class="kpi-value">{total_o_minus} Units</div></div>""", unsafe_allow_html=True)
        with col2: st.markdown(f"""<div class="kpi-card bg-blue"><div class="kpi-title">📦 Total PPE Stock</div><div class="kpi-value">{total_ppe} Boxes</div></div>""", unsafe_allow_html=True)
        with col3: st.markdown(f"""<div class="kpi-card bg-green"><div class="kpi-title">🚑 System Logistics</div><div class="kpi-value">{active_transfers} Requests</div></div>""", unsafe_allow_html=True)

        st.markdown("""<div style="border-bottom: 2px solid #333; margin: 30px 0 20px 0;"></div>""", unsafe_allow_html=True) 

        # 2. GRAPH SECTION (Full Width / Vertical)
        st.markdown("""<h3 style="color: #0288d1; border-left: 5px solid #0288d1; padding-left: 15px; margin-bottom: 20px;">📊 Regional Stock Distribution</h3>""", unsafe_allow_html=True)
        if inv_data:
            df_inv = pd.DataFrame(inv_data, columns=['Barcode', 'Facility', 'Item', 'Category', 'Qty', 'Expiry'])
            stock_chart_data = df_inv.groupby('Facility')['Qty'].sum()
            st.bar_chart(stock_chart_data, color="#0288d1", height=400)
        else:
            st.info("No inventory data to visualize.")

        st.markdown("""<div style="border-bottom: 2px solid #333; margin: 40px 0 20px 0;"></div>""", unsafe_allow_html=True)

        # 3. LOGISTICS OVERVIEW (Vertical Scroll Window)
        st.markdown("""<h3 style="color: #66bb6a; border-left: 5px solid #66bb6a; padding-left: 15px; margin-bottom: 20px;">🚑 Real-Time Logistics Ledger</h3>""", unsafe_allow_html=True)
        data = models.get_full_transfer_history()
        if data: 
            df_logs = pd.DataFrame(data, columns=['Status ID', 'Origin', 'Destination', 'Supply', 'Qty', 'Status', 'Timestamp'])
            # height=400 creates the sliding/scrollable box for massive data
            st.dataframe(df_logs, use_container_width=True, hide_index=True, height=400)
        else:
            st.info("No active logistics found.")

   # --- PAGE 2: HOSPITALS ---
    elif choice == "🏥 Hospitals":
        st.title("Hospital Management")
        
        if st.session_state.role_id == 1:
            tabs = st.tabs(["View Directory", "Add Hospital", "Manage Records"])
            tab_read, tab_create, tab_manage = tabs
        else:
            tabs = st.tabs(["View Directory"])
            tab_read = tabs[0]
            tab_create = tab_manage = None
            
        render_crud_tabs(tab_read, tab_create, tab_manage, "Facility", ['Hospital_ID', 'Name', 'Location', 'Contact'], 
                         models.get_all_hospitals, models.add_hospital, models.update_hospital, models.delete_hospital)

   # --- PAGE 3: INVENTORY ---
    elif choice == "📦 Inventory":
        st.title("Inventory & Stock Management")
        
        # UI HELPER: Fetch dictionaries to map text names to database IDs
        hospitals = models.get_all_hospitals()
        hosp_dict = {f"{h[1]} ({h[2]})": h[0] for h in hospitals} if hospitals else {}
        
        items = models.get_all_items()
        item_dict = {f"{i[1]} ({i[2]})": i[0] for i in items} if items else {}
        
        if st.session_state.role_id == 1:
            # Clean tab names without "Admin:" or "Staff:" prefixes
            tabs = st.tabs(["Global Catalog", "Add Item", "Manage Catalog", "Hospital Stock Search", "Allocate Stock", "Dispense Item"])
            tab_read, tab_create, tab_manage, tab_search, tab_allocate, tab_dispense = tabs
        else:
            # Staff only sees the tabs relevant to them
            tabs = st.tabs(["Global Catalog", "Hospital Stock Search", "Dispense Item"])
            tab_read, tab_search, tab_dispense = tabs
            tab_create = tab_manage = tab_allocate = None
        
        render_crud_tabs(tab_read, tab_create, tab_manage, "Item", ['Item_ID', 'Item_Name', 'Category', 'Unit_Type'], 
                         models.get_all_items, models.add_item, models.update_item, models.delete_item)
        
        with tab_search:
            st.subheader("View Specific Hospital Stock")
            h_search_name = st.selectbox("Select Hospital Facility:", options=["-- Select Facility --"] + list(hosp_dict.keys()))
            
            if st.button("Search Stock"):
                if h_search_name == "-- Select Facility --":
                    st.warning("Please select a facility.")
                else:
                    stock = models.get_inventory_by_hospital(hosp_dict[h_search_name])
                    if stock:
                        # Map item IDs back to names for the display table
                        i_map = {i[0]: i[1] for i in items} if items else {}
                        formatted_stock = [(s[0], s[1], f"{s[2]} - {i_map.get(s[2], 'Unknown')}", s[3], s[4]) for s in stock]
                        st.dataframe(pd.DataFrame(formatted_stock, columns=['Inventory_ID (Barcode)', 'Hospital_ID', 'Item', 'Quantity', 'Expiry']), use_container_width=True, hide_index=True)
                    else:
                        st.info("No stock found for this facility.")
                    
        if tab_allocate:
            with tab_allocate:
                st.subheader("Allocate Stock to Hospital Warehouse")
                with st.form("allocate_stock_form", clear_on_submit=True):
                    s_hosp = st.selectbox("Target Hospital", options=list(hosp_dict.keys()))
                    s_item = st.selectbox("Catalog Item", options=list(item_dict.keys()))
                    s_qty = st.number_input("Quantity to Dispatch", min_value=1, step=1)
                    s_exp = st.date_input("Batch Expiry Date")
                    
                    if st.form_submit_button("Allocate Inventory"):
                        models.add_hospital_inventory(hosp_dict[s_hosp], item_dict[s_item], s_qty, s_exp.strftime('%Y-%m-%d'), st.session_state.username)
                        st.success(f"✅ {s_qty} units successfully allocated to {s_hosp}!")
                
        with tab_dispense:
            with st.form("dispense_stock_form", clear_on_submit=True):
                st.subheader("Record Medical Usage")
                st.caption("Subtract items used on patients from our local warehouse.")
                # We leave this as a number input because Inventory_IDs act like Barcodes you scan or type
                use_inv_id = st.number_input("Inventory ID (Barcode)", min_value=1, step=1)
                use_qty = st.number_input("Quantity Used", min_value=1, step=1)
                
                if st.form_submit_button("Log Usage"):
                    models.consume_hospital_inventory(use_inv_id, use_qty, st.session_state.username)
                    st.success(f"✅ {use_qty} units dispensed and logged!")

 # --- PAGE 4: DONORS ---
    elif choice == "🩸 Donors":
        st.title("Blood Donor Management")
        
        # UI HELPER: Fetch dictionaries for dropdowns
        donors = models.get_all_donors()
        donor_dict = {f"{d[1]} (Blood: {d[2]}) - {d[3]}": d[0] for d in donors} if donors else {}
        
        hospitals = models.get_all_hospitals()
        hosp_dict = {f"{h[1]} ({h[2]})": h[0] for h in hospitals} if hospitals else {}
        
        if st.session_state.role_id == 1:
            tabs = st.tabs(["View Donors", "Register Donor", "Manage Records", "Log Donation", "Manage Donations", "Register Walk-In"])
            tab_read, tab_create, tab_manage, tab_log, tab_manage_logs, tab_walkin = tabs
        else:
            tabs = st.tabs(["View Donors", "Log Donation", "Register Walk-In"])
            tab_read, tab_log, tab_walkin = tabs
            tab_create = tab_manage = tab_manage_logs = None
        
        render_crud_tabs(tab_read, tab_create, tab_manage, "Donor", ['Donor_ID', 'Name', 'Blood_Type', 'Contact'], 
                         models.get_all_donors, models.add_donor, models.update_donor, models.delete_donor)
        
        with tab_log:
            with st.form("log_donation_form", clear_on_submit=True):
                st.subheader("Record New Donation")
                log_d_name = st.selectbox("Select Registered Donor", options=list(donor_dict.keys()))
                log_h_name = st.selectbox("Receiving Hospital Facility", options=list(hosp_dict.keys()))
                log_date = st.date_input("Donation Date")
                log_amt = st.number_input("Amount (ml)", min_value=50, step=50)
                
                if st.form_submit_button("Log Record"):
                    if log_d_name and log_h_name:
                        models.add_donation_record(donor_dict[log_d_name], hosp_dict[log_h_name], log_date.strftime('%Y-%m-%d'), log_amt, st.session_state.username)
                        st.success("✅ Donation logged!")
                    
        if tab_manage_logs:
            with tab_manage_logs:
                st.subheader("Manage Logged Donations")
                donations = models.get_all_donations()
                if donations:
                    # Creating readable text for the dropdown
                    d_map = {d[0]: f"{d[1]} ({d[2]})" for d in donors} if donors else {}
                    h_map = {h[0]: h[1] for h in hospitals} if hospitals else {}
                    
                    mapping = {f"Log #{row[0]} | {d_map.get(row[1], 'Unknown')} at {h_map.get(row[2], 'Unknown')} | {row[4]}ml": row[0] for row in donations}
                    selected = st.selectbox("Select Donation Record:", options=list(mapping.keys()))
                    target_id = mapping[selected]
                    
                    colA, colB = st.columns(2)
                    with colA:
                        with st.form("update_donation_form"):
                            st.write("#### ✏️ Correct Amount")
                            u_amt = st.number_input("New Amount (ml)", min_value=0, step=50)
                            if st.form_submit_button("Update Record"):
                                models.update_donation_amount(target_id, u_amt, st.session_state.username)
                                st.success("✅ Donation amount updated!")
                                st.rerun()
                    with colB:
                        with st.form("delete_donation_form"):
                            st.write("#### ⚠️ Danger Zone")
                            confirm = st.checkbox("I confirm permanent deletion of this log.")
                            if st.form_submit_button("Delete Record"):
                                if confirm:
                                    models.delete_donation_record(target_id, st.session_state.username)
                                    st.success("🗑️ Record Deleted!")
                                    st.rerun()
                                else:
                                    st.warning("Check the confirmation box.")
                else:
                    st.info("No donation records found.")
                
        with tab_walkin:
            with st.form("staff_register_donor", clear_on_submit=True):
                st.subheader("Register Walk-In Donor")
                d_name = st.text_input("Full Name")
                d_blood = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                d_contact = st.text_input("Contact Info")
                
                if st.form_submit_button("Register Donor"):
                    if d_name:
                        models.add_donor(d_name, d_blood, d_contact, st.session_state.username)
                        st.success("✅ Donor registered by Medical Staff!")
                    else:
                        st.error("Name is required.")

  
    # --- PAGE 5: TRANSFERS ---
    elif choice == "🚑 Transfers":
        st.title("Resource Transfer Requests")
        
        # Fetch dictionaries to map text names to database IDs for dropdowns
        hospitals = models.get_all_hospitals()
        hosp_dict = {f"{h[1]} ({h[2]})": h[0] for h in hospitals} if hospitals else {}
        
        items = models.get_all_items()
        item_dict = {f"{i[1]} ({i[2]})": i[0] for i in items} if items else {}
        
        # RBAC Enforcement: Tab Generation
        if st.session_state.role_id == 1:
            tabs = st.tabs(["Active Requests", "Create Request", "Update Status", "Cancel Request", "Request Supply"])
            tab_read, tab_create, tab_update_status, tab_manage, tab_request = tabs
        else:
            tabs = st.tabs(["Active Requests", "Request Supply"])
            tab_read, tab_request = tabs
            tab_create = tab_update_status = tab_manage = None
            
        # 1. READ VIEW (Names instead of IDs)
        with tab_read:
            reqs = models.get_all_transfer_requests()
            if reqs:
                h_map = {h[0]: h[1] for h in hospitals} if hospitals else {}
                i_map = {i[0]: i[1] for i in items} if items else {}
                formatted_data = [(
                    r[0], h_map.get(r[1], 'Unknown'), h_map.get(r[2], 'Unknown'), i_map.get(r[3], 'Unknown'), r[4]
                ) for r in reqs]
                st.dataframe(pd.DataFrame(formatted_data, columns=['Req_ID', 'Origin_Hospital', 'Dest_Hospital', 'Item', 'Qty']), use_container_width=True, hide_index=True)
            else:
                st.info("No active transfer requests found.")
                
        # 2. ADMIN CREATE (Dropdown Menus)
        if tab_create:
            with tab_create:
                with st.form("admin_create_transfer", clear_on_submit=True):
                    st.subheader("Create Transfer Request")
                    c_orig = st.selectbox("Origin Hospital", options=list(hosp_dict.keys()))
                    c_dest = st.selectbox("Destination Hospital", options=list(hosp_dict.keys()))
                    c_item = st.selectbox("Item Requested", options=list(item_dict.keys()))
                    c_qty = st.number_input("Quantity", min_value=1, step=1)
                    
                    if st.form_submit_button("Submit Request"):
                        if c_orig == c_dest:
                            st.error("Origin and Destination cannot be the same.")
                        else:
                            # Passes the mapped integer ID to the database, not the string!
                            models.create_transfer_request(hosp_dict[c_orig], hosp_dict[c_dest], item_dict[c_item], c_qty, st.session_state.username)
                            st.success("✅ Transfer Request Created!")
                            st.rerun()

        # 3. ADMIN UPDATE STATUS (Dropdown for exact request)
        if tab_update_status:
            with tab_update_status:
                with st.form("update_status_form", clear_on_submit=True):
                    st.write("### Update Logistics Status")
                    if reqs:
                        # Creates a readable dropdown string like "Req #5 | O- Blood to PIMS"
                        req_options = {f"Req #{r[0]} | {i_map.get(r[3], 'Item')} to {h_map.get(r[2], 'Hosp')}": r[0] for r in reqs}
                        r_id_sel = st.selectbox("Select Request to Update", options=list(req_options.keys()))
                        r_status = st.selectbox("New Logistics Status", ["Pending", "In Transit", "Delivered", "Cancelled"])
                        
                        if st.form_submit_button("Update Status Ledger"):
                            models.add_transfer_status(req_options[r_id_sel], r_status, st.session_state.username)
                            st.success(f"✅ Status updated to {r_status}!")
                    else:
                        st.info("No active requests to update.")

        # 4. ADMIN CANCEL/DELETE
        if tab_manage:
            with tab_manage:
                with st.form("delete_transfer_form"):
                    st.write("#### ⚠️ Cancel/Delete Transfer Request")
                    if reqs:
                        req_options = {f"Req #{r[0]} | {i_map.get(r[3], 'Item')} to {h_map.get(r[2], 'Hosp')}": r[0] for r in reqs}
                        del_id_sel = st.selectbox("Select Request to Delete", options=list(req_options.keys()))
                        confirm = st.checkbox("I confirm permanent deletion.")
                        
                        if st.form_submit_button("Delete Request"):
                            if confirm:
                                models.delete_transfer_request(req_options[del_id_sel], st.session_state.username)
                                st.success("🗑️ Request Deleted!")
                                st.rerun()
                            else:
                                st.warning("Check the confirmation box.")
                    else:
                        st.info("No requests to delete.")

        # 5. STAFF REQUEST (Dropdown Menus)
        with tab_request:
            with st.form("staff_create_transfer", clear_on_submit=True):
                st.subheader("Initiate Emergency Transfer")
                t_orig = st.selectbox("Our Hospital", options=list(hosp_dict.keys()))
                t_dest = st.selectbox("Requesting From (Destination)", options=list(hosp_dict.keys()))
                t_item = st.selectbox("Required Item", options=list(item_dict.keys()))
                t_qty = st.number_input("Quantity Needed", min_value=1, step=1)
                
                if st.form_submit_button("Submit Request"):
                    if t_orig == t_dest:
                        st.error("Cannot request from your own hospital.")
                    else:
                        models.create_transfer_request(hosp_dict[t_orig], hosp_dict[t_dest], item_dict[t_item], t_qty, st.session_state.username)
                        st.success("✅ Emergency request routed to logistics!")

# --- PAGE 6: SYSTEM ADMIN ---
    elif choice == "⚙️ System Admin":
        st.title("System Administration")
        
        # UI HELPER: Fetch dictionaries for dropdowns
        hospitals = models.get_all_hospitals()
        hosp_dict = {f"{h[1]} ({h[2]})": h[0] for h in hospitals} if hospitals else {}
        # Add an option for system-wide admins who aren't tied to one hospital
        hosp_options = ["Global System (No Specific Hospital)"] + list(hosp_dict.keys())

        if st.session_state.role_id == 1:
            tab1, tab2, tab3 = st.tabs(["Raw Audit Logs", "Authorize New Employee", "Manage Personnel"])
            
            with tab1:
                logs = models.get_all_logs()
                if logs:
                    try:
                        st.dataframe(pd.DataFrame(logs, columns=['Log_ID', 'Staff_ID', 'Action', 'Table_Affected', 'Timestamp']), use_container_width=True, hide_index=True)
                    except ValueError:
                        st.dataframe(pd.DataFrame(logs))
                else:
                    st.info("No audit logs recorded yet.")
                    
            with tab2:
                with st.form("add_staff_form", clear_on_submit=True):
                    st.subheader("Register New System User")
                    new_user = st.text_input("New Username")
                    new_pass = st.text_input("Temporary Password", type="password")
                    role_selection = st.selectbox("Assign Access Level", ["2 - Medical Staff", "1 - System Administrator"])
                    new_hosp = st.selectbox("Assigned Hospital", options=hosp_options)
                    
                    if st.form_submit_button("Authorize Employee"):
                        if new_user and new_pass:
                            h_id_to_save = None if new_hosp == "Global System (No Specific Hospital)" else hosp_dict[new_hosp]
                            models.add_staff(new_user, new_pass, 1 if "1" in role_selection else 2, h_id_to_save, st.session_state.username)
                            st.success(f"✅ Employee '{new_user}' securely added to roster!")
                            st.rerun()
                        else:
                            st.error("Username and Password required.")
                            
            with tab3:
                st.subheader("Update or Revoke Access")
                staff_list = models.get_all_staff()
                if staff_list:
                    mapping = {f"ID: {row[0]} | User: {row[1]} | Role: {row[3]}": row[0] for row in staff_list}
                    selected = st.selectbox("Select Employee to Manage:", options=list(mapping.keys()))
                    target_id = mapping[selected]
                    
                    colA, colB = st.columns(2)
                    with colA:
                        with st.form("update_staff_form"):
                            st.write("#### ✏️ Update Authorization")
                            st.caption("Leave blank to keep existing data.")
                            u_pass = st.text_input("New Password", type="password")
                            u_role = st.selectbox("New Access Level", ["", "2 - Medical Staff", "1 - System Administrator"])
                            u_hosp = st.selectbox("New Assigned Hospital", options=["-- Keep Current --"] + hosp_options)
                            
                            if st.form_submit_button("Update Employee"):
                                parsed_role = 1 if "1" in u_role else (2 if "2" in u_role else None)
                                
                                parsed_hosp = None
                                if u_hosp != "-- Keep Current --":
                                    parsed_hosp = None if u_hosp == "Global System (No Specific Hospital)" else hosp_dict[u_hosp]
                                
                                # Only update if at least one field changed
                                if u_pass or parsed_role or u_hosp != "-- Keep Current --":
                                    models.update_staff(target_id, u_pass, parsed_role, parsed_hosp, st.session_state.username)
                                    st.success("✅ Employee Authorization Updated!")
                                    st.rerun()
                                else:
                                    st.warning("Please fill at least one field to update.")
                                    
                    with colB:
                        with st.form("delete_staff_form"):
                            st.write("#### ⚠️ Danger Zone")
                            confirm = st.checkbox("I confirm I want to permanently revoke this user's access.")
                            if st.form_submit_button("Revoke Access"):
                                if confirm:
                                    current_user_data = models.get_staff_by_username(st.session_state.username)
                                    if current_user_data and target_id == current_user_data[0]:
                                        st.error("⛔ Security Exception: You cannot delete your own Admin account.")
                                    else:
                                        models.delete_staff(target_id, st.session_state.username)
                                        st.success("🗑️ Access Revoked!")
                                        st.rerun()
                                else:
                                    st.warning("Check the confirmation box to proceed.")
                else:
                    st.info("No personnel found.")
        else:
            st.error("## ⛔ SECURITY VIOLATION\nYou are attempting to access a Level 1 clearance area.")

    # --- PAGE 7: ADVANCED REPORTS (THE JOIN SHOWCASE) ---
    elif choice == "📈 Advanced Reports":
        st.title("Network Analytics & Reporting")
        st.markdown("This module utilizes operations to combine data across the network.")
        
        rep1, rep2, rep3, rep4, rep5, rep6, rep7 = st.tabs([
            "Personnel Roster", 
            "Global Stock Report", 
            "Donation Analytics", 
            "Logistics History", 
            "Deep Audit Trail", 
            "Blood Bank Summary", 
            "Logistics Impact"
        ])
        
        with rep1:
            st.subheader("Staff Directory (Staff + Roles + Hospitals)")
            data = models.get_staff_report()
            if data:
                st.dataframe(pd.DataFrame(data, columns=['ID', 'Username', 'System Role', 'Assigned Facility']), use_container_width=True, hide_index=True)
            else:
                st.info("No data available.")
                
        with rep2:
            st.subheader("Comprehensive Inventory (Stock + Facilities + Catalog)")
            data = models.get_inventory_report()
            if data:
                st.dataframe(pd.DataFrame(data, columns=['Barcode', 'Facility', 'Item', 'Category', 'Qty', 'Expiry']), use_container_width=True, hide_index=True)
            else:
                st.info("No data available.")
                
        with rep3:
            st.subheader("Blood Drive Metrics (Donations + Donors + Hospitals)")
            data = models.get_donation_report()
            if data:
                st.dataframe(pd.DataFrame(data, columns=['Log ID', 'Donor Name', 'Blood Type', 'Receiving Facility', 'Date', 'Volume (ml)']), use_container_width=True, hide_index=True)
            else:
                st.info("No data available.")
                
        with rep4:
            st.subheader("End-to-End Logistics (Status + Requests + 2x Hospitals + Items)")
            st.caption("Features to track the exact movement of supplies.")
            data = models.get_full_transfer_history()
            if data:
                st.dataframe(pd.DataFrame(data, columns=['Log ID', 'Origin', 'Destination', 'Supply', 'Qty', 'Status', 'Timestamp']), use_container_width=True, hide_index=True)
            else:
                st.info("No data available.")
                
        with rep5:
            st.subheader("Deep Audit Trail (Logs + Staff + Roles)")
            st.caption("User tracking table to actual system roles for maximum security visibility.")
            data = models.get_deep_audit_report()
            if data:
                st.dataframe(pd.DataFrame(data, columns=['Log ID', 'Timestamp', 'Username', 'System Role', 'Action Taken', 'Database Table']), use_container_width=True, hide_index=True)
            else:
                st.info("No data available.")
                
        # --- NEW AGGREGATE REPORTS TABS ---
        
        with rep6:
            st.subheader("Blood Bank Summary ")
            st.caption("Calculates total blood volume available at each facility by grouping donors and records.")
            data = models.get_blood_bank_summary()
            if data:
                st.dataframe(pd.DataFrame(data, columns=['Hospital', 'Blood Type', 'Total Donors', 'Total Volume (ml)']), use_container_width=True, hide_index=True)
            else:
                st.info("No data available.")

        with rep7:
            st.subheader("Logistics Impact Report ")
            st.caption("Shows total items successfully exported by grouping delivered shipments and categories.")
            data = models.get_logistics_impact()
            if data:
                st.dataframe(pd.DataFrame(data, columns=['Supplying Hospital', 'Item Category', 'Items Delivered', 'Shipment Count']), use_container_width=True, hide_index=True)
            else:
                st.info("No data available.")