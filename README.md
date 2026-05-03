# 🩺 VitalFlow Secure Medical Network

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

VitalFlow is a healthcare logistics and blood bank management system. It's built to help a network of hospitals keep track of their medical supplies, manage regional blood donations, and handle emergency resource transfers safely and efficiently.

---

## ✨ Core Features

* **🛡️ Role-Based Access:** The system shows different dashboards and tools depending on who is logged in (System Admins get a full network view, while Medical Staff only manage their specific hospital).
* **🔒 Automatic Audit Trails:** Everything that happens in the system is logged automatically. There is always a clear, timestamped record of who made what changes.
* **📦 Live Logistics Tracking:** Securely handles transferring inventory between hospitals, with built-in safeguards to make sure items don't accidentally disappear from the system if a transfer fails.
* **🩸 Blood Bank Management:** Keeps track of registered donors, blood types, and exactly how much blood is available at each specific hospital warehouse.
* **📊 Network Analytics:** Provides clear, big-picture reports so admins can easily visualize overall network health, total inventory levels, and logistics history.

## 🏗️ Architecture & Database Integrity

The backend is powered by a reliable SQLite database designed to keep data accurate and prevent user errors:
* **Strict Data Rules:** The database is set up to reject invalid data, like negative inventory numbers or non-standard blood types.
* **Linked Records:** The database enforces relationships between tables, so deleting or updating a record safely handles any connected data automatically.
* **Clean User Interface:** Users select easy-to-read names from dropdown menus instead of dealing with raw database IDs. This makes the app much easier to use while keeping the backend data perfectly organized.

---

## 🚀 Local Installation & Setup

### 1. Prerequisites
Ensure you have Python installed. Clone the repository and install the required packages:

```bash
git clone https://github.com/yourusername/vitalflow.git
cd vitalflow
pip install -r requirements.txt
```

### 2. Initialize the Database
Build the database tables:

```bash
python setup.py
```

### 3. Seed the Network Data
Populate the database with realistic medical records:

```bash
python seed.py
```

### 4. Launch the Application
Start the Streamlit dashboard:

```bash
streamlit run gui_app.py
```

---

## 🐳 Docker Deployment (Recommended)

VitalFlow is fully containerized. You can deploy the entire app instantly using Docker.

**1. Build the Docker Image:**

```bash
docker build -t vitalflow-app .
```

**2. Run the Container:**

```bash
docker run -p 8501:8501 vitalflow-app
```
Access the application locally at: `http://localhost:8501`

---

## 🔐 Default Login Credentials

If you ran the `seed.py` file, you can test the different access levels using these accounts:

| Role | Username | Password | Features Unlocked |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `asad_admin` | `pass123` | Full System Access, Advanced Reports, Security Audits |
| **Medical Staff** | `dr_abdullah` | `pass123` | View Global Catalog, Request Transfers, Log Usage |

---

## 🎓 Academic Highlights (For Grading / Code Review)

If you are reviewing this code for a grade, here are a few specific things to look out for:
* **`models.py`:** Check out the `execute_query()` function for how the automatic audit logs work, and `add_transfer_status` for how it handles inventory rollbacks safely.
* **`gui_app.py`:** Look at how the dropdown menus map readable text (like hospital names) to database IDs to keep the user interface clean and intuitive.
* **`schema.sql`:** You'll find the strict database constraints and `CASCADE` rules here that keep the data secure.
* **Advanced Reports (GUI Tab 7):** This section runs the relational SQL queries to generate network-wide summaries.

---
*Built for the H-11 Campus Final Defense.*
