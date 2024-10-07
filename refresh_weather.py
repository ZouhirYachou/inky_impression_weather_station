import hitherdither
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto
from datetime import datetime

import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# Load weather code definitions from stellasphere git repo
import urllib.request, json 
with urllib.request.urlopen("https://gist.githubusercontent.com/stellasphere/9490c195ed2b53c707087c8c2db4ec0c/raw/76b0cb0ef0bfd8a2ec988aa54e30ecd1b483495d/descriptions.json") as url:
    weather_code_definition = json.load(url)


# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 48.8534,
	"longitude": 2.3488,
	"current": ["temperature_2m", "relative_humidity_2m", "is_day", "rain", "weather_code", "wind_speed_10m", "precipitation_probability"],
	"hourly": ["temperature_2m", "weather_code"],
	"daily": ["temperature_2m_max", "temperature_2m_min",],
	"timezone": "Europe/Berlin",
	"forecast_days": 2
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]

# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_relative_humidity_2m = current.Variables(1).Value()
current_is_day = current.Variables(2).Value()
current_rain = current.Variables(3).Value()
current_weather_code = current.Variables(4).Value()
current_wind_speed_10m = current.Variables(5).Value()
current_precipitation_probability = current.Variables(6).Value()

# Daily data
daily = response.Daily()
daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()

# Hourly data
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(1).ValuesAsNumpy()

##################################################################

# Initialize the Inky Impression display
inky_display = auto()
inky_display.set_border(inky_display.WHITE)

saturation = 0.5
thresholds = [64, 64, 64]
palette = hitherdither.palette.Palette(inky_display._palette_blend(saturation, dtype='uint24'))

# Create a new image with a white background
img = Image.new("P", (inky_display.width, inky_display.height), color=inky_display.WHITE)
draw = ImageDraw.Draw(img)

# Load fonts
font_file_bold = "fonts/RobotoCondensed-Bold.ttf"
font_file_Regular = "fonts/RobotoCondensed-Regular.ttf"
font_small = ImageFont.truetype(font_file_bold, 20)
font_medium = ImageFont.truetype(font_file_bold, 26)
font_large = ImageFont.truetype(font_file_Regular, 82)


# Define vars for current weather
if int(current_is_day) == 1 :
  day_or_night = 'day'
else:
  day_or_night = 'night'

location = "Paris, FR"
temperature = str(int(current_temperature_2m)) +"°C"
temperature_min = str(int(daily_temperature_2m_min[0]))
temperature_max = str(int(daily_temperature_2m_max[0]))
temperature_low_hi = temperature_min +"°C | " + temperature_max + "°C"
weather = weather_code_definition[str(int(current_weather_code))][day_or_night]["description"]
rain_chance = "Rain: " + str(int(current_precipitation_probability))+ " %"
humidity = "Hum: " + str(int(current_relative_humidity_2m))+ " %"
wind_speed = "Wind: " + str(int(current_wind_speed_10m))+ " km/h"

# Get current date
dt = datetime.now()
dt_format = dt.strftime("%A %d %B")

# get current hour to select correct offset forecast
current_hour = dt.hour

# Define text for forecast
forcast_2h_element_list = int(current_hour) + 2
forcast_2h_temp = str(int(hourly_temperature_2m[forcast_2h_element_list]))+"°C"
forcast_2h_weather = weather_code_definition[str(int(hourly_weather_code[forcast_2h_element_list]))][day_or_night]["description"]
forcast_2h_icon = str(int(hourly_weather_code[forcast_2h_element_list]))+ "_" + day_or_night

forcast_4h_element_list = int(current_hour) + 4
forcast_4h_temp = str(int(hourly_temperature_2m[forcast_4h_element_list]))+"°C"
forcast_4h_weather = weather_code_definition[str(int(hourly_weather_code[forcast_4h_element_list]))][day_or_night]["description"]
forcast_4h_icon = str(int(hourly_weather_code[forcast_4h_element_list]))+ "_" + day_or_night

forcast_6h_element_list = int(current_hour) + 6
forcast_6h_temp = str(int(hourly_temperature_2m[forcast_6h_element_list]))+"°C"
forcast_6h_weather = weather_code_definition[str(int(hourly_weather_code[forcast_6h_element_list]))][day_or_night]["description"]
forcast_6h_icon = str(int(hourly_weather_code[forcast_6h_element_list]))+ "_" + day_or_night

forcast_8h_element_list = int(current_hour) + 8
forcast_8h_temp = str(int(hourly_temperature_2m[forcast_8h_element_list]))+"°C"
forcast_8h_weather = weather_code_definition[str(int(hourly_weather_code[forcast_8h_element_list]))][day_or_night]["description"]
forcast_8h_icon = str(int(hourly_weather_code[forcast_8h_element_list]))+ "_" + day_or_night


# Draw the location
draw.text((10, 10), location, inky_display.BLACK, font=font_medium)

# Draw the date
date_text_width, date_text_height = (draw.textsize(dt_format, font=font_medium))
draw.text((inky_display.WIDTH - date_text_width - 10, 10), dt_format, inky_display.BLACK, font=font_medium)

# Draw the temperature
temp_text_width, temp_text_height = (draw.textsize(temperature, font=font_large))
draw.text((20, inky_display.HEIGHT / 5 ), temperature, inky_display.BLACK, font=font_large)

