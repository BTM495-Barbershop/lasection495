import tkinter as tk
from tkinter import messagebox
import random
import sqlite3
import os
from twilio.rest import Client
from pathlib import Path

# Load environment variables (or set them manually if not using .env)
TWILIO_ACCOUNT_SID = "AC725e0bcde0f7228431f83b35d0d37860"
TWILIO_AUTH_TOKEN = "6fbfb076255ec939565d885545d83dc8"
TWILIO_PHONE_NUMBER = "+14389017118"

# Path to your SQLite database file
db_path = Path("/Users/jayedahmed/Desktop/RegisteredUser.db")


# Function to initialize the database with the RegisteredUser table
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS RegisteredUser (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing unique ID
        firstName TEXT NOT NULL,
        lastName TEXT NOT NULL,
        phoneNumber TEXT UNIQUE NOT NULL,          -- Enforces unique phone numbers
        email TEXT UNIQUE NOT NULL,                -- Enforces unique email addresses
        userType TEXT CHECK(userType IN ('employee', 'customer')) NOT NULL  -- Restricts to 'employee' or 'customer'
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()
    conn.close()


# Initialize the database and create the table if it doesn't exist
init_db()


class RegistrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Registration Form - LaSection")

        # Variables
        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.user_type_var = tk.StringVar()
        self.verification_code = None

        # UI Setup
        self.fillupform()

    # Method to fill up the form
    def fillupform(self):
        tk.Label(self.root, text="First Name").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.first_name_var).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Last Name").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.last_name_var).grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Email").grid(row=2, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.email_var).grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Phone Number").grid(row=3, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.phone_var).grid(row=3, column=1, padx=10, pady=10)

        tk.Label(self.root, text="User Type (employee/customer)").grid(row=4, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.user_type_var).grid(row=4, column=1, padx=10, pady=10)

        # Submit button
        tk.Button(self.root, text="Submit", command=self.submit_form).grid(row=5, column=1, pady=20)

    # Method to verify filled form for duplicates
    def verifyFilledForm(self, email, phone):
        if not phone.startswith("+1"):
            phone = "+1" + phone
            self.phone_var.set(phone)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM RegisteredUser WHERE email = ? OR phoneNumber = ?", (email, phone))
        result = cursor.fetchone()
        conn.close()

        if result:
            if result[3] == email:
                messagebox.showerror("Error", "This email is already registered. Please use a different email.")
            elif result[4] == phone:
                messagebox.showerror("Error", "This phone number is already registered. Please use a different number.")
            return False
        return True

    # Method to handle form submission and check for duplicates
    def submit_form(self):
        email = self.email_var.get()
        phone = self.phone_var.get()
        user_type = self.user_type_var.get().lower()

        if user_type not in ['employee', 'customer']:
            messagebox.showerror("Error", "User type must be 'employee' or 'customer'.")
            return

        # Ensure phone number starts with +1
        if not phone.startswith("+1"):
            phone = "+1" + phone
            self.phone_var.set(phone)  # Update the phone variable with +1 prefix

        if self.verifyFilledForm(email, phone):
            self.sendVerificationCode(phone)

    # Method to send verification code using Twilio
    def sendVerificationCode(self, phone):
        # Generate a random 6-digit code
        self.verification_code = str(random.randint(100000, 999999))

        # Send the code via Twilio SMS
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"Your verification code for LaSection is: {self.verification_code}",
                from_=TWILIO_PHONE_NUMBER,
                to=phone
            )
            self.submitVerificationCode()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send verification code: {e}")

    # Method to open verification code entry window
    def submitVerificationCode(self):
        verify_window = tk.Toplevel(self.root)
        verify_window.title("Verification Code")

        tk.Label(verify_window, text="Enter the verification code sent to your phone:").pack(pady=10)
        self.code_entry = tk.Entry(verify_window)
        self.code_entry.pack(pady=5)

        tk.Button(verify_window, text="Verify", command=lambda: self.checkVerificationCode(verify_window)).pack(pady=10)

    # Method to check the entered verification code
    def checkVerificationCode(self, window):
        entered_code = self.code_entry.get()

        if entered_code == self.verification_code:
            window.destroy()  # Close verification window
            self.complete_registration()
        else:
            messagebox.showerror("Error", "Incorrect verification code. Please try again.")

    # Final method to complete registration and save to database
    def complete_registration(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO RegisteredUser (firstName, lastName, phoneNumber, email, userType) VALUES (?, ?, ?, ?, ?)",
            (self.first_name_var.get(), self.last_name_var.get(), self.phone_var.get(), self.email_var.get(),
             self.user_type_var.get().lower()))
        conn.commit()
        conn.close()

        messagebox.showinfo("Registration Successful",
                            f"Registration successful! Welcome to LaSection, {self.first_name_var.get()}.")


# Run the application
root = tk.Tk()
app = RegistrationApp(root)
root.mainloop()
