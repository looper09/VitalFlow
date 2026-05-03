import sqlite3
import psycopg2
import streamlit as st
import os

def get_db_connection():
    """
    Returns a connection to either the Supabase PostgreSQL database
    (if running on Streamlit Cloud) or the local SQLite database 
    (if running on your laptop in VS Code).
    """
    
    # 1. CLOUD MODE (Safely check for Streamlit Secrets)
    try:
        if "DB_URL" in st.secrets:
            return psycopg2.connect(st.secrets["DB_URL"])
    except Exception:
        # If st.secrets throws an error locally, we just pass and move to Step 2
        pass

    # 2. LOCAL MODE (Defaults to SQLite for your VS Code)
    try:
        # Assumes VitalFlow.db is in the same folder as this script
        db_path = os.path.join(os.path.dirname(__file__), 'VitalFlow.db')
        conn = sqlite3.connect(db_path)
        
        # Enforce Foreign Key Constraints for the local SQLite file
        conn.execute('PRAGMA foreign_keys = ON;') 
        
        return conn
    except Exception as e:
        print(f"Failed to connect to Local DB: {e}")
        return None

# Quick test if you run this file directly
if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        print("Database connection successful!")
        conn.close()
    else:
        print("Database connection failed.")