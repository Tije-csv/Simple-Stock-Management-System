#!/usr/bin/env python3
import sqlite3
from typing import Optional

DB_NAME = "stocks.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                stock INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                supplier_id INTEGER,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                date TEXT NOT NULL DEFAULT (date('now')),
                type TEXT NOT NULL CHECK(type IN ('IN','OUT')),
                FOREIGN KEY(product_id) REFERENCES Products(id),
                FOREIGN KEY(supplier_id) REFERENCES Suppliers(id)
            )
            """
        )
        conn.commit()
    print("Database initialized.")


def create_product(name: str, price: float):
    name = name.strip()
    if not name:
        print("Product name cannot be empty.")
        return
    if price < 0:
        print("Price cannot be negative.")
        return

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO Products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
    print(f"Product '{name}' added.")


def add_supplier(name: str, contact: str):
    name = name.strip()
    contact = str(contact).strip()
    if not name:
        print("Supplier name cannot be empty.")
        return
    if not contact:
        print("Supplier contact cannot be empty.")
        return

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO Suppliers (name, contact) VALUES (?, ?)", (name, contact))
        conn.commit()
    print(f"Supplier '{name}' added.")


def product_exists(product_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM Products WHERE id = ?", (product_id,))
        return cur.fetchone() is not None


def supplier_exists(supplier_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM Suppliers WHERE id = ?", (supplier_id,))
        return cur.fetchone() is not None


def add_stock(product_id: int, supplier_id: Optional[int], quantity: int):
    if quantity <= 0:
        print("Quantity must be a positive integer.")
        return
    if not product_exists(product_id):
        print("Product not found.")
        return
    if supplier_id is not None and not supplier_exists(supplier_id):
        print("Supplier not found.")
        return

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Transactions (product_id, supplier_id, quantity, type) VALUES (?, ?, ?, 'IN')",
            (product_id, supplier_id, quantity),
        )
        cur.execute("UPDATE Products SET stock = stock + ? WHERE id = ?", (quantity, product_id))
        conn.commit()
    print(f"Added {quantity} unit(s) to product id {product_id}.")


def remove_stock(product_id: int, quantity: int):
    if quantity <= 0:
        print("Quantity must be a positive integer.")
        return
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT stock FROM Products WHERE id = ?", (product_id,))
        row = cur.fetchone()
        if row is None:
            print("Product not found.")
            return
        current_stock = row["stock"]
        if current_stock < quantity:
            print("Error: Insufficient stock.")
            return
        cur.execute(
            "INSERT INTO Transactions (product_id, supplier_id, quantity, type) VALUES (?, NULL, ?, 'OUT')",
            (product_id, quantity),
        )
        cur.execute("UPDATE Products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
        conn.commit()
    print(f"Removed {quantity} unit(s) from product id {product_id}.")


def list_products():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, price, stock FROM Products ORDER BY id")
        results = cur.fetchall()
        if not results:
            print("No products found.")
            return
        print(f"{'ID':>3}  {'Name':<25}  {'Price':>8}  {'Stock':>6}")
        print("-" * 48)
        for r in results:
            print(f"{r['id']:>3}  {r['name']:<25}  {r['price']:>8.2f}  {r['stock']:>6}")


def view_products_history(product_id: int):
    if not product_exists(product_id):
        print("Product not found.")
        return
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT Transactions.date AS date, Transactions.quantity AS quantity,
                   Transactions.type AS type, COALESCE(Suppliers.name, 'N/A') AS supplier
            FROM Transactions
            LEFT JOIN Suppliers ON Transactions.supplier_id = Suppliers.id
            WHERE Transactions.product_id = ?
            ORDER BY Transactions.date DESC, Transactions.id DESC
            """,
            (product_id,),
        )
        rows = cur.fetchall()
        if not rows:
            print("No transaction history for this product.")
            return
        print(f"History for product id {product_id}:")
        print(f"{'Date':<12}  {'Type':<3}  {'Qty':>4}  {'Supplier'}")
        print("-" * 40)
        for r in rows:
            print(f"{r['date']:<12}  {r['type']:<3}  {r['quantity']:>4}  {r['supplier']}")


def update_product_price(product_id: int, new_price: float):
    if new_price < 0:
        print("Price cannot be negative.")
        return
    if not product_exists(product_id):
        print("Product not found.")
        return
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE Products SET price = ? WHERE id = ?", (new_price, product_id))
        conn.commit()
    print(f"Updated price of product id {product_id} to {new_price:.2f}.")


def del_supplier(supplier_id: int):
    if not supplier_exists(supplier_id):
        print("Supplier not found.")
        return
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM Suppliers WHERE id = ?", (supplier_id,))
        conn.commit()
    print(f"Deleted supplier id {supplier_id}.")


def prompt_int(prompt: str, allow_empty: bool = False) -> Optional[int]:
    s = input(prompt).strip()
    if allow_empty and s == "":
        return None
    try:
        return int(s)
    except ValueError:
        print("Please enter a valid integer.")
        return None


def prompt_float(prompt: str) -> Optional[float]:
    s = input(prompt).strip()
    try:
        return float(s)
    except ValueError:
        print("Please enter a valid number.")
        return None


def main():
    init_db()
    while True:
        print("\n=== Stock management system ===")
        print("1. Add Product")
        print("2. Add Supplier")
        print("3. Add Stock")
        print("4. Remove Stock")
        print("5. List products")
        print("6. View Product History")
        print("7. Update Price")
        print("8. Delete Supplier")
        print("9. Exit")

        choice = prompt_int("\nEnter your choice: ")
        if choice is None:
            continue

        try:
            if choice == 1:
                name = input("Enter product name: ").strip()
                price = prompt_float("Enter product price: ")
                if price is None:
                    continue
                create_product(name, price)

            elif choice == 2:
                name = input("Enter supplier name: ").strip()
                contact = input("Enter supplier contact: ").strip()
                add_supplier(name, contact)

            elif choice == 3:
                pid = prompt_int("Product id: ")
                if pid is None:
                    continue
                sid = prompt_int("Supplier id (leave blank if none): ", allow_empty=True)
                qty = prompt_int("Quantity to add: ")
                if qty is None:
                    continue
                add_stock(pid, sid, qty)

            elif choice == 4:
                pid = prompt_int("Product id: ")
                if pid is None:
                    continue
                qty = prompt_int("Quantity to remove: ")
                if qty is None:
                    continue
                remove_stock(pid, qty)

            elif choice == 5:
                list_products()

            elif choice == 6:
                pid = prompt_int("Product id: ")
                if pid is None:
                    continue
                view_products_history(pid)

            elif choice == 7:
                pid = prompt_int("Product id: ")
                if pid is None:
                    continue
                new_price = prompt_float("Enter new price: ")
                if new_price is None:
                    continue
                update_product_price(pid, new_price)

            elif choice == 8:
                sid = prompt_int("Supplier id: ")
                if sid is None:
                    continue
                del_supplier(sid)

            elif choice == 9:
                print("Thank you, goodbye.")
                break

            else:
                print("Invalid choice. Try again.")

        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
