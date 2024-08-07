from flask import Flask, render_template, request  # Import necessary modules from Flask
import requests  # Import requests module for making HTTP requests

app = Flask(__name__)  # Create a Flask application instance

# OpenWeatherMap API key (replace with your own)
API_KEY = '2700e3c31449b6feaaad1b4e48951b01'

@app.route('/', methods=['GET', 'POST'])  # Define a route for the root URL ('/'), supporting GET and POST methods
def index():
    if request.method == 'POST':  # Check if the request method is POST (form submission)
        city = request.form['city']  # Retrieve the value of 'city' from the submitted form data
        if city:
            # Fetch weather data from OpenWeatherMap API using the city name
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
            response = requests.get(url)  # Send a GET request to the API endpoint
            if response.status_code == 200:  # Check if the API request was successful
                weather_data = response.json()  # Convert API response to JSON format
                return render_template('result.html', city=city, weather=weather_data)  # Render result.html template with weather data
            else:
                return render_template('result.html', city=city, error='City NOT FOUND 404')  # Render result.html template with error message
    return render_template('index.html')  # Render index.html template for GET requests and initial page load

if __name__ == '__main__':
    app.run(debug=True)  # Start the Flask application in debug mode if executed directly
