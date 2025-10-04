import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class MultipleSalesManager:
    def __init__(self, root_window, main_app, db_manager, colors, fonts):
        self.root_window = root_window  # Tkinter root window for creating modals
        self.main_app = main_app        # Main application object for calling methods
        self.db = db_manager
        self.COLORS = colors
        self.FONTS = fonts
        self.sales_rows = []
        self.instance_id = id(self)  # Unique identifier for this instance
        self.session_ref_counter = 0  # Counter for Ref IDs in current session
        print(f"MultipleSalesManager instance created with ID: {self.instance_id}")
        
    def show_multiple_sales_modal(self):
        """Show full-screen modal for adding multiple sales with table interface"""
        print(f"=== OPENING MULTIPLE SALES MODAL ===")
        print(f"Initial sales_rows length: {len(self.sales_rows)}")
        print(f"Initial sales_rows id: {id(self.sales_rows)}")
        
        # Create full-screen modal (80% of screen)
        modal = tk.Toplevel(self.root_window)
        modal.title("Add Multiple Sales - Table View")
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
                              text="Add Multiple Sales - Table View",
                              font=self.FONTS['heading'],
                              fg=self.COLORS['primary'],
                              bg=self.COLORS['light'])
        title_label.pack(pady=(0, 10))
        
        # Generate single Ref ID for all entries in this transaction
        self.transaction_ref_id = self.generate_ref_id('S')
        
        # Check if this Ref ID already exists
        if not self.check_ref_id_exists():
            modal.destroy()
            return
        
        # Instructions and top controls frame
        top_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        top_frame.pack(fill='x', pady=(0, 20))
        
        # Left side - Instructions and Ref ID
        left_frame = tk.Frame(top_frame, bg=self.COLORS['light'])
        left_frame.pack(side='left', fill='x', expand=True)
        
        instructions_label = tk.Label(left_frame, 
                                     text="Instructions: Select supplier below, then fill in the table. Use 'Add Row' to create more entries.",
                                     font=self.FONTS['body'],
                                     fg=self.COLORS['dark'],
                                     bg=self.COLORS['light'])
        instructions_label.pack(anchor='w')
        
        # Ref ID display (smaller)
        ref_frame = tk.Frame(left_frame, bg=self.COLORS['light'])
        ref_frame.pack(anchor='w', pady=(5, 0))
        
        ref_label = tk.Label(ref_frame, 
                            text="Ref ID:",
                            font=self.FONTS['body'],
                            fg=self.COLORS['primary'],
                            bg=self.COLORS['light'])
        ref_label.pack(side='left')
        
        ref_display = tk.Label(ref_frame, 
                              text=self.transaction_ref_id,
                              font=self.FONTS['body'],
                              fg=self.COLORS['primary'],
                              bg=self.COLORS['light'],
                              relief='solid',
                              bd=1,
                              padx=8,
                              pady=2)
        ref_display.pack(side='left', padx=(5, 0))
        
        # Note: top-right save removed; primary save is in bottom bar
        
        # Simple supplier selection
        supplier_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        supplier_frame.pack(fill='x', pady=(0, 15))
        
        supplier_label = tk.Label(supplier_frame, 
                                 text="Supplier:",
                                 font=self.FONTS['body'],
                                 fg=self.COLORS['dark'],
                                 bg=self.COLORS['light'])
        supplier_label.pack(side='left')
        
        # Load suppliers for dropdown
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
        # Prevent default dropdown from opening; we will open our own picker
        def prevent_dropdown(_e):
            try:
                return 'break'
            finally:
                pass
        self.supplier_combo.pack(side='left', padx=(10, 0))

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
        self.sales_balance_projected_label = tk.Label(balance_card,
                                                      text='Projected: 0.00 g',
                                                      font=self.FONTS['body'],
                                                      fg=self.COLORS['primary'],
                                                      bg='#eef7ff')
        self.sales_balance_projected_label.pack(side='right', padx=(0, 10), pady=6)
        self.sales_balance_current_label = tk.Label(balance_card,
                                                    text='Current: 0.00 g',
                                                    font=self.FONTS['body'],
                                                    fg=self.COLORS['dark'],
                                                    bg='#eef7ff')
        self.sales_balance_current_label.pack(side='right', padx=(0, 16), pady=6)

        def get_selected_supplier_name_sales():
            text = self.supplier_combo.get().strip()
            return text.split(' - ')[1] if ' - ' in text else ''

        def compute_rows_total_fine_sales():
            total = 0.0
            try:
                for rd in self.sales_rows:
                    val = float((rd['fine_entry'].get() or '0').strip())
                    total += val
            except Exception:
                pass
            return total

        def update_balance_preview_sales(_e=None):
            supplier_name = get_selected_supplier_name_sales()
            current = 0.0
            if supplier_name:
                try:
                    current = float(self.main_app.get_supplier_balance(supplier_name) or 0.0)
                except Exception:
                    current = 0.0
            total_fine = compute_rows_total_fine_sales()
            projected = current + total_fine  # sales add grams
            self.sales_balance_current_label.config(text=f"Current Balance: {current:.3f} g")
            self.sales_balance_projected_label.config(text=f"Projected: {projected:.3f} g")

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
                        update_balance_preview_sales()
                    except Exception:
                        pass
                picker.destroy()
            refresh_list()
            search_entry.bind('<KeyRelease>', lambda _e: refresh_list())
            listbox.bind('<Return>', choose_and_close)
            listbox.bind('<Double-Button-1>', choose_and_close)
            picker.bind('<Escape>', lambda _e: picker.destroy())
            picker.after(10, lambda: search_entry.focus_set())
        self.supplier_combo.bind('<Button-1>', open_supplier_picker)
        self.supplier_combo.bind('<Button-3>', open_supplier_picker)
        self.supplier_combo.bind('<Down>', prevent_dropdown)
        self.supplier_combo.bind('<Return>', prevent_dropdown)
        self.supplier_combo.bind('<<ComboboxSelected>>', update_balance_preview_sales)
        try:
            update_balance_preview_sales()
        except Exception:
            pass
        
        # Table frame
        table_frame = tk.Frame(main_frame, bg=self.COLORS['white'], relief='raised', bd=2)
        table_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Table header with Add Row button
        header_frame = tk.Frame(table_frame, bg=self.COLORS['info'], height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Left side - Table title
        title_frame = tk.Frame(header_frame, bg=self.COLORS['info'])
        title_frame.pack(side='left', fill='both', expand=True)
        
        header_title = tk.Label(title_frame, 
                               text="Sales Entry Table",
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
        
        # Header labels with proper widths to match fields exactly (removed Supplier column)
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
            # Load suppliers
            suppliers_query = "SELECT supplier_id, supplier_name FROM suppliers WHERE is_active = 1 ORDER BY supplier_name"
            suppliers_data = self.db.execute_query(suppliers_query)
            supplier_options = [f"{row[0]} - {row[1]}" for row in suppliers_data]
            
            # Load items
            items_query = "SELECT item_id, item_name FROM items WHERE is_active = 1 ORDER BY item_name"
            items_data = self.db.execute_query(items_query)
            item_options = [f"{row[0]} - {row[1]}" for row in items_data]
        except Exception as e:
            print(f"Error loading dropdown data: {e}")
            supplier_options = []
            item_options = []
        
        # Clear any existing sales rows
        print(f"Before clearing - sales_rows length: {len(self.sales_rows)}")
        self.sales_rows.clear()
        print(f"After clearing - sales_rows length: {len(self.sales_rows)}")
        print(f"After clearing - sales_rows id: {id(self.sales_rows)}")
        
        # Reset session counter for new modal session
        self.session_ref_counter = 0
        print(f"Session ref counter reset to: {self.session_ref_counter}")
        
        # Add a test marker to verify self object consistency
        self.test_marker = "MODAL_OPENED"
        print(f"Test marker set: {self.test_marker}")
        
        def create_sales_row(row_num):
            """Create a new sales row"""
            print(f"=== CREATE_SALES_ROW CALLED ===")
            print(f"Row number: {row_num}")
            print(f"Current sales_rows length: {len(self.sales_rows)}")
            print(f"Current sales_rows id: {id(self.sales_rows)}")
            print(f"Test marker: {getattr(self, 'test_marker', 'NOT_FOUND')}")
            print(f"Instance ID: {getattr(self, 'instance_id', 'NOT_FOUND')}")
            
            # Highlight the first row to make it more visible
            bg_color = self.COLORS['light'] if row_num == 0 else self.COLORS['white']
            row_frame = tk.Frame(scrollable_frame, bg=bg_color, relief='raised', bd=2)
            row_frame.pack(fill='x', padx=10, pady=2)
            
            # Add a subtle border to make rows more distinct
            if row_num == 0:
                row_frame.config(relief='solid', bd=2)
            
            # Use the single transaction Ref ID for all rows (already generated)
            ref_id = self.transaction_ref_id
            
            # Item dropdown
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
            for i in range(9):  # Updated to 9 columns (removed Ref ID and Supplier)
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
                        update_balance_preview_sales()
                    except Exception:
                        pass
                except (ValueError, ZeroDivisionError, TypeError) as e:
                    print(f"Error in calculate_fine_gold: {e}")  # Debug print
                    fine_entry.config(state='normal')
                    fine_entry.delete(0, tk.END)
                    fine_entry.insert(0, "0.00")
                    fine_entry.config(state='readonly')
                    try:
                        update_balance_preview_sales()
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
            
            # Manual test utility removed; live events handle calculations
            
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
            # Shift delete to previous column index after removing Test
            delete_btn.grid(row=0, column=7, sticky='ew', padx=1, pady=1)
            
            # Focus on item combo for first row
            if row_num == 0:
                item_combo.focus()
            
            # Trigger initial calculations after a short delay to ensure fields are ready
            def trigger_initial_calculations():
                print("Triggering initial calculations...")  # Debug print
                test_calculations()
            
            # Use after_idle and a short delay to ensure the GUI is fully updated
            row_frame.after_idle(trigger_initial_calculations)
            row_frame.after(100, trigger_initial_calculations)
            
            # Store row data
            row_data = {
                'row_num': row_num,
                'ref_id': ref_id,
                'item_combo': item_combo,
                'gross_entry': gross_entry,
                'less_entry': less_entry,
                'net_entry': net_entry,
                'tunch_entry': tunch_entry,
                'wastage_entry': wastage_entry,
                'fine_entry': fine_entry,
                'row_frame': row_frame
            }
            
            self.sales_rows.append(row_data)
            print(f"Added row {row_num} to sales_rows. Total rows now: {len(self.sales_rows)}")  # Debug print
            print(f"Sales_rows content after append: {[r['row_num'] for r in self.sales_rows]}")  # Debug print
            print(f"Sales_rows id after append: {id(self.sales_rows)}")  # Debug print
            update_status()
            return row_data
        
        def delete_row(row_num):
            """Delete a specific row"""
            for i, row_data in enumerate(self.sales_rows):
                if row_data['row_num'] == row_num:
                    row_data['row_frame'].destroy()
                    self.sales_rows.pop(i)
                    update_status()
                    break
        
        def add_new_row():
            """Add a new row to the table"""
            print(f"=== ADD_NEW_ROW CALLED ===")
            row_num = len(self.sales_rows)
            print(f"Adding new row {row_num}. Current sales_rows length: {len(self.sales_rows)}")  # Debug print
            print(f"Sales_rows id in add_new_row: {id(self.sales_rows)}")
            print(f"Test marker in add_new_row: {getattr(self, 'test_marker', 'NOT_FOUND')}")
            create_sales_row(row_num)
            print(f"After create_sales_row call - sales_rows length: {len(self.sales_rows)}")
        
        def save_all_sales():
            """Save all sales to database"""
            print(f"=== SAVE ALL SALES DEBUG ===")
            print(f"Number of sales rows: {len(self.sales_rows)}")
            print(f"Sales rows content: {self.sales_rows}")
            print(f"Sales rows type: {type(self.sales_rows)}")
            print(f"Sales rows id: {id(self.sales_rows)}")
            print(f"Instance ID: {getattr(self, 'instance_id', 'NOT_FOUND')}")
            print(f"Test marker: {getattr(self, 'test_marker', 'NOT_FOUND')}")
            
            if not self.sales_rows:
                messagebox.showerror("Error", "No sales to save")
                return
            
            # Check if supplier is selected
            supplier_text = self.supplier_combo.get().strip()
            if not supplier_text:
                messagebox.showerror("Error", "Please select a supplier for all entries")
                return
            
            # Validate Ref ID is set
            if not hasattr(self, 'transaction_ref_id') or not self.transaction_ref_id:
                messagebox.showerror("Error", "Transaction Ref ID not generated. Please try again.")
                return
            
            try:
                # Extract supplier info from screen-level selection
                supplier_id = int(supplier_text.split(' - ')[0])
                supplier_name = supplier_text.split(' - ')[1]
                
                print(f"=== TRANSACTION DETAILS ===")
                print(f"Transaction Ref ID: {self.transaction_ref_id}")
                print(f"Supplier: {supplier_name} (ID: {supplier_id})")
                print(f"Number of rows to process: {len(self.sales_rows)}")
                
                sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                saved_count = 0
                
                for i, row_data in enumerate(self.sales_rows):
                    print(f"\n--- Processing Row {i+1} ---")
                    item_text = row_data['item_combo'].get().strip()
                    gross = row_data['gross_entry'].get().strip()
                    less = row_data['less_entry'].get().strip()
                    tunch = row_data['tunch_entry'].get().strip()
                    wastage = row_data['wastage_entry'].get().strip()
                    
                    print(f"Supplier: '{supplier_name}' (from screen selection)")
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
                    
                    # Insert into database with single Ref ID for all entries
                    query = '''
                        INSERT INTO sales (ref_id, supplier_name, item_id, gross_weight, less_weight, 
                                         net_weight, tunch_percentage, wastage_percentage, fine_gold, sale_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
                    
                    insert_data = (
                        self.transaction_ref_id,  # Use single Ref ID for all entries
                        supplier_name,
                        item_id,
                        float(gross),
                        float(less),
                        net_weight,
                        float(tunch),
                        float(wastage),
                        fine_gold,
                        sale_date
                    )
                    
                    print(f"Inserting data: {insert_data}")
                    try:
                        self.db.execute_update(query, insert_data)
                        print(f"Data inserted successfully into sales table!")
                    except Exception as db_error:
                        print(f"Database error inserting row {i+1}: {db_error}")
                        print(f"Query: {query}")
                        print(f"Data: {insert_data}")
                        raise db_error
                    
                    # Update item inventory (subtract from inventory for sales)
                    self.main_app.update_item_inventory(item_id, fine_gold, net_weight, 'subtract')
                    
                    # Update supplier balance (add monetary value to supplier balance for sales)
                    # Update supplier balance in grams for sale
                    self.main_app.update_supplier_balance(supplier_name, fine_gold, 'add')
                    
                    saved_count += 1
                    print(f"Row {i+1}: Successfully saved!")
                
                print(f"\n=== SAVE RESULT ===")
                print(f"Total rows processed: {len(self.sales_rows)}")
                print(f"Successfully saved: {saved_count}")
                
                if saved_count > 0:
                    self.main_app.show_toast(f"Successfully saved {saved_count} sales with Ref ID: {self.transaction_ref_id}!", success=True)
                    # Call main app's load_unified_data method to refresh the unified table
                    print(f"Calling main_app.load_unified_data() to refresh main table...")
                    print(f"Main app object: {self.main_app}")
                    print(f"Main app type: {type(self.main_app)}")
                    
                    if hasattr(self.main_app, 'load_unified_data'):
                        print(f"Found load_unified_data method, calling it...")
                        self.main_app.load_unified_data()
                        print(f"Main unified table refreshed successfully!")
                    else:
                        print(f"Main app does not have load_unified_data method!")
                        print(f"Available methods: {[method for method in dir(self.main_app) if not method.startswith('_')]}")
                    modal.destroy()
                else:
                    messagebox.showerror("Error", "No valid sales to save. Please fill all required fields.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error saving sales: {e}")
        
        def clear_all_rows():
            """Clear all rows"""
            for row_data in self.sales_rows:
                row_data['row_frame'].destroy()
            self.sales_rows.clear()
            update_status()
            self.main_app.show_toast("All rows cleared", success=True)
        
        def update_status():
            """Update the status label with current row count (safe before label exists)"""
            print(f"=== UPDATE_STATUS CALLED ===")
            print(f"Sales_rows length in update_status: {len(self.sales_rows)}")
            print(f"Sales_rows id in update_status: {id(self.sales_rows)}")
            try:
                if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                    self.status_label.config(text=f"Rows: {len(self.sales_rows)}")
                    print(f"Status label updated to: Rows: {len(self.sales_rows)}")
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
            create_sales_row(i)
        
        # Add debugging for modal lifecycle
        def on_modal_close():
            print(f"=== MODAL CLOSING ===")
            print(f"Final sales_rows length: {len(self.sales_rows)}")
            print(f"Final sales_rows id: {id(self.sales_rows)}")
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
        
        # Bottom buttons frame
        button_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        button_frame.pack(side='bottom', fill='x', pady=(8, 8))

        def on_save_click():
            print(f"=== SAVE BUTTON CLICKED ===")
            print(f"Before save_all_sales - sales_rows length: {len(self.sales_rows)}")
            print(f"Sales_rows id before save: {id(self.sales_rows)}")
            save_all_sales()
            print(f"After save_all_sales - sales_rows length: {len(self.sales_rows)}")

        add_row_btn_bottom = tk.Button(button_frame,
                                 text="➕ Add Row",
                                 command=add_new_row,
                                 font=self.FONTS['body'],
                                 bg=self.COLORS['success'],
                                 fg=self.COLORS['white'],
                                 relief='raised',
                                 bd=2,
                                 padx=20,
                                 pady=8)
        add_row_btn_bottom.pack(side='left')

        save_all_btn_bottom = tk.Button(button_frame, 
                               text="💾 Save Sales",
                               command=on_save_click,
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
        modal.bind('<Control-s>', lambda _e: save_all_sales())
        modal.bind('<Control-a>', lambda _e: add_new_row())
        # Remove duplicate Ctrl+Q binding - Ctrl+A is sufficient
    
    def generate_ref_id(self, prefix):
        """Generate reference ID with format: S/P + DDMMYY + / + 3-digit incremental"""
        # Get current date in DDMMYY format
        today = datetime.now()
        date_str = today.strftime('%d%m%y')
        
        print(f"Generating Ref ID for prefix: {prefix}, date: {date_str}")  # Debug print
        
        # Get next incremental number for today
        try:
            # First check if sales table exists
            table_check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='sales'"
            table_result = self.db.execute_query(table_check_query)
            
            if not table_result:
                print("Sales table doesn't exist, using default count of 0")
                max_db_num = 0
            else:
                # Get the highest existing number for today
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
    
    def check_ref_id_exists(self):
        """Check if the generated Ref ID already exists in the database"""
        try:
            query = "SELECT COUNT(*) FROM sales WHERE ref_id = ?"
            result = self.db.execute_query(query, (self.transaction_ref_id,))
            
            if result and result[0][0] > 0:
                # Ref ID exists, show error
                messagebox.showerror("Error", 
                    f"Ref ID '{self.transaction_ref_id}' already exists in the database.\n"
                    f"Please try again to generate a new Ref ID.")
                print(f"ERROR: Ref ID {self.transaction_ref_id} already exists!")
                return False
            else:
                print(f"Ref ID {self.transaction_ref_id} is available")
                return True
                
        except Exception as e:
            print(f"Error checking Ref ID existence: {e}")
            messagebox.showerror("Error", f"Error checking Ref ID: {e}")
            return False
    
    def show_multiple_sales_modal_for_edit(self, ref_id):
        """Show multiple sales modal for editing an existing transaction group"""
        print(f"=== OPENING MULTIPLE SALES MODAL FOR EDIT ===")
        print(f"Ref ID to edit: {ref_id}")
        
        # Load existing data for this Ref ID
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
                
            print(f"Found {len(existing_records)} existing records for Ref ID: {ref_id}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading existing data: {e}")
            return
        
        # Create full-screen modal (80% of screen)
        modal = tk.Toplevel(self.root_window)
        modal.title(f"Edit Sales Transaction - {ref_id}")
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
                              text=f"Edit Sales Transaction - {ref_id}",
                              font=self.FONTS['heading'],
                              fg=self.COLORS['primary'],
                              bg=self.COLORS['light'])
        title_label.pack(pady=(0, 10))
        
        # Set the transaction Ref ID for editing
        self.transaction_ref_id = ref_id
        self.is_edit_mode = True
        self.existing_sale_ids = [record[0] for record in existing_records]  # Store sale_ids for deletion
        
        # Instructions and top controls frame
        top_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        top_frame.pack(fill='x', pady=(0, 20))
        
        # Left side - Instructions and Ref ID
        left_frame = tk.Frame(top_frame, bg=self.COLORS['light'])
        left_frame.pack(side='left', fill='x', expand=True)
        
        instructions_label = tk.Label(left_frame, 
                                     text="Instructions: Modify the table below. Use 'Add Row' to create more entries or delete existing ones.",
                                     font=self.FONTS['body'],
                                     fg=self.COLORS['dark'],
                                     bg=self.COLORS['light'])
        instructions_label.pack(anchor='w')
        
        # Ref ID display (smaller)
        ref_frame = tk.Frame(left_frame, bg=self.COLORS['light'])
        ref_frame.pack(anchor='w', pady=(5, 0))
        
        ref_label = tk.Label(ref_frame, 
                            text="Ref ID:",
                            font=self.FONTS['body'],
                            fg=self.COLORS['primary'],
                            bg=self.COLORS['light'])
        ref_label.pack(side='left')
        
        ref_display = tk.Label(ref_frame, 
                              text=self.transaction_ref_id,
                              font=self.FONTS['body'],
                              fg=self.COLORS['primary'],
                              bg=self.COLORS['light'],
                              relief='solid',
                              bd=1,
                              padx=8,
                              pady=2)
        ref_display.pack(side='left', padx=(5, 0))
        
        # Right side - Save button
        def on_save_click():
            print(f"=== SAVE BUTTON CLICKED (EDIT MODE) ===")
            print(f"Before save_all_sales - sales_rows length: {len(self.sales_rows)}")
            print(f"Sales_rows id before save: {id(self.sales_rows)}")
            save_all_sales_edit()
            print(f"After save_all_sales - sales_rows length: {len(self.sales_rows)}")
        
        # Top-right save removed; bottom bar has primary save button
        
        # Simple supplier selection
        supplier_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        supplier_frame.pack(fill='x', pady=(0, 15))
        
        supplier_label = tk.Label(supplier_frame, 
                                 text="Supplier:",
                                 font=self.FONTS['body'],
                                 fg=self.COLORS['dark'],
                                 bg=self.COLORS['light'])
        supplier_label.pack(side='left')
        
        # Load suppliers for dropdown
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
        self.supplier_combo.pack(side='left', padx=(10, 0))
        
        # Set the supplier from the first record
        if existing_records:
            first_supplier = existing_records[0][1]  # supplier_name
            # Find matching supplier in dropdown
            for option in supplier_options:
                if option.endswith(f" - {first_supplier}"):
                    self.supplier_combo.set(option)
                    break
        
        # Table frame
        table_frame = tk.Frame(main_frame, bg=self.COLORS['white'], relief='raised', bd=2)
        table_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Table header (title only)
        header_frame = tk.Frame(table_frame, bg=self.COLORS['info'], height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        title_frame = tk.Frame(header_frame, bg=self.COLORS['info'])
        title_frame.pack(side='left', fill='both', expand=True)
        header_title = tk.Label(title_frame, text="Sales Entry Table", font=self.FONTS['subheading'], fg=self.COLORS['white'], bg=self.COLORS['info'])
        header_title.pack(expand=True)
        
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
        
        # Header labels with proper widths to match fields exactly (removed Supplier column)
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
        
        # Clear any existing sales rows
        print(f"Before clearing - sales_rows length: {len(self.sales_rows)}")
        self.sales_rows.clear()
        print(f"After clearing - sales_rows length: {len(self.sales_rows)}")
        print(f"After clearing - sales_rows id: {id(self.sales_rows)}")
        
        # Reset session counter for new modal session
        self.session_ref_counter = 0
        print(f"Session ref counter reset to: {self.session_ref_counter}")
        
        # Add a test marker to verify self object consistency
        self.test_marker = "MODAL_OPENED_EDIT"
        print(f"Test marker set: {self.test_marker}")
        
        # Create a local reference to the class instance's sales_rows for the nested functions
        sales_rows_ref = self.sales_rows
        
        def create_sales_row(row_num, existing_data=None):
            """Create a new sales row with optional existing data"""
            print(f"=== CREATE_SALES_ROW CALLED (EDIT MODE) ===")
            print(f"Row number: {row_num}")
            print(f"Existing data: {existing_data}")
            print(f"Current sales_rows length: {len(sales_rows_ref)}")
            print(f"Current sales_rows id: {id(sales_rows_ref)}")
            print(f"Test marker: {getattr(self, 'test_marker', 'NOT_FOUND')}")
            print(f"Instance ID: {getattr(self, 'instance_id', 'NOT_FOUND')}")
            
            # Highlight the first row to make it more visible
            bg_color = self.COLORS['light'] if row_num == 0 else self.COLORS['white']
            row_frame = tk.Frame(scrollable_frame, bg=bg_color, relief='raised', bd=2)
            row_frame.pack(fill='x', padx=10, pady=2)
            
            # Add a subtle border to make rows more distinct
            if row_num == 0:
                row_frame.config(relief='solid', bd=2)
            
            # Use the single transaction Ref ID for all rows (already generated)
            ref_id = self.transaction_ref_id
            
            # Item dropdown
            item_combo = ttk.Combobox(row_frame, 
                                    font=self.FONTS['body'],
                                    width=30,
                                    state='readonly',
                                    values=item_options)
            item_combo.grid(row=0, column=0, sticky='ew', padx=1, pady=1)
            
            # Set existing item if provided
            if existing_data:
                item_name = existing_data[2]  # item_name from existing data
                # Find matching item in dropdown
                for option in item_options:
                    if option.endswith(f" - {item_name}"):
                        item_combo.set(option)
                        break
            
            # Gross Weight
            gross_entry = tk.Entry(row_frame, 
                                 font=self.FONTS['body'],
                                 width=15,
                                 justify='center')
            gross_entry.insert(0, f"{existing_data[3]:.3f}" if existing_data else "0.000")
            gross_entry.grid(row=0, column=1, sticky='ew', padx=1, pady=1)
            
            # Less Weight
            less_entry = tk.Entry(row_frame, 
                                font=self.FONTS['body'],
                                width=15,
                                justify='center')
            less_entry.insert(0, f"{existing_data[4]:.3f}" if existing_data else "0.000")
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
            tunch_entry.insert(0, f"{existing_data[6]:.1f}" if existing_data else "0.0")
            tunch_entry.grid(row=0, column=4, sticky='ew', padx=1, pady=1)
            
            # Wastage
            wastage_entry = tk.Entry(row_frame, 
                                   font=self.FONTS['body'],
                                   width=15,
                                   justify='center')
            wastage_entry.insert(0, f"{existing_data[7]:.1f}" if existing_data else "0.0")
            wastage_entry.grid(row=0, column=5, sticky='ew', padx=1, pady=1)
            
            # Fine Gold (calculated, readonly)
            fine_entry = tk.Entry(row_frame, 
                                font=self.FONTS['body'],
                                width=18,
                                state='readonly',
                                justify='center')
            fine_entry.grid(row=0, column=6, sticky='ew', padx=1, pady=1)
            
            # Configure grid weights
            for i in range(9):  # Updated to 9 columns (removed Ref ID and Supplier)
                row_frame.grid_columnconfigure(i, weight=1)
            
            # Calculation functions (same as before)
            def calculate_net_weight():
                try:
                    gross_text = gross_entry.get().strip()
                    less_text = less_entry.get().strip()
                    
                    print(f"Calculating net weight - Gross: '{gross_text}', Less: '{less_text}'")
                    
                    if not gross_text and not less_text:
                        net_entry.config(state='normal')
                        net_entry.delete(0, tk.END)
                        net_entry.insert(0, "0.00")
                        net_entry.config(state='readonly')
                        return
                    
                    gross = float(gross_text or 0)
                    less = float(less_text or 0)
                    net = gross - less
                    
                    print(f"Net weight calculated: {net:.2f}")
                    
                    net_entry.config(state='normal')
                    net_entry.delete(0, tk.END)
                    net_entry.insert(0, f"{net:.2f}")
                    net_entry.config(state='readonly')
                    calculate_fine_gold()
                except (ValueError, TypeError) as e:
                    print(f"Error in calculate_net_weight: {e}")
                    net_entry.config(state='normal')
                    net_entry.delete(0, tk.END)
                    net_entry.insert(0, "0.00")
                    net_entry.config(state='readonly')
            
            def calculate_fine_gold():
                try:
                    net_text = net_entry.get().strip()
                    tunch_text = tunch_entry.get().strip()
                    wastage_text = wastage_entry.get().strip()
                    
                    print(f"Calculating fine gold - Net: '{net_text}', Tunch: '{tunch_text}', Wastage: '{wastage_text}'")
                    
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
                    
                    print(f"Fine gold calculated: {fine_gold:.2f}")
                    
                    fine_entry.config(state='normal')
                    fine_entry.delete(0, tk.END)
                    fine_entry.insert(0, f"{fine_gold:.2f}")
                    fine_entry.config(state='readonly')
                    try:
                        update_balance_preview_sales()
                    except Exception:
                        pass
                except (ValueError, ZeroDivisionError, TypeError) as e:
                    print(f"Error in calculate_fine_gold: {e}")
                    fine_entry.config(state='normal')
                    fine_entry.delete(0, tk.END)
                    fine_entry.insert(0, "0.00")
                    fine_entry.config(state='readonly')
            
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
                print("Triggering initial calculations...")
                test_calculations()
            
            # Use after_idle to ensure the GUI is fully updated
            row_frame.after_idle(trigger_initial_calculations)
            
            # Also trigger after a short delay
            row_frame.after(100, trigger_initial_calculations)
            
            # Test after a longer delay
            row_frame.after(500, test_calculations)
            
            # Store row data
            row_data = {
                'row_num': row_num,
                'ref_id': ref_id,
                'item_combo': item_combo,
                'gross_entry': gross_entry,
                'less_entry': less_entry,
                'net_entry': net_entry,
                'tunch_entry': tunch_entry,
                'wastage_entry': wastage_entry,
                'fine_entry': fine_entry,
                'row_frame': row_frame,
                'existing_sale_id': existing_data[0] if existing_data else None  # Store original sale_id if editing
            }
            
            sales_rows_ref.append(row_data)
            print(f"Added row {row_num} to sales_rows. Total rows now: {len(sales_rows_ref)}")
            print(f"Sales_rows content after append: {[r['row_num'] for r in sales_rows_ref]}")
            print(f"Sales_rows id after append: {id(sales_rows_ref)}")
            update_status()
            return row_data
        
        def delete_row(row_num):
            """Delete a specific row"""
            for i, row_data in enumerate(sales_rows_ref):
                if row_data['row_num'] == row_num:
                    row_data['row_frame'].destroy()
                    sales_rows_ref.pop(i)
                    update_status()
                    break
        
        def add_new_row():
            """Add a new row to the table"""
            print(f"=== ADD_NEW_ROW CALLED (EDIT MODE) ===")
            row_num = len(sales_rows_ref)
            print(f"Adding new row {row_num}. Current sales_rows length: {len(sales_rows_ref)}")
            print(f"Sales_rows id in add_new_row: {id(sales_rows_ref)}")
            print(f"Test marker in add_new_row: {getattr(self, 'test_marker', 'NOT_FOUND')}")
            create_sales_row(row_num)
            print(f"After create_sales_row call - sales_rows length: {len(sales_rows_ref)}")
        
        def save_all_sales_edit():
            """Save all sales changes to database (edit mode)"""
            print(f"=== SAVE ALL SALES EDIT DEBUG ===")
            print(f"Number of sales rows: {len(sales_rows_ref)}")
            print(f"Sales rows content: {sales_rows_ref}")
            print(f"Sales rows type: {type(sales_rows_ref)}")
            print(f"Sales rows id: {id(sales_rows_ref)}")
            print(f"Instance ID: {getattr(self, 'instance_id', 'NOT_FOUND')}")
            print(f"Test marker: {getattr(self, 'test_marker', 'NOT_FOUND')}")
            
            if not sales_rows_ref:
                messagebox.showerror("Error", "No sales to save")
                return
            
            # Check if supplier is selected
            supplier_text = self.supplier_combo.get().strip()
            if not supplier_text:
                messagebox.showerror("Error", "Please select a supplier for all entries")
                return
            
            # Validate Ref ID is set
            if not hasattr(self, 'transaction_ref_id') or not self.transaction_ref_id:
                messagebox.showerror("Error", "Transaction Ref ID not generated. Please try again.")
                return
            
            try:
                # Extract supplier info from screen-level selection
                supplier_id = int(supplier_text.split(' - ')[0])
                supplier_name = supplier_text.split(' - ')[1]
                
                print(f"=== TRANSACTION DETAILS (EDIT) ===")
                print(f"Transaction Ref ID: {self.transaction_ref_id}")
                print(f"Supplier: {supplier_name} (ID: {supplier_id})")
                print(f"Number of rows to process: {len(self.sales_rows)}")
                
                sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                saved_count = 0
                
                # First, delete all existing records for this Ref ID
                print(f"Deleting existing records for Ref ID: {self.transaction_ref_id}")
                delete_existing_query = "DELETE FROM sales WHERE ref_id = ?"
                self.db.execute_update(delete_existing_query, (self.transaction_ref_id,))
                print(f"Deleted existing records for Ref ID: {self.transaction_ref_id}")
                
                # Then insert all current rows as new records
                for i, row_data in enumerate(sales_rows_ref):
                    print(f"\n--- Processing Row {i+1} (EDIT) ---")
                    item_text = row_data['item_combo'].get().strip()
                    gross = row_data['gross_entry'].get().strip()
                    less = row_data['less_entry'].get().strip()
                    tunch = row_data['tunch_entry'].get().strip()
                    wastage = row_data['wastage_entry'].get().strip()
                    
                    print(f"Supplier: '{supplier_name}' (from screen selection)")
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
                    
                    # Insert into database with single Ref ID for all entries
                    query = '''
                        INSERT INTO sales (ref_id, supplier_name, item_id, gross_weight, less_weight, 
                                         net_weight, tunch_percentage, wastage_percentage, fine_gold, sale_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
                    
                    insert_data = (
                        self.transaction_ref_id,  # Use single Ref ID for all entries
                        supplier_name,
                        item_id,
                        float(gross),
                        float(less),
                        net_weight,
                        float(tunch),
                        float(wastage),
                        fine_gold,
                        sale_date
                    )
                    
                    print(f"Inserting data: {insert_data}")
                    try:
                        self.db.execute_update(query, insert_data)
                        print(f"Data inserted successfully into sales table!")
                    except Exception as db_error:
                        print(f"Database error inserting row {i+1}: {db_error}")
                        print(f"Query: {query}")
                        print(f"Data: {insert_data}")
                        raise db_error
                    
                    # Update item inventory (subtract from inventory for sales)
                    self.main_app.update_item_inventory(item_id, fine_gold, net_weight, 'subtract')
                    
                    # Update supplier balance (add monetary value to supplier balance for sales)
                    self.main_app.update_supplier_balance(supplier_name, fine_gold, 'add')
                    
                    saved_count += 1
                    print(f"Row {i+1}: Successfully saved!")
                
                print(f"\n=== SAVE RESULT (EDIT) ===")
                print(f"Total rows processed: {len(self.sales_rows)}")
                print(f"Successfully saved: {saved_count}")
                
                if saved_count > 0:
                    self.main_app.show_toast(f"Successfully updated {saved_count} sales with Ref ID: {self.transaction_ref_id}!", success=True)
                    # Call main app's load_unified_data method to refresh the unified table
                    print(f"Calling main_app.load_unified_data() to refresh main table...")
                    print(f"Main app object: {self.main_app}")
                    print(f"Main app type: {type(self.main_app)}")
                    
                    if hasattr(self.main_app, 'load_unified_data'):
                        print(f"Found load_unified_data method, calling it...")
                        self.main_app.load_unified_data()
                        print(f"Main unified table refreshed successfully!")
                    else:
                        print(f"Main app does not have load_unified_data method!")
                        print(f"Available methods: {[method for method in dir(self.main_app) if not method.startswith('_')]}")
                    modal.destroy()
                else:
                    messagebox.showerror("Error", "No valid sales to save. Please fill all required fields.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error saving sales: {e}")
        
        def clear_all_rows():
            """Clear all rows"""
            for row_data in self.sales_rows:
                row_data['row_frame'].destroy()
            self.sales_rows.clear()
            update_status()
            self.main_app.show_toast("All rows cleared", success=True)
        
        def update_status():
            """Update the status label with current row count"""
            print(f"=== UPDATE_STATUS CALLED (EDIT) ===")
            print(f"Sales_rows length in update_status: {len(sales_rows_ref)}")
            print(f"Sales_rows id in update_status: {id(sales_rows_ref)}")
            try:
                if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                    self.status_label.config(text=f"Rows: {len(sales_rows_ref)}")
                    print(f"Status label updated to: Rows: {len(sales_rows_ref)}")
                else:
                    print("Status label not available yet, skipping update")
            except Exception as e:
                print(f"Error updating status label: {e}")
                print("Status label not available yet, skipping update")
        
        # Pack canvas and scrollbar first
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create rows from existing data
        print("Creating rows from existing data...")
        for i, existing_record in enumerate(existing_records):
            print(f"Creating row {i} with existing data: {existing_record}")
            create_sales_row(i, existing_record)
        print(f"After creating rows from existing data, sales_rows length: {len(sales_rows_ref)}")
        
        # Add debugging for modal lifecycle
        def on_modal_close():
            print(f"=== MODAL CLOSING (EDIT) ===")
            print(f"Final sales_rows length: {len(sales_rows_ref)}")
            print(f"Final sales_rows id: {id(sales_rows_ref)}")
            modal.destroy()
        
        modal.protocol("WM_DELETE_WINDOW", on_modal_close)
        
        # Status frame + default rows and bottom controls
        status_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        status_frame.pack(fill='x', pady=(10, 0))
        
        self.status_label = tk.Label(status_frame, 
                                    text="Rows: 0",
                                    font=self.FONTS['body'],
                                    fg=self.COLORS['primary'],
                                    bg=self.COLORS['light'])
        self.status_label.pack(side='left')
        
        # Create default 6 rows for new modal
        if not self.is_edit_mode:
            for i in range(6):
                add_new_row()

        # Bottom buttons frame
        button_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        button_frame.pack(fill='x', pady=(15, 0))
        
        add_row_btn_bottom = tk.Button(button_frame,
                                 text="➕ Add Row",
                                 command=add_new_row,
                                 font=self.FONTS['body'],
                                 bg=self.COLORS['success'],
                                 fg=self.COLORS['white'],
                                 relief='raised',
                                 bd=2,
                                 padx=20,
                                 pady=8)
        add_row_btn_bottom.pack(side='left')

        save_all_btn_bottom = tk.Button(button_frame,
                               text="💾 Save Changes (Ctrl+S)" if self.is_edit_mode else "💾 Save Sales (Ctrl+S)",
                               command=on_save_click,
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
