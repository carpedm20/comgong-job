from sqlalchemy import Column, Integer, String, Text

from database import Base

class Company(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    cid = Column(String(50), primary_key=True)
    name = Column(String(50), unique=True)
    url = Column(String(120), unique=True)

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __repr__(self):
        return '<Company %s: %s>' % (self.name, self.url)

class Recruit(object):
    __tablename__ = 'recruit'
    id = Column(Integer, primary_key=True)
    company = Column(String(50), primary_key=True)
    job = Column(String(50), primary_key=True)
    content = Column(Text, unique=True)

    def __init__(self, company, job, content):
        self.company = company
        self.job = job
        self.content = content

    @property
    def url(self):
        return self.id

    def __repr__(self):
        return '<Recruit %s (%s): %s>' % (self.company.name, self.job, self.url)
