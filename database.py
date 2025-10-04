"""
Database module for Gold Jewelry Business Management System
Handles all database operations and table creation
"""

import sqlite3
import os
import shutil
import csv
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='gold_jewelry.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database and create tables"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print("Database connected successfully")
            
            # Test database connection
            self.cursor.execute("SELECT 1")
            test_result = self.cursor.fetchone()
            print(f"Database test query result: {test_result}")
            
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise e
        
        # Create tables
        self.create_tables()
        
        # Migrate existing data if needed
        self.migrate_database()
        
        # Insert default data
        self.insert_default_data()
        
        # Commit all changes
        self.conn.commit()
        print("Database initialization completed successfully")
    
    def create_tables(self):
        """Create all database tables"""
        # Gold Types table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS gold_types (
                gold_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                purity_percentage REAL NOT NULL,
                description TEXT
            )
        ''')
        
        # Gold Inventory table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS gold_inventory (
                inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                gold_type_id INTEGER,
                weight_grams REAL NOT NULL,
                purity_percentage REAL NOT NULL,
                form TEXT NOT NULL,
                description TEXT,
                received_date TEXT NOT NULL,
                supplier_info TEXT,
                FOREIGN KEY (gold_type_id) REFERENCES gold_types (gold_type_id)
            )
        ''')
        
        # Check if is_available column exists and drop it if it does
        self.cursor.execute("PRAGMA table_info(gold_inventory)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'is_available' in columns:
            # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
            self.cursor.execute('''
                CREATE TABLE gold_inventory_new (
                    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gold_type_id INTEGER,
                    weight_grams REAL NOT NULL,
                    purity_percentage REAL NOT NULL,
                    form TEXT NOT NULL,
                    description TEXT,
                    received_date TEXT NOT NULL,
                    supplier_info TEXT,
                    FOREIGN KEY (gold_type_id) REFERENCES gold_types (gold_type_id)
                )
            ''')
            
            # Copy data from old table to new table (excluding is_available column)
            self.cursor.execute('''
                INSERT INTO gold_inventory_new 
                (inventory_id, gold_type_id, weight_grams, purity_percentage, form, description, received_date, supplier_info)
                SELECT inventory_id, gold_type_id, weight_grams, purity_percentage, form, description, received_date, supplier_info
                FROM gold_inventory
            ''')
            
            # Drop old table and rename new table
            self.cursor.execute('DROP TABLE gold_inventory')
            self.cursor.execute('ALTER TABLE gold_inventory_new RENAME TO gold_inventory')
        
        # Freelancers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS freelancers (
                freelancer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                specialization TEXT,
                phone TEXT,
                address TEXT,
                bank_details TEXT,
                joined_date TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Designs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS designs (
                design_id INTEGER PRIMARY KEY AUTOINCREMENT,
                design_name TEXT NOT NULL,
                design_code TEXT UNIQUE,
                category TEXT NOT NULL,
                complexity_level TEXT NOT NULL,
                estimated_gold_weight REAL NOT NULL,
                design_specifications TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Work Orders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_orders (
                work_order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                freelancer_id INTEGER,
                gold_type_id INTEGER,
                jewelry_design TEXT NOT NULL,
                original_metal_weight REAL NOT NULL,
                gold_weight_issued REAL NOT NULL,
                expected_final_weight REAL NOT NULL,
                issue_date TEXT NOT NULL,
                expected_completion_date TEXT,
                status TEXT DEFAULT 'issued',
                special_instructions TEXT,
                wastage_weight REAL DEFAULT 0,
                final_jewelry_weight REAL DEFAULT 0,
                completion_date TEXT,
                notes TEXT,
                FOREIGN KEY (freelancer_id) REFERENCES freelancers (freelancer_id),
                FOREIGN KEY (gold_type_id) REFERENCES gold_types (gold_type_id)
            )
        ''')
        
        # Check if original_metal_weight column exists and add it if it doesn't
        self.cursor.execute("PRAGMA table_info(work_orders)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'original_metal_weight' not in columns:
            # Add the new column to existing table
            self.cursor.execute('ALTER TABLE work_orders ADD COLUMN original_metal_weight REAL DEFAULT 0')
            print("Added original_metal_weight column to work_orders table")
        
        # Suppliers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                gst_number TEXT,
                is_active BOOLEAN DEFAULT 1,
                balance REAL DEFAULT 0.0
            )
        ''')
        
        # Gold Purchases table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS gold_purchases (
                purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                gold_type_id INTEGER,
                weight_grams REAL NOT NULL,
                purity_percentage REAL NOT NULL,
                purchase_date TEXT NOT NULL,
                invoice_number TEXT,
                notes TEXT,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id),
                FOREIGN KEY (gold_type_id) REFERENCES gold_types (gold_type_id)
            )
        ''')
        
        # Raini Orders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS raini_orders (
                raini_id INTEGER PRIMARY KEY AUTOINCREMENT,
                purity_percentage REAL NOT NULL,
                pure_gold_weight REAL NOT NULL,
                impurities_weight REAL NOT NULL,
                total_weight REAL NOT NULL,
                created_date TEXT NOT NULL,
                status TEXT DEFAULT 'Active',
                notes TEXT
            )
        ''')
        
        # Check if copper_percentage column exists and add it if it doesn't
        self.cursor.execute("PRAGMA table_info(raini_orders)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        if 'copper_percentage' not in columns:
            print("Adding copper and silver columns to raini_orders table...")
            self.cursor.execute('ALTER TABLE raini_orders ADD COLUMN copper_percentage REAL DEFAULT 0')
            self.cursor.execute('ALTER TABLE raini_orders ADD COLUMN copper_weight REAL DEFAULT 0')
            self.cursor.execute('ALTER TABLE raini_orders ADD COLUMN silver_percentage REAL DEFAULT 0')
            self.cursor.execute('ALTER TABLE raini_orders ADD COLUMN silver_weight REAL DEFAULT 0')
            print("Successfully added copper and silver columns")
        
        # Check if actual_weight column exists and add it if it doesn't
        self.cursor.execute("PRAGMA table_info(raini_orders)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        if 'actual_weight' not in columns:
            print("Adding actual_weight column to raini_orders table...")
            self.cursor.execute('ALTER TABLE raini_orders ADD COLUMN actual_weight REAL DEFAULT 0')
            print("Successfully added actual_weight column")
        
        # Check and add inventory columns to items table
        try:
            # Check if items table exists and get its columns
            self.cursor.execute("PRAGMA table_info(items)")
            items_columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'fine_weight' not in items_columns:
                print("Adding fine_weight column to items table...")
                self.cursor.execute('ALTER TABLE items ADD COLUMN fine_weight REAL DEFAULT 0.0')
                print("Successfully added fine_weight column to items")
            
            if 'net_weight' not in items_columns:
                print("Adding net_weight column to items table...")
                self.cursor.execute('ALTER TABLE items ADD COLUMN net_weight REAL DEFAULT 0.0')
                print("Successfully added net_weight column to items")
        except sqlite3.OperationalError as e:
            print(f"Error checking items table columns: {e}")
        
        # Check and add balance column to suppliers table
        try:
            # Check if suppliers table exists and get its columns
            self.cursor.execute("PRAGMA table_info(suppliers)")
            suppliers_columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'balance' not in suppliers_columns:
                print("Adding balance column to suppliers table...")
                self.cursor.execute('ALTER TABLE suppliers ADD COLUMN balance REAL DEFAULT 0.0')
                print("Successfully added balance column to suppliers")
        except sqlite3.OperationalError as e:
            print(f"Error checking suppliers table columns: {e}")
        
        # Add gold price per gram setting (global setting)
        try:
            # Check if settings table exists
            self.cursor.execute("PRAGMA table_info(settings)")
            settings_columns = [column[1] for column in self.cursor.fetchall()]
            
            if not settings_columns:  # Table doesn't exist
                print("Creating settings table...")
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        setting_key TEXT PRIMARY KEY,
                        setting_value TEXT
                    )
                ''')
                print("Settings table created")
            
            # Check if gold_price_per_gram setting exists
            self.cursor.execute("SELECT setting_value FROM settings WHERE setting_key = 'gold_price_per_gram'")
            if not self.cursor.fetchone():
                print("Adding default gold price per gram setting...")
                self.cursor.execute("INSERT INTO settings (setting_key, setting_value) VALUES ('gold_price_per_gram', '5000')")
                print("Default gold price set to ₹5000 per gram")
        except sqlite3.OperationalError as e:
            print(f"Error setting up gold price: {e}")
        
        # Items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                item_code TEXT UNIQUE,
                description TEXT,
                category TEXT,
                is_active BOOLEAN DEFAULT 1,
                fine_weight REAL DEFAULT 0.0,
                net_weight REAL DEFAULT 0.0,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sales table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ref_id TEXT NOT NULL,
                supplier_name TEXT NOT NULL,
                item_id INTEGER,
                gross_weight REAL NOT NULL,
                less_weight REAL NOT NULL,
                net_weight REAL NOT NULL,
                tunch_percentage REAL NOT NULL,
                wastage_percentage REAL NOT NULL,
                fine_gold REAL NOT NULL,
                sale_date TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (item_id) REFERENCES items (item_id)
            )
        ''')
        
    def migrate_database(self):
        """Migrate existing database schema if needed"""
        try:
            # Check if ref_id column has UNIQUE constraint
            cursor = self.cursor.execute("PRAGMA table_info(sales)")
            columns = cursor.fetchall()
            
            # Check if we need to recreate the sales table to remove UNIQUE constraint
            cursor = self.cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='sales'")
            table_sql = cursor.fetchone()
            
            if table_sql and 'ref_id TEXT UNIQUE' in table_sql[0]:
                print("Migrating sales table to remove UNIQUE constraint from ref_id...")
                
                # Create new table without UNIQUE constraint
                self.cursor.execute('''
                    CREATE TABLE sales_new (
                        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ref_id TEXT NOT NULL,
                        supplier_name TEXT NOT NULL,
                        item_id INTEGER,
                        gross_weight REAL NOT NULL,
                        less_weight REAL NOT NULL,
                        net_weight REAL NOT NULL,
                        tunch_percentage REAL NOT NULL,
                        wastage_percentage REAL NOT NULL,
                        fine_gold REAL NOT NULL,
                        sale_date TEXT NOT NULL,
                        notes TEXT,
                        FOREIGN KEY (item_id) REFERENCES items (item_id)
                    )
                ''')
                
                # Copy data from old table to new table
                self.cursor.execute('''
                    INSERT INTO sales_new 
                    SELECT * FROM sales
                ''')
                
                # Drop old table
                self.cursor.execute('DROP TABLE sales')
                
                # Rename new table
                self.cursor.execute('ALTER TABLE sales_new RENAME TO sales')
                
                print("Sales table migration completed successfully")
                
        except Exception as e:
            print(f"Database migration error: {e}")
            # Continue execution even if migration fails
    
    def insert_default_data(self):
        """Insert default data into tables"""
        # Insert default gold types if not exists
        self.cursor.execute('''
            INSERT OR IGNORE INTO gold_types (name, purity_percentage, description)
            VALUES 
                ('24K', 99.9, 'Pure gold'),
                ('22K', 91.7, '22 karat gold'),
                ('18K', 75.0, '18 karat gold'),
                ('14K', 58.3, '14 karat gold')
        ''')
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            raise e
    
    def execute_update(self, query, params=None):
        """Execute an update query"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.rowcount
        except sqlite3.Error as e:
            print(f"Update execution error: {e}")
            self.conn.rollback()
            raise e
    
    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")

    # -------------------------
    # Backup/Restore/Export APIs
    # -------------------------
    def get_db_path(self):
        """Return the absolute path to the SQLite database file."""
        try:
            return os.path.abspath(self.db_path)
        except Exception:
            return self.db_path

    def backup_to(self, dest_file_path: str) -> str:
        """Create a copy of the database file at dest_file_path. Returns the path written."""
        if not dest_file_path:
            raise ValueError("Destination path not provided")
        # Ensure directory exists
        os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
        # Ensure all writes are flushed
        try:
            self.conn.commit()
        except Exception:
            pass
        src = self.get_db_path()
        shutil.copy2(src, dest_file_path)
        print(f"Database backed up to: {dest_file_path}")
        return dest_file_path

    def restore_from(self, source_file_path: str) -> None:
        """Restore database from source_file_path. Closes and reopens the connection."""
        if not source_file_path or not os.path.exists(source_file_path):
            raise FileNotFoundError("Backup file not found")
        # Close current connection
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
        # Replace the db file
        dest = self.get_db_path()
        os.makedirs(os.path.dirname(dest) or '.', exist_ok=True)
        shutil.copy2(source_file_path, dest)
        # Reopen
        self.init_database()
        print(f"Database restored from: {source_file_path}")

    def table_exists(self, table_name: str) -> bool:
        row = self.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return bool(row)

    def export_table_to_csv(self, table_name: str, csv_file_path: str) -> str:
        """Export a single table to CSV. Returns the file path written."""
        if not self.table_exists(table_name):
            print(f"Table '{table_name}' does not exist, skipping export")
            return ''
        # Fetch column names
        cols = self.execute_query(f"PRAGMA table_info({table_name})")
        headers = [c[1] for c in cols]
        rows = self.execute_query(f"SELECT * FROM {table_name}")
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"Exported table '{table_name}' to {csv_file_path}")
        return csv_file_path

    def export_supplier_ledger_csv(self, csv_file_path: str) -> str:
        """Export a derived supplier ledger: +fine_gold for Sales, -fine_gold for Purchases."""
        parts = []
        if self.table_exists('sales'):
            parts.append(
                "SELECT sale_date as date, ref_id, supplier_name, fine_gold as delta_fine_gold, 'Sale' as type FROM sales"
            )
        if self.table_exists('purchases'):
            parts.append(
                "SELECT purchase_date as date, ref_id, supplier_name, -fine_gold as delta_fine_gold, 'Purchase' as type FROM purchases"
            )
        if not parts:
            print("No sales/purchases tables present; skipping supplier ledger export")
            return ''
        union_sql = " UNION ALL ".join(parts) + " ORDER BY date ASC"
        rows = self.execute_query(union_sql)
        headers = ['date', 'ref_id', 'supplier_name', 'delta_fine_gold', 'type']
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for r in rows:
                writer.writerow(r)
        print(f"Exported supplier ledger to {csv_file_path}")
        return csv_file_path

    def export_all_to_dir(self, export_dir: str) -> dict:
        """Export key tables and derived ledgers to CSV files in export_dir. Returns dict of names to paths."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs(export_dir, exist_ok=True)
        out = {}
        def p(name):
            return os.path.join(export_dir, f"{name}_{timestamp}.csv")
        # Core tables
        for table in ['suppliers', 'items', 'sales', 'purchases', 'karigar_orders', 'karigar_order_items', 'raini_orders']:
            try:
                path = self.export_table_to_csv(table, p(table))
                if path:
                    out[table] = path
            except Exception as e:
                print(f"Error exporting {table}: {e}")
        # Ledgers (derived)
        try:
            ledger_path = self.export_supplier_ledger_csv(p('supplier_ledger'))
            if ledger_path:
                out['supplier_ledger'] = ledger_path
        except Exception as e:
            print(f"Error exporting supplier_ledger: {e}")
        return out
