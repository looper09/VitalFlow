from database import get_connection

def test_local_connection():
    # This will call the function from your updated database.py
    conn = get_connection()
    
    if conn:
        try:
            # Let's try to grab just one hospital name to prove it works
            cursor = conn.cursor()
            cursor.execute("SELECT Name FROM Hospitals LIMIT 1")
            hospital_name = cursor.fetchone()[0]
            
            print("✅ SUCCESS: Connected to Local SQLite Database!")
            print(f"🏥 Found Hospital: {hospital_name}")
            
        except Exception as e:
            print(f"❌ ERROR reading data: {e}")
        finally:
            conn.close()
    else:
        print("❌ CRITICAL ERROR: Could not get a connection.")

if __name__ == '__main__':
    test_local_connection()