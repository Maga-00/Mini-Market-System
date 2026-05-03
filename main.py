import json
import time
import os
import datetime

# Məlumatların idarə edilməsi
def load_data(filename, default):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(default, f, indent=4)
        return default
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def log_event(username, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(f"history_{username}.log", "a", encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")

# Giriş Sistemi
def login():
    users = load_data('users.json', [])
    attempts = 0
    while attempts < 3:
        u_name = input("\nİstifadəçi adı: ")
        u_pass = input("Şifrə: ")
        for u in users:
            if u['username'] == u_name and u['password'] == u_pass:
                log_event(u_name, "LOGIN_SUCCESS")
                return u, users
        attempts += 1
        print(f"Səhv! Cəhd {attempts}/3")
        if attempts == 3:
            print("10 saniyə gözləyin...")
            for i in range(10, 0, -1):
                print(f"Gözləyin: {i} san", end="\r")
                time.sleep(1)
            attempts = 0 
    return None, None

# Əsas Menyu
def main_menu(user, all_users):
    products = load_data('products.json', {})
    basket = []
    fav_file = f"favorites_{user['username']}.json"
    favorites = load_data(fav_file, [])

    while True:
        print(f"\n--- MAĞAZA (Balans: {user['balance']} AZN) ---")
        print("1. Kateqoriyalar\n2. Səbətim\n3. Favoritlərim\n4. Tarixçə (Log)\n5. Şifrəni Dəyiş\n0. Çıxış")
        choice = input("Seçim: ")

        if choice == "1":
            cats = list(products.keys())
            for i, c in enumerate(cats, 1): print(f"{i}. {c}")
            c_idx = int(input("Kateqoriya: ")) - 1
            sel_cat = cats[c_idx]
            for p in products[sel_cat]: print(f"ID:{p['id']} | {p['name']} - {p['price']} AZN")
            
            p_id = int(input("Məhsul ID (Geri: 0): "))
            if p_id != 0:
                prod = next(p for p in products[sel_cat] if p['id'] == p_id)
                qty = int(input(f"{prod['name']} miqdarı: "))
                op = input("[B] Səbət | [F] Favorit | [X] Geri: ").upper()
                if op == 'B':
                    basket.append({"name": prod['name'], "price": prod['price'], "qty": qty, "total": prod['price']*qty})
                    log_event(user['username'], f"BASKET_ADD: {prod['name']} x{qty}")
                elif op == 'F':
                    favorites.append(prod)
                    save_data(fav_file, favorites)
                    log_event(user['username'], f"FAV_ADD: {prod['name']}")

        elif choice == "2":
            total = sum(i['total'] for i in basket)
            for i, m in enumerate(basket): print(f"{i}. {m['name']} x{m['qty']} = {m['total']} AZN")
            print(f"Cəmi: {total} AZN")
            if input("Almaq üçün 'ok' yazın: ").lower() == 'ok':
                if user['balance'] >= total:
                    user['balance'] -= total
                    save_data('users.json', all_users)
                    log_event(user['username'], f"CHECKOUT_SUCCESS: {total} AZN")
                    basket = []
                    print("Uğurlu!")
                else: print("Balans yetərli deyil!")

        elif choice == "4":
            log_path = f"history_{user['username']}.log"
            if os.path.exists(log_path):
                with open(log_path, "r") as f: print(f.read())

        elif choice == "0": break

# Başla
u_obj, all_u = login()
if u_obj: main_menu(u_obj, all_u)