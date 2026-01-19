import sqlite3

def init_db():
    with sqlite3.connect("stocks.db") as connection:
        cur = connection.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS Products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, price REAL NOT NULL, stock INT DEFAULT 0)")
        cur.execute("CREATE TABLE IF NOT EXISTS Suppliers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, contact TEXT NOT NULL)")
        cur.execute("CREATE TABLE IF NOT EXISTS Transactions (id INTEGER PRIMARY KEY, product_id INT NOT NULL, supplier_id INT NOT NULL, quantity INT NOT NULL, date DEFAULT CURRENT_DATE, type TEXT NOT NULL, FOREIGN KEY(product_id) REFERENCES Products(id), FOREIGN KEY(supplier_id) REFERENCES Suppliers(id))")
        print("Database created successfully")

def create_product(name, price):
    with sqlite3.connect("stocks.db") as connection:
        cur = connection.cursor()
        cur.execute("INSERT INTO Products (name, price) VALUES (?,?)", (name, price))
        connection.commit()
        print("Added values into stocks table successfully")



def remove_stock(product_id, quantity):
    with sqlite3.connect("stocks.db") as connection:
        cur = connection.cursor()
        cur.execute("SELECT stock FROM Products WHERE id = ?", (product_id,))
        result = cur.fetchone()

        if result is None:
            print("Product not found")
            return
        
        current_stock = result[0]
        if current_stock < quantity:
            print("Error: Insufficient stock")
        else:
            cur.execute("INSERT INTO Transactions (product_id, supplier_id, quantity, type) VALUES (?, NULL, ?, 'OUT')", (product_id, quantity))
            cur.execute("UPDATE Products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
            connection.commit()
            print("Stock removed")

def list_products():
    with sqlite3.connect("stocks.db") as connection:
        cur = connection.cursor()
        cur.execute('SELECT id, name, price, stock FROM Products')
        results = cur.fetchall()
        if not results:
            print("No products")
        else:
            for row in results:
                print(row)

def update_product_price(product_id, new_price):
    with sqlite3.connect("stocks.db") as connection:
        cur = connection.cursor()
        cur.execute("UPDATE Products SET price = ? WHERE id = ?", (new_price, product_id))
        connection.commit()
        print("Price updated")



def add_supplier(name, contact):
    with sqlite3.connect("stocks.db") as connection:
        cur = connection.cursor()
        cur.execute("INSERT INTO Suppliers (name, contact) VALUES (?,?)", (name, contact))
        connection.commit()
        print("Supplier added")

def add_stock(product_id, supplier_id, quantity):
    with sqlite3.connect("stocks.db") as connection:
        cur = connection.cursor()
        cur.execute("INSERT INTO Transactions (product_id, supplier_id, quantity, type) VALUES (?,?,?,'IN')", (product_id, supplier_id, quantity))
        cur.execute("UPDATE Products SET stock = stock + ? WHERE id = ?", (quantity, product_id))
        connection.commit()
        print("Stock added")

def view_products_history(product_id):
    with sqlite3.connect("stocks.db") as connection:
        cur = connection.cursor()
        cur.execute("SELECT Transactions.date, Transactions.quantity, Transactions.type, Suppliers.name FROM Transactions LEFT JOIN Suppliers ON Transactions.supplier_id = Suppliers.id WHERE Transactions.product_id = ?", (product_id,))
        results = cur.fetchall()
        if not results:
            print("No History")
        else:
            for row in results:
                print(row)

def del_supplier(supplier_id):
    with sqlite3.connect("stocks.db") as connection:
        cur = connection.cursor()
        cur.execute("DELETE FROM Suppliers WHERE id = ?", (supplier_id,))
        connection.commit()
        print("Supplier deleted")

def main():
    init_db()
    while True:
        print("\n=== Stock management system")
        print("1. Add Product")
        print("2. Add Supplier")
        print("3. Add Stock")
        print("4. Remove Stocks")
        print("5. List products")
        print("6. View Product Hsitory")
        print("7. Update Price")
        print("8. Delete Supplier")
        print("9. Exit")

        try:
            choice = int(input("\n Enter your choice:"))

            if choice == 1:
                name = input("Enter a name")
                price = float(input("Enter a price"))
                create_product(name, price)

            elif choice == 2:
                name = input("Enter a name")
                contact = int(input("Enter a contact"))
                add_supplier(name, contact)

            elif choice == 3:
                product_id = int(input("What's the product id"))
                supplier_id = int(input("Enter supplier id"))
                quantity = int(input("Enter quantity"))
                add_stock(product_id, supplier_id, quantity)

            elif choice == 4:
                product_id = int(input("Enter product id"))
                quantity = int(input("Enter qauntity"))
                remove_stock(product_id, quantity)
            
            elif choice == 5:
                list_products()
            
            elif choice == 6:
                product_id = int(input("Enter product id"))
                view_products_history(product_id)

            elif choice == 7:
                product_id = int(input("Enter a product id"))
                new_price = float(input("Enter a new price"))
                update_product_price(product_id, new_price)

            elif choice == 8:
                supplier_id = int(input("Enter supplier's infromation id"))
                del_supplier(supplier_id)

            elif choice == 9:
                print("Thank you, goodbye")
                break 
            else:
                print("Invalid choice! Please try again.")
        
        except ValueError:
            print("Error: Please enter a valid number!")
        except Exception as e:
            print(f"Error: {e}")

          
            


if __name__ == "__main__":
    main()
   