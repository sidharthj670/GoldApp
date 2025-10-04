"""
Main application file for Gold Jewelry Business Management System
This is the entry point for the application
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager
from inventory import InventoryManager
from freelancer import FreelancerManager
from workorder import WorkOrderManager
from karigar_orders import KarigarOrdersManager
from supplier import SupplierManager
from multiple_sales import MultipleSalesManager
from multiple_purchases import MultiplePurchasesManager

# Define color scheme
COLORS = {
    'primary': '#2c3e50',      # Dark blue-gray
    'secondary': '#3498db',     # Blue
    'accent': '#e74c3c',       # Red
    'success': '#27ae60',      # Green
    'warning': '#f39c12',      # Orange
    'info': '#17a2b8',        # Light blue
    'danger': '#e74c3c',      # Red (same as accent)
    'light': '#ecf0f1',       # Light gray
    'dark': '#34495e',        # Dark gray
    'white': '#ffffff',       # White
    'gold': '#ffd700',        # Gold
    'silver': '#c0c0c0'       # Silver
}

# Define fonts
FONTS = {
    'title': ('Segoe UI', 24, 'bold'),
    'heading': ('Segoe UI', 16, 'bold'),
    'subheading': ('Segoe UI', 12, 'bold'),
    'body': ('Segoe UI', 10),
    'button': ('Segoe UI', 10, 'bold'),
    'small': ('Segoe UI', 9)
}

class GoldJewelryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gold Jewelry Business Management System")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS['light'])
        
        # Configure style
        self.configure_styles()
        
        # Center the window
        self.center_window()
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Initialize managers
        self.freelancer_manager = FreelancerManager(self.db, self.show_toast)
        self.work_order_manager = WorkOrderManager(self.db)
        self.karigar_orders_manager = KarigarOrdersManager(self.root, self, self.db, COLORS, FONTS)
        self.supplier_manager = SupplierManager(self.db, self)
        self.multiple_sales_manager = MultipleSalesManager(self.root, self, self.db, COLORS, FONTS)
        self.multiple_purchases_manager = MultiplePurchasesManager(self.root, self, self.db, COLORS, FONTS)
        
        # Create main interface
        self.create_widgets()
        
        # Load initial data
        self.load_data()
    
        # Add global keyboard shortcuts
        self.setup_keyboard_shortcuts()

        # Initialize toast notification system
        self.toast_label = None
        self.toast_after_id = None

        # Backup scheduler handle
        self._schedule_backup_job_id = None
        # Ensure scheduler state aligns with toggle if created later
        # Will be (re)synchronized when home tab is built or toggle changes

    def show_toast(self, message, duration=3000, success=True):
        """Show a toast notification that disappears automatically"""
        # Cancel any existing toast
        if self.toast_after_id:
            self.root.after_cancel(self.toast_after_id)
            if self.toast_label:
                self.toast_label.destroy()

        # Create toast label
        self.toast_label = tk.Label(
            self.root,
            text=message,
            font=('Segoe UI', 10, 'bold'),
            bg='#27ae60' if success else '#e74c3c',
            fg='white',
            padx=15,
            pady=8,
            relief='raised',
            bd=0
        )

        # Position toast at bottom-right corner
        self.toast_label.place(relx=1.0, rely=1.0, anchor='se', x=-20, y=-20)

        # Auto-hide after duration
        self.toast_after_id = self.root.after(duration, self.hide_toast)

    def hide_toast(self):
        """Hide the current toast notification"""
        if self.toast_label:
            self.toast_label.destroy()
            self.toast_label = None
        self.toast_after_id = None

    def setup_keyboard_shortcuts(self):
        """Set up global keyboard shortcuts for the application"""
        # Bind shortcuts to main window (only when no modal is open)
        self.root.bind('<Control-a>', lambda e: self.handle_global_shortcut('Ctrl+A'))
        self.root.bind('<Control-s>', lambda e: self.handle_global_shortcut('Ctrl+S'))
        self.root.bind('<Control-d>', lambda e: self.handle_global_shortcut('Ctrl+D'))
        self.root.bind('<Control-q>', lambda e: self.handle_global_shortcut('Ctrl+Q'))
        self.root.bind('<Control-r>', lambda e: self.handle_global_shortcut('Ctrl+R'))

    def handle_global_shortcut(self, shortcut):
        """Handle global keyboard shortcuts"""
        # Only process if no modal is currently open
        try:
            # Check if any toplevel windows exist (modals)
            toplevels = [w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)]
            if toplevels:
                # If modals exist, don't process global shortcuts
                return
        except:
            pass

        if shortcut == 'Ctrl+A':
            # Try to focus on supplier selection or add new item
            try:
                # Check if we're on a tab that has supplier selection
                current_tab = self.notebook.index(self.notebook.select())
                if current_tab == 1:  # Sales/Purchase tab
                    self.add_sale()  # Open add sale modal
                elif current_tab == 0:  # Home tab
                    self.create_sale_entry()
                elif current_tab == 2:  # Items tab
                    self.add_item()
                elif current_tab == 3:  # Karigar Orders tab
                    self.karigar_orders_manager.show_create_order_modal()
                elif current_tab == 4:  # Karigar tab
                    self.add_freelancer()
                elif current_tab == 5:  # Suppliers tab
                    self.add_supplier()
                elif current_tab == 6:  # Raini tab
                    self.add_raini_order()
            except Exception:
                pass

        elif shortcut == 'Ctrl+S':
            # Save current form or complete current operation
            try:
                # This would need context-specific logic based on current modal
                pass
            except Exception:
                pass

        elif shortcut == 'Ctrl+D':
            # Delete selected items
            try:
                current_tab = self.notebook.index(self.notebook.select())
                if current_tab == 2:  # Items tab
                    self.delete_selected_items()
                elif current_tab == 3:  # Karigar Orders tab
                    self.delete_work_order()
                elif current_tab == 5:  # Suppliers tab
                    self.delete_selected_supplier()
                elif current_tab == 6:  # Raini tab
                    self.delete_raini_order()
            except Exception:
                pass

        elif shortcut == 'Ctrl+Q':
            # Quick actions - could be add row in forms or other quick actions
            try:
                # This would need context-specific logic
                pass
            except Exception:
                pass

        elif shortcut == 'Ctrl+R':
            # Refresh current view
            try:
                current_tab = self.notebook.index(self.notebook.select())
                if current_tab == 0:  # Home
                    self.load_home_data()
                elif current_tab == 1:  # Sales/Purchase
                    self.load_unified_data()
                elif current_tab == 2:  # Items
                    self.load_items_data()
                elif current_tab == 3:  # Karigar Orders
                    self.load_karigar_orders_data()
                elif current_tab == 4:  # Karigar
                    self.load_freelancer_data()
                elif current_tab == 5:  # Suppliers
                    self.load_supplier_data()
                elif current_tab == 6:  # Raini
                    self.load_raini_data()
            except Exception:
                pass

    def configure_styles(self):
        """Configure ttk styles for better appearance"""
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme for better custom styling
        
        # Configure notebook style
        style.configure('TNotebook', background=COLORS['light'], borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=COLORS['white'], 
                       foreground=COLORS['primary'],
                       padding=[20, 10],
                       font=FONTS['button'])
        style.map('TNotebook.Tab',
                 background=[('selected', '#000000'),
                           ('active', COLORS['secondary']),
                           ('!selected', COLORS['white'])],
                 foreground=[('selected', '#ffffff'),
                           ('active', COLORS['white']),
                           ('!selected', COLORS['primary'])])
        
        # Configure treeview style
        style.configure('Treeview', 
                       background=COLORS['white'],
                       foreground=COLORS['dark'],
                       fieldbackground=COLORS['white'],
                       font=FONTS['body'])
        style.configure('Treeview.Heading',
                       background=COLORS['white'],
                       foreground=COLORS['dark'],
                       font=FONTS['subheading'],
                       relief='flat',
                       borderwidth=1)
        
        # Configure frame style
        style.configure('TFrame', background=COLORS['light'])
        
        # Configure label style
        style.configure('TLabel', background=COLORS['light'], font=FONTS['body'])
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    @staticmethod
    def center_modal(modal_window, width, height):
        """Center a modal dialog on screen"""
        modal_window.update_idletasks()
        x = (modal_window.winfo_screenwidth() // 2) - (width // 2)
        y = (modal_window.winfo_screenheight() // 2) - (height // 2)
        modal_window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create the main interface widgets"""
        # Create header
        self.create_header()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Configure notebook style
        self.notebook.configure(style='TNotebook')
        
        # Bind tab change event to refresh home data
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        # Create tabs
        self.create_home_tab()
        self.create_inventory_tab()
        self.create_raini_inventory_tab()
        self.create_items_tab()
        self.create_work_orders_tab()
        self.create_freelancers_tab()
        self.create_suppliers_tab()
    
    def create_header(self):
        """Create application header"""
        header_frame = tk.Frame(self.root, bg=COLORS['primary'], height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, 
                              text="Gold Jewelry Business Management System",
                              font=FONTS['title'],
                              fg=COLORS['white'],
                              bg=COLORS['primary'])
        title_label.pack(expand=True)
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Manage your gold inventory, work orders, and business operations",
                                 font=FONTS['body'],
                                 fg=COLORS['light'],
                                 bg=COLORS['primary'])
        subtitle_label.pack()

        # Backup/Restore/Export quick actions on header right
        actions_frame = tk.Frame(header_frame, bg=COLORS['primary'])
        actions_frame.place(relx=1.0, rely=0.5, anchor='e')
        backup_btn = self.create_beautiful_button(actions_frame, "🗄️ Backup Now", self.backup_database_now, 'secondary', 14)
        backup_btn.pack(side='left', padx=(0, 8))
        restore_btn = self.create_beautiful_button(actions_frame, "♻️ Restore...", self.restore_database_from_file, 'warning', 14)
        restore_btn.pack(side='left', padx=(0, 8))
        export_btn = self.create_beautiful_button(actions_frame, "📤 Export CSVs", self.export_all_csvs, 'info', 14)
        export_btn.pack(side='left')
    
    def on_tab_changed(self, event):
        """Handle tab change events"""
        selected_tab = event.widget.tab('current')['text']
        if selected_tab == "🏠 Home":
            # Refresh home page data when home tab is selected
            self.load_home_data()
            # Start/refresh backup scheduler if user enabled it
            self.schedule_daily_backup_if_enabled()

    # -------------------------
    # Backup/Restore/Export handlers
    # -------------------------
    def _make_backup_dir(self):
        import os
        backup_dir = os.path.join(os.getcwd(), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def backup_database_now(self):
        try:
            import os
            from datetime import datetime
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            dest = os.path.join(self._make_backup_dir(), f'gold_jewelry_backup_{ts}.db')
            path = self.db.backup_to(dest)
            self.show_toast(f"Backup created: {os.path.basename(path)}", success=True)
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup: {e}")

    def restore_database_from_file(self):
        try:
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(title='Select backup file', filetypes=[('SQLite DB', '*.db'), ('All files', '*.*')])
            if not file_path:
                return
            if not messagebox.askyesno("Confirm Restore", "Restoring will overwrite current data. Continue?"):
                return
            self.db.restore_from(file_path)
            # Reload views
            self.load_data()
            self.show_toast("Database restored successfully", success=True)
        except Exception as e:
            messagebox.showerror("Restore Error", f"Failed to restore: {e}")

    def export_all_csvs(self):
        try:
            from tkinter import filedialog
            export_dir = filedialog.askdirectory(title='Choose export folder')
            if not export_dir:
                return
            results = self.db.export_all_to_dir(export_dir)
            if results:
                self.show_toast(f"Exported {len(results)} files to folder", success=True)
            else:
                self.show_toast("Nothing to export", success=False)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSVs: {e}")

    def on_toggle_auto_backup(self):
        self.schedule_daily_backup_if_enabled()

    def schedule_daily_backup_if_enabled(self):
        # Cancel previous
        if getattr(self, '_schedule_backup_job_id', None):
            try:
                self.root.after_cancel(self._schedule_backup_job_id)
            except Exception:
                pass
            self._schedule_backup_job_id = None

        if hasattr(self, 'auto_backup_enabled') and self.auto_backup_enabled.get():
            # Schedule next backup roughly 24 hours later
            interval_ms = 24 * 60 * 60 * 1000
            def _job():
                try:
                    self.backup_database_now()
                finally:
                    self.schedule_daily_backup_if_enabled()
            self._schedule_backup_job_id = self.root.after(interval_ms, _job)
    
    def create_home_tab(self):
        """Create home page tab with three sections"""
        home_frame = ttk.Frame(self.notebook)
        self.notebook.add(home_frame, text="🏠 Home")
        
        # Main container with three sections
        main_container = tk.Frame(home_frame, bg=COLORS['light'])
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Section 1: Create New Entry (20% width)
        entry_section = tk.Frame(main_container, bg=COLORS['white'], relief='raised', bd=2)
        entry_section.pack(side='left', fill='y', padx=(0, 10))
        entry_section.configure(width=280)  # 20% of 1400px ≈ 280px
        entry_section.pack_propagate(False)
        
        # Entry section header
        entry_header = tk.Frame(entry_section, bg=COLORS['primary'], height=50)
        entry_header.pack(fill='x')
        entry_header.pack_propagate(False)
        
        entry_title = tk.Label(entry_header, 
                              text="Create New Entry",
                              font=FONTS['heading'],
                              fg=COLORS['white'],
                              bg=COLORS['primary'])
        entry_title.pack(expand=True)
        
        # Entry buttons container
        entry_buttons_frame = tk.Frame(entry_section, bg=COLORS['white'])
        entry_buttons_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create entry buttons
        sale_btn = self.create_beautiful_button(entry_buttons_frame, "💰 Sale", self.create_sale_entry, 'success', 20, 'Ctrl+A')
        sale_btn.pack(fill='x', pady=(0, 10))
        
        purchase_btn = self.create_beautiful_button(entry_buttons_frame, "🛒 Purchase", self.create_purchase_entry, 'info', 20, 'Ctrl+A')
        purchase_btn.pack(fill='x', pady=(0, 10))
        
        new_order_btn = self.create_beautiful_button(entry_buttons_frame, "🧑‍🏭 New Karigar Order", lambda: self.karigar_orders_manager.show_create_order_modal(), 'secondary', 20, 'Ctrl+A')
        new_order_btn.pack(fill='x')

        # Scheduled backup toggle (session-based)
        schedule_frame = tk.Frame(entry_buttons_frame, bg=COLORS['white'])
        schedule_frame.pack(fill='x', pady=(10, 0))
        self.auto_backup_enabled = tk.BooleanVar(value=False)
        schedule_chk = tk.Checkbutton(schedule_frame,
                                      text="Enable Daily Backup (session)",
                                      variable=self.auto_backup_enabled,
                                      fg=COLORS['dark'], bg=COLORS['white'],
                                      activebackground=COLORS['white'], activeforeground=COLORS['dark'],
                                      command=self.on_toggle_auto_backup)
        schedule_chk.pack(anchor='w')
        
        # Section 2: Main Table (60% width)
        table_section = tk.Frame(main_container, bg=COLORS['white'], relief='raised', bd=2)
        table_section.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Table section header
        table_header = tk.Frame(table_section, bg=COLORS['secondary'], height=50)
        table_header.pack(fill='x')
        table_header.pack_propagate(False)
        
        table_title = tk.Label(table_header, 
                              text="Today's Sales & Purchase Orders",
                              font=FONTS['heading'],
                              fg=COLORS['white'],
                              bg=COLORS['secondary'])
        table_title.pack(expand=True)
        
        # Table container
        table_container = tk.Frame(table_section, bg=COLORS['white'])
        table_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Create main table for today's orders
        columns = ('Ref ID', 'Type', 'Supplier', 'Item', 'Gross (g)', 'Less (g)', 'Net (g)', 'Tunch (%)', 'Wastage (%)', 'Fine Gold (g)', 'Time')
        self.home_main_tree = ttk.Treeview(table_container, columns=columns, show='headings', style='Treeview')
        
        for col in columns:
            self.home_main_tree.heading(col, text=col)
            self.home_main_tree.column(col, width=80, anchor='center')
        
        # Configure alternating row colors
        self.home_main_tree.tag_configure('even', background=COLORS['light'])
        self.home_main_tree.tag_configure('odd', background=COLORS['white'])
        
        self.home_main_tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar for main table
        main_scrollbar = ttk.Scrollbar(table_container, orient='vertical', command=self.home_main_tree.yview)
        main_scrollbar.pack(side='right', fill='y')
        self.home_main_tree.configure(yscrollcommand=main_scrollbar.set)
        
        # Section 3: Raini Pending Orders (20% width)
        pending_section = tk.Frame(main_container, bg=COLORS['white'], relief='raised', bd=2)
        pending_section.pack(side='right', fill='y')
        pending_section.configure(width=280)  # 20% of 1400px ≈ 280px
        pending_section.pack_propagate(False)
        
        # Pending section header
        pending_header = tk.Frame(pending_section, bg=COLORS['warning'], height=50)
        pending_header.pack(fill='x')
        pending_header.pack_propagate(False)
        
        pending_title = tk.Label(pending_header, 
                                text="Raini Pending Orders",
                                font=FONTS['heading'],
                                fg=COLORS['white'],
                                bg=COLORS['warning'])
        pending_title.pack(expand=True)
        
        # Pending table container
        pending_table_container = tk.Frame(pending_section, bg=COLORS['white'])
        pending_table_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Create pending orders table
        pending_columns = ('ID', 'Weight (g)')
        self.home_pending_tree = ttk.Treeview(pending_table_container, columns=pending_columns, show='headings', style='Treeview')
        
        for col in pending_columns:
            self.home_pending_tree.heading(col, text=col)
            self.home_pending_tree.column(col, width=100, anchor='center')
        
        # Configure alternating row colors
        self.home_pending_tree.tag_configure('even', background=COLORS['light'])
        self.home_pending_tree.tag_configure('odd', background=COLORS['white'])
        
        # Bind double-click event for complete order action
        self.home_pending_tree.bind('<Double-1>', self.on_home_pending_double_click)
        
        self.home_pending_tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar for pending table
        pending_scrollbar = ttk.Scrollbar(pending_table_container, orient='vertical', command=self.home_pending_tree.yview)
        pending_scrollbar.pack(side='right', fill='y')
        self.home_pending_tree.configure(yscrollcommand=pending_scrollbar.set)
        
        # Load data for home tab
        self.load_home_data()
    
    def create_raini_inventory_tab(self):
        """Create Raini Inventory management tab"""
        raini_frame = ttk.Frame(self.notebook)
        self.notebook.add(raini_frame, text="🥇 Raini Inventory")
        
        # Buttons frame with better styling
        btn_frame = tk.Frame(raini_frame, bg=COLORS['light'])
        btn_frame.pack(fill='x', padx=15, pady=15)
        
        # Create beautiful buttons
        add_raini_btn = self.create_beautiful_button(btn_frame, "➕ New Raini Order", self.add_raini_order, 'success', 18, 'Ctrl+A')
        add_raini_btn.pack(side='left', padx=(0, 10))
        
        complete_raini_btn = self.create_beautiful_button(btn_frame, "✅ Complete Order", self.complete_raini_order, 'warning', 18, 'Ctrl+S')
        complete_raini_btn.pack(side='left', padx=(0, 10))
        
        update_raini_btn = self.create_beautiful_button(btn_frame, "✏️ Update Order", self.update_raini_order, 'info', 18, 'Ctrl+U')
        update_raini_btn.pack(side='left', padx=(0, 10))

        delete_raini_btn = self.create_beautiful_button(btn_frame, "🗑️ Delete Order", self.delete_raini_order, 'warning', 18, 'Ctrl+D')
        delete_raini_btn.pack(side='left', padx=(0, 10))
        
        # Total Raini gold display with better styling
        total_frame = tk.Frame(raini_frame, bg=COLORS['white'], relief='raised', bd=2)
        total_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        total_inner_frame = tk.Frame(total_frame, bg=COLORS['white'])
        total_inner_frame.pack(fill='x', padx=20, pady=15)
        
        # Left side - Completed Raini Gold
        left_frame = tk.Frame(total_inner_frame, bg=COLORS['white'])
        left_frame.pack(side='left', fill='x', expand=True)
        
        self.total_raini_label = tk.Label(left_frame, 
                                        text="Total Raini Gold: 0.00 grams", 
                                        font=FONTS['heading'],
                                        fg=COLORS['primary'],
                                        bg=COLORS['white'])
        self.total_raini_label.pack(anchor='w')
        
        # Right side - Pending Orders Info
        right_frame = tk.Frame(total_inner_frame, bg=COLORS['white'])
        right_frame.pack(side='right')
        
        self.pending_orders_label = tk.Label(right_frame, 
                                           text="Pending Orders: 0 (0.00g)", 
                                           font=FONTS['subheading'],
                                           fg=COLORS['warning'],
                                           bg=COLORS['white'])
        self.pending_orders_label.pack(anchor='e')
        
        # Add a gold icon
        gold_icon = tk.Label(total_inner_frame, text="🥇", font=("Arial", 20), bg=COLORS['white'])
        gold_icon.pack(side='right', padx=(10, 0))
        
        # Treeview for Raini inventory with better styling
        tree_frame = tk.Frame(raini_frame, bg=COLORS['light'])
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        columns = ('ID', 'Purity (%)', 'Pure Gold (g)', 'Impurities (g)', 'Copper (g)', 'Silver (g)', 'Expected Weight (g)', 'Actual Weight (g)', 'Created Date', 'Status')
        self.raini_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', style='Treeview')
        
        for col in columns:
            self.raini_tree.heading(col, text=col)
            self.raini_tree.column(col, width=120, anchor='center')
        
        # Configure alternating row colors
        self.raini_tree.tag_configure('even', background=COLORS['light'])
        self.raini_tree.tag_configure('odd', background=COLORS['white'])
        
        self.raini_tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.raini_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.raini_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load Raini data
        self.load_raini_data()
    
    def create_beautiful_button(self, parent, text, command, color='secondary', width=18, shortcut=None):
        """Create a beautifully styled button with optional shortcut support"""
        button = tk.Button(parent, 
                          text=text,
                          command=command,
                          bg=COLORS[color],
                          fg=COLORS['white'],
                          font=FONTS['button'],
                          relief='raised',
                          bd=2,
                          cursor='hand2',
                          width=width,
                          height=1)
        
        # Add hover effects and shortcut tooltips
        def on_enter(e):
            button.config(bg=COLORS['info'], relief='sunken')
            if shortcut:
                # Show shortcut tooltip
                try:
                    # Create tooltip label if it doesn't exist
                    if not hasattr(button, '_tooltip'):
                        button._tooltip = tk.Label(button, text=f"({shortcut})",
                                                 bg=COLORS['info'], fg='white',
                                                 font=('Arial', 8, 'bold'), padx=2, pady=1)
                    # Position tooltip above the button
                    button._tooltip.place(x=button.winfo_width()//2 - 20, y=-25, anchor='center')
                except Exception:
                    pass
        
        def on_leave(e):
            button.config(bg=COLORS[color], relief='raised')
            # Hide tooltip
            try:
                if hasattr(button, '_tooltip'):
                    button._tooltip.place_forget()
            except Exception:
                pass
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
        return button
    
    def create_items_tab(self):
        """Create items management tab"""
        items_frame = ttk.Frame(self.notebook)
        self.notebook.add(items_frame, text="📦 Items")
        
        # Items tab content
        items_content = tk.Frame(items_frame, bg=COLORS['light'])
        items_content.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header section
        header_frame = tk.Frame(items_content, bg=COLORS['white'], relief='raised', bd=2)
        header_frame.pack(fill='x', pady=(0, 15))
        
        header_inner = tk.Frame(header_frame, bg=COLORS['white'])
        header_inner.pack(fill='x', padx=20, pady=15)
        
        title_label = tk.Label(header_inner, 
                              text="Items Management", 
                              font=FONTS['heading'],
                              fg=COLORS['primary'],
                              bg=COLORS['white'])
        title_label.pack(side='left')
        
        # Delete and Add item buttons
        delete_item_btn = self.create_beautiful_button(header_inner, "🗑️ Delete Item(s)", self.delete_selected_items, 'warning', 18, 'Ctrl+D')
        delete_item_btn.pack(side='right', padx=(0, 8))
        add_item_btn = self.create_beautiful_button(header_inner, "➕ Add Item", self.add_item, 'success', 18, 'Ctrl+A')
        add_item_btn.pack(side='right')
        
        # Items table
        table_frame = tk.Frame(items_content, bg=COLORS['white'], relief='raised', bd=2)
        table_frame.pack(fill='both', expand=True)
        
        # Create treeview for items (requested columns)
        columns = ('ID', 'Item Name', 'Gross Weight (g)', 'Less (g)', 'Net Weight (g)', 'Wastage (%)')
        self.items_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Treeview')
        
        for col in columns:
            self.items_tree.heading(col, text=col)
            self.items_tree.column(col, width=120, anchor='center')
        
        # Configure alternating row colors
        self.items_tree.tag_configure('even', background=COLORS['light'])
        self.items_tree.tag_configure('odd', background=COLORS['white'])
        
        self.items_tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar for items table
        items_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.items_tree.yview)
        items_scrollbar.pack(side='right', fill='y')
        self.items_tree.configure(yscrollcommand=items_scrollbar.set)
        
        # Load items data
        self.load_items_data()
    
    def load_items_data(self):
        """Load items data from database"""
        if not hasattr(self, 'items_tree'):
            return
            
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        try:
            query = '''
                WITH 
                p AS (
                    SELECT item_id,
                           SUM(gross_weight) AS g,
                           SUM(less_weight)  AS l,
                           SUM(net_weight)   AS n,
                           SUM(wastage_percentage * net_weight) AS wsum
                    FROM sales
                    WHERE ref_id LIKE 'P%'
                    GROUP BY item_id
                ),
                s AS (
                    SELECT item_id,
                           SUM(gross_weight) AS g,
                           SUM(less_weight)  AS l,
                           SUM(net_weight)   AS n,
                           SUM(wastage_percentage * net_weight) AS wsum
                    FROM sales
                    WHERE ref_id LIKE 'S%'
                    GROUP BY item_id
                )
                SELECT 
                    i.item_id,
                    i.item_name,
                    CASE WHEN LOWER(COALESCE(i.category,'')) = 'raini'
                         THEN COALESCE(i.net_weight, 0)
                         ELSE COALESCE(p.g,0) - COALESCE(s.g,0)
                    END AS gross_weight,
                    CASE WHEN LOWER(COALESCE(i.category,'')) = 'raini'
                         THEN 0
                         ELSE COALESCE(p.l,0) - COALESCE(s.l,0)
                    END AS less_weight,
                    CASE WHEN LOWER(COALESCE(i.category,'')) = 'raini'
                         THEN COALESCE(i.net_weight, 0)
                         ELSE COALESCE(p.n,0) - COALESCE(s.n,0)
                    END AS net_weight,
                    CASE 
                        WHEN LOWER(COALESCE(i.category,'')) = 'raini' THEN 0
                        WHEN (COALESCE(p.n,0) - COALESCE(s.n,0)) <> 0 
                            THEN (COALESCE(p.wsum,0) - COALESCE(s.wsum,0)) / (COALESCE(p.n,0) - COALESCE(s.n,0))
                        ELSE 0
                    END AS wastage_percentage
                FROM items i
                LEFT JOIN p ON p.item_id = i.item_id
                LEFT JOIN s ON s.item_id = i.item_id
                ORDER BY i.item_id DESC
            '''
            rows = self.db.execute_query(query)
            
            for i, row in enumerate(rows):
                tag = 'even' if i % 2 == 0 else 'odd'
                gross = float(row[2] or 0)
                less = float(row[3] or 0)
                netw = float(row[4] or 0)
                wastage_pct = float(row[5] or 0)
                formatted_row = (
                    row[0],                 # ID
                    row[1],                 # Item Name
                    f"{gross:.3f}",        # Gross Weight (g)
                    f"{less:.3f}",         # Less (g)
                    f"{netw:.3f}",         # Net Weight (g)
                    f"{wastage_pct:.2f}"   # Wastage (%)
                )
                self.items_tree.insert('', 'end', values=formatted_row, tags=(tag,))
                
        except Exception as e:
            print(f"Error loading items data: {e}")

    def delete_selected_items(self):
        """Delete selected item records from items table"""
        try:
            if not hasattr(self, 'items_tree'):
                messagebox.showwarning("Warning", "Items table is not available")
                return
            selection = self.items_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select item(s) to delete")
                return
            # Collect selected item_ids
            item_ids = []
            for sel in selection:
                vals = self.items_tree.item(sel).get('values') or []
                if vals:
                    item_ids.append(vals[0])
            if not item_ids:
                return
            # Confirm
            if not messagebox.askyesno("Confirm Delete", f"Delete {len(item_ids)} item(s)? This cannot be undone."):
                return
            # Delete from DB
            placeholders = ','.join(['?'] * len(item_ids))
            self.db.execute_update(f"DELETE FROM items WHERE item_id IN ({placeholders})", tuple(item_ids))
            # Refresh table
            self.load_items_data()
            self.show_toast("Selected item(s) deleted", success=True)
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting item(s): {e}")
    
    def update_item_inventory(self, item_id, fine_weight_change, net_weight_change, operation='add'):
        """Update item inventory based on purchase or sale operations"""
        try:
            if operation == 'add':
                # For purchases - add to inventory
                query = '''
                    UPDATE items 
                    SET fine_weight = COALESCE(fine_weight, 0) + ?,
                        net_weight = COALESCE(net_weight, 0) + ?
                    WHERE item_id = ?
                '''
            else:
                # For sales - subtract from inventory
                query = '''
                    UPDATE items 
                    SET fine_weight = COALESCE(fine_weight, 0) - ?,
                        net_weight = COALESCE(net_weight, 0) - ?
                    WHERE item_id = ?
                '''
            
            self.db.execute_update(query, (fine_weight_change, net_weight_change, item_id))
            print(f"Updated inventory for item {item_id}: {operation} {fine_weight_change}g fine, {net_weight_change}g net")
            
            # Refresh items data display
            self.load_items_data()
            
        except Exception as e:
            print(f"Error updating item inventory: {e}")
    
    def update_item_inventory_for_record_update(self, ref_id, old_fine_gold, old_net_weight, new_fine_gold, new_net_weight, old_item_id, new_item_id, is_purchase=False):
        """Update item inventory when a record is updated"""
        try:
            # First, reverse the old inventory change
            if is_purchase:
                # Reverse old purchase (subtract old values)
                self.update_item_inventory(old_item_id, old_fine_gold, old_net_weight, 'subtract')
            else:
                # Reverse old sale (add back old values)
                self.update_item_inventory(old_item_id, old_fine_gold, old_net_weight, 'add')
            
            # Then apply the new inventory change
            if is_purchase:
                # Apply new purchase (add new values)
                self.update_item_inventory(new_item_id, new_fine_gold, new_net_weight, 'add')
            else:
                # Apply new sale (subtract new values)
                self.update_item_inventory(new_item_id, new_fine_gold, new_net_weight, 'subtract')
                
        except Exception as e:
            print(f"Error updating item inventory for record update: {e}")
    
    def update_supplier_balance(self, supplier_name, amount_change, operation='add'):
        """Update supplier balance (in fine gold grams) based on operations.
        Convention:
        - For Purchase (we receive gold): subtract grams from supplier's owed balance
        - For Sale (we give out gold): add grams to supplier's owed balance
        """
        try:
            if operation == 'add':
                # For sales - add grams owed to supplier
                query = '''
                    UPDATE suppliers 
                    SET balance = COALESCE(balance, 0) + ?
                    WHERE supplier_name = ?
                '''
            else:
                # For purchases - subtract grams owed to supplier
                query = '''
                    UPDATE suppliers 
                    SET balance = COALESCE(balance, 0) - ?
                    WHERE supplier_name = ?
                '''
            
            self.db.execute_update(query, (amount_change, supplier_name))
            print(f"Updated balance for supplier {supplier_name}: {operation} {amount_change}")
            
        except Exception as e:
            print(f"Error updating supplier balance: {e}")
    
    def update_supplier_balance_for_record_update(self, supplier_name, old_amount, new_amount, old_supplier_name, new_supplier_name, is_purchase=False):
        """Update supplier balance when a record is updated"""
        try:
            # First, reverse the old balance change
            if is_purchase:
                # Reverse old purchase (add back old amount)
                self.update_supplier_balance(old_supplier_name, old_amount, 'add')
            else:
                # Reverse old sale (subtract back old amount)
                self.update_supplier_balance(old_supplier_name, old_amount, 'subtract')
            
            # Then apply the new balance change
            if is_purchase:
                # Apply new purchase (subtract new amount)
                self.update_supplier_balance(new_supplier_name, new_amount, 'subtract')
            else:
                # Apply new sale (add new amount)
                self.update_supplier_balance(new_supplier_name, new_amount, 'add')
                
        except Exception as e:
            print(f"Error updating supplier balance for record update: {e}")
    
    def get_supplier_balance(self, supplier_name):
        """Get current balance for a supplier"""
        try:
            query = "SELECT COALESCE(balance, 0) FROM suppliers WHERE supplier_name = ?"
            result = self.db.execute_query(query, (supplier_name,))
            if result:
                return result[0][0]
            return 0.0
        except Exception as e:
            print(f"Error getting supplier balance: {e}")
            return 0.0
    
    def get_gold_price_per_gram(self):
        """Get current gold price per gram from settings"""
        try:
            query = "SELECT setting_value FROM settings WHERE setting_key = 'gold_price_per_gram'"
            result = self.db.execute_query(query)
            if result:
                return float(result[0][0])
            return 5000.0  # Default price if not set
        except Exception as e:
            print(f"Error getting gold price: {e}")
            return 5000.0  # Default price on error
    
    def calculate_monetary_value(self, fine_gold_weight):
        """Deprecated: Monetary value no longer used for supplier balance updates."""
        price_per_gram = self.get_gold_price_per_gram()
        return fine_gold_weight * price_per_gram
    
    def delete_selected_sales(self):
        """Delete selected sales records"""
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select sales records to delete")
            return
        
        # Get details of selected records
        records_to_delete = []
        for item in selection:
            values = self.sales_tree.item(item)['values']
            ref_id = values[0]
            records_to_delete.append(ref_id)
        
        # Show confirmation dialog
        if len(records_to_delete) == 1:
            message = f"Are you sure you want to delete sales record {records_to_delete[0]}?\n\nThis will also adjust the item inventory."
        else:
            message = f"Are you sure you want to delete {len(records_to_delete)} sales records?\n\nThis will also adjust the item inventory for all affected items."
        
        if messagebox.askyesno("Confirm Delete", message):
            self.delete_sales_records(records_to_delete)
    
    def delete_selected_purchases(self):
        """Delete selected purchase records"""
        selection = self.purchases_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select purchase records to delete")
            return
        
        # Get details of selected records
        records_to_delete = []
        for item in selection:
            values = self.purchases_tree.item(item)['values']
            ref_id = values[0]
            records_to_delete.append(ref_id)
        
        # Show confirmation dialog
        if len(records_to_delete) == 1:
            message = f"Are you sure you want to delete purchase record {records_to_delete[0]}?\n\nThis will also adjust the item inventory."
        else:
            message = f"Are you sure you want to delete {len(records_to_delete)} purchase records?\n\nThis will also adjust the item inventory for all affected items."
        
        if messagebox.askyesno("Confirm Delete", message):
            self.delete_purchase_records(records_to_delete)
    
    def delete_sales_records(self, ref_ids):
        """Delete sales records and adjust inventory"""
        try:
            deleted_count = 0
            for ref_id in ref_ids:
                # Get record details before deletion
                query = "SELECT item_id, fine_gold, net_weight, supplier_name FROM sales WHERE ref_id = ?"
                record_data = self.db.execute_query(query, (ref_id,))
                
                if record_data:
                    item_id, fine_gold, net_weight, supplier_name = record_data[0]
                    
                    # Delete the record
                    delete_query = "DELETE FROM sales WHERE ref_id = ?"
                    self.db.execute_update(delete_query, (ref_id,))
                    
                    # Adjust inventory (add back the weights since it was a sale)
                    self.update_item_inventory(item_id, fine_gold, net_weight, 'add')
                    
                    # Adjust supplier balance in grams (reverse sale)
                    self.update_supplier_balance(supplier_name, fine_gold, 'subtract')
                    
                    deleted_count += 1
                    print(f"Deleted sales record {ref_id} and adjusted inventory and supplier balance")
            
            if deleted_count > 0:
                self.show_toast(f"Successfully deleted {deleted_count} sales record(s)", success=True)
                self.load_unified_data()  # Refresh the unified table
            else:
                messagebox.showerror("Error", "No records were deleted")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting sales records: {e}")
    
    def delete_purchase_records(self, ref_ids):
        """Delete purchase records and adjust inventory"""
        try:
            deleted_count = 0
            for ref_id in ref_ids:
                # Get record details before deletion
                query = "SELECT item_id, fine_gold, net_weight, supplier_name FROM sales WHERE ref_id = ?"
                record_data = self.db.execute_query(query, (ref_id,))
                
                if record_data:
                    item_id, fine_gold, net_weight, supplier_name = record_data[0]
                    
                    # Delete the record
                    delete_query = "DELETE FROM sales WHERE ref_id = ?"
                    self.db.execute_update(delete_query, (ref_id,))
                    
                    # Adjust inventory (subtract the weights since it was a purchase)
                    self.update_item_inventory(item_id, fine_gold, net_weight, 'subtract')
                    
                    # Adjust supplier balance in grams (reverse purchase)
                    self.update_supplier_balance(supplier_name, fine_gold, 'add')
                    
                    deleted_count += 1
                    print(f"Deleted purchase record {ref_id} and adjusted inventory and supplier balance")
            
            if deleted_count > 0:
                self.show_toast(f"Successfully deleted {deleted_count} purchase record(s)", success=True)
                self.load_unified_data()  # Refresh the unified table
            else:
                messagebox.showerror("Error", "No records were deleted")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting purchase records: {e}")
    
    def delete_selected_unified_records(self):
        """Delete selected unified records (sales or purchases)"""
        selection = self.unified_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select records to delete")
            return
        
        # Get details of selected records (only parent items)
        records_to_delete = []
        for item in selection:
            values = self.unified_tree.item(item)['values']
            # Only process parent items (those with Ref ID)
            if values[1]:  # Ref ID exists
                record_type = values[0]  # Type (Sale or Purchase)
                ref_id = values[1]  # Ref ID for the transaction group
                records_to_delete.append((record_type, ref_id))
            else:
                # For child items, get the parent's data
                parent = self.unified_tree.parent(item)
                if parent:
                    parent_values = self.unified_tree.item(parent)['values']
                    record_type = parent_values[0]  # Type (Sale or Purchase)
                    ref_id = parent_values[1]  # Ref ID for the transaction group
                    # Avoid duplicates
                    if (record_type, ref_id) not in records_to_delete:
                        records_to_delete.append((record_type, ref_id))
        
        if not records_to_delete:
            messagebox.showwarning("Warning", "Please select valid records to delete")
            return
        
        # Show confirmation dialog
        if len(records_to_delete) == 1:
            record_type, ref_id = records_to_delete[0]
            message = f"Are you sure you want to delete {record_type.lower()} transaction {ref_id}?\n\nThis will delete all entries in this transaction and adjust the item inventory."
        else:
            message = f"Are you sure you want to delete {len(records_to_delete)} transactions?\n\nThis will delete all entries in these transactions and adjust the item inventory for all affected items."
        
        if messagebox.askyesno("Confirm Delete", message):
            self.delete_unified_records(records_to_delete)
    
    def delete_unified_records(self, records):
        """Delete unified records and adjust inventory"""
        try:
            deleted_count = 0
            for record_type, ref_id in records:
                # Get all record details before deletion
                query = "SELECT item_id, fine_gold, net_weight, supplier_name FROM sales WHERE ref_id = ?"
                all_records = self.db.execute_query(query, (ref_id,))
                
                if all_records:
                    # Delete all records with this Ref ID
                    delete_query = "DELETE FROM sales WHERE ref_id = ?"
                    self.db.execute_update(delete_query, (ref_id,))
                    
                    # Adjust inventory for all deleted records
                    for record_data in all_records:
                        item_id, fine_gold, net_weight, supplier_name = record_data
                        
                        if record_type == 'Sale':
                            # Adjust inventory (add back the weights since it was a sale)
                            self.update_item_inventory(item_id, fine_gold, net_weight, 'add')
                            # Adjust supplier balance in grams (reverse sale)
                            self.update_supplier_balance(supplier_name, fine_gold, 'subtract')
                        else:  # Purchase
                            # Adjust inventory (subtract the weights since it was a purchase)
                            self.update_item_inventory(item_id, fine_gold, net_weight, 'subtract')
                            # Adjust supplier balance in grams (reverse purchase)
                            self.update_supplier_balance(supplier_name, fine_gold, 'add')
                    
                    deleted_count += len(all_records)
                    print(f"Deleted {record_type.lower()} record {ref_id} and adjusted inventory and supplier balance")
            
            if deleted_count > 0:
                self.show_toast(f"Successfully deleted {deleted_count} record(s)", success=True)
                self.load_unified_data()  # Refresh the unified table
            else:
                messagebox.showerror("Error", "No records were deleted")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting records: {e}")
    
    def show_unified_context_menu(self, event):
        """Show context menu for unified records"""
        # Select the item under the cursor
        item = self.unified_tree.identify_row(event.y)
        if item:
            self.unified_tree.selection_set(item)
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Update Record", command=self.on_unified_record_double_click)
            context_menu.add_separator()
            context_menu.add_command(label="Delete Record", command=self.delete_selected_unified_records)
            
            # Show context menu
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def show_sales_context_menu(self, event):
        """Show context menu for sales records"""
        # Select the item under the cursor
        item = self.sales_tree.identify_row(event.y)
        if item:
            self.sales_tree.selection_set(item)
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Edit Record", command=self.edit_selected_sales)
            context_menu.add_command(label="Delete Record(s)", command=self.delete_selected_sales)
            context_menu.add_separator()
            context_menu.add_command(label="Refresh", command=self.load_sales_data)
            
            # Show the context menu
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def show_purchases_context_menu(self, event):
        """Show context menu for purchase records"""
        # Select the item under the cursor
        item = self.purchases_tree.identify_row(event.y)
        if item:
            self.purchases_tree.selection_set(item)
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Edit Record", command=self.edit_selected_purchases)
            context_menu.add_command(label="Delete Record(s)", command=self.delete_selected_purchases)
            context_menu.add_separator()
            context_menu.add_command(label="Refresh", command=self.load_purchases_data)
            
            # Show the context menu
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def edit_selected_sales(self):
        """Edit selected sales record"""
        selection = self.sales_tree.selection()
        if selection:
            item = self.sales_tree.item(selection[0])
            values = item['values']
            ref_id = values[0]
            self.open_update_sales_modal(ref_id, None)
        else:
            messagebox.showwarning("Warning", "Please select a sales record to edit")
    
    def edit_selected_purchases(self):
        """Edit selected purchase record"""
        selection = self.purchases_tree.selection()
        if selection:
            item = self.purchases_tree.item(selection[0])
            values = item['values']
            ref_id = values[0]
            self.open_update_purchase_modal(ref_id, None)
        else:
            messagebox.showwarning("Warning", "Please select a purchase record to edit")
    
    def add_item(self):
        """Show modal for adding new item"""
        modal = tk.Toplevel(self.root)
        modal.title("Add New Item")
        modal.geometry("600x500")
        modal.resizable(False, False)
        modal.transient(self.root)
        modal.grab_set()
        
        # Center the modal
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (600 // 2)
        y = (modal.winfo_screenheight() // 2) - (500 // 2)
        modal.geometry(f"600x500+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(modal, bg=COLORS['light'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="Add New Item",
                              font=FONTS['heading'],
                              fg=COLORS['primary'],
                              bg=COLORS['light'])
        title_label.pack(pady=(0, 20))
        
        # Item Name
        name_frame = tk.Frame(main_frame, bg=COLORS['light'])
        name_frame.pack(fill='x', pady=(0, 15))
        
        name_label = tk.Label(name_frame, 
                             text="Item Name:",
                             font=FONTS['body'],
                             fg=COLORS['dark'],
                             bg=COLORS['light'])
        name_label.pack(anchor='w')
        
        name_entry = tk.Entry(name_frame, 
                             font=FONTS['body'],
                             width=40)
        name_entry.pack(fill='x', pady=(5, 0))
        
        # (Item Code removed)
        
        # Category
        category_frame = tk.Frame(main_frame, bg=COLORS['light'])
        category_frame.pack(fill='x', pady=(0, 15))
        
        category_label = tk.Label(category_frame, 
                                 text="Category:",
                                 font=FONTS['body'],
                                 fg=COLORS['dark'],
                                 bg=COLORS['light'])
        category_label.pack(anchor='w')
        
        category_entry = tk.Entry(category_frame, 
                                 font=FONTS['body'],
                                 width=40)
        category_entry.pack(fill='x', pady=(5, 0))
        
        # Description
        desc_frame = tk.Frame(main_frame, bg=COLORS['light'])
        desc_frame.pack(fill='x', pady=(0, 20))
        
        desc_label = tk.Label(desc_frame, 
                             text="Description:",
                             font=FONTS['body'],
                             fg=COLORS['dark'],
                             bg=COLORS['light'])
        desc_label.pack(anchor='w')
        
        desc_text = tk.Text(desc_frame, 
                           font=FONTS['body'],
                           width=40,
                           height=4)
        desc_text.pack(fill='x', pady=(5, 0))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=COLORS['light'])
        button_frame.pack(fill='x', pady=(20, 0))
        
        def save_item():
            name = name_entry.get().strip()
            category = category_entry.get().strip()
            description = desc_text.get('1.0', tk.END).strip()
            
            if not name:
                messagebox.showerror("Error", "Item name is required")
                return
            
            try:
                query = '''
                    INSERT INTO items (item_name, category, description)
                    VALUES (?, ?, ?)
                '''
                self.db.execute_update(query, (name, category, description))
                self.show_toast("Item added successfully!", success=True)
                self.load_items_data()
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error adding item: {e}")
        
        save_btn = tk.Button(button_frame, 
                            text="💾 Save Item",
                            command=save_item,
                            font=('Arial', 12, 'bold'),
                            bg=COLORS['success'],
                            fg=COLORS['white'],
                            relief='raised',
                            bd=3,
                            padx=20,
                            pady=8)
        save_btn.pack(side='right', padx=(10, 0))
        
        cancel_btn = tk.Button(button_frame, 
                              text="❌ Cancel",
                              command=modal.destroy,
                              font=('Arial', 12, 'bold'),
                              bg=COLORS['secondary'],
                              fg=COLORS['white'],
                              relief='raised',
                              bd=3,
                              padx=20,
                              pady=8)
        cancel_btn.pack(side='right')
    
    def add_sale(self):
        """Show multiple sales modal directly"""
        self.add_multiple_sales()
    
    def add_multiple_sales(self):
        """Show multiple sales modal using the dedicated manager class"""
        self.multiple_sales_manager.show_multiple_sales_modal()
    
    def edit_sales_transaction_group(self, ref_id):
        """Edit a sales transaction group using the multiple sales screen"""
        self.multiple_sales_manager.show_multiple_sales_modal_for_edit(ref_id)
    
    def validate_number_input(self, char, action, index, value_after, value_before, **kwargs):
        """Validate that only numbers and decimal point are entered"""
        # Allow special keys (backspace, delete, arrow keys, etc.)
        if action == '0':  # Deletion
            return True
        if action == '1':  # Insertion
            # Allow digits and decimal point
            if char.isdigit() or char == '.':
                # Prevent multiple decimal points
                if char == '.' and '.' in value_before:
                    return False
                return True
            return False
        return True
    
    def add_number_validation(self, entry_widget):
        """Add number validation to an entry widget"""
        entry_widget.config(validate='all', validatecommand=(entry_widget.register(self.validate_number_input), '%S', '%d', '%i', '%P', '%s'))
    
    def populate_entry_field(self, entry_widget, value):
        """Properly populate an entry field by clearing it first"""
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, str(value))
    
    def generate_ref_id(self, prefix):
        """Generate reference ID with format: S/P + DDMMYY + / + 3-digit incremental"""
        from datetime import datetime
        
        # Get current date in DDMMYY format
        today = datetime.now()
        date_str = today.strftime('%d%m%y')
        
        # Get next incremental number for today
        try:
            # Get the highest existing number for today
            query = f"SELECT ref_id FROM sales WHERE ref_id LIKE '{prefix}{date_str}/%' ORDER BY ref_id DESC LIMIT 1"
            result = self.db.execute_query(query)
            
            if result and result[0][0]:
                # Extract the number from the highest existing ref_id
                existing_ref = result[0][0]
                existing_num = int(existing_ref.split('/')[-1])
                next_num = existing_num + 1
            else:
                next_num = 1
                
            # Format as 3-digit number
            ref_id = f"{prefix}{date_str}/{next_num:03d}"
            
            # Double-check that this Ref ID doesn't already exist
            check_query = "SELECT COUNT(*) FROM sales WHERE ref_id = ?"
            check_result = self.db.execute_query(check_query, (ref_id,))
            if check_result and check_result[0][0] > 0:
                print(f"WARNING: Ref ID {ref_id} already exists! Incrementing...")
                next_num += 1
                ref_id = f"{prefix}{date_str}/{next_num:03d}"
            
            return ref_id
        except Exception as e:
            print(f"Error generating ref ID: {e}")
            return f"{prefix}{date_str}/001"
    
    def create_inventory_tab(self):
        """Create inventory management tab"""
        inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(inventory_frame, text="🏆 Sales/Purchase Order")
        
        # Buttons frame with better styling
        btn_frame = tk.Frame(inventory_frame, bg=COLORS['light'])
        btn_frame.pack(fill='x', padx=15, pady=15)
        
        # Create beautiful buttons
        add_purchase_btn = self.create_beautiful_button(btn_frame, "🛒 Add Purchase", self.add_purchase, 'info', 18, 'Ctrl+A')
        add_purchase_btn.pack(side='left', padx=(0, 10))
        
        add_sale_btn = self.create_beautiful_button(btn_frame, "💰 Add Sale", self.add_sale, 'success', 18, 'Ctrl+A')
        add_sale_btn.pack(side='left', padx=(0, 10))
        
        # Delete button for unified records
        delete_record_btn = self.create_beautiful_button(btn_frame, "🗑️ Delete Record", self.delete_selected_unified_records, 'danger', 18, 'Ctrl+D')
        delete_record_btn.pack(side='right', padx=(10, 0))
        
        # Unified Sales/Purchase Records table
        unified_section = tk.Frame(inventory_frame, bg=COLORS['white'], relief='raised', bd=2)
        unified_section.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Unified section header
        unified_header = tk.Frame(unified_section, bg=COLORS['info'], height=40)
        unified_header.pack(fill='x')
        unified_header.pack_propagate(False)
        
        unified_title = tk.Label(unified_header, 
                              text="Sales/Purchase Records",
                              font=FONTS['subheading'],
                              fg=COLORS['white'],
                              bg=COLORS['info'])
        unified_title.pack(expand=True)

        # Filter controls section
        filter_frame = tk.Frame(unified_section, bg=COLORS['light'], height=50)
        filter_frame.pack(fill='x', pady=(0, 10))
        filter_frame.pack_propagate(False)

        # Filter label
        filter_label = tk.Label(filter_frame,
                               text="Filters:",
                               font=FONTS['body'],
                               fg=COLORS['dark'],
                               bg=COLORS['light'])
        filter_label.pack(side='left', padx=(10, 10))

        # Supplier filter
        supplier_filter_frame = tk.Frame(filter_frame, bg=COLORS['light'])
        supplier_filter_frame.pack(side='left', padx=(0, 15))

        tk.Label(supplier_filter_frame, text="Supplier:", font=FONTS['body'], bg=COLORS['light']).pack(side='left')
        self.supplier_filter_var = tk.StringVar()
        supplier_filter_combo = ttk.Combobox(supplier_filter_frame,
                                          textvariable=self.supplier_filter_var,
                                          font=FONTS['body'],
                                          width=20,
                                          state='readonly')
        supplier_filter_combo.pack(side='left', padx=(5, 0))

        # Load supplier options for filter
        try:
            suppliers = self.db.execute_query("SELECT supplier_name FROM suppliers WHERE is_active = 1 ORDER BY supplier_name")
            supplier_options = ['All'] + [row[0] for row in suppliers]
            supplier_filter_combo['values'] = supplier_options
            supplier_filter_combo.set('All')
        except Exception:
            supplier_options = ['All']
            supplier_filter_combo['values'] = supplier_options
            supplier_filter_combo.set('All')

        # Date range filters with calendar picker
        date_filter_frame = tk.Frame(filter_frame, bg=COLORS['light'])
        date_filter_frame.pack(side='left')

        # From date picker
        from_date_frame = tk.Frame(date_filter_frame, bg=COLORS['light'])
        from_date_frame.pack(side='left')

        tk.Label(from_date_frame, text="From:", font=FONTS['body'], bg=COLORS['light']).pack(side='left')
        self.from_date_var = tk.StringVar()
        from_date_entry = tk.Entry(from_date_frame,
                                  textvariable=self.from_date_var,
                                  font=FONTS['body'],
                                  width=12,
                                  relief='solid',
                                  bd=1)
        from_date_entry.pack(side='left', padx=(5, 5))
        from_date_entry.insert(0, "YYYY-MM-DD")  # Placeholder text

        # Clear placeholder when user starts typing
        def clear_placeholder_from(event):
            if from_date_entry.get() == "YYYY-MM-DD":
                from_date_entry.delete(0, tk.END)
        from_date_entry.bind('<FocusIn>', clear_placeholder_from)

        # Calendar button for From date
        from_cal_btn = tk.Button(from_date_frame,
                                text="📅",
                                command=lambda: self.show_date_picker(self.from_date_var, from_date_entry),
                                font=FONTS['body'],
                                bg=COLORS['info'],
                                fg='white',
                                relief='raised',
                                bd=1,
                                width=3,
                                cursor='hand2')
        from_cal_btn.pack(side='left')

        # To date picker
        to_date_frame = tk.Frame(date_filter_frame, bg=COLORS['light'])
        to_date_frame.pack(side='left', padx=(15, 0))

        tk.Label(to_date_frame, text="To:", font=FONTS['body'], bg=COLORS['light']).pack(side='left')
        self.to_date_var = tk.StringVar()
        to_date_entry = tk.Entry(to_date_frame,
                                textvariable=self.to_date_var,
                                font=FONTS['body'],
                                width=12,
                                relief='solid',
                                bd=1)
        to_date_entry.pack(side='left', padx=(5, 5))
        to_date_entry.insert(0, "YYYY-MM-DD")  # Placeholder text

        # Clear placeholder when user starts typing
        def clear_placeholder_to(event):
            if to_date_entry.get() == "YYYY-MM-DD":
                to_date_entry.delete(0, tk.END)
        to_date_entry.bind('<FocusIn>', clear_placeholder_to)

        # Calendar button for To date
        to_cal_btn = tk.Button(to_date_frame,
                              text="📅",
                              command=lambda: self.show_date_picker(self.to_date_var, to_date_entry),
                              font=FONTS['body'],
                              bg=COLORS['info'],
                              fg='white',
                              relief='raised',
                              bd=1,
                              width=3,
                              cursor='hand2')
        to_cal_btn.pack(side='left')

        # Filter buttons
        filter_btns_frame = tk.Frame(filter_frame, bg=COLORS['light'])
        filter_btns_frame.pack(side='right', padx=(10, 10))

        apply_filter_btn = self.create_beautiful_button(filter_btns_frame, "🔍 Apply Filter", self.apply_unified_filters, 'info', 14)
        apply_filter_btn.pack(side='left', padx=(0, 5))

        clear_filter_btn = self.create_beautiful_button(filter_btns_frame, "❌ Clear", self.clear_unified_filters, 'secondary', 14)
        clear_filter_btn.pack(side='left')

        # Unified table container
        unified_table_frame = tk.Frame(unified_section, bg=COLORS['light'])
        unified_table_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Create treeview for unified sales/purchases with Type column (including hidden sale_id)
        unified_columns = ('Type', 'Ref ID', 'Supplier', 'Item', 'Gross (g)', 'Less (g)', 'Net (g)', 'Tunch (%)', 'Wastage (%)', 'Fine Gold (g)', 'Date', 'Sale ID')
        self.unified_tree = ttk.Treeview(unified_table_frame, columns=unified_columns, show='tree headings', style='Treeview')
        
        for col in unified_columns:
            self.unified_tree.heading(col, text=col)
            if col == 'Type':
                self.unified_tree.column(col, width=80, anchor='center')
            elif col == 'Sale ID':
                self.unified_tree.column(col, width=0, minwidth=0)  # Hide the column
            else:
                self.unified_tree.column(col, width=100, anchor='center')
        
        # Configure alternating row colors
        self.unified_tree.tag_configure('even', background=COLORS['light'])
        self.unified_tree.tag_configure('odd', background=COLORS['white'])
        self.unified_tree.tag_configure('sale', background='#e8f5e8')  # Light green for sales
        self.unified_tree.tag_configure('purchase', background='#e8f0ff')  # Light blue for purchases
        
        # Configure selection
        self.unified_tree.configure(selectmode='extended')  # Multiple row selection
        
        self.unified_tree.pack(side='left', fill='both', expand=True)
        
        # Initialize selected record variable
        self.selected_unified_record = None
        
        # Scrollbar for unified table
        unified_scrollbar = ttk.Scrollbar(unified_table_frame, orient='vertical', command=self.unified_tree.yview)
        unified_scrollbar.pack(side='right', fill='y')
        self.unified_tree.configure(yscrollcommand=unified_scrollbar.set)
        
        # Bind selection and double-click events
        self.unified_tree.bind('<<TreeviewSelect>>', self.on_unified_record_select)
        self.unified_tree.bind('<Double-1>', self.on_unified_record_double_click)
        self.unified_tree.bind('<Button-1>', self.on_unified_tree_click)
        
        # Bind delete key for unified records
        self.unified_tree.bind('<Delete>', lambda e: self.delete_selected_unified_records())
        self.unified_tree.bind('<BackSpace>', lambda e: self.delete_selected_unified_records())
        
        # Bind right-click context menu for unified records
        self.unified_tree.bind('<Button-3>', self.show_unified_context_menu)
        
        # Load unified data
        self.load_unified_data()
    
    def on_unified_tree_click(self, event):
        """Handle tree click for expand/collapse functionality"""
        # Get the item that was clicked
        item = self.unified_tree.identify('item', event.x, event.y)
        if not item:
            return
        
        # Check if the click was on the text column (expand/collapse area)
        region = self.unified_tree.identify('region', event.x, event.y)
        if region == 'text':
            # Get the item text to check if it's a parent item
            item_text = self.unified_tree.item(item, 'text')
            if item_text.startswith('▶') or item_text.startswith('▼'):
                # Toggle the item's open/closed state
                is_open = self.unified_tree.item(item, 'open')
                self.unified_tree.item(item, open=not is_open)
                
                # Update the icon
                if not is_open:
                    # Item is now open, change to ▼
                    new_text = item_text.replace('▶', '▼', 1)
                else:
                    # Item is now closed, change to ▶
                    new_text = item_text.replace('▼', '▶', 1)
                
                self.unified_tree.item(item, text=new_text)
    
    def on_unified_record_select(self, event):
        """Handle unified record selection"""
        selection = self.unified_tree.selection()
        if selection:
            item = self.unified_tree.item(selection[0])
            values = item['values']
            # Check if this is a parent item (has Ref ID) or child item
            if values[1]:  # Ref ID exists for parent items
                self.selected_unified_record = values[1]  # Ref ID
                # Auto-expand parent items when selected to show all child records
                item_text = self.unified_tree.item(selection[0], 'text')
                if item_text.startswith('▶'):
                    # Item is collapsed, expand it
                    self.unified_tree.item(selection[0], open=True)
                    # Update the icon
                    new_text = item_text.replace('▶', '▼', 1)
                    self.unified_tree.item(selection[0], text=new_text)
            else:
                # For child items, get the parent's Ref ID
                parent = self.unified_tree.parent(selection[0])
                if parent:
                    parent_values = self.unified_tree.item(parent)['values']
                    self.selected_unified_record = parent_values[1]  # Parent's Ref ID
                else:
                    self.selected_unified_record = None
        else:
            self.selected_unified_record = None
    
    def on_unified_record_double_click(self, event):
        """Handle unified record double-click to open multiple sales screen for editing"""
        selection = self.unified_tree.selection()
        if selection:
            item = self.unified_tree.item(selection[0])
            values = item['values']
            # Check if this is a parent item or child item
            if values[1]:  # Ref ID exists for parent items
                record_type = values[0]  # Type (Sale or Purchase)
                ref_id = values[1]  # Ref ID for the transaction group
            else:
                # For child items, get the parent's data
                parent = self.unified_tree.parent(selection[0])
                if parent:
                    parent_values = self.unified_tree.item(parent)['values']
                    record_type = parent_values[0]  # Type (Sale or Purchase)
                    ref_id = parent_values[1]  # Ref ID for the transaction group
                else:
                    messagebox.showwarning("Warning", "Please select a valid record to update")
                    return
            if record_type == 'Sale':
                # Open multiple sales screen for editing this transaction group
                self.edit_sales_transaction_group(ref_id)
            else:  # Purchase
                # Open multiple purchases screen for editing this transaction group
                try:
                    self.multiple_purchases_manager.show_multiple_purchases_modal_for_edit(ref_id)
                except Exception as e:
                    messagebox.showerror("Error", f"Error opening purchase editor: {e}")
        else:
            messagebox.showwarning("Warning", "Please select a record to update")
    
    def load_unified_data(self, supplier_filter=None, from_date=None, to_date=None):
        """Load both sales and purchases data into unified table with merged Ref IDs and optional filtering"""
        if not hasattr(self, 'unified_tree'):
            return
            
        # Clear existing items
        for item in self.unified_tree.get_children():
            self.unified_tree.delete(item)
        
        try:
            # Build WHERE clause for filters
            where_conditions = ["s.ref_id LIKE 'S%'"]
            query_params = []

            if supplier_filter and supplier_filter != 'All':
                where_conditions.append("s.supplier_name = ?")
                query_params.append(supplier_filter)

            if from_date:
                where_conditions.append("DATE(s.sale_date) >= ?")
                query_params.append(from_date)

            if to_date:
                where_conditions.append("DATE(s.sale_date) <= ?")
                query_params.append(to_date)

            where_clause = " AND ".join(where_conditions)

            # Load sales data with filters
            sales_query = f'''
                SELECT
                    'Sale' as type,
                    s.ref_id,
                    s.supplier_name,
                    i.item_name,
                    s.gross_weight,
                    s.less_weight,
                    s.net_weight,
                    s.tunch_percentage,
                    s.wastage_percentage,
                    s.fine_gold,
                    s.sale_date,
                    s.sale_id
                FROM sales s
                LEFT JOIN items i ON s.item_id = i.item_id
                WHERE {where_clause}
                ORDER BY s.ref_id DESC, s.sale_date DESC
            '''
            sales_rows = self.db.execute_query(sales_query, tuple(query_params)) if query_params else self.db.execute_query(sales_query)
            
            # Load purchases data with filters (reuse same filter logic)
            purchases_where_conditions = ["s.ref_id LIKE 'P%'"]
            purchases_query_params = []

            if supplier_filter and supplier_filter != 'All':
                purchases_where_conditions.append("s.supplier_name = ?")
                purchases_query_params.append(supplier_filter)

            if from_date:
                purchases_where_conditions.append("DATE(s.sale_date) >= ?")
                purchases_query_params.append(from_date)

            if to_date:
                purchases_where_conditions.append("DATE(s.sale_date) <= ?")
                purchases_query_params.append(to_date)

            purchases_where_clause = " AND ".join(purchases_where_conditions)

            purchases_query = f'''
                SELECT
                    'Purchase' as type,
                    s.ref_id,
                    s.supplier_name,
                    i.item_name,
                    s.gross_weight,
                    s.less_weight,
                    s.net_weight,
                    s.tunch_percentage,
                    s.wastage_percentage,
                    s.fine_gold,
                    s.sale_date,
                    s.sale_id
                FROM sales s
                LEFT JOIN items i ON s.item_id = i.item_id
                WHERE {purchases_where_clause}
                ORDER BY s.ref_id DESC, s.sale_date DESC
            '''
            purchases_rows = self.db.execute_query(purchases_query, tuple(purchases_query_params)) if purchases_query_params else self.db.execute_query(purchases_query)
            
            # Combine all records
            all_records = []
            if sales_rows:
                all_records.extend(sales_rows)
            if purchases_rows:
                all_records.extend(purchases_rows)
            
            # Group records by Ref ID to merge entries
            grouped_records = {}
            for row in all_records:
                ref_id = row[1]
                if ref_id not in grouped_records:
                    grouped_records[ref_id] = []
                grouped_records[ref_id].append(row)
            
            # Sort grouped records by the most recent date in each group
            sorted_groups = sorted(grouped_records.items(), 
                                 key=lambda x: max(record[10] or '' for record in x[1]), 
                                 reverse=True)
            
            for ref_id, records in sorted_groups:
                # Sort records within each group by date
                records.sort(key=lambda x: x[10] or '', reverse=True)
                
                # Calculate totals for the group
                total_gross = sum(record[4] for record in records)
                total_less = sum(record[5] for record in records)
                total_net = sum(record[6] for record in records)
                total_fine_gold = sum(record[9] for record in records)
                
                # Get common data from first record
                first_record = records[0]
                record_type = first_record[0]
                supplier_name = first_record[2]
                sale_date = first_record[10]
                
                # Create merged entry
                tag = 'sale' if record_type == 'Sale' else 'purchase'
                
                # Insert the merged summary row with expand/collapse icon (expanded by default)
                parent_item = self.unified_tree.insert('', 'end',
                    text=f"▼ {record_type} - {ref_id} ({len(records)} items)",  # Text column with expand icon and count (▼ for expanded)
                    values=(
                        record_type,  # Type
                        ref_id,  # Ref ID
                        supplier_name,  # Supplier
                        f"{len(records)} items",  # Item count instead of individual item
                        f"{total_gross:.2f}",  # Total Gross
                        f"{total_less:.2f}",  # Total Less
                        f"{total_net:.2f}",  # Total Net
                        f"{total_fine_gold:.2f}g",  # Total Fine Gold (combined)
                        f"{len(records)} entries",  # Wastage column used for entry count
                        f"{total_fine_gold:.2f}",  # Fine Gold (duplicate for display)
                        sale_date[:10] if sale_date else 'N/A',  # Date (first 10 chars)
                        ''  # Sale ID (empty for summary row)
                ), tags=(tag,), open=True)  # Start expanded by default

                # Store the ref_id in the item for later reference
                self.unified_tree.set(parent_item, 'Ref ID', ref_id)

                # Add individual item rows as children (visible since parent is expanded)
                for i, record in enumerate(records):
                    item_name = record[3] or 'N/A'
                    child_item = self.unified_tree.insert(parent_item, 'end', 
                        text=f"  • {item_name}",
                        values=(
                            '',  # Type (empty for child items)
                            '',  # Ref ID (empty for child items)
                            '',  # Supplier (empty for child items)
                            item_name,  # Item name
                            f"{record[4]:.2f}",  # Gross
                            f"{record[5]:.2f}",  # Less
                            f"{record[6]:.2f}",  # Net
                            f"{record[7]:.1f}%",  # Tunch
                            f"{record[8]:.1f}%",  # Wastage
                            f"{record[9]:.2f}",  # Fine Gold
                            record[10][:10] if record[10] else 'N/A',  # Date
                            record[11]  # Sale ID
                        ), tags=(f"{tag}_child",))
                
                # Keep parent item expanded by default
                
        except Exception as e:
            print(f"Error loading unified data: {e}")
    
    def create_work_orders_tab(self):
        """Create karigar (work) orders management tab"""
        work_frame = ttk.Frame(self.notebook)
        self.notebook.add(work_frame, text="🧑‍🏭 Karigar Orders")
        
        # Buttons frame with better styling
        btn_frame = tk.Frame(work_frame, bg=COLORS['light'])
        btn_frame.pack(fill='x', padx=15, pady=15)
        
        # Create beautiful buttons in two rows
        top_btn_frame = tk.Frame(btn_frame, bg=COLORS['light'])
        top_btn_frame.pack(fill='x', pady=(0, 10))
        
        new_order_btn = self.create_beautiful_button(top_btn_frame, "📝 New Karigar Order", lambda: self.karigar_orders_manager.show_create_order_modal(), 'success', 18, 'Ctrl+A')
        new_order_btn.pack(side='left', padx=(0, 10))
        
        complete_order_btn = self.create_beautiful_button(top_btn_frame, "✅ Complete Order", self.complete_work_order, 'warning', 18, 'Ctrl+S')
        complete_order_btn.pack(side='left', padx=(0, 10))
        
        bottom_btn_frame = tk.Frame(btn_frame, bg=COLORS['light'])
        bottom_btn_frame.pack(fill='x')
        
        view_details_btn = self.create_beautiful_button(bottom_btn_frame, "👁️ View Details", self.view_work_order_details, 'secondary', 18, 'Ctrl+V')
        view_details_btn.pack(side='left', padx=(0, 10))
        
        delete_order_btn = self.create_beautiful_button(bottom_btn_frame, "🗑️ Delete Order", self.delete_work_order, 'accent', 18, 'Ctrl+D')
        delete_order_btn.pack(side='left', padx=(0, 10))
        
        # Treeview for work orders with better styling
        tree_frame = tk.Frame(work_frame, bg=COLORS['light'])
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        columns = ('Order ID', 'Karigar', 'Issued (g)', 'Received (g)', 'Balance (g)', 'Status', 'Created At')
        self.work_orders_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', style='Treeview')
        
        for col in columns:
            self.work_orders_tree.heading(col, text=col)
            self.work_orders_tree.column(col, width=120, anchor='center')
        
        # Configure alternating row colors
        self.work_orders_tree.tag_configure('even', background=COLORS['light'])
        self.work_orders_tree.tag_configure('odd', background=COLORS['white'])
        
        self.work_orders_tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.work_orders_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.work_orders_tree.configure(yscrollcommand=scrollbar.set)
        
        # Initial load
        self.load_karigar_orders_data()

        # Double-click: if in progress, open edit modal
        def on_order_double_click(_e=None):
            try:
                selection = self.work_orders_tree.selection()
                if not selection:
                    return
                vals = self.work_orders_tree.item(selection[0])['values']
                if not vals:
                    return
                order_id = vals[0]
                status = str(vals[5]).strip().lower() if len(vals) > 5 else ''
                if status == 'in progress':
                    self.karigar_orders_manager.show_edit_order_modal(order_id)
                else:
                    # For other statuses, just refresh for now
                    self.load_karigar_orders_data()
            except Exception:
                self.load_karigar_orders_data()
        self.work_orders_tree.bind('<Double-1>', on_order_double_click)

    def load_karigar_orders_data(self):
        """Load rows from karigar_orders table into the karigar orders tree"""
        if not hasattr(self, 'work_orders_tree'):
            return
        for item in self.work_orders_tree.get_children():
            self.work_orders_tree.delete(item)
        try:
            # Ensure table exists
            self.db.execute_update(
                """
                CREATE TABLE IF NOT EXISTS karigar_orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    karigar_id INTEGER,
                    karigar_name TEXT,
                    issued_total REAL DEFAULT 0,
                    received_total REAL DEFAULT 0,
                    balance_total REAL DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT
                )
                """
            )
            # Backfill status column if missing
            try:
                cols = self.db.execute_query("PRAGMA table_info(karigar_orders)") or []
                has_status = any(c[1].lower() == 'status' for c in cols)
                if not has_status:
                    self.db.execute_update("ALTER TABLE karigar_orders ADD COLUMN status TEXT DEFAULT 'pending'")
            except Exception:
                pass
            rows = self.db.execute_query(
                """
                SELECT order_id, karigar_name, issued_total, received_total, balance_total, status, created_at
                FROM karigar_orders
                WHERE LOWER(COALESCE(status, '')) = 'in progress'
                ORDER BY order_id DESC
                """
            ) or []
            for i, r in enumerate(rows):
                tag = 'even' if i % 2 == 0 else 'odd'
                self.work_orders_tree.insert('', 'end', values=(
                    r[0],                 # Order ID
                    r[1] or '',           # Karigar
                    f"{(r[2] or 0):.2f}",# Issued
                    f"{(r[3] or 0):.2f}",# Received
                    f"{(r[4] or 0):.2f}",# Balance
                    (r[5] or 'pending').capitalize(), # Status
                    r[6] or ''            # Created At
                ), tags=(tag,))
        except Exception as e:
            try:
                messagebox.showerror("Error", f"Error loading karigar orders: {e}")
            except Exception:
                print(f"Error loading karigar orders: {e}")

    def _set_karigar_order_status(self, status_value: str):
        """Helper to set selected karigar orders to a given status."""
        try:
            if not hasattr(self, 'work_orders_tree'):
                messagebox.showwarning("Warning", "Karigar Orders table is not available")
                return
            selection = self.work_orders_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select order(s) to update")
                return
            ids = []
            for item in selection:
                vals = self.work_orders_tree.item(item)['values']
                if vals:
                    ids.append(vals[0])
            if not ids:
                return
            q = f"UPDATE karigar_orders SET status = ? WHERE order_id IN ({','.join(['?']*len(ids))})"
            self.db.execute_update(q, tuple([status_value] + ids))
            self.load_karigar_orders_data()
            self.show_toast(f"Order(s) marked {status_value.capitalize()}", success=True)
        except Exception as e:
            try:
                messagebox.showerror("Error", f"Error updating order status: {e}")
            except Exception:
                print(f"Error updating order status: {e}")

    def update_work_order(self):
        """Mark selected karigar orders as In Progress"""
        self._set_karigar_order_status('in progress')

    def complete_work_order(self):
        """Mark selected karigar orders as Completed"""
        self._set_karigar_order_status('completed')
    
    def create_freelancers_tab(self):
        """Create karigar (freelancers) management tab"""
        freelancer_frame = ttk.Frame(self.notebook)
        self.notebook.add(freelancer_frame, text="👥 Karigar")
        
        # Buttons frame with better styling
        btn_frame = tk.Frame(freelancer_frame, bg=COLORS['light'])
        btn_frame.pack(fill='x', padx=15, pady=15)
        
        # Create beautiful buttons
        add_freelancer_btn = self.create_beautiful_button(btn_frame, "➕ Add Freelancer", self.add_freelancer, 'success', 18, 'Ctrl+A')
        add_freelancer_btn.pack(side='left', padx=(0, 10))
        
        edit_freelancer_btn = self.create_beautiful_button(btn_frame, "✏️ Edit Freelancer", self.edit_freelancer, 'info', 18, 'Ctrl+E')
        edit_freelancer_btn.pack(side='left', padx=(0, 10))
        
        # Treeview for freelancers with better styling
        tree_frame = tk.Frame(freelancer_frame, bg=COLORS['light'])
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        columns = ('ID', 'Name', 'Specialization', 'Phone', 'Address', 'Joined Date', 'Active')
        self.freelancers_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', style='Treeview')
        
        for col in columns:
            self.freelancers_tree.heading(col, text=col)
            self.freelancers_tree.column(col, width=120, anchor='center')
        
        # Configure alternating row colors
        self.freelancers_tree.tag_configure('even', background=COLORS['light'])
        self.freelancers_tree.tag_configure('odd', background=COLORS['white'])
        
        self.freelancers_tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.freelancers_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.freelancers_tree.configure(yscrollcommand=scrollbar.set)
        
        # Set the tree for freelancer manager
        self.freelancer_manager.set_freelancers_tree(self.freelancers_tree)
        
        # Bind double-click to show freelancer work orders
        self.freelancers_tree.bind('<Double-1>', lambda e: self.view_freelancer_work_orders())
    
    
    def create_suppliers_tab(self):
        """Create suppliers management tab"""
        supplier_frame = ttk.Frame(self.notebook)
        self.notebook.add(supplier_frame, text="🏢 Suppliers")
        
        # Buttons frame with better styling
        btn_frame = tk.Frame(supplier_frame, bg=COLORS['light'])
        btn_frame.pack(fill='x', padx=15, pady=15)
        
        # Create beautiful buttons
        add_supplier_btn = self.create_beautiful_button(btn_frame, "➕ Add Supplier", self.add_supplier, 'success', 18, 'Ctrl+A')
        add_supplier_btn.pack(side='left', padx=(0, 10))
        
        edit_supplier_btn = self.create_beautiful_button(btn_frame, "✏️ Edit Supplier", self.edit_supplier, 'info', 18, 'Ctrl+E')
        edit_supplier_btn.pack(side='left', padx=(0, 10))
        
        delete_supplier_btn = self.create_beautiful_button(btn_frame, "🗑️ Delete Supplier", self.delete_selected_supplier, 'danger', 18, 'Ctrl+D')
        delete_supplier_btn.pack(side='right', padx=(10, 0))
        
        # Treeview for suppliers with better styling
        tree_frame = tk.Frame(supplier_frame, bg=COLORS['light'])
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        columns = ('ID', 'Name', 'Contact Person', 'Phone', 'Email', 'Address', 'GST Number', 'Active')
        self.suppliers_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', style='Treeview')
        
        for col in columns:
            self.suppliers_tree.heading(col, text=col)
            self.suppliers_tree.column(col, width=120, anchor='center')
        
        # Configure alternating row colors
        self.suppliers_tree.tag_configure('even', background=COLORS['light'])
        self.suppliers_tree.tag_configure('odd', background=COLORS['white'])
        
        self.suppliers_tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.suppliers_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.suppliers_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click event
        self.suppliers_tree.bind('<Double-1>', self.on_supplier_double_click)
        
        # Bind delete key and context menu
        self.suppliers_tree.bind('<Delete>', lambda e: self.delete_selected_supplier())
        self.suppliers_tree.bind('<BackSpace>', lambda e: self.delete_selected_supplier())
        self.suppliers_tree.bind('<Button-3>', self.show_supplier_context_menu)
        
        # Set the tree for supplier manager
        self.supplier_manager.set_suppliers_tree(self.suppliers_tree)
    
    def on_supplier_double_click(self, event):
        """Handle supplier double-click to show all sales and purchase orders"""
        selection = self.suppliers_tree.selection()
        if selection:
            item = self.suppliers_tree.item(selection[0])
            values = item['values']
            supplier_id = values[0]  # Get supplier ID from first column
            supplier_name = values[1]  # Get supplier name from second column
            self.show_supplier_orders(supplier_id, supplier_name)
        else:
            messagebox.showwarning("Warning", "Please select a supplier to view orders")
    
    def show_supplier_orders(self, supplier_id, supplier_name):
        """Show all sales and purchase orders for a specific supplier"""
        # Create modal for showing supplier orders
        modal = tk.Toplevel(self.root)
        modal.title(f"Orders for {supplier_name}")
        modal.geometry("1200x700")
        modal.resizable(True, True)
        modal.transient(self.root)
        modal.grab_set()
        
        # Center the modal
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (600)
        y = (modal.winfo_screenheight() // 2) - (350)
        modal.geometry(f"1200x700+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(modal, bg=COLORS['light'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text=f"All Orders for {supplier_name}",
                              font=FONTS['heading'],
                              fg=COLORS['primary'],
                              bg=COLORS['light'])
        title_label.pack(pady=(0, 10))
        
        # Balance display
        balance = self.get_supplier_balance(supplier_name)
        balance_label = tk.Label(main_frame, 
                                text=f"Current Balance: {balance:.2f}gm",
                                font=FONTS['subheading'],
                                fg=COLORS['success'] if balance >= 0 else COLORS['danger'],
                                bg=COLORS['light'])
        balance_label.pack(pady=(0, 20))
        
        # Create notebook for Sales and Purchases tabs
        notebook = ttk.Notebook(main_frame)
        notebook.configure(style='TNotebook')
        notebook.pack(fill='both', expand=True)
        
        # Sales tab
        sales_frame = ttk.Frame(notebook)
        notebook.add(sales_frame, text="Sales Orders")
        
        # Sales table
        sales_columns = ('Ref ID', 'Item', 'Gross (g)', 'Less (g)', 'Net (g)', 'Tunch (%)', 'Wastage (%)', 'Fine Gold (g)', 'Date')
        sales_tree = ttk.Treeview(sales_frame, columns=sales_columns, show='headings', style='Treeview')
        
        for col in sales_columns:
            sales_tree.heading(col, text=col)
            sales_tree.column(col, width=100, anchor='center')
        
        # Configure alternating row colors
        sales_tree.tag_configure('even', background=COLORS['light'])
        sales_tree.tag_configure('odd', background=COLORS['white'])
        
        sales_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        # Sales scrollbar
        sales_scrollbar = ttk.Scrollbar(sales_frame, orient='vertical', command=sales_tree.yview)
        sales_scrollbar.pack(side='right', fill='y')
        sales_tree.configure(yscrollcommand=sales_scrollbar.set)
        
        # Purchases tab
        purchases_frame = ttk.Frame(notebook)
        notebook.add(purchases_frame, text="Purchase Orders")
        
        # Purchases table
        purchases_columns = ('Ref ID', 'Item', 'Gross (g)', 'Less (g)', 'Net (g)', 'Tunch (%)', 'Wastage (%)', 'Fine Gold (g)', 'Date')
        purchases_tree = ttk.Treeview(purchases_frame, columns=purchases_columns, show='headings', style='Treeview')
        
        for col in purchases_columns:
            purchases_tree.heading(col, text=col)
            purchases_tree.column(col, width=100, anchor='center')
        
        # Configure alternating row colors
        purchases_tree.tag_configure('even', background=COLORS['light'])
        purchases_tree.tag_configure('odd', background=COLORS['white'])
        
        purchases_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        # Purchases scrollbar
        purchases_scrollbar = ttk.Scrollbar(purchases_frame, orient='vertical', command=purchases_tree.yview)
        purchases_scrollbar.pack(side='right', fill='y')
        purchases_tree.configure(yscrollcommand=purchases_scrollbar.set)
        
        # Load data for both tables
        self.load_supplier_sales_data(sales_tree, supplier_name)
        self.load_supplier_purchases_data(purchases_tree, supplier_name)
        
        # Close button
        close_btn = tk.Button(main_frame, 
                             text="Close",
                             command=modal.destroy,
                             font=FONTS['body'],
                             bg=COLORS['secondary'],
                             fg=COLORS['white'],
                             relief='raised',
                             bd=2,
                             width=15)
        close_btn.pack(pady=(20, 0))
    
    def load_supplier_sales_data(self, tree_widget, supplier_name):
        """Load sales data for a specific supplier"""
        # Clear existing items
        for item in tree_widget.get_children():
            tree_widget.delete(item)
        
        try:
            query = '''
                SELECT 
                    s.ref_id,
                    COALESCE(i.item_name, 'N/A') as item_name,
                    s.gross_weight,
                    s.less_weight,
                    s.net_weight,
                    s.tunch_percentage,
                    s.wastage_percentage,
                    s.fine_gold,
                    s.sale_date
                FROM sales s
                LEFT JOIN items i ON s.item_id = i.item_id
                WHERE s.supplier_name = ? AND s.ref_id LIKE 'S%'
                ORDER BY s.sale_date DESC
            '''
            rows = self.db.execute_query(query, (supplier_name,))
            
            for i, row in enumerate(rows):
                tag = 'even' if i % 2 == 0 else 'odd'
                tree_widget.insert('', 'end', values=(
                    row[0],  # Ref ID
                    row[1],  # Item
                    f"{row[2]:.2f}",  # Gross
                    f"{row[3]:.2f}",  # Less
                    f"{row[4]:.2f}",  # Net
                    f"{row[5]:.1f}",  # Tunch
                    f"{row[6]:.1f}",  # Wastage
                    f"{row[7]:.2f}",  # Fine Gold
                    row[8][:10] if row[8] else 'N/A'  # Date
                ), tags=(tag,))
                
        except Exception as e:
            print(f"Error loading supplier sales data: {e}")
    
    def load_supplier_purchases_data(self, tree_widget, supplier_name):
        """Load purchase data for a specific supplier"""
        # Clear existing items
        for item in tree_widget.get_children():
            tree_widget.delete(item)
        
        try:
            query = '''
                SELECT 
                    s.ref_id,
                    COALESCE(i.item_name, 'N/A') as item_name,
                    s.gross_weight,
                    s.less_weight,
                    s.net_weight,
                    s.tunch_percentage,
                    s.wastage_percentage,
                    s.fine_gold,
                    s.sale_date
                FROM sales s
                LEFT JOIN items i ON s.item_id = i.item_id
                WHERE s.supplier_name = ? AND s.ref_id LIKE 'P%'
                ORDER BY s.sale_date DESC
            '''
            rows = self.db.execute_query(query, (supplier_name,))
            
            for i, row in enumerate(rows):
                tag = 'even' if i % 2 == 0 else 'odd'
                tree_widget.insert('', 'end', values=(
                    row[0],  # Ref ID
                    row[1],  # Item
                    f"{row[2]:.2f}",  # Gross
                    f"{row[3]:.2f}",  # Less
                    f"{row[4]:.2f}",  # Net
                    f"{row[5]:.1f}",  # Tunch
                    f"{row[6]:.1f}",  # Wastage
                    f"{row[7]:.2f}",  # Fine Gold
                    row[8][:10] if row[8] else 'N/A'  # Date
                ), tags=(tag,))
                
        except Exception as e:
            print(f"Error loading supplier purchases data: {e}")
    
    def delete_selected_supplier(self):
        """Delete selected supplier and all related records"""
        selection = self.suppliers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a supplier to delete")
            return
        
        # Get supplier details
        item = self.suppliers_tree.item(selection[0])
        values = item['values']
        supplier_id = values[0]
        supplier_name = values[1]
        
        # Check for related records
        related_sales = self.get_supplier_related_sales(supplier_name)
        related_purchases = self.get_supplier_related_purchases(supplier_name)
        
        # Show confirmation dialog with details
        message = f"Are you sure you want to delete supplier '{supplier_name}'?\n\n"
        message += f"This will also delete:\n"
        message += f"• {len(related_sales)} sales record(s)\n"
        message += f"• {len(related_purchases)} purchase record(s)\n\n"
        message += "This action cannot be undone!"
        
        if messagebox.askyesno("Confirm Delete", message):
            self.delete_supplier_and_related_data(supplier_id, supplier_name, related_sales, related_purchases)
    
    def get_supplier_related_sales(self, supplier_name):
        """Get all sales records for a supplier"""
        try:
            query = "SELECT ref_id, fine_gold, net_weight, item_id FROM sales WHERE supplier_name = ? AND ref_id LIKE 'S%'"
            return self.db.execute_query(query, (supplier_name,))
        except Exception as e:
            print(f"Error getting related sales: {e}")
            return []
    
    def get_supplier_related_purchases(self, supplier_name):
        """Get all purchase records for a supplier"""
        try:
            query = "SELECT ref_id, fine_gold, net_weight, item_id FROM sales WHERE supplier_name = ? AND ref_id LIKE 'P%'"
            return self.db.execute_query(query, (supplier_name,))
        except Exception as e:
            print(f"Error getting related purchases: {e}")
            return []
    
    def delete_supplier_and_related_data(self, supplier_id, supplier_name, related_sales, related_purchases):
        """Delete supplier and all related sales/purchase records"""
        try:
            deleted_sales = 0
            deleted_purchases = 0
            
            # Delete sales records and adjust inventory
            for sale in related_sales:
                ref_id, fine_gold, net_weight, item_id = sale
                
                # Adjust inventory (add back weights since deleting sale)
                self.update_item_inventory(item_id, fine_gold, net_weight, 'add')
                
                # Adjust supplier balance (subtract monetary value since deleting sale)
                monetary_value = self.calculate_monetary_value(fine_gold)
                self.update_supplier_balance(supplier_name, monetary_value, 'subtract')
                
                # Delete the sales record
                delete_query = "DELETE FROM sales WHERE ref_id = ?"
                self.db.execute_update(delete_query, (ref_id,))
                deleted_sales += 1
                print(f"Deleted sales record {ref_id}")
            
            # Delete purchase records and adjust inventory
            for purchase in related_purchases:
                ref_id, fine_gold, net_weight, item_id = purchase
                
                # Adjust inventory (subtract weights since deleting purchase)
                self.update_item_inventory(item_id, fine_gold, net_weight, 'subtract')
                
                # Adjust supplier balance (add back monetary value since deleting purchase)
                monetary_value = self.calculate_monetary_value(fine_gold)
                self.update_supplier_balance(supplier_name, monetary_value, 'add')
                
                # Delete the purchase record
                delete_query = "DELETE FROM sales WHERE ref_id = ?"
                self.db.execute_update(delete_query, (ref_id,))
                deleted_purchases += 1
                print(f"Deleted purchase record {ref_id}")
            
            # Delete the supplier
            supplier_delete_query = "DELETE FROM suppliers WHERE supplier_id = ?"
            self.db.execute_update(supplier_delete_query, (supplier_id,))
            
            # Refresh all tables
            self.load_suppliers_data()
            self.load_unified_data()
            self.load_items_data()
            
            self.show_toast(f"Successfully deleted supplier '{supplier_name}' • Deleted {deleted_sales} sales, {deleted_purchases} purchases, adjusted inventory", success=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting supplier: {e}")
    
    def show_supplier_context_menu(self, event):
        """Show context menu for suppliers"""
        # Select the item under the cursor
        item = self.suppliers_tree.identify_row(event.y)
        if item:
            self.suppliers_tree.selection_set(item)
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="View Orders", command=self.view_selected_supplier_orders)
            context_menu.add_command(label="Edit Supplier", command=self.edit_selected_supplier)
            context_menu.add_command(label="Delete Supplier", command=self.delete_selected_supplier)
            context_menu.add_separator()
            context_menu.add_command(label="Refresh", command=self.load_suppliers_data)
            
            # Show the context menu
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def view_selected_supplier_orders(self):
        """View orders for selected supplier"""
        selection = self.suppliers_tree.selection()
        if selection:
            item = self.suppliers_tree.item(selection[0])
            values = item['values']
            supplier_id = values[0]
            supplier_name = values[1]
            self.show_supplier_orders(supplier_id, supplier_name)
        else:
            messagebox.showwarning("Warning", "Please select a supplier to view orders")
    
    def edit_selected_supplier(self):
        """Edit selected supplier"""
        selection = self.suppliers_tree.selection()
        if selection:
            # This would call the existing edit_supplier function
            # For now, just show a message
            messagebox.showinfo("Info", "Edit supplier functionality - to be implemented")
        else:
            messagebox.showwarning("Warning", "Please select a supplier to edit")
    
    def load_suppliers_data(self):
        """Load suppliers data from database"""
        if not hasattr(self, 'suppliers_tree'):
            return
            
        # Clear existing items
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        
        try:
            query = '''
                SELECT 
                    supplier_id,
                    supplier_name,
                    contact_person,
                    phone,
                    email,
                    address,
                    gst_number,
                    CASE WHEN is_active = 1 THEN 'Active' ELSE 'Inactive' END as status
                FROM suppliers
                ORDER BY supplier_name
            '''
            rows = self.db.execute_query(query)
            
            for i, row in enumerate(rows):
                tag = 'even' if i % 2 == 0 else 'odd'
                self.suppliers_tree.insert('', 'end', values=row, tags=(tag,))
                
        except Exception as e:
            print(f"Error loading suppliers data: {e}")
    
    
    def load_data(self):
        """Load data into all treeviews"""
        self.work_order_manager.load_work_orders()
        self.freelancer_manager.load_freelancers()
        self.load_suppliers_data()
        self.load_home_data()
        self.load_raini_data()
    
    
    
    def load_suppliers(self):
        """Load suppliers data"""
        self.supplier_manager.load_suppliers()
    
    # Inventory methods
    def add_gold(self):
        """Add new gold to inventory"""
        messagebox.showinfo("Info", "Gold entry functionality to be implemented")
    
    def generate_purchase_ref_id(self):
        """Generate purchase reference ID with format: P + DDMMYY + / + 3-digit incremental"""
        from datetime import datetime
        today = datetime.now()
        date_str = today.strftime('%d%m%y')
        
        try:
            # Get the highest existing number for today from sales table
            query = f"SELECT ref_id FROM sales WHERE ref_id LIKE 'P{date_str}/%' ORDER BY ref_id DESC LIMIT 1"
            result = self.db.execute_query(query)
            
            if result and result[0][0]:
                existing_ref = result[0][0]
                existing_num = int(existing_ref.split('/')[-1])
                next_num = existing_num + 1
            else:
                next_num = 1
            
            # Format as 3-digit number
            ref_id = f"P{date_str}/{next_num:03d}"
            
            # Double-check that this Ref ID doesn't already exist
            check_query = "SELECT COUNT(*) FROM sales WHERE ref_id = ?"
            check_result = self.db.execute_query(check_query, (ref_id,))
            if check_result and check_result[0][0] > 0:
                print(f"WARNING: Ref ID {ref_id} already exists! Incrementing...")
                next_num += 1
                ref_id = f"P{date_str}/{next_num:03d}"
                
        except Exception as e:
            print(f"Error generating purchase ref ID: {e}")
            next_num = 1
            ref_id = f"P{date_str}/{next_num:03d}"
        
        return ref_id
    
    def add_purchase(self):
        """Add new gold purchase - open multiple purchases directly"""
        self.multiple_purchases_manager.show_multiple_purchases_modal()
    
    
    def open_update_sales_modal(self, ref_id, parent_modal):
        """Open modal to update a specific sales record"""
        # Close the selection modal if it exists
        if parent_modal:
            parent_modal.destroy()
        
        # Get the sales record data
        try:
            query = '''
                SELECT 
                    s.ref_id,
                    s.supplier_name,
                    s.item_id,
                    s.gross_weight,
                    s.less_weight,
                    s.net_weight,
                    s.tunch_percentage,
                    s.wastage_percentage,
                    s.fine_gold,
                    s.sale_date
                FROM sales s
                WHERE s.ref_id = ?
            '''
            result = self.db.execute_query(query, (ref_id,))
            
            if not result:
                messagebox.showerror("Error", "Sales record not found")
                return
                
            record = result[0]
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading sales record: {e}")
            return
        
        # Create update modal
        update_modal = tk.Toplevel(self.root)
        update_modal.title(f"Update Sales Order - {ref_id}")
        update_modal.geometry("700x600")
        update_modal.resizable(False, False)
        update_modal.transient(self.root)
        update_modal.grab_set()
        
        # Center the modal
        update_modal.update_idletasks()
        x = (update_modal.winfo_screenwidth() // 2) - (700 // 2)
        y = (update_modal.winfo_screenheight() // 2) - (600 // 2)
        update_modal.geometry(f"700x600+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(update_modal, bg=COLORS['light'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text=f"Update Sales Order - {ref_id}",
                              font=FONTS['heading'],
                              fg=COLORS['primary'],
                              bg=COLORS['light'])
        title_label.pack(pady=(0, 20))
        
        # Ref ID (readonly)
        ref_frame = tk.Frame(main_frame, bg=COLORS['light'])
        ref_frame.pack(fill='x', pady=(0, 15))
        
        ref_label = tk.Label(ref_frame, 
                            text="Ref ID:",
                            font=FONTS['body'],
                            fg=COLORS['dark'],
                            bg=COLORS['light'])
        ref_label.pack(anchor='w')
        
        ref_entry = tk.Entry(ref_frame, 
                            font=FONTS['body'],
                            width=30,
                            state='readonly')
        ref_entry.pack(fill='x', pady=(5, 0))
        ref_entry.config(state='normal')
        ref_entry.insert(0, ref_id)
        ref_entry.config(state='readonly')
        
        # Load suppliers and items for dropdowns
        try:
            suppliers = self.db.execute_query("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name")
            supplier_options = [f"{s[0]} - {s[1]}" for s in suppliers]
            
            items = self.db.execute_query("SELECT item_id, item_name FROM items ORDER BY item_name")
            item_options = [f"{i[0]} - {i[1]}" for i in items]
        except Exception as e:
            messagebox.showerror("Error", f"Error loading dropdown data: {e}")
            supplier_options = []
            item_options = []
        
        # Supplier dropdown
        supplier_frame = tk.Frame(main_frame, bg=COLORS['light'])
        supplier_frame.pack(fill='x', pady=(0, 15))
        
        supplier_label = tk.Label(supplier_frame, 
                                 text="Supplier:",
                                 font=FONTS['body'],
                                 fg=COLORS['dark'],
                                 bg=COLORS['light'])
        supplier_label.pack(anchor='w')
        
        supplier_combo = ttk.Combobox(supplier_frame, 
                                     font=FONTS['body'],
                                     width=30,
                                     state='readonly')
        supplier_combo['values'] = supplier_options
        supplier_combo.pack(fill='x', pady=(5, 0))
        
        # Set current supplier
        current_supplier = f"{record[1]}"  # supplier_name
        for option in supplier_options:
            if current_supplier in option:
                supplier_combo.set(option)
                break
        
        # Item dropdown
        item_frame = tk.Frame(main_frame, bg=COLORS['light'])
        item_frame.pack(fill='x', pady=(0, 15))
        
        item_label = tk.Label(item_frame, 
                             text="Item:",
                             font=FONTS['body'],
                             fg=COLORS['dark'],
                             bg=COLORS['light'])
        item_label.pack(anchor='w')
        
        item_combo = ttk.Combobox(item_frame, 
                                 font=FONTS['body'],
                                 width=30,
                                 state='readonly')
        item_combo['values'] = item_options
        item_combo.pack(fill='x', pady=(5, 0))
        
        # Set current item
        current_item_id = record[2]  # item_id
        for option in item_options:
            if option.startswith(f"{current_item_id} -"):
                item_combo.set(option)
                break
        
        # Weight fields in a row
        weight_frame = tk.Frame(main_frame, bg=COLORS['light'])
        weight_frame.pack(fill='x', pady=(0, 15))
        
        # Gross weight
        gross_frame = tk.Frame(weight_frame, bg=COLORS['light'])
        gross_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        gross_label = tk.Label(gross_frame, 
                              text="Gross Weight:",
                              font=FONTS['body'],
                              fg=COLORS['dark'],
                              bg=COLORS['light'])
        gross_label.pack(anchor='w')
        
        gross_entry = tk.Entry(gross_frame, 
                              font=FONTS['body'],
                              width=15)
        gross_entry.pack(fill='x', pady=(5, 0))
        self.populate_entry_field(gross_entry, record[3])  # gross_weight
        
        # Less weight
        less_frame = tk.Frame(weight_frame, bg=COLORS['light'])
        less_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        less_label = tk.Label(less_frame, 
                             text="Less Weight:",
                             font=FONTS['body'],
                             fg=COLORS['dark'],
                             bg=COLORS['light'])
        less_label.pack(anchor='w')
        
        less_entry = tk.Entry(less_frame, 
                             font=FONTS['body'],
                             width=15)
        less_entry.pack(fill='x', pady=(5, 0))
        self.populate_entry_field(less_entry, record[4])  # less_weight
        
        # Net weight (calculated)
        net_frame = tk.Frame(weight_frame, bg=COLORS['light'])
        net_frame.pack(side='left', fill='x', expand=True)
        
        net_label = tk.Label(net_frame, 
                            text="Net Weight:",
                            font=FONTS['body'],
                            fg=COLORS['dark'],
                            bg=COLORS['light'])
        net_label.pack(anchor='w')
        
        net_entry = tk.Entry(net_frame, 
                            font=FONTS['body'],
                            width=15,
                            state='readonly')
        net_entry.pack(fill='x', pady=(5, 0))
        net_entry.config(state='normal')
        self.populate_entry_field(net_entry, record[5])  # net_weight
        net_entry.config(state='readonly')
        
        # Percentage fields in a row
        percentage_frame = tk.Frame(main_frame, bg=COLORS['light'])
        percentage_frame.pack(fill='x', pady=(0, 15))
        
        # Tunch percentage
        tunch_frame = tk.Frame(percentage_frame, bg=COLORS['light'])
        tunch_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        tunch_label = tk.Label(tunch_frame, 
                              text="Tunch %:",
                              font=FONTS['body'],
                              fg=COLORS['dark'],
                              bg=COLORS['light'])
        tunch_label.pack(anchor='w')
        
        tunch_entry = tk.Entry(tunch_frame, 
                              font=FONTS['body'],
                              width=15)
        tunch_entry.pack(fill='x', pady=(5, 0))
        self.populate_entry_field(tunch_entry, record[6])  # tunch_percentage
        
        # Wastage percentage
        wastage_frame = tk.Frame(percentage_frame, bg=COLORS['light'])
        wastage_frame.pack(side='left', fill='x', expand=True)
        
        wastage_label = tk.Label(wastage_frame, 
                                text="Wastage %:",
                                font=FONTS['body'],
                                fg=COLORS['dark'],
                                bg=COLORS['light'])
        wastage_label.pack(anchor='w')
        
        wastage_entry = tk.Entry(wastage_frame, 
                                font=FONTS['body'],
                                width=15)
        wastage_entry.pack(fill='x', pady=(5, 0))
        self.populate_entry_field(wastage_entry, record[7])  # wastage_percentage
        
        # Fine gold (calculated)
        fine_frame = tk.Frame(main_frame, bg=COLORS['light'])
        fine_frame.pack(fill='x', pady=(0, 15))
        
        fine_label = tk.Label(fine_frame, 
                             text="Fine Gold:",
                             font=FONTS['body'],
                             fg=COLORS['dark'],
                             bg=COLORS['light'])
        fine_label.pack(anchor='w')
        
        fine_entry = tk.Entry(fine_frame, 
                             font=FONTS['body'],
                             width=30,
                             state='readonly')
        fine_entry.pack(fill='x', pady=(5, 0))
        fine_entry.config(state='normal')
        self.populate_entry_field(fine_entry, record[8])  # fine_gold
        fine_entry.config(state='readonly')
        
        # Calculation function
        def calculate_values():
            try:
                gross = float(gross_entry.get() or 0)
                less = float(less_entry.get() or 0)
                tunch = float(tunch_entry.get() or 0)
                wastage = float(wastage_entry.get() or 0)
                
                # Calculate net weight
                net_weight = gross - less
                
                # Calculate fine gold
                fine_gold = (net_weight / 100 * tunch) + (net_weight / 100 * wastage)
                
                # Update readonly fields
                net_entry.config(state='normal')
                net_entry.delete(0, tk.END)
                net_entry.insert(0, f"{net_weight:.2f}")
                net_entry.config(state='readonly')
                
                fine_entry.config(state='normal')
                fine_entry.delete(0, tk.END)
                fine_entry.insert(0, f"{fine_gold:.2f}")
                fine_entry.config(state='readonly')
                
            except (ValueError, TypeError):
                pass
        
        # Bind calculation events
        gross_entry.bind('<KeyRelease>', lambda e: calculate_values())
        less_entry.bind('<KeyRelease>', lambda e: calculate_values())
        tunch_entry.bind('<KeyRelease>', lambda e: calculate_values())
        wastage_entry.bind('<KeyRelease>', lambda e: calculate_values())
        
        # Add number validation to all numeric fields
        self.add_number_validation(gross_entry)
        self.add_number_validation(less_entry)
        self.add_number_validation(tunch_entry)
        self.add_number_validation(wastage_entry)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=COLORS['light'])
        button_frame.pack(fill='x', pady=(20, 0))
        
        def save_update():
            """Save the updated sales record"""
            supplier_text = supplier_combo.get().strip()
            item_text = item_combo.get().strip()
            gross = gross_entry.get().strip()
            less = less_entry.get().strip()
            tunch = tunch_entry.get().strip()
            wastage = wastage_entry.get().strip()
            
            if not all([supplier_text, item_text, gross, less, tunch, wastage]):
                messagebox.showerror("Error", "All fields are required")
                return
            
            try:
                # Get old values for inventory and balance adjustment
                old_query = "SELECT item_id, fine_gold, net_weight, supplier_name FROM sales WHERE ref_id = ?"
                old_values = self.db.execute_query(old_query, (ref_id,))
                if old_values:
                    old_item_id, old_fine_gold, old_net_weight, old_supplier_name = old_values[0]
                else:
                    old_item_id, old_fine_gold, old_net_weight, old_supplier_name = 0, 0, 0, ""
                
                # Extract supplier_id and supplier_name
                supplier_id = int(supplier_text.split(' - ')[0])
                supplier_name = supplier_text.split(' - ')[1]
                
                # Extract item_id
                item_id = int(item_text.split(' - ')[0])
                
                # Calculate values
                net_weight = float(gross) - float(less)
                fine_gold = (net_weight / 100 * float(tunch)) + (net_weight / 100 * float(wastage))
                
                # Update the record
                query = '''
                    UPDATE sales 
                    SET supplier_name = ?, item_id = ?, gross_weight = ?, less_weight = ?, 
                        net_weight = ?, tunch_percentage = ?, wastage_percentage = ?, fine_gold = ?
                    WHERE ref_id = ?
                '''
                self.db.execute_update(query, (
                    supplier_name, item_id, float(gross), float(less),
                    net_weight, float(tunch), float(wastage), fine_gold, ref_id
                ))
                
                # Update item inventory (reverse old sale, apply new sale)
                self.update_item_inventory_for_record_update(
                    ref_id, old_fine_gold, old_net_weight, fine_gold, net_weight, 
                    old_item_id, item_id, is_purchase=False
                )
                
                # Update supplier balance (reverse old sale, apply new sale)
                old_monetary_value = self.calculate_monetary_value(old_fine_gold)
                new_monetary_value = self.calculate_monetary_value(fine_gold)
                self.update_supplier_balance_for_record_update(
                    ref_id, old_monetary_value, new_monetary_value, old_supplier_name, supplier_name, is_purchase=False
                )
                
                self.show_toast("Sales record updated successfully!", success=True)
                self.load_unified_data()  # Refresh unified table
                update_modal.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error updating sales record: {e}")
        
        save_btn = tk.Button(button_frame, 
                            text="Save Update",
                            command=save_update,
                            font=FONTS['body'],
                            bg=COLORS['success'],
                            fg=COLORS['white'],
                            relief='raised',
                            bd=2)
        save_btn.pack(side='right', padx=(10, 0))
        
        cancel_btn = tk.Button(button_frame, 
                              text="Cancel",
                              command=update_modal.destroy,
                              font=FONTS['body'],
                              bg=COLORS['secondary'],
                              fg=COLORS['white'],
                              relief='raised',
                              bd=2)
        cancel_btn.pack(side='right')
    
    def open_update_purchase_modal(self, ref_id, parent_modal):
        """Open modal to update a specific purchase record"""
        # Close the selection modal if it exists
        if parent_modal:
            parent_modal.destroy()
        
        # Get the purchase record data
        try:
            query = '''
                SELECT 
                    s.ref_id,
                    s.supplier_name,
                    s.item_id,
                    s.gross_weight,
                    s.less_weight,
                    s.net_weight,
                    s.tunch_percentage,
                    s.wastage_percentage,
                    s.fine_gold,
                    s.sale_date
                FROM sales s
                WHERE s.ref_id = ?
            '''
            result = self.db.execute_query(query, (ref_id,))
            
            if not result:
                messagebox.showerror("Error", "Purchase record not found")
                return
                
            record = result[0]
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading purchase record: {e}")
            return
        
        # Create update modal
        update_modal = tk.Toplevel(self.root)
        update_modal.title(f"Update Purchase Order - {ref_id}")
        update_modal.geometry("700x600")
        update_modal.resizable(False, False)
        update_modal.transient(self.root)
        update_modal.grab_set()
        
        # Center the modal
        update_modal.update_idletasks()
        x = (update_modal.winfo_screenwidth() // 2) - (700 // 2)
        y = (update_modal.winfo_screenheight() // 2) - (600 // 2)
        update_modal.geometry(f"700x600+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(update_modal, bg=COLORS['light'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text=f"Update Purchase Order - {ref_id}",
                              font=FONTS['heading'],
                              fg=COLORS['primary'],
                              bg=COLORS['light'])
        title_label.pack(pady=(0, 20))
        
        # Ref ID (readonly)
        ref_frame = tk.Frame(main_frame, bg=COLORS['light'])
        ref_frame.pack(fill='x', pady=(0, 15))
        
        ref_label = tk.Label(ref_frame, 
                            text="Ref ID:",
                            font=FONTS['body'],
                            fg=COLORS['dark'],
                            bg=COLORS['light'])
        ref_label.pack(anchor='w')
        
        ref_entry = tk.Entry(ref_frame, 
                            font=FONTS['body'],
                            width=30,
                            state='readonly')
        ref_entry.pack(fill='x', pady=(5, 0))
        ref_entry.config(state='normal')
        ref_entry.insert(0, ref_id)
        ref_entry.config(state='readonly')
        
        # Load suppliers and items for dropdowns
        try:
            suppliers = self.db.execute_query("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name")
            supplier_options = [f"{s[0]} - {s[1]}" for s in suppliers]
            
            items = self.db.execute_query("SELECT item_id, item_name FROM items ORDER BY item_name")
            item_options = [f"{i[0]} - {i[1]}" for i in items]
        except Exception as e:
            messagebox.showerror("Error", f"Error loading dropdown data: {e}")
            supplier_options = []
            item_options = []
        
        # Supplier dropdown
        supplier_frame = tk.Frame(main_frame, bg=COLORS['light'])
        supplier_frame.pack(fill='x', pady=(0, 15))
        
        supplier_label = tk.Label(supplier_frame, 
                                 text="Supplier:",
                                 font=FONTS['body'],
                                 fg=COLORS['dark'],
                                 bg=COLORS['light'])
        supplier_label.pack(anchor='w')
        
        supplier_combo = ttk.Combobox(supplier_frame, 
                                     font=FONTS['body'],
                                     width=30,
                                     state='readonly')
        supplier_combo['values'] = supplier_options
        supplier_combo.pack(fill='x', pady=(5, 0))
        
        # Set current supplier
        current_supplier = f"{record[1]}"  # supplier_name
        for option in supplier_options:
            if current_supplier in option:
                supplier_combo.set(option)
                break
        
        # Item dropdown
        item_frame = tk.Frame(main_frame, bg=COLORS['light'])
        item_frame.pack(fill='x', pady=(0, 15))
        
        item_label = tk.Label(item_frame, 
                             text="Item:",
                             font=FONTS['body'],
                             fg=COLORS['dark'],
                             bg=COLORS['light'])
        item_label.pack(anchor='w')
        
        item_combo = ttk.Combobox(item_frame, 
                                 font=FONTS['body'],
                                 width=30,
                                 state='readonly')
        item_combo['values'] = item_options
        item_combo.pack(fill='x', pady=(5, 0))
        
        # Set current item
        current_item_id = record[2]  # item_id
        for option in item_options:
            if option.startswith(f"{current_item_id} -"):
                item_combo.set(option)
                break
        
        # Weight fields in a row
        weight_frame = tk.Frame(main_frame, bg=COLORS['light'])
        weight_frame.pack(fill='x', pady=(0, 15))
        
        # Gross weight
        gross_frame = tk.Frame(weight_frame, bg=COLORS['light'])
        gross_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        gross_label = tk.Label(gross_frame, 
                              text="Gross Weight:",
                              font=FONTS['body'],
                              fg=COLORS['dark'],
                              bg=COLORS['light'])
        gross_label.pack(anchor='w')
        
        gross_entry = tk.Entry(gross_frame, 
                              font=FONTS['body'],
                              width=15)
        gross_entry.pack(fill='x', pady=(5, 0))
        self.populate_entry_field(gross_entry, record[3])  # gross_weight
        
        # Less weight
        less_frame = tk.Frame(weight_frame, bg=COLORS['light'])
        less_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        less_label = tk.Label(less_frame, 
                             text="Less Weight:",
                             font=FONTS['body'],
                             fg=COLORS['dark'],
                             bg=COLORS['light'])
        less_label.pack(anchor='w')
        
        less_entry = tk.Entry(less_frame, 
                             font=FONTS['body'],
                             width=15)
        less_entry.pack(fill='x', pady=(5, 0))
        self.populate_entry_field(less_entry, record[4])  # less_weight
        
        # Net weight (calculated)
        net_frame = tk.Frame(weight_frame, bg=COLORS['light'])
        net_frame.pack(side='left', fill='x', expand=True)
        
        net_label = tk.Label(net_frame, 
                            text="Net Weight:",
                            font=FONTS['body'],
                            fg=COLORS['dark'],
                            bg=COLORS['light'])
        net_label.pack(anchor='w')
        
        net_entry = tk.Entry(net_frame, 
                            font=FONTS['body'],
                            width=15,
                            state='readonly')
        net_entry.pack(fill='x', pady=(5, 0))
        net_entry.config(state='normal')
        self.populate_entry_field(net_entry, record[5])  # net_weight
        net_entry.config(state='readonly')
        
        # Percentage fields in a row
        percentage_frame = tk.Frame(main_frame, bg=COLORS['light'])
        percentage_frame.pack(fill='x', pady=(0, 15))
        
        # Tunch percentage
        tunch_frame = tk.Frame(percentage_frame, bg=COLORS['light'])
        tunch_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        tunch_label = tk.Label(tunch_frame, 
                              text="Tunch %:",
                              font=FONTS['body'],
                              fg=COLORS['dark'],
                              bg=COLORS['light'])
        tunch_label.pack(anchor='w')
        
        tunch_entry = tk.Entry(tunch_frame, 
                              font=FONTS['body'],
                              width=15)
        tunch_entry.pack(fill='x', pady=(5, 0))
        self.populate_entry_field(tunch_entry, record[6])  # tunch_percentage
        
        # Wastage percentage
        wastage_frame = tk.Frame(percentage_frame, bg=COLORS['light'])
        wastage_frame.pack(side='left', fill='x', expand=True)
        
        wastage_label = tk.Label(wastage_frame, 
                                text="Wastage %:",
                                font=FONTS['body'],
                                fg=COLORS['dark'],
                                bg=COLORS['light'])
        wastage_label.pack(anchor='w')
        
        wastage_entry = tk.Entry(wastage_frame, 
                                font=FONTS['body'],
                                width=15)
        wastage_entry.pack(fill='x', pady=(5, 0))
        self.populate_entry_field(wastage_entry, record[7])  # wastage_percentage
        
        # Fine Gold (calculated)
        fine_frame = tk.Frame(main_frame, bg=COLORS['light'])
        fine_frame.pack(fill='x', pady=(0, 15))
        
        fine_label = tk.Label(fine_frame, 
                             text="Fine Gold:",
                             font=FONTS['body'],
                             fg=COLORS['dark'],
                             bg=COLORS['light'])
        fine_label.pack(anchor='w')
        
        fine_entry = tk.Entry(fine_frame, 
                             font=FONTS['body'],
                             width=30,
                             state='readonly')
        fine_entry.pack(fill='x', pady=(5, 0))
        fine_entry.config(state='normal')
        self.populate_entry_field(fine_entry, record[8])  # fine_gold
        fine_entry.config(state='readonly')
        
        # Calculation function
        def calculate_values():
            try:
                gross = float(gross_entry.get() or 0)
                less = float(less_entry.get() or 0)
                tunch = float(tunch_entry.get() or 0)
                wastage = float(wastage_entry.get() or 0)
                
                net_weight = gross - less
                fine_gold = (net_weight / 100 * tunch) + (net_weight / 100 * wastage)
                
                net_entry.config(state='normal')
                net_entry.delete(0, tk.END)
                net_entry.insert(0, f"{net_weight:.2f}")
                net_entry.config(state='readonly')
                
                fine_entry.config(state='normal')
                fine_entry.delete(0, tk.END)
                fine_entry.insert(0, f"{fine_gold:.2f}")
                fine_entry.config(state='readonly')
                
            except (ValueError, TypeError):
                pass
        
        # Bind calculation events
        gross_entry.bind('<KeyRelease>', lambda e: calculate_values())
        less_entry.bind('<KeyRelease>', lambda e: calculate_values())
        tunch_entry.bind('<KeyRelease>', lambda e: calculate_values())
        wastage_entry.bind('<KeyRelease>', lambda e: calculate_values())
        
        # Add number validation to all numeric fields
        self.add_number_validation(gross_entry)
        self.add_number_validation(less_entry)
        self.add_number_validation(tunch_entry)
        self.add_number_validation(wastage_entry)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=COLORS['light'])
        button_frame.pack(fill='x', pady=(20, 0))
        
        def save_update():
            """Save the updated purchase record"""
            supplier_text = supplier_combo.get().strip()
            item_text = item_combo.get().strip()
            gross = gross_entry.get().strip()
            less = less_entry.get().strip()
            tunch = tunch_entry.get().strip()
            wastage = wastage_entry.get().strip()
            
            if not all([supplier_text, item_text, gross, less, tunch, wastage]):
                messagebox.showerror("Error", "All fields are required")
                return
            
            try:
                # Get old values for inventory and balance adjustment
                old_query = "SELECT item_id, fine_gold, net_weight, supplier_name FROM sales WHERE ref_id = ?"
                old_values = self.db.execute_query(old_query, (ref_id,))
                if old_values:
                    old_item_id, old_fine_gold, old_net_weight, old_supplier_name = old_values[0]
                else:
                    old_item_id, old_fine_gold, old_net_weight, old_supplier_name = 0, 0, 0, ""
                
                # Extract supplier_id and supplier_name
                supplier_id = int(supplier_text.split(' - ')[0])
                supplier_name = supplier_text.split(' - ')[1]
                
                # Extract item_id
                item_id = int(item_text.split(' - ')[0])
                
                # Calculate values
                net_weight = float(gross) - float(less)
                fine_gold = (net_weight / 100 * float(tunch)) + (net_weight / 100 * float(wastage))
                
                # Update the record
                query = '''
                    UPDATE sales 
                    SET supplier_name = ?, item_id = ?, gross_weight = ?, less_weight = ?, 
                        net_weight = ?, tunch_percentage = ?, wastage_percentage = ?, fine_gold = ?
                    WHERE ref_id = ?
                '''
                self.db.execute_update(query, (
                    supplier_name, item_id, float(gross), float(less),
                    net_weight, float(tunch), float(wastage), fine_gold, ref_id
                ))
                
                # Update item inventory (reverse old purchase, apply new purchase)
                self.update_item_inventory_for_record_update(
                    ref_id, old_fine_gold, old_net_weight, fine_gold, net_weight, 
                    old_item_id, item_id, is_purchase=True
                )
                
                # Update supplier balance (reverse old purchase, apply new purchase)
                old_monetary_value = self.calculate_monetary_value(old_fine_gold)
                new_monetary_value = self.calculate_monetary_value(fine_gold)
                self.update_supplier_balance_for_record_update(
                    ref_id, old_monetary_value, new_monetary_value, old_supplier_name, supplier_name, is_purchase=True
                )
                
                self.show_toast("Purchase record updated successfully!", success=True)
                self.load_unified_data()  # Refresh unified table
                update_modal.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error updating purchase record: {e}")
        
        save_btn = tk.Button(button_frame, 
                            text="Save Update",
                            command=save_update,
                            font=FONTS['body'],
                            bg=COLORS['success'],
                            fg=COLORS['white'],
                            relief='raised',
                            bd=2)
        save_btn.pack(side='right', padx=(10, 0))
        
        cancel_btn = tk.Button(button_frame, 
                              text="Cancel",
                              command=update_modal.destroy,
                              font=FONTS['body'],
                              bg=COLORS['secondary'],
                              fg=COLORS['white'],
                              relief='raised',
                              bd=2)
        cancel_btn.pack(side='right')
    
    def show_inventory_breakdown(self):
        """Show inventory breakdown by gold form and purity"""
        messagebox.showinfo("Info", "Inventory breakdown functionality to be implemented")
    
    # Work order (Karigar Orders) methods - routed to new flow
    def new_work_order(self):
        """Create new karigar order"""
        try:
            self.karigar_orders_manager.show_create_order_modal()
        except Exception as e:
            messagebox.showerror("Error", f"Error opening karigar order modal: {e}")
    
    def update_work_order(self):
        """Mark selected orders as In Progress"""
        self._set_karigar_order_status('in progress')
    
    def complete_work_order(self):
        """Mark selected orders as Completed"""
        self._set_karigar_order_status('completed')
    
    def view_work_order_details(self):
        """Refresh orders table (details modal can be added later)"""
        self.load_karigar_orders_data()
    
    def delete_work_order(self):
        """Delete selected karigar order(s) from table"""
        try:
            selection = self.work_orders_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select order(s) to delete")
                return
            ids = []
            for item in selection:
                vals = self.work_orders_tree.item(item)['values']
                if vals:
                    ids.append(vals[0])
            if not ids:
                return
            if not messagebox.askyesno("Confirm", f"Delete {len(ids)} order(s)?"):
                return
            q = f"DELETE FROM karigar_orders WHERE order_id IN ({','.join(['?']*len(ids))})"
            self.db.execute_update(q, tuple(ids))
            self.load_karigar_orders_data()
            self.show_toast("Order(s) deleted", success=True)
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting order(s): {e}")
    
    # Freelancer methods
    def add_freelancer(self):
        """Add new freelancer"""
        self.freelancer_manager.add_freelancer(self.root)
    
    def edit_freelancer(self):
        """Edit freelancer details"""
        self.freelancer_manager.edit_freelancer(self.root)
    
    def view_freelancer_work_orders(self):
        """View all work orders for a specific freelancer"""
        self.freelancer_manager.view_freelancer_work_orders(self.root)
    
    # Supplier methods
    def add_supplier(self):
        """Add new supplier"""
        self.supplier_manager.add_supplier(self.root)
    
    def edit_supplier(self):
        """Edit supplier details"""
        self.supplier_manager.edit_supplier(self.root)
    
    # Design methods (placeholder)
    

    
    
    # Home tab methods
    def load_home_data(self):
        """Load data for home tab tables"""
        self.load_recent_transactions()
        self.load_pending_orders()
    
    def load_recent_transactions(self):
        """Load today's sales and purchase orders into main table"""
        # Clear existing items
        for item in self.home_main_tree.get_children():
            self.home_main_tree.delete(item)
        
        try:
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Load today's sales and purchase orders
            query = '''
                SELECT 
                    s.ref_id,
                    CASE 
                        WHEN s.ref_id LIKE 'S%' THEN 'Sale'
                        WHEN s.ref_id LIKE 'P%' THEN 'Purchase'
                        ELSE 'Unknown'
                    END as type,
                    s.supplier_name,
                    COALESCE(i.item_name, 'N/A') as item_name,
                    s.gross_weight,
                    s.less_weight,
                    s.net_weight,
                    s.tunch_percentage,
                    s.wastage_percentage,
                    s.fine_gold,
                    strftime('%H:%M', s.sale_date) as time
                FROM sales s
                LEFT JOIN items i ON s.item_id = i.item_id
                WHERE DATE(s.sale_date) = ?
                ORDER BY s.sale_date DESC
            '''
            rows = self.db.execute_query(query, (today,))
            
            for i, row in enumerate(rows):
                tag = 'even' if i % 2 == 0 else 'odd'
                self.home_main_tree.insert('', 'end', values=(
                    row[0],  # Ref ID
                    row[1],  # Type (Sale/Purchase)
                    row[2],  # Supplier
                    row[3],  # Item
                    f"{row[4]:.2f}",  # Gross
                    f"{row[5]:.2f}",  # Less
                    f"{row[6]:.2f}",  # Net
                    f"{row[7]:.1f}",  # Tunch
                    f"{row[8]:.1f}",  # Wastage
                    f"{row[9]:.2f}",  # Fine Gold
                    row[10]  # Time
                ), tags=(tag,))
                
        except Exception as e:
            print(f"Error loading today's orders: {e}")
            # Add sample data if database is empty
            sample_data = [
                ("S110925/001", "Sale", "Sample Supplier", "Ring", "25.50", "2.00", "23.50", "91.6", "2.0", "22.03", "14:30"),
                ("P110925/001", "Purchase", "Gold Supplier", "Chain", "50.00", "1.50", "48.50", "99.9", "1.0", "48.99", "15:45"),
                ("S110925/002", "Sale", "Another Supplier", "Earring", "15.75", "0.75", "15.00", "83.3", "1.5", "12.72", "16:20")
            ]
            
            for i, data in enumerate(sample_data):
                tag = 'even' if i % 2 == 0 else 'odd'
                self.home_main_tree.insert('', 'end', values=data, tags=(tag,))
    
    def load_pending_orders(self):
        """Load pending Raini orders from database"""
        # Check if home_pending_tree exists
        if not hasattr(self, 'home_pending_tree'):
            print("home_pending_tree not found, skipping load_pending_orders")
            return
            
        # Clear existing items
        for item in self.home_pending_tree.get_children():
            self.home_pending_tree.delete(item)
        
        try:
            print("Loading pending Raini orders from database...")
            
            # First, check if raini_orders table exists
            table_check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='raini_orders'"
            table_exists = self.db.execute_query(table_check_query)
            
            if not table_exists:
                print("raini_orders table does not exist")
                return
            
            # Load pending Raini orders
            query = '''
                SELECT 
                    raini_id as id,
                    total_weight as weight
                FROM raini_orders
                WHERE status = 'Pending'
                ORDER BY created_date ASC
                LIMIT 15
            '''
            rows = self.db.execute_query(query)
            print(f"Found {len(rows)} pending Raini orders")
            
            # If no pending orders found, show empty table
            if len(rows) == 0:
                print("No pending orders found")
            
            # Display the data
            for i, row in enumerate(rows):
                tag = 'even' if i % 2 == 0 else 'odd'
                self.home_pending_tree.insert('', 'end', values=(
                    row[0], f"{row[1]:.2f}"
                ), tags=(tag,))
                
        except Exception as e:
            print(f"Error loading pending Raini orders: {e}")
    
    def on_home_pending_double_click(self, event):
        """Handle double-click on home pending orders table"""
        selection = self.home_pending_tree.selection()
        if not selection:
            return
            
        item = self.home_pending_tree.item(selection[0])
        values = item['values']
        
        if len(values) < 2:
            return
            
        order_id = values[0]
        
        # Get the full order details from database
        try:
            query = '''
                SELECT 
                    raini_id,
                    purity_percentage,
                    pure_gold_weight,
                    impurities_weight,
                    copper_weight,
                    silver_weight,
                    total_weight,
                    created_date,
                    status
                FROM raini_orders
                WHERE raini_id = ? AND status = 'Pending'
            '''
            order_details = self.db.execute_query(query, (order_id,))
            
            if order_details:
                order_values = order_details[0]
                self.show_complete_raini_modal(order_id, order_values)
            else:
                messagebox.showerror("Error", "Order not found or already completed")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading order details: {e}")
    
    def create_sale_entry(self):
        """Create new sale entry"""
        self.add_sale()
    
    def create_purchase_entry(self):
        """Create new purchase entry"""
        self.add_purchase()
    
    def create_issue_entry(self):
        """Create new issue entry"""
        self.new_work_order()
    
    def create_received_entry(self):
        """Create new received entry"""
        self.complete_work_order()
    
    # Raini Inventory methods
    def add_raini_order(self):
        """Open modal to add new Raini order"""
        self.show_raini_order_modal()
    
    def complete_raini_order(self):
        """Complete a Raini order"""
        # Get selected item
        selected_item = self.raini_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a Raini order to complete")
            return
        
        # Get order details
        item_values = self.raini_tree.item(selected_item[0])['values']
        order_id = item_values[0]
        status = item_values[8]  # Status is the last column
        
        if status == "Completed":
            messagebox.showinfo("Info", "This order is already completed")
            return
        
        # Show completion modal
        self.show_complete_raini_modal(order_id, item_values)
    
    def update_raini_order(self):
        """Update existing Raini order"""
        messagebox.showinfo("Info", "Update Raini order functionality to be implemented")
    
    def delete_raini_order(self):
        """Delete selected Raini order(s)"""
        try:
            if not hasattr(self, 'raini_tree'):
                messagebox.showwarning("Warning", "Raini table is not available")
                return
            selection = self.raini_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select order(s) to delete")
                return
            ids = []
            for it in selection:
                vals = self.raini_tree.item(it).get('values') or []
                if vals:
                    try:
                        ids.append(int(vals[0]))
                    except Exception:
                        ids.append(vals[0])
            if not ids:
                return
            if not messagebox.askyesno("Confirm Delete", f"Delete {len(ids)} Raini order(s)? This cannot be undone."):
                return
            placeholders = ','.join(['?'] * len(ids))
            # Delete child details if any (best-effort)
            try:
                # If a detail table exists, clear it first to avoid FK issues
                detail_exists = False
                try:
                    chk = self.db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='raini_order_items'")
                    detail_exists = bool(chk)
                except Exception:
                    detail_exists = False
                if detail_exists:
                    self.db.execute_update(f"DELETE FROM raini_order_items WHERE raini_id IN ({placeholders})", tuple(ids))
            except Exception:
                pass
            try:
                self.db.execute_update(f"DELETE FROM raini_orders WHERE raini_id IN ({placeholders})", tuple(ids))
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting Raini order(s): {e}")
                return
            self.load_raini_data()
            try:
                self.load_home_data()
            except Exception:
                pass
            self.show_toast("Selected Raini order(s) deleted", success=True)
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting Raini order(s): {e}")
    
    def load_raini_data(self):
        """Load Raini inventory data"""
        # Check if raini_tree exists (tab might not be created yet)
        if not hasattr(self, 'raini_tree'):
            print("raini_tree not found, skipping load_raini_data")
            return
            
        print("Loading Raini data from database...")
        
        # Clear existing items
        for item in self.raini_tree.get_children():
            self.raini_tree.delete(item)
        
        try:
            # First check if raini_orders table exists
            table_check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='raini_orders'"
            table_exists = self.db.execute_query(table_check_query)
            
            if not table_exists:
                print("raini_orders table does not exist, loading sample data")
                self._load_sample_raini_data()
                return
            
            # Load Raini orders from database
            query = '''
                SELECT 
                    raini_id,
                    purity_percentage,
                    pure_gold_weight,
                    impurities_weight,
                    copper_weight,
                    silver_weight,
                    total_weight,
                    actual_weight,
                    created_date,
                    status
                FROM raini_orders
                ORDER BY created_date DESC
            '''
            rows = self.db.execute_query(query)
            print(f"Found {len(rows)} Raini orders in database")
            
            if len(rows) > 0:
                for i, row in enumerate(rows):
                    tag = 'even' if i % 2 == 0 else 'odd'
                    actual_weight_display = f"{row[7]:.3f}" if row[7] is not None else "N/A"
                    self.raini_tree.insert('', 'end', values=(
                        row[0], f"{row[1]:.2f}", f"{row[2]:.3f}", 
                        f"{row[3]:.3f}", f"{row[4]:.3f}", f"{row[5]:.3f}", 
                        f"{row[6]:.3f}", actual_weight_display, row[8], row[9]
                    ), tags=(tag,))
            else:
                # Show empty state instead of injecting sample rows to avoid confusion after deletions
                print("No Raini orders found in database")
                
        except Exception as e:
            print(f"Error loading Raini data: {e}")
            # Do not load sample rows on error; leave table empty to avoid confusion
        
        # Update total Raini gold display
        self.update_total_raini_display()
    
    def _load_sample_raini_data(self):
        """Load sample Raini data when database is empty or has errors"""
        print("Loading sample Raini data...")
        sample_data = [
            (1, "75.00", "100.00", "33.33", "16.67", "8.33", "133.33", "N/A", "2024-01-15", "Pending"),
            (2, "91.60", "50.00", "4.58", "2.29", "1.15", "54.58", "N/A", "2024-01-14", "Pending"),
            (3, "99.50", "25.00", "0.13", "0.07", "0.03", "25.13", "25.50", "2024-01-13", "Completed")
        ]
        for i, row in enumerate(sample_data):
            tag = 'even' if i % 2 == 0 else 'odd'
            self.raini_tree.insert('', 'end', values=row, tags=(tag,))
    
    def update_total_raini_display(self):
        """Update the total Raini gold display and pending orders info"""
        # Check if labels exist (tab might not be created yet)
        if not hasattr(self, 'total_raini_label') or not hasattr(self, 'pending_orders_label'):
            return
            
        try:
            # Get completed Raini gold total
            completed_query = "SELECT SUM(actual_weight) FROM raini_orders WHERE status = 'Completed'"
            completed_result = self.db.execute_query(completed_query)
            total_raini = completed_result[0][0] if completed_result and completed_result[0][0] else 0
            self.total_raini_label.config(text=f"Total Raini Gold: {total_raini:.2f} grams")
            
            # Get pending orders count and total weight
            pending_query = '''
                SELECT COUNT(*), SUM(total_weight) 
                FROM raini_orders 
                WHERE status = 'Pending'
            '''
            pending_result = self.db.execute_query(pending_query)
            pending_count = pending_result[0][0] if pending_result and pending_result[0][0] else 0
            pending_weight = pending_result[0][1] if pending_result and pending_result[0][1] else 0
            
            self.pending_orders_label.config(text=f"Pending Orders: {pending_count} ({pending_weight:.2f}g)")
            
        except Exception as e:
            print(f"Error updating Raini display: {e}")
            self.total_raini_label.config(text="Total Raini Gold: 0.00 grams")
            self.pending_orders_label.config(text="Pending Orders: 0 (0.00g)")
    
    def show_raini_order_modal(self):
        """Show modal for creating new Raini order"""
        modal = tk.Toplevel(self.root)
        modal.title("New Raini Order")
        modal.geometry("600x550")
        modal.configure(bg=COLORS['light'])
        modal.resizable(False, False)
        
        # Center the modal
        self.center_modal(modal, 600, 550)
        
        # Make modal modal
        modal.transient(self.root)
        modal.grab_set()
        
        # Main frame
        main_frame = tk.Frame(modal, bg=COLORS['light'], padx=20, pady=20)
        main_frame.pack(fill='both', expand=True, pady=(0, 0))  # Remove bottom padding to give more space
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="New Raini Order",
                              font=FONTS['heading'],
                              fg=COLORS['primary'],
                              bg=COLORS['light'])
        title_label.pack(pady=(0, 20))
        
        # Purity selection frame with two columns
        purity_frame = tk.Frame(main_frame, bg=COLORS['light'])
        purity_frame.pack(fill='x', pady=(0, 15))
        
        # Left column - Purity dropdown (half width)
        left_purity_frame = tk.Frame(purity_frame, bg=COLORS['light'])
        left_purity_frame.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        purity_label = tk.Label(left_purity_frame, 
                               text="Purity:",
                               font=FONTS['subheading'],
                               fg=COLORS['dark'],
                               bg=COLORS['light'])
        purity_label.pack(anchor='w')
        
        # Purity dropdown
        purity_var = tk.StringVar()
        purity_combo = ttk.Combobox(left_purity_frame, 
                                   textvariable=purity_var,
                                   values=["Custom", "75%", "83.3%", "91.6%", "99.5%", "99.99%"],
                                   state="readonly",
                                   font=FONTS['body'])
        purity_combo.pack(fill='x', pady=(5, 0))
        purity_combo.set("75%")  # Default selection
        
        # Right column - Custom purity field (half width, initially hidden)
        right_purity_frame = tk.Frame(purity_frame, bg=COLORS['light'])
        # Don't pack initially - will be shown when Custom is selected
        
        custom_purity_label = tk.Label(right_purity_frame, 
                                      text="Enter Purity %:",
                                      font=FONTS['subheading'],
                                      fg=COLORS['accent'],
                                      bg=COLORS['light'])
        custom_purity_label.pack(anchor='w')
        
        custom_purity_entry = tk.Entry(right_purity_frame, 
                                      font=FONTS['body'],
                                      relief='solid',
                                      bd=2)
        custom_purity_entry.pack(fill='x', pady=(5, 0))
        
        # Weight input frame
        weight_frame = tk.Frame(main_frame, bg=COLORS['light'])
        weight_frame.pack(fill='x', pady=(0, 15))
        
        weight_label = tk.Label(weight_frame, 
                               text="Pure Gold Weight (grams):",
                               font=FONTS['subheading'],
                               fg=COLORS['dark'],
                               bg=COLORS['light'])
        weight_label.pack(anchor='w')
        
        weight_entry = tk.Entry(weight_frame, 
                               font=FONTS['body'],
                               width=20)
        weight_entry.pack(fill='x', pady=(5, 0))
        
        # Impurities composition frame
        impurities_frame = tk.Frame(main_frame, bg=COLORS['light'])
        impurities_frame.pack(fill='x', pady=(0, 15))
        
        impurities_title = tk.Label(impurities_frame, 
                                   text="Impurities Composition:",
                                   font=FONTS['subheading'],
                                   fg=COLORS['primary'],
                                   bg=COLORS['light'])
        impurities_title.pack(anchor='w', pady=(0, 10))
        
        # Copper and Silver input frame (side by side)
        composition_frame = tk.Frame(impurities_frame, bg=COLORS['light'])
        composition_frame.pack(fill='x')
        
        # Copper frame (left)
        copper_frame = tk.Frame(composition_frame, bg=COLORS['light'])
        copper_frame.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        copper_label = tk.Label(copper_frame, 
                               text="Copper %:",
                               font=FONTS['body'],
                               fg=COLORS['dark'],
                               bg=COLORS['light'])
        copper_label.pack(anchor='w')
        
        copper_var = tk.StringVar()
        silver_var = tk.StringVar()
        # initialize defaults via variables to avoid race conditions
        copper_var.set("0.00")
        silver_var.set("100.00")
        
        copper_entry = tk.Entry(copper_frame, 
                               font=FONTS['body'],
                               relief='solid',
                               bd=2,
                               textvariable=copper_var)
        copper_entry.pack(fill='x', pady=(5, 0))
        
        copper_weight_label = tk.Label(copper_frame, 
                                      text="Weight: 0.00g",
                                      font=FONTS['small'],
                                      fg=COLORS['info'],
                                      bg=COLORS['light'])
        copper_weight_label.pack(anchor='w', pady=(2, 0))
        
        # Silver frame (right)
        silver_frame = tk.Frame(composition_frame, bg=COLORS['light'])
        silver_frame.pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        silver_label = tk.Label(silver_frame, 
                               text="Silver %:",
                               font=FONTS['body'],
                               fg=COLORS['dark'],
                               bg=COLORS['light'])
        silver_label.pack(anchor='w')
        
        silver_entry = tk.Entry(silver_frame, 
                               font=FONTS['body'],
                               relief='solid',
                               bd=2,
                               textvariable=silver_var)
        silver_entry.pack(fill='x', pady=(5, 0))
        
        silver_weight_label = tk.Label(silver_frame, 
                                      text="Weight: 0.00g",
                                      font=FONTS['small'],
                                      fg=COLORS['info'],
                                      bg=COLORS['light'])
        silver_weight_label.pack(anchor='w', pady=(2, 0))

        # Keep copper% + silver% = 100 helpers
        def _as_float(text):
            try:
                t = (text or '').strip().replace('%', '')
                if t == '':
                    return 0.0
                val = float(t)
                try:
                    print(f"[RainiDebug] _as_float input='{text}' parsed={val}")
                except Exception:
                    pass
                return val
            except Exception:
                try:
                    print(f"[RainiDebug] _as_float failed for input='{text}', defaulting 0.0")
                except Exception:
                    pass
                return 0.0

        def _clamp_pct(v: float) -> float:
            if v < 0:
                return 0.0
            if v > 100:
                return 100.0
            return v

        updating_pair = { 'active': False }

        def _set_entry_value(var: tk.StringVar, value: str):
            try:
                # Defer to next loop turn to avoid race with focus-out handlers
                def _apply():
                    try:
                        updating_pair['active'] = True
                        var.set(value)
                    finally:
                        updating_pair['active'] = False
                copper_entry.after(0, _apply)
            except Exception:
                try:
                    updating_pair['active'] = True
                    var.set(value)
                finally:
                    updating_pair['active'] = False

        def _auto_fill_counterpart(changed: str):
            try:
                if changed == 'copper':
                    raw = copper_entry.get()
                    c = _clamp_pct(_as_float(raw))
                    # If user left it empty, normalize to 0.00
                    if (raw or '').strip() == '':
                        c = 0.0
                    s = _clamp_pct(100.0 - c)
                    try:
                        print(f"[RainiDebug] on_copper_blur raw='{raw}' -> c={c:.2f}, s={s:.2f}")
                    except Exception:
                        pass
                    _set_entry_value(silver_var, f"{s:.2f}")
                    _set_entry_value(copper_var, f"{c:.2f}")
                else:
                    raw = silver_entry.get()
                    s = _clamp_pct(_as_float(raw))
                    if (raw or '').strip() == '':
                        s = 0.0
                    c = _clamp_pct(100.0 - s)
                    try:
                        print(f"[RainiDebug] on_silver_blur raw='{raw}' -> s={s:.2f}, c={c:.2f}")
                    except Exception:
                        pass
                    _set_entry_value(copper_var, f"{c:.2f}")
                    _set_entry_value(silver_var, f"{s:.2f}")
                calculate_impurities()
            except Exception:
                try:
                    print(f"[RainiDebug] _auto_fill_counterpart exception (changed={changed})", flush=True)
                except Exception:
                    pass
                pass

        def on_copper_blur(_e=None):
            try:
                print(f"[RainiDebug] on_copper_blur start focus={modal.focus_get()}")
            except Exception:
                pass
            _auto_fill_counterpart('copper')
            try:
                # Defer read to allow after(0) writers to complete
                def _log_after():
                    try:
                        print(f"[RainiDebug] on_copper_blur end copper='{copper_entry.get()}', silver='{silver_entry.get()}'")
                    except Exception:
                        pass
                modal.after(0, _log_after)
            except Exception:
                pass

        def on_silver_blur(_e=None):
            try:
                print(f"[RainiDebug] on_silver_blur start focus={modal.focus_get()}")
            except Exception:
                pass
            _auto_fill_counterpart('silver')
            try:
                def _log_after():
                    try:
                        print(f"[RainiDebug] on_silver_blur end copper='{copper_entry.get()}', silver='{silver_entry.get()}'")
                    except Exception:
                        pass
                modal.after(0, _log_after)
            except Exception:
                pass

        # Default both if both are empty at start
        try:
            print("[RainiDebug] Initialized defaults copper=0.00, silver=100.00 (via vars)")
        except Exception:
            pass
        # Bind: when user finishes editing one, auto-fill the other to sum 100
        copper_entry.bind('<FocusOut>', on_copper_blur)
        silver_entry.bind('<FocusOut>', on_silver_blur)
        # Also react on Enter key
        copper_entry.bind('<Return>', on_copper_blur)
        silver_entry.bind('<Return>', on_silver_blur)
        
        # Calculation results frame
        calc_frame = tk.Frame(main_frame, bg=COLORS['white'], relief='raised', bd=2)
        calc_frame.pack(fill='x', pady=(0, 15))
        
        calc_title = tk.Label(calc_frame, 
                             text="Calculation Results:",
                             font=FONTS['subheading'],
                             fg=COLORS['primary'],
                             bg=COLORS['white'])
        calc_title.pack(pady=(10, 5))
        
        # Results labels
        self.impurities_label = tk.Label(calc_frame, 
                                        text="Impurities needed: 0.00 grams",
                                        font=FONTS['body'],
                                        fg=COLORS['dark'],
                                        bg=COLORS['white'])
        self.impurities_label.pack()
        
        self.total_weight_label = tk.Label(calc_frame, 
                                          text="Total weight: 0.00 grams",
                                          font=FONTS['body'],
                                          fg=COLORS['dark'],
                                          bg=COLORS['white'])
        self.total_weight_label.pack(pady=(0, 10))
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg=COLORS['light'])
        buttons_frame.pack(fill='x', pady=(20, 0))
        # Container aligned to the right to keep buttons bottom-right
        right_btns = tk.Frame(buttons_frame, bg=COLORS['light'])
        right_btns.pack(side='right')
        
        def toggle_custom_purity(event=None):
            """Toggle custom purity field visibility"""
            if purity_var.get() == "Custom":
                right_purity_frame.pack(side='right', fill='x', expand=True, padx=(5, 0))
                custom_purity_entry.focus()  # Focus on the custom entry field
            else:
                right_purity_frame.pack_forget()
                custom_purity_entry.delete(0, tk.END)  # Clear the custom field
            calculate_impurities()
        
        def calculate_impurities(event=None):
            """Calculate impurities needed and composition weights"""
            try:
                pure_gold = float(weight_entry.get()) if weight_entry.get() else 0
                purity_text = purity_var.get()
                
                if purity_text == "Custom":
                    if not custom_purity_entry.get().strip():
                        # If custom is selected but no value entered, show 0
                        purity = 0
                    else:
                        purity = float(custom_purity_entry.get())
                else:
                    purity = float(purity_text.replace('%', ''))
                
                # Get copper and silver percentages
                copper_percent = float(copper_var.get()) if copper_var.get() else 0
                silver_percent = float(silver_var.get()) if silver_var.get() else 0
                try:
                    print(f"[RainiDebug] save pre-validate copper={copper_percent}, silver={silver_percent}, sum={copper_percent+silver_percent}")
                except Exception:
                    pass
                
                if pure_gold > 0 and purity > 0 and purity <= 100:
                    # Calculate impurities needed
                    # If we have pure_gold grams of 100% gold and want purity% gold
                    # Total weight = pure_gold / (purity / 100)
                    # Impurities = Total weight - pure_gold
                    total_weight = pure_gold / (purity / 100)
                    impurities = total_weight - pure_gold
                    
                    # Calculate copper and silver weights
                    copper_weight = (impurities * copper_percent) / 100 if copper_percent > 0 else 0
                    silver_weight = (impurities * silver_percent) / 100 if silver_percent > 0 else 0
                    
                    # Update main calculation labels
                    self.impurities_label.config(text=f"Impurities needed: {impurities:.2f} grams")
                    self.total_weight_label.config(text=f"Total weight: {total_weight:.2f} grams")
                    
                    # Update composition weight labels
                    copper_weight_label.config(text=f"Weight: {copper_weight:.2f}g")
                    silver_weight_label.config(text=f"Weight: {silver_weight:.2f}g")
                else:
                    self.impurities_label.config(text="Impurities needed: 0.00 grams")
                    self.total_weight_label.config(text="Total weight: 0.00 grams")
                    copper_weight_label.config(text="Weight: 0.00g")
                    silver_weight_label.config(text="Weight: 0.00g")
            except ValueError:
                self.impurities_label.config(text="Impurities needed: 0.00 grams")
                self.total_weight_label.config(text="Total weight: 0.00 grams")
                copper_weight_label.config(text="Weight: 0.00g")
                silver_weight_label.config(text="Weight: 0.00g")
        
        def save_raini_order():
            """Save the Raini order"""
            try:
                pure_gold = float(weight_entry.get()) if weight_entry.get() else 0
                purity_text = purity_var.get()
                
                if purity_text == "Custom":
                    if not custom_purity_entry.get().strip():
                        messagebox.showerror("Error", "Please enter a custom purity percentage")
                        return
                    purity = float(custom_purity_entry.get())
                else:
                    purity = float(purity_text.replace('%', ''))
                
                if pure_gold <= 0:
                    messagebox.showerror("Error", "Please enter a valid pure gold weight")
                    return
                
                if purity <= 0 or purity > 100:
                    messagebox.showerror("Error", "Please enter a valid purity percentage (0-100)")
                    return
                
                # Get copper and silver percentages
                copper_percent = float(copper_entry.get()) if copper_entry.get() else 0
                silver_percent = float(silver_entry.get()) if silver_entry.get() else 0

                # Enforce copper% + silver% = 100 before save
                if abs((copper_percent + silver_percent) - 100.0) > 1e-6:
                    # Try auto-correct once using current field focus as hint
                    try:
                        widget = modal.focus_get()
                        if widget is copper_entry:
                            on_copper_blur()
                        elif widget is silver_entry:
                            on_silver_blur()
                    except Exception:
                        pass
                    # Re-read and validate again
                    copper_percent = float(copper_var.get()) if copper_var.get() else 0
                    silver_percent = float(silver_var.get()) if silver_var.get() else 0
                    try:
                        print(f"[RainiDebug] save post-autofill copper={copper_percent}, silver={silver_percent}, sum={copper_percent+silver_percent}")
                    except Exception:
                        pass
                    if abs((copper_percent + silver_percent) - 100.0) > 1e-6:
                        messagebox.showerror("Error", "Copper% + Silver% must total 100%")
                        return
                
                # Calculate final values
                total_weight = pure_gold / (purity / 100)
                impurities = total_weight - pure_gold
                copper_weight = (impurities * copper_percent) / 100 if copper_percent > 0 else 0
                silver_weight = (impurities * silver_percent) / 100 if silver_percent > 0 else 0
                
                # Save to database
                query = '''
                    INSERT INTO raini_orders 
                    (purity_percentage, pure_gold_weight, impurities_weight, total_weight, 
                     copper_percentage, copper_weight, silver_percentage, silver_weight, 
                     created_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), 'Pending')
                '''
                self.db.execute_update(query, (purity, pure_gold, impurities, total_weight, 
                                            copper_percent, copper_weight, silver_percent, silver_weight))
                
                self.show_toast(f"Raini order created successfully! • Pure Gold: {pure_gold:.2f}g • Purity: {purity:.2f}% • Expected Weight: {total_weight:.2f}g", success=True)
                
                # Refresh data and close modal
                self.load_raini_data()
                self.load_home_data()  # Refresh home page data
                modal.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving Raini order: {e}")
        
        # Bind events
        purity_combo.bind('<<ComboboxSelected>>', toggle_custom_purity)
        weight_entry.bind('<KeyRelease>', calculate_impurities)
        custom_purity_entry.bind('<KeyRelease>', calculate_impurities)
        copper_entry.bind('<KeyRelease>', calculate_impurities)
        silver_entry.bind('<KeyRelease>', calculate_impurities)
        
        # Add number validation to all numeric fields
        self.add_number_validation(weight_entry)
        self.add_number_validation(custom_purity_entry)
        self.add_number_validation(copper_entry)
        self.add_number_validation(silver_entry)
        
        # Buttons
        save_btn = tk.Button(buttons_frame, 
                            text="Save Order",
                            command=save_raini_order,
                            bg=COLORS['success'],
                            fg=COLORS['white'],
                            font=FONTS['button'],
                            relief='raised',
                            bd=2,
                            cursor='hand2',
                            width=15)
        save_btn.pack(side='left', padx=(0, 10))
        
        cancel_btn = tk.Button(buttons_frame, 
                              text="Cancel",
                              command=modal.destroy,
                              bg=COLORS['accent'],
                              fg=COLORS['white'],
                              font=FONTS['button'],
                              relief='raised',
                              bd=2,
                              cursor='hand2',
                              width=15)
        cancel_btn.pack(side='left')
    
    def show_complete_raini_modal(self, order_id, order_values):
        """Show modal for completing Raini order"""
        modal = tk.Toplevel(self.root)
        modal.title("Complete Raini Order")
        modal.geometry("500x450")  # Increased height to accommodate buttons
        modal.configure(bg=COLORS['light'])
        modal.resizable(False, False)
        
        # Center the modal
        self.center_modal(modal, 500, 450)
        
        # Make modal modal
        modal.transient(self.root)
        modal.grab_set()

        # Add keyboard shortcuts for Complete Raini Order modal
        modal.bind('<Control-s>', lambda _e: complete_order())
        modal.bind('<Control-d>', lambda _e: complete_order())  # Ctrl+D for delete/save
        
        # Main frame
        main_frame = tk.Frame(modal, bg=COLORS['light'], padx=20, pady=20)
        main_frame.pack(fill='both', expand=True, pady=(0, 0))  # Remove bottom padding to give more space
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="Complete Raini Order",
                              font=FONTS['heading'],
                              fg=COLORS['primary'],
                              bg=COLORS['light'])
        title_label.pack(pady=(0, 20))
        
        # Order details frame
        details_frame = tk.Frame(main_frame, bg=COLORS['white'], relief='raised', bd=2)
        details_frame.pack(fill='x', pady=(0, 20))
        
        details_title = tk.Label(details_frame, 
                                text="Order Details:",
                                font=FONTS['subheading'],
                                fg=COLORS['primary'],
                                bg=COLORS['white'])
        details_title.pack(pady=(10, 5))
        
        # Order details labels
        details_text = f"""Order ID: {order_id}
Purity: {order_values[1]}%
Pure Gold: {order_values[2]}g
Impurities: {order_values[3]}g
Copper: {order_values[4]}g
Silver: {order_values[5]}g
Expected Total: {order_values[6]}g"""
        
        details_label = tk.Label(details_frame, 
                                text=details_text,
                                font=FONTS['body'],
                                fg=COLORS['dark'],
                                bg=COLORS['white'],
                                justify='left')
        details_label.pack(pady=(0, 10))
        
        # Actual weight input frame
        weight_frame = tk.Frame(main_frame, bg=COLORS['light'])
        weight_frame.pack(fill='x', pady=(0, 10))  # Reduced padding to give more space for buttons
        
        weight_label = tk.Label(weight_frame, 
                               text="Actual Weight of Raini (grams):",
                               font=FONTS['subheading'],
                               fg=COLORS['dark'],
                               bg=COLORS['light'])
        weight_label.pack(anchor='w')
        
        weight_entry = tk.Entry(weight_frame, 
                               font=FONTS['body'],
                               width=20)
        weight_entry.pack(fill='x', pady=(5, 0))
        
        # Add number validation to weight entry
        self.add_number_validation(weight_entry)
        
        def complete_order():
            """Complete the Raini order"""
            try:
                actual_weight = float(weight_entry.get()) if weight_entry.get() else 0
                
                if actual_weight <= 0:
                    messagebox.showerror("Error", "Please enter a valid actual weight")
                    return
                
                # Update order status and actual weight
                query = '''
                    UPDATE raini_orders 
                    SET status = 'Completed', actual_weight = ?
                    WHERE raini_id = ?
                '''
                self.db.execute_update(query, (actual_weight, order_id))
                
                # Auto-create or update Raini item based on purity
                try:
                    # Purity percentage is at index 1 in order_values for both sources
                    purity_val = 0.0
                    try:
                        purity_val = float(order_values[1])
                    except Exception:
                        purity_val = 0.0
                    # Build item name: Raini (75) for 75.0, or Raini (91.6) for fractional
                    if int(purity_val) == purity_val:
                        purity_label = f"{int(purity_val)}"
                    else:
                        purity_label = (f"{purity_val:.2f}").rstrip('0').rstrip('.')
                    item_name = f"Raini ({purity_label})"
                    fine_to_add = actual_weight * (purity_val / 100.0)
                    net_to_add = actual_weight
                    # Find existing item
                    existing = None
                    try:
                        existing = self.db.execute_query(
                            "SELECT item_id FROM items WHERE item_name = ? LIMIT 1",
                            (item_name,)
                        )
                    except Exception:
                        existing = None
                    if existing and len(existing) > 0:
                        item_id = existing[0][0]
                        # Update existing inventory
                        try:
                            self.db.execute_update(
                                """
                                UPDATE items
                                SET fine_weight = COALESCE(fine_weight, 0) + ?,
                                    net_weight = COALESCE(net_weight, 0) + ?
                                WHERE item_id = ?
                                """,
                                (fine_to_add, net_to_add, item_id)
                            )
                        except Exception:
                            pass
                    else:
                        # Insert new item record
                        from datetime import datetime as _dt
                        created_ts = _dt.now().strftime('%Y-%m-%d %H:%M:%S')
                        description = f"Raini output {purity_label}%"
                        try:
                            self.db.execute_update(
                                """
                                INSERT INTO items (item_name, item_code, category, description, fine_weight, net_weight, is_active, created_date)
                                VALUES (?, NULL, 'Raini', ?, ?, ?, 1, ?)
                                """,
                                (item_name, description, fine_to_add, net_to_add, created_ts)
                            )
                        except Exception:
                            # Fallback: try minimal insert
                            try:
                                self.db.execute_update(
                                    "INSERT INTO items (item_name, fine_weight, net_weight) VALUES (?, ?, ?)",
                                    (item_name, fine_to_add, net_to_add)
                                )
                            except Exception:
                                pass
                    # Refresh items view after change
                    try:
                        self.load_items_data()
                    except Exception:
                        pass
                except Exception as raini_item_err:
                    # Non-fatal: log error but continue
                    try:
                        print(f"Error updating Raini item inventory: {raini_item_err}")
                    except Exception:
                        pass

                self.show_toast(f"Raini order completed successfully! • Order ID: {order_id} • Actual Weight: {actual_weight:.3f}g", success=True)
                
                # Refresh data and close modal
                self.load_raini_data()
                self.load_home_data()  # Refresh home page data
                modal.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid numeric value")
            except Exception as e:
                messagebox.showerror("Error", f"Error completing order: {e}")
        
        # Buttons frame (use same layout as other modals)
        buttons_frame = tk.Frame(main_frame, bg=COLORS['light'])
        buttons_frame.pack(fill='x', pady=(10, 0))  # Reduced padding to give more space
        # Container aligned to the right to keep buttons bottom-right
        right_btns = tk.Frame(buttons_frame, bg=COLORS['light'])
        right_btns.pack(side='right')
        # Debug: check if right_btns frame is being created
        try:
            print(f"[RainiDebug] right_btns created: {right_btns}")
        except Exception:
            pass

        # Buttons (thicker and properly styled)
        complete_btn = self.create_beautiful_button(right_btns, "💾 Complete Order", complete_order, 'success', 18)
        complete_btn.pack(side='right', padx=(0, 8), pady=6, ipady=8)

        cancel_btn = self.create_beautiful_button(right_btns, "❌ Cancel", modal.destroy, 'secondary', 18)
        cancel_btn.pack(side='right', padx=(8, 0), pady=6, ipady=8)


    def apply_unified_filters(self):
        """Apply filters to the unified table"""
        supplier = self.supplier_filter_var.get() if hasattr(self, 'supplier_filter_var') else None
        from_date = self.from_date_var.get() if hasattr(self, 'from_date_var') else None
        to_date = self.to_date_var.get() if hasattr(self, 'to_date_var') else None

        self.load_unified_data(supplier_filter=supplier, from_date=from_date, to_date=to_date)

    def clear_unified_filters(self):
        """Clear all filters and reload the table"""
        # Reset filter variables
        if hasattr(self, 'supplier_filter_var'):
            self.supplier_filter_var.set('All')
        if hasattr(self, 'from_date_var'):
            self.from_date_var.set('')
        if hasattr(self, 'to_date_var'):
            self.to_date_var.set('')

        # Reload data without filters
        self.load_unified_data()

    def show_date_picker(self, date_var, entry_widget):
        """Show a simple calendar popup for date selection"""
        from datetime import datetime, timedelta

        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Select Date")
        popup.geometry("300x350")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        # Center the popup relative to main window
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 175
        popup.geometry(f"+{x}+{y}")

        # Get current date or use today's date
        try:
            current_date = datetime.strptime(date_var.get(), "%Y-%m-%d") if date_var.get() else datetime.now()
        except:
            current_date = datetime.now()

        selected_date = [current_date]  # Use list to make it mutable

        # Month/Year header
        header_frame = tk.Frame(popup, bg=COLORS['primary'])
        header_frame.pack(fill='x', padx=10, pady=10)

        # Navigation buttons
        nav_frame = tk.Frame(header_frame, bg=COLORS['primary'])
        nav_frame.pack()

        prev_btn = tk.Button(nav_frame, text="◀", command=lambda: change_month(-1),
                           bg=COLORS['primary'], fg='white', font=('Arial', 12, 'bold'),
                           relief='flat', cursor='hand2')
        prev_btn.pack(side='left', padx=10)

        def change_month(delta):
            # More reliable month navigation
            current_date = selected_date[0]

            # Calculate new month and year
            new_month = current_date.month + delta
            new_year = current_date.year

            # Handle year boundaries
            if new_month < 1:
                new_month = 12
                new_year -= 1
            elif new_month > 12:
                new_month = 1
                new_year += 1

            # Create new date with 1st day of new month
            try:
                new_date = current_date.replace(year=new_year, month=new_month, day=1)
                selected_date[0] = new_date
                update_calendar()
            except ValueError:
                # Handle edge cases (like Feb 29 in non-leap years)
                # Try the last day of the target month
                if new_month == 12:
                    new_date = current_date.replace(year=new_year, month=new_month, day=31)
                else:
                    new_date = current_date.replace(year=new_year, month=new_month+1, day=1) - timedelta(days=1)
                selected_date[0] = new_date.replace(day=1)
                update_calendar()

        def update_calendar():
            # Clear existing calendar
            for widget in calendar_frame.winfo_children():
                widget.destroy()

            # Update month/year label
            month_year_label.config(text=selected_date[0].strftime("%B %Y"))

            # Get calendar data
            import calendar
            cal = calendar.monthcalendar(selected_date[0].year, selected_date[0].month)

            # Day headers
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for i, day in enumerate(days):
                day_label = tk.Label(calendar_frame, text=day, font=('Arial', 10, 'bold'),
                                   bg=COLORS['light'], fg=COLORS['dark'])
                day_label.grid(row=0, column=i, padx=2, pady=2, sticky='nsew')

            # Calendar days
            for week_num, week in enumerate(cal):
                for day_num, day in enumerate(week):
                    if day != 0:
                        day_btn = tk.Button(calendar_frame,
                                          text=str(day),
                                          command=lambda d=day: select_date(d),
                                          font=('Arial', 10),
                                          bg=COLORS['white'],
                                          fg=COLORS['dark'],
                                          relief='raised',
                                          bd=1,
                                          cursor='hand2')
                        day_btn.grid(row=week_num+1, column=day_num, padx=1, pady=1, sticky='nsew')

                        # Highlight current day
                        if (day == datetime.now().day and
                            selected_date[0].month == datetime.now().month and
                            selected_date[0].year == datetime.now().year):
                            day_btn.config(bg=COLORS['info'], fg='white')

                        # Highlight selected day
                        if (day == selected_date[0].day and
                            selected_date[0].month == selected_date[0].month and
                            selected_date[0].year == selected_date[0].year):
                            day_btn.config(bg=COLORS['success'], fg='white')

        def select_date(day):
            selected_date[0] = selected_date[0].replace(day=day)
            date_str = selected_date[0].strftime("%Y-%m-%d")
            date_var.set(date_str)
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, date_str)
            popup.destroy()

        month_year_label = tk.Label(nav_frame, text=current_date.strftime("%B %Y"),
                                  font=('Arial', 14, 'bold'), bg=COLORS['primary'], fg='white')
        month_year_label.pack(side='left', padx=20)

        next_btn = tk.Button(nav_frame, text="▶", command=lambda: change_month(1),
                           bg=COLORS['primary'], fg='white', font=('Arial', 12, 'bold'),
                           relief='flat', cursor='hand2')
        next_btn.pack(side='left', padx=10)

        # Calendar frame
        calendar_frame = tk.Frame(popup, bg=COLORS['light'])
        calendar_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Configure grid weights for calendar layout
        for i in range(7):
            calendar_frame.grid_columnconfigure(i, weight=1)

        # Today/Close buttons
        bottom_frame = tk.Frame(popup, bg=COLORS['light'])
        bottom_frame.pack(fill='x', padx=10, pady=10)

        today_btn = tk.Button(bottom_frame, text="Today",
                            command=lambda: select_date(datetime.now().day),
                            bg=COLORS['success'], fg='white', font=('Arial', 10, 'bold'))
        today_btn.pack(side='left')

        close_btn = tk.Button(bottom_frame, text="Close",
                            command=popup.destroy,
                            bg=COLORS['secondary'], fg='white', font=('Arial', 10, 'bold'))
        close_btn.pack(side='right')

        # Initialize calendar
        update_calendar()


    def __del__(self):
        """Cleanup when application closes"""
        if hasattr(self, 'db'):
            self.db.close_connection()

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = GoldJewelryApp(root)
    
    # Handle window close event
    def on_closing():
        app.db.close_connection()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
