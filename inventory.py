"""
Inventory module for Gold Jewelry Business Management System
Handles all inventory-related operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import DatabaseManager

class InventoryManager:
    def __init__(self, db_manager, main_app=None):
        """Initialize inventory manager with database connection and optional main app reference"""
        self.db = db_manager
        self.main_app = main_app
        self.inventory_tree = None
    
    def set_inventory_tree(self, tree):
        """Set the inventory treeview widget"""
        self.inventory_tree = tree
    
    def load_inventory(self):
        """Load inventory data into treeview"""
        if not self.inventory_tree:
            return
            
        # Clear existing items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        try:
            # Load data from database
            query = '''
                SELECT i.inventory_id, i.weight_grams, i.purity_percentage, 
                       i.form, i.description, i.received_date
                FROM gold_inventory i
                ORDER BY i.received_date DESC
            '''
            rows = self.db.execute_query(query)
            
            for row in rows:
                self.inventory_tree.insert('', 'end', values=(
                    row[0], f"{row[1]:.2f}", 
                    f"{row[2]:.1f}", row[3], row[4], row[5]
                ))
        except Exception as e:
            print(f"Error loading inventory: {e}")
            messagebox.showerror("Database Error", f"Error loading inventory: {str(e)}")
    
    def get_total_gold_available(self):
        """Calculate total gold available in inventory"""
        try:
            query = '''
                SELECT SUM(weight_grams) as total_weight
                FROM gold_inventory
            '''
            result = self.db.execute_query(query)
            total_weight = result[0][0] if result and result[0][0] is not None else 0
            return total_weight
        except Exception as e:
            print(f"Error calculating total gold: {e}")
            return 0
    
    def add_gold(self, parent_window):
        """Add new gold to inventory"""
        # Create add gold window
        add_window = tk.Toplevel(parent_window)
        add_window.title("Add Gold to Inventory")
        add_window.geometry("500x450")
        add_window.configure(bg='#ecf0f1')
        add_window.transient(parent_window)
        add_window.grab_set()
        add_window.resizable(False, False)
        
        # Center the window on screen
        from main import GoldJewelryApp
        GoldJewelryApp.center_modal(add_window, 500, 450)
        
        # Create header frame
        header_frame = tk.Frame(add_window, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Title with icon
        title_label = tk.Label(header_frame, text="🥇 Add Gold to Inventory", 
                               font=("Segoe UI", 20, "bold"), 
                               fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Subtitle
        subtitle_label = tk.Label(header_frame, text="Add new gold to your inventory", 
                                 font=("Segoe UI", 10), 
                                 fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack()
        
        # Create main frame
        main_frame = tk.Frame(add_window, bg='#ecf0f1')
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Create form fields with better styling
        form_frame = tk.Frame(main_frame, bg='#ecf0f1')
        form_frame.pack(fill='x', expand=True)
        
        # Weight field
        weight_frame = tk.Frame(form_frame, bg='#ecf0f1')
        weight_frame.pack(fill='x', pady=(0, 20))
        
        weight_label = tk.Label(weight_frame, text="⚖️ Weight (grams) *", 
                               font=("Segoe UI", 12, "bold"), 
                               fg='#2c3e50', bg='#ecf0f1')
        weight_label.pack(anchor='w', pady=(0, 8))
        
        weight_entry = tk.Entry(weight_frame, width=50, font=("Segoe UI", 11),
                               relief='flat', bd=2, highlightthickness=2,
                               highlightcolor='#3498db', highlightbackground='#bdc3c7')
        weight_entry.pack(fill='x')
        
        # Gold Percentage field
        gold_percent_frame = tk.Frame(form_frame, bg='#ecf0f1')
        gold_percent_frame.pack(fill='x', pady=(0, 20))
        
        gold_percent_label = tk.Label(gold_percent_frame, text="📊 Gold Percentage (%) *", 
                                     font=("Segoe UI", 12, "bold"), 
                                     fg='#2c3e50', bg='#ecf0f1')
        gold_percent_label.pack(anchor='w', pady=(0, 8))
        
        gold_percent_entry = tk.Entry(gold_percent_frame, width=50, font=("Segoe UI", 11),
                                     relief='flat', bd=2, highlightthickness=2,
                                     highlightcolor='#3498db', highlightbackground='#bdc3c7')
        gold_percent_entry.insert(0, "99.9")  # Default to 24K purity
        gold_percent_entry.pack(fill='x')
        
        # Date field
        date_frame = tk.Frame(form_frame, bg='#ecf0f1')
        date_frame.pack(fill='x', pady=(0, 25))
        
        date_label = tk.Label(date_frame, text="📅 Date *", 
                             font=("Segoe UI", 12, "bold"), 
                             fg='#2c3e50', bg='#ecf0f1')
        date_label.pack(anchor='w', pady=(0, 8))
        
        date_entry = tk.Entry(date_frame, width=20, font=("Segoe UI", 11),
                             relief='flat', bd=2, highlightthickness=2,
                             highlightcolor='#3498db', highlightbackground='#bdc3c7')
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(anchor='w')
        
        date_hint = tk.Label(date_frame, text="(YYYY-MM-DD format)", 
                            font=("Segoe UI", 9), 
                            fg='#7f8c8d', bg='#ecf0f1')
        date_hint.pack(anchor='w', pady=(2, 0))
        
        # Buttons frame with better styling
        button_frame = tk.Frame(main_frame, bg='#ecf0f1')
        button_frame.pack(fill='x', pady=(20, 0))
        
        def save_gold():
            """Save the gold to inventory"""
            # Get values
            weight = weight_entry.get().strip()
            gold_percentage = gold_percent_entry.get().strip()
            received_date = date_entry.get().strip()
            
            # Validation
            if not weight or not weight.replace('.', '').isdigit():
                messagebox.showerror("Error", "Please enter a valid weight!")
                weight_entry.focus()
                return
                
            if not gold_percentage or not gold_percentage.replace('.', '').isdigit():
                messagebox.showerror("Error", "Please enter a valid gold percentage!")
                gold_percent_entry.focus()
                return
                
            if not received_date:
                messagebox.showerror("Error", "Date is required!")
                return
            
            try:
                weight = float(weight)
                gold_percentage = float(gold_percentage)
                
                if weight <= 0:
                    messagebox.showerror("Error", "Weight must be greater than 0!")
                    weight_entry.focus()
                    return
                    
                if gold_percentage <= 0 or gold_percentage > 100:
                    messagebox.showerror("Error", "Gold percentage must be between 0 and 100!")
                    gold_percent_entry.focus()
                    return
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values!")
                return
            
            # Validate date format
            try:
                datetime.strptime(received_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return
            
            try:
                # Use default gold type (24K) and insert into inventory
                query = '''
                    INSERT INTO gold_inventory (gold_type_id, weight_grams, purity_percentage, 
                                              form, description, received_date, supplier_info)
                    VALUES (1, ?, ?, 'bar', 'Gold added manually', ?, 'Manual entry')
                '''
                self.db.execute_update(query, (weight, gold_percentage, received_date))
                
                if self.main_app:
                    self.main_app.show_toast(f"Gold added to inventory successfully! • Weight: {weight:.2f}g • Purity: {gold_percentage:.1f}% • Date: {received_date}", success=True)
                else:
                    print(f"Gold added to inventory successfully! Weight: {weight:.2f} grams, Purity: {gold_percentage:.1f}%, Date: {received_date}")
                
                # Refresh data
                self.load_inventory()
                
                # Close window
                add_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error adding gold: {str(e)}")
        
        def cancel():
            """Cancel and close window"""
            add_window.destroy()
        
                # Save and Cancel buttons with beautiful styling
        save_btn = tk.Button(button_frame, text="💾 SAVE", command=save_gold, 
                           bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), 
                           height=2, width=20, relief="raised", bd=2, cursor="hand2")
        save_btn.pack(side='right', padx=(10, 0))
        
        # Add hover effects for save button
        def save_enter(e):
            save_btn.config(bg="#2ecc71", relief="sunken")
        def save_leave(e):
            save_btn.config(bg="#27ae60", relief="raised")
        save_btn.bind('<Enter>', save_enter)
        save_btn.bind('<Leave>', save_leave)
        
        cancel_btn = tk.Button(button_frame, text="❌ CANCEL", command=cancel,
                              bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), 
                              height=2, width=20, relief="raised", bd=2, cursor="hand2")
        cancel_btn.pack(side='right')
        
        # Add hover effects for cancel button
        def cancel_enter(e):
            cancel_btn.config(bg="#c0392b", relief="sunken")
        def cancel_leave(e):
            cancel_btn.config(bg="#e74c3c", relief="raised")
        cancel_btn.bind('<Enter>', cancel_enter)
        cancel_btn.bind('<Leave>', cancel_leave)
        
        # Add separator and instruction with better styling
        separator = tk.Frame(main_frame, height=2, bg='#bdc3c7')
        separator.pack(fill='x', pady=(15, 10))
        
        instruction_label = tk.Label(main_frame, text="* Required fields", 
                                   font=("Segoe UI", 9), 
                                   fg="#7f8c8d", bg='#ecf0f1')
        instruction_label.pack()
        
        # Set focus and bind keys
        weight_entry.focus()
        add_window.bind('<Return>', lambda e: save_gold())
        add_window.bind('<Escape>', lambda e: cancel())
    
    def add_purchase(self, parent_window):
        """Add new gold purchase"""
        # Check if we have suppliers
        supplier_count = self.db.execute_query("SELECT COUNT(*) FROM suppliers WHERE is_active = 1")[0][0]
        
        if supplier_count == 0:
            messagebox.showwarning("Warning", "No active suppliers found!\nPlease add suppliers first.")
            return
        
        # Create purchase window
        purchase_window = tk.Toplevel(parent_window)
        purchase_window.title("Add Gold Purchase")
        purchase_window.geometry("550x750")
        purchase_window.transient(parent_window)
        purchase_window.grab_set()
        purchase_window.resizable(False, False)
        
        # Center the window on screen
        from main import GoldJewelryApp
        GoldJewelryApp.center_modal(purchase_window, 550, 750)
        
        # Create main frame
        main_frame = ttk.Frame(purchase_window, padding="25")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Add Gold Purchase", 
                               font=("Arial", 18, "bold"), foreground="#2c3e50")
        title_label.pack(pady=(0, 25))
        
        # Create form fields
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='x', expand=True)
        
        # Supplier Selection
        supplier_frame = ttk.Frame(form_frame)
        supplier_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(supplier_frame, text="Select Supplier *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        
        # Get active suppliers
        suppliers = self.db.execute_query("SELECT supplier_id, supplier_name FROM suppliers WHERE is_active = 1 ORDER BY supplier_name")
        
        supplier_var = tk.StringVar()
        supplier_combo = ttk.Combobox(supplier_frame, textvariable=supplier_var, 
                                     values=[f"{s[1]}" for s in suppliers], 
                                     state="readonly", width=40, font=("Arial", 11))
        supplier_combo.pack(fill='x')
        
        # Gold Form
        gold_form_frame = ttk.Frame(form_frame)
        gold_form_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(gold_form_frame, text="Gold Form *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        
        gold_form_var = tk.StringVar()
        gold_form_combo = ttk.Combobox(gold_form_frame, textvariable=gold_form_var, 
                                      values=["Chain", "Saman", "Sona"], 
                                      state="readonly", width=40, font=("Arial", 11))
        gold_form_combo.pack(fill='x')
        
        # Gold Purity
        gold_purity_frame = ttk.Frame(form_frame)
        gold_purity_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(gold_purity_frame, text="Gold Purity (%) *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        
        gold_purity_var = tk.StringVar()
        gold_purity_combo = ttk.Combobox(gold_purity_frame, textvariable=gold_purity_var, 
                                        values=["75", "83.3", "91.6", "99.9"], 
                                        state="readonly", width=40, font=("Arial", 11))
        gold_purity_combo.pack(fill='x')
        
        # Weight
        weight_frame = ttk.Frame(form_frame)
        weight_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(weight_frame, text="Weight (grams) *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        weight_entry = ttk.Entry(weight_frame, width=40, font=("Arial", 11))
        weight_entry.pack(fill='x')
        

        
        # Purchase Date
        date_frame = ttk.Frame(form_frame)
        date_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(date_frame, text="Purchase Date *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        date_entry = ttk.Entry(date_frame, width=20, font=("Arial", 11))
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(anchor='w')
        ttk.Label(date_frame, text="(YYYY-MM-DD format)", 
                 font=("Arial", 9), foreground="#7f8c8d").pack(anchor='w', pady=(2, 0))
        
        # Invoice Number
        invoice_frame = ttk.Frame(form_frame)
        invoice_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(invoice_frame, text="Invoice Number", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        invoice_entry = ttk.Entry(invoice_frame, width=40, font=("Arial", 11))
        invoice_entry.pack(fill='x')
        
        # Notes
        notes_frame = ttk.Frame(form_frame)
        notes_frame.pack(fill='x', pady=(0, 25))
        
        ttk.Label(notes_frame, text="Purchase Notes", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        notes_text = tk.Text(notes_frame, height=3, width=40, font=("Arial", 11))
        notes_text.pack(fill='x')
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        def save_purchase():
            """Save the purchase and add to inventory"""
            # Get values
            supplier_name = supplier_var.get()
            gold_form = gold_form_var.get()
            gold_purity = gold_purity_var.get()
            weight = weight_entry.get().strip()
            purchase_date = date_entry.get().strip()
            invoice_number = invoice_entry.get().strip()
            notes = notes_text.get(1.0, tk.END).strip()
            
            # Validation
            if not supplier_name:
                messagebox.showerror("Error", "Please select a supplier!")
                return
                
            if not gold_form:
                messagebox.showerror("Error", "Please select a gold form!")
                gold_form_combo.focus()
                return
                
            if not gold_purity:
                messagebox.showerror("Error", "Please select a gold purity!")
                gold_purity_combo.focus()
                return
                
            if not weight or not weight.replace('.', '').isdigit():
                messagebox.showerror("Error", "Please enter a valid weight!")
                weight_entry.focus()
                return
                
            if not purchase_date:
                messagebox.showerror("Error", "Purchase date is required!")
                return
            
            try:
                weight = float(weight)
                gold_purity_float = float(gold_purity)
                
                if weight <= 0:
                    messagebox.showerror("Error", "Weight must be greater than 0!")
                    weight_entry.focus()
                    return
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values!")
                return
            
            # Validate date format
            try:
                datetime.strptime(purchase_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return
            
            try:
                # Get supplier ID
                supplier_id = None
                for s in suppliers:
                    if s[1] == supplier_name:
                        supplier_id = s[0]
                        break
                
                # Use default gold type (24K) for purchases
                gold_type_id = 1
                
                # Insert into purchases table
                purchase_query = '''
                    INSERT INTO gold_purchases (supplier_id, gold_type_id, weight_grams, 
                                              purity_percentage, purchase_date, invoice_number, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                '''
                self.db.execute_update(purchase_query, (supplier_id, gold_type_id, weight, gold_purity_float, purchase_date, invoice_number, notes))
                
                # Also add to inventory
                inventory_query = '''
                    INSERT INTO gold_inventory (gold_type_id, weight_grams, purity_percentage, 
                                              form, description, received_date, supplier_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                '''
                self.db.execute_update(inventory_query, (gold_type_id, weight, gold_purity_float, gold_form, notes, purchase_date, supplier_name))
                
                if self.main_app:
                    self.main_app.show_toast(f"Gold purchase recorded successfully! • Supplier: {supplier_name} • Weight: {weight:.2f}g • Purity: {gold_purity}% • Form: {gold_form}", success=True)
                else:
                    print(f"Gold purchase recorded successfully! Supplier: {supplier_name}, Weight: {weight:.2f} grams, Purity: {gold_purity}%, Form: {gold_form}")
                
                # Refresh data
                self.load_inventory()
                
                # Close window
                purchase_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error recording purchase: {str(e)}")
        
        def cancel():
            """Cancel and close window"""
            purchase_window.destroy()
        
        # Save and Cancel buttons with better sizing
        save_btn = tk.Button(button_frame, text="💾 RECORD PURCHASE", command=save_purchase, 
                           bg="#3498db", fg="white", font=("Segoe UI", 10, "bold"), 
                           height=2, width=25, relief="raised", bd=2, cursor="hand2")
        save_btn.pack(side='left', padx=(0, 10))
        
        cancel_btn = tk.Button(button_frame, text="❌ CANCEL", command=cancel, 
                             bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), 
                             height=2, width=20, relief="raised", bd=2, cursor="hand2")
        cancel_btn.pack(side='left')
        
        # Center the button frame
        button_frame.pack_configure(anchor='center')
        
        # Add separator before new purchase button
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=(20, 10))
        
        # Add a centered "Create New Purchase" button at the bottom
        new_purchase_frame = ttk.Frame(main_frame)
        new_purchase_frame.pack(fill='x', pady=(10, 20))
        
        def create_new_purchase():
            """Create a new purchase (clear form and start fresh)"""
            # Clear all form fields
            supplier_var.set("")
            gold_form_var.set("")
            gold_purity_var.set("")
            weight_entry.delete(0, tk.END)
            date_entry.delete(0, tk.END)
            date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            invoice_entry.delete(0, tk.END)
            notes_text.delete(1.0, tk.END)
            
            # Set focus to supplier combo
            supplier_combo.focus()
            
            if self.main_app:
                self.main_app.show_toast("Form cleared! Ready for new purchase", success=True)
            else:
                print("Form cleared! Ready for new purchase")
        
        # Create the new purchase button with more prominent styling
        new_purchase_btn = tk.Button(new_purchase_frame, text="🔄 CREATE NEW PURCHASE", command=create_new_purchase,
                                   bg="#27ae60", fg="white", font=("Segoe UI", 12, "bold"),
                                   height=3, width=35, relief="raised", bd=2, cursor="hand2")
        new_purchase_btn.pack(anchor='center', pady=10)
        
        # Add hover effect for new purchase button
        def on_enter_new_purchase(e):
            new_purchase_btn['bg'] = '#2ecc71'
            new_purchase_btn['relief'] = 'sunken'
        def on_leave_new_purchase(e):
            new_purchase_btn['bg'] = '#27ae60'
            new_purchase_btn['relief'] = 'raised'
        
        new_purchase_btn.bind("<Enter>", on_enter_new_purchase)
        new_purchase_btn.bind("<Leave>", on_leave_new_purchase)
        
        # Debug: Print button info
        print(f"New purchase button created: {new_purchase_btn}")
        print(f"Button frame children: {len(new_purchase_frame.winfo_children())}")
        print(f"Button text: {new_purchase_btn['text']}")
        print(f"Button geometry: {new_purchase_btn.winfo_geometry()}")
        
        # Add hover effects
        def on_enter_save(e):
            save_btn['bg'] = '#2980b9'
        def on_leave_save(e):
            save_btn['bg'] = '#3498db'
        
        save_btn.bind("<Enter>", on_enter_save)
        save_btn.bind("<Leave>", on_leave_save)
        
        # Add separator and instruction
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=(15, 10))
        ttk.Label(main_frame, text="* Required fields", 
                 font=("Arial", 9), foreground="#7f8c8d").pack()
        
        # Ensure window is properly configured
        purchase_window.update()
        purchase_window.deiconify()
        purchase_window.lift()
        purchase_window.focus_force()
        
        # Debug: Print window info
        print(f"Purchase window geometry: {purchase_window.geometry()}")
        print(f"Main frame children count: {len(main_frame.winfo_children())}")
        
        # Set focus and bind keys
        supplier_combo.focus()
        purchase_window.bind('<Return>', lambda e: save_purchase())
        purchase_window.bind('<Escape>', lambda e: cancel())
    
    def update_inventory(self, parent_window):
        """Update inventory manually"""
        # Get selected inventory item
        selected_item = self.inventory_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an inventory item to update!")
            return
        
        # Get inventory data
        inventory_id = self.inventory_tree.item(selected_item[0])['values'][0]
        
        # Fetch inventory details
        query = '''
            SELECT i.inventory_id, i.weight_grams, i.purity_percentage, 
                   i.form, i.description, i.received_date, i.supplier_info
            FROM gold_inventory i
            WHERE i.inventory_id = ?
        '''
        inventory_data = self.db.execute_query(query, (inventory_id,))[0]
        
        if not inventory_data:
            messagebox.showerror("Error", "Inventory item not found!")
            return
        
        # Create update window
        update_window = tk.Toplevel(parent_window)
        update_window.title("Update Inventory Item")
        update_window.geometry("500x500")
        update_window.transient(parent_window)
        update_window.grab_set()
        update_window.resizable(False, False)
        
        # Center the window on screen
        from main import GoldJewelryApp
        GoldJewelryApp.center_modal(update_window, 500, 500)
        
        # Create main frame
        main_frame = ttk.Frame(update_window, padding="25")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Update Inventory Item", 
                               font=("Arial", 16, "bold"), foreground="#2c3e50")
        title_label.pack(pady=(0, 20))
        
        # Inventory info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(info_frame, text=f"Item ID: {inventory_data[0]}", 
                 font=("Arial", 11, "bold")).pack(anchor='w')
        ttk.Label(info_frame, text=f"Current Weight: {inventory_data[1]:.2f} grams", 
                 font=("Arial", 11)).pack(anchor='w')
        ttk.Label(info_frame, text=f"Purity: {inventory_data[2]:.1f}%", 
                 font=("Arial", 11)).pack(anchor='w')
        ttk.Label(info_frame, text=f"Form: {inventory_data[3]}", 
                 font=("Arial", 11)).pack(anchor='w')
        
        # New Weight
        weight_frame = ttk.Frame(main_frame)
        weight_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(weight_frame, text="New Weight (grams) *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        weight_entry = ttk.Entry(weight_frame, width=30, font=("Arial", 11))
        weight_entry.insert(0, str(inventory_data[2]))
        weight_entry.pack(fill='x')
        
        # Description
        description_frame = ttk.Frame(main_frame)
        description_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(description_frame, text="Description", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        description_entry = ttk.Entry(description_frame, width=40, font=("Arial", 11))
        description_entry.insert(0, inventory_data[4] or "")
        description_entry.pack(fill='x')
        

        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        def update_item():
            """Update the inventory item"""
            new_weight = weight_entry.get().strip()
            description = description_entry.get().strip()
            
            # Validation
            if not new_weight or not new_weight.replace('.', '').isdigit():
                messagebox.showerror("Error", "Please enter a valid weight!")
                weight_entry.focus()
                return
            
            try:
                new_weight = float(new_weight)
                
                if new_weight < 0:
                    messagebox.showerror("Error", "Weight cannot be negative!")
                    weight_entry.focus()
                    return
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid numeric weight!")
                return
            
            try:
                # Update inventory
                query = '''
                    UPDATE gold_inventory 
                    SET weight_grams = ?, description = ?
                    WHERE inventory_id = ?
                '''
                self.db.execute_update(query, (new_weight, description, inventory_id))
                
                if self.main_app:
                    self.main_app.show_toast(f"Inventory item updated successfully! • New Weight: {new_weight:.2f}g", success=True)
                else:
                    print(f"Inventory item updated successfully! New Weight: {new_weight:.2f} grams")
                
                # Refresh data
                self.load_inventory()
                
                # Close window
                update_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error updating inventory: {str(e)}")
        
        def delete_item():
            """Delete the inventory item"""
            if messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete this inventory item?\n\n"
                                 f"Form: {inventory_data[3]}\n"
                                 f"Weight: {inventory_data[1]:.2f} grams\n"
                                 f"Purity: {inventory_data[2]:.1f}%\n\n"
                                 f"This action cannot be undone!"):
                try:
                    # Check if item is allocated to work orders
                    allocated_count = self.db.execute_query('''
                        SELECT COUNT(*) FROM work_orders wo
                        JOIN gold_inventory i ON wo.gold_type_id = i.gold_type_id
                        WHERE i.inventory_id = ? AND wo.status IN ('issued', 'in_progress')
                    ''', (inventory_id,))[0][0]
                    
                    if allocated_count > 0:
                        messagebox.showwarning("Cannot Delete", 
                                             f"Cannot delete this inventory item because it's allocated to {allocated_count} active work order(s).\n\n"
                                             f"Please complete or cancel the work orders first.")
                        return
                    
                    # Delete inventory item
                    self.db.execute_update('DELETE FROM gold_inventory WHERE inventory_id = ?', (inventory_id,))
                    
                    if self.main_app:
                        self.main_app.show_toast("Inventory item deleted successfully!", success=True)
                    else:
                        print("Inventory item deleted successfully!")
                    
                    # Refresh data
                    self.load_inventory()
                    
                    # Close window
                    update_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Database Error", f"Error deleting inventory item: {str(e)}")
        
        def cancel():
            """Cancel and close window"""
            update_window.destroy()
        
        # Update, Delete and Cancel buttons
        update_btn = tk.Button(button_frame, text="UPDATE", command=update_item, 
                             bg="#f39c12", fg="white", font=("Arial", 12, "bold"), 
                             height=2, width=15, relief="flat", bd=0, cursor="hand2")
        update_btn.pack(side='right', padx=(10, 0))
        
        delete_btn = tk.Button(button_frame, text="DELETE", command=delete_item, 
                             bg="#e74c3c", fg="white", font=("Arial", 12, "bold"), 
                             height=2, width=15, relief="flat", bd=0, cursor="hand2")
        delete_btn.pack(side='right', padx=(5, 0))
        
        cancel_btn = tk.Button(button_frame, text="CANCEL", command=cancel, 
                             bg="#95a5a6", fg="white", font=("Arial", 12, "bold"), 
                             height=2, width=15, relief="flat", bd=0, cursor="hand2")
        cancel_btn.pack(side='right')
        
        # Add hover effects
        def on_enter_update(e):
            update_btn['bg'] = '#e67e22'
        def on_leave_update(e):
            update_btn['bg'] = '#f39c12'
        
        update_btn.bind("<Enter>", on_enter_update)
        update_btn.bind("<Leave>", on_leave_update)
        
        # Set focus and bind keys
        weight_entry.focus()
        update_window.bind('<Return>', lambda e: update_item())
        update_window.bind('<Escape>', lambda e: cancel())
    
    def show_inventory_breakdown(self, parent_window):
        """Show inventory breakdown by gold form and purity"""
        # Create breakdown window
        breakdown_window = tk.Toplevel(parent_window)
        breakdown_window.title("Inventory Breakdown by Form and Purity")
        breakdown_window.geometry("800x600")
        breakdown_window.configure(bg='#ecf0f1')
        breakdown_window.transient(parent_window)
        breakdown_window.grab_set()
        breakdown_window.resizable(True, True)
        
        # Center the window on screen
        from main import GoldJewelryApp
        GoldJewelryApp.center_modal(breakdown_window, 800, 600)
        
        # Create header frame
        header_frame = tk.Frame(breakdown_window, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Title with icon
        title_label = tk.Label(header_frame, text="📊 Inventory Breakdown", 
                               font=("Segoe UI", 20, "bold"), 
                               fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Subtitle
        subtitle_label = tk.Label(header_frame, text="Gold inventory by form and purity", 
                                 font=("Segoe UI", 10), 
                                 fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack()
        
        # Create main frame
        main_frame = tk.Frame(breakdown_window, bg='#ecf0f1')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create breakdown data
        try:
            # Get inventory breakdown data from actual database
            breakdown_data = self.get_inventory_breakdown()
            print(f"Debug: Retrieved breakdown data: {breakdown_data}")
            
            # Create summary frame
            summary_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
            summary_frame.pack(fill='x', pady=(0, 20))
            
            # Summary title
            summary_title = tk.Label(summary_frame, text="📈 Summary", 
                                   font=("Segoe UI", 16, "bold"), 
                                   fg='#2c3e50', bg='white')
            summary_title.pack(pady=15)
            
            # Summary content
            summary_content = tk.Frame(summary_frame, bg='white')
            summary_content.pack(padx=20, pady=(0, 20))
            
            total_items = sum(sum(category.values()) for category in breakdown_data.values())
            total_weight = self.get_total_gold_available()
            
            tk.Label(summary_content, text=f"Total Items: {total_items}", 
                    font=("Segoe UI", 12, "bold"), fg='#27ae60', bg='white').pack(anchor='w')
            tk.Label(summary_content, text=f"Total Weight: {total_weight:.2f} grams", 
                    font=("Segoe UI", 12, "bold"), fg='#27ae60', bg='white').pack(anchor='w')
            
            # Create detailed breakdown frame
            details_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
            details_frame.pack(fill='both', expand=True)
            
            # Details title
            details_title = tk.Label(details_frame, text="📋 Detailed Breakdown", 
                                   font=("Segoe UI", 16, "bold"), 
                                   fg='#2c3e50', bg='white')
            details_title.pack(pady=15)
            
            # Create scrollable text area
            text_frame = tk.Frame(details_frame, bg='white')
            text_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            # Text widget with scrollbar
            text_widget = tk.Text(text_frame, height=20, width=80, 
                                font=("Consolas", 10), bg='#f8f9fa', 
                                fg='#2c3e50', relief='flat', bd=0)
            scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Populate breakdown data in the requested format
            breakdown_text = "GOLD INVENTORY BREAKDOWN\n"
            breakdown_text += "=" * 50 + "\n\n"
            
            for form in ["Chain", "Saman", "Sona"]:
                purities = breakdown_data.get(form, {})
                
                # Calculate total weight for this form
                total_weight = 0
                total_count = 0
                
                for purity in ["75", "83.3", "91.6", "99.9"]:
                    weight = self.get_weight_by_form_purity(form, purity)
                    count = purities.get(purity, 0)
                    total_weight += weight
                    total_count += count
                
                # Display form header with total weight
                breakdown_text += f"📦 {form}: ({total_weight:.2f} grams)\n"
                breakdown_text += "-" * 40 + "\n"
                
                # Display each purity with count
                for purity in ["75", "83.3", "91.6", "99.9"]:
                    count = purities.get(purity, 0)
                    if count > 0:
                        breakdown_text += f"  {purity}%: {count} {form.lower()}\n"
                    else:
                        breakdown_text += f"  {purity}%: 0 {form.lower()}\n"
                
                # Display total count for this form
                breakdown_text += f"Total no of {form.lower()}: {total_count}\n"
                breakdown_text += "\n"
            
            text_widget.insert('1.0', breakdown_text)
            text_widget.config(state='disabled')  # Make read-only
            
        except Exception as e:
            error_label = tk.Label(main_frame, text=f"Error loading breakdown: {str(e)}", 
                                 font=("Segoe UI", 12), fg='#e74c3c', bg='#ecf0f1')
            error_label.pack(expand=True)
        
        # Close button
        close_btn = tk.Button(main_frame, text="❌ Close", command=breakdown_window.destroy,
                             bg="#95a5a6", fg="white", font=("Segoe UI", 12, "bold"), 
                             height=2, width=15, relief="raised", bd=2, cursor="hand2")
        close_btn.pack(pady=20)
        
        # Add hover effects
        def on_enter_close(e):
            close_btn.config(bg="#7f8c8d", relief="sunken")
        def on_leave_close(e):
            close_btn.config(bg="#95a5a6", relief="raised")
        
        close_btn.bind('<Enter>', on_enter_close)
        close_btn.bind('<Leave>', on_leave_close)
    
    def get_inventory_breakdown(self):
        """Get inventory breakdown by form and purity from actual database"""
        try:
            # Query to get actual inventory data grouped by form and purity
            query = '''
                SELECT form, purity_percentage, COUNT(*) as count
                FROM gold_inventory
                WHERE form IS NOT NULL AND form != ''
                GROUP BY form, purity_percentage
                ORDER BY form, purity_percentage
            '''
            rows = self.db.execute_query(query)
            
            # Initialize breakdown structure
            breakdown = {
                'Chain': {'75': 0, '83.3': 0, '91.6': 0, '99.9': 0},
                'Saman': {'75': 0, '83.3': 0, '91.6': 0, '99.9': 0},
                'Sona': {'75': 0, '83.3': 0, '91.6': 0, '99.9': 0}
            }
            
            # Populate breakdown with actual data from database
            for row in rows:
                form, purity, count = row
                # Convert purity to string for comparison
                purity_str = str(purity)
                
                # Only include forms we're tracking and valid purities
                if form in breakdown and purity_str in breakdown[form]:
                    breakdown[form][purity_str] = count
                elif form not in ['Chain', 'Saman', 'Sona']:
                    # Handle other forms that might exist in database
                    print(f"Found form '{form}' with purity {purity}% and count {count} - not in standard breakdown")
            
            return breakdown
            
        except Exception as e:
            print(f"Error getting inventory breakdown: {e}")
            # Return empty breakdown on error
            return {
                'Chain': {'75': 0, '83.3': 0, '91.6': 0, '99.9': 0},
                'Saman': {'75': 0, '83.3': 0, '91.6': 0, '99.9': 0},
                'Sona': {'75': 0, '83.3': 0, '91.6': 0, '99.9': 0}
            }
    
    def get_weight_by_form_purity(self, form, purity):
        """Get total weight for a specific form and purity from actual database"""
        try:
            query = '''
                SELECT SUM(weight_grams) as total_weight
                FROM gold_inventory
                WHERE form = ? AND purity_percentage = ?
            '''
            result = self.db.execute_query(query, (form, float(purity)))
            total_weight = result[0][0] if result and result[0][0] is not None else 0.0
            print(f"Debug: {form} {purity}% = {total_weight} grams")
            return total_weight
            
        except Exception as e:
            print(f"Error getting weight for {form} {purity}%: {e}")
            return 0.0
