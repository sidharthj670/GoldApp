"""
Freelancer module for Gold Jewelry Business Management System
Handles all freelancer-related operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import DatabaseManager

class FreelancerManager:
    def __init__(self, db_manager, toast_callback=None):
        """Initialize freelancer manager with database connection and optional toast callback"""
        self.db = db_manager
        self.freelancers_tree = None
        self.toast_callback = toast_callback
    
    def set_freelancers_tree(self, tree):
        """Set the freelancers treeview widget"""
        self.freelancers_tree = tree
    
    def load_freelancers(self):
        """Load freelancers data into treeview"""
        if not self.freelancers_tree:
            return
            
        # Clear existing items
        for item in self.freelancers_tree.get_children():
            self.freelancers_tree.delete(item)
        
        try:
            # Load data from database - load ALL freelancers (active and inactive)
            query = '''
                SELECT freelancer_id, full_name, specialization, phone, address, joined_date, is_active
                FROM freelancers
                ORDER BY full_name
            '''
            rows = self.db.execute_query(query)
            print(f"Loaded {len(rows)} freelancers from database")
            
            for row in rows:
                active = "Yes" if row[6] else "No"
                # Ensure all values are properly formatted
                values = (
                    row[0],  # ID
                    row[1] or "",  # Name
                    row[2] or "",  # Specialization
                    row[3] or "",  # Phone
                    row[4] or "",  # Address
                    row[5] or "",  # Joined Date
                    active  # Active Status
                )
                self.freelancers_tree.insert('', 'end', values=values)
                
        except Exception as e:
            print(f"Error loading freelancers: {e}")
            messagebox.showerror("Database Error", f"Error loading freelancers: {str(e)}")
    
    def add_freelancer(self, parent_window):
        """Add new freelancer"""
        # Create a new top-level window for adding freelancer
        add_window = tk.Toplevel(parent_window)
        add_window.title("Add New Freelancer")
        add_window.geometry("450x350")
        add_window.transient(parent_window)
        add_window.grab_set()
        add_window.resizable(False, False)
        
        # Center the window on screen
        from main import GoldJewelryApp
        GoldJewelryApp.center_modal(add_window, 450, 350)
        
        # Create main frame with better padding
        main_frame = ttk.Frame(add_window, padding="25")
        main_frame.pack(fill='both', expand=True)
        
        # Title with better styling
        title_label = ttk.Label(main_frame, text="Add New Freelancer", 
                               font=("Arial", 18, "bold"), foreground="#2c3e50")
        title_label.pack(pady=(0, 25))
        
        # Create form fields with better spacing
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='x', expand=True)
        
        # Full Name - Required field
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(name_frame, text="Full Name *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        name_entry = ttk.Entry(name_frame, width=40, font=("Arial", 11))
        name_entry.pack(fill='x')
        
        # Phone
        phone_frame = ttk.Frame(form_frame)
        phone_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(phone_frame, text="Phone Number", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        phone_entry = ttk.Entry(phone_frame, width=40, font=("Arial", 11))
        phone_entry.pack(fill='x')
        
        # Address
        address_frame = ttk.Frame(form_frame)
        address_frame.pack(fill='x', pady=(0, 25))
        
        ttk.Label(address_frame, text="Address", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        address_entry = ttk.Entry(address_frame, width=40, font=("Arial", 11))
        address_entry.pack(fill='x')
        
        # Buttons frame with better styling
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        def save_freelancer():
            """Save the freelancer to database"""
            # Get values from entries
            full_name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            address = address_entry.get().strip()
            
            print(f"Attempting to save freelancer: {full_name}")
            
            # Validation - only name is required
            if not full_name:
                messagebox.showerror("Error", "Full Name is required!")
                name_entry.focus()
                return
            
            try:
                # Insert into database - simplified fields
                query = '''
                    INSERT INTO freelancers (full_name, phone, address, joined_date)
                    VALUES (?, ?, ?, ?)
                '''
                self.db.execute_update(query, (full_name, phone, address, datetime.now().strftime("%Y-%m-%d")))
                print(f"Freelancer '{full_name}' saved to database successfully")
                
                # Show success message using toast callback if available
                if self.toast_callback:
                    self.toast_callback(f"Freelancer '{full_name}' added successfully!", success=True)
                else:
                    print(f"Freelancer '{full_name}' added successfully!")

                # Refresh the freelancers list
                print("Refreshing freelancers list...")
                self.load_freelancers()
                
                # Close the window
                add_window.destroy()
                
            except Exception as e:
                print(f"Database error saving freelancer: {e}")
                messagebox.showerror("Database Error", f"Error saving freelancer: {str(e)}")
        
        def cancel():
            """Cancel and close window"""
            add_window.destroy()
        
        # Save and Cancel buttons with better styling
        save_btn = tk.Button(button_frame, text="💾 SAVE", command=save_freelancer,
                           bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"),
                           height=3, width=18, relief="raised", bd=2, cursor="hand2", padx=20, pady=8)
        save_btn.pack(side='right', padx=(10, 0))

        cancel_btn = tk.Button(button_frame, text="❌ CANCEL", command=cancel,
                             bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"),
                             height=3, width=18, relief="raised", bd=2, cursor="hand2", padx=20, pady=8)
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
        add_window.bind('<Return>', lambda e: save_freelancer())
        add_window.bind('<Escape>', lambda e: cancel())
    
    def edit_freelancer(self, parent_window):
        """Edit freelancer details"""
        # Get selected freelancer
        selected_item = self.freelancers_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a freelancer to edit!")
            return
        
        # Get freelancer data
        freelancer_id = self.freelancers_tree.item(selected_item[0])['values'][0]
        
        # Fetch freelancer details from database
        query = '''
            SELECT full_name, specialization, phone, address, bank_details, joined_date, is_active
            FROM freelancers
            WHERE freelancer_id = ?
        '''
        freelancer_data = self.db.execute_query(query, (freelancer_id,))[0]
        
        if not freelancer_data:
            messagebox.showerror("Error", "Freelancer not found!")
            return
        
        # Create edit window
        edit_window = tk.Toplevel(parent_window)
        edit_window.title("Edit Freelancer")
        edit_window.geometry("500x450")
        edit_window.transient(parent_window)
        edit_window.grab_set()
        
        # Center the window on screen
        from main import GoldJewelryApp
        GoldJewelryApp.center_modal(edit_window, 500, 450)
        
        # Create main frame
        main_frame = ttk.Frame(edit_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Edit Freelancer", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Create form fields
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='x', expand=True)
        
        # Full Name
        ttk.Label(form_frame, text="Full Name *:").pack(anchor='w', pady=(0, 5))
        name_entry = ttk.Entry(form_frame, width=50)
        name_entry.insert(0, freelancer_data[0])
        name_entry.pack(fill='x', pady=(0, 15))
        
        # Specialization
        ttk.Label(form_frame, text="Specialization:").pack(anchor='w', pady=(0, 5))
        specialization_entry = ttk.Entry(form_frame, width=50)
        specialization_entry.insert(0, freelancer_data[1] or "")
        specialization_entry.pack(fill='x', pady=(0, 15))
        
        # Phone
        ttk.Label(form_frame, text="Phone:").pack(anchor='w', pady=(0, 5))
        phone_entry = ttk.Entry(form_frame, width=50)
        phone_entry.insert(0, freelancer_data[2] or "")
        phone_entry.pack(fill='x', pady=(0, 15))
        
        # Address
        ttk.Label(form_frame, text="Address:").pack(anchor='w', pady=(0, 5))
        address_entry = ttk.Entry(form_frame, width=50)
        address_entry.insert(0, freelancer_data[3] or "")
        address_entry.pack(fill='x', pady=(0, 15))
        
        # Bank Details
        ttk.Label(form_frame, text="Bank Details:").pack(anchor='w', pady=(0, 5))
        bank_entry = ttk.Entry(form_frame, width=50)
        bank_entry.insert(0, freelancer_data[4] or "")
        bank_entry.pack(fill='x', pady=(0, 15))
        
        # Joined Date
        ttk.Label(form_frame, text="Joined Date *:").pack(anchor='w', pady=(0, 5))
        date_entry = ttk.Entry(form_frame, width=20)
        date_entry.insert(0, freelancer_data[5])
        date_entry.pack(anchor='w', pady=(0, 15))
        
        # Active Status
        active_var = tk.BooleanVar(value=bool(freelancer_data[6]))
        active_check = ttk.Checkbutton(form_frame, text="Active", variable=active_var)
        active_check.pack(anchor='w', pady=(0, 15))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        def update_freelancer():
            """Update the freelancer in database"""
            # Get values from entries
            full_name = name_entry.get().strip()
            specialization = specialization_entry.get().strip()
            phone = phone_entry.get().strip()
            address = address_entry.get().strip()
            bank_details = bank_entry.get().strip()
            joined_date = date_entry.get().strip()
            is_active = active_var.get()
            
            # Validation
            if not full_name:
                messagebox.showerror("Error", "Full Name is required!")
                return
            
            if not joined_date:
                messagebox.showerror("Error", "Joined Date is required!")
                return
            
            # Validate date format
            try:
                datetime.strptime(joined_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return
            
            try:
                # Update database
                query = '''
                    UPDATE freelancers 
                    SET full_name = ?, specialization = ?, phone = ?, address = ?, 
                        bank_details = ?, joined_date = ?, is_active = ?
                    WHERE freelancer_id = ?
                '''
                self.db.execute_update(query, (full_name, specialization, phone, address, bank_details, joined_date, is_active, freelancer_id))
                
                # Show success message using toast callback if available
                if self.toast_callback:
                    self.toast_callback(f"Freelancer '{full_name}' updated successfully!", success=True)
                else:
                    print(f"Freelancer '{full_name}' updated successfully!")
                
                # Refresh the freelancers list
                self.load_freelancers()
                
                # Close the window
                edit_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error updating freelancer: {str(e)}")
        
        def delete_freelancer():
            """Delete the freelancer"""
            if messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete freelancer '{freelancer_data[0]}'?\n\nThis action cannot be undone!"):
                try:
                    # Check if freelancer has work orders
                    work_order_count = self.db.execute_query('''
                        SELECT COUNT(*) FROM work_orders WHERE freelancer_id = ?
                    ''', (freelancer_id,))[0][0]
                    
                    if work_order_count > 0:
                        messagebox.showwarning("Cannot Delete", 
                                             f"Cannot delete freelancer '{freelancer_data[0]}' because they have {work_order_count} work order(s).\n\nPlease complete or reassign their work orders first.")
                        return
                    
                    # Delete freelancer
                    self.db.execute_update('DELETE FROM freelancers WHERE freelancer_id = ?', (freelancer_id,))
                    
                    if self.toast_callback:
                        self.toast_callback(f"Freelancer '{freelancer_data[0]}' deleted successfully!", success=True)
                    else:
                        print(f"Freelancer '{freelancer_data[0]}' deleted successfully!")
                    
                    # Refresh the freelancers list
                    self.load_freelancers()
                    
                    # Close the window
                    edit_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Database Error", f"Error deleting freelancer: {str(e)}")
        
        def cancel():
            """Cancel and close window"""
            edit_window.destroy()
        
        # Buttons with proper styling
        delete_btn = tk.Button(button_frame, text="🗑️ DELETE", command=delete_freelancer,
                              bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"),
                              height=2, width=18, relief="raised", bd=2, cursor="hand2")
        delete_btn.pack(side='left', padx=(0, 10))

        update_btn = tk.Button(button_frame, text="💾 UPDATE", command=update_freelancer,
                              bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"),
                              height=2, width=18, relief="raised", bd=2, cursor="hand2")
        update_btn.pack(side='right', padx=(5, 0))

        cancel_btn = tk.Button(button_frame, text="❌ CANCEL", command=cancel,
                              bg="#95a5a6", fg="white", font=("Segoe UI", 10, "bold"),
                              height=2, width=18, relief="raised", bd=2, cursor="hand2")
        cancel_btn.pack(side='right')

        # Add hover effects for buttons
        def on_enter_delete(e):
            delete_btn['bg'] = '#c0392b'
        def on_leave_delete(e):
            delete_btn['bg'] = '#e74c3c'
        def on_enter_update(e):
            update_btn['bg'] = '#2ecc71'
        def on_leave_update(e):
            update_btn['bg'] = '#27ae60'
        def on_enter_cancel(e):
            cancel_btn['bg'] = '#7f8c8d'
        def on_leave_cancel(e):
            cancel_btn['bg'] = '#95a5a6'

        delete_btn.bind("<Enter>", on_enter_delete)
        delete_btn.bind("<Leave>", on_leave_delete)
        update_btn.bind("<Enter>", on_enter_update)
        update_btn.bind("<Leave>", on_leave_update)
        cancel_btn.bind("<Enter>", on_enter_cancel)
        cancel_btn.bind("<Leave>", on_leave_cancel)
        
        # Set focus to name entry
        name_entry.focus()
        
        # Bind Enter key to update
        edit_window.bind('<Return>', lambda e: update_freelancer())
        edit_window.bind('<Escape>', lambda e: cancel())
    
    def view_freelancer_work_orders(self, parent_window):
        """View all work orders for a specific freelancer"""
        # Get selected freelancer
        selected_item = self.freelancers_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a freelancer to view work orders!")
            return
        
        # Get freelancer data
        freelancer_id = self.freelancers_tree.item(selected_item[0])['values'][0]
        freelancer_name = self.freelancers_tree.item(selected_item[0])['values'][1]
        
        # Fetch freelancer details
        freelancer_query = '''
            SELECT freelancer_id, full_name, specialization, phone, address, joined_date, is_active
            FROM freelancers
            WHERE freelancer_id = ?
        '''
        freelancer_data = self.db.execute_query(freelancer_query, (freelancer_id,))[0]
        
        if not freelancer_data:
            messagebox.showerror("Error", "Freelancer not found!")
            return
        
        # Fetch all work orders for this freelancer
        work_orders_query = '''
            SELECT wo.work_order_id, wo.jewelry_design, wo.original_metal_weight,
                   wo.gold_weight_issued, wo.expected_final_weight, wo.status, 
                   wo.issue_date, wo.expected_completion_date, wo.completion_date,
                   wo.final_jewelry_weight, wo.wastage_weight, wo.notes
            FROM work_orders wo
            WHERE wo.freelancer_id = ?
            ORDER BY wo.issue_date DESC
        '''
        work_orders = self.db.execute_query(work_orders_query, (freelancer_id,))
        
        # Create work orders view window
        work_orders_window = tk.Toplevel(parent_window)
        work_orders_window.title(f"Work Orders - {freelancer_name}")
        work_orders_window.geometry("1000x700")
        work_orders_window.transient(parent_window)
        work_orders_window.grab_set()
        work_orders_window.resizable(True, True)
        
        # Center the window on screen
        from main import GoldJewelryApp
        GoldJewelryApp.center_modal(work_orders_window, 1000, 700)
        
        # Create main frame
        main_frame = ttk.Frame(work_orders_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Work Orders for {freelancer_name}", 
                               font=("Arial", 18, "bold"), foreground="#2c3e50")
        title_label.pack(pady=(0, 20))
        
        # Freelancer info frame
        info_frame = ttk.LabelFrame(main_frame, text="Freelancer Information", padding="15")
        info_frame.pack(fill='x', pady=(0, 20))
        
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill='x')
        
        # Display freelancer information
        ttk.Label(info_grid, text="Name:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(info_grid, text=freelancer_data[1], font=("Arial", 11)).grid(row=0, column=1, sticky='w', pady=5)
        
        ttk.Label(info_grid, text="Specialization:", font=("Arial", 11, "bold")).grid(row=0, column=2, sticky='w', padx=(20, 10), pady=5)
        specialization_text = freelancer_data[2] if freelancer_data[2] else "Not specified"
        ttk.Label(info_grid, text=specialization_text, font=("Arial", 11)).grid(row=0, column=3, sticky='w', pady=5)
        
        ttk.Label(info_grid, text="Phone:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        phone_text = freelancer_data[3] if freelancer_data[3] else "Not provided"
        ttk.Label(info_grid, text=phone_text, font=("Arial", 11)).grid(row=1, column=1, sticky='w', pady=5)
        
        ttk.Label(info_grid, text="Joined Date:", font=("Arial", 11, "bold")).grid(row=1, column=2, sticky='w', padx=(20, 10), pady=5)
        ttk.Label(info_grid, text=freelancer_data[5], font=("Arial", 11)).grid(row=1, column=3, sticky='w', pady=5)
        
        ttk.Label(info_grid, text="Status:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
        status_text = "Active" if freelancer_data[6] else "Inactive"
        status_color = "#27ae60" if freelancer_data[6] else "#e74c3c"
        ttk.Label(info_grid, text=status_text, font=("Arial", 11, "bold"), foreground=status_color).grid(row=2, column=1, sticky='w', pady=5)
        
        # Work orders summary
        summary_frame = ttk.LabelFrame(main_frame, text="Work Orders Summary", padding="15")
        summary_frame.pack(fill='x', pady=(0, 20))
        
        summary_grid = ttk.Frame(summary_frame)
        summary_grid.pack(fill='x')
        
        # Calculate summary statistics
        total_orders = len(work_orders)
        completed_orders = len([wo for wo in work_orders if wo[5] == 'completed'])
        in_progress_orders = len([wo for wo in work_orders if wo[5] == 'in_progress'])
        issued_orders = len([wo for wo in work_orders if wo[5] == 'issued'])
        
        total_gold_issued = sum([wo[3] for wo in work_orders if wo[3]])
        total_final_weight = sum([wo[9] for wo in work_orders if wo[9]])
        total_wastage = sum([wo[10] for wo in work_orders if wo[10]])
        
        # Display summary
        ttk.Label(summary_grid, text="Total Orders:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(summary_grid, text=str(total_orders), font=("Arial", 11)).grid(row=0, column=1, sticky='w', pady=5)
        
        ttk.Label(summary_grid, text="Completed:", font=("Arial", 11, "bold")).grid(row=0, column=2, sticky='w', padx=(20, 10), pady=5)
        ttk.Label(summary_grid, text=str(completed_orders), font=("Arial", 11), foreground="#27ae60").grid(row=0, column=3, sticky='w', pady=5)
        
        ttk.Label(summary_grid, text="In Progress:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(summary_grid, text=str(in_progress_orders), font=("Arial", 11), foreground="#f39c12").grid(row=1, column=1, sticky='w', pady=5)
        
        ttk.Label(summary_grid, text="Issued:", font=("Arial", 11, "bold")).grid(row=1, column=2, sticky='w', padx=(20, 10), pady=5)
        ttk.Label(summary_grid, text=str(issued_orders), font=("Arial", 11), foreground="#3498db").grid(row=1, column=3, sticky='w', pady=5)
        
        ttk.Label(summary_grid, text="Total Gold Issued:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(summary_grid, text=f"{total_gold_issued:.2f} grams", font=("Arial", 11)).grid(row=2, column=1, sticky='w', pady=5)
        
        ttk.Label(summary_grid, text="Total Wastage:", font=("Arial", 11, "bold")).grid(row=2, column=2, sticky='w', padx=(20, 10), pady=5)
        ttk.Label(summary_grid, text=f"{total_wastage:.2f} grams", font=("Arial", 11)).grid(row=2, column=3, sticky='w', pady=5)
        
        # Work orders table
        table_frame = ttk.LabelFrame(main_frame, text="Work Orders Details", padding="15")
        table_frame.pack(fill='both', expand=True)
        
        # Create treeview for work orders
        columns = ('Order ID', 'Design', 'Original Metal (g)', 'Gold Issued (g)', 'Expected (g)', 
                  'Status', 'Issue Date', 'Expected Completion', 'Completion Date', 'Final Weight (g)', 'Wastage (g)')
        work_orders_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        for col in columns:
            work_orders_tree.heading(col, text=col)
            work_orders_tree.column(col, width=100, minwidth=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=work_orders_tree.yview)
        work_orders_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        work_orders_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Populate work orders data
        for wo in work_orders:
            completion_date = wo[8] if wo[8] else "Pending"
            final_weight = f"{wo[9]:.2f}" if wo[9] else "N/A"
            wastage = f"{wo[10]:.2f}" if wo[10] else "N/A"
            
            # Color code status
            status = wo[5]
            if status == 'completed':
                status_color = "#27ae60"
            elif status == 'in_progress':
                status_color = "#f39c12"
            else:
                status_color = "#3498db"
            
            work_orders_tree.insert('', 'end', values=(
                wo[0],  # Order ID
                wo[1] or "Not specified",  # Design
                f"{wo[2]:.2f}",  # Original Metal
                f"{wo[3]:.2f}",  # Gold Issued
                f"{wo[4]:.2f}",  # Expected
                status.upper(),  # Status
                wo[6],  # Issue Date
                wo[7] or "Not set",  # Expected Completion
                completion_date,  # Completion Date
                final_weight,  # Final Weight
                wastage  # Wastage
            ))
        
        # Close button
        close_btn = tk.Button(main_frame, text="❌ CLOSE", command=work_orders_window.destroy,
                            bg="#95a5a6", fg="white", font=("Segoe UI", 10, "bold"),
                            height=2, width=18, relief="raised", bd=2, cursor="hand2")
        close_btn.pack(pady=(20, 0))
        
        # Add hover effect
        def on_enter_close(e):
            close_btn['bg'] = '#7f8c8d'
        def on_leave_close(e):
            close_btn['bg'] = '#95a5a6'
        
        close_btn.bind("<Enter>", on_enter_close)
        close_btn.bind("<Leave>", on_leave_close)
        
        # Bind escape key to close
        work_orders_window.bind('<Escape>', lambda e: work_orders_window.destroy())
