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
    company = Column(String(50), primary_key=True)
    job = Column(String(50), primary_key=True)
    content = Column(Text, unique=True)
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
        msg = '<Recruit %s (%s): %s>' % (self.company, self.job, self.url)
        return msg.encode('utf8')

Base.metadata.create_all(bind=engine)

import redis
r_server = redis.Redis('localhost')
token = r_server.get('cs-long-token')

graph = facebook.GraphAPI(access_token=token)

if __name__ == '__main__':
    while True:
        main_task(Recruit, db_session)

        recruits = Recruit.query.filter_by(published=False).all()

        if recruits:
            for r in recruits:
                msg = "[" + r.company + "] " + r.job + "\r\n\r\n" + r.content;

                graph.put_object("me", "feed",
                    message = msg.encode('utf-8'),
                    link = r.url,
                )

                r.published = True
                db_session.commit()

                print " [*] Publish %s" % r
                time.sleep(60)
                pass
        else:
            print " [!] Nothing to publish"

        time.sleep(60)
