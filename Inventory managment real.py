import sqlite3
import tkinter as tk
from tkinter import messagebox

class InventoryItem:
    def __init__(self, inventory_id, item_name, item_count, location_id):
        self.inventory_id = inventory_id
        self.item_name = item_name
        self.item_count = item_count
        self.location_id = location_id

    def __repr__(self):
        return f"{self.inventory_id} - {self.item_name}: {self.item_count} units (Location: {self.location_id})"


class Inventory:
    def __init__(self):
        # Connect to the database
        self.connection = sqlite3.connect(r"\\Mac\Home\Documents\inventory 6.db")
        self.cursor = self.connection.cursor()

        # Drop the existing inventory table (if any) and create a new one
        self.cursor.execute('DROP TABLE IF EXISTS inventory')
        self.cursor.execute('''
            CREATE TABLE inventory (
                Inventory_ID TEXT PRIMARY KEY,
                Location_ID TEXT,
                Item_Name TEXT NOT NULL,
                Item_Count INTEGER
            )
        ''')
        self.connection.commit()

        # Pre-populate the inventory with initial items
        self.initialize_inventory()

    def initialize_inventory(self):
        items = [
            ("001-OM", "Alcohol", 20, "Old Montreal"),
            ("002-OM", "Tissue", 30, "Old Montreal"),
            ("003-OM", "Blades", 50, "Old Montreal"),
            ("004-OM", "Gel", 60, "Old Montreal"),
            ("001-DT", "Alcohol", 20, "Downtown"),
            ("002-DT", "Tissue", 30, "Downtown"),
            ("003-DT", "Blades", 50, "Downtown"),
            ("004-DT", "Gel", 60, "Downtown"),
            ("001-CDN", "Alcohol", 20, "Côte-des-Neiges"),
            ("002-CDN", "Tissue", 30, "Côte-des-Neiges"),
            ("003-CDN", "Blades", 50, "Côte-des-Neiges"),
            ("004-CDN", "Gel", 60, "Côte-des-Neiges")
        ]
        
        # Insert items into the table
        for inventory_id, item_name, item_count, location_id in items:
            self.cursor.execute('''
                INSERT OR IGNORE INTO inventory (Inventory_ID, Location_ID, Item_Name, Item_Count)
                VALUES (?, ?, ?, ?)
            ''', (inventory_id, location_id, item_name, item_count))
        
        self.connection.commit()

    def add_item(self, inventory_id, item_name, item_count, location_id):
        self.cursor.execute('''
            INSERT INTO inventory (Inventory_ID, Location_ID, Item_Name, Item_Count)
            VALUES (?, ?, ?, ?)
        ''', (inventory_id, location_id, item_name, item_count))
        self.connection.commit()
        return f"Item '{item_name}' added to inventory. " + self.check_stock_status(item_count)

    def update_item_count(self, inventory_id, new_count, location_id):
        self.cursor.execute('''
            UPDATE inventory
            SET Item_Count = ?
            WHERE Inventory_ID = ? AND Location_ID = ?
        ''', (new_count, inventory_id, location_id))
        self.connection.commit()
        return f"Item with ID '{inventory_id}' count updated to {new_count}. " + self.check_stock_status(new_count)

    def list_items_by_location(self, location_id):
        self.cursor.execute('''
            SELECT Inventory_ID, Item_Name, Item_Count
            FROM inventory
            WHERE Location_ID = ?
        ''', (location_id,))
        items = self.cursor.fetchall()

        if items:
            return "\n".join(
                f"{item[0]} - {item[1]}: {item[2]} units - {self.check_stock_status(item[2])}"
                for item in items
            )
        else:
            return f"No items found in Location {location_id}."

    def check_stock_status(self, count):
        if count < 25:
            return "low stock"
        elif 25 <= count <= 50:
            return "medium stock"
        else:
            return "high stock"

    def __del__(self):
        self.connection.close()


class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")

        self.inventory = Inventory()
        self.locations = ["Côte-des-Neiges", "Old Montreal", "Downtown"]

        # Location selection
        tk.Label(root, text="Select Location:").grid(row=0, column=0, padx=10, pady=10)
        self.location_var = tk.StringVar(value=self.locations[0])
        self.location_menu = tk.OptionMenu(root, self.location_var, *self.locations)
        self.location_menu.grid(row=0, column=1)

        # Inventory ID input
        tk.Label(root, text="Inventory ID:").grid(row=1, column=0, padx=10, pady=5)
        self.inventory_id_entry = tk.Entry(root)
        self.inventory_id_entry.grid(row=1, column=1)

        # Item Count input
        tk.Label(root, text="New Item Count:").grid(row=2, column=0, padx=10, pady=5)
        self.item_count_entry = tk.Entry(root)
        self.item_count_entry.grid(row=2, column=1)

        # Buttons
        tk.Button(root, text="Update Item Count", command=self.update_item_count).grid(row=3, column=0, padx=10, pady=10)
        tk.Button(root, text="List Items", command=self.list_items).grid(row=3, column=1, padx=10, pady=10)

    def update_item_count(self):
        location_id = self.location_var.get()
        inventory_id = self.inventory_id_entry.get()
        try:
            new_count = int(self.item_count_entry.get())
        except ValueError:
            messagebox.showerror("Error", "New Count must be a number.")
            return

        result = self.inventory.update_item_count(inventory_id, new_count, location_id)
        messagebox.showinfo("Update Item Count", result)

    def list_items(self):
        location_id = self.location_var.get()
        items = self.inventory.list_items_by_location(location_id)
        messagebox.showinfo(f"Items in {location_id}", items)


# Main application
root = tk.Tk()
app = InventoryApp(root)
root.mainloop()