import sqlite3
import pandas as pd

# Update the path to point to your database file
DB_PATH = "C:/Users/jonat/Downloads/EmployeeDatabase.db"

def load_data(userID):
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)

    # Ensure userID is an integer for SQL query
    try:
        userID = int(userID)
    except ValueError:
        raise ValueError("User ID must be a valid integer.")

    # Query the database to get the specific barber's data
    query = "SELECT * FROM Employees WHERE userID = ?"
    barber_data = pd.read_sql_query(query, conn, params=(userID,))

    # Close the database connection
    conn.close()
    return barber_data


def get_sales_value():
    try:
        return float(input("Enter total barber shop sales: "))
    except ValueError:
        print("Invalid input for sales. Please enter a number.")
        return get_sales_value()


def main():
    # Get barber userID
    userID = input("Enter user ID: ")

    # Load data for the given userID from the database
    try:
        barber_data = load_data(userID)
    except ValueError as e:
        print(e)
        return

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
    salary = (sales_value * commission_rate) + tip_value + (hours_worked * 10)

    # Display the amount of pay
    print(f"The barber's total salary is: ${salary:.2f}")

if __name__ == "__main__":
    main()