# Draw the temperature lows and highs
temp_low_text_width, temp_low_text_height = (draw.textsize(temperature_low_hi, font=font_small))
draw.text(((temp_text_width + 20 - temp_low_text_width) / 2, inky_display.HEIGHT / 2.5 ), temperature_low_hi, inky_display.BLACK, font=font_small)

# Draw the rain chance, humidity and wind 
rain_text_width, rain_text_height = (draw.textsize(rain_chance, font=font_medium))
humidity_text_height = (rain_text_height + 10)
wind_text_height = (rain_text_height + 10 ) * 2
draw.text(((inky_display.WIDTH / 1.4), (inky_display.HEIGHT / 5)), rain_chance, inky_display.BLACK, font=font_medium)
draw.text(((inky_display.WIDTH / 1.4), (inky_display.HEIGHT / 5) + humidity_text_height), humidity, inky_display.BLACK, font=font_medium)
draw.text(((inky_display.WIDTH / 1.4), (inky_display.HEIGHT / 5) + wind_text_height), wind_speed, inky_display.BLACK, font=font_medium)

 
# Draw the weather description
weather_text_width, weather_text_height = (draw.textsize(weather, font=font_medium))
draw.text(((inky_display.WIDTH - weather_text_width) / 2, (inky_display.HEIGHT + weather_text_height) / 2 ), weather, inky_display.BLACK, font=font_medium)

# Create function to draw the icons
def draw_icon(icon_code, icon_size_x, icon_size_y, pos_x, pos_y, palette, thresholds):
    icon_path = "icons/" + icon_code + ".jpg" 
    icon_img = Image.open(icon_path).convert("RGB")
    icon_img = icon_img.resize((icon_size_x, icon_size_y))
    image_dithered = hitherdither.ordered.bayer.bayer_dithering(icon_img, palette, thresholds, order=8)
    img.paste(image_dithered.convert("P"), (pos_x, pos_y))

# The the current weather icon
icon_code_jpg = str(int(current_weather_code)) + "_" + day_or_night
draw_icon(icon_code_jpg, 200, 200, int((inky_display.WIDTH - 200 ) / 2), 40, palette, thresholds)

forecast_separator_height = int(inky_display.HEIGHT / 1.5)

# Draw separators for forecast
draw.rectangle([inky_display.WIDTH / 4, forecast_separator_height, (inky_display.WIDTH / 4) + 3, inky_display.HEIGHT - 10], fill=inky_display.BLUE)
draw.rectangle([inky_display.WIDTH / 2, forecast_separator_height, (inky_display.WIDTH / 2) + 3, inky_display.HEIGHT - 10], fill=inky_display.BLUE)
draw.rectangle([inky_display.WIDTH / 1.33, forecast_separator_height, (inky_display.WIDTH / 1.33) + 3, inky_display.HEIGHT - 10], fill=inky_display.BLUE)

forecast_icon_height = int(inky_display.HEIGHT / 1.6)

def forecast_temp(temp, pos_x, pos_y):
    text_width, text_height = (draw.textsize(temp, font=font_medium))
    draw.text((pos_x - (text_width / 2), pos_y), temp, inky_display.BLACK, font=font_medium)

def forecast_weather(weather, pos_x, pos_y):
    text_width, text_height = (draw.textsize(weather, font=font_small))
    draw.text((pos_x - (text_width / 2), pos_y), weather, inky_display.BLACK, font=font_small)


# The the forcast +2h weather 
forecast_width_2h = int(inky_display.WIDTH / 8)
draw_icon(forcast_2h_icon, 80, 80, forecast_width_2h - 40 , forecast_icon_height, palette, thresholds)
forecast_temp(forcast_2h_temp, forecast_width_2h, forecast_icon_height + 80)
forecast_weather(forcast_2h_weather, forecast_width_2h, forecast_icon_height + 120)

# The the forcast +4h weather 
forecast_width_4h = int(inky_display.WIDTH / 8) * 3
draw_icon(forcast_4h_icon, 80, 80, forecast_width_4h - 40 , forecast_icon_height, palette, thresholds)
forecast_temp(forcast_4h_temp, forecast_width_4h, forecast_icon_height + 80)
forecast_weather(forcast_4h_weather, forecast_width_4h, forecast_icon_height + 120)

# The the forcast +6h weather 
forecast_width_6h = int(inky_display.WIDTH / 8) * 5
draw_icon(forcast_6h_icon, 80, 80, forecast_width_6h - 40 , forecast_icon_height, palette, thresholds)
forecast_temp(forcast_6h_temp, forecast_width_6h, forecast_icon_height + 80)
forecast_weather(forcast_6h_weather, forecast_width_6h, forecast_icon_height + 120)

# The the forcast +8h weather 
forecast_width_8h = int(inky_display.WIDTH / 8) * 7
draw_icon(forcast_8h_icon, 80, 80, forecast_width_8h - 40 , forecast_icon_height, palette, thresholds)
forecast_temp(forcast_8h_temp, forecast_width_8h, forecast_icon_height + 80)
forecast_weather(forcast_8h_weather, forecast_width_8h, forecast_icon_height + 120)

# Display the image on the Inky Impression
inky_display.set_image(img)
inky_display.show()
