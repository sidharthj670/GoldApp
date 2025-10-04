"""
Work Order module for Gold Jewelry Business Management System
Handles all work order-related operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import DatabaseManager

class WorkOrderManager:
    def __init__(self, db_manager, main_app=None):
        """Initialize work order manager with database connection and optional main app reference"""
        self.db = db_manager
        self.main_app = main_app
        self.work_orders_tree = None
    
    def set_work_orders_tree(self, tree):
        """Set the work orders treeview widget"""
        self.work_orders_tree = tree
    
    def load_work_orders(self):
        """Load work orders data into treeview"""
        if not self.work_orders_tree:
            return
            
        # Clear existing items
        for item in self.work_orders_tree.get_children():
            self.work_orders_tree.delete(item)
        
        try:
            # Load data from database
            query = '''
                SELECT wo.work_order_id, f.full_name, wo.jewelry_design, wo.original_metal_weight,
                       wo.gold_weight_issued, wo.expected_final_weight, wo.status, wo.issue_date, wo.completion_date
                FROM work_orders wo
                JOIN freelancers f ON wo.freelancer_id = f.freelancer_id
                ORDER BY wo.issue_date DESC
            '''
            rows = self.db.execute_query(query)
            
            for row in rows:
                completion_date = row[8] if row[8] else "Pending"
                self.work_orders_tree.insert('', 'end', values=(
                    row[0], row[1], row[2], 
                    f"{row[3]:.2f}", f"{row[4]:.2f}", f"{row[5]:.2f}", 
                    row[6], row[7], completion_date
                ))
        except Exception as e:
            print(f"Error loading work orders: {e}")
            messagebox.showerror("Database Error", f"Error loading work orders: {str(e)}")
    
    def new_work_order(self, parent_window):
        """Create new work order"""
        # Check if we have freelancers and gold inventory
        freelancer_count = self.db.execute_query("SELECT COUNT(*) FROM freelancers WHERE is_active = 1")[0][0]
        gold_count = self.db.execute_query("SELECT COUNT(*) FROM gold_inventory")[0][0]
        
        if freelancer_count == 0:
            messagebox.showwarning("Warning", "No active freelancers found!\nPlease add freelancers first.")
            return
            
        if gold_count == 0:
            messagebox.showwarning("Warning", "No gold inventory found!\nPlease add gold to inventory first.")
            return
        
        # Create work order window
        work_window = tk.Toplevel(parent_window)
        work_window.title("Create New Work Order")
        work_window.geometry("600x750")
        work_window.transient(parent_window)
        work_window.grab_set()
        work_window.resizable(False, False)
        
        # Center the window on screen
        from main import GoldJewelryApp
        GoldJewelryApp.center_modal(work_window, 600, 750)
        
        # Debug: Print window info
        print(f"Work order window created: {work_window.winfo_name()}")
        print(f"Window geometry: {work_window.geometry()}")
        
        # Center the window
        work_window.geometry("+%d+%d" % (parent_window.winfo_rootx() + 50, parent_window.winfo_rooty() + 50))
        
        # Create main frame
        main_frame = ttk.Frame(work_window, padding="25")
        main_frame.pack(fill='both', expand=True)
        
        # Debug: Print main frame info
        print(f"Main frame created and packed")
        
        # Create header frame for title and buttons
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 25))
        
        # Title on the left
        title_label = ttk.Label(header_frame, text="Create New Work Order", 
                               font=("Arial", 18, "bold"), foreground="#2c3e50")
        title_label.pack(side='left')
        
        # Buttons frame on the right
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side='right')
        
        # Debug: Print button frame info
        print(f"Button frame created and packed")
        
        # Button frame is now in the header
        
        # Create form fields
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='x', expand=True)
        
        # Freelancer Selection
        freelancer_frame = ttk.Frame(form_frame)
        freelancer_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(freelancer_frame, text="Select Freelancer *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        
        # Get active freelancers
        freelancers = self.db.execute_query("SELECT freelancer_id, full_name FROM freelancers WHERE is_active = 1 ORDER BY full_name")
        
        freelancer_var = tk.StringVar()
        freelancer_combo = ttk.Combobox(freelancer_frame, textvariable=freelancer_var, 
                                       values=[f"{f[1]}" for f in freelancers], 
                                       state="readonly", width=40, font=("Arial", 11))
        freelancer_combo.pack(fill='x')
        
        # Jewelry Design
        design_frame = ttk.Frame(form_frame)
        design_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(design_frame, text="Jewelry Design", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        design_entry = ttk.Entry(design_frame, width=40, font=("Arial", 11))
        design_entry.pack(fill='x')
        
        # Total Metal Weight
        total_weight_frame = ttk.Frame(form_frame)
        total_weight_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(total_weight_frame, text="Total Metal Weight (grams) *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        total_weight_entry = ttk.Entry(total_weight_frame, width=40, font=("Arial", 11))
        total_weight_entry.pack(fill='x')
        
        # Gold Percentage
        gold_percent_frame = ttk.Frame(form_frame)
        gold_percent_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(gold_percent_frame, text="Gold Percentage (%) *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        gold_percent_entry = ttk.Entry(gold_percent_frame, width=40, font=("Arial", 11))
        gold_percent_entry.pack(fill='x')
        
        # Calculated Gold Weight (read-only)
        calculated_weight_frame = ttk.Frame(form_frame)
        calculated_weight_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(calculated_weight_frame, text="Calculated Gold Weight (grams)", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        calculated_weight_label = ttk.Label(calculated_weight_frame, text="0.00", 
                                          font=("Arial", 11), foreground="#7f8c8d")
        calculated_weight_label.pack(anchor='w')
        
        # Form of Gold
        form_frame_gold = ttk.Frame(form_frame)
        form_frame_gold.pack(fill='x', pady=(0, 20))
        
        ttk.Label(form_frame_gold, text="Form of Gold *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        
        form_var = tk.StringVar()
        form_combo = ttk.Combobox(form_frame_gold, textvariable=form_var, 
                                 values=['raw', 'ring', 'earing', 'other'], 
                                 state="readonly", width=40, font=("Arial", 11))
        form_combo.pack(fill='x')
        
        # Expected Final Weight
        expected_frame = ttk.Frame(form_frame)
        expected_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(expected_frame, text="Expected Final Weight (grams) *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        expected_entry = ttk.Entry(expected_frame, width=40, font=("Arial", 11))
        expected_entry.pack(fill='x')
        
        # Expected Completion Date
        completion_frame = ttk.Frame(form_frame)
        completion_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(completion_frame, text="Expected Completion Date", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        completion_entry = ttk.Entry(completion_frame, width=20, font=("Arial", 11))
        completion_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        completion_entry.pack(anchor='w')
        ttk.Label(completion_frame, text="(YYYY-MM-DD format)", 
                 font=("Arial", 9), foreground="#7f8c8d").pack(anchor='w', pady=(2, 0))
        
        # Special Instructions
        instructions_frame = ttk.Frame(form_frame)
        instructions_frame.pack(fill='x', pady=(0, 25))
        
        ttk.Label(instructions_frame, text="Special Instructions", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        instructions_text = tk.Text(instructions_frame, height=3, width=40, font=("Arial", 11))
        instructions_text.pack(fill='x')
        
        # Function to calculate gold weight
        def calculate_gold_weight(*args):
            try:
                total_weight = float(total_weight_entry.get() or 0)
                gold_percent = float(gold_percent_entry.get() or 0)
                if total_weight > 0 and gold_percent > 0:
                    gold_weight = (total_weight * gold_percent) / 100
                    calculated_weight_label.config(text=f"{gold_weight:.2f}")
                else:
                    calculated_weight_label.config(text="0.00")
            except ValueError:
                calculated_weight_label.config(text="0.00")
        
        # Bind calculation to weight and percentage fields
        total_weight_entry.bind('<KeyRelease>', calculate_gold_weight)
        gold_percent_entry.bind('<KeyRelease>', calculate_gold_weight)
        
        def create_work_order():
            """Create the work order"""
            # Get values
            freelancer_name = freelancer_var.get()
            jewelry_design = design_entry.get().strip()
            total_weight = total_weight_entry.get().strip()
            gold_percent = gold_percent_entry.get().strip()
            calculated_gold_weight = calculated_weight_label.cget("text")
            form = form_var.get()
            expected_weight = expected_entry.get().strip()
            completion_date = completion_entry.get().strip()
            special_instructions = instructions_text.get(1.0, tk.END).strip()
            
            # Validation
            if not freelancer_name:
                messagebox.showerror("Error", "Please select a freelancer!")
                return
                
            if not total_weight or not total_weight.replace('.', '').isdigit():
                messagebox.showerror("Error", "Please enter a valid total metal weight!")
                total_weight_entry.focus()
                return
                
            if not gold_percent or not gold_percent.replace('.', '').isdigit():
                messagebox.showerror("Error", "Please enter a valid gold percentage!")
                gold_percent_entry.focus()
                return
                
            if not form:
                messagebox.showerror("Error", "Please select a form of gold!")
                return
                
            if not expected_weight or not expected_weight.replace('.', '').isdigit():
                messagebox.showerror("Error", "Please enter a valid expected weight!")
                expected_entry.focus()
                return
            
            try:
                total_weight = float(total_weight)
                gold_percent = float(gold_percent)
                expected_weight = float(expected_weight)
                
                if total_weight <= 0:
                    messagebox.showerror("Error", "Total metal weight must be greater than 0!")
                    total_weight_entry.focus()
                    return
                    
                if gold_percent <= 0 or gold_percent > 100:
                    messagebox.showerror("Error", "Gold percentage must be between 0 and 100!")
                    gold_percent_entry.focus()
                    return
                    
                if expected_weight <= 0:
                    messagebox.showerror("Error", "Expected final weight must be greater than 0!")
                    expected_entry.focus()
                    return
                    
                if expected_weight > total_weight:
                    messagebox.showerror("Error", "Expected final weight cannot be greater than total metal weight!")
                    return
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values!")
                return
            
            # Validate completion date
            if completion_date:
                try:
                    datetime.strptime(completion_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Invalid completion date format! Use YYYY-MM-DD")
                    return
            
            try:
                # Get freelancer ID
                freelancer_id = None
                for f in freelancers:
                    if f[1] == freelancer_name:
                        freelancer_id = f[0]
                        break
                
                # Use default gold type (24K) and insert into inventory if needed
                # For now, we'll use gold_type_id = 1 (24K) as default
                gold_type_id = 1
                
                # Check if enough gold is available
                available_gold = self.db.execute_query('''
                    SELECT SUM(weight_grams) FROM gold_inventory 
                    WHERE gold_type_id = ?
                ''', (gold_type_id,))[0][0] or 0
                
                required_gold = float(calculated_gold_weight)
                
                if available_gold < required_gold:
                    messagebox.showerror("Error", 
                                       f"Not enough 24K gold available!\n"
                                       f"Available: {available_gold:.2f} grams\n"
                                       f"Required: {required_gold:.2f} grams")
                    return
                
                # Create work order
                work_order_query = '''
                    INSERT INTO work_orders (freelancer_id, gold_type_id, jewelry_design, 
                                           original_metal_weight, gold_weight_issued, expected_final_weight, 
                                           issue_date, expected_completion_date, 
                                           status, special_instructions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'issued', ?)
                '''
                self.db.execute_update(work_order_query, (freelancer_id, gold_type_id, jewelry_design, total_weight, required_gold, 
                      expected_weight, datetime.now().strftime("%Y-%m-%d"), 
                      completion_date, special_instructions))
                
                # Note: Gold inventory is now managed without availability tracking
                # The work order tracks the gold issued, but inventory remains unchanged
                
                if self.main_app:
                    self.main_app.show_toast(f"Work order created successfully! • Freelancer: {freelancer_name} • Design: {jewelry_design} • Total Metal: {total_weight:.2f}g • Gold Weight: {required_gold:.2f}g", success=True)
                else:
                    print(f"Work order created successfully! Freelancer: {freelancer_name}, Design: {jewelry_design}, Total Metal: {total_weight:.2f} grams, Gold Weight: {required_gold:.2f} grams")
                
                # Refresh data
                self.load_work_orders()
                
                # Close window
                work_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error creating work order: {str(e)}")
        
        def cancel():
            """Cancel and close window"""
            work_window.destroy()
        
        # Create and Cancel buttons in header
        print("Creating SAVE button...")
        create_btn = tk.Button(button_frame, text="💾 SAVE", command=create_work_order, 
                             bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), 
                             height=2, width=18, relief="raised", bd=2, cursor="hand2")
        create_btn.pack(side='right', padx=(10, 0))
        print("SAVE button created and packed")
        
        print("Creating CANCEL button...")
        cancel_btn = tk.Button(button_frame, text="❌ CANCEL", command=cancel, 
                             bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), 
                             height=2, width=18, relief="raised", bd=2, cursor="hand2")
        cancel_btn.pack(side='right')
        print("CANCEL button created and packed")
        
        # Force update the window
        work_window.update()
        print("Window updated")
        
        # Add hover effects
        def on_enter_create(e):
            create_btn['bg'] = '#2ecc71'
        def on_leave_create(e):
            create_btn['bg'] = '#27ae60'
        def on_enter_cancel(e):
            cancel_btn['bg'] = '#c0392b'
        def on_leave_cancel(e):
            cancel_btn['bg'] = '#e74c3c'
        
        create_btn.bind("<Enter>", on_enter_create)
        create_btn.bind("<Leave>", on_leave_create)
        cancel_btn.bind("<Enter>", on_enter_cancel)
        cancel_btn.bind("<Leave>", on_leave_cancel)
        
        # Add instruction text below the header
        instruction_label = ttk.Label(main_frame, text="* Required fields", 
                                     font=("Arial", 9), foreground="#7f8c8d")
        instruction_label.pack(anchor='w', pady=(0, 10))
        
        # Set focus and bind keys
        design_entry.focus()
        work_window.bind('<Return>', lambda e: create_work_order())
        work_window.bind('<Escape>', lambda e: cancel())
        
        # Final debug and window configuration
        print("Work order window setup complete")
        print(f"Button frame children count: {len(button_frame.winfo_children())}")
        print(f"Main frame children count: {len(main_frame.winfo_children())}")
        
        # Ensure window is visible and properly configured
        work_window.deiconify()
        work_window.lift()
        work_window.focus_force()
    
    def update_work_order(self, parent_window):
        """Update work order status"""
        # Get selected work order
        selected_item = self.work_orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a work order to update!")
            return
        
        # Get work order data
        work_order_id = self.work_orders_tree.item(selected_item[0])['values'][0]
        
        # Fetch work order details
        query = '''
            SELECT wo.work_order_id, f.full_name, wo.jewelry_design, wo.original_metal_weight,
                   wo.gold_weight_issued, wo.expected_final_weight, wo.status, wo.issue_date, wo.completion_date,
                   wo.special_instructions
            FROM work_orders wo
            JOIN freelancers f ON wo.freelancer_id = f.freelancer_id
            WHERE wo.work_order_id = ?
        '''
        work_order_data = self.db.execute_query(query, (work_order_id,))[0]
        
        if not work_order_data:
            messagebox.showerror("Error", "Work order not found!")
            return
        
        # Create update window
        update_window = tk.Toplevel(parent_window)
        update_window.title("Update Work Order Status")
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
        title_label = ttk.Label(main_frame, text="Update Work Order Status", 
                               font=("Arial", 16, "bold"), foreground="#2c3e50")
        title_label.pack(pady=(0, 20))
        
        # Work order info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(info_frame, text=f"Order ID: {work_order_data[0]}", 
                 font=("Arial", 11, "bold")).pack(anchor='w')
        ttk.Label(info_frame, text=f"Freelancer: {work_order_data[1]}", 
                 font=("Arial", 11)).pack(anchor='w')
        ttk.Label(info_frame, text=f"Design: {work_order_data[2]}", 
                 font=("Arial", 11)).pack(anchor='w')
        ttk.Label(info_frame, text=f"Original Metal: {work_order_data[3]:.2f} grams", 
                 font=("Arial", 11)).pack(anchor='w')
        ttk.Label(info_frame, text=f"Gold Issued: {work_order_data[4]:.2f} grams", 
                 font=("Arial", 11)).pack(anchor='w')
        
        # Status selection
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(status_frame, text="New Status *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        
        status_var = tk.StringVar(value=work_order_data[6])
        status_combo = ttk.Combobox(status_frame, textvariable=status_var, 
                                   values=['issued', 'in_progress', 'completed', 'cancelled'], 
                                   state="readonly", width=30, font=("Arial", 11))
        status_combo.pack(fill='x')
        
        # Notes
        notes_frame = ttk.Frame(main_frame)
        notes_frame.pack(fill='x', pady=(0, 25))
        
        ttk.Label(notes_frame, text="Update Notes", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        notes_text = tk.Text(notes_frame, height=3, width=40, font=("Arial", 11))
        notes_text.pack(fill='x')
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        def update_status():
            """Update the work order status"""
            new_status = status_var.get()
            notes = notes_text.get(1.0, tk.END).strip()
            
            if not new_status:
                messagebox.showerror("Error", "Please select a status!")
                return
            
            try:
                # Prepare update query based on status
                if new_status == 'completed':
                    # If status is completed, set completion date
                    query = '''
                        UPDATE work_orders 
                        SET status = ?, notes = ?, completion_date = ?
                        WHERE work_order_id = ?
                    '''
                    completion_date = datetime.now().strftime("%Y-%m-%d")
                    self.db.execute_update(query, (new_status, notes, completion_date, work_order_id))
                    if self.main_app:
                        self.main_app.show_toast(f"Work order status updated to: {new_status} • Completion date: {completion_date}", success=True)
                    else:
                        print(f"Work order status updated to: {new_status}, Completion date: {completion_date}")
                else:
                    # For other statuses, don't set completion date
                    query = '''
                        UPDATE work_orders
                        SET status = ?, notes = ?
                        WHERE work_order_id = ?
                    '''
                    self.db.execute_update(query, (new_status, notes, work_order_id))
                    if self.main_app:
                        self.main_app.show_toast(f"Work order status updated to: {new_status}", success=True)
                    else:
                        print(f"Work order status updated to: {new_status}")
                
                # Refresh data
                self.load_work_orders()
                
                # Close window
                update_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error updating work order: {str(e)}")
        
        def cancel():
            """Cancel and close window"""
            update_window.destroy()
        
        # Update and Cancel buttons - centered
        update_btn = tk.Button(button_frame, text="✏️ UPDATE", command=update_status, 
                             bg="#f39c12", fg="white", font=("Segoe UI", 10, "bold"), 
                             height=2, width=18, relief="raised", bd=2, cursor="hand2")
        update_btn.pack(side='left', padx=(0, 10))
        
        cancel_btn = tk.Button(button_frame, text="❌ CANCEL", command=cancel, 
                             bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), 
                             height=2, width=18, relief="raised", bd=2, cursor="hand2")
        cancel_btn.pack(side='left')
        
        # Center the buttons
        button_frame.pack_configure(anchor='center')
        
        # Add hover effects
        def on_enter_update(e):
            update_btn['bg'] = '#e67e22'
        def on_leave_update(e):
            update_btn['bg'] = '#f39c12'
        
        update_btn.bind("<Enter>", on_enter_update)
        update_btn.bind("<Leave>", on_leave_update)
        
        # Set focus and bind keys
        status_combo.focus()
        update_window.bind('<Return>', lambda e: update_status())
        update_window.bind('<Escape>', lambda e: cancel())
    
    def complete_work_order(self, parent_window):
        """Complete work order with final details"""
        # Get selected work order
        selected_item = self.work_orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a work order to complete!")
            return
        
        # Get work order data
        work_order_id = self.work_orders_tree.item(selected_item[0])['values'][0]
        
        # Fetch work order details
        query = '''
            SELECT wo.work_order_id, f.full_name, wo.jewelry_design, wo.original_metal_weight,
                   wo.gold_weight_issued, wo.expected_final_weight, wo.status, wo.issue_date, wo.special_instructions
            FROM work_orders wo
            JOIN freelancers f ON wo.freelancer_id = f.freelancer_id
            WHERE wo.work_order_id = ?
        '''
        work_order_data = self.db.execute_query(query, (work_order_id,))[0]
        
        if not work_order_data:
            messagebox.showerror("Error", "Work order not found!")
            return
        
        if work_order_data[6] == 'completed':
            if self.main_app:
                self.main_app.show_toast("This work order is already completed!", success=False)
            else:
                print("This work order is already completed!")
            return
        
        # Create completion window
        complete_window = tk.Toplevel(parent_window)
        complete_window.title("Complete Work Order")
        complete_window.geometry("500x600")
        complete_window.transient(parent_window)
        complete_window.grab_set()
        complete_window.resizable(False, False)
        
        # Center the window on screen
        from main import GoldJewelryApp
        GoldJewelryApp.center_modal(complete_window, 500, 600)
        
        # Create main frame
        main_frame = ttk.Frame(complete_window, padding="25")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Complete Work Order", 
                               font=("Arial", 16, "bold"), foreground="#2c3e50")
        title_label.pack(pady=(0, 20))
        
        # Work order info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(info_frame, text=f"Order ID: {work_order_data[0]}", 
                 font=("Arial", 11, "bold")).pack(anchor='w')
        ttk.Label(info_frame, text=f"Freelancer: {work_order_data[1]}", 
                 font=("Arial", 11)).pack(anchor='w')
        ttk.Label(info_frame, text=f"Design: {work_order_data[2]}", 
                 font=("Arial", 11)).pack(anchor='w')
        ttk.Label(info_frame, text=f"Original Metal: {work_order_data[3]:.2f} grams", 
                 font=("Arial", 11)).pack(anchor='w')
        ttk.Label(info_frame, text=f"Gold Issued: {work_order_data[4]:.2f} grams", 
                 font=("Arial", 11)).pack(anchor='w')
        ttk.Label(info_frame, text=f"Expected: {work_order_data[5]:.2f} grams", 
                 font=("Arial", 11)).pack(anchor='w')
        
        # Final jewelry weight
        final_weight_frame = ttk.Frame(main_frame)
        final_weight_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(final_weight_frame, text="Final Jewelry Weight (grams) *", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        final_weight_entry = ttk.Entry(final_weight_frame, width=30, font=("Arial", 11))
        final_weight_entry.pack(fill='x')
        
        # Wastage weight
        wastage_frame = ttk.Frame(main_frame)
        wastage_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(wastage_frame, text="Wastage Weight (grams)", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        wastage_entry = ttk.Entry(wastage_frame, width=30, font=("Arial", 11))
        wastage_entry.insert(0, "0.0")
        wastage_entry.pack(fill='x')
        
        # Completion notes
        notes_frame = ttk.Frame(main_frame)
        notes_frame.pack(fill='x', pady=(0, 25))
        
        ttk.Label(notes_frame, text="Completion Notes", 
                 font=("Arial", 11, "bold"), foreground="#34495e").pack(anchor='w', pady=(0, 8))
        notes_text = tk.Text(notes_frame, height=3, width=40, font=("Arial", 11))
        notes_text.pack(fill='x')
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        def complete_order():
            """Complete the work order"""
            final_weight = final_weight_entry.get().strip()
            wastage_weight = wastage_entry.get().strip()
            notes = notes_text.get(1.0, tk.END).strip()
            
            # Validation
            if not final_weight or not final_weight.replace('.', '').isdigit():
                messagebox.showerror("Error", "Please enter a valid final weight!")
                final_weight_entry.focus()
                return
            
            if not wastage_weight or not wastage_weight.replace('.', '').isdigit():
                messagebox.showerror("Error", "Please enter a valid wastage weight!")
                wastage_entry.focus()
                return
            
            try:
                final_weight = float(final_weight)
                wastage_weight = float(wastage_weight)
                
                if final_weight < 0 or wastage_weight < 0:
                    messagebox.showerror("Error", "Weights cannot be negative!")
                    return
                
                # Check if weights make sense
                total_weight = final_weight + wastage_weight
                issued_weight = work_order_data[4]  # gold_weight_issued
                
                if abs(total_weight - issued_weight) > 0.1:  # Allow small tolerance
                    messagebox.showwarning("Warning", 
                                         f"Weight mismatch!\n"
                                         f"Issued: {issued_weight:.2f} grams\n"
                                         f"Final + Wastage: {total_weight:.2f} grams\n"
                                         f"Difference: {abs(total_weight - issued_weight):.2f} grams\n\n"
                                         f"Continue anyway?")
                    
                    if not messagebox.askyesno("Confirm", "Do you want to continue with this weight mismatch?"):
                        return
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric weights!")
                return
            
            try:
                # Update work order
                query = '''
                    UPDATE work_orders 
                    SET status = 'completed', final_jewelry_weight = ?, wastage_weight = ?,
                        completion_date = ?, notes = ?
                    WHERE work_order_id = ?
                '''
                self.db.execute_update(query, (final_weight, wastage_weight, datetime.now().strftime("%Y-%m-%d"), 
                      notes, work_order_id))
                
                if self.main_app:
                    self.main_app.show_toast(f"Work order completed successfully! • Final Weight: {final_weight:.2f}g • Wastage: {wastage_weight:.2f}g • Efficiency: {(final_weight/issued_weight)*100:.1f}%", success=True)
                else:
                    print(f"Work order completed successfully! Final Weight: {final_weight:.2f} grams, Wastage: {wastage_weight:.2f} grams, Efficiency: {(final_weight/issued_weight)*100:.1f}%")
                
                # Refresh data
                self.load_work_orders()
                
                # Close window
                complete_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error completing work order: {str(e)}")
        
        def cancel():
            """Cancel and close window"""
            complete_window.destroy()
        
        # Complete and Cancel buttons - centered
        complete_btn = tk.Button(button_frame, text="✅ COMPLETE", command=complete_order, 
                               bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), 
                               height=2, width=18, relief="raised", bd=2, cursor="hand2")
        complete_btn.pack(side='left', padx=(0, 10))
        
        cancel_btn = tk.Button(button_frame, text="❌ CANCEL", command=cancel, 
                             bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), 
                             height=2, width=18, relief="raised", bd=2, cursor="hand2")
        cancel_btn.pack(side='left')
        
        # Center the buttons
        button_frame.pack_configure(anchor='center')
        
        # Add hover effects
        def on_enter_complete(e):
            complete_btn['bg'] = '#2ecc71'
        def on_leave_complete(e):
            complete_btn['bg'] = '#27ae60'
        
        complete_btn.bind("<Enter>", on_enter_complete)
        complete_btn.bind("<Leave>", on_leave_complete)
        
        # Set focus and bind keys
        final_weight_entry.focus()
        complete_window.bind('<Return>', lambda e: complete_order())
        complete_window.bind('<Escape>', lambda e: cancel())
    
    def show_work_order_details(self, parent_window):
        """Show detailed information about a work order"""
        # Get selected work order
        selected_item = self.work_orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a work order to view details!")
            return
        
        # Get work order data
        work_order_id = self.work_orders_tree.item(selected_item[0])['values'][0]
        
        # Fetch detailed work order information
        query = '''
            SELECT wo.work_order_id, f.full_name, f.phone, f.address,
                   gt.name as gold_type, wo.jewelry_design, wo.original_metal_weight,
                   wo.gold_weight_issued, wo.expected_final_weight, wo.issue_date, wo.expected_completion_date,
                   wo.status, wo.special_instructions, wo.wastage_weight,
                   wo.final_jewelry_weight, wo.completion_date, wo.notes
            FROM work_orders wo
            JOIN freelancers f ON wo.freelancer_id = f.freelancer_id
            JOIN gold_types gt ON wo.gold_type_id = gt.gold_type_id
            WHERE wo.work_order_id = ?
        '''
        
        work_order_data = self.db.execute_query(query, (work_order_id,))[0]
        
        if not work_order_data:
            messagebox.showerror("Error", "Work order not found!")
            return
        
        # Create details window
        details_window = tk.Toplevel(parent_window)
        details_window.title(f"Work Order Details - #{work_order_data[0]}")
        details_window.geometry("600x700")
        details_window.transient(parent_window)
        details_window.grab_set()
        details_window.resizable(False, False)
        
        # Center the window on screen
        from main import GoldJewelryApp
        GoldJewelryApp.center_modal(details_window, 600, 700)
        
        # Create main frame
        main_frame = ttk.Frame(details_window, padding="25")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Work Order Details - #{work_order_data[0]}", 
                               font=("Arial", 18, "bold"), foreground="#2c3e50")
        title_label.pack(pady=(0, 25))
        
        # Create scrollable frame for content
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Work Order Information
        info_frame = ttk.LabelFrame(scrollable_frame, text="Work Order Information", padding="15")
        info_frame.pack(fill='x', pady=(0, 15))
        
        # Basic details in a grid layout
        details_grid = ttk.Frame(info_frame)
        details_grid.pack(fill='x')
        
        # Row 1: Order ID and Status
        ttk.Label(details_grid, text="Order ID:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(details_grid, text=f"#{work_order_data[0]}", font=("Arial", 11)).grid(row=0, column=1, sticky='w', pady=5)
        
        ttk.Label(details_grid, text="Status:", font=("Arial", 11, "bold")).grid(row=0, column=2, sticky='w', padx=(20, 10), pady=5)
        status_text = work_order_data[11].upper()
        status_color = "#27ae60" if work_order_data[11] == "completed" else "#f39c12" if work_order_data[11] == "in_progress" else "#3498db"
        status_label = ttk.Label(details_grid, text=status_text, font=("Arial", 11, "bold"), foreground=status_color)
        status_label.grid(row=0, column=3, sticky='w', pady=5)
        
        # Row 2: Issue Date and Expected Completion
        ttk.Label(details_grid, text="Issue Date:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(details_grid, text=work_order_data[8], font=("Arial", 11)).grid(row=1, column=1, sticky='w', pady=5)
        
        ttk.Label(details_grid, text="Expected Completion:", font=("Arial", 11, "bold")).grid(row=1, column=2, sticky='w', padx=(20, 10), pady=5)
        expected_date = work_order_data[10] if work_order_data[10] else "Not set"
        ttk.Label(details_grid, text=expected_date, font=("Arial", 11)).grid(row=1, column=3, sticky='w', pady=5)
        
        # Row 3: Completion Date (if completed)
        if work_order_data[15]:  # completion_date
            ttk.Label(details_grid, text="Completion Date:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
            ttk.Label(details_grid, text=work_order_data[15], font=("Arial", 11), foreground="#27ae60").grid(row=2, column=1, sticky='w', pady=5)
        
        # Freelancer Information
        freelancer_frame = ttk.LabelFrame(scrollable_frame, text="Freelancer Information", padding="15")
        freelancer_frame.pack(fill='x', pady=(0, 15))
        
        freelancer_grid = ttk.Frame(freelancer_frame)
        freelancer_grid.pack(fill='x')
        
        ttk.Label(freelancer_grid, text="Name:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(freelancer_grid, text=work_order_data[1], font=("Arial", 11)).grid(row=0, column=1, sticky='w', pady=5)
        
        ttk.Label(freelancer_grid, text="Phone:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        phone_text = work_order_data[2] if work_order_data[2] else "Not provided"
        ttk.Label(freelancer_grid, text=phone_text, font=("Arial", 11)).grid(row=1, column=1, sticky='w', pady=5)
        
        ttk.Label(freelancer_grid, text="Address:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
        address_text = work_order_data[3] if work_order_data[3] else "Not provided"
        ttk.Label(freelancer_grid, text=address_text, font=("Arial", 11)).grid(row=2, column=1, sticky='w', pady=5)
        
        # Order Details
        order_frame = ttk.LabelFrame(scrollable_frame, text="Order Details", padding="15")
        order_frame.pack(fill='x', pady=(0, 15))
        
        order_grid = ttk.Frame(order_frame)
        order_grid.pack(fill='x')
        
        ttk.Label(order_grid, text="Jewelry Design:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        design_text = work_order_data[5] if work_order_data[5] else "Not specified"
        ttk.Label(order_grid, text=design_text, font=("Arial", 11)).grid(row=0, column=1, sticky='w', pady=5)
        
        ttk.Label(order_grid, text="Gold Type:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(order_grid, text=work_order_data[4], font=("Arial", 11)).grid(row=1, column=1, sticky='w', pady=5)
        
        ttk.Label(order_grid, text="Original Metal:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(order_grid, text=f"{work_order_data[6]:.2f} grams", font=("Arial", 11)).grid(row=2, column=1, sticky='w', pady=5)
        
        ttk.Label(order_grid, text="Gold Issued:", font=("Arial", 11, "bold")).grid(row=3, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(order_grid, text=f"{work_order_data[7]:.2f} grams", font=("Arial", 11)).grid(row=3, column=1, sticky='w', pady=5)
        
        ttk.Label(order_grid, text="Expected Weight:", font=("Arial", 11, "bold")).grid(row=4, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(order_grid, text=f"{work_order_data[8]:.2f} grams", font=("Arial", 11)).grid(row=4, column=1, sticky='w', pady=5)
        
        # Final results (if completed)
        if work_order_data[11] == "completed":
            final_frame = ttk.LabelFrame(scrollable_frame, text="Final Results", padding="15")
            final_frame.pack(fill='x', pady=(0, 15))
            
            final_grid = ttk.Frame(final_frame)
            final_grid.pack(fill='x')
            
            ttk.Label(final_grid, text="Final Weight:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
            final_weight = work_order_data[14] if work_order_data[14] else 0
            ttk.Label(final_grid, text=f"{final_weight:.2f} grams", font=("Arial", 11)).grid(row=0, column=1, sticky='w', pady=5)
            
            ttk.Label(final_grid, text="Wastage:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
            wastage = work_order_data[13] if work_order_data[13] else 0
            ttk.Label(final_grid, text=f"{wastage:.2f} grams", font=("Arial", 11)).grid(row=1, column=1, sticky='w', pady=5)
            
            # Calculate efficiency
            if work_order_data[7] > 0:  # gold_weight_issued
                efficiency = (final_weight / work_order_data[7]) * 100
                ttk.Label(final_grid, text="Efficiency:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
                ttk.Label(final_grid, text=f"{efficiency:.1f}%", font=("Arial", 11), foreground="#27ae60").grid(row=2, column=1, sticky='w', pady=5)
        
        # Special Instructions
        if work_order_data[12]:  # special_instructions
            instructions_frame = ttk.LabelFrame(scrollable_frame, text="Special Instructions", padding="15")
            instructions_frame.pack(fill='x', pady=(0, 15))
            
            instructions_text = tk.Text(instructions_frame, height=3, width=60, font=("Arial", 10), wrap='word')
            instructions_text.pack(fill='x')
            instructions_text.insert('1.0', work_order_data[12])
            instructions_text.config(state='disabled')
        
        # Notes
        if work_order_data[16]:  # notes
            notes_frame = ttk.LabelFrame(scrollable_frame, text="Notes", padding="15")
            notes_frame.pack(fill='x', pady=(0, 15))
            
            notes_text = tk.Text(notes_frame, height=3, width=60, font=("Arial", 10), wrap='word')
            notes_text.pack(fill='x')
            notes_text.insert('1.0', work_order_data[16])
            notes_text.config(state='disabled')
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        close_btn = tk.Button(main_frame, text="❌ CLOSE", command=details_window.destroy,
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
        details_window.bind('<Escape>', lambda e: details_window.destroy())
    
    def delete_work_order(self, parent_window):
        """Delete a work order with confirmation"""
        # Get selected work order
        selected_item = self.work_orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a work order to delete!")
            return
        
        # Get work order data
        work_order_id = self.work_orders_tree.item(selected_item[0])['values'][0]
        
        # Fetch work order details for confirmation
        query = '''
            SELECT wo.work_order_id, f.full_name, wo.jewelry_design, wo.original_metal_weight,
                   wo.gold_weight_issued, wo.status, wo.issue_date
            FROM work_orders wo
            JOIN freelancers f ON wo.freelancer_id = f.freelancer_id
            WHERE wo.work_order_id = ?
        '''
        work_order_data = self.db.execute_query(query, (work_order_id,))[0]
        
        if not work_order_data:
            messagebox.showerror("Error", "Work order not found!")
            return
        
        # Check if work order can be deleted
        status = work_order_data[5]
        if status == "completed":
            messagebox.showwarning("Cannot Delete", 
                                 f"Cannot delete completed work order #{work_order_data[0]}!\n\n"
                                 f"Completed work orders should be kept for record keeping.\n"
                                 f"If you need to modify this order, please contact your administrator.")
            return
        
        # Create confirmation dialog
        confirm_window = tk.Toplevel(parent_window)
        confirm_window.title("Confirm Work Order Deletion")
        confirm_window.geometry("500x600")
        confirm_window.transient(parent_window)
        confirm_window.grab_set()
        confirm_window.resizable(False, False)
        
        # Center the window on screen
        from main import GoldJewelryApp
        GoldJewelryApp.center_modal(confirm_window, 500, 600)
        
        # Create main frame
        main_frame = ttk.Frame(confirm_window, padding="25")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Confirm Work Order Deletion", 
                               font=("Arial", 16, "bold"), foreground="#e74c3c")
        title_label.pack(pady=(0, 20))
        
        # Warning message
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill='x', pady=(0, 20))
        
        warning_label = ttk.Label(warning_frame, 
                                 text="⚠️ WARNING: This action cannot be undone!",
                                 font=("Arial", 12, "bold"), foreground="#e74c3c")
        warning_label.pack()
        
        # Work order details
        details_frame = ttk.LabelFrame(main_frame, text="Work Order Details", padding="15")
        details_frame.pack(fill='x', pady=(0, 20))
        
        details_grid = ttk.Frame(details_frame)
        details_grid.pack(fill='x')
        
        # Display work order information
        ttk.Label(details_grid, text="Order ID:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(details_grid, text=f"#{work_order_data[0]}", font=("Arial", 11)).grid(row=0, column=1, sticky='w', pady=5)
        
        ttk.Label(details_grid, text="Freelancer:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(details_grid, text=work_order_data[1], font=("Arial", 11)).grid(row=1, column=1, sticky='w', pady=5)
        
        ttk.Label(details_grid, text="Design:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
        design_text = work_order_data[2] if work_order_data[2] else "Not specified"
        ttk.Label(details_grid, text=design_text, font=("Arial", 11)).grid(row=2, column=1, sticky='w', pady=5)
        
        ttk.Label(details_grid, text="Original Metal:", font=("Arial", 11, "bold")).grid(row=3, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(details_grid, text=f"{work_order_data[3]:.2f} grams", font=("Arial", 11)).grid(row=3, column=1, sticky='w', pady=5)
        
        ttk.Label(details_grid, text="Gold Issued:", font=("Arial", 11, "bold")).grid(row=4, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(details_grid, text=f"{work_order_data[4]:.2f} grams", font=("Arial", 11)).grid(row=4, column=1, sticky='w', pady=5)
        
        ttk.Label(details_grid, text="Status:", font=("Arial", 11, "bold")).grid(row=5, column=0, sticky='w', padx=(0, 10), pady=5)
        status_color = "#f39c12" if status == "in_progress" else "#3498db"
        ttk.Label(details_grid, text=status.upper(), font=("Arial", 11, "bold"), foreground=status_color).grid(row=5, column=1, sticky='w', pady=5)
        
        ttk.Label(details_grid, text="Issue Date:", font=("Arial", 11, "bold")).grid(row=6, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(details_grid, text=work_order_data[6], font=("Arial", 11)).grid(row=6, column=1, sticky='w', pady=5)
        
        # Confirmation message
        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.pack(fill='x', pady=(0, 20))
        
        confirm_label = ttk.Label(confirm_frame, 
                                 text="Are you sure you want to delete this work order?\nThis will permanently remove all associated data.",
                                 font=("Arial", 11), foreground="#2c3e50")
        confirm_label.pack()
        
        # Add separator before buttons
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=(10, 20))
        
        def confirm_delete():
            """Confirm and delete the work order"""
            try:
                # Delete the work order
                delete_query = "DELETE FROM work_orders WHERE work_order_id = ?"
                self.db.execute_update(delete_query, (work_order_id,))
                
                if self.main_app:
                    self.main_app.show_toast(f"Work order #{work_order_data[0]} deleted successfully!", success=True)
                else:
                    print(f"Work order #{work_order_data[0]} deleted successfully!")
                
                # Refresh the work orders list
                self.load_work_orders()
                
                # Close the confirmation window
                confirm_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error deleting work order: {str(e)}")
        
        def cancel_delete():
            """Cancel the deletion"""
            confirm_window.destroy()
        
        # Buttons frame - simple centered layout
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 20))
        
        # Delete and Cancel buttons - centered
        print("Creating DELETE button...")  # Debug print
        delete_btn = tk.Button(button_frame, text="🗑️ DELETE", command=confirm_delete, 
                             bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), 
                             height=2, width=18, relief="raised", bd=2, cursor="hand2")
        delete_btn.pack(side='left', padx=(0, 10))
        print("DELETE button created and packed")  # Debug print
        
        print("Creating CANCEL button...")  # Debug print
        cancel_btn = tk.Button(button_frame, text="❌ CANCEL", command=cancel_delete, 
                             bg="#95a5a6", fg="white", font=("Segoe UI", 10, "bold"), 
                             height=2, width=18, relief="raised", bd=2, cursor="hand2")
        cancel_btn.pack(side='left')
        print("CANCEL button created and packed")  # Debug print
        
        # Center the buttons
        button_frame.pack_configure(anchor='center')
        
        # Add a test label to verify the frame is working
        test_label = ttk.Label(button_frame, text="Buttons should be above this text", 
                              font=("Arial", 9), foreground="#7f8c8d")
        test_label.pack(pady=(10, 0))
        
        # Add hover effects
        def on_enter_delete(e):
            delete_btn['bg'] = '#c0392b'
        
        def on_leave_delete(e):
            delete_btn['bg'] = '#e74c3c'
        
        def on_enter_cancel(e):
            cancel_btn['bg'] = '#7f8c8d'
        
        def on_leave_cancel(e):
            cancel_btn['bg'] = '#95a5a6'
        
        delete_btn.bind("<Enter>", on_enter_delete)
        delete_btn.bind("<Leave>", on_leave_delete)
        cancel_btn.bind("<Enter>", on_enter_cancel)
        cancel_btn.bind("<Leave>", on_leave_cancel)
        
        # Force update the window to ensure buttons are visible
        confirm_window.update()
        print("Window updated, buttons should be visible now")  # Debug print
        
        # Ensure window is visible and properly configured
        confirm_window.deiconify()
        confirm_window.lift()
        confirm_window.focus_force()
        
        # Set focus and bind keys
        cancel_btn.focus()
        confirm_window.bind('<Escape>', lambda e: cancel_delete())
