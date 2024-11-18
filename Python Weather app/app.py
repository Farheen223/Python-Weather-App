import requests
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageTk

# API key
api_key = 'dba75e34d3dcf327d464e693313930d1'

# Store recent searches
recent_searches = []

# Function to get weather data from the OpenWeather API
def get_weather_data(city, units):
    try:
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&units={units}&APPID={api_key}")
        response.raise_for_status()  # Check if the request was successful
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"Error: {err}")
        return None

# Function to get 5-day weather forecast from OpenWeather API
def get_5_day_forecast(city):
    try:
        response = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&APPID={api_key}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"Error: {err}")
        return None

# Function to convert units from user-friendly input to OpenWeather API parameters
def unit_converter(unit_input):
    if unit_input.lower() == 'c':
        return 'metric', 'Celsius'
    elif unit_input.lower() == 'f':
        return 'imperial', 'Fahrenheit'
    else:
        print("Invalid unit choice, defaulting to Celsius.")
        return 'metric', 'Celsius'

# Function to convert UTC time to local time using the timezone offset
def get_local_time(timezone_offset):
    utc_time = datetime.now(timezone.utc)
    local_time = utc_time + timedelta(seconds=timezone_offset)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

# Function to update the weather icon based on the weather condition
def update_weather_icon(weather):
    try:
        if weather == 'Clear':
            img = Image.open("clear.png")
        elif weather == 'Clouds':
            img = Image.open("cloudy.png")
        elif weather == 'Rain':
            img = Image.open("rainy.png")
        elif weather == 'Snow':
            img = Image.open("snowy.png")
        else:
            img = Image.open("weather-icon.png")  # Use a default image for other conditions
        img = img.resize((100, 100), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(img)
        weather_image_label.config(image=logo_img)
        weather_image_label.image = logo_img  # Keep a reference to avoid garbage collection
    except Exception as e:
        print(f"Error loading weather icon: {e}")

# Function to display the weather
def display_weather():
    city = city_entry.get()
    units, unit_label = unit_converter(unit_var.get())

    # Get weather data
    weather_data = get_weather_data(city, units)

    # Check if the data was retrieved successfully
    if weather_data and weather_data.get('cod') == 200:
        # Weather data extraction
        weather = weather_data['weather'][0]['main']
        description = weather_data['weather'][0]['description'].capitalize()
        temp = round(weather_data['main']['temp'])
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        timezone_offset = weather_data['timezone']

        # Get the local time based on the city's timezone
        local_time = get_local_time(timezone_offset)

        # Update labels with the weather data
        result_label.config(text=f"Weather in {city.capitalize()}:\n"
             f"Condition: {weather} ({description})\n"
             f"Temperature: {temp}°{unit_label}\n"
             f"Humidity: {humidity}%\n"
             f"Wind Speed: {wind_speed} {'m/s' if unit_label == 'Celsius' else 'mph'}\n"
             f"Local Time: {local_time}")

        # Update weather icon based on the weather condition
        update_weather_icon(weather)

        # Add to recent searches and update the listbox
        if city not in recent_searches:
            recent_searches.append(city)
            recent_listbox.insert(tk.END, city)

        # Display 5-day weather forecast
        display_forecast()
        
    else:
        # Show an error message if the city is not found
        result_label.config(text="City not found or an error occurred.")

# Function to display 5-day forecast
def display_forecast():
    city = city_entry.get()
    forecast_data = get_5_day_forecast(city)

    if forecast_data:
        clear_forecast_boxes()  # Clear previous forecast

        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for i in range(0, 40, 8):  # Display every 8th entry (one per day)
            day = forecast_data['list'][i]
            date_text = day['dt_txt'].split(" ")[0]
            day_of_week = days_of_week[datetime.strptime(date_text, '%Y-%m-%d').weekday()]
            temp = day['main']['temp']
            description = day['weather'][0]['description'].capitalize()

            # Create forecast box for each day
            day_frame = tk.Frame(forecast_frame, bg='#87CEEB',  bd=0, padx=5, pady=5, height = 90, width=50)
            day_frame.grid(row=0, column=i//8, padx=5, pady=5, sticky="nsew")

            day_label = tk.Label(day_frame, text=day_of_week, font=("Helvetica", 9, "bold"), bg='#87CEEB', fg='black')
            day_label.pack(pady=5)

            temp_label = tk.Label(day_frame, text=f"{temp}°C", font=("Helvetica", 8), bg='#87CEEB', fg='black')
            temp_label.pack(pady=5)

            description_label = tk.Label(day_frame, text=description, font=("Helvetica", 8), bg='#87CEEB', fg='black')
            description_label.pack(pady=5)
    else:
        forecast_label.config(text="Unable to retrieve forecast data.")

# Function to clear forecast boxes before displaying new forecast
def clear_forecast_boxes():
    for widget in forecast_frame.winfo_children():
        widget.destroy()

# Function to display weather for a city from recent searches
def display_recent_weather(event):
    try:
        selected_city = recent_listbox.get(recent_listbox.curselection())
        city_entry.delete(0, tk.END)
        city_entry.insert(0, selected_city)
        display_weather()
    except tk.TclError:
        print("No city selected from the listbox.")

# Function to switch to the "Recent Searches" tab
def open_recent_searches_tab():
    notebook.select(1)  # Switch to the second tab (recent searches)

# Create the main application window
app = tk.Tk()
app.title("Weather App")
app.geometry("500x700")
app.configure(bg="#ADD8E6")  # Light blue background

# Create Notebook (tabs)
notebook = ttk.Notebook(app)
notebook.pack(expand=True, fill="both")

# Create two tabs: one for the weather search and one for recent searches
weather_tab = tk.Frame(notebook, bg="#ADD8E6")
recent_searches_tab = tk.Frame(notebook, bg="#ADD8E6")

# Add tabs to the notebook
notebook.add(weather_tab, text="Weather Search")
notebook.add(recent_searches_tab, text="Recent Searches")

# Weather Tab content
# Initialize a placeholder label for the weather icon
img = Image.open("weather-icon.png")
img = img.resize((100, 100), Image.Resampling.LANCZOS)
logo_img = ImageTk.PhotoImage(img)

# Center the image
weather_image_label = tk.Label(weather_tab, image=logo_img, bg='#ADD8E6')
weather_image_label.pack(pady=(50, 10))

# Label to display the weather result (positioned under the image)
result_label = tk.Label(weather_tab, text="", font=("Helvetica", 10), justify="left", bg='#ADD8E6', fg='black')
result_label.pack(pady=10)

# Frame for 5-day forecast
forecast_frame = tk.Frame(weather_tab, bg="#ADD8E6")  # Defined forecast_frame 
forecast_frame.pack(pady=10)

# Define the forecast_label to display errors or status
forecast_label = tk.Label(weather_tab, text="", font=("Helvetica", 10), justify="left", bg='#ADD8E6', fg='black')
forecast_label.pack(pady=10)

# Frame to hold the city label and entry side by side
city_frame = tk.Frame(weather_tab, bg="#ADD8E6")
city_frame.pack(pady=10)

# City label and entry (aligned together)
city_label = tk.Label(city_frame, text="Enter City:", font=("Helvetica", 14, "bold"), bg='#ADD8E6', fg='black')
city_label.pack(side="left", padx=5)

city_entry = tk.Entry(city_frame, font=("Helvetica", 11), bg='#E0FFFF', fg='black', width=20)  # Light Cyan background
city_entry.pack(side="left", padx=5)

# Unit selection (Celsius or Fahrenheit)
unit_var = tk.StringVar(value="c")  # This is where we define unit_var

# Frame to hold unit selection and radio buttons side by side
unit_frame = tk.Frame(weather_tab, bg="#ADD8E6")
unit_frame.pack(pady=5)

unit_label = tk.Label(unit_frame, text="Select Unit:", font=("Helvetica", 10), bg='#ADD8E6', fg='black')
unit_label.pack(side="left", padx=5)

celsius_radio = tk.Radiobutton(unit_frame, text="Celsius", variable=unit_var, value="c", font=("Helvetica", 10), bg='#ADD8E6', fg='black', selectcolor='light gray')
celsius_radio.pack(side="left", padx=5)

fahrenheit_radio = tk.Radiobutton(unit_frame, text="Fahrenheit", variable=unit_var, value="f", font=("Helvetica", 10), bg='#ADD8E6', fg='black', selectcolor='light gray')
fahrenheit_radio.pack(side="left", padx=5)

# Submit button to get the weather
submit_button = tk.Button(weather_tab, text="Get Weather", command=display_weather, font=("Helvetica", 14, "bold"), bg='#4682B4', fg='white')
submit_button.pack(pady=20)

# Button to open recent searches tab
recent_searches_button = tk.Button(weather_tab, text="Open Recent Searches", command=open_recent_searches_tab, font=("Helvetica", 12, "bold"), bg='#4682B4', fg='white')
recent_searches_button.pack(pady=10)


# Recent Searches Tab content
recent_label = tk.Label(recent_searches_tab, text="Recent Searches:", font=("Helvetica", 14), bg='#ADD8E6', fg='black')
recent_label.pack(pady=10)

# Listbox to show recent searches
recent_listbox = tk.Listbox(recent_searches_tab, height=10, font=("Helvetica", 12), bg='#E0FFFF', fg='black')
recent_listbox.pack(pady=10, padx=20, fill='x')
recent_listbox.bind('<<ListboxSelect>>', display_recent_weather)

# Start the Tkinter event loop
app.mainloop()