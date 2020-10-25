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
    'clear-day': "assets/Sun.png",  # clear sky day
    'wind': "assets/Wind.png",  # wind
    'cloudy': "assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
    'rain': "assets/Rain.png",  # rain day
    'snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.png",  # sleet day
    'fog': "assets/Haze.png",  # fog day
    'clear-night': "assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "assets/Storm.png",  # thunderstorm
    'tornado': "assests/Tornado.png",  # tornado
    'hail': "assests/Hail.png"  # hail
}


class Clock(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='red')
        # initialize time label
        self.time1 = ''
        self.timeLbl = Label(self, font=('Helvetica', xlarge_text_size), fg="white", bg="green")
        self.timeLbl.pack(side=TOP, anchor=E)
        # initialize day of week
        self.day_of_week1 = ''
        # self.dayOWLbl = Label(self, text=self.day_of_week1, font=('Helvetica', small_text_size), fg="white", bg="black")
        # self.dayOWLbl.pack(side=TOP, anchor=CENTER)
        # initialize date label
        self.date1 = ''
        self.dateLbl = Label(self, text=self.day_of_week1 + ', ' + self.date1, font=('Helvetica', small_text_size),
                             fg="white", bg="blue")
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
        Frame.__init__(self, parent, bg='red')
        self.temperature = ''
        self.forecast = ''
        self.location = ''
        self.currently = ''
        self.icon = ''
        self.iconLbl = Label(self, bg="green")
        self.iconLbl.pack(side=TOP, anchor=CENTER, padx=20)
        self.degreeFrm = Frame(self, bg="blue")
        self.degreeFrm.pack(side=TOP, anchor=W)
        self.temperatureLbl = Label(self, font=('Helvetica', large_text_size), fg="white", bg="yellow")
        self.temperatureLbl.pack(side=TOP, anchor=CENTER, pady=0)
        # self.currentlyLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        # self.currentlyLbl.pack(side=TOP, anchor=CENTER)
        self.forecastLbl = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="brown")
        self.forecastLbl.pack(side=TOP, anchor=CENTER)
        self.locationLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="grey")
        self.locationLbl.pack(side=TOP, anchor=CENTER)
        self.get_weather()

    def get_ip(self):
        try:
            ip_url = "http://jsonip.com/"
            req = requests.get(ip_url)
            ip_json = json.loads(req.text)
            return ip_json['ip']
        except Exception as e:
            traceback.print_exc()
            return "Error: %s. Cannot get ip." % e

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
                "http://dataservice.accuweather.com/forecasts/v1/daily/5day/264863?apikey=iKTjxzrAqZoG3offbdoaxF2XyAhWya3Q")
            weather_obj = json.loads(r.text)

            degree_sign = u'\N{DEGREE SIGN}'
            # temperature2 = "%s%s" % (str(int(weather_obj['currently']['temperature'])), degree_sign)
            temperature2 = "%s%s" % (str(24), degree_sign)
            # currently2 = weather_obj['currently']['summary']
            currently2 = "currently2"
            # forecast2 = weather_obj["hourly"]["summary"]
            forecast2 = "Pogodnie"

            # icon_id = weather_obj['currently']['icon']
            icon_id = "icon_id"
            icon2 = None

            if icon_id in icon_lookup:
                icon2 = icon_lookup[icon_id]

            if icon2 is not None:
                if self.icon != icon2:
                    self.icon = icon2
                    image = Image.open(icon2)
                    image = image.resize((100, 100), Image.ANTIALIAS)
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
            if self.forecast != forecast2:
                self.forecast = forecast2
                self.forecastLbl.config(text=forecast2)
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

        self.after(600000, self.get_weather)

    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32


class Images(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='pink')
        self.my_img1 = ImageTk.PhotoImage(Image.open("images/1.jpg"))
        self.my_img2 = ImageTk.PhotoImage(Image.open("images/2.jpg"))
        self.my_img3 = ImageTk.PhotoImage(Image.open("images/1.jpg"))
        self.my_img4 = ImageTk.PhotoImage(Image.open("images/2.jpg"))
        self.my_img5 = ImageTk.PhotoImage(Image.open("images/1.jpg"))
        self.my_img6 = ImageTk.PhotoImage(Image.open("images/2.jpg"))
        self.my_img7 = ImageTk.PhotoImage(Image.open("images/1.jpg"))
        self.my_img8 = ImageTk.PhotoImage(Image.open("images/2.jpg"))

        self.image_list = [self.my_img1, self.my_img2, self.my_img3, self.my_img4, self.my_img5, self.my_img6,
                           self.my_img7, self.my_img8]

        self.my_label = Label(image=self.my_img1)
        self.my_label.config(borderwidth=0, highlightthickness=0)
        self.my_label.pack(side=BOTTOM, anchor=E, padx=50, pady=15)

        self.counter = 0
        self.forward_time()

    def forward_time(self):
        self.my_label.pack_forget()
        self.my_label = Label(image=self.image_list[self.counter])
        self.my_label.config(borderwidth=0, highlightthickness=0)

        self.counter += 1
        if self.counter == len(self.image_list):
            self.counter = 0

        self.my_label.pack()

        self.after(3000, lambda: self.forward_time())  # after 1000ms


class FullscreenWindow:

    def __init__(self):
        self.tk = Tk()
        self.tk.configure(background='white')
        self.leftFrame1 = Frame(self.tk, background='orange')
        self.rightFrame = Frame(self.tk, background='violet')
        self.leftFrame1.pack(side=LEFT, fill=BOTH, expand=YES)
        self.rightFrame.pack(side=TOP, fill=BOTH, expand=YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        # images
        self.images = Images(self.leftFrame1)
        self.images.pack(side=BOTTOM, anchor=S, padx=100, pady=0)
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
