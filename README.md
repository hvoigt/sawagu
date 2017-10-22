# Sawagu: post RSS headlines and links to Twitter

Because I wanted to automatically tweet links to my blog using my personalized
URL shortener (rather than whatever Feedburner sticks me with).

The word "[sawagu][defn]" is Japanese for "to make noise; to make racket; to be noisy"
or "to make a fuss", which seems about right for this purpose.

[defn]: http://www.romajidesu.com/dictionary/meaning-of-さわぐ.html

## Usage

Run with

    python sawagu/__init__.py

and it will post to twitter.

Create `.sawagu` file in your home directory with the following content
(see config [documentation][1] for further syntax information):

```
#CACHE_FILE = ~/.sawagu-cache.xml
FEED_URL = http://your.url.com?feed.rss
TWITTER_CONSUMER_KEY = XXXXXXXXXXXXXXXXXXXXXXXXX
TWITTER_CONSUMER_SECRET = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWITTER_ACCESS_TOKEN = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWITTER_ACCESS_TOKEN_SECRET = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

To get the twitter API keys you need to do the following:

1. Create/Have a twitter account
2. Use https://apps.twitter.com
3. Create New App
4. Fill in the details into the form and "Create your Twitter application"
5. Copy your `API key` and `API secrect` from the `API keys` tab
6. "Create my access token" further down on the page and copy `Access
token` and `Access token secret`.

[1]: http://www.voidspace.org.uk/python/configobj.html#config-files

## Usage in a cronjob

To use sawagu in a cronjob you can add the following line to your crontab:

```
0 * * * * python /path/to/sawagu/sawagu/__init__.py
```

which will search for new posts every hour.
