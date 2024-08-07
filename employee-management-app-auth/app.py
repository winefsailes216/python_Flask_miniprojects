from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key to secure sessions and cookies

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)  # Initialize the Flask-Login extension with the Flask app
login_manager.login_view = 'login'  # Set the login view endpoint for unauthenticated users

# File paths for storing employee and user data
EMPLOYEES_FILE = 'employees.txt'  # Path to the file where employee data is stored
USERS_FILE = 'users.txt'  # Path to the file where user data is stored

# In-memory storage for employee data
employees = {}  # Dictionary to hold employee data
next_id = 1  # Counter for the next employee ID

# In-memory storage for users
users = {}  # Dictionary to hold user data

def load_users():
    """Load users from a file."""
    global users  # Declare that we are modifying the global users variable
    if os.path.exists(USERS_FILE):  # Check if the users file exists
        with open(USERS_FILE, 'r') as f:  # Open the users file in read mode
            for line in f:  # Iterate over each line in the file
                username, password = line.strip().split(':')  # Split line into username and password
                users[username] = {'password': password}  # Store username and password in the users dictionary

def save_users():
    """Save users to a file."""
    with open(USERS_FILE, 'w') as f:  # Open the users file in write mode
        for username, user_data in users.items():  # Iterate over users dictionary
            f.write(f'{username}:{user_data["password"]}\n')  # Write each user to the file

# User class
class User(UserMixin):
    def __init__(self, username):
        self.id = username  # Set the user ID to the username

# Load user
@login_manager.user_loader
def load_user(user_id):
    """Callback to reload a user."""
    return User(user_id) if user_id in users else None  # Return a User object if the user ID is in the users dictionary

def load_employees():
    """Load employees from a file."""
    global employees, next_id  # Declare that we are modifying the global employees and next_id variables
    if os.path.exists(EMPLOYEES_FILE):  # Check if the employees file exists
        with open(EMPLOYEES_FILE, 'r') as f:  # Open the employees file in read mode
            for line in f:  # Iterate over each line in the file
                emp_id, name, position, salary = line.strip().split(',')  # Split line into employee details
                employees[int(emp_id)] = {  # Add employee to the dictionary
                    'id': int(emp_id),
                    'name': name,
                    'position': position,
                    'salary': salary
                }
                next_id = max(next_id, int(emp_id) + 1)  # Update the next_id to the highest employee ID + 1

def save_employees():
    """Save employees to a file."""
    with open(EMPLOYEES_FILE, 'w') as f:  # Open the employees file in write mode
        for emp in employees.values():  # Iterate over employee dictionary values
            f.write(f"{emp['id']},{emp['name']},{emp['position']},{emp['salary']}\n")  # Write each employee to the file

# Load initial data
load_users()  # Load users from the file
load_employees()  # Load employees from the file

# Home route
@app.route('/')
@login_required
def index():
    """Render the home page with the list of employees."""
    return render_template('index.html', employees=employees)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Render the login page and handle login requests."""
    if request.method == 'POST':  # Check if the request method is POST (form submission)
        username = request.form['username']  # Retrieve the username from the form
        password = request.form['password']  # Retrieve the password from the form
        if username in users and users[username]['password'] == password:  # Validate credentials
            user = User(username)  # Create a User object
            login_user(user)  # Log in the user
            return redirect(url_for('index'))  # Redirect to the home page
        return 'Invalid credentials'  # Return an error message if credentials are invalid
    return render_template('login.html')  # Render the login page for GET requests

# Logout route
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """Log out the current user and redirect to the login page."""
    logout_user()  # Log out the current user
    return redirect(url_for('login'))  # Redirect to the login page

# Create a new employee
@app.route('/employees/add', methods=['POST'])
@login_required
def create_employee():
    """Create a new employee and save to file."""
    global next_id  # Declare that we are modifying the global next_id variable
    name = request.form['name']  # Retrieve the name from the form
    position = request.form['position']  # Retrieve the position from the form
    salary = request.form['salary']  # Retrieve the salary from the form
    employee = {  # Create a new employee dictionary
        'id': next_id,
        'name': name,
        'position': position,
        'salary': salary
    }
    employees[next_id] = employee  # Add the employee to the employees dictionary
    next_id += 1  # Increment the next_id counter
    save_employees()  # Save the updated employees data to the file
    return redirect(url_for('index'))  # Redirect to the home page

# Read all employees
@app.route('/employees')
@login_required
def get_employees():
    """Return a JSON list of all employees."""
    return jsonify(list(employees.values()))  # Convert employee dictionary values to JSON

# Read a single employee
@app.route('/employees/<int:employee_id>')
@login_required
def get_employee(employee_id):
    """Return a JSON object for a single employee by ID."""
    employee = employees.get(employee_id)  # Retrieve employee by ID
    if employee:
        return jsonify(employee)  # Return employee data as JSON
    return jsonify({"error": "Employee not found"}), 404  # Return an error message if employee is not found

# Update employee - render update form
@app.route('/employees/<int:employee_id>/edit', methods=['GET'])
@login_required
def edit_employee(employee_id):
    """Render the update form for an employee."""
    employee = employees.get(employee_id)  # Retrieve employee by ID
    if employee:
        return render_template('update.html', employee=employee)  # Render the update form with employee data
    return redirect(url_for('index'))  # Redirect to the home page if employee is not found

# Update employee - handle form submission
@app.route('/employees/<int:employee_id>/update', methods=['POST'])
@login_required
def update_employee(employee_id):
    """Update an employee's details and save to file."""
    employee = employees.get(employee_id)  # Retrieve employee by ID
    if employee:
        employee['name'] = request.form.get('name', employee['name'])  # Update name if provided
        employee['position'] = request.form.get('position', employee['position'])  # Update position if provided
        employee['salary'] = request.form.get('salary', employee['salary'])  # Update salary if provided
        save_employees()  # Save the updated employees data to the file
        return redirect(url_for('index'))  # Redirect to the home page
    return jsonify({"error": "Employee not found"}), 404  # Return an error message if employee is not found

# Delete an employee
@app.route('/employees/<int:employee_id>/delete', methods=['POST'])
@login_required
def delete_employee(employee_id):
    """Delete an employee and save changes to file."""
    employee = employees.pop(employee_id, None)  # Remove employee from dictionary
    if employee:
        save_employees()  # Save the updated employees data to the file
        return redirect(url_for('index'))  # Redirect to the home page
    return jsonify({"error": "Employee not found"}), 404  # Return an error message if employee is not found

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application in debug mode
