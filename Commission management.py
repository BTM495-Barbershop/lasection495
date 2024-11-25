import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import messagebox

# Path
DB_PATH = "C:/Users/jonat/Downloads/EmployeeDatabase.db"

def load_data(userID):
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)

    # Ensure userID is formatted correctly 
    try:
        userID = int(userID)
    except ValueError:
        raise ValueError("User ID must be a valid integer.")

    # Query the database 
    query = "SELECT * FROM Employees WHERE userID = ?"
    barber_data = pd.read_sql_query(query, conn, params=(userID,))

    # Close 
    conn.close()
    return barber_data

def calculate_salary():
    userID = user_id_entry.get()
    try:
        # Load data for the given userID 
        barber_data = load_data(userID)
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

    if barber_data.empty:
        messagebox.showwarning("Not Found", "User ID not found.")
        return

    try:
        # Extract values for the barber
        commission_rate = barber_data['commissionRate'].values[0]
        hours_worked = barber_data['hoursWorked'].values[0]
        tip_value = barber_data['tipValue'].values[0]

        # Get sales value 
        sales_value = float(sales_entry.get())

        # Calculate total salary
        salary = (sales_value * commission_rate) + tip_value + (hours_worked * 10)

        # Display the result
        result_label.config(text=f"Total Salary: ${salary:.2f}", fg="green")
    except ValueError:
        messagebox.showerror("Error", "Invalid sales input. Please enter a number.")

# Create the main window
root = tk.Tk()
root.title("Barber Salary Calculator")

# User ID Label and Entry
tk.Label(root, text="Enter User ID:").grid(row=0, column=0, padx=10, pady=10)
user_id_entry = tk.Entry(root)
user_id_entry.grid(row=0, column=1, padx=10, pady=10)

# Sales Label and Entry
tk.Label(root, text="Enter Total Sales:").grid(row=1, column=0, padx=10, pady=10)
sales_entry = tk.Entry(root)
sales_entry.grid(row=1, column=1, padx=10, pady=10)

# Calculate Button
calculate_button = tk.Button(root, text="Calculate Salary", command=calculate_salary)
calculate_button.grid(row=2, column=0, columnspan=2, pady=20)

# Result Label
result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.grid(row=3, column=0, columnspan=2, pady=10)

# Run the application
root.mainloop()


