# inky_impression_weather_station
Repos with python scripts to diplay current weather and forcast on inky Impression displays
It uses the open-meteo Weather API to retreive weather and focast data
This python script has been tested on RPI 3 and RPI4 with the Inky Impression 7 colour display 5.7 inches, it should also work with the 7.3 inches variant.

The current state is unfinished:
To do list:
- Improve documentation
- Add missing icons for each weather code
- Load config.yml instead of using values in the script
- Create bash script to automate installation
- Add a cronjob to refresh the weather and forcast every hour or less
- Upload STL files for the 3D Printed case

# Requirements
- Raspberry Pi 3 or 4
- Inky Impression 7 Colour display (5.7 or 7.3 inches variant)
- Debian Bullseye

# Installation
- Enable SPI and I2C on the RPI
- Clone this repo
- Install python3 and python3-pip
- Install python libs (PyYAML,pandas, retry-requests, Pillow, openmeteo-requests, inky and hitherdither)

![alt text](https://i.imgur.com/0aoBufb.jpeg)
