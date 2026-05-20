"""
VitalFlow Secure Dashboard - Production UI
"""

from datetime import datetime
import pandas as pd
import streamlit as st

import models_compat as models
from security import PasswordSecurity
from logger_config import logger

st.set_page_config(page_title="VitalFlow Medical Network", page_icon="🩺", layout="wide")

st.markdown(
	"""
	<style>
	.stApp {
		background: #f4f7f6;
		color: #1f2937;
		font-size: 16px !important;
	}

	section[data-testid="stSidebar"] {
		display: none;
	}

	.block-container {
		padding-top: 0.5rem;
		padding-bottom: 2rem;
		max-width: 100%;
		margin: 0 auto;
		padding-left: 2rem;
		padding-right: 2rem;
	}

	.vf-header {
		background: #004d99;
		color: blue;
		border-radius: 18px;
		padding: 1.2rem 1.5rem;
		box-shadow: 0 10px 24px rgba(0, 0, 0, 0.12);
		margin-bottom: 1rem;
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
		width: 100%;
        box-sizing: border-box;
	}

	.vf-brand {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		font-weight: 800;
		font-size: 1.35rem;
		letter-spacing: 0.02em;
		white-space: nowrap;
		flex-wrap: wrap;
    }

	.vf-brand span:first-child {
		font-size: 1.4rem;
	}

	.vf-online {
		display: inline-block;
		padding: 0.35rem 0.75rem;
		border-radius: 999px;
		background: rgba(46, 184, 46, 0.18);
        border: 1px solid rgba(46, 184, 46, 0.35);
		color: #d9ffe0;
		font-size: 0.8rem;
		font-weight: 800;
		text-transform: uppercase;
		vertical-align: middle;
		white-space: nowrap;
    }

	.vf-user-chip {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		background: rgba(255, 255, 255, 0.14);
		border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 999px;
		padding: 0.5rem 1rem;
		font-weight: 700;
		white-space: nowrap;
		font-size: 0.95rem;
	}

	.stTabs [data-baseweb="tab-list"] {
		gap: 0.5rem;
		background: transparent;
        border-bottom: 2px solid #d4dde9;
		overflow-x: auto;
		padding-bottom: 0;
	}

	.stTabs [data-baseweb="tab"] {
		height: auto;
		padding: 0.95rem 1.35rem;
		border-radius: 12px 12px 0 0;
        border: 1px solid transparent;
		border-bottom: 2px solid transparent;
		background: transparent;
		color: #667085;
		font-weight: 800;
		font-size: 1rem;
		box-shadow: none;
        transition: all 0.2s ease;
	}

	.stTabs [aria-selected="true"] {
		background: white;
		color: #004d99;
		border-bottom: 3px solid #004d99;
		border-left: 1px solid #d4dde9;
        border-right: 1px solid #d4dde9;
		border-top: 1px solid #d4dde9;
	}

	.vf-shell {
		background: white;
		border: 1px solid #d8e1ec;
		border-radius: 18px;
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.06);
		padding: 1.75rem;
		margin-top: 1rem;
	}

	.vf-card {
		background: white;
		border: 1px solid #dbe4ee;
        border-radius: 16px;
		box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
		padding: 1.5rem;
	}

	.vf-section-title {
		color: #004d99;
		font-size: 1.6rem;
		font-weight: 800;
        margin: 0 0 1rem 0;
		padding-bottom: 0.5rem;
		border-bottom: 2px solid #e2e8f0;
	}

	.vf-subtitle {
		color: #6b7280;
		margin-top: -0.25rem;
		margin-bottom: 1.25rem;
		font-size: 1rem;
    }

	div[data-testid="metric-container"] {
		background: white;
		border-radius: 12px;
		border: 1px solid #e2e8f0;
		border-left-width: 8px;
		box-shadow: 0 4px 10px rgba(15, 23, 42, 0.05);
        padding: 1.25rem;
	}

	.stTextInput label,
	.stNumberInput label,
	.stSelectbox label,
	.stTextArea label,
	.stDateInput label,
	.stRadio label,
	.stCheckbox label {
		color: #0f1724 !important;
		opacity: 1 !important;
		text-shadow: none !important;
    }

	[data-testid="stForm"] {
		background: rgba(255,255,255,0.98) !important;
		padding: 0.8rem !important;
		border-radius: 12px !important;
		border: 1px solid #eef2f6 !important;
    }

	.stButton > button,
	button[kind="primary"],
	button[kind="secondary"],
	button[kind="tertiary"],
	button {
		background: #ffffff !important;
		color: #0f1724 !important;
		border: 1px solid #d4dde9 !important;
		border-radius: 10px !important;
		box-shadow: none !important;
    }

	.stButton > button:hover,
	button[kind="primary"]:hover,
	button[kind="secondary"]:hover,
	button[kind="tertiary"]:hover,
	button:hover {
		background: #f1f5f9 !important;
		color: #0f1724 !important;
	}

	</style>
	""",
	unsafe_allow_html=True,
)


# ==========================================
# SESSION STATE & LOGIN ENGINE
# ==========================================

if "logged_in" not in st.session_state:
	st.session_state.logged_in = False
	st.session_state.username = ""
	st.session_state.role_id = 2  
	st.session_state.hospital_id = 1
	st.session_state.staff_id = 1

# CRITICAL: Check for expired blood on every app reload
try:
	total_units, expired_units = models.check_blood_expiry()
	if expired_units > 0:
		logger.info(f"Auto-expired {expired_units} blood units during app startup")
except Exception as e:
	logger.warning(f"Blood expiry check failed: {e}")


