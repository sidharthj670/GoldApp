import tkinter as tk
from tkinter import ttk, messagebox

class KarigarOrdersManager:
    def __init__(self, root_window, main_app, db_manager, colors, fonts):
        self.root_window = root_window
        self.main_app = main_app
        self.db = db_manager
        self.COLORS = colors
        self.FONTS = fonts
        self.issued_rows = []
        self.received_rows = []

    def show_create_order_modal(self):
        modal = tk.Toplevel(self.root_window)
        modal.title("Create Karigar Order")
        modal.update_idletasks()
        sw, sh = modal.winfo_screenwidth(), modal.winfo_screenheight()
        mw, mh = int(sw * 0.8), int(sh * 0.8)
        mx, my = (sw - mw) // 2, (sh - mh) // 2
        modal.geometry(f"{mw}x{mh}+{mx}+{my}")
        modal.transient(self.root_window)
        modal.grab_set()
        # Close on ESC and keyboard shortcuts
        try:
            modal.bind('<Escape>', lambda _e: modal.destroy())
            # Keyboard shortcuts for create modal
            modal.bind('<Control-q>', lambda _e: add_issued_row())
            modal.bind('<Control-a>', lambda _e: add_received_row())
            modal.bind('<Control-s>', lambda _e: save_order())
            modal.bind('<Control-d>', lambda _e: save_order())  # Ctrl+D for delete/save
        except Exception:
            pass

        main_frame = tk.Frame(modal, bg=self.COLORS['light'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        title = tk.Label(main_frame, text="New Karigar Order", font=self.FONTS['heading'], fg=self.COLORS['primary'], bg=self.COLORS['light'])
        title.pack(pady=(0, 8))

        # Karigar selection
        karigar_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        karigar_frame.pack(fill='x', pady=(0, 10))
        tk.Label(karigar_frame, text="Karigar:", font=self.FONTS['body'], bg=self.COLORS['light'], fg=self.COLORS['dark']).pack(side='left')
        karigar_combo = ttk.Combobox(karigar_frame, font=self.FONTS['body'], width=30, state='readonly')

        def load_karigar_options():
            options = []
            # Heuristically detect columns
            try:
                cols = self.db.execute_query("PRAGMA table_info(freelancers)")
            except Exception:
                cols = []
            id_col, name_col, active_col = None, None, None
            if cols:
                colnames = [c[1] for c in cols]
                lower = [n.lower() for n in colnames]
                # id column
                for n in colnames:
                    ln = n.lower()
                    if ln.endswith('_id') or ln == 'id':
                        id_col = n
                        break
                # name column
                for n in colnames:
                    ln = n.lower()
                    if 'name' in ln:
                        name_col = n
                        break
                # active column (optional)
                for n in colnames:
                    ln = n.lower()
                    if ln in ('is_active','active'):
                        active_col = n
                        break
            # Build query safely
            if id_col and name_col:
                where_active = f"WHERE COALESCE({active_col},1)=1" if active_col else ""
                order = f"ORDER BY {name_col}"
                q = f"SELECT {id_col}, {name_col} FROM freelancers {where_active} {order}"
                try:
                    rows = self.db.execute_query(q)
                    if rows:
                        options = [f"{r[0]} - {r[1]}" for r in rows]
                except Exception:
                    options = []
            # Fallback: try known patterns
            if not options:
                patterns = [
                    "SELECT freelancer_id, freelancer_name FROM freelancers ORDER BY freelancer_name",
                    "SELECT id, name FROM freelancers ORDER BY name",
                ]
                for q in patterns:
                    try:
                        rows = self.db.execute_query(q)
                        if rows:
                            options = [f"{r[0]} - {r[1]}" for r in rows]
                            break
                    except Exception:
                        continue
            karigar_combo['values'] = options

        load_karigar_options()
        karigar_combo.pack(side='left', padx=(10, 0))
        # Top actions (ensure a visible save entry point)
        actions_top = tk.Frame(main_frame, bg=self.COLORS['light'])
        actions_top.pack(fill='x', pady=(0, 6))
        tk.Button(actions_top,
                  text='💾 Save Order',
                  command=lambda: save_order(),
                  font=self.FONTS['body'],
                  bg=self.COLORS['primary'],
                  fg='white',
                  relief='raised', bd=2, padx=16, pady=6).pack(side='right')
        # Reload on click in case list changed
        karigar_combo.bind('<Button-1>', lambda _e: load_karigar_options())

        # Two columns: Issued and Received
        body = tk.Frame(main_frame, bg=self.COLORS['light'])
        body.pack(fill='both', expand=True)

        issued_section = tk.Frame(body, bg=self.COLORS['white'], relief='ridge', bd=1)
        issued_section.pack(side='left', fill='both', expand=True, padx=(0, 8), pady=4)
        received_section = tk.Frame(body, bg=self.COLORS['white'], relief='ridge', bd=1)
        received_section.pack(side='right', fill='both', expand=True, padx=(8, 0), pady=4)

        tk.Label(issued_section, text="Issued Items", font=self.FONTS['subheading'], fg=self.COLORS['primary'], bg=self.COLORS['white']).pack(fill='x', pady=(6, 6))
        tk.Label(received_section, text="Received Items", font=self.FONTS['subheading'], fg=self.COLORS['primary'], bg=self.COLORS['white']).pack(fill='x', pady=(6, 6))

        # Issued table
        issued_canvas = tk.Canvas(issued_section, bg=self.COLORS['light'])
        issued_scroll = ttk.Scrollbar(issued_section, orient='vertical', command=issued_canvas.yview)
        issued_frame = tk.Frame(issued_canvas, bg=self.COLORS['light'])
        issued_frame.bind('<Configure>', lambda e: issued_canvas.configure(scrollregion=issued_canvas.bbox('all')))
        issued_canvas.create_window((0, 0), window=issued_frame, anchor='nw')
        issued_canvas.configure(yscrollcommand=issued_scroll.set)
        issued_canvas.pack(side='left', fill='both', expand=True)
        issued_scroll.pack(side='right', fill='y')

        # Received table
        recv_canvas = tk.Canvas(received_section, bg=self.COLORS['light'])
        recv_scroll = ttk.Scrollbar(received_section, orient='vertical', command=recv_canvas.yview)
        recv_frame = tk.Frame(recv_canvas, bg=self.COLORS['light'])
        recv_frame.bind('<Configure>', lambda e: recv_canvas.configure(scrollregion=recv_canvas.bbox('all')))
        recv_canvas.create_window((0, 0), window=recv_frame, anchor='nw')
        recv_canvas.configure(yscrollcommand=recv_scroll.set)
        recv_canvas.pack(side='left', fill='both', expand=True)
        recv_scroll.pack(side='right', fill='y')

        # Load inventory items for dropdowns
        try:
            items = self.db.execute_query("SELECT item_id, item_name FROM items WHERE is_active = 1 ORDER BY item_name")
            item_options = [f"{r[0]} - {r[1]}" for r in items]
        except Exception:
            item_options = []

        def add_issued_row():
            row = tk.Frame(issued_frame, bg=self.COLORS['light'], relief='ridge', bd=1)
            row.pack(fill='x', padx=6, pady=2)
            item_combo = ttk.Combobox(row, values=item_options, state='readonly', width=28, font=self.FONTS['body'])
            item_combo.grid(row=0, column=0, sticky='ew', padx=2, pady=2)
            wt_entry = tk.Entry(row, width=12, font=self.FONTS['body'], justify='center')
            wt_entry.grid(row=0, column=1, sticky='ew', padx=2, pady=2)
            # Bind live updates safely
            try:
                wt_entry.bind('<KeyRelease>', update_balance_view)
                wt_entry.bind('<FocusOut>', update_balance_view)
                item_combo.bind('<<ComboboxSelected>>', update_balance_view)
            except Exception:
                pass
            del_btn = tk.Button(row, text='🗑️', font=self.FONTS['body'], bg=self.COLORS['warning'], fg='white', relief='raised', bd=1, width=4,
                                command=lambda f=row: remove_issued_row(f))
            del_btn.grid(row=0, column=2, sticky='ew', padx=2, pady=2)
            self.issued_rows.append({'frame': row, 'item_combo': item_combo, 'weight_entry': wt_entry})
            # Trigger recalc immediately
            try:
                update_balance_view()
            except Exception:
                pass

        def add_received_row():
            row = tk.Frame(recv_frame, bg=self.COLORS['light'], relief='ridge', bd=1)
            row.pack(fill='x', padx=6, pady=2)
            item_combo = ttk.Combobox(row, values=item_options, state='readonly', width=28, font=self.FONTS['body'])
            item_combo.grid(row=0, column=0, sticky='ew', padx=2, pady=2)
            wt_entry = tk.Entry(row, width=12, font=self.FONTS['body'], justify='center')
            wt_entry.grid(row=0, column=1, sticky='ew', padx=2, pady=2)
            try:
                wt_entry.bind('<KeyRelease>', update_balance_view)
                wt_entry.bind('<FocusOut>', update_balance_view)
                item_combo.bind('<<ComboboxSelected>>', update_balance_view)
            except Exception:
                pass
            del_btn = tk.Button(row, text='🗑️', font=self.FONTS['body'], bg=self.COLORS['warning'], fg='white', relief='raised', bd=1, width=4,
                                command=lambda f=row: remove_received_row(f))
            del_btn.grid(row=0, column=2, sticky='ew', padx=2, pady=2)
            self.received_rows.append({'frame': row, 'item_combo': item_combo, 'weight_entry': wt_entry})
            try:
                update_balance_view()
            except Exception:
                pass

        def remove_issued_row(frame):
            try:
                for i, r in enumerate(list(self.issued_rows)):
                    if r.get('frame') == frame:
                        self.issued_rows.pop(i)
                        try:
                            r['frame'].destroy()
                        except Exception:
                            pass
                        break
            except Exception:
                pass
            update_balance_view()

        def remove_received_row(frame):
            try:
                for i, r in enumerate(list(self.received_rows)):
                    if r.get('frame') == frame:
                        self.received_rows.pop(i)
                        try:
                            r['frame'].destroy()
                        except Exception:
                            pass
                        break
            except Exception:
                pass
            update_balance_view()

        # Defaults
        for _ in range(3):
            add_issued_row()
        for _ in range(3):
            add_received_row()

        # Bottom: balance view and actions
        bottom = tk.Frame(main_frame, bg=self.COLORS['light'])
        bottom.pack(side='bottom', fill='x', pady=(8, 0))
        balance_card = tk.Frame(bottom, bg='#f7f7ff', relief='ridge', bd=1)
        balance_card.pack(fill='x', padx=6, pady=(0, 8))
        tk.Label(balance_card, text='Order Balance', font=self.FONTS['subheading'], fg=self.COLORS['primary'], bg='#f7f7ff').pack(side='left', padx=8, pady=6)
        balance_value = tk.Label(balance_card, text='0.00 g', font=self.FONTS['subheading'], fg=self.COLORS['dark'], bg='#f7f7ff')
        balance_value.pack(side='right', padx=10, pady=6)

        def parse_weight(entry):
            try:
                return float((entry.get() or '0').strip())
            except Exception:
                return 0.0

        def update_balance_view(_e=None):
            issued_total = sum(parse_weight(r['weight_entry']) for r in self.issued_rows)
            received_total = sum(parse_weight(r['weight_entry']) for r in self.received_rows)
            balance = issued_total - received_total
            balance_value.config(text=f"{balance:.3f} g")

        # Initial balance compute
        try:
            update_balance_view()
        except Exception:
            pass

        # Buttons
        btns = tk.Frame(bottom, bg=self.COLORS['light'])
        btns.pack(fill='x')
        add_issued = tk.Button(btns, text='➕ Add Issued', command=lambda: (add_issued_row(), update_balance_view()), font=self.FONTS['body'], bg=self.COLORS['success'], fg='white')
        add_issued.pack(side='left', padx=(0, 6))
        add_received = tk.Button(btns, text='➕ Add Received', command=lambda: (add_received_row(), update_balance_view()), font=self.FONTS['body'], bg=self.COLORS['info'], fg='white')
        add_received.pack(side='left', padx=(0, 6))

        def _unbind_row_events():
            try:
                for r in (self.issued_rows + self.received_rows):
                    try:
                        r['weight_entry'].unbind('<KeyRelease>')
                        r['weight_entry'].unbind('<FocusOut>')
                    except Exception:
                        pass
                    try:
                        # Combobox usually has no extra binds, but guard anyway
                        r['item_combo'].unbind('<<ComboboxSelected>>')
                    except Exception:
                        pass
            except Exception:
                pass

        def save_order():
            karigar_text = karigar_combo.get().strip()
            if not karigar_text:
                messagebox.showerror("Error", "Please select a karigar")
                return
            try:
                print("[KarigarOrder] SAVE start")
                print(f"  Issued rows: {len(self.issued_rows)} | Received rows: {len(self.received_rows)}")
                # compute totals
                issued_total = sum(parse_weight(r['weight_entry']) for r in self.issued_rows)
                received_total = sum(parse_weight(r['weight_entry']) for r in self.received_rows)
                balance_total = issued_total - received_total
                from datetime import datetime
                created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Generate Ref ID: KO + ddmmyy + / + seq
                date_str = datetime.now().strftime('%d%m%y')
                try:
                    row_last = self.db.execute_query(
                        "SELECT ref_id FROM karigar_orders WHERE ref_id LIKE ? ORDER BY ref_id DESC LIMIT 1",
                        (f"KO{date_str}/%",)
                    )
                    if row_last and row_last[0][0]:
                        last_num = int(str(row_last[0][0]).split('/')[-1])
                    else:
                        last_num = 0
                except Exception:
                    last_num = 0
                ref_id = f"KO{date_str}/{last_num + 1:03d}"
                karigar_id = int(karigar_text.split(' - ')[0]) if ' - ' in karigar_text else None
                karigar_name = karigar_text.split(' - ')[1] if ' - ' in karigar_text else karigar_text
                # Ensure karigar_orders table exists and insert summary row
                print(f"  Using Ref ID: {ref_id}")
                self.db.execute_update(
                    """
                    CREATE TABLE IF NOT EXISTS karigar_orders (
                        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ref_id TEXT,
                        karigar_id INTEGER,
                        karigar_name TEXT,
                        issued_total REAL DEFAULT 0,
                        received_total REAL DEFAULT 0,
                        balance_total REAL DEFAULT 0,
                        status TEXT DEFAULT 'in progress',
                        created_at TEXT
                    )
                    """
                )
                # Ensure ref_id column exists
                try:
                    cols = self.db.execute_query("PRAGMA table_info(karigar_orders)") or []
                    if not any(c[1].lower() == 'ref_id' for c in cols):
                        self.db.execute_update("ALTER TABLE karigar_orders ADD COLUMN ref_id TEXT")
                except Exception:
                    pass
                # Detail items table
                self.db.execute_update(
                    """
                    CREATE TABLE IF NOT EXISTS karigar_order_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id INTEGER,
                        item_id INTEGER,
                        item_name TEXT,
                        direction TEXT,
                        weight REAL,
                        created_at TEXT
                    )
                    """
                )
                self.db.execute_update(
                    """
                    INSERT INTO karigar_orders (ref_id, karigar_id, karigar_name, issued_total, received_total, balance_total, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'in progress', ?)
                    """,
                    (ref_id, karigar_id, karigar_name, issued_total, received_total, balance_total, created_at)
                )
                # Retrieve last order id
                try:
                    last_id_row = self.db.execute_query("SELECT last_insert_rowid()")
                    order_id = last_id_row[0][0] if last_id_row else None
                except Exception:
                    order_id = None
                print(f"  Inserted order_id: {order_id}")
                for r in self.issued_rows:
                    try:
                        exists_combo = 0
                        exists_entry = 0
                        try:
                            exists_combo = int(r['item_combo'].winfo_exists())
                            exists_entry = int(r['weight_entry'].winfo_exists())
                        except Exception:
                            pass
                        print(f"  [Issued] row exists? combo={exists_combo} entry={exists_entry}")
                        item_text = ''
                        try:
                            item_text = (r['item_combo'].get() or '').strip()
                        except Exception as ee:
                            print(f"    ERROR getting combo value: {ee}")
                            item_text = ''
                        if not item_text:
                            continue
                        item_id = int(item_text.split(' - ')[0])
                        wt = parse_weight(r['weight_entry'])
                        print(f"    issue item_id={item_id} name={item_text} wt={wt}")
                    except Exception as loop_e:
                        print(f"    ERROR preparing issued row: {loop_e}")
                        continue
                    # Subtract inventory
                    try:
                        self.main_app.update_item_inventory(item_id, wt, wt, 'subtract')
                    except Exception as inv_e:
                        print(f"    ERROR updating inventory (issued): {inv_e}")
                    if order_id and wt > 0:
                        try:
                            self.db.execute_update(
                                "INSERT INTO karigar_order_items (order_id, item_id, item_name, direction, weight, created_at) VALUES (?, ?, ?, 'issued', ?, ?)",
                                (order_id, item_id, item_text.split(' - ')[1], wt, created_at)
                            )
                        except Exception as det_e:
                            print(f"    ERROR inserting issued detail: {det_e}")
                for r in self.received_rows:
                    try:
                        exists_combo = 0
                        exists_entry = 0
                        try:
                            exists_combo = int(r['item_combo'].winfo_exists())
                            exists_entry = int(r['weight_entry'].winfo_exists())
                        except Exception:
                            pass
                        print(f"  [Received] row exists? combo={exists_combo} entry={exists_entry}")
                        item_text = ''
                        try:
                            item_text = (r['item_combo'].get() or '').strip()
                        except Exception as ee:
                            print(f"    ERROR getting combo value: {ee}")
                            item_text = ''
                        if not item_text:
                            continue
                        item_id = int(item_text.split(' - ')[0])
                        wt = parse_weight(r['weight_entry'])
                        print(f"    recv item_id={item_id} name={item_text} wt={wt}")
                    except Exception as loop_e:
                        print(f"    ERROR preparing received row: {loop_e}")
                        continue
                    # Add inventory
                    try:
                        self.main_app.update_item_inventory(item_id, wt, wt, 'add')
                    except Exception as inv_e:
                        print(f"    ERROR updating inventory (received): {inv_e}")
                    if order_id and wt > 0:
                        try:
                            self.db.execute_update(
                                "INSERT INTO karigar_order_items (order_id, item_id, item_name, direction, weight, created_at) VALUES (?, ?, ?, 'received', ?, ?)",
                                (order_id, item_id, item_text.split(' - ')[1], wt, created_at)
                            )
                        except Exception as det_e:
                            print(f"    ERROR inserting received detail: {det_e}")
                # Refresh table in main app if available
                try:
                    self.main_app.load_karigar_orders_data()
                except Exception:
                    pass
                self.main_app.show_toast("Karigar order saved and inventory updated", success=True)
                # Unbind events to prevent callbacks during destroy
                _unbind_row_events()
                modal.destroy()
            except Exception as e:
                # Log to console for easier debugging in addition to UI error
                try:
                    print(f"Error saving karigar order: {e}")
                except Exception:
                    pass
                messagebox.showerror("Error", f"Error saving order: {e}")

        save_btn = tk.Button(btns, text='💾 Save Order', command=save_order, font=self.FONTS['body'], bg=self.COLORS['primary'], fg='white')
        save_btn.pack(side='left', padx=(6, 6))
        cancel_btn = tk.Button(btns, text='❌ Cancel', command=modal.destroy, font=self.FONTS['body'], bg=self.COLORS['secondary'], fg='white')
        cancel_btn.pack(side='right')

    def show_edit_order_modal(self, order_id: int):
        """Open the same layout to add issued/received to an in-progress order.
        This appends to totals and updates inventory accordingly.
        """
        # Fetch existing summary
        try:
            row = self.db.execute_query(
                "SELECT karigar_id, karigar_name, issued_total, received_total, balance_total, status FROM karigar_orders WHERE order_id = ?",
                (order_id,)
            )
            if not row:
                messagebox.showerror("Error", "Order not found")
                return
            karigar_id, karigar_name, issued_total, received_total, balance_total, status = row[0]
            if str(status).strip().lower() != 'in progress':
                messagebox.showwarning("Warning", "Only in progress orders can be updated")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error loading order: {e}")
            return

        modal = tk.Toplevel(self.root_window)
        modal.title(f"Update Karigar Order #{order_id}")
        modal.update_idletasks()
        sw, sh = modal.winfo_screenwidth(), modal.winfo_screenheight()
        mw, mh = int(sw * 0.8), int(sh * 0.8)
        mx, my = (sw - mw) // 2, (sh - mh) // 2
        modal.geometry(f"{mw}x{mh}+{mx}+{my}")
        modal.transient(self.root_window)
        modal.grab_set()
        try:
            modal.bind('<Escape>', lambda _e: modal.destroy())
            # Keyboard shortcuts for edit modal
            modal.bind('<Control-q>', lambda _e: add_issued_row())
            modal.bind('<Control-a>', lambda _e: add_received_row())
            modal.bind('<Control-s>', lambda _e: apply_updates())
            modal.bind('<Control-d>', lambda _e: apply_updates())  # Ctrl+D for delete/save
        except Exception:
            pass

        main_frame = tk.Frame(modal, bg=self.COLORS['light'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        tk.Label(main_frame, text=f"Update Karigar Order #{order_id}", font=self.FONTS['heading'], fg=self.COLORS['primary'], bg=self.COLORS['light']).pack(pady=(0,8))

        karigar_frame = tk.Frame(main_frame, bg=self.COLORS['light'])
        karigar_frame.pack(fill='x', pady=(0, 10))
        tk.Label(karigar_frame, text="Karigar:", font=self.FONTS['body'], bg=self.COLORS['light'], fg=self.COLORS['dark']).pack(side='left')
        karigar_label = tk.Label(karigar_frame, text=karigar_name or '', font=self.FONTS['body'], bg=self.COLORS['light'], fg=self.COLORS['primary'])
        karigar_label.pack(side='left', padx=(8,0))

        # Reuse same body building for two sections
        body = tk.Frame(main_frame, bg=self.COLORS['light'])
        body.pack(fill='both', expand=True)
        issued_section = tk.Frame(body, bg=self.COLORS['white'], relief='ridge', bd=1)
        issued_section.pack(side='left', fill='both', expand=True, padx=(0, 8), pady=4)
        received_section = tk.Frame(body, bg=self.COLORS['white'], relief='ridge', bd=1)
        received_section.pack(side='right', fill='both', expand=True, padx=(8, 0), pady=4)
        tk.Label(issued_section, text="Issued Items", font=self.FONTS['subheading'], fg=self.COLORS['primary'], bg=self.COLORS['white']).pack(fill='x', pady=(6, 6))
        tk.Label(received_section, text="Received Items", font=self.FONTS['subheading'], fg=self.COLORS['primary'], bg=self.COLORS['white']).pack(fill='x', pady=(6, 6))

        issued_canvas = tk.Canvas(issued_section, bg=self.COLORS['light'])
        issued_scroll = ttk.Scrollbar(issued_section, orient='vertical', command=issued_canvas.yview)
        issued_frame = tk.Frame(issued_canvas, bg=self.COLORS['light'])
        issued_frame.bind('<Configure>', lambda e: issued_canvas.configure(scrollregion=issued_canvas.bbox('all')))
        issued_canvas.create_window((0, 0), window=issued_frame, anchor='nw')
        issued_canvas.configure(yscrollcommand=issued_scroll.set)
        issued_canvas.pack(side='left', fill='both', expand=True)
        issued_scroll.pack(side='right', fill='y')

        recv_canvas = tk.Canvas(received_section, bg=self.COLORS['light'])
        recv_scroll = ttk.Scrollbar(received_section, orient='vertical', command=recv_canvas.yview)
        recv_frame = tk.Frame(recv_canvas, bg=self.COLORS['light'])
        recv_frame.bind('<Configure>', lambda e: recv_canvas.configure(scrollregion=recv_canvas.bbox('all')))
        recv_canvas.create_window((0, 0), window=recv_frame, anchor='nw')
        recv_canvas.configure(yscrollcommand=recv_scroll.set)
        recv_canvas.pack(side='left', fill='both', expand=True)
        recv_scroll.pack(side='right', fill='y')

        try:
            items = self.db.execute_query("SELECT item_id, item_name FROM items WHERE is_active = 1 ORDER BY item_name")
            item_options = [f"{r[0]} - {r[1]}" for r in items]
        except Exception:
            item_options = []

        add_issued_rows, add_received_rows = [], []
        # Existing items lists
        exist_issued = tk.Frame(issued_frame, bg=self.COLORS['light'])
        exist_issued.pack(fill='x', padx=6, pady=2)
        exist_received = tk.Frame(recv_frame, bg=self.COLORS['light'])
        exist_received.pack(fill='x', padx=6, pady=2)
        def add_issued_row():
            row = tk.Frame(issued_frame, bg=self.COLORS['light'], relief='ridge', bd=1)
            row.pack(fill='x', padx=6, pady=2)
            item_combo = ttk.Combobox(row, values=item_options, state='readonly', width=28, font=self.FONTS['body'])
            item_combo.grid(row=0, column=0, sticky='ew', padx=2, pady=2)
            wt_entry = tk.Entry(row, width=12, font=self.FONTS['body'], justify='center')
            wt_entry.grid(row=0, column=1, sticky='ew', padx=2, pady=2)
            # Bind live updates
            try:
                wt_entry.bind('<KeyRelease>', update_balance_view)
                wt_entry.bind('<FocusOut>', update_balance_view)
                item_combo.bind('<<ComboboxSelected>>', update_balance_view)
            except Exception:
                pass
            add_issued_rows.append({'frame': row, 'item_combo': item_combo, 'weight_entry': wt_entry})
            # Trigger recalc immediately
            try:
                update_balance_view()
            except Exception:
                pass

        def add_received_row():
            row = tk.Frame(recv_frame, bg=self.COLORS['light'], relief='ridge', bd=1)
            row.pack(fill='x', padx=6, pady=2)
            item_combo = ttk.Combobox(row, values=item_options, state='readonly', width=28, font=self.FONTS['body'])
            item_combo.grid(row=0, column=0, sticky='ew', padx=2, pady=2)
            wt_entry = tk.Entry(row, width=12, font=self.FONTS['body'], justify='center')
            wt_entry.grid(row=0, column=1, sticky='ew', padx=2, pady=2)
            # Bind live updates
            try:
                wt_entry.bind('<KeyRelease>', update_balance_view)
                wt_entry.bind('<FocusOut>', update_balance_view)
                item_combo.bind('<<ComboboxSelected>>', update_balance_view)
            except Exception:
                pass
            add_received_rows.append({'frame': row, 'item_combo': item_combo, 'weight_entry': wt_entry})
            # Trigger recalc immediately
            try:
                update_balance_view()
            except Exception:
                pass

        # Load existing detail items
        try:
            items = self.db.execute_query(
                "SELECT item_name, direction, weight FROM karigar_order_items WHERE order_id = ? ORDER BY id",
                (order_id,)
            ) or []
            for item_name, direction, weight in items:
                host = exist_issued if str(direction).lower() == 'issued' else exist_received
                row = tk.Frame(host, bg=self.COLORS['light'])
                row.pack(fill='x', padx=0, pady=1)
                tk.Label(row, text=item_name or '', font=self.FONTS['body'], bg=self.COLORS['light'], fg=self.COLORS['dark'], width=28, anchor='w').grid(row=0, column=0, sticky='ew', padx=2)
                e = tk.Entry(row, width=12, font=self.FONTS['body'], justify='center')
                e.insert(0, f"{float(weight or 0):.2f}")
                e.config(state='readonly')
                e.grid(row=0, column=1, sticky='ew', padx=2)
        except Exception:
            pass
        # Provide 2 new rows each to add more
        for _ in range(2):
            add_issued_row()
        for _ in range(2):
            add_received_row()

        bottom = tk.Frame(main_frame, bg=self.COLORS['light'])
        bottom.pack(side='bottom', fill='x', pady=(8, 0))
        
        # Balance display section
        balance_frame = tk.Frame(bottom, bg='#f7f7ff', relief='ridge', bd=1)
        balance_frame.pack(fill='x', padx=6, pady=(0, 8))
        
        current_balance_label = tk.Label(balance_frame, text=f"Current Balance: {balance_total or 0:.3f} g", font=self.FONTS['body'], fg=self.COLORS['dark'], bg='#f7f7ff')
        current_balance_label.pack(side='left', padx=8, pady=6)
        
        balance_label = tk.Label(balance_frame, text=f"Projected Balance: {balance_total or 0:.3f} g", font=self.FONTS['subheading'], fg=self.COLORS['primary'], bg='#f7f7ff')
        balance_label.pack(side='right', padx=10, pady=6)

        def parse_w(e):
            try:
                return float((e.get() or '0').strip())
            except Exception:
                return 0.0

        def update_balance_view(_e=None):
            # Calculate deltas from new rows only
            issued_delta = sum(parse_w(r['weight_entry']) for r in add_issued_rows)
            received_delta = sum(parse_w(r['weight_entry']) for r in add_received_rows)
            # Show projected balance (current + deltas)
            projected_balance = (balance_total or 0) + issued_delta - received_delta
            # Update the balance display
            try:
                balance_label.config(text=f"Projected Balance: {projected_balance:.3f} g")
            except Exception:
                pass

        def apply_updates():
            try:
                issued_delta = sum(parse_w(r['weight_entry']) for r in add_issued_rows)
                received_delta = sum(parse_w(r['weight_entry']) for r in add_received_rows)
                new_issued = (issued_total or 0) + issued_delta
                new_received = (received_total or 0) + received_delta
                new_balance = new_issued - new_received
                # Update summary row
                self.db.execute_update(
                    "UPDATE karigar_orders SET issued_total = ?, received_total = ?, balance_total = ? WHERE order_id = ?",
                    (new_issued, new_received, new_balance, order_id)
                )
                # Adjust inventory for deltas only
                for r in add_issued_rows:
                    item_text = r['item_combo'].get().strip()
                    if not item_text:
                        continue
                    item_id = int(item_text.split(' - ')[0])
                    wt = parse_w(r['weight_entry'])
                    if wt > 0:
                        self.main_app.update_item_inventory(item_id, wt, wt, 'subtract')
                        # add detail record
                        from datetime import datetime
                        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.db.execute_update(
                            "INSERT INTO karigar_order_items (order_id, item_id, item_name, direction, weight, created_at) VALUES (?, ?, ?, 'issued', ?, ?)",
                            (order_id, item_id, item_text.split(' - ')[1], wt, created_at)
                        )
                for r in add_received_rows:
                    item_text = r['item_combo'].get().strip()
                    if not item_text:
                        continue
                    item_id = int(item_text.split(' - ')[0])
                    wt = parse_w(r['weight_entry'])
                    if wt > 0:
                        self.main_app.update_item_inventory(item_id, wt, wt, 'add')
                        from datetime import datetime
                        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.db.execute_update(
                            "INSERT INTO karigar_order_items (order_id, item_id, item_name, direction, weight, created_at) VALUES (?, ?, ?, 'received', ?, ?)",
                            (order_id, item_id, item_text.split(' - ')[1], wt, created_at)
                        )
                try:
                    self.main_app.load_karigar_orders_data()
                except Exception:
                    pass
                self.main_app.show_toast("Order updated", success=True)
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error updating order: {e}")

        btns = tk.Frame(bottom, bg=self.COLORS['light'])
        btns.pack(fill='x')
        tk.Button(btns, text='➕ Add Issued', command=add_issued_row, font=self.FONTS['body'], bg=self.COLORS['success'], fg='white').pack(side='left', padx=(0,6))
        tk.Button(btns, text='➕ Add Received', command=add_received_row, font=self.FONTS['body'], bg=self.COLORS['info'], fg='white').pack(side='left', padx=(0,6))
        tk.Button(btns, text='💾 Save Updates', command=apply_updates, font=self.FONTS['body'], bg=self.COLORS['primary'], fg='white').pack(side='left', padx=(6,6))
        tk.Button(btns, text='❌ Cancel', command=modal.destroy, font=self.FONTS['body'], bg=self.COLORS['secondary'], fg='white').pack(side='right')


