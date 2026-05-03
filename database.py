import sqlite3

def get_db_connection():
    # Connects to your existing vitalflow.db file
    conn = sqlite3.connect('vitalflow.db')
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    
    # 🚨 SECURITY FIX: Enforce Foreign Key Constraints & Cascades
    conn.execute('PRAGMA foreign_keys = ON;') 
    
    return conn

# Let's test the connection immediately
if __name__ == '__main__':
    conn = get_db_connection()
    print("Database connection successful with Foreign Keys enforced!")
    conn.close()