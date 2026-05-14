"""
IMS - Demo Data Seeder
Run this script once to populate the database with realistic sample data.
Usage: python seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ims import database as db
from datetime import datetime, timedelta
import random

db.initialize_database()

print("🌱 Seeding demo data...")

# ── Additional categories ──
for cat, desc in [
    ('Phones',       'Smartphones and feature phones'),
    ('Laptops',      'Portable computers and ultrabooks'),
    ('Accessories',  'Cables, cases, chargers'),
    ('Televisions',  'Smart TVs and displays'),
    ('Audio',        'Speakers, headphones, earbuds'),
    ('Tablets',      'iPads, Android tablets'),
    ('Cameras',      'Digital cameras and accessories'),
]:
    db.create_category(cat, desc)

cats = {c['name']: c['id'] for c in db.get_all_categories()}

# ── Suppliers ──
suppliers = [
    ('SUP-001', 'TechHub Distributors',   'Nairobi',    '0720000001', 'techhub@email.com'),
    ('SUP-002', 'Elite Electronics Ltd',  'Mombasa',    '0720000002', 'elite@email.com'),
    ('SUP-003', 'Global Gadgets Import',  'Kampala',    '0720000003', 'ggimport@email.com'),
    ('SUP-004', 'SilkRoute Tech',         'Dar es Salaam','0720000004','silkroute@email.com'),
]
for args in suppliers:
    db.create_supplier(*args)
sups = {s['suppliercode']: s['id'] for s in db.get_all_suppliers()}

# ── Products ──
products = [
    ('PRD-001', 'Samsung Galaxy A54',        'Phones',      'Android smartphone 128GB',        45,  32000, 5,  None),
    ('PRD-002', 'iPhone 14',                 'Phones',      'Apple smartphone 256GB',           18,  95000, 3,  None),
    ('PRD-003', 'Tecno Spark 20',            'Phones',      'Budget Android phone',             80,  12000, 10, None),
    ('PRD-004', 'Xiaomi Redmi Note 12',      'Phones',      '6.67" AMOLED display',             30,  18000, 5,  None),
    ('PRD-005', 'HP EliteBook 840',          'Laptops',     'Intel Core i7, 16GB RAM',          12,  85000, 3,  None),
    ('PRD-006', 'Dell Inspiron 15',          'Laptops',     'Core i5, 8GB RAM, 512GB SSD',     20,  62000, 4,  None),
    ('PRD-007', 'Lenovo ThinkPad E14',       'Laptops',     'Business laptop i5 Gen 12',        8,   72000, 3,  None),
    ('PRD-008', 'MacBook Air M2',            'Laptops',     'Apple Silicon, 8GB 256GB',         5,  145000, 2,  None),
    ('PRD-009', 'Samsung 55" Smart TV',      'Televisions', '4K UHD Smart TV',                  10,  55000, 2,  None),
    ('PRD-010', 'LG 43" LED TV',             'Televisions', 'Full HD LED Television',           15,  32000, 3,  None),
    ('PRD-011', 'JBL Charge 5 Speaker',      'Audio',       'Portable Bluetooth speaker',       25,  12000, 5,  None),
    ('PRD-012', 'Sony WH-1000XM5 Headphones','Audio',       'Noise cancelling headphones',      12,  28000, 3,  None),
    ('PRD-013', 'Samsung Galaxy Tab S8',     'Tablets',     '11" OLED tablet 128GB',           8,   65000, 3,  None),
    ('PRD-014', 'iPad 10th Gen',             'Tablets',     '10.9" Retina display 64GB',       6,   58000, 2,  None),
    ('PRD-015', 'USB-C Charging Cable 2m',  'Accessories', 'Fast charging cable',             200,   450, 30, None),
    ('PRD-016', 'Screen Protector Universal','Accessories', 'Tempered glass protector',        150,   350, 20, None),
    ('PRD-017', 'Anker 65W USB-C Charger',  'Accessories', 'GaN compact charger',              40,  3500, 10, None),
    ('PRD-018', 'Canon EOS M50 Mark II',    'Cameras',     'Mirrorless camera 24MP',           4,   75000, 2, '2026-12-31'),
    ('PRD-019', 'Sony ZV-E10 Camera',       'Cameras',     'Vlogging mirrorless camera',       3,   65000, 2,  None),
    ('PRD-020', 'Wireless Mouse Logitech',  'Accessories', 'Silent wireless mouse',            60,  2800, 15, None),
]
for p in products:
    db.create_product(p[0], p[1], cats.get(p[2]), p[3], p[4], p[5], p[6], p[7])

# ── Customers ──
customers = [
    ('Alice Wanjiru',   '0712345001', 'alice@email.com',   'Westlands, Nairobi'),
    ('Brian Omondi',    '0712345002', 'brian@email.com',   'Kilimani, Nairobi'),
    ('Carol Muthoni',   '0712345003', 'carol@email.com',   'Mombasa Road'),
    ('David Kamau',     '0712345004', 'david@email.com',   'Thika Road'),
    ('Esther Achieng',  '0712345005', 'esther@email.com',  'Kisumu Town'),
    ('Felix Mutua',     '0712345006', 'felix@email.com',   'Nakuru CBD'),
    ('Grace Chebet',    '0712345007', 'grace@email.com',   'Eldoret'),
    ('Hassan Omar',     '0712345008', 'hassan@email.com',  'Mombasa CBD'),
    ('Irene Njoki',     '0712345009', 'irene@email.com',   'Parklands'),
    ('James Otieno',    '0712345010', 'james@email.com',   'Langata'),
]
for c in customers:
    db.create_customer(*c)

custs = db.get_all_customers()
prods = db.get_all_products()
admin = db.authenticate_user('admin@ims.com', 'admin123')

# ── Seed purchases ──
print("  → Creating purchases...")
for i in range(5):
    supplier_id = list(sups.values())[i % len(sups)]
    items = []
    selected = random.sample(prods, random.randint(2, 4))
    for p in selected:
        qty  = random.randint(5, 30)
        cost = p['unit_price'] * random.uniform(0.6, 0.75)
        items.append({'product_id': p['id'], 'quantity': qty, 'unit_cost': round(cost, 2)})
    db.create_purchase(supplier_id, admin['id'], items)

# ── Seed sales orders ──
print("  → Creating sales orders...")
prods = db.get_all_products()  # refresh after purchases
for i in range(20):
    cust = random.choice(custs)
    cart = []
    selected = random.sample(prods, random.randint(1, 3))
    for p in selected:
        available = p['quantity']
        if available > 0:
            qty = random.randint(1, min(3, available))
            cart.append({'product_id': p['id'], 'quantity': qty, 'unit_price': p['unit_price']})
    if cart:
        db.create_order(cust['id'], admin['id'], cart)
    prods = db.get_all_products()  # refresh stock

print("\n✅ Demo data seeded successfully!")
print("━" * 50)
print("  Admin Login:")
print("  Email   : admin@ims.com")
print("  Password: admin123")
print("━" * 50)
print("\nRun the application with: python main.py")
