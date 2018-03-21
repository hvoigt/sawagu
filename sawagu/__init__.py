# -*- coding: utf-8 -*-
# vim: set sw=4, ts=4, et
import os
import datetime
import feedparser
import requests
import tweepy
import tempfile
from configobj import ConfigObj
from bs4 import BeautifulSoup as BS


def main():
    cache = Cache(Settings.CACHE_FILE)
    shortener = Shortener(Settings.SHORTENER_URL)
    tweeter = Tweeter(Settings.TWITTER_CONSUMER_KEY,
            Settings.TWITTER_CONSUMER_SECRET,
            Settings.TWITTER_ACCESS_TOKEN,
            Settings.TWITTER_ACCESS_TOKEN_SECRET)

    response = requests.get(Settings.FEED_URL)
    new_data = response.content.decode('utf-8', errors='replace');
    new_feed = feedparser.parse(new_data)

    last_data = cache.load().decode('utf-8', errors='replace');
    last_feed = feedparser.parse(last_data)

    now = datetime.datetime.now()
    new_entries = [x for x in new_feed.entries
            if x.id not in [y.id for y in last_feed.entries]
            and (now - struct_time_to_datetime(x.published_parsed)).days
                    <= Settings.MAX_AGE_DAYS]

    if len(new_entries) != 0:
        print "Got new entries:", len(new_entries)

    # tweet the oldest entries first
    new_entries.reverse()
    for entry in new_entries:
        message = Message(
                title=entry.title,
                link=shortener.shorten(entry.link),
                tags=[x.term for x in entry.tags],
                image=image_from_html(entry.summary))
        tweeter.send_tweet(message)

    cache.save(new_data.encode('utf-8'))


def struct_time_to_datetime(t):
    return datetime.datetime(*t[:5] + (min(t[5], 59),))

def image_from_html(html):
    image = ''
    soup = BS(html)
    for imgtag in soup.find_all('img'):
        image = imgtag['src']
        break;

    return image

class Shortener(object):

    def __init__(self, shortener_url):
        self.shortener_url = shortener_url

    def shorten(self, url):
        if not self.shortener_url:
            return url

        data = {'url': url}
        response = requests.post(self.shortener_url, data=data)
        short_url = response.content.strip()
        return short_url


class Message(object):

    def __init__(self, title='', link='', tags=(), image=''):
        self.title = title
        self.link = link
        self.tags = tags
        self.imageurl = image
        self.local_imagefile = ''

    def __del__(self):
        if self.local_imagefile:
            os.remove(self.local_imagefile)

    def __unicode__(self):
        message = self.link
        if not Settings.SHORTENER_URL:
            # if not using a configured shortener: links are automatically
            # shortened on twitter only use the short link in length
            # calculations
            calc_message = u'https://t.co/XXXXXXXXXX'
        else:
            calc_message = message

        if len(self.title + calc_message) + 1 > 140:
            title = self.truncate(self.title, u' ' + calc_message)
            message = title + u' ' + message
            calc_message = title + u' ' + calc_message
        else:
            message = self.title + u' ' + message
            calc_message = self.title + u' ' + calc_message

        for tag in self.tags:
            if len(calc_message + tag) + 2 <= 140:
                message += u" #" + tag
                calc_message += u" #" + tag

        return message

    def truncate(self, to_shorten, to_keep):
        shorten_by = len(to_shorten + to_keep) - 140 + 1
        result = to_shorten[:shorten_by] + u"…"
        return result

    def download_image(self):

        if not self.imageurl:
            return ''

        tempname = next(tempfile._get_candidate_names())
        filename = "/tmp/sawagu_" + tempname + ".jpg"
        request = requests.get(self.imageurl, stream=True)
        if request.status_code == 200:
            with open(filename, 'wb') as image:
                self.local_imagefile = filename
                for chunk in request:
                    image.write(chunk)

            return filename
        else:
            print("Unable to download image")
            return ''


class Cache(object):

    def __init__(self, cache_filename):
        self.cache_filename = cache_filename

    def save(self, data):
        with open(self.cache_filename, 'w') as f:
            f.write(data)

    def load(self):
        try:
            f = open(self.cache_filename, 'r')
        except IOError, e:
            if e.errno != 2:
                raise
            return ''
        else:
            data = f.read()
            f.close()
            return data


class Tweeter(object):

    def __init__(self, consumer_key, consumer_secret,
            access_token, access_token_secret):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth)

    def send_tweet(self, message):
        print "Sending message", unicode(message).encode('utf-8')

        image = message.download_image()

        try:

            if len(image) == 0:
                self.api.update_status(message)
            else:
                self.api.update_with_media(image, status=message)

        except tweepy.TweepError, e:
            if 'duplicate' not in str(e):
                raise
            print str(e)


def _get_local_settings():
    default_location = os.environ.get('HOME', '') + "/.sawagu"
    location_from_env = os.environ.get('SAWAGU_SETTINGS')

    if location_from_env and os.path.exists(location_from_env):
        return ConfigObj(location_from_env)

    elif os.path.exists(default_location):
        return ConfigObj(default_location)

    else:
        return ConfigObj()


class Settings(object):

    __config = _get_local_settings()

    CACHE_FILE = __config.get('CACHE_FILE') or os.environ.get('HOME', '/tmp') + '/.sawagu-cache.xml'
    FEED_URL = __config.get('FEED_URL') or ''
    MAX_AGE_DAYS = __config.get('MAX_AGE_DAYS') or 7
    SHORTENER_URL = __config.get('SHORTENER_URL') or ''
    TWITTER_CONSUMER_KEY = __config.get('TWITTER_CONSUMER_KEY') or ''
    TWITTER_CONSUMER_SECRET = __config.get('TWITTER_CONSUMER_SECRET') or ''
    TWITTER_ACCESS_TOKEN = __config.get('TWITTER_ACCESS_TOKEN') or ''
    TWITTER_ACCESS_TOKEN_SECRET = \
            __config.get('TWITTER_ACCESS_TOKEN_SECRET') or ''


if __name__ == '__main__':
    main()