def require_login():
	"""Real Authentication Screen."""
	if not st.session_state.logged_in:
		st.markdown("<h1 style='text-align: center; color: #004d99; margin-top: 50px;'>🩺 VitalFlow Medical Network</h1>", unsafe_allow_html=True)
		st.markdown("<p style='text-align: center; color: gray; margin-bottom: 30px;'>Secure Staff Portal</p>", unsafe_allow_html=True)
		
		col1, col2, col3 = st.columns([1, 2, 1])
		with col2:
			st.markdown("<div class='vf-card'>", unsafe_allow_html=True)
			with st.form("real_login_form"):
				username_input = st.text_input("Username", placeholder="e.g., asad_admin")
				password_input = st.text_input("Password", type="password", placeholder="••••••••")
				submit_button = st.form_submit_button("Authenticate Access", type="primary", use_container_width=True)
				
				if submit_button:
					user_record = models.get_staff_by_username(username_input)
					if user_record:
						stored_password = str(user_record[2])
						is_bcrypt = stored_password.startswith("$2")
						is_valid = PasswordSecurity.verify_password(password_input, stored_password) if is_bcrypt else False

						if not is_bcrypt:
							logger.warning("Blocked login for legacy password format account")
							st.error("Authentication Failed. Invalid credentials. If this continues, contact administrator.")
							is_valid = False

						if is_valid:
							st.session_state.logged_in = True
							st.session_state.username = username_input
							st.session_state.staff_id = user_record[0]
							st.session_state.role_id = user_record[3]
							st.session_state.hospital_id = user_record[4] if len(user_record) > 4 else 1
							st.rerun()
						else:
							st.error("Authentication Failed. Invalid password.")
					else:
						st.error("Authentication Failed. User not found.")
			st.markdown("</div>", unsafe_allow_html=True)
		return False
	return True


def top_header():
	"""Display the application header with user info."""
	role_name = "System Administrator" if st.session_state.role_id == 1 else "Medical Staff"
	st.markdown(
		f"""
		<div class='vf-header'>
			<div>
				<h1 style='margin:0; color:white;'>🩺 VitalFlow Dashboard</h1>
				<p style='margin:0.25rem 0 0 0; color:#e0eaf5;'>Medical Network Management System</p>
			</div>
			<div style='text-align: right; background: rgba(255,255,255,0.1); padding: 0.5rem 1.2rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2);'>
				<p style='margin:0; color:white; font-weight:bold; font-size: 1.1rem;'>👤 {st.session_state.username}</p>
				<p style='margin:0; color:#e0eaf5; font-size: 0.9rem;'>{role_name}</p>
			</div>
		</div>
		""",
		unsafe_allow_html=True,
	)


def section_hospitals():
	st.markdown("<div class='vf-card'>", unsafe_allow_html=True)
	st.markdown("<div class='vf-section-title'>Hospital Network</div>", unsafe_allow_html=True)
	st.markdown("<div class='vf-subtitle'>Manage facilities, contact details, and hospital records.</div>", unsafe_allow_html=True)

	hosp_tabs = st.tabs(["Directory", "Add / Update", "Hospital Map"])
	hospitals = models.get_all_hospitals() or []
	hosp_map = {f"{h[1]} ({h[2]})": h[0] for h in hospitals}

	with hosp_tabs[0]:
		st.markdown("#### 📋 Facility Directory")
		if hospitals:
			hosp_data = []
			for h in hospitals:
				hosp_data.append({
					"🏥 Name": h[1],
					"📍 Location": h[2],
					"📞 Contact": h[3] if len(h) > 3 else "N/A",
					"ID": h[0],
				})
			st.dataframe(hosp_data, use_container_width=True, hide_index=True)
		else:
			st.info("No hospitals registered yet.")
		st.divider()

	with hosp_tabs[1]:
		if st.session_state.role_id == 1:
			st.markdown("#### ➕ Add New Facility")
			col1, col2 = st.columns(2)

			with col1:
				st.markdown("<b>Register New Hospital</b>", unsafe_allow_html=True)
				with st.form("hospital_add_form"):
					h_name = st.text_input("Hospital Name", placeholder="General Hospital", help="Full official name of facility")
					h_loc = st.text_input("Location / Zone", placeholder="Downtown, Zone A", help="Geographic location or administrative zone")
					h_con = st.text_input("Emergency Contact", placeholder="+1 (555) 123-4567", help="Primary contact number for emergencies")
					if st.form_submit_button("✓ Register Facility", type="primary", use_container_width=True):
						if h_name and h_loc:
							success, msg = models.add_hospital(h_name, h_loc, h_con, st.session_state.staff_id)
							if success:
								st.success(f"✓ {msg}")
								st.rerun()
							else:
								st.error(f"✗ {msg}")
						else:
							st.warning("Hospital name and location are required")

			with col2:
				st.markdown("<b>Update Existing Hospital</b>", unsafe_allow_html=True)
				if hospitals:
					selected = st.selectbox("Select Hospital", list(hosp_map.keys()), key="hospital_manage")
					hosp_id = hosp_map[selected]

					with st.form("hospital_update_form"):
						u_name = st.text_input("New Name (leave blank to keep current)", help="Update facility name")
						u_loc = st.text_input("New Location (leave blank to keep current)", help="Update facility location")
						u_con = st.text_input("New Contact (leave blank to keep current)", help="Update emergency contact")
						if st.form_submit_button("✎ Update Facility", use_container_width=True):
							if u_name or u_loc or u_con:
								success, msg = models.update_hospital(hosp_id, u_name or None, u_loc or None, u_con or None, st.session_state.username)
								if success:
									st.success(f"✓ {msg}")
									st.rerun()
								else:
									st.error(f"✗ {msg}")
							else:
								st.warning("Please enter at least one field to update")

					st.divider()
					st.markdown("<b style='color: #cc0000;'>Delete Facility</b>", unsafe_allow_html=True)
					with st.form("hospital_delete_form"):
						confirm = st.checkbox("I confirm deletion of this facility", help="This action cannot be undone")
						if st.form_submit_button("🗑️ Delete Facility", use_container_width=True):
							if confirm:
								success, msg = models.delete_hospital(hosp_id, st.session_state.username)
								if success:
									st.success(f"✓ {msg}")
									st.rerun()
								else:
									st.error(f"✗ {msg}")
							else:
								st.error("Please confirm deletion")
				else:
					st.info("No hospitals available to edit.")
		else:
			st.info("🔒 Hospital editing is available to admins only.")

	with hosp_tabs[2]:
		st.markdown("#### 🗺️ Facility Map & Network")
		st.info("📍 Interactive map visualization coming soon. This will display all facilities on a geographic map with real-time status indicators.")

		if hospitals:
			st.markdown("**Registered Facilities:**")
			cols = st.columns(min(3, len(hospitals)))
			for idx, h in enumerate(hospitals):
				with cols[idx % 3]:
					st.markdown(f"""
					<div style='background: #f0f4f8; padding: 12px; border-radius: 8px; border-left: 4px solid #004d99;'>
					<b>{h[1]}</b><br>
					📍 {h[2]}<br>
					📞 {h[3] if len(h) > 3 else 'N/A'}
					</div>
					""", unsafe_allow_html=True)

	st.markdown("</div>", unsafe_allow_html=True)


