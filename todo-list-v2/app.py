from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)  # Create a new Flask application instance
TODO_FILE = "todo_list.txt"  # File to store tasks

def load_tasks():
    """Load tasks from the file."""
    if os.path.exists(TODO_FILE):  # Check if the file exists
        with open(TODO_FILE, "r") as file:  # Open the file in read mode
            tasks = file.readlines()  # Read all lines from the file
    else:
        tasks = []  # Initialize an empty list if the file does not exist
    return [task.strip() for task in tasks]  # Remove leading/trailing whitespace from each task

def save_tasks(tasks):
    """Save tasks to the file."""
    with open(TODO_FILE, "w") as file:  # Open the file in write mode
        for task in tasks:  # Iterate over the list of tasks
            file.write(task + "\n")  # Write each task to the file, followed by a newline

@app.route('/')
def index():
    """Render the home page with the list of tasks."""
    tasks = load_tasks()  # Load tasks from the file
    return render_template('index.html', tasks=tasks)  # Render the index template with tasks

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    """Render the add task page or handle task addition."""
    if request.method == 'POST':  # If the form is submitted
        task = request.form['task']  # Get the task from the form
        if task.strip() != "":  # Check if the task is not empty
            tasks = load_tasks()  # Load existing tasks
            tasks.append(task)  # Add the new task to the list
            save_tasks(tasks)  # Save the updated tasks to the file
        return redirect(url_for('index'))  # Redirect to the home page
    return render_template('add_task.html')  # Render the add task template

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """Render the edit task page or handle task update."""
    tasks = load_tasks()  # Load existing tasks
    if request.method == 'POST':  # If the form is submitted
        new_task = request.form['task']  # Get the new task from the form
        if new_task.strip() != "":  # Check if the new task is not empty
            tasks[task_id] = new_task  # Update the task at the specified index
            save_tasks(tasks)  # Save the updated tasks to the file
        return redirect(url_for('index'))  # Redirect to the home page
    task = tasks[task_id] if 0 <= task_id < len(tasks) else ""  # Get the task to edit
    return render_template('edit_task.html', task=task, task_id=task_id)  # Render the edit task template

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    """Handle task deletion."""
    tasks = load_tasks()  # Load existing tasks
    if 0 <= task_id < len(tasks):  # Check if the task index is valid
        tasks.pop(task_id)  # Remove the task at the specified index
        save_tasks(tasks)  # Save the updated tasks to the file
    return redirect(url_for('index'))  # Redirect to the home page

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application in debug mode
