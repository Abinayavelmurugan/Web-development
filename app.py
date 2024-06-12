from flask import Flask, jsonify, render_template
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Database connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "22-Feb-05"),
            database=os.getenv("DB_NAME", "Pharmacydb")
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Function to drop tables if they exist
def drop_tables(connection):
    try:
        cursor = connection.cursor()
        drop_table_queries = """
        DROP TABLE IF EXISTS Bill;
        DROP TABLE IF EXISTS Medicine;
        DROP TABLE IF EXISTS Employee;
        DROP TABLE IF EXISTS `Ordered Drugs`;
        DROP TABLE IF EXISTS Customer;
        """
        for query in drop_table_queries.split(';'):
            if query.strip():
                cursor.execute(query)
        connection.commit()
        cursor.close()
        print("Existing tables dropped successfully")
    except Error as e:
        print(f"Error dropping tables: {e}")

# Function to create tables
def create_tables(connection):
    try:
        cursor = connection.cursor()

        create_table_queries = """
        -- Create tables
        CREATE TABLE Customer (
            id              INT NOT NULL AUTO_INCREMENT, 
            `Name`          VARCHAR(255) NOT NULL, 
            Phone           BIGINT NOT NULL UNIQUE,
            address         VARCHAR(20),
            PRIMARY KEY (id)
        );

        CREATE TABLE `Ordered Drugs` (
            `Order ID`            INT NOT NULL AUTO_INCREMENT, 
            `Batch Number`        INT NOT NULL, 
            `Drug Name`           VARCHAR(255) NOT NULL,  
            `Ordered Quantity`    INT NOT NULL, 
            Price                 DECIMAL(10, 2) NOT NULL, 
            customerID            INT,
            CONSTRAINT fk_customer FOREIGN KEY (customerID) REFERENCES Customer(id),
            PRIMARY KEY (`Order ID`, `Drug Name`, `Batch Number`)
        );

        CREATE TABLE Employee (
            ID                INT NOT NULL AUTO_INCREMENT, 
            `Name`            VARCHAR(255) NOT NULL, 
            Role              VARCHAR(255) NOT NULL, 
            Salary            DECIMAL(10, 2) NOT NULL, 
            `Phone Number`    BIGINT NOT NULL, 
            PRIMARY KEY (ID)
        );

        CREATE TABLE Medicine (
            `Drug Name`       VARCHAR(255) NOT NULL, 
            `Batch Number`    INT NOT NULL, 
            MedicineType      VARCHAR(255) NOT NULL, 
            Manufacturer      VARCHAR(255) NOT NULL, 
            `Stock Quantity`  INT NOT NULL, 
            `Expiry Date`     DATE NOT NULL, 
            Price             DECIMAL(10, 2) NOT NULL, 
            PRIMARY KEY (`Drug Name`, `Batch Number`)
        );

        CREATE TABLE Bill (
            `Order ID`            INT NOT NULL, 
            `CustomerSSN`         INT NOT NULL, 
            `Total Amount`        DECIMAL(10, 2) NOT NULL, 
            `Customer Payment`    DECIMAL(10, 2) NOT NULL, 
            PRIMARY KEY (`Order ID`, `CustomerSSN`)
        );
        """

        for query in create_table_queries.split(';'):
            if query.strip():
                cursor.execute(query)

        connection.commit()
        cursor.close()
        print("Tables created successfully")
    except Error as e:
        print(f"Error creating tables: {e}")

# Function to insert dummy data
def insert_dummy_data(connection):
    try:
        cursor = connection.cursor()
        
        # Insert dummy values into Customer table
        customer_values = [
            (1, 'John', 1234567890, '123 Main St'),
            (2, 'Jane', 9876543210, '456 Elm St'),
            (3, 'Alice', 1112223333, '789 Oak St'),
            (4, 'Bob', 2223334444, '101 Pine St'),
            (5, 'Emily', 3334445555, '202 Cedar St')
        ]
        cursor.executemany("INSERT INTO Customer (id, `Name`, Phone, address) VALUES (%s, %s, %s, %s)", customer_values)

        # Insert dummy values into Ordered Drugs table
        ordered_drugs_values = [
            (100, 1, 'Drug A', 5, 25.00, 1),
            (101, 2, 'Drug B', 10, 50.00, 1),
            (102, 3, 'Drug C', 5, 37.50, 2),
            (103, 4, 'Drug D', 15, 225.00, 2),
            (104, 5, 'Drug E', 10, 250.00, 2)
        ]
        cursor.executemany("INSERT INTO `Ordered Drugs` (`Order ID`, `Batch Number`, `Drug Name`, `Ordered Quantity`, Price, customerID) VALUES (%s, %s, %s, %s, %s, %s)", ordered_drugs_values)

        # Insert dummy values into Employee table
        employee_values = [
            (1001, 'Alice', 'Pharmacist', 55000.00, 1234567890),
            (1002, 'Bob', 'Pharmacy Technician', 45000.00, 9876543210),
            (1003, 'Charlie', 'Pharmacist', 60000.00, 5556667777)
        ]
        cursor.executemany("INSERT INTO Employee (ID, `Name`, Role, Salary, `Phone Number`) VALUES (%s, %s, %s, %s, %s)", employee_values)

        # Insert dummy values into Medicine table
        medicine_values = [
            ('Drug A', 1, 'Tablet', 'Manufacturer A', 100, '2024-12-31', 5.00),
            ('Drug B', 2, 'Capsule', 'Manufacturer B', 150, '2023-10-15', 7.50),
            ('Drug C', 3, 'Syrup', 'Manufacturer C', 200, '2025-06-30', 10.00)
        ]
        cursor.executemany("INSERT INTO Medicine (`Drug Name`, `Batch Number`, MedicineType, Manufacturer, `Stock Quantity`, `Expiry Date`, Price) VALUES (%s, %s, %s, %s, %s, %s, %s)", medicine_values)

        # Insert dummy values into Bill table
        bill_values = [
            (10001, 123456789, 100.00, 80.00),
            (10002, 987654321, 75.00, 60.00),
            (10003, 111111111, 120.00, 100.00)
        ]
        cursor.executemany("INSERT INTO Bill (`Order ID`, `CustomerSSN`, `Total Amount`, `Customer Payment`) VALUES (%s, %s, %s, %s)", bill_values)

        # Commit the transaction
        connection.commit()
        print("Dummy data inserted successfully")
    except Error as e:
        print(f"Error inserting dummy data: {e}")

# Main function
connection = create_connection()
if connection:
    drop_tables(connection)
    create_tables(connection)
    insert_dummy_data(connection)
    connection.close()
    print("MySQL connection is closed")

# Route to render the frontend
@app.route('/')
def index():
    return render_template('index.html')

# Route to fetch and return stocked drugs data in JSON format
@app.route('/stocked-drugs')
def get_stocked_drugs():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Medicine")
    stocked_drugs_data = cursor.fetchall()
    connection.close()
    return jsonify(stocked_drugs_data)        

if __name__ == "__main__":
    app.run(debug=True)
