"""
IMS - Main GUI Application
Sales and Inventory Management System for Electronics
Built with Tkinter + SQLite + ReportLab
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os, sys, subprocess, platform
from datetime import datetime, date

# Local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ims import database as db
from ims import reports as rpt

# ── Colour Palette ─────────────────────────────────────────
C = {
    'primary':     '#1A5276',
    'primary_dk':  '#154360',
    'accent':      '#2E86C1',
    'success':     '#1E8449',
    'warning':     '#D4AC0D',
    'danger':      '#C0392B',
    'sidebar':     '#1C2833',
    'sidebar_sel': '#2E86C1',
    'bg':          '#F0F3F4',
    'white':       '#FFFFFF',
    'grey_lt':     '#D5D8DC',
    'grey':        '#7F8C8D',
    'text':        '#2C3E50',
    'card_bg':     '#FFFFFF',
}

FONT = 'Segoe UI'


def open_file(path):
    """Open a file with the OS default viewer."""
    try:
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':
            subprocess.run(['open', path])
        else:
            subprocess.run(['xdg-open', path])
    except Exception as e:
        messagebox.showinfo("Report Saved", f"Report saved to:\n{path}")


# ════════════════════════════════════════════════════════════
#  LOGIN WINDOW
# ════════════════════════════════════════════════════════════
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IMS – Login")
        self.geometry("440x520")
        self.resizable(False, False)
        self.configure(bg=C['primary'])
        self.current_user = None
        self._build()
        self.eval('tk::PlaceWindow . center')

    def _build(self):
        # Logo area
        tk.Label(self, text="📦", font=(FONT, 48), bg=C['primary'], fg=C['white']).pack(pady=(40, 6))
        tk.Label(self, text="Inventory Management System",
                 font=(FONT, 14, 'bold'), bg=C['primary'], fg=C['white']).pack()
        tk.Label(self, text="Electronics Store Edition",
                 font=(FONT, 10), bg=C['primary'], fg='#AED6F1').pack(pady=(0, 30))

        card = tk.Frame(self, bg=C['white'], bd=0)
        card.pack(fill='x', padx=40)

        def lbl(text):
            tk.Label(card, text=text, font=(FONT, 9), bg=C['white'],
                     fg=C['grey'], anchor='w').pack(fill='x', padx=20, pady=(12, 2))

        def entry(show=None):
            e = tk.Entry(card, font=(FONT, 11), bg='#EBF5FB', bd=0,
                         relief='flat', show=show)
            e.pack(fill='x', padx=20, ipady=8)
            tk.Frame(card, bg=C['accent'], height=2).pack(fill='x', padx=20)
            return e

        lbl("Email Address")
        self.e_email = entry()
        self.e_email.insert(0, "admin@ims.com")

        lbl("Password")
        self.e_pass = entry(show='•')
        self.e_pass.insert(0, "admin123")
        self.e_pass.bind('<Return>', lambda e: self._login())

        tk.Frame(card, bg=C['white'], height=20).pack()

        btn = tk.Button(card, text="SIGN IN", font=(FONT, 11, 'bold'),
                        bg=C['primary'], fg=C['white'], bd=0, cursor='hand2',
                        activebackground=C['accent'], activeforeground=C['white'],
                        command=self._login)
        btn.pack(fill='x', padx=20, ipady=10)
        tk.Frame(card, bg=C['white'], height=20).pack()

        self.lbl_error = tk.Label(self, text="", font=(FONT, 9),
                                   bg=C['primary'], fg='#F1948A')
        self.lbl_error.pack(pady=8)

    def _login(self):
        user = db.authenticate_user(self.e_email.get().strip(), self.e_pass.get())
        if user:
            self.current_user = user
            self.destroy()
        else:
            self.lbl_error.config(text="✗  Incorrect email or password.")


# ════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ════════════════════════════════════════════════════════════
class IMSApp(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.current_user = user
        self.title("IMS — Inventory Management System")
        self.geometry("1280x780")
        self.minsize(1100, 680)
        self.configure(bg=C['bg'])
        self._build_layout()
        self._show_dashboard()
        self.eval('tk::PlaceWindow . center')

    # ── Layout skeleton ────────────────────────────────────
    def _build_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=C['sidebar'], width=220)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        # Brand
        tk.Label(self.sidebar, text="📦  IMS", font=(FONT, 16, 'bold'),
                 bg=C['sidebar'], fg=C['white']).pack(pady=(20, 4))
        tk.Label(self.sidebar, text="Electronics Store",
                 font=(FONT, 9), bg=C['sidebar'], fg='#7F8C8D').pack()
        tk.Frame(self.sidebar, bg='#2C3E50', height=1).pack(fill='x', pady=10)

        # Nav items: (label, emoji, method)
        self._nav_btns = {}
        nav_items = [
            ("Dashboard",  "🏠", self._show_dashboard),
            ("Products",   "📱", self._show_products),
            ("Categories", "🏷", self._show_categories),
            ("Customers",  "👥", self._show_customers),
            ("Suppliers",  "🚚", self._show_suppliers),
            ("New Sale",   "🛒", self._show_new_sale),
            ("Purchases",  "📦", self._show_purchases),
            ("Orders",     "📋", self._show_orders),
            ("Reports",    "📊", self._show_reports),
            ("Users",      "👤", self._show_users),
        ]
        for label, icon, cmd in nav_items:
            btn = tk.Button(self.sidebar, text=f"  {icon}  {label}",
                            font=(FONT, 10), bg=C['sidebar'], fg='#BDC3C7',
                            activebackground=C['sidebar_sel'], activeforeground=C['white'],
                            bd=0, anchor='w', cursor='hand2',
                            command=lambda c=cmd, lbl=label: self._nav(c, lbl))
            btn.pack(fill='x', ipady=9, padx=8, pady=1)
            self._nav_btns[label] = btn

        tk.Frame(self.sidebar, bg='#2C3E50', height=1).pack(fill='x', pady=10)

        # User info + logout
        uframe = tk.Frame(self.sidebar, bg=C['sidebar'])
        uframe.pack(side='bottom', fill='x', pady=10, padx=8)
        tk.Label(uframe, text=f"👤  {self.current_user['fullname']}",
                 font=(FONT, 9, 'bold'), bg=C['sidebar'], fg='#AED6F1').pack(anchor='w')
        tk.Label(uframe, text=self.current_user['role'],
                 font=(FONT, 8), bg=C['sidebar'], fg='#7F8C8D').pack(anchor='w')
        tk.Button(uframe, text="Logout", font=(FONT, 8), bg='#922B21', fg=C['white'],
                  bd=0, cursor='hand2', command=self._logout).pack(anchor='w', pady=(6, 0))

        # Main content area
        self.main = tk.Frame(self, bg=C['bg'])
        self.main.pack(side='left', fill='both', expand=True)

    def _nav(self, cmd, label):
        for lbl, btn in self._nav_btns.items():
            btn.config(bg=C['sidebar_sel'] if lbl == label else C['sidebar'],
                       fg=C['white'] if lbl == label else '#BDC3C7',
                       font=(FONT, 10, 'bold') if lbl == label else (FONT, 10))
        cmd()

    def _clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    def _page_header(self, title, subtitle=''):
        hf = tk.Frame(self.main, bg=C['primary'], height=70)
        hf.pack(fill='x')
        hf.pack_propagate(False)
        tk.Label(hf, text=title, font=(FONT, 16, 'bold'),
                 bg=C['primary'], fg=C['white']).pack(side='left', padx=20, pady=10)
        if subtitle:
            tk.Label(hf, text=subtitle, font=(FONT, 9),
                     bg=C['primary'], fg='#AED6F1').pack(side='left')

    def _card(self, parent, title, value, color, icon):
        f = tk.Frame(parent, bg=color, bd=0)
        tk.Label(f, text=icon, font=(FONT, 22), bg=color, fg=C['white']).pack(pady=(12, 0))
        tk.Label(f, text=str(value), font=(FONT, 20, 'bold'), bg=color, fg=C['white']).pack()
        tk.Label(f, text=title, font=(FONT, 9), bg=color, fg='#D6EAF8').pack(pady=(0, 12))
        return f

    def _treeview(self, parent, columns, heights=14):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("IMS.Treeview", background=C['white'], foreground=C['text'],
                        rowheight=28, fieldbackground=C['white'], font=(FONT, 9))
        style.configure("IMS.Treeview.Heading", background=C['primary'],
                        foreground=C['white'], font=(FONT, 9, 'bold'))
        style.map("IMS.Treeview", background=[('selected', C['accent'])])

        frame = tk.Frame(parent, bg=C['bg'])
        tv = ttk.Treeview(frame, columns=list(columns.keys()), show='headings',
                          style='IMS.Treeview', height=heights)
        for col, width in columns.items():
            tv.heading(col, text=col)
            tv.column(col, width=width, anchor='w')

        vsb = ttk.Scrollbar(frame, orient='vertical', command=tv.yview)
        hsb = ttk.Scrollbar(frame, orient='horizontal', command=tv.xview)
        tv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tv.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Alternating row colours
        tv.tag_configure('odd',  background='#EBF5FB')
        tv.tag_configure('even', background=C['white'])
        return frame, tv

    def _toolbar_btn(self, parent, text, color, cmd):
        return tk.Button(parent, text=text, font=(FONT, 9), bg=color, fg=C['white'],
                         bd=0, padx=12, pady=6, cursor='hand2', activebackground=C['primary_dk'],
                         activeforeground=C['white'], command=cmd)

    def _logout(self):
        self.destroy()
        _start_login()

    # ══════════════════════════════════════════════════════
    #  DASHBOARD
    # ══════════════════════════════════════════════════════
    def _show_dashboard(self):
        self._clear_main()
        self._page_header("📊 Dashboard",
                          f"  Welcome back, {self.current_user['fullname']}  •  "
                          f"{datetime.now().strftime('%A, %d %B %Y')}")

        stats = db.get_dashboard_stats()
        content = tk.Frame(self.main, bg=C['bg'])
        content.pack(fill='both', expand=True, padx=20, pady=16)

        # ── KPI cards ─────────────────────────────────────
        cards_frame = tk.Frame(content, bg=C['bg'])
        cards_frame.pack(fill='x')

        cards = [
            ("Total Products",  stats['total_products'],  C['primary'],  "📱"),
            ("Total Customers", stats['total_customers'], C['accent'],   "👥"),
            ("Total Orders",    stats['total_orders'],    C['success'],  "📋"),
            ("Low Stock Items", stats['low_stock'],       C['warning'] if stats['low_stock'] > 0 else C['success'], "⚠"),
            ("Monthly Sales",   f"KES {stats['monthly_sales']:,.0f}", C['success'], "💰"),
            ("Total Purchases", f"KES {stats['total_purchases']:,.0f}", C['danger'], "📦"),
        ]
        for i, (title, val, color, icon) in enumerate(cards):
            c = self._card(cards_frame, title, val, color, icon)
            c.grid(row=0, column=i, padx=6, pady=4, sticky='ew')
            cards_frame.columnconfigure(i, weight=1)

        # ── Two column section ─────────────────────────────
        two_col = tk.Frame(content, bg=C['bg'])
        two_col.pack(fill='both', expand=True, pady=(16, 0))
        two_col.columnconfigure(0, weight=1)
        two_col.columnconfigure(1, weight=1)

        # Recent orders
        left = tk.Frame(two_col, bg=C['white'], bd=0, relief='flat')
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        tk.Label(left, text="Recent Orders", font=(FONT, 11, 'bold'),
                 bg=C['white'], fg=C['primary']).pack(anchor='w', padx=12, pady=(10, 4))
        tk.Frame(left, bg=C['grey_lt'], height=1).pack(fill='x')

        orders = db.get_all_orders()[:8]
        tf, tv = self._treeview(left, {'Order No.': 140, 'Customer': 160, 'Amount': 110, 'Date': 120}, 8)
        for i, o in enumerate(orders):
            tv.insert('', 'end', values=(
                o['order_number'], o.get('customer_name') or 'Walk-in',
                f"KES {o['total_amount']:,.2f}", o['created_at'][:10]
            ), tags=('even' if i % 2 == 0 else 'odd',))
        tf.pack(fill='both', expand=True, padx=8, pady=8)

        # Low stock alert
        right = tk.Frame(two_col, bg=C['white'], bd=0)
        right.grid(row=0, column=1, sticky='nsew', padx=(8, 0))
        tk.Label(right, text="⚠  Low Stock Alerts", font=(FONT, 11, 'bold'),
                 bg=C['white'], fg=C['warning']).pack(anchor='w', padx=12, pady=(10, 4))
        tk.Frame(right, bg=C['grey_lt'], height=1).pack(fill='x')

        low = db.get_low_stock_products()
        tf2, tv2 = self._treeview(right, {'Product': 180, 'Category': 120, 'Qty': 60, 'Min': 60}, 8)
        for i, p in enumerate(low):
            tv2.insert('', 'end', values=(
                p['name'], p.get('category_name') or '—',
                p['quantity'], p['reorder_level']
            ), tags=('even' if i % 2 == 0 else 'odd',))
        tf2.pack(fill='both', expand=True, padx=8, pady=8)

    # ══════════════════════════════════════════════════════
    #  PRODUCTS
    # ══════════════════════════════════════════════════════
    def _show_products(self):
        self._clear_main()
        self._page_header("📱 Products", "  Manage inventory items")

        # Toolbar
        tb = tk.Frame(self.main, bg=C['bg'])
        tb.pack(fill='x', padx=16, pady=8)
        self._toolbar_btn(tb, "➕  Add Product", C['primary'], self._add_product).pack(side='left', padx=4)
        self._toolbar_btn(tb, "✏  Edit",         C['accent'],  self._edit_product).pack(side='left', padx=4)
        self._toolbar_btn(tb, "🗑  Delete",       C['danger'],  self._delete_product).pack(side='left', padx=4)
        self._toolbar_btn(tb, "🔄  Refresh",      C['grey'],    self._show_products).pack(side='left', padx=4)

        # Search
        sf = tk.Frame(tb, bg=C['bg'])
        sf.pack(side='right')
        tk.Label(sf, text="Search:", bg=C['bg'], fg=C['text'], font=(FONT, 9)).pack(side='left')
        self._prod_search = tk.Entry(sf, font=(FONT, 9), width=22, bg=C['white'])
        self._prod_search.pack(side='left', padx=4, ipady=5)
        self._toolbar_btn(sf, "🔍", C['primary'], lambda: self._load_products()).pack(side='left')

        cols = {'Code': 90, 'Name': 200, 'Category': 120, 'Qty': 60,
                'Price (KES)': 100, 'Reorder': 65, 'Expiry': 100, 'Status': 90}
        tf, self._prod_tv = self._treeview(self.main, cols)
        tf.pack(fill='both', expand=True, padx=16, pady=(0, 12))
        self._load_products()

    def _load_products(self):
        search = getattr(self, '_prod_search', None)
        term = search.get().lower() if search else ''
        self._prod_tv.delete(*self._prod_tv.get_children())
        for i, p in enumerate(db.get_all_products()):
            if term and term not in p['name'].lower() and term not in p['productcode'].lower():
                continue
            status = ('Out of Stock' if p['quantity'] <= 0
                      else 'Low Stock' if p['quantity'] <= p['reorder_level']
                      else 'In Stock')
            self._prod_tv.insert('', 'end', iid=str(p['id']), values=(
                p['productcode'], p['name'],
                p.get('category_name') or '—',
                p['quantity'], f"{p['unit_price']:,.2f}",
                p['reorder_level'],
                p.get('expiry_date') or '—', status
            ), tags=('even' if i % 2 == 0 else 'odd',))

    def _add_product(self):
        self._product_form(None)

    def _edit_product(self):
        sel = self._prod_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a product to edit.")
            return
        pid = int(sel[0])
        prod = next((p for p in db.get_all_products() if p['id'] == pid), None)
        if prod:
            self._product_form(prod)

    def _delete_product(self):
        sel = self._prod_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a product to delete.")
            return
        if messagebox.askyesno("Confirm", "Delete selected product?"):
            db.delete_product(int(sel[0]))
            self._load_products()

    def _product_form(self, prod=None):
        cats = db.get_all_categories()
        cat_names = [c['name'] for c in cats]
        cat_map = {c['name']: c['id'] for c in cats}

        win = tk.Toplevel(self)
        win.title("Add Product" if not prod else "Edit Product")
        win.geometry("440x560")
        win.configure(bg=C['white'])
        win.grab_set()

        tk.Label(win, text="Add Product" if not prod else "Edit Product",
                 font=(FONT, 14, 'bold'), bg=C['white'], fg=C['primary']).pack(pady=(16, 0))
        tk.Frame(win, bg=C['grey_lt'], height=1).pack(fill='x', pady=8)

        form = tk.Frame(win, bg=C['white'])
        form.pack(fill='x', padx=24)

        fields = {}
        def row(label, key, default=''):
            tk.Label(form, text=label, font=(FONT, 9), bg=C['white'], fg=C['grey'],
                     anchor='w').pack(fill='x', pady=(6, 1))
            e = tk.Entry(form, font=(FONT, 10), bg='#EBF5FB', bd=1, relief='flat')
            e.pack(fill='x', ipady=6)
            if default:
                e.insert(0, str(default))
            fields[key] = e
            return e

        row("Product Code *", 'productcode', prod['productcode'] if prod else '')
        row("Product Name *",  'name',        prod['name']        if prod else '')

        tk.Label(form, text="Category", font=(FONT, 9), bg=C['white'],
                 fg=C['grey'], anchor='w').pack(fill='x', pady=(6, 1))
        cat_var = tk.StringVar()
        cat_cb  = ttk.Combobox(form, textvariable=cat_var, values=cat_names,
                                font=(FONT, 10), state='readonly')
        cat_cb.pack(fill='x', ipady=4)
        if prod and prod.get('category_name'):
            cat_var.set(prod['category_name'])
        elif cat_names:
            cat_var.set(cat_names[0])

        row("Description",   'description', prod['description']   if prod else '')
        row("Quantity *",    'quantity',    prod['quantity']       if prod else '0')
        row("Unit Price *",  'unit_price',  prod['unit_price']     if prod else '0')
        row("Reorder Level", 'reorder',     prod['reorder_level']  if prod else '5')
        row("Expiry Date (YYYY-MM-DD)", 'expiry', prod.get('expiry_date') or '')

        def save():
            try:
                code  = fields['productcode'].get().strip()
                name  = fields['name'].get().strip()
                qty   = int(fields['quantity'].get())
                price = float(fields['unit_price'].get())
                rl    = int(fields['reorder'].get())
                exp   = fields['expiry'].get().strip()
                desc  = fields['description'].get().strip()
                cat_id = cat_map.get(cat_var.get())

                if not code or not name:
                    messagebox.showwarning("Validation", "Code and Name are required.", parent=win)
                    return

                if prod:
                    db.update_product(prod['id'], code, name, cat_id, desc, qty, price, rl, exp)
                else:
                    ok, msg = db.create_product(code, name, cat_id, desc, qty, price, rl, exp)
                    if not ok:
                        messagebox.showerror("Error", msg, parent=win)
                        return
                win.destroy()
                self._load_products()
            except ValueError:
                messagebox.showerror("Error", "Quantity, price, and reorder level must be numbers.", parent=win)

        tk.Frame(win, bg=C['white'], height=10).pack()
        btn_f = tk.Frame(win, bg=C['white'])
        btn_f.pack(fill='x', padx=24)
        self._toolbar_btn(btn_f, "💾  Save", C['primary'], save).pack(side='left', fill='x', expand=True, padx=(0, 4))
        self._toolbar_btn(btn_f, "Cancel",   C['grey'],    win.destroy).pack(side='left', fill='x', expand=True)

    # ══════════════════════════════════════════════════════
    #  CATEGORIES
    # ══════════════════════════════════════════════════════
    def _show_categories(self):
        self._clear_main()
        self._page_header("🏷 Categories")

        tb = tk.Frame(self.main, bg=C['bg'])
        tb.pack(fill='x', padx=16, pady=8)
        self._toolbar_btn(tb, "➕  Add", C['primary'], self._add_category).pack(side='left', padx=4)
        self._toolbar_btn(tb, "✏  Edit", C['accent'], self._edit_category).pack(side='left', padx=4)
        self._toolbar_btn(tb, "🗑  Delete", C['danger'], self._delete_category).pack(side='left', padx=4)

        tf, self._cat_tv = self._treeview(self.main, {'ID': 60, 'Name': 200, 'Description': 350, 'Created': 140})
        tf.pack(fill='both', expand=True, padx=16, pady=(0, 12))
        self._load_categories()

    def _load_categories(self):
        self._cat_tv.delete(*self._cat_tv.get_children())
        for i, c in enumerate(db.get_all_categories()):
            self._cat_tv.insert('', 'end', iid=str(c['id']),
                                values=(c['id'], c['name'], c.get('description') or '—', c['created_at'][:10]),
                                tags=('even' if i % 2 == 0 else 'odd',))

    def _add_category(self):
        name = simpledialog.askstring("Add Category", "Category Name:", parent=self)
        if name:
            desc = simpledialog.askstring("Description", "Description (optional):", parent=self) or ''
            ok, msg = db.create_category(name.strip(), desc)
            if ok:
                self._load_categories()
            else:
                messagebox.showerror("Error", msg)

    def _edit_category(self):
        sel = self._cat_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a category first.")
            return
        cats = db.get_all_categories()
        cat = next((c for c in cats if str(c['id']) == sel[0]), None)
        if cat:
            name = simpledialog.askstring("Edit Category", "Name:", initialvalue=cat['name'], parent=self)
            if name:
                desc = simpledialog.askstring("Description", "Description:", initialvalue=cat.get('description') or '', parent=self) or ''
                db.update_category(cat['id'], name.strip(), desc)
                self._load_categories()

    def _delete_category(self):
        sel = self._cat_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a category first.")
            return
        if messagebox.askyesno("Confirm", "Delete this category?"):
            db.delete_category(int(sel[0]))
            self._load_categories()

    # ══════════════════════════════════════════════════════
    #  CUSTOMERS
    # ══════════════════════════════════════════════════════
    def _show_customers(self):
        self._clear_main()
        self._page_header("👥 Customers")

        tb = tk.Frame(self.main, bg=C['bg'])
        tb.pack(fill='x', padx=16, pady=8)
        self._toolbar_btn(tb, "➕  Add Customer", C['primary'], self._add_customer).pack(side='left', padx=4)
        self._toolbar_btn(tb, "✏  Edit",          C['accent'],  self._edit_customer).pack(side='left', padx=4)
        self._toolbar_btn(tb, "🗑  Delete",        C['danger'],  self._delete_customer).pack(side='left', padx=4)

        cols = {'ID': 50, 'Name': 200, 'Phone': 110, 'Email': 200, 'Address': 200, 'Credit': 100, 'Joined': 100}
        tf, self._cust_tv = self._treeview(self.main, cols)
        tf.pack(fill='both', expand=True, padx=16, pady=(0, 12))
        self._load_customers()

    def _load_customers(self):
        self._cust_tv.delete(*self._cust_tv.get_children())
        for i, c in enumerate(db.get_all_customers()):
            self._cust_tv.insert('', 'end', iid=str(c['id']),
                                 values=(c['id'], c['fullname'], c.get('phone') or '—',
                                         c.get('email') or '—', c.get('address') or '—',
                                         f"KES {c['credit']:,.2f}", c['created_at'][:10]),
                                 tags=('even' if i % 2 == 0 else 'odd',))

    def _add_customer(self): self._customer_form(None)

    def _edit_customer(self):
        sel = self._cust_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a customer.")
            return
        cust = next((c for c in db.get_all_customers() if str(c['id']) == sel[0]), None)
        if cust:
            self._customer_form(cust)

    def _delete_customer(self):
        sel = self._cust_tv.selection()
        if not sel:
            return
        if messagebox.askyesno("Confirm", "Delete this customer?"):
            db.delete_customer(int(sel[0]))
            self._load_customers()

    def _customer_form(self, cust=None):
        win = tk.Toplevel(self)
        win.title("Add Customer" if not cust else "Edit Customer")
        win.geometry("400x400")
        win.configure(bg=C['white'])
        win.grab_set()

        tk.Label(win, text="Customer Details", font=(FONT, 13, 'bold'),
                 bg=C['white'], fg=C['primary']).pack(pady=(16, 4))
        tk.Frame(win, bg=C['grey_lt'], height=1).pack(fill='x', pady=6)

        form = tk.Frame(win, bg=C['white'])
        form.pack(fill='x', padx=24)
        fields = {}

        def row(label, key, default=''):
            tk.Label(form, text=label, font=(FONT, 9), bg=C['white'], fg=C['grey'], anchor='w').pack(fill='x', pady=(6, 1))
            e = tk.Entry(form, font=(FONT, 10), bg='#EBF5FB', bd=1, relief='flat')
            e.pack(fill='x', ipady=6)
            if default: e.insert(0, default)
            fields[key] = e

        row("Full Name *", 'name',    cust['fullname']        if cust else '')
        row("Phone",       'phone',   cust.get('phone') or '' if cust else '')
        row("Email",       'email',   cust.get('email') or '' if cust else '')
        row("Address",     'address', cust.get('address') or '' if cust else '')

        def save():
            name = fields['name'].get().strip()
            if not name:
                messagebox.showwarning("Validation", "Name is required.", parent=win)
                return
            if cust:
                db.update_customer(cust['id'], name, fields['phone'].get(), fields['email'].get(), fields['address'].get())
            else:
                db.create_customer(name, fields['phone'].get(), fields['email'].get(), fields['address'].get())
            win.destroy()
            self._load_customers()

        tk.Frame(win, bg=C['white'], height=14).pack()
        bf = tk.Frame(win, bg=C['white'])
        bf.pack(fill='x', padx=24)
        self._toolbar_btn(bf, "💾  Save", C['primary'], save).pack(side='left', fill='x', expand=True, padx=(0, 4))
        self._toolbar_btn(bf, "Cancel",   C['grey'],    win.destroy).pack(side='left', fill='x', expand=True)

    # ══════════════════════════════════════════════════════
    #  SUPPLIERS
    # ══════════════════════════════════════════════════════
    def _show_suppliers(self):
        self._clear_main()
        self._page_header("🚚 Suppliers")

        tb = tk.Frame(self.main, bg=C['bg'])
        tb.pack(fill='x', padx=16, pady=8)
        self._toolbar_btn(tb, "➕  Add Supplier", C['primary'], self._add_supplier).pack(side='left', padx=4)
        self._toolbar_btn(tb, "✏  Edit",          C['accent'],  self._edit_supplier).pack(side='left', padx=4)
        self._toolbar_btn(tb, "🗑  Delete",        C['danger'],  self._delete_supplier).pack(side='left', padx=4)

        cols = {'Code': 80, 'Name': 180, 'Location': 140, 'Phone': 110, 'Email': 180, 'Balance': 100}
        tf, self._sup_tv = self._treeview(self.main, cols)
        tf.pack(fill='both', expand=True, padx=16, pady=(0, 12))
        self._load_suppliers()

    def _load_suppliers(self):
        self._sup_tv.delete(*self._sup_tv.get_children())
        for i, s in enumerate(db.get_all_suppliers()):
            self._sup_tv.insert('', 'end', iid=str(s['id']),
                                values=(s['suppliercode'], s['fullname'], s.get('location') or '—',
                                        s.get('phone') or '—', s.get('email') or '—',
                                        f"KES {s['balance']:,.2f}"),
                                tags=('even' if i % 2 == 0 else 'odd',))

    def _add_supplier(self): self._supplier_form(None)

    def _edit_supplier(self):
        sel = self._sup_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a supplier.")
            return
        sup = next((s for s in db.get_all_suppliers() if str(s['id']) == sel[0]), None)
        if sup:
            self._supplier_form(sup)

    def _delete_supplier(self):
        sel = self._sup_tv.selection()
        if not sel:
            return
        if messagebox.askyesno("Confirm", "Delete this supplier?"):
            db.delete_supplier(int(sel[0]))
            self._load_suppliers()

    def _supplier_form(self, sup=None):
        win = tk.Toplevel(self)
        win.title("Add Supplier" if not sup else "Edit Supplier")
        win.geometry("400x430")
        win.configure(bg=C['white'])
        win.grab_set()

        tk.Label(win, text="Supplier Details", font=(FONT, 13, 'bold'),
                 bg=C['white'], fg=C['primary']).pack(pady=(16, 4))
        tk.Frame(win, bg=C['grey_lt'], height=1).pack(fill='x', pady=6)

        form = tk.Frame(win, bg=C['white'])
        form.pack(fill='x', padx=24)
        fields = {}

        def row(label, key, default=''):
            tk.Label(form, text=label, font=(FONT, 9), bg=C['white'], fg=C['grey'], anchor='w').pack(fill='x', pady=(6, 1))
            e = tk.Entry(form, font=(FONT, 10), bg='#EBF5FB', bd=1, relief='flat')
            e.pack(fill='x', ipady=6)
            if default: e.insert(0, default)
            fields[key] = e

        row("Supplier Code *", 'code',     sup['suppliercode']     if sup else '')
        row("Full Name *",     'name',     sup['fullname']         if sup else '')
        row("Location",        'location', sup.get('location') or '' if sup else '')
        row("Phone",           'phone',    sup.get('phone') or ''   if sup else '')
        row("Email",           'email',    sup.get('email') or ''   if sup else '')

        def save():
            code = fields['code'].get().strip()
            name = fields['name'].get().strip()
            if not code or not name:
                messagebox.showwarning("Validation", "Code and Name required.", parent=win)
                return
            if sup:
                db.update_supplier(sup['id'], code, name, fields['location'].get(), fields['phone'].get(), fields['email'].get())
            else:
                ok, msg = db.create_supplier(code, name, fields['location'].get(), fields['phone'].get(), fields['email'].get())
                if not ok:
                    messagebox.showerror("Error", msg, parent=win)
                    return
            win.destroy()
            self._load_suppliers()

        tk.Frame(win, bg=C['white'], height=14).pack()
        bf = tk.Frame(win, bg=C['white'])
        bf.pack(fill='x', padx=24)
        self._toolbar_btn(bf, "💾  Save", C['primary'], save).pack(side='left', fill='x', expand=True, padx=(0, 4))
        self._toolbar_btn(bf, "Cancel",   C['grey'],    win.destroy).pack(side='left', fill='x', expand=True)

    # ══════════════════════════════════════════════════════
    #  NEW SALE
    # ══════════════════════════════════════════════════════
    def _show_new_sale(self):
        self._clear_main()
        self._page_header("🛒 New Sale", "  Process a sales transaction")

        content = tk.Frame(self.main, bg=C['bg'])
        content.pack(fill='both', expand=True, padx=20, pady=12)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        # ── Left: item picker ──
        left = tk.LabelFrame(content, text=" Select Products ", font=(FONT, 10, 'bold'),
                              bg=C['white'], fg=C['primary'], bd=1)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=4)

        tf, self._sale_prod_tv = self._treeview(left, {'Code': 80, 'Name': 180, 'Qty': 60, 'Price': 90}, 12)
        tf.pack(fill='both', expand=True, padx=8, pady=8)
        for i, p in enumerate(db.get_all_products()):
            if p['quantity'] > 0:
                self._sale_prod_tv.insert('', 'end', iid=str(p['id']),
                                          values=(p['productcode'], p['name'], p['quantity'],
                                                  f"KES {p['unit_price']:,.2f}"),
                                          tags=('even' if i % 2 == 0 else 'odd',))

        qty_f = tk.Frame(left, bg=C['white'])
        qty_f.pack(fill='x', padx=8, pady=(0, 8))
        tk.Label(qty_f, text="Qty:", bg=C['white'], font=(FONT, 9)).pack(side='left')
        self._sale_qty = tk.Entry(qty_f, width=6, font=(FONT, 10), bg='#EBF5FB')
        self._sale_qty.insert(0, '1')
        self._sale_qty.pack(side='left', padx=6, ipady=4)
        self._toolbar_btn(qty_f, "➕  Add to Cart", C['primary'], self._add_to_cart).pack(side='left')

        # ── Right: cart + customer ──
        right = tk.Frame(content, bg=C['bg'])
        right.grid(row=0, column=1, sticky='nsew', padx=(8, 0))

        cust_f = tk.LabelFrame(right, text=" Customer ", font=(FONT, 10, 'bold'),
                                bg=C['white'], fg=C['primary'], bd=1)
        cust_f.pack(fill='x', pady=(0, 8))
        custs = db.get_all_customers()
        cust_names = ['Walk-in Customer'] + [c['fullname'] for c in custs]
        self._sale_cust_ids = {c['fullname']: c['id'] for c in custs}
        self._sale_cust_var = tk.StringVar(value='Walk-in Customer')
        ttk.Combobox(cust_f, textvariable=self._sale_cust_var, values=cust_names,
                     font=(FONT, 10), state='readonly').pack(fill='x', padx=12, pady=8, ipady=4)

        cart_f = tk.LabelFrame(right, text=" Cart ", font=(FONT, 10, 'bold'),
                                bg=C['white'], fg=C['primary'], bd=1)
        cart_f.pack(fill='both', expand=True, pady=(0, 8))

        self._cart_items = []
        tf2, self._cart_tv = self._treeview(cart_f, {'Product': 180, 'Qty': 55, 'Unit Price': 95, 'Subtotal': 95}, 8)
        tf2.pack(fill='both', expand=True, padx=8, pady=8)

        cf = tk.Frame(cart_f, bg=C['white'])
        cf.pack(fill='x', padx=8, pady=(0, 8))
        self._toolbar_btn(cf, "🗑  Remove Item", C['danger'], self._remove_cart_item).pack(side='left')
        self._sale_total_var = tk.StringVar(value="Total: KES 0.00")
        tk.Label(cf, textvariable=self._sale_total_var, font=(FONT, 12, 'bold'),
                 bg=C['white'], fg=C['primary']).pack(side='right', padx=8)

        self._toolbar_btn(right, "✅  Complete Sale", C['success'], self._complete_sale).pack(
            fill='x', ipady=10)

    def _add_to_cart(self):
        sel = self._sale_prod_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a product first.")
            return
        try:
            qty = int(self._sale_qty.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid positive quantity.")
            return

        pid = int(sel[0])
        prods = db.get_all_products()
        prod = next((p for p in prods if p['id'] == pid), None)
        if not prod:
            return

        existing = next((i for i in self._cart_items if i['product_id'] == pid), None)
        total_qty = (existing['quantity'] + qty) if existing else qty

        if total_qty > prod['quantity']:
            messagebox.showerror("Stock Error", f"Only {prod['quantity']} units available.")
            return

        if existing:
            existing['quantity'] = total_qty
            existing['subtotal'] = total_qty * existing['unit_price']
        else:
            self._cart_items.append({
                'product_id': pid,
                'name': prod['name'],
                'quantity': qty,
                'unit_price': prod['unit_price'],
                'subtotal': qty * prod['unit_price'],
            })

        self._refresh_cart()

    def _refresh_cart(self):
        self._cart_tv.delete(*self._cart_tv.get_children())
        total = 0
        for i, item in enumerate(self._cart_items):
            self._cart_tv.insert('', 'end', iid=str(i),
                                 values=(item['name'], item['quantity'],
                                         f"KES {item['unit_price']:,.2f}",
                                         f"KES {item['subtotal']:,.2f}"),
                                 tags=('even' if i % 2 == 0 else 'odd',))
            total += item['subtotal']
        self._sale_total_var.set(f"Total: KES {total:,.2f}")

    def _remove_cart_item(self):
        sel = self._cart_tv.selection()
        if not sel:
            return
        idx = int(sel[0])
        self._cart_items.pop(idx)
        self._refresh_cart()

    def _complete_sale(self):
        if not self._cart_items:
            messagebox.showwarning("Empty Cart", "Add items to the cart first.")
            return

        cust_name = self._sale_cust_var.get()
        cust_id   = self._sale_cust_ids.get(cust_name)

        ok, result = db.create_order(cust_id, self.current_user['id'], self._cart_items)
        if ok:
            messagebox.showinfo("Sale Complete",
                                f"✅ Sale recorded successfully!\nOrder: {result}")
            self._cart_items = []
            self._show_new_sale()
        else:
            messagebox.showerror("Error", f"Failed to process sale:\n{result}")

    # ══════════════════════════════════════════════════════
    #  PURCHASES
    # ══════════════════════════════════════════════════════
    def _show_purchases(self):
        self._clear_main()
        self._page_header("📦 Purchases", "  Record stock received from suppliers")

        nb = ttk.Notebook(self.main)
        nb.pack(fill='both', expand=True, padx=16, pady=12)

        # Tab 1: New purchase
        tab1 = tk.Frame(nb, bg=C['bg'])
        nb.add(tab1, text='  New Purchase  ')
        self._build_purchase_form(tab1)

        # Tab 2: Purchase history
        tab2 = tk.Frame(nb, bg=C['bg'])
        nb.add(tab2, text='  Purchase History  ')
        cols = {'Purchase No.': 140, 'Date': 120, 'Supplier': 180, 'Staff': 140, 'Amount': 110, 'Status': 90}
        tf, self._pur_tv = self._treeview(tab2, cols)
        tf.pack(fill='both', expand=True, padx=8, pady=8)
        self._load_purchases()

    def _build_purchase_form(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        # Supplier selector
        sf = tk.LabelFrame(parent, text=" Supplier ", font=(FONT, 10, 'bold'),
                            bg=C['white'], fg=C['primary'])
        sf.grid(row=0, column=0, columnspan=2, sticky='ew', padx=8, pady=8)
        sups = db.get_all_suppliers()
        sup_names = [s['fullname'] for s in sups]
        self._pur_sup_ids = {s['fullname']: s['id'] for s in sups}
        self._pur_sup_var = tk.StringVar(value=sup_names[0] if sup_names else '')
        ttk.Combobox(sf, textvariable=self._pur_sup_var, values=sup_names,
                     font=(FONT, 10), state='readonly').pack(fill='x', padx=12, pady=8, ipady=4)

        # Product picker
        left = tk.LabelFrame(parent, text=" Select Products ", font=(FONT, 10, 'bold'),
                              bg=C['white'], fg=C['primary'])
        left.grid(row=1, column=0, sticky='nsew', padx=(8, 4), pady=4)
        tf, self._pur_prod_tv = self._treeview(left, {'Code': 80, 'Name': 180, 'Stock': 60, 'Price': 90}, 10)
        tf.pack(fill='both', expand=True, padx=8, pady=8)
        for i, p in enumerate(db.get_all_products()):
            self._pur_prod_tv.insert('', 'end', iid=str(p['id']),
                                     values=(p['productcode'], p['name'], p['quantity'],
                                             f"KES {p['unit_price']:,.2f}"),
                                     tags=('even' if i % 2 == 0 else 'odd',))

        qf = tk.Frame(left, bg=C['white'])
        qf.pack(fill='x', padx=8, pady=(0, 8))
        tk.Label(qf, text="Qty:", bg=C['white'], font=(FONT, 9)).pack(side='left')
        self._pur_qty = tk.Entry(qf, width=6, font=(FONT, 10), bg='#EBF5FB')
        self._pur_qty.insert(0, '1')
        self._pur_qty.pack(side='left', padx=6, ipady=4)
        tk.Label(qf, text="Cost:", bg=C['white'], font=(FONT, 9)).pack(side='left')
        self._pur_cost = tk.Entry(qf, width=8, font=(FONT, 10), bg='#EBF5FB')
        self._pur_cost.pack(side='left', padx=6, ipady=4)
        self._toolbar_btn(qf, "➕ Add", C['primary'], self._add_to_pur_cart).pack(side='left')

        # Cart
        right = tk.LabelFrame(parent, text=" Purchase Cart ", font=(FONT, 10, 'bold'),
                               bg=C['white'], fg=C['primary'])
        right.grid(row=1, column=1, sticky='nsew', padx=(4, 8), pady=4)
        self._pur_items = []
        tf2, self._pur_cart_tv = self._treeview(right, {'Product': 160, 'Qty': 55, 'Cost': 95, 'Subtotal': 95}, 10)
        tf2.pack(fill='both', expand=True, padx=8, pady=8)

        bf = tk.Frame(right, bg=C['white'])
        bf.pack(fill='x', padx=8, pady=(0, 8))
        self._toolbar_btn(bf, "🗑 Remove", C['danger'], self._remove_pur_item).pack(side='left')
        self._pur_total_var = tk.StringVar(value="Total: KES 0.00")
        tk.Label(bf, textvariable=self._pur_total_var, font=(FONT, 11, 'bold'),
                 bg=C['white'], fg=C['primary']).pack(side='right')

        self._toolbar_btn(parent, "✅  Record Purchase", C['success'], self._complete_purchase).grid(
            row=2, column=0, columnspan=2, sticky='ew', padx=8, pady=8, ipady=10)

    def _add_to_pur_cart(self):
        sel = self._pur_prod_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a product.")
            return
        try:
            qty  = int(self._pur_qty.get())
            cost = float(self._pur_cost.get() or '0')
            if qty <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter valid quantity and cost.")
            return
        pid  = int(sel[0])
        prod = next((p for p in db.get_all_products() if p['id'] == pid), None)
        if not prod: return
        self._pur_items.append({'product_id': pid, 'name': prod['name'],
                                 'quantity': qty, 'unit_cost': cost,
                                 'subtotal': qty * cost})
        self._pur_cart_tv.delete(*self._pur_cart_tv.get_children())
        total = 0
        for i, item in enumerate(self._pur_items):
            self._pur_cart_tv.insert('', 'end', iid=str(i),
                                     values=(item['name'], item['quantity'],
                                             f"KES {item['unit_cost']:,.2f}",
                                             f"KES {item['subtotal']:,.2f}"),
                                     tags=('even' if i % 2 == 0 else 'odd',))
            total += item['subtotal']
        self._pur_total_var.set(f"Total: KES {total:,.2f}")

    def _remove_pur_item(self):
        sel = self._pur_cart_tv.selection()
        if not sel: return
        idx = int(sel[0])
        self._pur_items.pop(idx)
        self._pur_cart_tv.delete(*self._pur_cart_tv.get_children())
        total = 0
        for i, item in enumerate(self._pur_items):
            self._pur_cart_tv.insert('', 'end', iid=str(i),
                                     values=(item['name'], item['quantity'],
                                             f"KES {item['unit_cost']:,.2f}",
                                             f"KES {item['subtotal']:,.2f}"),
                                     tags=('even' if i % 2 == 0 else 'odd',))
            total += item['subtotal']
        self._pur_total_var.set(f"Total: KES {total:,.2f}")

    def _complete_purchase(self):
        if not self._pur_items:
            messagebox.showwarning("Empty", "Add items first.")
            return
        sup_name = self._pur_sup_var.get()
        sup_id   = self._pur_sup_ids.get(sup_name)
        if not sup_id:
            messagebox.showwarning("Supplier", "Please select a supplier.")
            return
        ok, result = db.create_purchase(sup_id, self.current_user['id'], self._pur_items)
        if ok:
            messagebox.showinfo("Done", f"✅ Purchase recorded!\nRef: {result}")
            self._pur_items = []
            self._show_purchases()
        else:
            messagebox.showerror("Error", result)

    def _load_purchases(self):
        self._pur_tv.delete(*self._pur_tv.get_children())
        for i, p in enumerate(db.get_all_purchases()):
            self._pur_tv.insert('', 'end', iid=str(p['id']),
                                values=(p['purchase_number'], p['created_at'][:16],
                                        p.get('supplier_name') or '—', p.get('staff_name') or '—',
                                        f"KES {p['total_amount']:,.2f}", p['status']),
                                tags=('even' if i % 2 == 0 else 'odd',))

    # ══════════════════════════════════════════════════════
    #  ORDERS
    # ══════════════════════════════════════════════════════
    def _show_orders(self):
        self._clear_main()
        self._page_header("📋 Orders", "  Sales order history")

        tb = tk.Frame(self.main, bg=C['bg'])
        tb.pack(fill='x', padx=16, pady=8)
        self._toolbar_btn(tb, "🔍  View Details", C['accent'],   self._view_order_details).pack(side='left', padx=4)
        self._toolbar_btn(tb, "🔄  Refresh",      C['grey'],     self._show_orders).pack(side='left', padx=4)

        cols = {'Order No.': 140, 'Date': 130, 'Customer': 180, 'Staff': 140, 'Total': 110, 'Status': 90}
        tf, self._ord_tv = self._treeview(self.main, cols)
        tf.pack(fill='both', expand=True, padx=16, pady=(0, 12))
        for i, o in enumerate(db.get_all_orders()):
            self._ord_tv.insert('', 'end', iid=str(o['id']),
                                values=(o['order_number'], o['created_at'][:16],
                                        o.get('customer_name') or 'Walk-in',
                                        o.get('staff_name') or '—',
                                        f"KES {o['total_amount']:,.2f}", o['status']),
                                tags=('even' if i % 2 == 0 else 'odd',))

    def _view_order_details(self):
        sel = self._ord_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select an order to view.")
            return
        order_id = int(sel[0])
        items = db.get_order_items(order_id)

        win = tk.Toplevel(self)
        win.title(f"Order Details")
        win.geometry("580x420")
        win.configure(bg=C['white'])

        orders = db.get_all_orders()
        order = next((o for o in orders if o['id'] == order_id), {})
        tk.Label(win, text=f"Order: {order.get('order_number', '')}",
                 font=(FONT, 13, 'bold'), bg=C['white'], fg=C['primary']).pack(pady=(16, 2))
        tk.Label(win, text=f"Customer: {order.get('customer_name') or 'Walk-in'}  |  "
                            f"Date: {order.get('created_at', '')[:16]}",
                 font=(FONT, 9), bg=C['white'], fg=C['grey']).pack()
        tk.Frame(win, bg=C['grey_lt'], height=1).pack(fill='x', pady=8)

        cols = {'Product': 200, 'Code': 100, 'Qty': 60, 'Unit Price': 110, 'Subtotal': 110}
        tf, tv = self._treeview(win, cols, 10)
        tf.pack(fill='both', expand=True, padx=16, pady=8)
        for i, item in enumerate(items):
            tv.insert('', 'end', values=(item.get('product_name') or '—', item.get('productcode') or '—',
                                          item['quantity'], f"KES {item['unit_price']:,.2f}",
                                          f"KES {item['subtotal']:,.2f}"),
                      tags=('even' if i % 2 == 0 else 'odd',))
        tk.Label(win, text=f"Total: KES {order.get('total_amount', 0):,.2f}",
                 font=(FONT, 11, 'bold'), bg=C['white'], fg=C['primary']).pack(anchor='e', padx=20, pady=6)

    # ══════════════════════════════════════════════════════
    #  USERS
    # ══════════════════════════════════════════════════════
    def _show_users(self):
        if self.current_user['role'] != 'Admin':
            messagebox.showwarning("Access Denied", "Only administrators can manage users.")
            return
        self._clear_main()
        self._page_header("👤 User Management")

        tb = tk.Frame(self.main, bg=C['bg'])
        tb.pack(fill='x', padx=16, pady=8)
        self._toolbar_btn(tb, "➕  Add User", C['primary'], self._add_user).pack(side='left', padx=4)
        self._toolbar_btn(tb, "✏  Edit",      C['accent'],  self._edit_user).pack(side='left', padx=4)
        self._toolbar_btn(tb, "🗑  Delete",    C['danger'],  self._delete_user).pack(side='left', padx=4)

        cols = {'ID': 50, 'Full Name': 200, 'Email': 220, 'Role': 90, 'Status': 80, 'Joined': 100}
        tf, self._user_tv = self._treeview(self.main, cols)
        tf.pack(fill='both', expand=True, padx=16, pady=(0, 12))
        self._load_users()

    def _load_users(self):
        self._user_tv.delete(*self._user_tv.get_children())
        for i, u in enumerate(db.get_all_users()):
            self._user_tv.insert('', 'end', iid=str(u['id']),
                                 values=(u['id'], u['fullname'], u['email'],
                                         u['role'], u['status'], u['created_at'][:10]),
                                 tags=('even' if i % 2 == 0 else 'odd',))

    def _add_user(self): self._user_form(None)

    def _edit_user(self):
        sel = self._user_tv.selection()
        if not sel: messagebox.showwarning("Select", "Select a user."); return
        user = next((u for u in db.get_all_users() if str(u['id']) == sel[0]), None)
        if user: self._user_form(user)

    def _delete_user(self):
        sel = self._user_tv.selection()
        if not sel: return
        if int(sel[0]) == self.current_user['id']:
            messagebox.showwarning("Error", "You cannot delete yourself.")
            return
        if messagebox.askyesno("Confirm", "Delete this user?"):
            db.delete_user(int(sel[0]))
            self._load_users()

    def _user_form(self, user=None):
        win = tk.Toplevel(self)
        win.title("Add User" if not user else "Edit User")
        win.geometry("400x440")
        win.configure(bg=C['white'])
        win.grab_set()

        tk.Label(win, text="User Details", font=(FONT, 13, 'bold'),
                 bg=C['white'], fg=C['primary']).pack(pady=(16, 4))
        tk.Frame(win, bg=C['grey_lt'], height=1).pack(fill='x', pady=6)

        form = tk.Frame(win, bg=C['white'])
        form.pack(fill='x', padx=24)
        fields = {}

        def row(label, key, default='', show=None):
            tk.Label(form, text=label, font=(FONT, 9), bg=C['white'], fg=C['grey'], anchor='w').pack(fill='x', pady=(6, 1))
            e = tk.Entry(form, font=(FONT, 10), bg='#EBF5FB', bd=1, relief='flat', show=show)
            e.pack(fill='x', ipady=6)
            if default: e.insert(0, default)
            fields[key] = e

        row("Full Name *", 'name',     user['fullname'] if user else '')
        row("Email *",     'email',    user['email']    if user else '')
        if not user:
            row("Password *", 'password', '', show='•')

        tk.Label(form, text="Role", font=(FONT, 9), bg=C['white'], fg=C['grey'], anchor='w').pack(fill='x', pady=(6, 1))
        role_var = tk.StringVar(value=user['role'] if user else 'Staff')
        ttk.Combobox(form, textvariable=role_var, values=['Admin', 'Manager', 'Staff'],
                     state='readonly', font=(FONT, 10)).pack(fill='x', ipady=4)

        tk.Label(form, text="Status", font=(FONT, 9), bg=C['white'], fg=C['grey'], anchor='w').pack(fill='x', pady=(6, 1))
        status_var = tk.StringVar(value=user['status'] if user else 'Active')
        ttk.Combobox(form, textvariable=status_var, values=['Active', 'Inactive'],
                     state='readonly', font=(FONT, 10)).pack(fill='x', ipady=4)

        def save():
            name  = fields['name'].get().strip()
            email = fields['email'].get().strip()
            if not name or not email:
                messagebox.showwarning("Validation", "Name and email required.", parent=win)
                return
            if user:
                db.update_user(user['id'], name, email, role_var.get(), status_var.get())
            else:
                pwd = fields['password'].get()
                if not pwd:
                    messagebox.showwarning("Validation", "Password required.", parent=win)
                    return
                ok, msg = db.create_user(name, email, pwd, role_var.get())
                if not ok:
                    messagebox.showerror("Error", msg, parent=win)
                    return
            win.destroy()
            self._load_users()

        tk.Frame(win, bg=C['white'], height=14).pack()
        bf = tk.Frame(win, bg=C['white'])
        bf.pack(fill='x', padx=24)
        self._toolbar_btn(bf, "💾  Save", C['primary'], save).pack(side='left', fill='x', expand=True, padx=(0, 4))
        self._toolbar_btn(bf, "Cancel",   C['grey'],    win.destroy).pack(side='left', fill='x', expand=True)

    # ══════════════════════════════════════════════════════
    #  REPORTS
    # ══════════════════════════════════════════════════════
    def _show_reports(self):
        self._clear_main()
        self._page_header("📊 Reports", "  Generate and export PDF reports")

        content = tk.Frame(self.main, bg=C['bg'])
        content.pack(fill='both', expand=True, padx=20, pady=16)

        # Date range picker (shared)
        df = tk.LabelFrame(content, text=" Date Range Filter ", font=(FONT, 10, 'bold'),
                            bg=C['white'], fg=C['primary'])
        df.pack(fill='x', pady=(0, 16))

        drow = tk.Frame(df, bg=C['white'])
        drow.pack(padx=16, pady=12)
        tk.Label(drow, text="From:", bg=C['white'], font=(FONT, 10)).pack(side='left')
        self._rpt_from = tk.Entry(drow, width=12, font=(FONT, 10), bg='#EBF5FB')
        self._rpt_from.insert(0, datetime.now().strftime('%Y-%m-01'))
        self._rpt_from.pack(side='left', padx=8, ipady=5)
        tk.Label(drow, text="To:", bg=C['white'], font=(FONT, 10)).pack(side='left')
        self._rpt_to = tk.Entry(drow, width=12, font=(FONT, 10), bg='#EBF5FB')
        self._rpt_to.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self._rpt_to.pack(side='left', padx=8, ipady=5)

        # Report cards
        cards_frame = tk.Frame(content, bg=C['bg'])
        cards_frame.pack(fill='both', expand=True)

        reports = [
            ("📈 Sales Report",          "Sales transactions for the selected date range",
             C['success'],  self._gen_sales_report),
            ("📦 Inventory Status",       "Current stock levels, values & status for all products",
             C['primary'],  self._gen_inventory_report),
            ("🏆 Top Selling Products",   "Best-selling products ranked by units sold",
             C['accent'],   self._gen_top_products_report),
            ("👥 Customer Report",        "Customer order history and total spend",
             '#8E44AD',     self._gen_customer_report),
            ("🚚 Purchase Report",        "Supplier purchases for the selected date range",
             C['danger'],   self._gen_purchase_report),
            ("⚠  Low Stock Alert",       "Products at or below reorder level requiring action",
             C['warning'],  self._gen_low_stock_report),
        ]

        for i, (title, desc, color, cmd) in enumerate(reports):
            row, col = divmod(i, 3)
            card = tk.Frame(cards_frame, bg=C['white'], bd=1, relief='groove')
            card.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
            cards_frame.columnconfigure(col, weight=1)

            tk.Label(card, text=title, font=(FONT, 12, 'bold'),
                     bg=C['white'], fg=color).pack(anchor='w', padx=16, pady=(14, 4))
            tk.Label(card, text=desc, font=(FONT, 9),
                     bg=C['white'], fg=C['grey'], wraplength=240, justify='left').pack(anchor='w', padx=16)
            tk.Frame(card, bg=C['white'], height=10).pack()
            tk.Button(card, text="Generate PDF  →", font=(FONT, 9, 'bold'),
                      bg=color, fg=C['white'], bd=0, padx=14, pady=7,
                      cursor='hand2', activebackground=C['primary_dk'],
                      command=cmd).pack(anchor='w', padx=16, pady=(0, 14))

    def _gen_sales_report(self):
        start = self._rpt_from.get().strip()
        end   = self._rpt_to.get().strip()
        rows  = db.report_sales_by_period(start, end)
        if not rows:
            messagebox.showinfo("No Data", f"No sales found between {start} and {end}.")
            return
        path = rpt.generate_sales_report(rows, start, end)
        messagebox.showinfo("Report Ready", f"Sales report generated!\n{path}")
        open_file(path)

    def _gen_inventory_report(self):
        rows = db.report_inventory_status()
        if not rows:
            messagebox.showinfo("No Data", "No products in database.")
            return
        path = rpt.generate_inventory_report(rows)
        messagebox.showinfo("Report Ready", f"Inventory report generated!\n{path}")
        open_file(path)

    def _gen_top_products_report(self):
        rows = db.report_top_selling_products()
        if not rows:
            messagebox.showinfo("No Data", "No sales data found.")
            return
        path = rpt.generate_top_products_report(rows)
        messagebox.showinfo("Report Ready", f"Top products report generated!\n{path}")
        open_file(path)

    def _gen_customer_report(self):
        rows = db.report_customer_purchases()
        if not rows:
            messagebox.showinfo("No Data", "No customer data found.")
            return
        path = rpt.generate_customer_report(rows)
        messagebox.showinfo("Report Ready", f"Customer report generated!\n{path}")
        open_file(path)

    def _gen_purchase_report(self):
        start = self._rpt_from.get().strip()
        end   = self._rpt_to.get().strip()
        rows  = db.report_purchase_by_period(start, end)
        if not rows:
            messagebox.showinfo("No Data", f"No purchases found between {start} and {end}.")
            return
        path = rpt.generate_purchase_report(rows, start, end)
        messagebox.showinfo("Report Ready", f"Purchase report generated!\n{path}")
        open_file(path)

    def _gen_low_stock_report(self):
        rows = db.get_low_stock_products()
        if not rows:
            messagebox.showinfo("All Good", "✅ No low stock items detected.")
            return
        path = rpt.generate_low_stock_report(rows)
        messagebox.showinfo("Report Ready", f"Low stock report generated!\n{path}")
        open_file(path)


# ════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════
def _start_login():
    login = LoginWindow()
    login.mainloop()
    return login.current_user


def main():
    db.initialize_database()
    user = _start_login()
    if user:
        app = IMSApp(user)
        app.mainloop()


if __name__ == '__main__':
    main()
