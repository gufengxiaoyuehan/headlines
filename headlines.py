#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from flask import make_response
from flask import Flask
from flask import render_template
from flask import request
import feedparser
import json
import sys

if sys.version[0] == "2":
    from urllib import quote
    from urllib2 import urlopen 
else:
    from urllib.parse import quote 
    from urllib.request import urlopen
    

RSS_FEEDS = {'bbc':'http://feeds.bbci.co.uk/news/rss.xml',
         'cnn':'http://rss.cnn.com/rss/edition.rss',
         'fox':'http://feeds.foxnews.com/foxnews/latest',
         'iol':'http://www.iol.co.za/cmlink/1.640'
        }
DEFAULTS = {
    "publication":"bbc",
    "city":"London",
    "currency_from":"GBP",
    "currency_to":"USD"
}
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=004796af1ecd4045a0ae22dd05923b37"
CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=ae1310e25fc749b5a74cf7b46a42b008"
app = Flask(__name__)

def get_weather(query):
    query = quote(query) # quote to encode reserved characters
    url = WEATHER_URL.format(query)
    data = urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"],
                    "temperature":parsed["main"]["temp"],
                    "city":parsed["name"],
                    "country":parsed["sys"]["country"]
        }
        return weather

def get_rates(frm,to):
    all_currency = urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get("rates")
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/frm_rate, parsed.keys())
    
def get_news(query):
    feed = feedparser.parse(RSS_FEEDS[query])
    return feed["entries"]
        
@app.route("/", methods=['GET',"POST"])
def home():
    # get customized headlines based on user input or default.
    publication = get_value_with_fallback("publication")
 
    articles = get_news(publication.lower())
 
    # get customized weather based on user input or default
    city = get_value_with_fallback("city")
    
    weather = get_weather(city)
    
    # get customized currency based on user input or default 
    currency_from = get_value_with_fallback("currency_from")
    currency_to = get_value_with_fallback("currency_to")
    
    rate,currencies = get_rates(currency_from,currency_to)
    
    response = make_response(render_template("home.html", articles=articles
            ,domain=publication, weather= weather,currency_from = 
            currency_from, currency_to=currency_to, rate=rate,
            currencies =sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication",publication,expires=expires)
    response.set_cookie("city",city,expires=expires)
    response.set_cookie("currency_from",currency_from,expires=expires)
    response.set_cookie("currency_to",currency_to,expires=expires)
    return response
   
def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
