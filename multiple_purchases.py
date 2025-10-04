import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class MultiplePurchasesManager:
    def __init__(self, root_window, main_app, db_manager, colors, fonts):
        self.root_window = root_window  # Tkinter root window for creating modals
        self.main_app = main_app        # Main application object for calling methods
        self.db = db_manager
        self.COLORS = colors
        self.FONTS = fonts
        self.purchase_rows = []
        self.instance_id = id(self)  # Unique identifier for this instance
        self.session_ref_counter = 0  # Counter for Ref IDs in current session
        print(f"MultiplePurchasesManager instance created with ID: {self.instance_id}")
        
    def show_multiple_purchases_modal(self):
        """Show full-screen modal for adding multiple purchases with table interface
        Uses screen-level supplier and one Ref ID for the whole transaction.
        """
        print(f"=== OPENING MULTIPLE PURCHASES MODAL ===")
        print(f"Initial purchase_rows length: {len(self.purchase_rows)}")
        print(f"Initial purchase_rows id: {id(self.purchase_rows)}")
        
        # Create modal at 80% of screen
        modal = tk.Toplevel(self.root_window)
        modal.title("Add Multiple Purchases - Table View")
        modal.update_idletasks()
        sw = modal.winfo_screenwidth()
        sh = modal.winfo_screenheight()
        mw = int(sw * 0.8)
        mh = int(sh * 0.8)
        mx = (sw - mw) // 2
        my = (sh - mh) // 2
        modal.geometry(f"{mw}x{mh}+{mx}+{my}")
        modal.transient(self.root_window)
        modal.grab_set()
        
        # Main frame
        main_frame = tk.Frame(modal, bg=self.COLORS['light'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="Add Multiple Purchases - Table View",
                              font=self.FONTS['heading'],
                              fg=self.COLORS['primary'],
                              bg=self.COLORS['light'])
        title_label.pack(pady=(0, 10))
        
        # Generate a transaction Ref ID once (P...)
        self.transaction_ref_id = self.generate_ref_id('P')
        
        # Check if this Ref ID already exists (prevent duplicate transaction)
        if not self.check_ref_id_exists():
            modal.destroy()
            return
        
        # Instructions (top)
        top_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        top_frame.pack(fill='x', pady=(0, 10))
        
        # Instructions on the left
        instructions_label = tk.Label(top_frame, 
                                     text="Instructions: Fill in the table below. Use 'Add Row' to create more entries.",
                                     font=self.FONTS['body'],
                                     fg=self.COLORS['dark'],
                                     bg=self.COLORS['light'])
        instructions_label.pack(side='left')
        
        # Note: Save/Add Row buttons moved to bottom

        # Screen-level supplier dropdown (Supplier: [dropdown])
        supplier_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        supplier_frame.pack(fill='x', pady=(0, 10))
        supplier_label = tk.Label(supplier_frame,
                                  text="Supplier:",
                                  font=self.FONTS['body'],
                                  fg=self.COLORS['dark'],
                                  bg=self.COLORS['light'])
        supplier_label.pack(side='left')
        
        # Table frame
        table_frame = tk.Frame(main_frame, bg=self.COLORS['white'], relief='raised', bd=2)
        table_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Table header with Add Row button
        header_frame = tk.Frame(table_frame, bg=self.COLORS['info'], height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Left side - Table title
        title_frame = tk.Frame(header_frame, bg=self.COLORS['info'])
        title_frame.pack(side='left', fill='both', expand=True)
        
        header_title = tk.Label(title_frame, 
                               text="Purchase Entry Table",
                               font=self.FONTS['subheading'],
                               fg=self.COLORS['white'],
                               bg=self.COLORS['info'])
        header_title.pack(expand=True)
        
        # (Add Row button moved to bottom - keeping header clean)
        
        # Scrollable frame for table
        canvas = tk.Canvas(table_frame, bg=self.COLORS['light'])
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['light'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Table headers
        headers_frame = tk.Frame(scrollable_frame, bg=self.COLORS['white'], relief='raised', bd=1)
        headers_frame.pack(fill='x', padx=10, pady=10)
        
        # Header labels (Ref ID and Supplier removed - handled at screen level)
        header_configs = [
            ("Item", 30), ("Gross (g)", 15), ("Less (g)", 15), ("Net (g)", 15), 
            ("Tunch (%)", 15), ("Wastage (%)", 15), ("Fine Gold (g)", 18), ("Action", 6)
        ]
        
        for i, (header, width) in enumerate(header_configs):
            label = tk.Label(headers_frame, 
                           text=header,
                           font=self.FONTS['body'],
                           fg=self.COLORS['white'],
                           bg=self.COLORS['primary'],
                           relief='raised',
                           bd=1,
                           width=width,
                           anchor='center')
            label.grid(row=0, column=i, sticky='ew', padx=1, pady=1)
        
        # Configure grid weights
        for i in range(len(header_configs)):
            headers_frame.grid_columnconfigure(i, weight=1)
        
        # Load dropdown data
        try:
            # Load items
            items_query = "SELECT item_id, item_name FROM items WHERE is_active = 1 ORDER BY item_name"
            items_data = self.db.execute_query(items_query)
            item_options = [f"{row[0]} - {row[1]}" for row in items_data]
        except Exception as e:
            print(f"Error loading dropdown data: {e}")
            item_options = []

        # Load suppliers for screen-level dropdown
        try:
            suppliers_query = "SELECT supplier_id, supplier_name FROM suppliers WHERE is_active = 1 ORDER BY supplier_name"
            suppliers_data = self.db.execute_query(suppliers_query)
            supplier_options = [f"{row[0]} - {row[1]}" for row in suppliers_data]
        except Exception as e:
            print(f"Error loading suppliers: {e}")
            supplier_options = []
        
        self.supplier_combo = ttk.Combobox(supplier_frame,
                                           font=self.FONTS['body'],
                                           width=30,
                                           state='readonly',
                                           values=supplier_options)
        # Prevent default dropdown opening; use custom picker only
        def prevent_dropdown(_e):
            try:
                return 'break'
            finally:
                pass
        self.supplier_combo.pack(side='left', padx=(10, 0))

        # Supplier picker modal with search
        def open_supplier_picker(_e=None):
            picker = tk.Toplevel(modal)
            picker.title("Select Supplier")
            picker.transient(modal)
            picker.grab_set()
            picker.resizable(False, False)
            tk.Label(picker, text="Search:", font=self.FONTS['body']).pack(anchor='w', padx=10, pady=(10, 0))
            search_var = tk.StringVar()
            search_entry = tk.Entry(picker, textvariable=search_var, font=self.FONTS['body'], width=40)
            search_entry.pack(fill='x', padx=10, pady=(0, 10))
            listbox = tk.Listbox(picker, height=12, font=self.FONTS['body'])
            listbox.pack(fill='both', expand=True, padx=10, pady=(0, 10))
            def refresh_list():
                query = search_var.get().strip().lower()
                listbox.delete(0, tk.END)
                for opt in supplier_options:
                    if query in opt.lower():
                        listbox.insert(tk.END, opt)
            def choose_and_close(_e=None):
                sel = listbox.get(tk.ACTIVE)
                if sel:
                    self.supplier_combo.set(sel)
                    try:
                        update_balance_preview_purch()
                    except Exception:
                        pass
                picker.destroy()
            refresh_list()
            search_entry.bind('<KeyRelease>', lambda _e: refresh_list())
            listbox.bind('<Return>', choose_and_close)
            listbox.bind('<Double-Button-1>', choose_and_close)
            picker.bind('<Escape>', lambda _e: picker.destroy())
            picker.after(10, lambda: search_entry.focus_set())
        
        # Open picker when clicking supplier field and via shortcut
        self.supplier_combo.bind('<Button-1>', open_supplier_picker)
        self.supplier_combo.bind('<Button-3>', open_supplier_picker)
        self.supplier_combo.bind('<Down>', prevent_dropdown)
        self.supplier_combo.bind('<Return>', prevent_dropdown)
        
        # Balance preview section (uniform card-style)
        balance_wrap = tk.Frame(main_frame, bg=self.COLORS['light'])
        balance_wrap.pack(fill='x', pady=(6, 8))
        balance_card = tk.Frame(balance_wrap, bg='#eef7ff', relief='ridge', bd=1)
        balance_card.pack(fill='x', padx=6, pady=0)
        bal_title = tk.Label(balance_card,
                             text='Supplier Balance',
                             font=self.FONTS['subheading'],
                             fg=self.COLORS['primary'],
                             bg='#eef7ff')
        bal_title.pack(side='left', padx=8, pady=6)
        self.purch_balance_projected_label = tk.Label(balance_card,
                                                      text='Projected: 0.00 g',
                                                      font=self.FONTS['body'],
                                                      fg=self.COLORS['primary'],
                                                      bg='#eef7ff')
        self.purch_balance_projected_label.pack(side='right', padx=(0, 10), pady=6)
        self.purch_balance_current_label = tk.Label(balance_card,
                                                    text='Current: 0.00 g',
                                                    font=self.FONTS['body'],
                                                    fg=self.COLORS['dark'],
                                                    bg='#eef7ff')
        self.purch_balance_current_label.pack(side='right', padx=(0, 16), pady=6)

        def get_selected_supplier_name_purch():
            text = self.supplier_combo.get().strip()
            return text.split(' - ')[1] if ' - ' in text else ''

        def compute_rows_total_fine_purch():
            total = 0.0
            for rd in self.purchase_rows:
                try:
                    val = float((rd['fine_entry'].get() or '0').strip())
                    total += val
                except Exception:
                    pass
            return total

        def update_balance_preview_purch(_e=None):
            supplier_name = get_selected_supplier_name_purch()
            current = 0.0
            if supplier_name:
                try:
                    current = float(self.main_app.get_supplier_balance(supplier_name) or 0.0)
                except Exception:
                    current = 0.0
            total_fine = compute_rows_total_fine_purch()
            projected = current - total_fine  # purchases subtract grams
            self.purch_balance_current_label.config(text=f"Current Balance: {current:.3f} g")
            self.purch_balance_projected_label.config(text=f"Projected: {projected:.3f} g")
        
        self.supplier_combo.bind('<<ComboboxSelected>>', update_balance_preview_purch)
        # Populate immediately if a value is already set (or after programmatic set)
        try:
            update_balance_preview_purch()
        except Exception:
            pass
        
        # Clear any existing purchase rows
        print(f"Before clearing - purchase_rows length: {len(self.purchase_rows)}")
        self.purchase_rows.clear()
        print(f"After clearing - purchase_rows length: {len(self.purchase_rows)}")
        print(f"After clearing - purchase_rows id: {id(self.purchase_rows)}")
        
        # Reset session counter for new modal session
        self.session_ref_counter = 0
        print(f"Session ref counter reset to: {self.session_ref_counter}")
        
        # Add a test marker to verify self object consistency
        self.test_marker = "MODAL_OPENED"
        print(f"Test marker set: {self.test_marker}")
        
        def create_purchase_row(row_num, existing_data=None):
            """Create a new purchase row"""
            print(f"=== CREATE_PURCHASE_ROW CALLED ===")
            print(f"Row number: {row_num}")
            print(f"Current purchase_rows length: {len(self.purchase_rows)}")
            print(f"Current purchase_rows id: {id(self.purchase_rows)}")
            print(f"Test marker: {getattr(self, 'test_marker', 'NOT_FOUND')}")
            print(f"Instance ID: {getattr(self, 'instance_id', 'NOT_FOUND')}")
            
            # Highlight the first row to make it more visible
            bg_color = self.COLORS['light'] if row_num == 0 else self.COLORS['white']
            row_frame = tk.Frame(scrollable_frame, bg=bg_color, relief='raised', bd=2)
            row_frame.pack(fill='x', padx=10, pady=2)
            
            # Add a subtle border to make rows more distinct
            if row_num == 0:
                row_frame.config(relief='solid', bd=2)
            
            # Item dropdown in first column
            item_combo = ttk.Combobox(row_frame, 
                                    font=self.FONTS['body'],
                                    width=30,
                                    state='readonly',
                                    values=item_options)
            item_combo.grid(row=0, column=0, sticky='ew', padx=1, pady=1)
            
            # Gross Weight
            gross_entry = tk.Entry(row_frame, 
                                 font=self.FONTS['body'],
                                 width=15,
                                 justify='center')
            gross_entry.insert(0, "0.00")
            gross_entry.grid(row=0, column=1, sticky='ew', padx=1, pady=1)
            
            # Less Weight
            less_entry = tk.Entry(row_frame, 
                                font=self.FONTS['body'],
                                width=15,
                                justify='center')
            less_entry.insert(0, "0.00")
            less_entry.grid(row=0, column=2, sticky='ew', padx=1, pady=1)
            
            # Net Weight (calculated, readonly)
            net_entry = tk.Entry(row_frame, 
                               font=self.FONTS['body'],
                               width=15,
                               state='readonly',
                               justify='center')
            net_entry.grid(row=0, column=3, sticky='ew', padx=1, pady=1)
            
            # Tunch
            tunch_entry = tk.Entry(row_frame, 
                                 font=self.FONTS['body'],
                                 width=15,
                                 justify='center')
            tunch_entry.insert(0, "0.0")
            tunch_entry.grid(row=0, column=4, sticky='ew', padx=1, pady=1)
            
            # Wastage
            wastage_entry = tk.Entry(row_frame, 
                                   font=self.FONTS['body'],
                                   width=15,
                                   justify='center')
            wastage_entry.insert(0, "0.0")
            wastage_entry.grid(row=0, column=5, sticky='ew', padx=1, pady=1)
            
            # Fine Gold (calculated, readonly)
            fine_entry = tk.Entry(row_frame, 
                                font=self.FONTS['body'],
                                width=18,
                                state='readonly',
                                justify='center')
            fine_entry.grid(row=0, column=6, sticky='ew', padx=1, pady=1)
            
            # Configure grid weights
            for i in range(11):
                row_frame.grid_columnconfigure(i, weight=1)
            
            # Calculation functions
            def calculate_net_weight():
                try:
                    gross_text = gross_entry.get().strip()
                    less_text = less_entry.get().strip()
                    
                    print(f"Calculating net weight - Gross: '{gross_text}', Less: '{less_text}'")  # Debug print
                    
                    if not gross_text and not less_text:
                        net_entry.config(state='normal')
                        net_entry.delete(0, tk.END)
                        net_entry.insert(0, "0.00")
                        net_entry.config(state='readonly')
                        return
                    
                    gross = float(gross_text or 0)
                    less = float(less_text or 0)
                    net = gross - less
                    
                    print(f"Net weight calculated: {net:.3f}")  # Debug print
                    
                    net_entry.config(state='normal')
                    net_entry.delete(0, tk.END)
                    net_entry.insert(0, f"{net:.3f}")
                    net_entry.config(state='readonly')
                    calculate_fine_gold()
                except (ValueError, TypeError) as e:
                    print(f"Error in calculate_net_weight: {e}")  # Debug print
                    net_entry.config(state='normal')
                    net_entry.delete(0, tk.END)
                    net_entry.insert(0, "0.00")
                    net_entry.config(state='readonly')
            
            def calculate_fine_gold():
                try:
                    net_text = net_entry.get().strip()
                    tunch_text = tunch_entry.get().strip()
                    wastage_text = wastage_entry.get().strip()
                    
                    print(f"Calculating fine gold - Net: '{net_text}', Tunch: '{tunch_text}', Wastage: '{wastage_text}'")  # Debug print
                    
                    if not net_text and not tunch_text and not wastage_text:
                        fine_entry.config(state='normal')
                        fine_entry.delete(0, tk.END)
                        fine_entry.insert(0, "0.00")
                        fine_entry.config(state='readonly')
                        return
                    
                    net = float(net_text or 0)
                    tunch = float(tunch_text or 0)
                    wastage = float(wastage_text or 0)
                    
                    # Formula: Net weight/100*tunch + net weight/wastage*100
                    if wastage != 0:  # Avoid division by zero
                        fine_gold = (net / 100 * tunch) + (net / 100 * wastage)
                    else:
                        fine_gold = net / 100 * tunch
                    
                    print(f"Fine gold calculated: {fine_gold:.3f}")  # Debug print
                    
                    fine_entry.config(state='normal')
                    fine_entry.delete(0, tk.END)
                    fine_entry.insert(0, f"{fine_gold:.3f}")
                    fine_entry.config(state='readonly')
                    try:
                        update_balance_preview_purch()
                    except Exception:
                        pass
                except (ValueError, ZeroDivisionError, TypeError) as e:
                    print(f"Error in calculate_fine_gold: {e}")  # Debug print
                    fine_entry.config(state='normal')
                    fine_entry.delete(0, tk.END)
                    fine_entry.insert(0, "0.00")
                    fine_entry.config(state='readonly')
                    try:
                        update_balance_preview_purch()
                    except Exception:
                        pass
            
            # Bind calculation events for immediate response
            def on_gross_change(event=None):
                print("Gross weight changed, calculating net weight...")
                calculate_net_weight()
            
            def on_less_change(event=None):
                print("Less weight changed, calculating net weight...")
                calculate_net_weight()
            
            def on_tunch_change(event=None):
                print("Tunch changed, calculating fine gold...")
                calculate_fine_gold()
            
            def on_wastage_change(event=None):
                print("Wastage changed, calculating fine gold...")
                calculate_fine_gold()
            
            # Bind events
            gross_entry.bind('<KeyRelease>', on_gross_change)
            gross_entry.bind('<FocusOut>', on_gross_change)
            gross_entry.bind('<Button-1>', on_gross_change)
            less_entry.bind('<KeyRelease>', on_less_change)
            less_entry.bind('<FocusOut>', on_less_change)
            less_entry.bind('<Button-1>', on_less_change)
            tunch_entry.bind('<KeyRelease>', on_tunch_change)
            tunch_entry.bind('<FocusOut>', on_tunch_change)
            tunch_entry.bind('<Button-1>', on_tunch_change)
            wastage_entry.bind('<KeyRelease>', on_wastage_change)
            wastage_entry.bind('<FocusOut>', on_wastage_change)
            wastage_entry.bind('<Button-1>', on_wastage_change)
            
            # Test function to manually trigger calculations
            def test_calculations():
                print("=== TESTING CALCULATIONS ===")
                print(f"Gross entry value: '{gross_entry.get()}'")
                print(f"Less entry value: '{less_entry.get()}'")
                print(f"Net entry value: '{net_entry.get()}'")
                print("Calling calculate_net_weight()...")
                calculate_net_weight()
                print(f"After calculation - Net entry value: '{net_entry.get()}'")
                print("=== END TEST ===")
            
            # Test button for calculations (temporary)
            # Test button removed
            
            # Delete button
            delete_btn = tk.Button(row_frame, 
                                 text="🗑️",
                                 font=self.FONTS['body'],
                                 bg=self.COLORS['warning'],
                                 fg=self.COLORS['white'],
                                 relief='raised',
                                 bd=1,
                                 width=6,
                                 command=lambda: delete_row(row_num))
            delete_btn.grid(row=0, column=7, sticky='ew', padx=1, pady=1)
            
            # Focus on item combo for first row
            if row_num == 0:
                item_combo.focus()
            
            # Trigger initial calculations after a short delay to ensure fields are ready
            def trigger_initial_calculations():
                on_change()
            row_frame.after_idle(trigger_initial_calculations)
            row_frame.after(100, trigger_initial_calculations)
            
            # Store row data
            row_data = {
                'row_num': row_num,
                'item_combo': item_combo,
                'gross_entry': gross_entry,
                'less_entry': less_entry,
                'net_entry': net_entry,
                'tunch_entry': tunch_entry,
                'wastage_entry': wastage_entry,
                'fine_entry': fine_entry,
                'row_frame': row_frame
            }
            
            # Populate existing data in edit mode
            if existing_data:
                item_name = existing_data[2]
                for option in item_options:
                    if option.endswith(f" - {item_name}"):
                        item_combo.set(option)
                        break
            
            self.purchase_rows.append(row_data)
            print(f"Added row {row_num} to purchase_rows. Total rows now: {len(self.purchase_rows)}")  # Debug print
            print(f"Purchase_rows content after append: {[r['row_num'] for r in self.purchase_rows]}")  # Debug print
            print(f"Purchase_rows id after append: {id(self.purchase_rows)}")  # Debug print
            update_status()
            return row_data
        
        def delete_row(row_num):
            """Delete a specific row"""
            for i, row_data in enumerate(self.purchase_rows):
                if row_data['row_num'] == row_num:
                    row_data['row_frame'].destroy()
                    self.purchase_rows.pop(i)
                    update_status()
                    break
        
        def add_new_row():
            """Add a new row to the table"""
            print(f"=== ADD_NEW_ROW CALLED ===")
            row_num = len(self.purchase_rows)
            print(f"Adding new row {row_num}. Current purchase_rows length: {len(self.purchase_rows)}")  # Debug print
            print(f"Purchase_rows id in add_new_row: {id(self.purchase_rows)}")
            print(f"Test marker in add_new_row: {getattr(self, 'test_marker', 'NOT_FOUND')}")
            create_purchase_row(row_num)
            print(f"After create_purchase_row call - purchase_rows length: {len(self.purchase_rows)}")
        
        def save_all_purchases():
            """Save all purchases to database"""
            print(f"=== SAVE ALL PURCHASES DEBUG ===")
            print(f"Number of purchase rows: {len(self.purchase_rows)}")
            print(f"Purchase rows content: {self.purchase_rows}")
            print(f"Purchase rows type: {type(self.purchase_rows)}")
            print(f"Purchase rows id: {id(self.purchase_rows)}")
            print(f"Instance ID: {getattr(self, 'instance_id', 'NOT_FOUND')}")
            print(f"Test marker: {getattr(self, 'test_marker', 'NOT_FOUND')}")
            
            if not self.purchase_rows:
                messagebox.showerror("Error", "No purchases to save")
                return
            
            try:
                # Screen-level supplier
                supplier_text = self.supplier_combo.get().strip()
                if not supplier_text:
                    messagebox.showerror("Error", "Please select a supplier for all entries")
                    return
                supplier_id = int(supplier_text.split(' - ')[0])
                supplier_name = supplier_text.split(' - ')[1]
                
                purchase_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                saved_count = 0
                
                for i, row_data in enumerate(self.purchase_rows):
                    print(f"\n--- Processing Row {i+1} ---")
                    item_text = row_data['item_combo'].get().strip()
                    gross = row_data['gross_entry'].get().strip()
                    less = row_data['less_entry'].get().strip()
                    tunch = row_data['tunch_entry'].get().strip()
                    wastage = row_data['wastage_entry'].get().strip()
                    
                    print(f"Supplier: '{supplier_text}'")
                    print(f"Item: '{item_text}'")
                    print(f"Gross: '{gross}'")
                    print(f"Less: '{less}'")
                    print(f"Tunch: '{tunch}'")
                    print(f"Wastage: '{wastage}'")
                    
                    # Check if essential fields are filled (item, gross, less)
                    essential_fields = [item_text, gross, less]
                    if not all(essential_fields):
                        print(f"Row {i+1}: Skipping - missing essential fields")
                        continue
                    
                    # Check if tunch and wastage have valid values (not empty and not just "0.0")
                    if not tunch or tunch == "0.0" or tunch == "0":
                        print(f"Row {i+1}: Skipping - invalid tunch value: '{tunch}'")
                        continue
                        
                    if not wastage or wastage == "0.0" or wastage == "0":
                        print(f"Row {i+1}: Skipping - invalid wastage value: '{wastage}'")
                        continue
                    
                    # Extract item info
                    item_id = int(item_text.split(' - ')[0])
                    
                    # Calculate values
                    net_weight = float(gross) - float(less)
                    if float(wastage) != 0:  # Avoid division by zero
                        fine_gold = (net_weight / 100 * float(tunch)) + (net_weight / 100 * float(wastage))
                    else:
                        fine_gold = net_weight / 100 * float(tunch)
                    
                    # Insert into database
                    query = '''
                        INSERT INTO sales (ref_id, supplier_name, item_id, gross_weight, less_weight, 
                                         net_weight, tunch_percentage, wastage_percentage, fine_gold, sale_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
                    
                    insert_data = (
                        self.transaction_ref_id,
                        supplier_name,
                        item_id,
                        float(gross),
                        float(less),
                        net_weight,
                        float(tunch),
                        float(wastage),
                        fine_gold,
                        purchase_date
                    )
                    
                    print(f"Inserting data: {insert_data}")
                    self.db.execute_update(query, insert_data)
                    print(f"Data inserted successfully into purchases table!")
                    
                    # Update item inventory (add to inventory for purchases)
                    self.main_app.update_item_inventory(item_id, fine_gold, net_weight, 'add')
                    
                    # Update supplier balance in grams for purchase (we owe less)
                    self.main_app.update_supplier_balance(supplier_name, fine_gold, 'subtract')
                    
                    saved_count += 1
                    print(f"Row {i+1}: Successfully saved!")
                
                print(f"\n=== SAVE RESULT ===")
                print(f"Total rows processed: {len(self.purchase_rows)}")
                print(f"Successfully saved: {saved_count}")
                
                if saved_count > 0:
                    self.main_app.show_toast(f"Successfully saved {saved_count} purchases!", success=True)
                    # Refresh unified table view
                    try:
                        self.main_app.load_unified_data()
                        print(f"Main unified table refreshed successfully!")
                    except Exception as e:
                        print(f"Error refreshing unified table: {e}")
                    modal.destroy()
                else:
                    messagebox.showerror("Error", "No valid purchases to save. Please fill all required fields.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error saving purchases: {e}")
        
        def clear_all_rows():
            """Clear all rows"""
            for row_data in self.purchase_rows:
                row_data['row_frame'].destroy()
            self.purchase_rows.clear()
            update_status()
            self.main_app.show_toast("All rows cleared", success=True)
        
        def update_status():
            """Update the status label with current row count (safe before label exists)"""
            print(f"=== UPDATE_STATUS CALLED ===")
            print(f"Purchase_rows length in update_status: {len(self.purchase_rows)}")
            print(f"Purchase_rows id in update_status: {id(self.purchase_rows)}")
            try:
                if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                    self.status_label.config(text=f"Rows: {len(self.purchase_rows)}")
                    print(f"Status label updated to: Rows: {len(self.purchase_rows)}")
                else:
                    print("Status label not available yet, skipping update")
            except Exception as e:
                print(f"Error updating status label: {e}")
                print("Status label not available yet, skipping update")
        
        # Pack canvas and scrollbar first
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create default 6 rows after canvas is packed
        for i in range(6):
            create_purchase_row(i)
        
        # Add debugging for modal lifecycle
        def on_modal_close():
            print(f"=== MODAL CLOSING ===")
            print(f"Final purchase_rows length: {len(self.purchase_rows)}")
            print(f"Final purchase_rows id: {id(self.purchase_rows)}")
            modal.destroy()
        
        modal.protocol("WM_DELETE_WINDOW", on_modal_close)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        status_frame.pack(fill='x', pady=(10, 0))
        
        self.status_label = tk.Label(status_frame, 
                                    text="Rows: 0",
                                    font=self.FONTS['body'],
                                    fg=self.COLORS['primary'],
                                    bg=self.COLORS['light'])
        self.status_label.pack(side='left')
        # Initialize status label text now that it exists
        update_status()
        
        # Bottom buttons: Add Row, Save, Clear All, Cancel
        button_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        button_frame.pack(side='bottom', fill='x', pady=(8, 8))

        add_row_btn_bottom = tk.Button(button_frame,
                                 text="➕ Add Row",
                                 command=lambda: (create_purchase_row(len(self.purchase_rows)), update_status()),
                                 font=self.FONTS['body'],
                                 bg=self.COLORS['success'],
                                 fg=self.COLORS['white'],
                                 relief='raised',
                                 bd=2,
                                 padx=20,
                                 pady=8)
        add_row_btn_bottom.pack(side='left')

        def on_save_click_bottom():
            save_all_purchases()

        save_all_btn_bottom = tk.Button(button_frame,
                                 text="💾 Save Purchases (Ctrl+S)",
                                 command=on_save_click_bottom,
                                 font=self.FONTS['body'],
                                 bg=self.COLORS['primary'],
                                 fg=self.COLORS['white'],
                                 relief='raised',
                                 bd=2,
                                 padx=20,
                                 pady=8)
        save_all_btn_bottom.pack(side='left', padx=(10, 0))
        
        clear_all_btn = tk.Button(button_frame, 
                                 text="🗑️ Clear All",
                                 command=clear_all_rows,
                                 font=self.FONTS['body'],
                                 bg=self.COLORS['warning'],
                                 fg=self.COLORS['white'],
                                 relief='raised',
                                 bd=2,
                                 padx=20,
                                 pady=8)
        clear_all_btn.pack(side='left', padx=(10, 15))
        
        cancel_btn = tk.Button(button_frame, 
                              text="❌ Cancel",
                              command=modal.destroy,
                              font=self.FONTS['body'],
                              bg=self.COLORS['secondary'],
                              fg=self.COLORS['white'],
                              relief='raised',
                              bd=2,
                              padx=20,
                              pady=8)
        cancel_btn.pack(side='right')

        # Keyboard shortcuts
        modal.bind_all('<Control-q>', lambda _e: add_row_btn_bottom.invoke())
        modal.bind_all('<Control-Q>', lambda _e: add_row_btn_bottom.invoke())
        modal.bind_all('<Control-s>', lambda _e: save_all_btn_bottom.invoke())
        modal.bind_all('<Control-S>', lambda _e: save_all_btn_bottom.invoke())
        modal.bind_all('<Control-a>', open_supplier_picker)
        modal.bind_all('<Control-A>', open_supplier_picker)
        modal.bind('<Escape>', lambda _e: modal.destroy())
        # Add keyboard shortcuts for the modal
        modal.bind('<Control-s>', lambda _e: save_all_purchases())
        modal.bind('<Control-a>', lambda _e: add_new_row())
        # Remove duplicate Ctrl+Q binding - Ctrl+A is sufficient

    def check_ref_id_exists(self) -> bool:
        """Return True if self.transaction_ref_id does NOT exist yet (safe to create).
        If it exists, show an error and return False.
        """
        try:
            query = "SELECT COUNT(*) FROM sales WHERE ref_id = ?"
            result = self.db.execute_query(query, (self.transaction_ref_id,))
            exists = result and result[0][0] > 0
            if exists:
                messagebox.showerror("Duplicate Ref ID", f"Ref ID {self.transaction_ref_id} already exists. Please try again.")
                return False
            return True
        except Exception as e:
            print(f"Error checking Ref ID existence: {e}")
            return False

    def show_multiple_purchases_modal_for_edit(self, ref_id: str):
        """Open multiple purchases modal in edit mode for a given Ref ID.
        Loads all rows for the transaction, allows editing, and saves by deleting
        existing rows and re-inserting current rows with the same Ref ID.
        """
        # Load existing rows
        try:
            query = '''
                SELECT 
                    s.sale_id,
                    s.supplier_name,
                    i.item_name,
                    s.gross_weight,
                    s.less_weight,
                    s.net_weight,
                    s.tunch_percentage,
                    s.wastage_percentage,
                    s.fine_gold,
                    s.sale_date
                FROM sales s
                LEFT JOIN items i ON s.item_id = i.item_id
                WHERE s.ref_id = ?
                ORDER BY s.sale_id
            '''
            existing_records = self.db.execute_query(query, (ref_id,))
            if not existing_records:
                messagebox.showerror("Error", f"No records found for Ref ID: {ref_id}")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error loading existing purchases: {e}")
            return

        # Open base modal (add flow) but preset state
        self.transaction_ref_id = ref_id
        # Ensure a clean state for this modal session
        try:
            self.purchase_rows.clear()
        except Exception:
            self.purchase_rows = []
        modal = tk.Toplevel(self.root_window)
        modal.title(f"Edit Purchases - {ref_id}")
        modal.update_idletasks()
        sw = modal.winfo_screenwidth()
        sh = modal.winfo_screenheight()
        mw = int(sw * 0.8)
        mh = int(sh * 0.8)
        mx = (sw - mw) // 2
        my = (sh - mh) // 2
        modal.geometry(f"{mw}x{mh}+{mx}+{my}")
        modal.transient(self.root_window)
        modal.grab_set()

        main_frame = tk.Frame(modal, bg=self.COLORS['light'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        title_label = tk.Label(main_frame,
                               text=f"Edit Purchases - {ref_id}",
                               font=self.FONTS['heading'],
                               fg=self.COLORS['primary'],
                               bg=self.COLORS['light'])
        title_label.pack(pady=(0, 10))

        top_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        top_frame.pack(fill='x', pady=(0, 20))

        def on_save_click():
            save_all_purchases_edit()

        # Top-right save removed; bottom bar has primary save button

        # Supplier frame
        supplier_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        supplier_frame.pack(fill='x', pady=(0, 15))
        supplier_label = tk.Label(supplier_frame, text="Supplier:", font=self.FONTS['body'], fg=self.COLORS['dark'], bg=self.COLORS['light'])
        supplier_label.pack(side='left')
        try:
            suppliers_query = "SELECT supplier_id, supplier_name FROM suppliers WHERE is_active = 1 ORDER BY supplier_name"
            suppliers_data = self.db.execute_query(suppliers_query)
            supplier_options = [f"{row[0]} - {row[1]}" for row in suppliers_data]
        except Exception:
            supplier_options = []
        self.supplier_combo = ttk.Combobox(supplier_frame, font=self.FONTS['body'], width=30, state='readonly', values=supplier_options)
        self.supplier_combo.pack(side='left', padx=(10, 0))
        first_supplier = existing_records[0][1]
        for option in supplier_options:
            if option.endswith(f" - {first_supplier}"):
                self.supplier_combo.set(option)
                break

        # Table
        table_frame = tk.Frame(main_frame, bg=self.COLORS['white'], relief='raised', bd=2)
        table_frame.pack(fill='both', expand=True, pady=(0, 15))
        header_frame = tk.Frame(table_frame, bg=self.COLORS['info'], height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        title_frame = tk.Frame(header_frame, bg=self.COLORS['info'])
        title_frame.pack(side='left', fill='both', expand=True)
        header_title = tk.Label(title_frame, text="Purchase Entry Table", font=self.FONTS['subheading'], fg=self.COLORS['white'], bg=self.COLORS['info'])
        header_title.pack(expand=True)

        def on_add_row_click():
            create_purchase_row(len(self.purchase_rows))

        add_row_btn = tk.Button(header_frame, text="➕ Add Row", command=on_add_row_click, font=self.FONTS['subheading'], bg=self.COLORS['success'], fg=self.COLORS['white'], relief='raised', bd=3, padx=20, pady=8)
        add_row_btn.pack(side='right', padx=10, pady=5)

        canvas = tk.Canvas(table_frame, bg=self.COLORS['light'])
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['light'])
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Headers
        headers_frame = tk.Frame(scrollable_frame, bg=self.COLORS['white'], relief='raised', bd=1)
        headers_frame.pack(fill='x', padx=10, pady=10)
        header_configs = [("Item", 30), ("Gross (g)", 15), ("Less (g)", 15), ("Net (g)", 15), ("Tunch (%)", 15), ("Wastage (%)", 15), ("Fine Gold (g)", 18), ("Action", 6)]
        for i, (header, width) in enumerate(header_configs):
            label = tk.Label(headers_frame, text=header, font=self.FONTS['body'], fg=self.COLORS['white'], bg=self.COLORS['primary'], relief='raised', bd=1, width=width, anchor='center')
            label.grid(row=0, column=i, sticky='ew', padx=1, pady=1)
            headers_frame.grid_columnconfigure(i, weight=1)

        # Load items
        try:
            items_query = "SELECT item_id, item_name FROM items WHERE is_active = 1 ORDER BY item_name"
            items_data = self.db.execute_query(items_query)
            item_options = [f"{row[0]} - {row[1]}" for row in items_data]
        except Exception:
            item_options = []

        # Reuse create_purchase_row from add modal scope by redefining a minimal version here
        def create_purchase_row(row_num, existing_data_row=None):
            bg_color = self.COLORS['light'] if row_num == 0 else self.COLORS['white']
            row_frame = tk.Frame(scrollable_frame, bg=bg_color, relief='raised', bd=2)
            row_frame.pack(fill='x', padx=10, pady=2)
            if row_num == 0:
                row_frame.config(relief='solid', bd=2)
            item_combo = ttk.Combobox(row_frame, font=self.FONTS['body'], width=30, state='readonly', values=item_options)
            item_combo.grid(row=0, column=0, sticky='ew', padx=1, pady=1)
            gross_entry = tk.Entry(row_frame, font=self.FONTS['body'], width=15, justify='center')
            gross_entry.grid(row=0, column=1, sticky='ew', padx=1, pady=1)
            less_entry = tk.Entry(row_frame, font=self.FONTS['body'], width=15, justify='center')
            less_entry.grid(row=0, column=2, sticky='ew', padx=1, pady=1)
            net_entry = tk.Entry(row_frame, font=self.FONTS['body'], width=15, state='readonly', justify='center')
            net_entry.grid(row=0, column=3, sticky='ew', padx=1, pady=1)
            tunch_entry = tk.Entry(row_frame, font=self.FONTS['body'], width=15, justify='center')
            tunch_entry.grid(row=0, column=4, sticky='ew', padx=1, pady=1)
            wastage_entry = tk.Entry(row_frame, font=self.FONTS['body'], width=15, justify='center')
            wastage_entry.grid(row=0, column=5, sticky='ew', padx=1, pady=1)
            fine_entry = tk.Entry(row_frame, font=self.FONTS['body'], width=18, state='readonly', justify='center')
            fine_entry.grid(row=0, column=6, sticky='ew', padx=1, pady=1)
            def calculate_net_weight():
                try:
                    gross = float(gross_entry.get() or 0)
                    less = float(less_entry.get() or 0)
                    net = gross - less
                    net_entry.config(state='normal')
                    net_entry.delete(0, tk.END)
                    net_entry.insert(0, f"{net:.2f}")
                    net_entry.config(state='readonly')
                except Exception:
                    pass
            def calculate_fine_gold():
                try:
                    net_text = net_entry.get().strip()
                    tunch_text = tunch_entry.get().strip()
                    wastage_text = wastage_entry.get().strip()
                    net = float(net_text or 0)
                    tunch = float(tunch_text or 0)
                    wastage = float(wastage_text or 0)
                    fine_gold = (net / 100 * tunch) + (net / 100 * wastage) if wastage != 0 else (net / 100 * tunch)
                    fine_entry.config(state='normal')
                    fine_entry.delete(0, tk.END)
                    fine_entry.insert(0, f"{fine_gold:.2f}")
                    fine_entry.config(state='readonly')
                    try:
                        update_balance_preview_purch()
                    except Exception:
                        pass
                except Exception:
                    fine_entry.config(state='normal')
                    fine_entry.delete(0, tk.END)
                    fine_entry.insert(0, "0.00")
                    fine_entry.config(state='readonly')
            def on_change(_e=None):
                calculate_net_weight()
                calculate_fine_gold()
            for w in (gross_entry, less_entry, tunch_entry, wastage_entry):
                w.bind('<KeyRelease>', on_change)
                w.bind('<FocusOut>', on_change)
            # Pre-fill values when existing data is provided
            if existing_data_row is not None:
                try:
                    # existing_data_row indices:
                    # 2=item_name, 3=gross, 4=less, 5=net, 6=tunch, 7=wastage, 8=fine
                    item_name = existing_data_row[2]
                    for option in item_options:
                        if option.endswith(f" - {item_name}"):
                            item_combo.set(option)
                            break
                    gross_entry.delete(0, tk.END)
                    gross_entry.insert(0, f"{float(existing_data_row[3] or 0):.2f}")
                    less_entry.delete(0, tk.END)
                    less_entry.insert(0, f"{float(existing_data_row[4] or 0):.2f}")
                    net_entry.config(state='normal')
                    net_entry.delete(0, tk.END)
                    net_entry.insert(0, f"{float(existing_data_row[5] or 0):.2f}")
                    net_entry.config(state='readonly')
                    tunch_entry.delete(0, tk.END)
                    tunch_entry.insert(0, f"{float(existing_data_row[6] or 0):.1f}")
                    wastage_entry.delete(0, tk.END)
                    wastage_entry.insert(0, f"{float(existing_data_row[7] or 0):.1f}")
                    fine_entry.config(state='normal')
                    fine_entry.delete(0, tk.END)
                    fine_entry.insert(0, f"{float(existing_data_row[8] or 0):.2f}")
                    fine_entry.config(state='readonly')
                except Exception:
                    # Fall back to computing values if direct fill fails
                    on_change()
            # Removed test utility and button; use live on_change events only
            # Removed test utility and button; use live on_change events only
            delete_btn = tk.Button(row_frame, text="🗑️", font=self.FONTS['body'], bg=self.COLORS['warning'], fg=self.COLORS['white'], relief='raised', bd=1, width=6, command=lambda: delete_row(row_num))
            delete_btn.grid(row=0, column=7, sticky='ew', padx=1, pady=1)
            if row_num == 0:
                item_combo.focus()
            row_data = {
                'row_num': row_num,
                'item_combo': item_combo,
                'gross_entry': gross_entry,
                'less_entry': less_entry,
                'net_entry': net_entry,
                'tunch_entry': tunch_entry,
                'wastage_entry': wastage_entry,
                'fine_entry': fine_entry,
                'row_frame': row_frame
            }
            self.purchase_rows.append(row_data)
            return row_data

        def delete_row(row_num):
            for i, row_data in enumerate(self.purchase_rows):
                if row_data['row_num'] == row_num:
                    row_data['row_frame'].destroy()
                    self.purchase_rows.pop(i)
                    break

        # Pack canvas
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create rows from existing data
        for i, existing_record in enumerate(existing_records):
            create_purchase_row(i, existing_record)

        def save_all_purchases_edit():
            # Save by replacing existing rows
            if not self.purchase_rows:
                messagebox.showerror("Error", "No purchases to save")
                return
            supplier_text = self.supplier_combo.get().strip()
            if not supplier_text:
                messagebox.showerror("Error", "Please select a supplier for all entries")
                return
            supplier_name = supplier_text.split(' - ')[1]
            try:
                # Delete existing
                self.db.execute_update("DELETE FROM sales WHERE ref_id = ?", (self.transaction_ref_id,))
                # Insert current
                purchase_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for row_data in self.purchase_rows:
                    item_text = row_data['item_combo'].get().strip()
                    gross = row_data['gross_entry'].get().strip()
                    less = row_data['less_entry'].get().strip()
                    tunch = row_data['tunch_entry'].get().strip()
                    wastage = row_data['wastage_entry'].get().strip()
                    if not all([item_text, gross, less, tunch, wastage]):
                        continue
                    item_id = int(item_text.split(' - ')[0])
                    net_weight = float(gross) - float(less)
                    fine_gold = (net_weight / 100 * float(tunch)) + (net_weight / 100 * float(wastage)) if float(wastage) != 0 else (net_weight / 100 * float(tunch))
                    self.db.execute_update(
                        """
                        INSERT INTO sales (ref_id, supplier_name, item_id, gross_weight, less_weight, net_weight, tunch_percentage, wastage_percentage, fine_gold, sale_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            self.transaction_ref_id,
                            supplier_name,
                            item_id,
                            float(gross),
                            float(less),
                            net_weight,
                            float(tunch),
                            float(wastage),
                            fine_gold,
                            purchase_date,
                        ),
                    )
                self.main_app.load_unified_data()
                self.main_app.show_toast("Purchases updated successfully!", success=True)
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error saving purchases: {e}")

        # Keyboard shortcuts for edit modal
        modal.bind_all('<Control-q>', lambda _e: on_add_row_click())
        modal.bind_all('<Control-Q>', lambda _e: on_add_row_click())
        modal.bind_all('<Control-s>', lambda _e: on_save_click())
        modal.bind_all('<Control-S>', lambda _e: on_save_click())
        modal.bind_all('<Control-a>', lambda _e: supplier_frame.event_generate('<Button-1>'))
        modal.bind_all('<Control-A>', lambda _e: supplier_frame.event_generate('<Button-1>'))
        modal.bind('<Escape>', lambda _e: modal.destroy())
        # Add keyboard shortcuts for the edit modal
        modal.bind('<Control-s>', lambda _e: save_all_purchases_edit())
        modal.bind('<Control-a>', lambda _e: add_new_row())
        # Remove duplicate Ctrl+Q binding - Ctrl+A is sufficient

        # Bottom buttons for edit modal: Update Record and Cancel
        button_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        button_frame.pack(side='bottom', fill='x', pady=(8, 8))
        
        update_btn = tk.Button(button_frame,
                               text="💾 Update Record",
                               command=save_all_purchases_edit,
                               font=self.FONTS['body'],
                               bg=self.COLORS['primary'],
                               fg=self.COLORS['white'],
                               relief='raised',
                               bd=2,
                               padx=20,
                               pady=8)
        update_btn.pack(side='left')
        
        cancel_btn = tk.Button(button_frame, 
                              text="❌ Cancel",
                              command=modal.destroy,
                              font=self.FONTS['body'],
                              bg=self.COLORS['secondary'],
                              fg=self.COLORS['white'],
                              relief='raised',
                              bd=2,
                              padx=20,
                              pady=8)
        cancel_btn.pack(side='right')
    
    def generate_ref_id(self, prefix):
        """Generate reference ID with format: P + DDMMYY + / + 3-digit incremental"""
        # Get current date in DDMMYY format
        today = datetime.now()
        date_str = today.strftime('%d%m%y')
        
        print(f"Generating Ref ID for prefix: {prefix}, date: {date_str}")  # Debug print
        
        # Get next incremental number for today
        try:
            # Get the highest existing number for today from sales table
            query = f"SELECT ref_id FROM sales WHERE ref_id LIKE '{prefix}{date_str}/%' ORDER BY ref_id DESC LIMIT 1"
            print(f"Executing query: {query}")  # Debug print
            result = self.db.execute_query(query)
            
            if result and result[0][0]:
                # Extract the number from the highest existing ref_id
                existing_ref = result[0][0]
                print(f"Highest existing ref_id: {existing_ref}")
                # Extract number after the last slash
                existing_num = int(existing_ref.split('/')[-1])
                max_db_num = existing_num
                print(f"Highest existing number: {max_db_num}")
            else:
                max_db_num = 0
                print(f"No existing records found for today")
            
            # Use the higher of database max number or session counter
            next_num = max(max_db_num, self.session_ref_counter) + 1
            print(f"Max DB number: {max_db_num}, Session counter: {self.session_ref_counter}, Next num: {next_num}")
            
            # Update session counter
            self.session_ref_counter = next_num
            
        except Exception as e:
            print(f"Error generating ref ID: {e}")
            self.session_ref_counter += 1
            next_num = self.session_ref_counter
        
        # Format as 3-digit number
        ref_id = f"{prefix}{date_str}/{next_num:03d}"
        
        # Double-check that this Ref ID doesn't already exist
        try:
            check_query = "SELECT COUNT(*) FROM sales WHERE ref_id = ?"
            check_result = self.db.execute_query(check_query, (ref_id,))
            if check_result and check_result[0][0] > 0:
                print(f"WARNING: Ref ID {ref_id} already exists! Incrementing...")
                self.session_ref_counter += 1
                next_num = self.session_ref_counter
                ref_id = f"{prefix}{date_str}/{next_num:03d}"
                print(f"New Ref ID after increment: {ref_id}")
        except Exception as e:
            print(f"Error checking Ref ID uniqueness: {e}")
        
        print(f"Final Generated Ref ID: {ref_id}")  # Debug print
        return ref_id