def section_inventory():
	st.markdown("<div class='vf-card'>", unsafe_allow_html=True)
	st.markdown("<div class='vf-section-title'>Inventory Management</div>", unsafe_allow_html=True)
	st.markdown("<div class='vf-subtitle'>Medical equipment, stock allocation, and usage tracking.</div>", unsafe_allow_html=True)

	inv_tabs = st.tabs(["Catalog", "Add Item", "Stock Levels", "Allocate Stock", "Usage Log"])
	items = models.get_all_items() or []
	hospitals = models.get_all_hospitals() or []
	hosp_map = {f"{h[1]} ({h[2]})": h[0] for h in hospitals}
	item_map = {f"{i[1]} ({i[2]})": i[0] for i in items}

	with inv_tabs[0]:
		st.markdown("#### 📦 Equipment Catalog")
		if items:
			item_data = []
			for i in items:
				item_data.append({
					"🏷️ Equipment Name": i[1],
					"📁 Category": i[2],
					"📊 Unit": i[3] if len(i) > 3 else "Unit",
					"ID": i[0]
				})
			st.dataframe(item_data, use_container_width=True, hide_index=True)
		else:
			st.info("No inventory items registered yet.")
		st.divider()

	with inv_tabs[1]:
		st.markdown("#### ➕ Register New Equipment")
		if st.session_state.role_id == 1:
			with st.form("inventory_add_form"):
				col1, col2 = st.columns(2)
				with col1:
					item_name = st.text_input("Equipment Name", placeholder="Suction Machine", help="Official name of equipment/supply")
					category = st.selectbox("Category", ["Equipment", "Medical Supplies", "PPE", "IV Fluids", "Medications"], help="Product classification")
				with col2:
					unit_type = st.text_input("Unit Type", placeholder="units/boxes/milliliters", help="How is this item measured/counted?")
				if st.form_submit_button("✓ Register Equipment", type="primary", use_container_width=True) and item_name and unit_type:
					success, msg = models.add_item(item_name, category, unit_type, st.session_state.username)
					if success:
						st.success(f"✓ {msg}")
						st.rerun()
					else:
						st.error(f"✗ {msg}")
		else:
			st.info("🔒 Equipment registration is available to admins only.")

	with inv_tabs[2]:
		st.markdown("#### 📊 Stock Levels by Facility")
		if hospitals:
			selected_hospital = st.selectbox("Select Hospital", list(hosp_map.keys()), key="trial_stock_hosp")
			if st.button("🔍 Check Stock Levels", use_container_width=True):
				stock = models.get_inventory_by_hospital(hosp_map[selected_hospital])
				if stock:
					stock_data = []
					for s in stock:
						stock_data.append({
							"📦 Quantity": s[4] if len(s) > 4 else "N/A",
							"📅 Expiry": s[5] if len(s) > 5 else "N/A",
							"ID": s[0]
						})
					st.dataframe(stock_data, use_container_width=True, hide_index=True)
				else:
					st.info("No stock found at this facility.")
		else:
			st.info("Add hospitals first before checking stock.")

	with inv_tabs[3]:
		st.markdown("#### 🎯 Allocate Stock to Facility")
		if st.session_state.role_id == 1:
			if hospitals and items:
				with st.form("allocate_inventory_form"):
					col1, col2 = st.columns(2)
					with col1:
						st.markdown("<b>Destination</b>", unsafe_allow_html=True)
						alloc_hosp = st.selectbox("Target Hospital", list(hosp_map.keys()), key="trial_alloc_hosp", help="Hospital to receive stock")
						alloc_item = st.selectbox("Equipment", list(item_map.keys()), key="trial_alloc_item", help="Equipment type to allocate")
					with col2:
						st.markdown("<b>Quantity & Expiry</b>", unsafe_allow_html=True)
						alloc_qty = st.number_input("Quantity to Allocate", min_value=1, step=1, help="Number of units to send")
						alloc_exp = st.date_input("Expiry Date", help="When does this stock expire?")
					if st.form_submit_button("✓ Allocate Stock", type="primary", use_container_width=True):
						if not alloc_exp:
							st.error("Please select an expiry date.")
						else:
							success, msg = models.add_hospital_inventory(
								hosp_map[alloc_hosp],
								item_map[alloc_item],
								alloc_qty,
								alloc_exp.strftime("%Y-%m-%d"),
								st.session_state.username,
							)
							if success:
								st.success(f"✓ {msg}")
								st.rerun()
							else:
								st.error(f"✗ {msg}")
			else:
				st.info("Set up hospitals and equipment first.")
		else:
			st.info("🔒 Stock allocation is available to admins only.")

	with inv_tabs[4]:
		st.markdown("#### 📝 Equipment Usage Log")
		if st.session_state.role_id == 1:
			with st.form("consume_inventory_form"):
				col1, col2 = st.columns(2)
				with col1:
					use_inv_id = st.number_input("Inventory ID", min_value=1, step=1, help="ID of the inventory allocation to consume from")
				with col2:
					use_qty = st.number_input("Units Used", min_value=1, step=1, help="How many units were consumed?")
				if st.form_submit_button("✓ Log Usage", type="primary", use_container_width=True):
						success, msg = models.consume_hospital_inventory(use_inv_id, use_qty, st.session_state.username)
						if success:
							st.success(f"✓ {msg}")
							st.rerun()
						else:
							st.error(f"✗ {msg}")
	st.markdown("</div>", unsafe_allow_html=True)


