import tkinter as tk
from tkinter import ttk, messagebox
import random

class BarbershopLoyaltyProgram:
    def __init__(self, root):
        self.root = root
        self.root.title("Barbershop Loyalty Program")
        
        # Program Details
        self.programName = "LaSectionPoints"
        self.pointsPerService = {"Haircut": 10, "Haircut & Beards": 20, "Braids": 30}
        self.customers = {}
        self.totalPoints = 0

        # UI Setup
        self.create_ui()

    def create_ui(self):
        # Title
        title_label = tk.Label(self.root, text="Barbershop Loyalty Program", font=("Arial", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Program Name
        program_label = tk.Label(self.root, text=f"Program: {self.programName}", font=("Arial", 12))
        program_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Customer Name
        name_label = tk.Label(self.root, text="Customer Name:", font=("Arial", 12))
        name_label.grid(row=2, column=0, sticky=tk.W, padx=10)
        self.name_entry = tk.Entry(self.root, font=("Arial", 12))
        self.name_entry.grid(row=2, column=1, padx=10, pady=5)

        # Service Selection
        service_label = tk.Label(self.root, text="Choose Service:", font=("Arial", 12))
        service_label.grid(row=3, column=0, sticky=tk.W, padx=10)
        self.service_combo = ttk.Combobox(self.root, font=("Arial", 12))
        self.service_combo["values"] = list(self.pointsPerService.keys())
        self.service_combo.grid(row=3, column=1, padx=10, pady=5)

        # Add Points Button
        add_points_button = tk.Button(self.root, text="Add Points", font=("Arial", 12), command=self.add_points)
        add_points_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Total Points
        self.points_label = tk.Label(self.root, text=f"Total Points: {self.totalPoints}", font=("Arial", 12))
        self.points_label.grid(row=5, column=0, columnspan=2, pady=10)

        # Customer List Button
        customer_list_button = tk.Button(self.root, text="View Customers", font=("Arial", 12), command=self.display_customers)
        customer_list_button.grid(row=6, column=0, columnspan=2, pady=5)

    def generate_account_id(self, customer_name):
        # Generate an account ID using the initials and a random 4-digit number
        name_parts = customer_name.split()
        if len(name_parts) < 2:
            messagebox.showerror("Error", "Please enter both first and last name.")
            return None
        initials = name_parts[0][0].upper() + name_parts[1][0].upper()
        unique_id = random.randint(1000, 9999)
        return f"{initials}{unique_id}"

    def add_points(self):
        customer_name = self.name_entry.get().strip()
        service = self.service_combo.get()

        if not customer_name:
            messagebox.showerror("Error", "Please enter the customer's name.")
            return
        if service not in self.pointsPerService:
            messagebox.showerror("Error", "Please select a valid service.")
            return

        # Generate or find account ID
        account_id = self.generate_account_id(customer_name)
        if not account_id:
            return
        if account_id not in self.customers:
            self.customers[account_id] = {"name": customer_name, "points": 0}
        
        # Add points for the service
        points = self.pointsPerService[service]
        self.customers[account_id]["points"] += points
        self.totalPoints += points

        # Update total points label
        self.points_label.config(text=f"Total Points: {self.totalPoints}")
        messagebox.showinfo("Success", f"{points} points added for {service}.\nAccount ID: {account_id}")

    def display_customers(self):
        customer_list = "\n".join(
            [f"ID: {acc_id} | Name: {data['name']} | Points: {data['points']}" for acc_id, data in self.customers.items()]
        )
        if not customer_list:
            customer_list = "No customers added yet."
        messagebox.showinfo("Customer List", customer_list)

if __name__ == "__main__":
    root = tk.Tk()
    app = BarbershopLoyaltyProgram(root)
    root.mainloop()