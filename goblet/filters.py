from flask import current_app as app, url_for
from jinja2 import Markup, escape, Undefined
import hashlib
from goblet.memoize import memoize
import stat
import time
import chardet

filters = {}
def filter(name_or_func):
    if callable(name_or_func):
        filters[name_or_func.__name__] = name_or_func
        return name_or_func
    def decorator(func):
        filters[name_or_func] = func
        return func
    return decorator

@filter('gravatar')
@memoize
def gravatar(email, size=21):
    return 'http://www.gravatar.com/avatar/%s?s=%d&d=mm' % (hashlib.md5(email).hexdigest(), size)

@filter
def humantime(ctime):
    timediff = time.time() - ctime
    if timediff < 0:
        return 'in the future'
    if timediff < 60:
        return 'just now'
    if timediff < 120:
        return 'a minute ago'
    if timediff < 3600:
        return "%d minutes ago" % (timediff / 60)
    if timediff < 7200:
        return "an hour ago"
    if timediff < 86400:
        return "%d hours ago" % (timediff / 3600)
    if timediff < 172800:
        return "a day ago"
    if timediff < 2592000:
        return "%d days ago" % (timediff / 86400)
    if timediff < 5184000:
        return "a month ago"
    if timediff < 31104000:
        return "%d months ago" % (timediff / 2592000)
    if timediff < 62208000:
        return "a year ago"
    return "%d years ago" % (timediff / 31104000)

@filter
def shortmsg(message):
    message += "\n"
    short, long = message.split('\n', 1)
    if len(short) > 80:
        short = escape(short[:short.rfind(' ',0,80)]) + Markup('&hellip;')
    return short

@filter
def longmsg(message):
    message += "\n"
    short, long = message.split('\n', 1)
    if len(short) > 80:
        long = message
    long = long.strip()
    if not long:
        return ""
    return Markup('<pre class="invisible">%s</pre>') % escape(long)

@filter
def strftime(timestamp, format):
    return time.strftime(format, time.gmtime(timestamp))

@filter
def decode(data):
    encoding = chardet.detect(data)['encoding'] or 'utf-8'
    return data.decode(encoding)

@filter
def ornull(data):
    if hasattr(data, '__iter__'):
        for d in data:
            if not isinstance(d, Undefined):
                data = d
                break
        else:
            return 'null'
    if isinstance(data, Undefined):
        return 'null'
    for attr in ('name', 'hex'):
        data = getattr(data, attr, data)
    return Markup('"%s"') % data

def register_filters(app):
    app.jinja_env.filters.update(filters)