def section_blood_bank():
	st.markdown("<div class='vf-card'>", unsafe_allow_html=True)
	st.markdown("<div class='vf-section-title'>🩸 Blood Bank</div>", unsafe_allow_html=True)
	st.markdown("<div class='vf-subtitle'>Blood operations, donor eligibility, and transfusion controls.</div>", unsafe_allow_html=True)

	bb_tabs = st.tabs(["Blood Inventory", "Donor Registry", "Operations", "Reports"])
	hospitals = models.get_all_hospitals() or []
	hosp_map = {f"{h[1]} ({h[2]})": h[0] for h in hospitals}
	donors = models.get_all_donors() or []
	donor_map = {f"{d[1]} (Blood: {d[2]})": d[0] for d in donors}

	with bb_tabs[0]:
		st.markdown("#### 💾 Blood Inventory by Facility")
		if hospitals:
			col1, col2 = st.columns(2)
			with col1:
				selected_hospital = st.selectbox("Select Hospital", list(hosp_map.keys()), key="trial_bb_hosp", help="Choose facility to view")
			with col2:
				blood_filter = st.selectbox("Filter by Blood Type", ["All", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], key="trial_bb_filter", help="Search by blood type")
			
			blood_rows = models.get_blood_by_hospital(hosp_map[selected_hospital], None if blood_filter == "All" else blood_filter)
			if blood_rows:
				blood_data = []
				for b in blood_rows:
					blood_data.append({
						"🩸 Type": b[2],
						"📊 Quantity (ml)": b[3] if len(b) > 3 else "N/A",
						"📅 Expiry": b[4] if len(b) > 4 else "N/A",
						"✓ Status": b[5] if len(b) > 5 else "Active"
					})
				st.dataframe(blood_data, use_container_width=True, hide_index=True)
			else:
				st.info("No blood units found at this hospital.")
		else:
			st.info("No hospitals available. Register hospitals first.")
		st.divider()

	with bb_tabs[1]:
		st.markdown("#### 👥 Donor Registry")
		if donors:
			donor_data = []
			for d in donors:
				donor_data.append({
					"👤 Name": d[1],
					"🩸 Blood Type": d[2],
					"📞 Contact": d[3] if len(d) > 3 else "N/A"
				})
			st.dataframe(donor_data, use_container_width=True, hide_index=True)
		else:
			st.info("No donors registered yet.")

		st.divider()
		st.markdown("#### ➕ Register New Donor")
		if st.session_state.role_id == 1:
			with st.form("trial_donor_add_form"):
				col1, col2 = st.columns(2)
				with col1:
					d_name = st.text_input("Full Name", placeholder="John Smith", help="Legal name of donor")
					d_blood = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], help="Certified blood type")
				with col2:
					d_contact = st.text_input("Contact Info", placeholder="+1 (555) 123-4567", help="Phone or email")
					if st.form_submit_button("✓ Register Donor", type="primary", use_container_width=True):
						if d_name:
							success, msg = models.add_donor(d_name, d_blood, d_contact, st.session_state.username)
							if success:
								st.success(f"✓ {msg}")
								st.rerun()
							else:
								st.error(f"✗ {msg}")
						else:
							st.warning("Name is required.")
		else:
			st.info("🔒 Donor registration is available to admins only.")

	with bb_tabs[2]:
		left, right = st.columns(2)
		
		with left:
			st.markdown("#### 🔍 Eligibility Check")
			if donors:
				eligible_donor = st.selectbox("Select Donor", list(donor_map.keys()), key="trial_elig_donor", help="Check donation eligibility")
				if st.button("✓ Check Eligibility", use_container_width=True):
					donor_id = donor_map[eligible_donor]
					is_eligible, details = models.check_donor_eligibility(donor_id)
					if is_eligible:
						st.success("✓ Eligible to donate")
					else:
						st.warning("⏳ Cooldown active - wait required")
					st.json(details)
			else:
				st.info("No donors registered.")
		
		with right:
			st.markdown("#### 🚨 Emergency Authority")
			st.warning("🔐 Emergency Blood Draw Override - Use in critical trauma or mass casualty situations only.", icon="⚠️")
			
			if donors:
				override_donor = st.selectbox("Select Donor for Override", list(donor_map.keys()), key="live_override_donor")
				override_reason = st.text_input("Clinical Justification", placeholder="e.g., Mass casualty event")

				if st.button("🔓 Authorize Emergency Override", type="primary", use_container_width=True):
					if override_reason:
						success, msg = models.override_donation_eligibility(
							donor_id=donor_map[override_donor],
							override_reason=override_reason,
							staff_id=st.session_state.staff_id
						)
						if success:
							st.success(f"✓ {msg}")
						else:
							st.error(f"✗ {msg}")
					else:
						st.error("You must provide a clinical justification for the audit log.")
			else:
				st.info("No donors registered to override.")

		st.divider()
		
		if st.session_state.role_id == 1:
			st.markdown("#### 🩹 Add Blood Stock")
			if hospitals:
				with st.form("trial_blood_stock_form"):
					col1, col2 = st.columns(2)
					with col1:
						add_hosp = st.selectbox("Hospital", list(hosp_map.keys()), key="trial_add_blood_hosp", help="Destination hospital")
						add_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], help="Type of blood unit")
					with col2:
						add_qty = st.number_input("Quantity (ml)", min_value=50, max_value=50000, step=50, value=450, help="Volume in milliliters")
						add_date = st.date_input("Collection Date", help="When was unit collected?")
					if st.form_submit_button("✓ Add Blood Stock", type="primary", use_container_width=True):
						if not add_date:
							st.error("Please select a collection date.")
						else:
							success, message, _ = models.add_blood_stock(
								hosp_map[add_hosp],
								add_type,
								add_qty,
								add_date.strftime("%Y-%m-%d"),
								st.session_state.username,
							)
							if success:
								st.success(f"✓ {message}")
								st.rerun()
							else:
								st.error(f"✗ {message}")

			st.divider()
			st.markdown("#### 🩸 Log Transfusion/Usage")
			if hospitals:
				st.info("🩹 Use this to record blood transfusions, wastage, or testing. Blood quantity will be automatically decremented.")
				with st.form("trial_transfusion_log_form"):
					col1, col2 = st.columns(2)
					with col1:
						trans_hosp = st.selectbox("Hospital", list(hosp_map.keys()), key="trial_trans_hosp", help="Hospital where transfusion occurred")
						trans_type = st.selectbox("Blood Type to Use", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], key="trial_trans_type", help="Select blood type needed")
					with col2:
						trans_qty = st.number_input("Volume Used (ml)", min_value=1, max_value=50000, step=50, value=450, key="trial_trans_qty", help="How much was used/wasted?")
						trans_reason = st.selectbox("Reason", ["Transfusion", "Testing", "Wastage", "Spillage", "Other"], key="trial_trans_reason", help="Purpose of usage")
					
					if st.form_submit_button("✓ Log Usage", type="primary", use_container_width=True):
						# Get blood units of this type at this hospital
						blood_units = models.get_blood_by_hospital(hosp_map[trans_hosp], trans_type, active_only=True)
						if blood_units and len(blood_units) > 0:
							# Use the first available unit (earliest expiry)
							blood_id = blood_units[0][0]
							success, msg = models.consume_blood(blood_id, trans_qty, st.session_state.username)
							if success:
								st.success(f"✓ {msg}")
								st.rerun()
							else:
								st.error(f"✗ {msg}")
						else:
							st.error(f"❌ No {trans_type} blood available at this hospital")
			else:
				st.info("Register hospitals first.")

			st.divider()
			st.markdown("#### 📝 Donation Records")
			if donors and hospitals:
				st.info("⚠️ System will automatically check 90-day eligibility. Donations from ineligible donors will be rejected unless overridden by admin.")
				with st.form("trial_donation_record_form"):
					col1, col2 = st.columns(2)
					with col1:
						donation_donor = st.selectbox("Donor", list(donor_map.keys()), key="trial_donation_donor", help="Select donor")
						donation_hosp = st.selectbox("Hospital", list(hosp_map.keys()), key="trial_donation_hosp", help="Collection facility")
					with col2:
						donation_date = st.date_input("Donation Date", help="When did donation occur?")
						donation_amount = st.number_input("Volume (ml)", min_value=50, step=50, value=450, help="Amount collected")
					
					allow_ineligible = st.checkbox("⚠️ Override eligibility check (admin only, logs to audit)", value=False, help="Use only in emergencies - requires justification")
					
					if st.form_submit_button("✓ Log Donation", type="primary", use_container_width=True):
						if not donation_date:
							st.error("Please select a donation date.")
						else:
							donor_id = donor_map[donation_donor]
							
							# Check eligibility
							is_eligible, eligibility_details = models.check_donor_eligibility(donor_id)
							
							if not is_eligible and not allow_ineligible:
								st.error(f"❌ Donor ineligible for donation. {eligibility_details.get('reason', 'Unknown reason')}")
								st.json(eligibility_details)
							elif not is_eligible and allow_ineligible:
								# Override with justification
								success, msg = models.override_donation_eligibility(
									donor_id=donor_id,
									override_reason=f"Emergency donation - {donation_amount}ml on {donation_date.strftime('%Y-%m-%d')}",
									staff_id=st.session_state.staff_id
								)
								if success:
									# Now log the donation
									success2, msg2 = models.record_donation_completed(donor_id, hosp_map[donation_hosp], donation_amount, donation_date.strftime("%Y-%m-%d"), st.session_state.username)
									if success2:
										st.success(f"✓ {msg2} (with override)")
										st.rerun()
									else:
										st.error(f"✗ Override succeeded but donation logging failed: {msg2}")
								else:
									st.error(f"✗ {msg}")
							else:
								# Eligible - proceed normally
								success, msg = models.record_donation_completed(donor_id, hosp_map[donation_hosp], donation_amount, donation_date.strftime("%Y-%m-%d"), st.session_state.username)
								if success:
									st.success(f"✓ {msg}")
									st.rerun()
								else:
									st.error(f"✗ {msg}")
			else:
				st.info("Register donors and hospitals first.")
		else:
			st.info("🔒 Blood operations are restricted to admins.")

	with bb_tabs[3]:
		st.markdown("#### 📊 Blood Inventory Summary")
		summary_rows = models.get_blood_bank_summary_by_type()
		if summary_rows:
			summary_data = []
			for s in summary_rows:
				summary_data.append({
					"🩸 Type": s[0],
					"📦 Units": s[1],
					"📊 Total (ml)": s[2],
					"🕐 Earliest": s[3] if len(s) > 3 else "N/A",
					"🕑 Latest": s[4] if len(s) > 4 else "N/A",
					"✓ Active": s[5] if len(s) > 5 else "Yes"
				})
			st.dataframe(summary_data, use_container_width=True, hide_index=True)
		else:
			st.info("No blood inventory available.")

		if st.session_state.role_id == 1:
			st.divider()
			st.markdown("#### 📈 Donor Eligibility Report")
			report_rows = models.get_donor_eligibility_report()
			if report_rows:
				report_data = []
				for r in report_rows:
					report_data.append({
						"👤 Name": r[1],
						"🩸 Blood": r[2],
						"📅 Last Donation": r[3] if len(r) > 3 else "Never",
						"✓ Status": r[4] if len(r) > 4 else "Eligible",
						"📊 Days Since": r[5] if len(r) > 5 else "N/A"
					})
				st.dataframe(report_data, use_container_width=True, hide_index=True)
			else:
				st.info("No donor data available.")

	st.markdown("</div>", unsafe_allow_html=True)


