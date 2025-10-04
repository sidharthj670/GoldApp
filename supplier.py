"""
Supplier module for Gold Jewelry Business Management System
Handles all supplier-related operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import DatabaseManager

class SupplierManager:
    def __init__(self, db_manager, main_app=None):
        """Initialize supplier manager with database connection and optional main app reference"""
        self.db = db_manager
        self.main_app = main_app
        self.suppliers_tree = None
    
    def set_suppliers_tree(self, tree):
        """Set the suppliers treeview widget"""
        self.suppliers_tree = tree
    
    def load_suppliers(self):
        """Load suppliers data into treeview"""
        if not self.suppliers_tree:
            return
            
        # Clear existing items
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        
        try:
            # Load data from database - load ALL suppliers (active and inactive)
            query = '''
                SELECT supplier_id, supplier_name, contact_person, phone, email, address, gst_number, is_active
                FROM suppliers
                ORDER BY supplier_name
            '''
            rows = self.db.execute_query(query)
            print(f"Loaded {len(rows)} suppliers from database")
            
            for row in rows:
                active = "Yes" if row[7] else "No"
                # Ensure all values are properly formatted
                values = (
                    row[0],  # ID
                    row[1] or "",  # Name
                    row[2] or "",  # Contact Person
                    row[3] or "",  # Phone
                    row[4] or "",  # Email
                    row[5] or "",  # Address
                    row[6] or "",  # GST Number
                    active  # Active Status
                )
                self.suppliers_tree.insert('', 'end', values=values)
                
        except Exception as e:
            print(f"Error loading suppliers: {e}")
            messagebox.showerror("Database Error", f"Error loading suppliers: {str(e)}")
    
    def add_supplier(self, parent_window):
        """Add new supplier"""
        # Create a new top-level window for adding supplier
        add_window = tk.Toplevel(parent_window)
        add_window.title("Add New Supplier")
        add_window.geometry("500x600")
        add_window.transient(parent_window)
        add_window.grab_set()
        add_window.resizable(False, False)
        
        # Center the window on screen
        from main import GoldJewelryApp
        GoldJewelryApp.center_modal(add_window, 500, 600)
        
        # Create main frame with better padding
        main_frame = ttk.Frame(add_window, padding="25")
        main_frame.pack(fill='both', expand=True)
        
        # Title with better styling
        title_label = ttk.Label(main_frame, text="Add New Supplier", 
                               font=("Arial", 18, "bold"), foreground="#2c3e50")
        title_label.pack(pady=(0, 25))
        
        # Create form fields with better spacing
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='x', expand=True)
        
        # Supplier Name - Required field
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(name_frame, text="Supplier Name *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        name_entry = ttk.Entry(name_frame, width=40, font=("Arial", 11))
        name_entry.pack(fill='x')
        
        # Contact Person
        contact_frame = ttk.Frame(form_frame)
        contact_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(contact_frame, text="Contact Person", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        contact_entry = ttk.Entry(contact_frame, width=40, font=("Arial", 11))
        contact_entry.pack(fill='x')
        
        # Phone
        phone_frame = ttk.Frame(form_frame)
        phone_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(phone_frame, text="Phone Number", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        phone_entry = ttk.Entry(phone_frame, width=40, font=("Arial", 11))
        phone_entry.pack(fill='x')
        
        # Email
        email_frame = ttk.Frame(form_frame)
        email_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(email_frame, text="Email Address", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        email_entry = ttk.Entry(email_frame, width=40, font=("Arial", 11))
        email_entry.pack(fill='x')
        
        # Address
        address_frame = ttk.Frame(form_frame)
        address_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(address_frame, text="Address", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        address_text = tk.Text(address_frame, height=3, width=40, font=("Arial", 11))
        address_text.pack(fill='x')
        
        # GST Number
        gst_frame = ttk.Frame(form_frame)
        gst_frame.pack(fill='x', pady=(0, 25))
        
        ttk.Label(gst_frame, text="GST Number", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        gst_entry = ttk.Entry(gst_frame, width=40, font=("Arial", 11))
        gst_entry.pack(fill='x')
        
        # Buttons frame with better styling
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        def save_supplier():
            """Save the supplier to database"""
            # Get values from entries
            supplier_name = name_entry.get().strip()
            contact_person = contact_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            address = address_text.get(1.0, tk.END).strip()
            gst_number = gst_entry.get().strip()
            
            print(f"Attempting to save supplier: {supplier_name}")
            
            # Validation - only name is required
            if not supplier_name:
                messagebox.showerror("Error", "Supplier Name is required!")
                name_entry.focus()
                return
            
            # Email validation (if provided)
            if email and '@' not in email:
                messagebox.showerror("Error", "Please enter a valid email address!")
                email_entry.focus()
                return
            
            try:
                # Insert into database
                query = '''
                    INSERT INTO suppliers (supplier_name, contact_person, phone, email, address, gst_number, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                '''
                self.db.execute_update(query, (supplier_name, contact_person, phone, email, address, gst_number))
                
                print(f"Supplier '{supplier_name}' saved to database successfully")
                
                # Show success message using main app toast
                if self.main_app:
                    self.main_app.show_toast(f"Supplier '{supplier_name}' added successfully!", success=True)
                else:
                    print(f"Supplier '{supplier_name}' added successfully!")
                
                # Refresh the suppliers list
                print("Refreshing suppliers list...")
                self.load_suppliers()
                
                # Close the window
                add_window.destroy()
                
            except Exception as e:
                print(f"Database error saving supplier: {e}")
                messagebox.showerror("Database Error", f"Error saving supplier: {str(e)}")
        
        def cancel():
            """Cancel and close window"""
            add_window.destroy()
        
        # Save and Cancel buttons with better styling
        save_btn = tk.Button(button_frame, text="💾 SAVE", command=save_supplier, 
                           bg="#27ae60", fg="white", font=("Segoe UI", 11, "bold"), 
                           height=1, width=15, relief="flat", bd=0, cursor="hand2",
                           padx=20, pady=8)
        save_btn.pack(side='right', padx=(10, 0))
        
        cancel_btn = tk.Button(button_frame, text="❌ CANCEL", command=cancel, 
                             bg="#e74c3c", fg="white", font=("Segoe UI", 11, "bold"), 
                             height=1, width=15, relief="flat", bd=0, cursor="hand2",
                             padx=20, pady=8)
        cancel_btn.pack(side='right')
        
        # Add hover effects for buttons
        def on_enter_save(e):
            save_btn['bg'] = '#2ecc71'
        
        def on_leave_save(e):
            save_btn['bg'] = '#27ae60'
        
        def on_enter_cancel(e):
            cancel_btn['bg'] = '#c0392b'
        
        def on_leave_cancel(e):
            cancel_btn['bg'] = '#e74c3c'
        
        save_btn.bind("<Enter>", on_enter_save)
        save_btn.bind("<Leave>", on_leave_save)
        cancel_btn.bind("<Enter>", on_enter_cancel)
        cancel_btn.bind("<Leave>", on_leave_cancel)
        
        # Add a subtle separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=(15, 10))
        
        # Add helpful instruction
        ttk.Label(main_frame, text="* Required field", 
                 font=("Arial", 9), foreground="#7f8c8d").pack()
        
        # Set focus to name entry
        name_entry.focus()
        
        # Bind Enter key to save and Escape to cancel
        add_window.bind('<Return>', lambda e: save_supplier())
        add_window.bind('<Escape>', lambda e: cancel())
    
    def edit_supplier(self, parent_window):
        """Edit supplier details"""
        # Get selected supplier
        selected_item = self.suppliers_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a supplier to edit!")
            return
        
        # Get supplier data
        supplier_id = self.suppliers_tree.item(selected_item[0])['values'][0]
        
        # Fetch supplier details from database
        query = '''
            SELECT supplier_id, supplier_name, contact_person, phone, email, address, gst_number, is_active
            FROM suppliers
            WHERE supplier_id = ?
        '''
        supplier_data = self.db.execute_query(query, (supplier_id,))[0]
        
        if not supplier_data:
            messagebox.showerror("Error", "Supplier not found!")
            return
        
        # Create edit window
        edit_window = tk.Toplevel(parent_window)
        edit_window.title("Edit Supplier")
        edit_window.geometry("500x600")
        edit_window.transient(parent_window)
        edit_window.grab_set()
        edit_window.resizable(False, False)
        
        # Center the window on screen
        from main import GoldJewelryApp
        GoldJewelryApp.center_modal(edit_window, 500, 600)
        
        # Create main frame
        main_frame = ttk.Frame(edit_window, padding="25")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Edit Supplier", 
                               font=("Arial", 18, "bold"), foreground="#2c3e50")
        title_label.pack(pady=(0, 25))
        
        # Create form fields
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='x', expand=True)
        
        # Supplier Name
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(name_frame, text="Supplier Name *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        name_entry = ttk.Entry(name_frame, width=40, font=("Arial", 11))
        name_entry.insert(0, supplier_data[1])
        name_entry.pack(fill='x')
        
        # Contact Person
        contact_frame = ttk.Frame(form_frame)
        contact_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(contact_frame, text="Contact Person", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        contact_entry = ttk.Entry(contact_frame, width=40, font=("Arial", 11))
        contact_entry.insert(0, supplier_data[2] or "")
        contact_entry.pack(fill='x')
        
        # Phone
        phone_frame = ttk.Frame(form_frame)
        phone_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(phone_frame, text="Phone Number", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        phone_entry = ttk.Entry(phone_frame, width=40, font=("Arial", 11))
        phone_entry.insert(0, supplier_data[3] or "")
        phone_entry.pack(fill='x')
        
        # Email
        email_frame = ttk.Frame(form_frame)
        email_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(email_frame, text="Email Address", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        email_entry = ttk.Entry(email_frame, width=40, font=("Arial", 11))
        email_entry.insert(0, supplier_data[4] or "")
        email_entry.pack(fill='x')
        
        # Address
        address_frame = ttk.Frame(form_frame)
        address_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(address_frame, text="Address", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        address_text = tk.Text(address_frame, height=3, width=40, font=("Arial", 11))
        address_text.insert(1.0, supplier_data[5] or "")
        address_text.pack(fill='x')
        
        # GST Number
        gst_frame = ttk.Frame(form_frame)
        gst_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(gst_frame, text="GST Number", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        gst_entry = ttk.Entry(gst_frame, width=40, font=("Arial", 11))
        gst_entry.insert(0, supplier_data[6] or "")
        gst_entry.pack(fill='x')
        
        # Active Status
        active_frame = ttk.Frame(form_frame)
        active_frame.pack(fill='x', pady=(0, 25))
        
        active_var = tk.BooleanVar(value=bool(supplier_data[7]))
        active_check = ttk.Checkbutton(active_frame, text="Active", variable=active_var)
        active_check.pack(anchor='w')
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        def update_supplier():
            """Update the supplier in database"""
            # Get values from entries
            supplier_name = name_entry.get().strip()
            contact_person = contact_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            address = address_text.get(1.0, tk.END).strip()
            gst_number = gst_entry.get().strip()
            is_active = active_var.get()
            
            # Validation
            if not supplier_name:
                messagebox.showerror("Error", "Supplier Name is required!")
                return
            
            # Email validation (if provided)
            if email and '@' not in email:
                messagebox.showerror("Error", "Please enter a valid email address!")
                email_entry.focus()
                return
            
            try:
                # Update database
                query = '''
                    UPDATE suppliers 
                    SET supplier_name = ?, contact_person = ?, phone = ?, email = ?, 
                        address = ?, gst_number = ?, is_active = ?
                    WHERE supplier_id = ?
                '''
                self.db.execute_update(query, (supplier_name, contact_person, phone, email, 
                                            address, gst_number, is_active, supplier_id))
                
                # Show success message using main app toast
                if self.main_app:
                    self.main_app.show_toast(f"Supplier '{supplier_name}' updated successfully!", success=True)
                else:
                    print(f"Supplier '{supplier_name}' updated successfully!")
                
                # Refresh the suppliers list
                self.load_suppliers()
                
                # Close the window
                edit_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error updating supplier: {str(e)}")
        
        def delete_supplier():
            """Delete the supplier"""
            if messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete supplier '{supplier_data[1]}'?\n\nThis action cannot be undone!"):
                try:
                    # Check if supplier has purchases
                    purchase_query = '''
                        SELECT COUNT(*) FROM gold_purchases WHERE supplier_id = ?
                    '''
                    purchase_count = self.db.execute_query(purchase_query, (supplier_id,))[0][0]
                    
                    if purchase_count > 0:
                        messagebox.showwarning("Cannot Delete", 
                                             f"Cannot delete supplier '{supplier_data[1]}' because they have {purchase_count} purchase record(s).\n\nPlease delete the purchase records first.")
                        return
                    
                    # Delete supplier
                    delete_query = 'DELETE FROM suppliers WHERE supplier_id = ?'
                    self.db.execute_update(delete_query, (supplier_id,))
                    
                    if self.main_app:
                        self.main_app.show_toast(f"Supplier '{supplier_data[1]}' deleted successfully!", success=True)
                    else:
                        print(f"Supplier '{supplier_data[1]}' deleted successfully!")
                    
                    # Refresh the suppliers list
                    self.load_suppliers()
                    
                    # Close the window
                    edit_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Database Error", f"Error deleting supplier: {str(e)}")
        
        def cancel():
            """Cancel and close window"""
            edit_window.destroy()
        
        # Update, Delete and Cancel buttons
        update_btn = tk.Button(button_frame, text="✏️ UPDATE", command=update_supplier, 
                             bg="#f39c12", fg="white", font=("Segoe UI", 11, "bold"), 
                             height=1, width=15, relief="flat", bd=0, cursor="hand2",
                             padx=20, pady=8)
        update_btn.pack(side='right', padx=(10, 0))
        
        delete_btn = tk.Button(button_frame, text="🗑️ DELETE", command=delete_supplier, 
                             bg="#e74c3c", fg="white", font=("Segoe UI", 11, "bold"), 
                             height=1, width=15, relief="flat", bd=0, cursor="hand2",
                             padx=20, pady=8)
        delete_btn.pack(side='right', padx=(5, 0))
        
        cancel_btn = tk.Button(button_frame, text="❌ CANCEL", command=cancel, 
                             bg="#95a5a6", fg="white", font=("Segoe UI", 11, "bold"), 
                             height=1, width=15, relief="flat", bd=0, cursor="hand2",
                             padx=20, pady=8)
        cancel_btn.pack(side='right')
        
        # Add hover effects
        def on_enter_update(e):
            update_btn['bg'] = '#e67e22'
        def on_leave_update(e):
            update_btn['bg'] = '#f39c12'
        
        def on_enter_delete(e):
            delete_btn['bg'] = '#c0392b'
        def on_leave_delete(e):
            delete_btn['bg'] = '#e74c3c'
        
        def on_enter_cancel(e):
            cancel_btn['bg'] = '#7f8c8d'
        def on_leave_cancel(e):
            cancel_btn['bg'] = '#95a5a6'
        
        update_btn.bind("<Enter>", on_enter_update)
        update_btn.bind("<Leave>", on_leave_update)
        delete_btn.bind("<Enter>", on_enter_delete)
        delete_btn.bind("<Leave>", on_leave_delete)
        cancel_btn.bind("<Enter>", on_enter_cancel)
        cancel_btn.bind("<Leave>", on_leave_cancel)
        
        # Set focus to name entry
        name_entry.focus()
        
        # Bind Enter key to update and Escape to cancel
        edit_window.bind('<Return>', lambda e: update_supplier())
        edit_window.bind('<Escape>', lambda e: cancel())
