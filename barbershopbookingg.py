import tkinter as tk
from tkinter import messagebox
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class BarberShopBooking:
    def __init__(self, root):
        self.root = root
        self.root.title("Barber Shop Booking System")
        self.root.geometry("600x700")
        
        # Initialize booking information
        self.location = tk.StringVar()
        self.barber_id = tk.IntVar()  # Updated to store barber's userId
        self.barber_name = tk.StringVar()  # Store barber's name
        self.service_type = tk.StringVar()
        self.time_slot = tk.StringVar()
        self.client_name = tk.StringVar()  # New client name variable
        self.email = tk.StringVar()
        self.phone_number = tk.StringVar()
        self.payment_method = tk.StringVar()
        
        # Database connection
        self.conn = sqlite3.connect('barbershop2.db')  # Updated database name
        self.cursor = self.conn.cursor()
        
        # Map barbers to userIds
        self.barber_mapping = {"Gonz": 5, "Roland": 6, "Mahir": 7}
        
        # Build interface
        self.build_interface()

    def build_interface(self):
        tk.Label(self.root, text="Enter Client Name").pack()
        tk.Entry(self.root, textvariable=self.client_name).pack()

        tk.Label(self.root, text="Select Location").pack()
        tk.Button(self.root, text="Cote-Des-Neiges", command=lambda: self.set_location("Cote-Des-Neiges"), activebackground="yellow").pack()
        tk.Button(self.root, text="Old Montreal", command=lambda: self.set_location("Old Montreal"), activebackground="yellow").pack()
        tk.Button(self.root, text="Downtown", command=lambda: self.set_location("Downtown"), activebackground="yellow").pack()

        tk.Label(self.root, text="Select Barber").pack()
        tk.Button(self.root, text="Gonz", command=lambda: self.set_barber("Gonz"), activebackground="yellow").pack()
        tk.Button(self.root, text="Mahir", command=lambda: self.set_barber("Mahir"), activebackground="yellow").pack()
        tk.Button(self.root, text="Roland", command=lambda: self.set_barber("Roland"), activebackground="yellow").pack()

        tk.Label(self.root, text="Select Service Type").pack()
        tk.Button(self.root, text="Haircut $40 (10pts)", command=lambda: self.set_service_type("Haircut"), activebackground="yellow").pack()
        tk.Button(self.root, text="Haircut & Beard $50 (20pts)", command=lambda: self.set_service_type("Haircut & Beard"), activebackground="yellow").pack()
        tk.Button(self.root, text="Braids $70 (30pts)", command=lambda: self.set_service_type("Braids"), activebackground="yellow").pack()

        tk.Label(self.root, text="Select Time Slot").pack()
        tk.Button(self.root, text="Choose Day and Time Slot", command=self.show_time_slot_page, activebackground="yellow").pack()

        tk.Label(self.root, text="Enter Email").pack()
        tk.Entry(self.root, textvariable=self.email).pack()
        
        tk.Label(self.root, text="Enter Phone Number").pack()
        tk.Entry(self.root, textvariable=self.phone_number).pack()

        tk.Label(self.root, text="Select Payment Method").pack()
        tk.Button(self.root, text="Pay in Person", command=lambda: self.set_payment_method("In Person"), activebackground="yellow").pack()
        tk.Button(self.root, text="Pay with Debit/Visa", command=self.online_payment_page, activebackground="yellow").pack()

        tk.Button(self.root, text="Book Appointment", command=self.book_appointment, activebackground="yellow").pack()

    def set_location(self, location):
        self.location.set(location)

    def set_barber(self, barber_name):
        # Set barber by userId and name based on the mapping
        self.barber_id.set(self.barber_mapping[barber_name])
        self.barber_name.set(barber_name)

    def set_service_type(self, service_type):
        self.service_type.set(service_type)

    def set_time_slot(self, time_slot):
        self.time_slot.set(time_slot)

    def set_payment_method(self, payment_method):
        self.payment_method.set(payment_method)

    def online_payment_page(self):
        payment_window = tk.Toplevel(self.root)
        payment_window.title("Online Payment")
        self.set_payment_method("Debit/Visa")
        
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
        
        tk.Button(payment_window, text="Confirm Payment", command=payment_window.destroy, activebackground="yellow").pack()

    def show_time_slot_page(self):
        """Show the time slot selection page with dynamic availability in a grid layout."""
        time_slot_window = tk.Toplevel(self.root)
        time_slot_window.title("Select Day and Time Slot")
        time_slot_window.geometry("700x500")  # Adjust the window size if needed
        
        # Predefined days and hours for time slots
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        hours = [f"{hour}:00" for hour in range(9, 17)]

        # Title for time slot window
        tk.Label(time_slot_window, text="Available Time Slots", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=len(hours) + 1, pady=10)

        # Create time slots for each day in a grid layout
        for row, day in enumerate(days, start=1):
            # Day Label
            tk.Label(time_slot_window, text=day, font=("Arial", 12)).grid(row=row, column=0, padx=10, pady=5, sticky="w")

            # Time slots for the day
            for col, hour in enumerate(hours, start=1):
                combined_slot = f"{day} {hour}"
                query = """
                SELECT timeSlot FROM bookings WHERE userId = ? AND location = ? AND timeSlot = ?
                """
                is_booked = self.cursor.execute(query, (self.barber_id.get(), self.location.get(), combined_slot)).fetchone()

                state = tk.DISABLED if is_booked else tk.NORMAL
                button_text = f"{hour}"

                tk.Button(
                    time_slot_window,
                    text=button_text,
                    state=state,
                    width=8,
                    command=lambda s=combined_slot: self.select_time_slot(s, time_slot_window),
                    activebackground="yellow"
                ).grid(row=row, column=col, padx=5, pady=5)

    def select_time_slot(self, slot, window):
        self.set_time_slot(slot)
        window.destroy()

    def book_appointment(self):
        if not self.time_slot.get() or not self.client_name.get():
            messagebox.showerror("Error", "Please enter client name and select a time slot.")
            return

        query = """
        SELECT * FROM bookings WHERE userId = ? AND location = ? AND timeSlot = ?
        """
        existing_booking = self.cursor.execute(query, (self.barber_id.get(), self.location.get(), self.time_slot.get())).fetchone()

        if existing_booking:
            messagebox.showerror("Unavailable", "This time slot is already booked. Please choose another slot.")
        else:
            try:
                self.cursor.execute("""
                INSERT INTO bookings (location, userId, barber, serviceType, timeSlot, clientName, email, phoneNumber, paymentMethod) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, 
                (self.location.get(), self.barber_id.get(), self.barber_name.get(), self.service_type.get(), self.time_slot.get(),
                 self.client_name.get(), self.email.get(), self.phone_number.get(), self.payment_method.get()))
                self.conn.commit()
                self.send_confirmation_email()
                messagebox.showinfo("Booking Confirmation", "Your appointment has been successfully booked!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to book appointment: {e}")

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
        Barber: {self.barber_name.get()}
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
            messagebox.showerror("Email Error", "Failed to send email: Incorrect username or password. Check your email settings.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BarberShopBooking(root)
    root.mainloop()