def section_donors():
	st.markdown("<div class='vf-card'>", unsafe_allow_html=True)
	st.markdown("<div class='vf-section-title'>👥 Donor Management</div>", unsafe_allow_html=True)
	st.markdown("<div class='vf-subtitle'>Register donors, track donations, and manage donor records.</div>", unsafe_allow_html=True)

	donor_tabs = st.tabs(["Donor Registry", "Register Donor", "Donation History", "Manage Records"])
	donors = models.get_all_donors() or []

	with donor_tabs[0]:
		st.markdown("#### 👥 Registered Donors")
		if donors:
			donor_data = []
			for d in donors:
				donor_data.append({
					"👤 Name": d[1],
					"🩸 Blood Type": d[2],
					"📞 Contact": d[3] if len(d) > 3 else "N/A",
					"ID": d[0]
				})
			st.dataframe(donor_data, use_container_width=True, hide_index=True)
		else:
			st.info("No donors registered yet.")
		st.divider()

	with donor_tabs[1]:
		st.markdown("#### ➕ Register New Donor")
		if st.session_state.role_id == 1:
			with st.form("trial_add_donor_form"):
				col1, col2 = st.columns(2)
				with col1:
					d_name = st.text_input("Full Name", key="trial_donor_name", placeholder="John Smith", help="Legal name of donor")
					d_blood = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], key="trial_donor_blood", help="Certified blood type")
				with col2:
					d_contact = st.text_input("Contact Info", key="trial_donor_contact", placeholder="+1 (555) 123-4567", help="Phone or email")
					if st.form_submit_button("✓ Register Donor", type="primary", use_container_width=True):
						if d_name:
							success, msg = models.add_donor(d_name, d_blood, d_contact, st.session_state.username)
							if success:
								st.success(f"✓ {msg}")
								st.rerun()
							else:
								st.error(f"✗ {msg}")
						else:
							st.warning("Name is required.")
		else:
			st.info("🔒 Donor registration is available to admins only.")

	with donor_tabs[2]:
		st.markdown("#### 📝 Donation History")
		hospitals = models.get_all_hospitals() or []
		hosp_map = {f"{h[1]} ({h[2]})": h[0] for h in hospitals}
		donor_map = {f"{d[1]} (Blood: {d[2]})": d[0] for d in donors}
		
		if donor_map and hosp_map:
			with st.form("trial_log_donation_form"):
				col1, col2 = st.columns(2)
				with col1:
					log_donor = st.selectbox("Donor", list(donor_map.keys()), key="trial_log_donor", help="Select donor")
					log_hosp = st.selectbox("Hospital", list(hosp_map.keys()), key="trial_log_hosp", help="Collection facility")
				with col2:
					log_date = st.date_input("Donation Date", help="When did donation occur?")
					log_amt = st.number_input("Volume (ml)", min_value=50, step=50, help="Donation amount in milliliters")
				if st.form_submit_button("✓ Log Donation", type="primary", use_container_width=True):
						if not log_date:
							st.error("Please select a donation date.")
						else:
							success, msg = models.add_donation_record(
								donor_map[log_donor],
								hosp_map[log_hosp],
								log_date.strftime("%Y-%m-%d"),
								log_amt,
								st.session_state.username,
							)
							if success:
								st.success(f"✓ {msg}")
								st.rerun()
							else:
								st.error(f"✗ {msg}")
		else:
			st.info("Add donors and hospitals first.")

	with donor_tabs[3]:
		st.markdown("#### 📊 Donor Management")
		st.info("Use the Donor Registry tab to view all registered donors and their information. Use Donation History to log new donations. All changes are automatically tracked in the system.")

	st.markdown("</div>", unsafe_allow_html=True)


