import sqlite3
import json
import os

DB_FILE = "project_tracker.db"
JSON_FILE = "projects.json"

def create_schema(conn):
    cursor = conn.cursor()
    
    # Projects Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        name TEXT,
        type TEXT
    )
    ''')
    
    # Modules Table (supports sub-modules via parent_module_id)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS modules (
        id INTEGER PRIMARY KEY,
        project_id INTEGER,
        name TEXT,
        parent_module_id INTEGER,
        FOREIGN KEY(project_id) REFERENCES projects(id),
        FOREIGN KEY(parent_module_id) REFERENCES modules(id)
    )
    ''')
    
    # Gateways Table
    # Entity Type: 'project', 'module' (we treat sub-module as module here, just ID reference)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gateways (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT,
        entity_id INTEGER,
        gateway TEXT,
        plan_date TEXT,
        actual_date TEXT,
        ecn TEXT
    )
    ''')
    
    conn.commit()

def migrate_data(conn):
    if not os.path.exists(JSON_FILE):
        print("No JSON file found to migrate.")
        return

    with open(JSON_FILE, 'r') as f:
        projects = json.load(f)
        
    cursor = conn.cursor()
    
    for p in projects:
        print(f"Migrating Project: {p['name']}")
        cursor.execute("INSERT OR REPLACE INTO projects (id, name, type) VALUES (?, ?, ?)", 
                       (p['id'], p['name'], p.get('type', '')))
        
        # Project Gateways
        for gw, date in p.get('gateways', {}).items():
            if date:
                cursor.execute("INSERT INTO gateways (entity_type, entity_id, gateway, plan_date) VALUES (?, ?, ?, ?)",
                               ('project', p['id'], gw, date))
        
        # Modules
        if 'modules' in p:
            for m in p['modules']:
                print(f"  - Module: {m['name']}")
                cursor.execute("INSERT OR REPLACE INTO modules (id, project_id, name) VALUES (?, ?, ?)",
                               (m['id'], p['id'], m['name']))
                
                # Module Gateways
                for gw, data in m.get('gateways', {}).items():
                    # Check if data is dict (v3 standard) or just date (legacy check)
                    if isinstance(data, dict):
                        cursor.execute("INSERT INTO gateways (entity_type, entity_id, gateway, plan_date, actual_date, ecn) VALUES (?, ?, ?, ?, ?, ?)",
                                       ('module', m['id'], gw, data.get('p', ''), data.get('a', ''), data.get('ecn', '')))
                
                # Sub-Modules
                if 'sub_modules' in m:
                    for s in m['sub_modules']:
                        print(f"    - Sub-Module: {s['name']}")
                        cursor.execute("INSERT OR REPLACE INTO modules (id, project_id, name, parent_module_id) VALUES (?, ?, ?, ?)",
                                       (s['id'], p['id'], s['name'], m['id']))
                        
                        # Sub-Module Gateways
                        for gw, data in s.get('gateways', {}).items():
                            if isinstance(data, dict):
                                cursor.execute("INSERT INTO gateways (entity_type, entity_id, gateway, plan_date, actual_date, ecn) VALUES (?, ?, ?, ?, ?, ?)",
                                               ('module', s['id'], gw, data.get('p', ''), data.get('a', ''), data.get('ecn', '')))

    conn.commit()
    print("Migration Complete.")

if __name__ == "__main__":
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE) # Clean start for baseline
    
    conn = sqlite3.connect(DB_FILE)
    create_schema(conn)
    migrate_data(conn)
    conn.close()
