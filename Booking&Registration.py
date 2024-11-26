import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from pathlib import Path
import random
from twilio.rest import Client
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

ctk.set_appearance_mode("Dark")  # Set dark mode
ctk.set_default_color_theme("green")
# Path to the SQLite database
db_path = Path("/Users/jayedahmed/Desktop/RegisteredUser.db")

# Twilio API credentials
TWILIO_ACCOUNT_SID = "AC725e0bcde0f7228431f83b35d0d37860"
TWILIO_AUTH_TOKEN = "0a815b4fc975b6b916fbf15afe497e9e"
TWILIO_PHONE_NUMBER = "+14389017118"

# Global variable to track login status and user info
user_logged_in = False
current_user_email = None  # Tracks the currently logged-in user's email


# Function to verify login credentials
def verify_login(email, password):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query to verify user
        query = "SELECT * FROM RegisteredUser WHERE email = ? AND password = ?"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            return True
        else:
            return False
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))
        return False


# Class for registration functionality
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
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        self.verification_code = None

        # UI Setup
        self.fillupform()

    def fillupform(self):
        ctk.CTkLabel(self.root, text="First Name").grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkEntry(self.root, textvariable=self.first_name_var).grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.root, text="Last Name").grid(row=1, column=0, padx=10, pady=10)
        ctk.CTkEntry(self.root, textvariable=self.last_name_var).grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.root, text="Email").grid(row=2, column=0, padx=10, pady=10)
        ctk.CTkEntry(self.root, textvariable=self.email_var).grid(row=2, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.root, text="Phone Number").grid(row=3, column=0, padx=10, pady=10)
        ctk.CTkEntry(self.root, textvariable=self.phone_var).grid(row=3, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.root, text="User Type (employee/customer)").grid(row=4, column=0, padx=10, pady=10)
        ctk.CTkEntry(self.root, textvariable=self.user_type_var).grid(row=4, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.root, text="Password").grid(row=5, column=0, padx=10, pady=10)
        ctk.CTkEntry(self.root, textvariable=self.password_var, show="*").grid(row=5, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.root, text="Confirm Password").grid(row=6, column=0, padx=10, pady=10)
        ctk.CTkEntry(self.root, textvariable=self.confirm_password_var, show="*").grid(row=6, column=1, padx=10, pady=10)

        ctk.CTkButton(self.root, text="Submit", command=self.submit_form, fg_color="#4CAF50", hover_color="#45A049").grid(row=7, column=1, pady=20)

    def verifyFilledForm(self, email, phone):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM RegisteredUser WHERE email = ? OR phoneNumber = ?", (email, phone))
        result = cursor.fetchone()
        conn.close()

        if result:
            if result[3] == email:
                messagebox.showerror("Error", "This email is already registered.")
            elif result[4] == phone:
                messagebox.showerror("Error", "This phone number is already registered.")
            return False
        return True

    def submit_form(self):
        email = self.email_var.get()
        phone = self.phone_var.get()
        user_type = self.user_type_var.get().lower()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()

        if user_type not in ["employee", "customer"]:
            messagebox.showerror("Error", "User type must be 'employee' or 'customer'.")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        if not phone.startswith("+1"):
            phone = "+1" + phone
            self.phone_var.set(phone)

        if self.verifyFilledForm(email, phone):
            self.sendVerificationCode(phone)

    def sendVerificationCode(self, phone):
        self.verification_code = str(random.randint(100000, 999999))
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

    def submitVerificationCode(self):
        verify_window = ctk.CTkToplevel(self.root)
        verify_window.title("Verification Code")

        ctk.CTkLabel(verify_window, text="Enter the verification code sent to your phone:").pack(pady=10)
        self.code_entry = ctk.CTkEntry(verify_window)
        self.code_entry.pack(pady=5)

        ctk.CTkButton(verify_window, text="Verify", command=lambda: self.checkVerificationCode(verify_window)).pack(pady=10)

    def checkVerificationCode(self, window):
        entered_code = self.code_entry.get()

        if entered_code == self.verification_code:
            window.destroy()
            self.complete_registration()
        else:
            messagebox.showerror("Error", "Incorrect verification code.")

    def complete_registration(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO RegisteredUser (firstName, lastName, phoneNumber, email, userType, password) VALUES (?, ?, ?, ?, ?, ?)",
            (self.first_name_var.get(), self.last_name_var.get(), self.phone_var.get(), self.email_var.get(),
             self.user_type_var.get().lower(), self.password_var.get()))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Registration successful!")

        self.root.destroy()