def section_transfers():
	st.markdown("<div class='vf-card'>", unsafe_allow_html=True)
	st.markdown("<div class='vf-section-title'>🚚 Transfer Management</div>", unsafe_allow_html=True)
	st.markdown("<div class='vf-subtitle'>Request, track, and complete inter-facility supply transfers.</div>", unsafe_allow_html=True)

	transfer_tabs = st.tabs(["Open Requests", "Create Request", "Track Status", "Cancel Transfer"])
	hospitals = models.get_all_hospitals() or []
	items = models.get_all_items() or []
	hosp_map = {f"{h[1]} ({h[2]})": h[0] for h in hospitals}
	item_map = {f"{i[1]} ({i[2]})": i[0] for i in items}
	requests = models.get_all_transfer_requests() or []

	with transfer_tabs[0]:
		st.markdown("#### 📋 All Transfer Requests")
		if requests:
			request_data = []
			for r in requests:
				request_data.append({
					"🔢 Req ID": r[0],
					"📤 From": r[1] if len(r) > 1 else "N/A",
					"📥 To": r[2] if len(r) > 2 else "N/A",
					"📦 Item": r[3] if len(r) > 3 else "N/A",
					"📊 Quantity": r[4] if len(r) > 4 else "N/A"
				})
			st.dataframe(request_data, use_container_width=True, hide_index=True)
		else:
			st.info("No transfer requests yet.")
		st.divider()

	with transfer_tabs[1]:
		st.markdown("#### ➕ Create New Transfer Request")
		if st.session_state.role_id == 1:
			if hosp_map and item_map:
				with st.form("trial_create_transfer_form"):
					col1, col2 = st.columns(2)
					with col1:
						st.markdown("<b>Routing</b>", unsafe_allow_html=True)
						origin = st.selectbox("Origin Hospital", list(hosp_map.keys()), key="trial_transfer_origin", help="Sending facility")
						destination = st.selectbox("Destination Hospital", list(hosp_map.keys()), key="trial_transfer_destination", help="Receiving facility")
					with col2:
						st.markdown("<b>Item & Quantity</b>", unsafe_allow_html=True)
						item = st.selectbox("Equipment", list(item_map.keys()), key="trial_transfer_item", help="What to transfer")
						qty = st.number_input("Quantity to Transfer", min_value=1, step=1, help="How many units")
					if st.form_submit_button("✓ Create Request", type="primary", use_container_width=True):
							success, msg = models.create_transfer_request(hosp_map[origin], hosp_map[destination], item_map[item], qty, st.session_state.username)
							if success:
								st.success(f"✓ {msg}")
								st.rerun()
							else:
								st.error(f"✗ {msg}")
			else:
				st.info("Register hospitals and equipment first.")
		else:
			st.info("🔒 Transfer requests can only be created by admins.")

	with transfer_tabs[2]:
		st.markdown("#### 📊 Track Transfer Status")
		if st.session_state.role_id == 1:
			if requests:
				req_lookup = {f"Req #{row[0]} | Item {row[3]}": row[0] for row in requests}
				with st.form("trial_update_transfer_form"):
					col1, col2 = st.columns(2)
					with col1:
						selected_req = st.selectbox("Select Request", list(req_lookup.keys()), key="trial_update_req", help="Choose request to update")
					with col2:
						new_status = st.selectbox("New Status", ["Pending", "In Transit", "Delivered", "Cancelled"], key="trial_update_status", help="Update transfer status")
					if st.form_submit_button("✓ Update Status", type="primary", use_container_width=True):
							success, msg = models.add_transfer_status(req_lookup[selected_req], new_status, st.session_state.username)
							if success:
								st.success(f"✓ {msg}")
								st.rerun()
							else:
								st.error(f"✗ {msg}")
			else:
				st.info("No transfer requests to track.")
		else:
			st.info("🔒 Status updates are available to admins only.")

	with transfer_tabs[3]:
		st.markdown("#### ❌ Cancel Transfer Request")
		if st.session_state.role_id == 1:
			if requests:
				req_lookup = {f"Req #{row[0]} | Item {row[3]}": row[0] for row in requests}
				with st.form("trial_cancel_transfer_form"):
					selected_req = st.selectbox("Select Request to Cancel", list(req_lookup.keys()), key="trial_cancel_req", help="Choose request to cancel")
					confirm = st.checkbox("I confirm this cancellation cannot be undone", help="This action is permanent")
					if st.form_submit_button("🗑️ Cancel Request", type="primary", use_container_width=True):
						if confirm:
									success, msg = models.delete_transfer_request(req_lookup[selected_req], st.session_state.username)
									if success:
										st.success(f"✓ {msg}")
										st.rerun()
									else:
										st.error(f"✗ {msg}")
						else:
							st.error("Please confirm cancellation")
			else:
				st.info("No transfers available to cancel.")
		else:
			st.info("🔒 Cancellations can only be performed by admins.")

	st.markdown("</div>", unsafe_allow_html=True)


