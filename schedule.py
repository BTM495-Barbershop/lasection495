class Barber:
    def __init__(self, name):
        self.name = name
        self.is_booked = False  
        self.availability = []  

    def set_status(self, status):
        """Sets the barber's status to Booked or Free."""
        self.is_booked = status
        status_str = "Booked" if status else "Free"
        print(f"{self.name} is now {status_str}.")

    def get_status(self):
        """Returns the barber's current status."""
        return "Booked" if self.is_booked else "Free"

    def set_availability(self, available_times):
        """Sets the barber's availability with a list of available time slots."""
        self.availability = available_times
        print(f"{self.name}'s availability has been updated.")

    def get_availability(self):
        """Returns the barber's current availability."""
        return self.availability


class BarberShop:
    def __init__(self):
        
        self.barbers = [Barber(name) for name in ["Barber1", "Barber2", "Barber3", "Barber4"]]

    def show_availability(self):
        """Displays the availability and booking status of all barbers."""
        print("\nBarber Availability:")
        for barber in self.barbers:
            status = barber.get_status()
            times = ", ".join([t.strftime("%H:%M") for t in barber.get_availability()])
            print(f"{barber.name} - Status: {status} | Available Times: {times if times else 'No availability set'}")

    def set_barber_status(self, barber_name, status):
        """Updates the booking status of a specified barber."""
        for barber in self.barbers:
            if barber.name == barber_name:
                barber.set_status(status)
                break
        else:
            print("Barber not found.")

    def set_barber_availability(self, barber_name, available_times):
        """Updates the availability of a specified barber."""
        for barber in self.barbers:
            if barber.name == barber_name:
                barber.set_availability(available_times)
                break
        else:
            print("Barber not found.")



