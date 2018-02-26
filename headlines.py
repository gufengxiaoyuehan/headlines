#!/usr/bin/env python

from flask import Flask
from flask import render_template
from flask import request
import feedparser

RSS_FEEDS = {'bbc':'http://feeds.bbci.co.uk/news/rss.xml',
         'cnn':'http://rss.cnn.com/rss/edition.rss',
         'fox':'http://feeds.foxnews.com/foxnews/latest',
         'iol':'http://www.iol.co.za/cmlink/1.640'
        }
app = Flask(__name__)

@app.route("/")
def get_news():
    query = request.args.get("publication")
    if not query or query.lower() not in RSS_FEEDS:
        publication = "bbc"
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    first_article = feed["entries"][0]
    return render_template("home.html", articles=feed["entries"]
            ,domain=publication)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
