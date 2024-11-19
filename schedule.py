import tkinter as tk
from tkinter import messagebox

class AvailabilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Barber Availability")
        self.selected_location = None
        self.selected_month = None
        self.selected_day = None
        self.selected_times = []

        self.create_widgets()

    def create_widgets(self):
        # Location Section
        tk.Label(self.root, text="Select Your Location").grid(row=0, column=0)
        locations = ["Downtown", "Old Montreal", "Cote-Des-Neiges"]
        for i, loc in enumerate(locations):
            button = tk.Button(self.root, text=loc, command=lambda loc=loc: self.select_location(loc))
            button.grid(row=1, column=i)

        # Month Section
        tk.Label(self.root, text="Select Month").grid(row=2, column=0)
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        for i, month in enumerate(months):
            button = tk.Button(self.root, text=month, command=lambda month=month: self.select_month(month))
            button.grid(row=3, column=i)

        # Day Section
        tk.Label(self.root, text="Select Day").grid(row=4, column=0)
        days = list(range(1, 32))
        for i, day in enumerate(days):
            button = tk.Button(self.root, text=str(day), command=lambda day=day: self.select_day(day))
            button.grid(row=5, column=i)

        # Time Slots Section
        tk.Label(self.root, text="Select Time Slots").grid(row=6, column=0)
        self.time_buttons = []
        times = [f"{hour}:{minute:02d}" for hour in range(9, 20) for minute in [0, 30]]
        for i, time in enumerate(times):
            button = tk.Button(self.root, text=time, command=lambda time=time: self.toggle_time_slot(time))
            button.grid(row=7 + i // 6, column=i % 6)
            self.time_buttons.append(button)

        # Action Buttons
        self.add_button = tk.Button(self.root, text="Add Availability", command=self.add_availability)
        self.add_button.grid(row=13, column=0)

        self.remove_button = tk.Button(self.root, text="Remove Availability", command=self.remove_availability)
        self.remove_button.grid(row=13, column=1)

    def select_location(self, location):
        self.selected_location = location

    def select_month(self, month):
        self.selected_month = month

    def select_day(self, day):
        self.selected_day = day

    def toggle_time_slot(self, time):
        if time in self.selected_times:
            self.selected_times.remove(time)
        else:
            self.selected_times.append(time)

    def add_availability(self):
        if not self.selected_location or not self.selected_month or not self.selected_day:
            messagebox.showerror("Error", "Please select location, month, and day.")
        elif not self.selected_times:
            messagebox.showerror("Error", "Please select at least one time slot.")
        else:
            messagebox.showinfo("Success", "Your availability has been updated.")
            self.reset_selection()

    def remove_availability(self):
        self.selected_times.clear()
        for button in self.time_buttons:
            button.config(bg="SystemButtonFace")

    def reset_selection(self):
        self.selected_location = None
        self.selected_month = None
        self.selected_day = None
        self.selected_times.clear()
        for button in self.time_buttons:
            button.config(bg="SystemButtonFace")


if __name__ == "__main__":
    root = tk.Tk()
    app = AvailabilityApp(root)
    root.mainloop()

