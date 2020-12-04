#!/usr/bin/env python3
# smartmirror.py
# requirements
# requests, feedparser, traceback, Pillow

from tkinter import *
import locale
import threading
import time
import requests
import json
import traceback
import feedparser

from PIL import Image, ImageTk
from contextlib import contextmanager

LOCALE_LOCK = threading.Lock()

ui_locale = ''  # e.g. 'fr_FR' fro French, '' as default
time_format = 24  # 12 or 24
# date_format = "%b %d, %Y" # check python doc for strftime() for options
date_format = "%d %b"  # check python doc for strftime() for options
news_country_code = 'us'
weather_api_token = '<TOKEN>'  # create account at https://darksky.net/dev/
weather_lang = 'en'  # see https://darksky.net/dev/docs/forecast for full list of language parameters values
weather_unit = 'us'  # see https://darksky.net/dev/docs/forecast for full list of unit parameters values
latitude = None  # Set this if IP location lookup does not work for you (must be a string)
longitude = None  # Set this if IP location lookup does not work for you (must be a string)
xlarge_text_size = 75
large_text_size = 60
medium_text_size = 28
small_text_size = 18
i = 0
forecast2 = ''
wiadomosc = ''


@contextmanager
def setlocale(name):  # thread proof function to work with locale
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)


# maps open weather icons to
# icon reading is not impacted by the 'lang' parameter
icon_lookup = {
    '1': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Sun.png",
    '2': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Sun.png",
    '3': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/PartlySunny.png",
    '4': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/PartlySunny.png",
    '5': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Haze.png",
    '11': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Haze.png",
    '37': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Haze.png",
    '6': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Cloud.png",
    '7': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Cloud.png",
    '8': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Cloud.png",
    '38': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Cloud.png",
    '12': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Rain.png",
    '13': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Rain.png",
    '14': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Rain.png",
    '18': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Rain.png",
    '39': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Rain.png",
    '40': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Rain.png",
    '15': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Storm.png",
    '16': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Storm.png",
    '17': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Storm.png",
    '41': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Storm.png",
    '42': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Storm.png",
    '19': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Snow.png",
    '20': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Snow.png",
    '21': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Snow.png",
    '22': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Snow.png",
    '23': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Snow.png",
    '43': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Snow.png",
    '44': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Snow.png",
    '24': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Hail.png",
    '25': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Hail.png",
    '26': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Hail.png",
    '29': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Hail.png",
    '32': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Wind.png",
    '33': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Moon.png",
    '34': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Moon.png",
    '35': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/PartlyMoon.png",
    '36': "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/PartlyMoon.png"
}


