import sqlite3

# Name of your local database file
db_file = 'VitalFlow.db'
# Name of the output file
output_file = 'data_dump.sql'

def dump_sqlite():
    try:
        conn = sqlite3.connect(db_file)
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in conn.iterdump():
                f.write('%s\n' % line)
        print(f"✅ Success! Your data has been exported to {output_file}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    dump_sqlite()