# Function to show the main menu
def show_main_menu():
    global user_logged_in, current_user_email

    menu_window = ctk.CTkToplevel(root)
    menu_window.title("Main Menu")
    menu_window.geometry("400x400")

    ctk.CTkLabel(menu_window, text="La Section Barbershop", font=("Helvetica", 16), text_color="yellow").pack(pady=10)

    def about_us():
        messagebox.showinfo(
            "About Us",
            "La Section Barbershop was started in Montreal, Côte-des-Neiges, "
            "with a vision to provide premium haircuts and a great community space."
        )

    def services():
        messagebox.showinfo(
            "Services",
            "Services Offered:\n\n"
            "- Haircut: $40\n"
            "- Haircut & Beard: $50\n"
            "- Braids: $70\n"
            "\n"
            "We believe in customer loyalty. Therefore by creating an account,\n"
            "you will be able to accumulate loyalty points from each completed appointment.\n\n"
            "Points can be redeemed to purchase La Section grooming product or pay for you haircut!"
        )

    def start_booking():
        if not user_logged_in:
            messagebox.showinfo("Login Required", "Please log in to book an appointment.")
            login_action()  # Redirect to login if not logged in
            return

        # Open a new window for the booking interface
        booking_window = ctk.CTkToplevel(root)
        BarberShopBooking(booking_window)

    class BarberShopBooking:
        def __init__(self, root):
            self.root = root
            self.root.title("Barber Shop Booking System")
            self.root.geometry("700x1000")

            # Initialize booking information
            self.location = tk.StringVar()
            self.barber = tk.StringVar()
            self.service_type = tk.StringVar()
            self.time_slot = tk.StringVar()
            self.client_name = tk.StringVar()
            self.email = tk.StringVar()
            self.phone_number = tk.StringVar()
            self.payment_method = tk.StringVar()

            # Path to the barbershop booking database
            self.booking_db_path = "/Users/jayedahmed/Downloads/lasection495-main 4/barbershop.db"

            # Build interface
            self.build_interface()

        def build_interface(self):

            ctk.CTkLabel(self.root, text="Select Location").pack(pady=5)

            # Button for Cote-Des-Neiges
            ctk.CTkButton(self.root, text="Cote-Des-Neiges",
                          command=lambda: self.set_location("Cote-Des-Neiges")).pack(pady=5)

            # Button for Old Montreal
            ctk.CTkButton(self.root, text="Old Montreal",
                          command=lambda: self.set_location("Old Montreal")).pack(pady=5)

            # Button for Downtown
            ctk.CTkButton(self.root, text="Downtown",
                          command=lambda: self.set_location("Downtown")).pack(pady=5)

            ctk.CTkLabel(self.root, text="Select Barber").pack(pady=5)

            # Button for Gonz
            ctk.CTkButton(self.root, text="Gonz", command=lambda: self.set_barber("Gonz")).pack(pady=5)

            # Button for Mahir
            ctk.CTkButton(self.root, text="Mahir", command=lambda: self.set_barber("Mahir")).pack(pady=5)

            # Button for Roland
            ctk.CTkButton(self.root, text="Roland", command=lambda: self.set_barber("Roland")).pack(pady=5)

            ctk.CTkLabel(self.root, text="Select Service Type").pack(pady=5)

            # Service Type Buttons
            ctk.CTkButton(self.root, text="Haircut $40 (10pts)", command=lambda: self.set_service_type("Haircut")).pack(
                pady=5)
            ctk.CTkButton(self.root, text="Haircut & Beard $50 (20pts)",
                          command=lambda: self.set_service_type("Haircut & Beard")).pack(pady=5)
            ctk.CTkButton(self.root, text="Braids $70 (30pts)", command=lambda: self.set_service_type("Braids")).pack(
                pady=5)

            # Time Slot Selection
            ctk.CTkLabel(self.root, text="Select Time Slot").pack(pady=5)
            ctk.CTkButton(self.root, text="Choose Day and Time Slot", command=self.show_time_slot_page).pack(pady=5)

            #Client Name
            ctk.CTkLabel(self.root, text="Enter Client's Name").pack(pady=5)
            ctk.CTkEntry(self.root, textvariable=self.client_name).pack(pady=5)

            # Email Entry
            ctk.CTkLabel(self.root, text="Enter Email").pack(pady=5)
            ctk.CTkEntry(self.root, textvariable=self.email).pack(pady=5)

            # Phone Number Entry
            ctk.CTkLabel(self.root, text="Enter Phone Number").pack(pady=5)
            ctk.CTkEntry(self.root, textvariable=self.phone_number).pack(pady=5)

            # Payment Method
            ctk.CTkLabel(self.root, text="Select Payment Method").pack(pady=5)
            ctk.CTkButton(self.root, text="Pay in Person", command=lambda: self.set_payment_method("In Person")).pack(
                pady=5)
            ctk.CTkButton(self.root, text="Pay with Card/Points", command=self.online_payment_page).pack(pady=5)

            # Book Appointment Button
            ctk.CTkButton(self.root, text="Book Appointment", command=self.book_appointment).pack(pady=20)

        def set_location(self, location):
            self.location.set(location)

        def set_barber(self, barber):
            self.barber.set(barber)

        def set_service_type(self, service_type):
            self.service_type.set(service_type)

        def set_time_slot(self, time_slot):
            self.time_slot.set(time_slot)

        def set_payment_method(self, payment_method):
            self.payment_method.set(payment_method)

        def online_payment_page(self):
            payment_window = tk.Toplevel(self.root)
            payment_window.title("Online Payment")
            self.set_payment_method("Card or Points")

            tk.Label(payment_window, text="Card Number").pack()
            card_number = tk.Entry(payment_window)
            card_number.pack()

            tk.Label(payment_window, text="Expiry Date (MM/YY)").pack()
            expiry_date = tk.Entry(payment_window)
            expiry_date.pack()

            tk.Label(payment_window, text="CRC Code").pack()
            crc_code = tk.Entry(payment_window)
            crc_code.pack()

            tk.Label(payment_window, text="Full Name").pack()
            full_name = tk.Entry(payment_window)
            full_name.pack()

            tk.Button(payment_window, text="Confirm Payment", command=payment_window.destroy,
                      activebackground="yellow").pack()

        def show_time_slot_page(self):
            if not self.barber.get():
                messagebox.showerror("Error", "Please select a barber first.")
                return

            time_slot_window = ctk.CTkToplevel(self.root)
            time_slot_window.title(f"Available Slots for {self.barber.get()}")
            time_slot_window.geometry("900x500")

            ctk.CTkLabel(time_slot_window, text=f"Available Time Slots for {self.barber.get()}",
                         font=("Arial", 14)).pack(pady=10)

            try:
                # Connect to the Availability database
                conn = sqlite3.connect("/Users/jayedahmed/Desktop/Availability.db")
                cursor = conn.cursor()

                # Fetch available slots for the selected barber
                cursor.execute("""
                    SELECT day, timeSlot 
                    FROM availability 
                    WHERE status = 'Available' AND Barber = ?
                    ORDER BY day, timeSlot
                """, (self.barber.get(),))
                available_slots = cursor.fetchall()
                conn.close()

                if not available_slots:
                    ctk.CTkLabel(time_slot_window, text="No available time slots for the selected barber.",
                                 font=("Arial", 12)).pack()
                    return

                # Create a calendar view
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                hours = [f"{hour}:00" for hour in range(9, 18)]  # 9 AM to 5 PM
                slots_grid = {day: {hour: False for hour in hours} for day in days}

                # Mark available slots in the grid
                for day, time in available_slots:
                    if day in slots_grid and time in slots_grid[day]:
                        slots_grid[day][time] = True

                # Create a frame for the calendar
                calendar_frame = ctk.CTkFrame(time_slot_window)
                calendar_frame.pack(pady=10)

                # Header row (days)
                ctk.CTkLabel(calendar_frame, text="Time", width=12, anchor="center").grid(row=0, column=0)
                for col, day in enumerate(days, start=1):
                    ctk.CTkLabel(calendar_frame, text=day, width=12, anchor="center").grid(row=0, column=col)

                # Fill in the calendar
                for row, hour in enumerate(hours, start=1):
                    # Time column
                    ctk.CTkLabel(calendar_frame, text=hour, width=12, anchor="center").grid(row=row, column=0)

                    for col, day in enumerate(days, start=1):
                        if slots_grid[day][hour]:  # Available
                            ctk.CTkButton(
                                calendar_frame,
                                text="Available",
                                command=lambda d=day, t=hour: self.select_time_slot(d, t, time_slot_window)
                            ).grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                        else:  # Unavailable
                            ctk.CTkLabel(
                                calendar_frame,
                                text="Unavailable",
                                width=12,
                                anchor="center"
                            ).grid(row=row, column=col, padx=5, pady=5)

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error fetching available time slots: {e}")

        def select_time_slot(self, day, time, window):
            self.set_time_slot(f"{day} {time}")

            # Update the slot to "Unavailable" in the Availability DB
            try:
                conn = sqlite3.connect("/Users/jayedahmed/Desktop/Availability.db")
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE availability 
                    SET status = 'Unavailable' 
                    WHERE day = ? AND timeSlot = ? AND barber = ?
                """, (day, time, self.barber.get()))  # Filter by barber, day, and time slot
                conn.commit()
                conn.close()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error updating time slot: {e}")
                return

            window.destroy()

        def book_appointment(self):
            if not self.time_slot.get() or not self.client_name.get():
                messagebox.showerror("Error", "Please enter the client's name and select a time slot.")
                return

            try:
                # Connect to the barbershop database
                conn = sqlite3.connect("/Users/jayedahmed/Desktop/barbershop.db")
                cursor = conn.cursor()

                # Ensure the bookings table exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bookings (
                        BookingId INTEGER PRIMARY KEY AUTOINCREMENT,
                        location TEXT,
                        barber TEXT,
                        serviceType TEXT,
                        timeSlot INTEGER,
                        email TEXT,
                        phoneNumber INTEGER,
                        paymentMethod TEXT,
                        clientName TEXT,
                        LocationID NUMERIC,
                        UserID NUMERIC
                    )
                """)

                # Insert booking details into the table
                cursor.execute("""
                    INSERT INTO bookings (
                        location, barber, serviceType, timeSlot, email, phoneNumber, paymentMethod, clientName, LocationID, UserID
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.location.get(),  # Location
                    self.barber.get(),  # Barber
                    self.service_type.get(),  # Service Type
                    self.time_slot.get(),  # Time Slot
                    self.email.get(),  # Email
                    self.phone_number.get(),  # Phone Number
                    self.payment_method.get(),  # Payment Method
                    self.client_name.get(),  # Client Name
                    None,  # LocationID (Set to None or a default value)
                    None  # UserID (Set to None or a default value)
                ))
                conn.commit()
                conn.close()

                # Send confirmation email
                self.send_confirmation_email()

                # Show confirmation message
                messagebox.showinfo("Booking Confirmation", "Your appointment has been successfully booked!")

                self.root.destroy()

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to save booking: {e}")

        def send_confirmation_email(self):
            sender_email = "barbershoplasection@gmail.com"
            sender_password = "vknl bljy ujmo hhix"
            receiver_email = self.email.get()

            message = MIMEMultipart("alternative")
            message["Subject"] = "Appointment Confirmation"
            message["From"] = sender_email
            message["To"] = receiver_email

            text = f"""
            Hello {self.client_name.get()},
            Your booking is confirmed!
            Location: {self.location.get()}
            Barber: {self.barber.get()}
            Service: {self.service_type.get()}
            Time Slot: {self.time_slot.get()}
            """
            part = MIMEText(text, "plain")
            message.attach(part)

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, message.as_string())
            except smtplib.SMTPAuthenticationError:
                messagebox.showerror("Email Error",
                                     "Failed to send email: Incorrect username or password. Check your email settings.")

    def add_availability():
        global user_logged_in, current_user_email
        if not user_logged_in:
            messagebox.showinfo("Login Required", "Please log in to manage availability.")
            login_action()
            return

        # Check if the logged-in user is an employee
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT userType FROM RegisteredUser WHERE email = ?", (current_user_email,))
            user_type = cursor.fetchone()
            conn.close()

            if not user_type or user_type[0] != 'employee':
                messagebox.showerror("Access Denied", "Only employees can manage availability.")
                return
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        # Open the availability window for employees
        open_availability_window()

    def open_availability_window():
        availability_window = tk.Toplevel(root)
        availability_window.title("Barber's Availability")
        availability_window.geometry("800x600")

        # Display employee email
        ctk.CTkLabel(availability_window, text=f"Employee: {current_user_email}", font=("Helvetica", 12)).pack(pady=10)

        # Days and hours
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        hours = [f"{hour}:00" for hour in range(9, 18)]  # 9 AM to 5 PM

        # Container for availability checkboxes
        selections = {}  # Dictionary to track selections

        # Create a grid of checkboxes
        ctk.CTkLabel(availability_window, text="Select Availability", font=("Helvetica", 12)).pack(pady=5)
        grid_frame = ctk.CTkFrame(availability_window)
        grid_frame.pack(pady=10, fill="both", expand=True)

        # Configure grid layout for centering
        for col in range(len(days) + 1):  # Configure all columns (time slots + days)
            grid_frame.grid_columnconfigure(col, weight=1)

        # Column headers (days)
        ctk.CTkLabel(grid_frame, text="Time Slot", anchor="center").grid(row=0, column=0, padx=10, pady=5)
        for col, day in enumerate(days, start=1):
            ctk.CTkLabel(grid_frame, text=day, anchor="center").grid(row=0, column=col, padx=10, pady=5)

        # Create the grid of checkboxes
        for row, hour in enumerate(hours, start=1):
            # Time slot label (leftmost column)
            ctk.CTkLabel(grid_frame, text=hour, anchor="center").grid(row=row, column=0, padx=10, pady=5)

            for col, day in enumerate(days, start=1):
                var = tk.BooleanVar()
                selections[(day, hour)] = var

                # Perfectly centered checkbox
                ctk.CTkSwitch(grid_frame, text="", variable=var).grid(row=row, column=col, sticky="ns", pady=5)

        # Submit button
        def submit_availability():
            to_insert = []

            # Determine the barber's name based on the email
            barber_name = None
            if current_user_email == "Mahir123@gmail.com":
                barber_name = "Mahir"
            elif current_user_email == "Roland123@gmail.com":
                barber_name = "Roland"
            elif current_user_email == "Gonz123@gmail.com":
                barber_name = "Gonz"

            if not barber_name:
                messagebox.showerror("Error", "Could not determine barber name based on email.")
                return

            # Prepare data for insertion
            for (day, time), var in selections.items():
                if var.get():  # If the checkbox is selected
                    to_insert.append((current_user_email, day, time, "Available", barber_name))

            if not to_insert:
                messagebox.showerror("No Selection", "Please select at least one time slot.")
                return

            # Save all selected availabilities to the database
            try:
                conn = sqlite3.connect("/Users/jayedahmed/Desktop/Availability.db")
                cursor = conn.cursor()

                # Create the table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS availability (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employeeEmail TEXT NOT NULL,
                        day TEXT NOT NULL,
                        timeSlot TEXT NOT NULL,
                        status TEXT NOT NULL,
                        Barber TEXT,
                        UNIQUE(employeeEmail, day, timeSlot)
                    )
                """)

                # Insert or update availability records
                cursor.executemany("""
                    INSERT OR REPLACE INTO availability (employeeEmail, day, timeSlot, status, Barber) 
                    VALUES (?, ?, ?, ?, ?)
                """, to_insert)

                conn.commit()
                conn.close()

                messagebox.showinfo("Success", f"{len(to_insert)} time slots added successfully!")
                availability_window.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error saving availability: {e}")

        # Add the Submit button
        ctk.CTkButton(availability_window, text="Submit", command=submit_availability).pack(pady=20)

    def view_loyalty_profile():
        global user_logged_in, current_user_email
        if not user_logged_in:
            messagebox.showinfo("Login Required", "Please log in to view your loyalty profile.")
            login_action()
            return

        try:
            # Connect to the RegisteredUser database
            conn = sqlite3.connect("/Users/jayedahmed/Desktop/RegisteredUser.db")
            cursor = conn.cursor()

            # Retrieve user's first name, last name, and loyalty points
            query = "SELECT firstName, lastName, loyaltyPoints FROM RegisteredUser WHERE email = ?"
            cursor.execute(query, (current_user_email,))
            user_data = cursor.fetchone()
            conn.close()

            if user_data:
                first_name, last_name, loyalty_points = user_data

                # Create a new window to display the loyalty profile
                loyalty_window = tk.Toplevel(root)
                loyalty_window.title("Loyalty Profile")
                loyalty_window.geometry("400x300")

                # Display user's name and loyalty points
                tk.Label(loyalty_window, text=f"{first_name} {last_name}", font=("Arial", 16)).pack(pady=10)
                tk.Label(loyalty_window, text=f"Loyalty Points: {loyalty_points}", font=("Arial", 12)).pack(pady=10)

                # Redeem points button
                def redeem_points():
                    # Create a new window for choosing redemption options
                    redemption_window = tk.Toplevel(loyalty_window)
                    redemption_window.title("Redeem Points Options")
                    redemption_window.geometry("400x200")

                    tk.Label(redemption_window, text="Choose how to redeem your points:", font=("Arial", 14)).pack(
                        pady=20)

                    # Option 1: Book Appointment
                    def redirect_to_booking():
                        redemption_window.destroy()  # Close this window
                        loyalty_window.destroy()  # Close the loyalty profile window
                        start_booking()  # Redirect to booking process

                    ctk.CTkButton(redemption_window, text="Book Appointment", command=redirect_to_booking).pack(pady=10)

                    # Option 2: Purchase Grooming Product
                    def show_coming_soon():
                        messagebox.showinfo("Coming Soon", "Website currently under development.")
                        redemption_window.destroy()  # Close this window

                    ctk.CTkButton(redemption_window, text="Purchase Grooming Product", command=show_coming_soon).pack(
                        pady=10)

                ctk.CTkButton(loyalty_window, text="Redeem Points", command=redeem_points, font=("Arial", 12)).pack(
                    pady=20)
            else:
                messagebox.showerror("Error", "User data not found.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    # Log Out button
    def log_out():
        global user_logged_in, current_user_email
        user_logged_in = False
        current_user_email = None
        messagebox.showinfo("Logged Out", "You have successfully logged out.")
        menu_window.destroy()

    # Buttons for the main menu
    ctk.CTkButton(menu_window, text="About Us", command=about_us, fg_color="#000000",  hover_color="#333333",  text_color="white").pack(pady=5)
    ctk.CTkButton(menu_window, text="Services", command=services, fg_color="#000000",  hover_color="#333333",  text_color="white").pack(pady=5)
    ctk.CTkButton(menu_window, text="Book Now", command=start_booking, fg_color="#000000",  hover_color="#333333",  text_color="white").pack(pady=5)
    ctk.CTkButton(menu_window, text="Add Availability", command=add_availability, fg_color="#000000",  hover_color="#333333",  text_color="white").pack(pady=5)
    ctk.CTkButton(menu_window, text="Loyalty Profile", command=view_loyalty_profile, fg_color="#000000",  hover_color="#333333",  text_color="white").pack(pady=10)

    # Show Log Out button if logged in
    if user_logged_in:
        ctk.CTkButton(menu_window, text="Log Out", command=log_out, fg_color="#FF0000",  hover_color="#CC0000").pack(pady=10)




# Login functionality
def login_action():
    login_window = ctk.CTkToplevel(root)
    login_window.title("Login")
    login_window.geometry("300x250")

    ctk.CTkLabel(login_window, text="Email").pack(pady=5)
    email_entry = ctk.CTkEntry(login_window)
    email_entry.pack(pady=5)

    ctk.CTkLabel(login_window, text="Password").pack(pady=5)
    password_entry = ctk.CTkEntry(login_window, show="*")
    password_entry.pack(pady=5)

    def attempt_login():
        global user_logged_in, current_user_email
        email = email_entry.get()
        password = password_entry.get()

        if verify_login(email, password):
            user_logged_in = True
            current_user_email = email
            messagebox.showinfo("Login Successful", "Welcome back!")
            login_window.destroy()
            show_main_menu()
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")

    ctk.CTkButton(login_window, text="Login", command=attempt_login, fg_color="#4CAF50", hover_color="#45A049").pack(pady=10)

    # Register button to open the registration window
    ctk.CTkButton(login_window, text="Register", command=lambda: RegistrationApp(tk.Toplevel(login_window)),fg_color="#000000",  hover_color="#333333",  text_color="white").pack(pady=5)


# Main application logic
root = ctk.CTk()
root.title("La Section Barbershop")
root.geometry("0x0")

# Open the main menu on application start
show_main_menu()

root.mainloop()
