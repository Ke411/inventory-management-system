# 📦 Inventory Management System (IMS)
**Sales and Inventory Management System for Electronics**

A full-featured desktop application built with Python (Tkinter + SQLite + ReportLab),
following the design documented in John Kennedy's BIT 03105 project.

---

## 📋 Table of Contents
1. [Project Structure](#project-structure)
2. [System Requirements](#system-requirements)
3. [Installation (Step-by-Step)](#installation)
4. [Running the Application](#running-the-application)
5. [Database Schema](#database-schema)
6. [Module Guide](#module-guide)
7. [Reports](#reports)
8. [Default Credentials](#default-credentials)
9. [Troubleshooting](#troubleshooting)

---

## 🗂 Project Structure

```
IMS/
├── main.py              ← Application entry point (GUI)
├── seed_data.py         ← Demo data loader (run once)
├── requirements.txt     ← Python dependencies
├── ims_data.db          ← SQLite database (auto-created)
├── reports/             ← Generated PDF reports (auto-created)
└── ims/
    ├── __init__.py
    ├── database.py      ← All database operations (SQLite)
    └── reports.py       ← PDF report generator (ReportLab)
```

---

## 💻 System Requirements

| Component       | Minimum Requirement                         |
|-----------------|---------------------------------------------|
| OS              | Windows 10+ / macOS 11+ / Ubuntu 20.04+    |
| Python          | 3.8 or higher                               |
| RAM             | 512 MB                                      |
| Storage         | 100 MB free space                           |
| Display         | 1280×768 minimum                            |

---

## ⚙️ Installation (Step-by-Step)

### Step 1 — Install Python
Download and install Python 3.8+ from https://python.org/downloads/

Verify installation:
```bash
python --version
# or
python3 --version
```

### Step 2 — Download / Clone the Project
```bash
git clone <repository-url>
cd IMS
```
Or simply unzip the project folder and navigate into it.

### Step 3 — Create a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 4 — Install Dependencies
```bash
pip install -r requirements.txt
```
This installs `reportlab` (PDF generation). All other libraries (`tkinter`, `sqlite3`) 
are built into Python's standard library.

> **Linux note**: If tkinter is missing run:
> ```bash
> sudo apt-get install python3-tk   # Ubuntu/Debian
> sudo dnf install python3-tkinter  # Fedora
> ```

### Step 5 — Seed Demo Data (Optional but recommended)
```bash
python seed_data.py
```
This creates 20 products, 10 customers, 4 suppliers, 5 purchases, and 20 sales orders.

---

## ▶️ Running the Application

```bash
python main.py
```

The Login window opens. Use the default credentials below.

---

## 🔑 Default Credentials

| Field    | Value            |
|----------|------------------|
| Email    | admin@ims.com    |
| Password | admin123         |
| Role     | Admin (full access) |

---

## 🗄 Database Schema

The application uses SQLite (`ims_data.db`), auto-created on first run.

### Tables

#### `users`
| Column     | Type    | Description              |
|------------|---------|--------------------------|
| id         | INTEGER | Primary key              |
| fullname   | TEXT    | User's full name         |
| email      | TEXT    | Login email (unique)     |
| password   | TEXT    | SHA-256 hashed password  |
| role       | TEXT    | Admin / Manager / Staff  |
| status     | TEXT    | Active / Inactive        |
| created_at | TEXT    | Timestamp                |

#### `categories`
| Column      | Type    | Description           |
|-------------|---------|-----------------------|
| id          | INTEGER | Primary key           |
| name        | TEXT    | Category name (unique)|
| description | TEXT    | Optional description  |

#### `products`
| Column        | Type    | Description                   |
|---------------|---------|-------------------------------|
| id            | INTEGER | Primary key                   |
| productcode   | TEXT    | Unique product code           |
| name          | TEXT    | Product name                  |
| category_id   | INTEGER | FK → categories               |
| description   | TEXT    | Product description           |
| quantity      | INTEGER | Current stock level           |
| unit_price    | REAL    | Selling price (KES)           |
| reorder_level | INTEGER | Minimum threshold for alerts  |
| expiry_date   | TEXT    | Optional expiry date          |

#### `customers`
| Column    | Type    | Description       |
|-----------|---------|-------------------|
| id        | INTEGER | Primary key       |
| fullname  | TEXT    | Customer name     |
| phone     | TEXT    | Phone number      |
| email     | TEXT    | Email address     |
| address   | TEXT    | Physical address  |
| credit    | REAL    | Total amount paid |

#### `suppliers`
| Column       | Type    | Description              |
|--------------|---------|--------------------------|
| id           | INTEGER | Primary key              |
| suppliercode | TEXT    | Unique code              |
| fullname     | TEXT    | Supplier name            |
| location     | TEXT    | City/region              |
| phone / email| TEXT    | Contact details          |
| debit/credit | REAL    | Financial tracking       |
| balance      | REAL    | Net balance              |

#### `orders` + `order_items`
Sales transactions. Each order references a customer and user; items reference products.
Stock is automatically deducted when an order is completed.

#### `purchases` + `purchase_items`
Stock received from suppliers. Stock is automatically incremented on save.

---

## 📱 Module Guide

### Dashboard
- KPI cards: total products, customers, orders, low-stock count, monthly sales, total purchases
- Recent orders table
- Live low-stock alert table

### Products
- Add / Edit / Delete products
- Search by name or code
- Tracks: code, name, category, quantity, price, reorder level, expiry date, stock status

### Categories
- Manage product categories
- Inline edit via dialog boxes

### Customers
- Full CRUD for customer records
- Tracks total credit (spend)

### Suppliers
- Full CRUD for supplier records
- Tracks debit (amount owed)

### New Sale (Point of Sale)
1. Select customer (or walk-in)
2. Browse product list and add to cart
3. Adjust quantities
4. Click "Complete Sale"
   - Stock auto-decremented
   - Order number auto-generated
   - Customer credit updated

### Purchases
- Two tabs: New Purchase form + Purchase History
- Select supplier → add products with quantity and cost
- Stock auto-incremented on save

### Orders
- Full order history with filters
- Click "View Details" to see itemised breakdown

### Users (Admin only)
- Create / edit / deactivate user accounts
- Role-based access: Admin, Manager, Staff

### Reports
- Date range picker shared across period reports
- Six report types → professional PDF output

---

## 📊 Reports

Six PDF reports are available from the Reports module:

| Report                  | Description                                      | Format    |
|-------------------------|--------------------------------------------------|-----------|
| Sales Report            | All orders in date range, totals, KPIs           | Landscape |
| Inventory Status        | All products with stock value and status codes    | Landscape |
| Top Selling Products    | Ranked by units sold, gold/silver/bronze medals  | Portrait  |
| Customer Report         | Customers ranked by total spend                  | Portrait  |
| Purchase Report         | Supplier purchases in date range                 | Landscape |
| Low Stock Alert         | Products below reorder level, colour-coded       | Portrait  |

Reports are saved to the `reports/` folder and auto-opened with your OS PDF viewer.

---

## 🛠 Troubleshooting

### `ModuleNotFoundError: No module named 'tkinter'`
Install tkinter for your OS:
```bash
sudo apt-get install python3-tk        # Ubuntu/Debian
sudo dnf install python3-tkinter       # Fedora
brew install python-tk                 # macOS with Homebrew
```

### `ModuleNotFoundError: No module named 'reportlab'`
```bash
pip install reportlab
```

### Database locked / permission error
Ensure only one instance of the app is running.
Delete `ims_data.db` to reset to a clean state (all data will be lost).

### Login fails after password change
Passwords are SHA-256 hashed. Use `seed_data.py` to restore defaults.

---

## 🔒 Security Notes
- Passwords are hashed with SHA-256 (not stored as plain text)
- Role-based access: Users module is Admin-only
- SQLite foreign keys are enforced

---

## 📬 Contact
John Kennedy — kennedyouma784@gmail.com 
BIT 03105 Programming Project — KCA University, Sep–Dec 2024
