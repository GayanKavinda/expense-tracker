import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def make_request(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, err_body
    except Exception as e:
        return 500, str(e)

def main():
    print("=== Starting API Flow Test ===")
    
    # 1. Register
    email = "test_flow_user@example.com"
    password = "password123!"
    print(f"\n1. Registering user: {email}...")
    status, res = make_request("/auth/register", "POST", {"email": email, "password": password})
    if status in (200, 201):
        print("Registration successful!")
    elif status == 400 and "already registered" in str(res):
        print("User already registered. Proceeding to login...")
    else:
        print(f"Registration status {status}: {res}")

    # 2. Login
    print("\n2. Logging in...")
    # Swagger/FastAPI OAuth2 password flow expects form data, but our login endpoint accepts JSON too?
    # Let's try JSON first, if not, we can do application/x-www-form-urlencoded if needed.
    status, res = make_request("/auth/login", "POST", {"email": email, "password": password})
    if status != 200:
        print(f"Failed to login (status {status}): {res}")
        return
    
    token = res["access_token"]
    print("Login successful! Token acquired.")

    # 3. Create Categories
    categories = [
        {"name": "Food", "color": "#ff0000", "icon": "food"},
        {"name": "Transport", "color": "#00ff00", "icon": "car"},
        {"name": "Utilities", "color": "#0000ff", "icon": "bolt"}
    ]
    category_ids = {}
    print("\n3. Creating Categories...")
    for cat in categories:
        status, res = make_request("/categories/", "POST", cat, token)
        if status in (200, 201):
            category_ids[cat["name"]] = res["id"]
            print(f"Created category '{cat['name']}' with ID {res['id']}")
        else:
            print(f"Failed to create category '{cat['name']}' (status {status}): {res}")
            # Try to fetch existing categories if conflict
            if status == 400 or status == 409 or True:
                status_get, res_get = make_request("/categories/", "GET", token=token)
                if status_get == 200:
                    for existing_cat in res_get:
                        if existing_cat["name"] == cat["name"]:
                            category_ids[cat["name"]] = existing_cat["id"]
                            print(f"Found existing category '{cat['name']}' with ID {existing_cat['id']}")

    # 4. Add Expenses
    expenses = [
        {"amount": 1500.00, "currency": "LKR", "description": "Lunch", "date": "2026-06-01", "category_id": category_ids.get("Food")},
        {"amount": 850.00, "currency": "LKR", "description": "Snacks", "date": "2026-06-02", "category_id": category_ids.get("Food")},
        {"amount": 5000.00, "currency": "LKR", "description": "Fuel", "date": "2026-06-03", "category_id": category_ids.get("Transport")},
        {"amount": 120.00, "currency": "LKR", "description": "Bus ticket", "date": "2026-06-04", "category_id": category_ids.get("Transport")},
        {"amount": 12000.00, "currency": "LKR", "description": "Electricity bill", "date": "2026-06-05", "category_id": category_ids.get("Utilities")},
        {"amount": 2200.00, "currency": "LKR", "description": "Groceries", "date": "2026-06-05", "category_id": category_ids.get("Food")},
        {"amount": 4500.00, "currency": "LKR", "description": "Water bill", "date": "2026-06-06", "category_id": category_ids.get("Utilities")}
    ]
    
    print("\n4. Adding Expenses...")
    for exp in expenses:
        status, res = make_request("/expenses/", "POST", exp, token)
        if status in (200, 201):
            print(f"Added expense: {exp['description']} ({exp['amount']} {exp['currency']})")
        else:
            print(f"Failed to add expense {exp['description']} (status {status}): {res}")

    # 5. GET /insights/
    print("\n5. GETting /insights/...")
    status, res = make_request("/insights/", "GET", token=token)
    if status == 200:
        print("Response /insights/:")
        print(json.dumps(res, indent=2))
    else:
        print(f"Failed to get insights (status {status}): {res}")

    # 6. GET /insights/monthly
    print("\n6. GETting /insights/monthly...")
    status, res = make_request("/insights/monthly", "GET", token=token)
    if status == 200:
        print("Response /insights/monthly:")
        print(json.dumps(res, indent=2))
    else:
        print(f"Failed to get monthly insights (status {status}): {res}")

if __name__ == "__main__":
    main()
