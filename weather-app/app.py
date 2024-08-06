#app.py
from flask import Flask, jsonify, render_template, request  # Import necessary functions from Flask
import requests  # Import requests for making HTTP requests
from weather_data import weather_data  # Import the mock weather data

app = Flask(__name__)  # Create a new Flask application instance

# Mock API endpoint to get weather data
@app.route('/api/weather/<city>', methods=['GET'])  # Define a route for getting weather data via an API call
def get_weather(city):
    city = city.title()  # Capitalize the city name for matching with mock data
    if city in weather_data:  # Check if the city is in the mock data
        return jsonify(weather_data[city])  # Return the weather data as a JSON response
    else:
        return jsonify({"error": "City not found"}), 404  # Return an error if the city is not found

# Web app route to display the home page
@app.route('/')
def index():
    return render_template('index.html')  # Render the home page template

# Web app route to handle the weather form submission
@app.route('/weather', methods=['POST'])
def weather():
    city = request.form.get('city')  # Get the city name from the form submission
    response = requests.get(f'http://127.0.0.1:5000/api/weather/{city}')  # Make a request to the mock API endpoint
    if response.status_code == 200:  # Check if the API request was successful
        data = response.json()  # Parse the JSON response
        return render_template('result.html', city=city, data=data)  # Render the result page with weather data
    else:
        return render_template('result.html', city=city, data=None)  # Render the result page with an error message

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application in debug mode
