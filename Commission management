import pandas as pd

def load_data():
    data = pd.read_csv('MOCK_DATA.csv')
    return data

def get_sales_value():
    try:
        return float(input("Enter total barber shop sales: "))
    except ValueError:
        print("Invalid input for sales. Please enter a number.")
        return get_sales_value()

def main():
    # Load data from CSV
    data = load_data()

    # Get barber userID
    userID = input("Enter user ID: ")

    # Filter data by userID
    barber_data = data[data['userID'] == int(userID)]

    if barber_data.empty:
        print("User ID not found.")
        return

    # Extract values for the barber
    commission_rate = barber_data['commissionRate'].values[0]
    hours_worked = barber_data['hoursWorked'].values[0]
    tip_value = barber_data['tipValue'].values[0]

    # Prompt for and get the amount of sales
    sales_value = get_sales_value()

    # Calculate total salary
    salary = (sales_value * commission_rate) + tip_value + (hours_worked *10)

    # Display the amount of pay
    print(f"The barber's total salary is: ${salary:.2f}")

if __name__ == "__main__":
    main()
