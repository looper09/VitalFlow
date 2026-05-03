import sqlite3
import os

def build_database():
    print("Building VitalFlow tables...")
    
    # This guarantees the file is created exactly where VS Code is looking
    conn = sqlite3.connect('vitalflow.db')
    
    # Open your schema file and run it
    with open('schema.sql', 'r') as sql_file:
        sql_script = sql_file.read()
        conn.executescript(sql_script)
        
    conn.close()
    print("✅ Tables created successfully in the correct folder!")

if __name__ == '__main__':
    build_database()