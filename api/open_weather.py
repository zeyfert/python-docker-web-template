from api import OpenWeather

def main():
    open_weather = OpenWeather('Larnaka', '')
    open_weather.send_data_to_mongo()

if __name__ == '__main__':
    main()
