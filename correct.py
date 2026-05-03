# Open the file we made in the last step
with open('final_supabase_data.sql', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# This is the STRICT relational hierarchy order. 
# Parents must be inserted before children.
ordered_tables = [
    'roles', 
    'hospitals', 
    'inventory_items', 
    'donors', 
    'staff', 
    'hospital_inventory', 
    'donation_records', 
    'transfer_requests', 
    'transfer_status', 
    'audit_logs'
]

# Create a dictionary to hold the lines for each table
sorted_data = {table: [] for table in ordered_tables}

# Sort every INSERT statement into the correct bucket
for line in lines:
    if line.startswith('INSERT INTO'):
        for table in ordered_tables:
            # Match the table name exactly
            if f'INSERT INTO {table} ' in line:
                sorted_data[table].append(line)
                break

# Write them out in the perfect order
with open('perfect_supabase_data.sql', 'w', encoding='utf-8') as f:
    for table in ordered_tables:
        if sorted_data[table]:
            f.write(f"-- Inserting data for {table.upper()}\n")
            f.writelines(sorted_data[table])
            f.write('\n')

print("✅ Success! Your data is strictly ordered in 'perfect_supabase_data.sql'")