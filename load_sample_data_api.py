import requests
import random
import time

API_BASE = "http://localhost:8000/api"  # Change to your QA/Dev API base URL
ADMIN_USER = "admin1"
ADMIN_PASS = "testpass"

# Helper: Auth and get JWT token
def get_token():
    resp = requests.post(f"{API_BASE}/token/", json={"username": ADMIN_USER, "password": ADMIN_PASS})
    resp.raise_for_status()
    return resp.json()["access"]

def api_call(method, endpoint, token=None, payload=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{API_BASE}{endpoint}"
    resp = requests.request(method, url, headers=headers, json=payload)
    if resp.status_code not in (200, 201, 204):
        print(f"API {method} {endpoint} failed: {resp.status_code} {resp.text}")
    return resp

# Helper: Delete all data in dependency order
RESOURCE_ORDER = [
    "/stock-movements/", "/stock-adjustments/", "/purchase-orders/", "/sales-orders/", "/stock/", "/products/", "/categories/", "/suppliers/", "/warehouses/", "/locations/", "/users/", "/customers/"
]

def delete_all(token):
    for endpoint in RESOURCE_ORDER:
        resp = api_call("GET", endpoint, token)
        if resp.status_code == 200:
            for obj in resp.json().get("results", []):
                obj_id = obj.get("id")
                if obj_id:
                    del_resp = api_call("DELETE", f"{endpoint}{obj_id}/", token)
                    # If deleting a category fails due to ProtectedError, skip and continue
                    if endpoint == "/categories/" and del_resp.status_code == 500 and "ProtectedError" in del_resp.text:
                        print(f"Skipping category {obj_id} deletion due to ProtectedError.")

# Create categories
CATEGORY_NAMES = [
    'Smartphones', 'Laptops', 'Tablets', 'Televisions', 'Headphones', 'Wearables',
    'Refrigerators', 'Washing Machines', 'Microwaves', 'Air Conditioners', 'Cameras',
    'Printers', 'Monitors', 'Networking', 'Smart Home', 'Speakers', 'Coffee Makers',
    'Vacuum Cleaners', 'Ovens', 'Dishwashers', 'Fitness Equipment', 'Lighting', 'Security',
    'Furniture', 'Clothing', 'Shoes', 'Bags', 'Watches', 'Jewelry', 'Toys', 'Books', 'Stationery',
    'Garden', 'Tools', 'Automotive', 'Pet Supplies', 'Groceries', 'Beauty', 'Health', 'Sports', 'Outdoors'
]

def create_categories(token):
    ids = []
    for name in CATEGORY_NAMES[:40]:
        resp = api_call("POST", "/categories/", token, {"name": name})
        if resp.status_code == 201:
            ids.append(resp.json()["id"])
    return ids

# Create suppliers
SUPPLIER_DATA = [
    ("Tech Distributors", "tech@distributors.com"),
    ("Global Electronics", "sales@globalelectronics.com"),
    ("Appliance Hub", "info@appliancehub.com"),
    ("Fashion Mart", "contact@fashionmart.com"),
    ("Sports World", "orders@sportsworld.com")
]

def create_suppliers(token):
    ids = []
    for name, email in SUPPLIER_DATA:
        resp = api_call("POST", "/suppliers/", token, {"name": name, "email": email})
        if resp.status_code == 201:
            ids.append(resp.json()["id"])
    return ids

# Create warehouses
WAREHOUSE_DATA = [
    ("Central Warehouse", 5000, "100 Main St"),
    ("East Depot", 3000, "200 East St"),
    ("West Storage", 2000, "300 West St")
]

def create_warehouses(token):
    ids = []
    for name, cap, addr in WAREHOUSE_DATA:
        resp = api_call("POST", "/warehouses/", token, {"name": name, "capacity": cap, "address": addr})
        if resp.status_code == 201:
            ids.append(resp.json()["id"])
    return ids

# Create locations

def create_locations(token, warehouse_ids):
    ids = []
    for wh_id in warehouse_ids:
        for i in range(1, 6):
            resp = api_call("POST", "/locations/", token, {"name": f"WH{wh_id}-Loc{i}", "warehouse": wh_id, "type": "Bin"})
            if resp.status_code == 201:
                ids.append(resp.json()["id"])
    return ids

# Create products
BRANDS = [
    ("Apple", ["iPhone 14", "MacBook Pro", "iPad Air"]),
    ("Samsung", ["Galaxy S23", "Galaxy Tab S8", "QLED TV"]),
    ("Sony", ["Bravia TV", "WH-1000XM5", "PlayStation 5"]),
    ("LG", ["OLED TV", "Gram Laptop", "Refrigerator"]),
    ("Dell", ["XPS 13", "Inspiron 15", "Monitor"]),
    ("HP", ["Spectre x360", "DeskJet Printer", "Envy Laptop"]),
    ("Lenovo", ["ThinkPad X1", "Yoga Slim", "Legion 5"]),
    ("Whirlpool", ["Washing Machine", "Microwave", "Refrigerator"]),
    ("Bosch", ["Dishwasher", "Oven", "Vacuum Cleaner"]),
    ("Nike", ["Air Max", "Revolution 5", "Metcon 7"]),
    ("Adidas", ["Ultraboost", "Superstar", "Stan Smith"]),
    ("Canon", ["EOS R5", "PowerShot G7", "PIXMA Printer"]),
    ("Philips", ["Hue Bulb", "Air Fryer", "Sonicare"]),
    ("Asus", ["ROG Phone", "ZenBook", "TUF Gaming"]),
    ("Panasonic", ["Lumix Camera", "Microwave", "TV"]),
    ("Puma", ["RS-X", "Future Rider", "Cali"]),
    ("Reebok", ["Nano X", "Classic Leather", "Floatride"]),
    ("Casio", ["G-Shock", "Edifice", "Calculator"]),
    ("Fossil", ["Gen 6", "Leather Bag", "Watch"]),
    ("Levi’s", ["501 Jeans", "Trucker Jacket", "T-Shirt"])
]

def create_products(token, category_ids, supplier_ids, warehouse_ids):
    ids = []
    sku_counter = 1000
    used_skus = set()
    used_barcodes = set()
    for cat_id in category_ids:
        for brand, models in BRANDS:
            for model in models:
                name = f"{brand} {model}"
                # Guarantee unique SKU/barcode
                while True:
                    sku = f"SKU{sku_counter}"
                    barcode = f"BAR{sku_counter}"
                    if sku not in used_skus and barcode not in used_barcodes:
                        used_skus.add(sku)
                        used_barcodes.add(barcode)
                        break
                    sku_counter += 1
                unit_price = 100 + (sku_counter % 500)
                payload = {
                    "name": name,
                    "sku": sku,
                    "barcode": barcode,
                    "category_id": cat_id,
                    "supplier": supplier_ids[sku_counter % len(supplier_ids)],
                    "warehouse": warehouse_ids[sku_counter % len(warehouse_ids)],
                    "unit_price": unit_price,
                    "price": unit_price
                }
                resp = api_call("POST", "/products/", token, payload)
                if resp.status_code == 201:
                    ids.append(resp.json()["id"])
                sku_counter += 1
                if len(ids) > 40:
                    break
            if len(ids) > 40:
                break
        if len(ids) > 40:
            break
    return ids

# Create stock

def create_stock(token, product_ids, warehouse_ids, location_ids):
    ids = []
    for i, prod_id in enumerate(product_ids):
        wh_id = warehouse_ids[i % len(warehouse_ids)]
        loc_id = location_ids[i % len(location_ids)]
        qty = random.randint(10, 50)
        payload = {
            "product": prod_id,
            "warehouse": wh_id,
            "location": loc_id,
            "quantity": qty
        }
        resp = api_call("POST", "/stock/", token, payload)
        if resp.status_code == 201:
            ids.append(resp.json()["id"])
    return ids

# Main script
if __name__ == "__main__":
    token = get_token()
    print("Deleting all existing data...")
    delete_all(token)

    # Verify products are deleted before creating new ones
    prod_check = api_call("GET", "/products/", token)
    prod_results = prod_check.json().get("results", []) if prod_check.status_code == 200 else []
    if prod_results:
        print(f"WARNING: {len(prod_results)} products remain after deletion. Please fix manually and retry.")
        import sys
        sys.exit(1)
    else:
        print("Creating categories...")
        category_ids = create_categories(token)
        print("Creating suppliers...")
        supplier_ids = create_suppliers(token)
        print("Creating warehouses...")
        warehouse_ids = create_warehouses(token)
        print("Creating locations...")
        location_ids = create_locations(token, warehouse_ids)
        print("Creating products...")
        product_ids = create_products(token, category_ids, supplier_ids, warehouse_ids)

    print("Creating stock...")
    # If product_ids is empty, skip stock creation
    if product_ids:
        stock_ids = create_stock(token, product_ids, warehouse_ids, location_ids)
    else:
        print("No products available for stock creation.")
    print("Sample data loaded for all FE pages!")
