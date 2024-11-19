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

        # Set dark gray background
        self.root.configure(bg="#2b2b2b")

        # Initialize booking information
        self.location = tk.StringVar()
        self.barber = tk.StringVar()
        self.service_type = tk.StringVar()
        self.time_slot = tk.StringVar()
        self.client_name = tk.StringVar()
        self.email = tk.StringVar()
        self.phone_number = tk.StringVar()
        self.payment_method = tk.StringVar()

        # Database connection
        self.conn = sqlite3.connect('barbershop.db')
        self.cursor = self.conn.cursor()

        # Build interface
        self.build_interface()

    def build_interface(self):
        common_label_style = {"bg": "#2b2b2b", "fg": "white"}  # For labels
        entry_style = {"bg": "white", "fg": "black"}  # Standard entry style

        tk.Label(self.root, text="Enter Client Name", **common_label_style).pack()
        tk.Entry(self.root, textvariable=self.client_name, **entry_style).pack()

        tk.Label(self.root, text="Select Location", **common_label_style).pack()
        tk.Button(self.root, text="Cote-Des-Neiges", command=lambda: self.set_location("Cote-Des-Neiges"), activebackground="yellow").pack()
        tk.Button(self.root, text="Old Montreal", command=lambda: self.set_location("Old Montreal"), activebackground="yellow").pack()
        tk.Button(self.root, text="Downtown", command=lambda: self.set_location("Downtown"), activebackground="yellow").pack()

        tk.Label(self.root, text="Select Barber", **common_label_style).pack()
        tk.Button(self.root, text="Gonz", command=lambda: self.set_barber("Gonz"), activebackground="yellow").pack()
        tk.Button(self.root, text="Mahir", command=lambda: self.set_barber("Mahir"), activebackground="yellow").pack()
        tk.Button(self.root, text="Roland", command=lambda: self.set_barber("Roland"), activebackground="yellow").pack()

        tk.Label(self.root, text="Select Service Type", **common_label_style).pack()
        tk.Button(self.root, text="Haircut $40 (10pts)", command=lambda: self.set_service_type("Haircut"), activebackground="yellow").pack()
        tk.Button(self.root, text="Haircut & Beard $50 (20pts)", command=lambda: self.set_service_type("Haircut & Beard"), activebackground="yellow").pack()
        tk.Button(self.root, text="Braids $70 (30pts)", command=lambda: self.set_service_type("Braids"), activebackground="yellow").pack()

        tk.Label(self.root, text="Select Time Slot", **common_label_style).pack()
        tk.Button(self.root, text="Choose Day and Time Slot", command=self.show_time_slot_page, activebackground="yellow").pack()

        tk.Label(self.root, text="Enter Email", **common_label_style).pack()
        tk.Entry(self.root, textvariable=self.email, **entry_style).pack()

        tk.Label(self.root, text="Enter Phone Number", **common_label_style).pack()
        tk.Entry(self.root, textvariable=self.phone_number, **entry_style).pack()

        tk.Label(self.root, text="Select Payment Method", **common_label_style).pack()
        tk.Button(self.root, text="Pay in Person", command=lambda: self.set_payment_method("In Person"), activebackground="yellow").pack()
        tk.Button(self.root, text="Pay with Debit/Visa", command=lambda: self.set_payment_method("Debit/Visa"), activebackground="yellow").pack()

        tk.Button(self.root, text="Book Appointment", command=self.book_appointment, activebackground="yellow").pack()

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
        payment_window.configure(bg="#2b2b2b")  # Dark background for the new window

        tk.Label(payment_window, text="Card Number", bg="#2b2b2b", fg="white").pack()
        card_number = tk.Entry(payment_window)
        card_number.pack()

        tk.Label(payment_window, text="Expiry Date (MM/YY)", bg="#2b2b2b", fg="white").pack()
        expiry_date = tk.Entry(payment_window)
        expiry_date.pack()

        tk.Label(payment_window, text="CRC Code", bg="#2b2b2b", fg="white").pack()
        crc_code = tk.Entry(payment_window)
        crc_code.pack()

        tk.Label(payment_window, text="Full Name", bg="#2b2b2b", fg="white").pack()
        full_name = tk.Entry(payment_window)
        full_name.pack()

        tk.Button(payment_window, text="Confirm Payment", command=payment_window.destroy, activebackground="yellow").pack()

    def show_time_slot_page(self):
        time_slot_window = tk.Toplevel(self.root)
        time_slot_window.title("Select Day and Time Slot")
        time_slot_window.configure(bg="#2b2b2b")  # Set dark background for the new window

        common_label_style = {"bg": "#2b2b2b", "fg": "white"}
        tk.Label(time_slot_window, text="Available Time Slots", **common_label_style).pack()

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        hours = [f"{hour}:00" for hour in range(9, 17)]

        for day in days:
            frame = tk.Frame(time_slot_window, bg="#2b2b2b")  # Frame with dark background
            frame.pack(anchor="w")

            tk.Label(frame, text=day, **common_label_style).pack(side="left")
            for hour in hours:
                combined_slot = f"{day} {hour}"
                query = """
                SELECT timeSlot FROM bookings WHERE barber = ? AND location = ? AND timeSlot = ?
                """
                is_booked = self.cursor.execute(query, (self.barber.get(), self.location.get(), combined_slot)).fetchone()

                if is_booked:
                    tk.Button(
                        frame,
                        text=f"{hour} - Unavailable",
                        state=tk.DISABLED,
                        bg="#444444",
                        fg="white"
                    ).pack(side="left", padx=2)
                else:
                    tk.Button(
                        frame,
                        text=hour,
                        command=lambda s=combined_slot: self.select_time_slot(s, time_slot_window),
                        activebackground="yellow",
                        bg="white"
                    ).pack(side="left", padx=2)

    def select_time_slot(self, slot, window):
        self.set_time_slot(slot)
        window.destroy()

    def book_appointment(self):
        if not self.time_slot.get() or not self.client_name.get():
            messagebox.showerror("Error", "Please enter client name and select a time slot.")
            return

        query = """
        SELECT * FROM bookings WHERE barber = ? AND location = ? AND timeSlot = ?
        """
        existing_booking = self.cursor.execute(query, (self.barber.get(), self.location.get(), self.time_slot.get())).fetchone()

        if existing_booking:
            messagebox.showerror("Unavailable", "This time slot is already booked. Please choose another slot.")
        else:
            try:
                self.cursor.execute("""
                INSERT INTO bookings (location, barber, serviceType, timeSlot, clientName, email, phoneNumber, paymentMethod) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, 
                (self.location.get(), self.barber.get(), self.service_type.get(), self.time_slot.get(), self.client_name.get(),
                 self.email.get(), self.phone_number.get(), self.payment_method.get()))
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
            messagebox.showerror("Email Error", "Failed to send email: Incorrect username or password. Check your email settings.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BarberShopBooking(root)
    root.mainloop()


