import re
import os
import time
from glob import glob
import facebook


from tasks import *

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, Integer, String, Text, Boolean

import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

engine = create_engine('sqlite:///cs.db', echo=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    cid = Column(String(50), primary_key=True)
    name = Column(String(50), unique=True)
    url = Column(String(120), unique=True)

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __repr__(self):
        msg = '<Company %s: %s>' % (self.name, self.url)
        return msg.encode('utf8')

class Recruit(Base):
    __tablename__ = 'recruit'
    id = Column(Integer, primary_key=True)
    company = Column(String(50))
    job = Column(String(50))
    content = Column(Text)
    published = Column(Boolean, default=False)

    def __init__(self, job, company, content, id):
        self.job = job
        self.company = company
        self.content = content
        self.id = id

    @property
    def url(self):
        return "http://rocketpun.ch/recruit/" + str(self.id)

    def __repr__(self):
        msg = '<Recruit %s<%s> (%s): %s>' % (self.company, self.id, self.job, self.url)
        return msg.encode('utf8')

Base.metadata.create_all(bind=engine)

import redis
import json
import mechanize
import urllib2

def get_acces_token():
    r_server = redis.Redis('localhost')
    email = r_server.get('fb_email')
    password = r_server.get('fb_pass')

    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7')]
    cookies = mechanize.CookieJar()

    browser.open('https://www.facebook.com/dialog/oauth?scope=manage_pages,publish_actions&redirect_uri=https://carpedm20.github.io/&response_type=token&client_id=641444019231608')

    browser.select_form(nr=0)
    browser.form['email'] = email
    browser.form['pass'] = password
    response = browser.submit()

    url = response.geturl()
    account_app_access = url[url.find("access_token=")+len("access_token="):url.find('&expi')]

    page_id = '512098305554140'
    page_app_access_url = "https://graph.facebook.com/me/accounts?access_token=" + account_app_access
    print page_app_access_url
    j = urllib2.urlopen(page_app_access_url)
    j = json.loads(j.read())

    for d in j['data']:
        if d['id'] == '512098305554140':
            app_access = d['access_token']
            return app_access

if __name__ == '__main__':
    while True:

        main_task(Recruit, db_session)

        recruits = Recruit.query.filter_by(published=False).all()

        if recruits:
            for r in recruits:
                msg = "[" + r.company + "] " + r.job + "\r\n\r\n" + r.content;

                token = get_acces_token()
                graph = facebook.GraphAPI(access_token=token)
                graph.put_object("me", "feed",
                    message = msg.encode('utf-8'),
                    link = r.url,
                )

                r.published = True
                db_session.commit()

                print " [*] Publish %s <%s>" % (r, token.encode('utf-8'))
                time.sleep(3600)
                pass
        else:
            print " [!] Nothing to publish"

        time.sleep(3600)