def section_admin():
	st.markdown("<div class='vf-card'>", unsafe_allow_html=True)
	st.markdown("<div class='vf-section-title'>⚙️ Administration</div>", unsafe_allow_html=True)
	st.markdown("<div class='vf-subtitle'>User management, permissions, and system control.</div>", unsafe_allow_html=True)

	if st.session_state.role_id != 1:
		st.error("🔒 Access Denied: Administrator privileges required.")
		st.markdown("</div>", unsafe_allow_html=True)
		return

	admin_tabs = st.tabs(["Activity Logs", "Add Staff", "Manage Staff"])
	hospitals = models.get_all_hospitals() or []
	hosp_map = {f"{h[1]} ({h[2]})": h[0] for h in hospitals}

	with admin_tabs[0]:
		st.markdown("#### 📋 System Activity Log")
		logs = models.get_all_logs(limit=100) or []
		if logs:
			log_data = []
			for log in logs:
				log_data.append({
					"👤 Staff": log[1] if len(log) > 1 else "N/A",
					"🎯 Action": log[2] if len(log) > 2 else "N/A",
					"📊 Table": log[3] if len(log) > 3 else "N/A",
					"⏰ Timestamp": log[4] if len(log) > 4 else "N/A"
				})
			st.dataframe(log_data, use_container_width=True, hide_index=True)
		else:
			st.info("No activity logs recorded yet.")
		st.divider()

	with admin_tabs[1]:
		st.markdown("#### ➕ Create Staff Account")
		with st.form("trial_add_staff_form"):
			col1, col2 = st.columns(2)
			with col1:
				st.markdown("<b>Credentials</b>", unsafe_allow_html=True)
				new_user = st.text_input("Username", placeholder="john.smith", help="Unique login username")
				new_pass = st.text_input("Password", type="password", placeholder="••••••••", help="Secure password")
			with col2:
				st.markdown("<b>Assignment</b>", unsafe_allow_html=True)
				new_role = st.selectbox("Role", ["1 - System Admin", "2 - Medical Staff"], help="User permission level")
				new_hosp = st.selectbox("Hospital Assignment", ["Global System"] + list(hosp_map.keys()), help="Primary facility or system-wide")
			if st.form_submit_button("✓ Create Account", type="primary", use_container_width=True):
				hosp_id = None if new_hosp == "Global System" else hosp_map[new_hosp]
				role_id = 1 if new_role.startswith("1") else 2
				success, msg = models.add_staff(new_user, new_pass, role_id, hosp_id, st.session_state.username)
				if success:
					st.success(f"✓ {msg}")
					st.rerun()
				else:
					st.error(f"✗ {msg}")

	with admin_tabs[2]:
		st.markdown("#### 👥 Staff Directory")
		staff_list = models.get_all_staff() or []
		if staff_list:
			staff_data = []
			for staff in staff_list:
				role_name = "System Admin" if staff[2] == 1 else "Medical Staff" if staff[2] == 2 else "Unknown"
				staff_data.append({
					"👤 Username": staff[1],
					"🎯 Role": role_name,
					"🏥 Hospital": staff[3] if len(staff) > 3 else "Global",
					"ID": staff[0]
				})
			st.dataframe(staff_data, use_container_width=True, hide_index=True)
		else:
			st.info("No staff records found.")

	st.markdown("</div>", unsafe_allow_html=True)


def section_analytics():
	st.markdown("<div class='vf-card'>", unsafe_allow_html=True)
	st.markdown("<div class='vf-section-title'>📊 Analytics & Reports</div>", unsafe_allow_html=True)
	st.markdown("<div class='vf-subtitle'>System insights, trends, and comprehensive reporting.</div>", unsafe_allow_html=True)

	report_tabs = st.tabs(["Staff", "Inventory", "Donations", "Transfers", "Audit", "Blood Bank", "Operations"])

	with report_tabs[0]:
		st.markdown("#### 👥 Staff Report")
		data = models.get_staff_report() or []
		if data:
			st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
		else:
			st.info("No staff data available.")

	with report_tabs[1]:
		st.markdown("#### 📦 Inventory Report")
		data = models.get_inventory_report() or []
		if data:
			st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
		else:
			st.info("No inventory data available.")

	with report_tabs[2]:
		st.markdown("#### 🩸 Donation Report")
		data = models.get_donation_report() or []
		if data:
			st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
		else:
			st.info("No donation data available.")

	with report_tabs[3]:
		st.markdown("#### 🚚 Transfer History")
		data = models.get_full_transfer_history() or []
		if data:
			st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
		else:
			st.info("No transfer history available.")

	with report_tabs[4]:
		st.markdown("#### 🔍 Audit Trail")
		data = models.get_deep_audit_report() or []
		if data:
			st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
		else:
			st.info("No audit data available.")

	with report_tabs[5]:
		st.markdown("#### 🩸 Blood Bank Summary")
		data = models.get_blood_bank_summary_by_type() or []
		if data:
			blood_summary = []
			for row in data:
				blood_summary.append({
					"🩸 Type": row[0],
					"📦 Units": row[1],
					"📊 Volume (ml)": row[2],
					"🕐 Earliest": row[3] if len(row) > 3 else "N/A",
					"🕑 Latest": row[4] if len(row) > 4 else "N/A",
					"✓ Status": row[5] if len(row) > 5 else "Active"
				})
			st.dataframe(blood_summary, use_container_width=True, hide_index=True)
		else:
			st.info("No blood bank data available.")

	with report_tabs[6]:
		st.markdown("#### 📈 Operational Impact")
		data = models.get_logistics_impact() or []
		if data:
			st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
		else:
			st.info("No operational data available.")

	st.markdown("</div>", unsafe_allow_html=True)