class Clock(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        # initialize time label
        self.time1 = ''
        self.timeLbl = Label(self, font=('Helvetica', xlarge_text_size), fg="white", bg="black")
        self.timeLbl.pack(side=TOP, anchor=E)
        # initialize day of week
        self.day_of_week1 = ''
        # self.dayOWLbl = Label(self, text=self.day_of_week1, font=('Helvetica', small_text_size), fg="white", bg="black")
        # self.dayOWLbl.pack(side=TOP, anchor=CENTER)
        # initialize date label
        self.date1 = ''
        self.dateLbl = Label(self, text=self.day_of_week1 + ', ' + self.date1, font=('Helvetica', small_text_size),
                             fg="white", bg="black")
        self.dateLbl.pack(side=TOP, anchor=CENTER)
        self.tick()

    def tick(self):
        with setlocale(ui_locale):
            if time_format == 12:
                time2 = time.strftime('%I:%M %p')  # hour in 12h format
            else:
                time2 = time.strftime('%H:%M')  # hour in 24h format

            day_of_week2 = time.strftime('%A')
            date2 = time.strftime(date_format)
            # if time string has changed, update it
            if time2 != self.time1:
                self.time1 = time2
                self.timeLbl.config(text=time2)
            # if day_of_week2 != self.day_of_week1:
            #     self.day_of_week1 = day_of_week2
            #     self.dayOWLbl.config(text=day_of_week2)
            if date2 != self.date1:
                self.date1 = date2
                self.dateLbl.config(text=day_of_week2 + ', ' + date2)
            # calls itself every 200 milliseconds
            # to update the time display as needed
            # could use >200 ms, but display gets jerky
            self.timeLbl.after(200, self.tick)


class Weather(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.temperature = ''
        self.forecast = ''
        self.location = ''
        self.currently = ''
        self.icon = ''
        self.iconLbl = Label(self, bg="black")
        self.iconLbl.pack(side=TOP, anchor=CENTER, padx=20, pady=0)
        self.degreeFrm = Frame(self, bg="black")
        self.degreeFrm.pack(side=TOP, anchor=W)
        self.temperatureLbl = Label(self, font=('Helvetica', large_text_size), fg="white", bg="black")
        self.temperatureLbl.pack(side=TOP, anchor=CENTER, pady=0)
        # self.currentlyLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        # self.currentlyLbl.pack(side=TOP, anchor=CENTER)
        self.forecastLbl = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.forecastLbl.pack(side=TOP, anchor=CENTER)
        self.locationLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.locationLbl.pack(side=TOP, anchor=CENTER)
        self.get_weather()
        self.show_forecast()
    

    def get_ip(self):
        try:
            ip_url = "http://jsonip.com/"
            req = requests.get(ip_url)
            ip_json = json.loads(req.text)
            return ip_json['ip']
        except Exception as e:
            traceback.print_exc()
            return "Error: %s. Cannot get ip." % e

    def show_forecast(self):
        global i
        if len(wiadomosc) >12:
            forecast2 = wiadomosc[i:i+12]
            i += 3
            if i > len(wiadomosc):
                i = 0
            if self.forecast != forecast2:
                self.forecast = forecast2
                self.forecastLbl.config(text=forecast2)
            self.after(1000, self.show_forecast)
        elif len(wiadomosc) < 12:
            forecast2 = wiadomosc
            if self.forecast != forecast2:
                self.forecast = forecast2
                self.forecastLbl.config(text=forecast2)
            self.after(10000, self.show_forecast)

    def get_weather(self):
        try:

            if latitude is None and longitude is None:
                # get location
                location_req_url = "http://freegeoip.net/json/%s" % self.get_ip()
                # r = requests.get("http://dataservice.accuweather.com/forecasts/v1/daily/5day/264863?apikey=iKTjxzrAqZoG3offbdoaxF2XyAhWya3Q") #(location_req_url)
                # location_obj = json.loads(r.text)
                #
                # lat = location_obj['latitude']
                # lon = location_obj['longitude']

                location2 = "Wyszków, mazowieckie"

                # get weather
                # weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, lat,lon,weather_lang,weather_unit)
            else:
                location2 = ""
                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (
                    weather_api_token, latitude, longitude, weather_lang, weather_unit)

            r = requests.get(
                "http://dataservice.accuweather.com/currentconditions/v1/264863?apikey=A4kdm8u4wiZD6rwAVfLyneoH8sAG82LG&language=pl-PL")
            api = json.loads(r.content)[0]

            degree_sign = u'\N{DEGREE SIGN}'
            # temperature2 = "%s%s" % (str(int(weather_obj['currently']['temperature'])), degree_sign)
            Temperature = api.get('Temperature').get('Metric').get('Value')
            temperature2 = "%s %sC" % (str(round(Temperature)), degree_sign)
            # currently2 = weather_obj['currently']['summary']
            currently2 = "currently2"
            # forecast2 = weather_obj["hourly"]["summary"]
            WeatherText = api.get('WeatherText')
            global wiadomosc
            wiadomosc = WeatherText
            global forecast2

            # icon_id = weather_obj['currently']['icon']
            IsDayTime = api.get('IsDayTime')
            WeatherIcon = api.get('WeatherIcon')
            icon_id = "icon_id"
            icon_id = str(WeatherIcon)
            icon2 = None

            if icon_id in icon_lookup:
                icon2 = icon_lookup[icon_id]
            elif (icon_id == "30") | (icon_id == "31"):
                if(IsDayTime):
                    icon2 = "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Sun.png"
                else:
                    icon2 = "/home/pi/Desktop/SmartMirror/Smart-Mirror-master/assets/Moon.png"

            if icon2 is not None:
                if self.icon != icon2:
                    self.icon = icon2
                    image = Image.open(icon2)
                    image = image.resize((200, 200), Image.ANTIALIAS)
                    image = image.convert('RGB')
                    photo = ImageTk.PhotoImage(image)

                    self.iconLbl.config(image=photo)
                    self.iconLbl.image = photo
            else:
                # remove image
                self.iconLbl.config(image='')

            # if self.currently != currently2:
            #     self.currently = currently2
            #     self.currentlyLbl.config(text=currently2)
            if self.temperature != temperature2:
                self.temperature = temperature2
                self.temperatureLbl.config(text=temperature2)
            if self.location != location2:
                if location2 == ", ":
                    self.location = "Cannot Pinpoint Location"
                    self.locationLbl.config(text="Cannot Pinpoint Location")
                else:
                    self.location = location2
                    self.locationLbl.config(text=location2)
        except Exception as e:
            traceback.print_exc()
            print("Error: %s. Cannot get weather." % e)

        self.after(1800000, self.get_weather)

    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32


class Images(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='pink')
        self.my_img1 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/1.jpg"))
        self.my_img2 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/2.jpg"))
        self.my_img3 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/3.jpg"))
        self.my_img4 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/4.jpg"))
        self.my_img5 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/5.jpg"))
        self.my_img6 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/6.jpg"))
        self.my_img7 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/7.jpg"))
        self.my_img8 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/8.jpg"))
        self.my_img9 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/9.jpg"))
        self.my_img10 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/10.jpg"))
        self.my_img11 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/11.jpg"))
        self.my_img12 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/12.jpg"))
        self.my_img13 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/13.jpg"))
        self.my_img14 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/14.jpg"))
        self.my_img15 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/15.jpg"))
        self.my_img16 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/16.jpg"))
        self.my_img17 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/17.jpg"))
        self.my_img18 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/18.jpg"))
        self.my_img19 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/19.jpg"))
        self.my_img20 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/20.jpg"))
        self.my_img21 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/21.jpg"))
        self.my_img22 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/22.jpg"))
        self.my_img23 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/23.jpg"))
        self.my_img24 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/24.jpg"))
        self.my_img25 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/25.jpg"))
        self.my_img26 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/26.jpg"))
        self.my_img27 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/27.jpg"))
        self.my_img28 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/28.jpg"))
        self.my_img29 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/29.jpg"))
        self.my_img30 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/30.jpg"))
        self.my_img31 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/31.jpg"))
        self.my_img32 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/32.jpg"))
        self.my_img33 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/33.jpg"))
        self.my_img34 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/34.jpg"))
        self.my_img35 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/35.jpg"))
        self.my_img36 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/36.jpg"))
        self.my_img37 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/37.jpg"))
        self.my_img38 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/38.jpg"))
        self.my_img39 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/39.jpg"))
        self.my_img40 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/40.jpg"))
        self.my_img41 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/41.jpg"))
        self.my_img42 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/42.jpg"))
        self.my_img43 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/43.jpg"))
        self.my_img44 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/44.jpg"))
        self.my_img45 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/45.jpg"))
        self.my_img46 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/46.jpg"))
        self.my_img47 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/47.jpg"))
        self.my_img48 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/48.jpg"))
        self.my_img49 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/49.jpg"))
        self.my_img50 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/50.jpg"))
        self.my_img51 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/51.jpg"))
        self.my_img52 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/52.jpg"))
        self.my_img53 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/53.jpg"))
        self.my_img54 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/54.jpg"))
        self.my_img55 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/55.jpg"))
        self.my_img56 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/56.jpg"))
        self.my_img57 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/57.jpg"))
        self.my_img58 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/58.jpg"))
        self.my_img59 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/59.jpg"))
        self.my_img60 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/60.jpg"))
        self.my_img61 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/61.jpg"))
        self.my_img62 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/62.jpg"))
        self.my_img63 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/63.jpg"))
        self.my_img64 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/64.jpg"))
        self.my_img65 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/65.jpg"))
        self.my_img66 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/66.jpg"))
        self.my_img67 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/67.jpg"))
        self.my_img68 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/68.jpg"))
        self.my_img69 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/69.jpg"))
        self.my_img70 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/70.jpg"))
        self.my_img71 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/71.jpg"))
        self.my_img72 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/72.jpg"))
        self.my_img73 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/73.jpg"))
        self.my_img74 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/74.jpg"))
        self.my_img75 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/75.jpg"))
        self.my_img76 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/76.jpg"))
        self.my_img77 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/77.jpg"))
        self.my_img78 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/78.jpg"))
        self.my_img79 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/79.jpg"))
        self.my_img80 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/80.jpg"))
        self.my_img81 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/81.jpg"))
        self.my_img82 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/82.jpg"))
        self.my_img83 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/83.jpg"))
        self.my_img84 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/84.jpg"))
        self.my_img85 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/85.jpg"))
        self.my_img86 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/86.jpg"))
        self.my_img87 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/87.jpg"))
        self.my_img88 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/88.jpg"))
        self.my_img89 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/89.jpg"))
        self.my_img90 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/90.jpg"))
        self.my_img91 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/91.jpg"))
        self.my_img92 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/92.jpg"))
        self.my_img93 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/93.jpg"))
        self.my_img94 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/94.jpg"))
        self.my_img95 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/95.jpg"))
        self.my_img96 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/96.jpg"))
        self.my_img97 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/97.jpg"))
        self.my_img98 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/98.jpg"))
        self.my_img99 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/99.jpg"))
        self.my_img100 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/100.jpg"))
        self.my_img101 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/101.jpg"))
        self.my_img102 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/102.jpg"))
        self.my_img103 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/103.jpg"))
        self.my_img104 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/104.jpg"))
        self.my_img105 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/105.jpg"))
        self.my_img106 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/106.jpg"))
        self.my_img107 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/107.jpg"))
        self.my_img108 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/108.jpg"))
        self.my_img109 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/109.jpg"))
        self.my_img110 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/110.jpg"))
        self.my_img111 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/111.jpg"))
        self.my_img112 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/112.jpg"))
        self.my_img113 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/113.jpg"))
        self.my_img114 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/114.jpg"))
        self.my_img115 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/115.jpg"))
        self.my_img116 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/116.jpg"))
        self.my_img117 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/117.jpg"))
        self.my_img118 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/118.jpg"))
        self.my_img119 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/119.jpg"))
        self.my_img120 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/120.jpg"))
        self.my_img121 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/121.jpg"))
        self.my_img122 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/122.jpg"))
        self.my_img123 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/123.jpg"))
        self.my_img124 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/124.jpg"))
        self.my_img125 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/125.jpg"))
        self.my_img126 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/126.jpg"))
        self.my_img127 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/127.jpg"))
        self.my_img128 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/128.jpg"))
        self.my_img129 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/129.jpg"))
        self.my_img130 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/130.jpg"))
        self.my_img131 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/131.jpg"))
        self.my_img132 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/132.jpg"))
        self.my_img133 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/133.jpg"))
        self.my_img134 = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/134.jpg"))

        self.image_list = [self.my_img1, self.my_img2, self.my_img3, self.my_img4, self.my_img5, self.my_img6,
                           self.my_img7, self.my_img8, self.my_img9, self.my_img10, self.my_img11, self.my_img12,
                           self.my_img13,
                           self.my_img14,
                           self.my_img15,
                           self.my_img16,
                           self.my_img17,
                           self.my_img18,
                           self.my_img19,
                           self.my_img20,
                           self.my_img21,
                           self.my_img22,
                           self.my_img23,
                           self.my_img24,
                           self.my_img25,
                           self.my_img26,
                           self.my_img27,
                           self.my_img28,
                           self.my_img29,
                           self.my_img30,
                           self.my_img31,
                           self.my_img32,
                           self.my_img33,
                           self.my_img34,
                           self.my_img35,
                           self.my_img36,
                           self.my_img37,
                           self.my_img38,
                           self.my_img39,
                           self.my_img40,
                           self.my_img41,
                           self.my_img42,
                           self.my_img43,
                           self.my_img44,
                           self.my_img45,
                           self.my_img46,
                           self.my_img47,
                           self.my_img48,
                           self.my_img49,
                           self.my_img50,
                           self.my_img51,
                           self.my_img52,
                           self.my_img53,
                           self.my_img54,
                           self.my_img55,
                           self.my_img56,
                           self.my_img57,
                           self.my_img58,
                           self.my_img59,
                           self.my_img60,
                           self.my_img61,
                           self.my_img62,
                           self.my_img63,
                           self.my_img64,
                           self.my_img65,
                           self.my_img66,
                           self.my_img67,
                           self.my_img68,
                           self.my_img69,
                           self.my_img70,
                           self.my_img71,
                           self.my_img72,
                           self.my_img73,
                           self.my_img74,
                           self.my_img75,
                           self.my_img76,
                           self.my_img77,
                           self.my_img78,
                           self.my_img79,
                           self.my_img80,
                           self.my_img81,
                           self.my_img82,
                           self.my_img83,
                           self.my_img84,
                           self.my_img85,
                           self.my_img86,
                           self.my_img87,
                           self.my_img88,
                           self.my_img89,
                           self.my_img90,
                           self.my_img91,
                           self.my_img92,
                           self.my_img93,
                           self.my_img94,
                           self.my_img95,
                           self.my_img96,
                           self.my_img97,
                           self.my_img98,
                           self.my_img99,
                           self.my_img100,
                           self.my_img101,
                           self.my_img102,
                           self.my_img103,
                           self.my_img104,
                           self.my_img105,
                           self.my_img106,
                           self.my_img107,
                           self.my_img108,
                           self.my_img109,
                           self.my_img110,
                           self.my_img111,
                           self.my_img112,
                           self.my_img113,
                           self.my_img114,
                           self.my_img115,
                           self.my_img116,
                           self.my_img117,
                           self.my_img118,
                           self.my_img119,
                           self.my_img120,
                           self.my_img121,
                           self.my_img122,
                           self.my_img123,
                           self.my_img124,
                           self.my_img125,
                           self.my_img126,
                           self.my_img127,
                           self.my_img128,
                           self.my_img129,
                           self.my_img130,
                           self.my_img131,
                           self.my_img132,
                           self.my_img133,
                           self.my_img134
                           ]

        self.my_label = Label(image=self.my_img1)
        self.my_label.config(borderwidth=0, highlightthickness=0)
        self.my_label.pack()

        self.counter = 0
        self.after(10000, lambda: self.forward_time())  # after 1000ms

    def forward_time(self):
        self.my_label.pack_forget()
        self.my_label = Label(image=self.image_list[self.counter])
        self.my_label.config(borderwidth=0, highlightthickness=0)

        self.counter += 1
        if self.counter == len(self.image_list):
            self.counter = 0

        self.my_label.pack()

        self.after(10000, lambda: self.forward_time())  # after 1000ms

class LockImage(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.lockimg = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/SmartMirror/Smart-Mirror-master/images/lockimage.jpg"))


        self.locklabel = Label(image=self.lockimg)
        self.locklabel.config(borderwidth=0, highlightthickness=0)
        self.locklabel.pack(side=BOTTOM, anchor=E, padx=0, pady=0)

class FullscreenWindow:

    def __init__(self):
        self.tk = Tk()
        self.tk.attributes('-fullscreen', True)
        self.tk.configure(background='black')
        self.leftFrame1 = Frame(self.tk, background='black')
        self.rightFrame = Frame(self.tk, background='black')
        self.leftFrame1.pack(side=LEFT, fill=BOTH, expand=YES)
        self.rightFrame.pack(side=TOP, fill=BOTH, expand=YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        # images
        self.lockimage = LockImage(self.rightFrame)
        self.lockimage.pack(side=BOTTOM, anchor=N, padx=0, pady=0)
        self.images = Images(self.rightFrame)
        self.images.pack(side=BOTTOM, anchor=S, padx=0, pady=0)
        # clock
        self.clock = Clock(self.leftFrame1)
        self.clock.pack(side=TOP, anchor=N, padx=30, pady=10)
        # weather
        self.weather = Weather(self.leftFrame1)
        self.weather.pack(side=BOTTOM, anchor=S, padx=30, pady=20)

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"


if __name__ == '__main__':
    w = FullscreenWindow()
    w.tk.mainloop()
