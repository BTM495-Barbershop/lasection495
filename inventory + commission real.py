import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


class Inventory:
    def __init__(self):
        self.connection = sqlite3.connect(r"\\Mac\Home\Documents\inventory 6.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                Inventory_ID TEXT PRIMARY KEY,
                Location_ID TEXT,
                Item_Name TEXT NOT NULL,
                Item_Count INTEGER
            )
        ''')
        self.connection.commit()

    def update_item_count(self, inventory_id, new_count, location_id):
        self.cursor.execute('''
            SELECT * FROM inventory WHERE Inventory_ID = ? AND Location_ID = ?
        ''', (inventory_id, location_id))
        item = self.cursor.fetchone()
        if item:
            self.cursor.execute('''
                UPDATE inventory
                SET Item_Count = ?
                WHERE Inventory_ID = ? AND Location_ID = ?
            ''', (new_count, inventory_id, location_id))
            self.connection.commit()
            return f"Item with ID '{inventory_id}' count updated to {new_count}."
        else:
            return f"Error: Item with ID '{inventory_id}' not found in location '{location_id}'."

    def list_items_by_location(self, location_id):
        self.cursor.execute('''
            SELECT Inventory_ID, Item_Name, Item_Count
            FROM inventory
            WHERE Location_ID = ?
        ''', (location_id,))
        items = self.cursor.fetchall()
        if items:
            return "\n".join(
                f"{item[0]} - {item[1]}: {item[2]} units ({self.check_stock_status(item[2])})"
                for item in items
            )
        else:
            return f"No items found in Location {location_id}."

    @staticmethod
    def check_stock_status(count):
        if count < 25:
            return "Low Stock"
        elif 25 <= count < 50:
            return "Medium Stock"
        else:
            return "High Stock"

    def __del__(self):
        self.connection.close()


class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("400x300")
        self.root.configure(bg="black")

        self.inventory = Inventory()
        self.locations = ["CDN", "OM", "DT"]

        ttk.Label(root, text="Select Location:", foreground="white", background="black").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.location_var = tk.StringVar(value=self.locations[0])
        self.location_menu = ttk.Combobox(root, textvariable=self.location_var, values=self.locations, state="readonly")
        self.location_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(root, text="Inventory ID:", foreground="white", background="black").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.inventory_id_entry = ttk.Entry(root)
        self.inventory_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(root, text="New Item Count:", foreground="white", background="black").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.item_count_entry = ttk.Entry(root)
        self.item_count_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        ttk.Button(root, text="Update Item Count", command=self.update_item_count).grid(row=3, column=0, padx=10, pady=10)
        ttk.Button(root, text="List Items", command=self.list_items).grid(row=3, column=1, padx=10, pady=10)
        ttk.Button(root, text="Back", command=self.go_back).grid(row=4, column=0, columnspan=2, pady=10)

    def update_item_count(self):
        inventory_id = self.inventory_id_entry.get()
        try:
            new_count = int(self.item_count_entry.get())
        except ValueError:
            messagebox.showerror("Error", "New Count must be a number.")
            return
        location_id = self.location_var.get()

        result = self.inventory.update_item_count(inventory_id, new_count, location_id)
        messagebox.showinfo("Update Item Count", result)

    def list_items(self):
        location_id = self.location_var.get()
        items = self.inventory.list_items_by_location(location_id)
        messagebox.showinfo(f"Items in {location_id}", items)

    def go_back(self):
        self.root.destroy()
        main_menu()


class CommissionManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Commission Management")
        self.root.geometry("400x500")
        self.root.configure(bg="black")

        self.connection = sqlite3.connect(r"\\Mac\Home\Downloads\EmployeeDatabase.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS salary (
                User_ID TEXT PRIMARY KEY,
                Commission_Rate REAL,
                Hours_Worked REAL,
                Tip_Value REAL,
                Total_Sales REAL,
                Salary REAL
            )
        ''')
        self.connection.commit()

        tk.Label(self.root, text="User ID:", bg="black", fg="white").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.user_id_entry = tk.Entry(self.root)
        self.user_id_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Total Sales:", bg="black", fg="white").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.total_sales_entry = tk.Entry(self.root)
        self.total_sales_entry.grid(row=1, column=1, padx=10, pady=10)

        calculate_button = tk.Button(self.root, text="Calculate Salary", command=self.calculate_salary, bg="blue", fg="white")
        calculate_button.grid(row=2, column=0, columnspan=2, pady=20)

        self.result_label = tk.Label(self.root, text="", bg="black", fg="white")
        self.result_label.grid(row=3, column=0, columnspan=2, pady=10)

    def calculate_salary(self):
        try:
            user_id = self.user_id_entry.get()
            total_sales = float(self.total_sales_entry.get())

            self.cursor.execute('''
                SELECT Commission_Rate, Hours_Worked, Tip_Value
                FROM salary
                WHERE User_ID = ?
            ''', (user_id,))
            record = self.cursor.fetchone()

            if record:
                commission_rate, hours_worked, tip_value = record
            else:
                messagebox.showerror("Error", f"No record found for User ID '{user_id}'.")
                return

            salary = (total_sales * commission_rate) + tip_value + (hours_worked * 10)

            self.cursor.execute('''
                UPDATE salary
                SET Total_Sales = ?, Salary = ?
                WHERE User_ID = ?
            ''', (total_sales, salary, user_id))
            self.connection.commit()

            self.result_label.config(text=f"User {user_id}'s total salary is: ${salary:.2f}")
            messagebox.showinfo("Salary Saved", f"Salary for User {user_id} has been updated in the database.")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid numeric value for Total Sales.")

    def __del__(self):
        self.connection.close()


class MainMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Menu")
        self.root.geometry("300x250")
        self.root.configure(bg="black")

        ttk.Button(root, text="Inventory", command=self.open_inventory).grid(row=0, column=0, padx=20, pady=20)
        ttk.Button(root, text="Commission Management", command=self.open_commission_management).grid(row=0, column=1, padx=20, pady=20)
        ttk.Button(root, text="Logout", command=self.logout).grid(row=1, column=0, columnspan=2, pady=10)

    def open_inventory(self):
        self.root.destroy()
        inventory_root = tk.Tk()
        app = InventoryApp(inventory_root)
        inventory_root.mainloop()

    def open_commission_management(self):
        self.root.destroy()
        commission_root = tk.Tk()
        app = CommissionManagementApp(commission_root)
        commission_root.mainloop()

    def logout(self):
        self.root.destroy()
        login_screen()


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("300x150")
        self.root.configure(bg="black")

        ttk.Label(root, text="Username:", foreground="white", background="black").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.username_entry = ttk.Entry(root)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(root, text="Password:", foreground="white", background="black").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.password_entry = ttk.Entry(root, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ttk.Button(root, text="Login", command=self.check_login).grid(row=2, column=0, columnspan=2, pady=10)

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "Gonz123@gmail.com" and password == "Lasection1234":
            self.root.destroy()
            main_menu()
        else:
            messagebox.showerror("Error", "Invalid username or password")


def main_menu():
    root = tk.Tk()
    app = MainMenuApp(root)
    root.mainloop()


def login_screen():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()


# Start with the login screen
login_screen()