def card(title, value, border_color, note=None, value_color="#0f1724"):
	"""Helper function to draw clinical KPI cards"""
	note_html = f"<p style='font-size:0.85rem; color:#6b7280; margin:0; font-weight:700;'>{note}</p>" if note else ""
	st.markdown(f"""
	<div style='background: white; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 8px solid {border_color}; padding: 1.25rem; box-shadow: 0 4px 10px rgba(15, 23, 42, 0.05); height: 100%;'>
		<p style='font-size:0.85rem; font-weight:800; color:#64748b; text-transform:uppercase; margin:0 0 0.5rem 0;'>{title}</p>
		<h3 style='font-size:2.2rem; font-weight:800; color:{value_color}; margin:0 0 0.25rem 0;'>{value}</h3>
		{note_html}
	</div>
	""", unsafe_allow_html=True)


def dashboard():
	st.markdown("<div class='vf-card'>", unsafe_allow_html=True)
	st.markdown("<div class='vf-section-title'>Network Overview</div>", unsafe_allow_html=True)
	st.markdown(
		"<div class='vf-subtitle'>A quick operational snapshot for facilities, blood stock, transfers, and donor activity.</div>",
		unsafe_allow_html=True,
	)
	st.markdown(
		"""
		<div style='background:#f8fbff; border:1px solid #dbe7f5; border-radius:14px; padding:0.85rem 1rem; margin-bottom:1rem; display:flex; flex-wrap:wrap; gap:0.75rem; align-items:center;'>
			<span style='background:#004d99; color:white; padding:0.35rem 0.7rem; border-radius:999px; font-size:0.78rem; font-weight:800;'>Live Snapshot</span>
			<span style='color:#475467; font-weight:600;'>Operational data updates from the database in real time.</span>
		</div>
		""",
		unsafe_allow_html=True,
	)

	hospitals = models.get_all_hospitals() or []
	donors = models.get_all_donors() or []
	transfers = models.get_all_transfer_requests() or []
	logs = models.get_all_logs(limit=10) or []
	blood_summary = models.get_blood_bank_summary_by_type() or []

	blood_type = "O- (Low)"
	blood_note = "-15 Units needed"
	for row in blood_summary:
		if str(row[0]).strip().upper() == "O-":
			units = int(row[1]) if row[1] is not None else 0
			blood_type = f"O- ({'Low' if units < 20 else 'Stable'})"
			blood_note = f"{max(0, 20 - units)} Units needed"
			break

	c1, c2, c3, c4 = st.columns(4)
	with c1:
		card("Total Facilities", str(len(hospitals)), "#004d99")
	with c2:
		card("Critical Stock", blood_type, "#cc0000", note=blood_note, value_color="#cc0000")
	with c3:
		card("Active Transfers", str(len(transfers)), "#2eb82e")
	with c4:
		card("Registered Donors", f"{len(donors):,}", "#6f42c1")

	st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
	left, right = st.columns([1.6, 1])
	with left:
		st.markdown("<h3 style='color:#004d99; margin-bottom:1rem; font-size:1.4rem; font-weight:700;'>Recent Network Activity</h3>", unsafe_allow_html=True)
		if logs:
			activity_df = pd.DataFrame(logs, columns=["Log ID", "User", "Action", "Table", "Timestamp"])
			st.dataframe(activity_df, use_container_width=True, hide_index=True)
		else:
			st.info("No activity logs recorded yet.")
	with right:
		st.markdown("<div class='vf-card' style='height:100%;'>", unsafe_allow_html=True)
		st.markdown("<div class='vf-section-title' style='font-size:1.3rem; margin-bottom:1rem; padding-bottom:0.75rem;'>📊 Quick Summary</div>", unsafe_allow_html=True)
		st.markdown(f"<p style='font-size:1.05rem; margin:0.75rem 0; font-weight:600;'>🏥 <strong>Facilities:</strong> {len(hospitals)}</p>", unsafe_allow_html=True)
		st.markdown(f"<p style='font-size:1.05rem; margin:0.75rem 0; font-weight:600;'>🚚 <strong>Active Transfers:</strong> {len(transfers)}</p>", unsafe_allow_html=True)
		st.markdown(f"<p style='font-size:1.05rem; margin:0.75rem 0; font-weight:600;'>👥 <strong>Registered Donors:</strong> {len(donors)}</p>", unsafe_allow_html=True)
		st.markdown(f"<p style='font-size:1.05rem; margin:0.75rem 0; font-weight:600;'>📝 <strong>Latest Logs:</strong> {len(logs)}</p>", unsafe_allow_html=True)
		st.write("\n")
		st.markdown(
			"<div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:1rem; color:#475467; font-size:1rem; line-height:1.5;'>"
			"💡 Use this panel for charts, network notes, or operations summary."
			"</div>",
			unsafe_allow_html=True,
		)
		st.markdown("</div>", unsafe_allow_html=True)

	st.markdown("</div>", unsafe_allow_html=True)


if require_login():
	top_header()

	# Added Logout Button right below the header, above tabs
	colA, colB = st.columns([8, 1])
	with colB:
		if st.button("🔒 Secure Logout", use_container_width=True):
			st.session_state.logged_in = False
			st.rerun()

	tabs = st.tabs([
		"Dashboard",
		"Hospitals",
		"Inventory",
		"Blood Bank",
		"Donors",
		"Transfers",
		"Admin",
		"Analytics",
	])

	with tabs[0]:
		dashboard()
	with tabs[1]:
		section_hospitals()
	with tabs[2]:
		section_inventory()
	with tabs[3]:
		section_blood_bank()
	with tabs[4]:
		section_donors()
	with tabs[5]:
		section_transfers()
	with tabs[6]:
		section_admin()
	with tabs[7]:
		section_analytics()

	st.markdown(
		f"<div style='text-align:center; color:gray; font-size:12px; margin-top: 2rem;'>VitalFlow Secure UI • {datetime.now().strftime('%Y-%m-%d')}</div>",
		unsafe_allow_html=True,
	)
