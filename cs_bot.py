# -*- coding:utf-8 -*-
import mechanize
import spynner
import facebook
import base64
import os
import time
import math
from PIL import Image
import smtplib
import atexit
import subprocess
from xvfbwrapper import Xvfb
from email.MIMEImage import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.MIMEText import MIMEText
from cs_config import *
import socket
import urllib2
from bs4 import BeautifulSoup
from urllib2 import urlopen
import csv

import simplejson as json
from selenium import webdriver

def send_mail(text, filename=''):
  global email_username, email_password

  fromaddr = 'hexa.portal@gmail.com'
  recipients = ['carpedm20@gmail.com']
  toaddrs  = ", ".join(recipients)

  username = email_username
  password = email_password

  msg = MIMEMultipart()
  msg['From'] = fromaddr
  msg['To'] = toaddrs
  msg['Subject'] = text

  part = MIMEText('text', "plain")
  part.set_payload(text)
  msg.attach(part)

  if filename is not '':
    img = MIMEImage(open(filename,"rb").read(), _subtype="png")
    img.add_header('Content-Disposition', 'attachment; filename="'+filename+'"')
    msg.attach(img)

  server = smtplib.SMTP('smtp.gmail.com:587')
  server.starttls()
  server.login(username,password)
  server.sendmail(fromaddr, recipients, msg.as_string())
  server.quit()
  print " - mail sended"


def long_slice(image_path, out_name, outdir, number):
  img = Image.open(image_path)
  width, height = img.size

  slice_size = height/number
  upper = 0
  left = 0
  slices = int(math.ceil(height/slice_size))

  count = 1
  for slice in range(slices):
    if count == slices:
      lower = height
    else:
      lower = int(count * slice_size)
    bbox = (left, upper-30, width, lower+30)
    working_slice = img.crop(bbox)
    upper += slice_size
    working_slice.save(os.path.join(outdir, out_name + "_" + str(count)+".png"))
    count +=1

def width_slice(image_path, out_name, outdir, number):
  img = Image.open(image_path)
  width, height = img.size

  slice_size = width/number
  upper = 0
  left = 0
  slices = int(math.ceil(width/slice_size))

  count = 1
  for slice in range(slices):
    if count == slices:
      right = width
    else:
      right = int(count * slice_size)
    bbox = (left-50, 0, right+50, height)
    working_slice = img.crop(bbox)
    left += slice_size
    working_slice.save(os.path.join(outdir, out_name + "_" + str(count)+".png"))
    count +=1

from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 600))
display.start()

job_url = {}
kaist = {}
career_kaist = {}
snu = {}
postech = {}

kaist['list'] = 'http://cs.kaist.ac.kr/csbb/jboard.cs?tbl=recruit&page='
kaist['base'] = 'http://cs.kaist.ac.kr/csbb/'
# http://cs.kaist.ac.kr/csbb/view.cs?no=1216&tbl=recruit&page=1

# POST http://career.kaist.ac.kr/sub0101/recrute/index
# search=Y&division=&region=&occupational=IT%2C%EC%A0%95%EB%B3%B4%ED%86%B5%EC%8B%A0%2C%EC%A0%84%EC%82%B0&keyword=&x=44&y=11
career_kaist['list'] = 'http://career.kaist.ac.kr/sub0101/recrute/index'
career_kaist['base'] = 'http://career.kaist.ac.kr/'
# http://career.kaist.ac.kr/sub0101/recrute/view/id/669

#snu['list'] = 'http://cse.snu.ac.kr/department-notices?c[0]=40&c[1]=2&keys=&page='
#snu['base'] = 'http://cse.snu.ac.kr/'
# http://cse.snu.ac.kr/node/9606

postech['list'] = 'http://phome.postech.ac.kr/user/indexSub.action?codyMenuSeq=18726&siteId=cse&menuUIType=sub&dum=dum&boardId=11622&page='
postech['base'] = 'http://phome.postech.ac.kr/user/'
# http://phome.postech.ac.kr/user/boardList.action?command=view&page=1&boardId=11622&boardSeq=287839

job_url['kaist'] = kaist
job_url['career_kaist'] = career_kaist
#job_url['snu'] = snu
job_url['postech'] = postech

schools = job_url.keys()
ci_session = ''

from selenium import webdriver
import requests

def get_career_session():
  global ci_session

  data = {"type" : "company",
          "userid" : cs_id,
          "passwd" : cs_passwd }

  r = requests.session()
  career_login_url = "http://career.kaist.ac.kr/member/authority/choice_login"

  r.post(career_login_url,data = data)

  ci_session = r.cookies['ci_session']

def exit_handler():
  global display
  display.stop()
  
atexit.register(exit_handler)

while 1:
  print '.'
  #br_mech = mechanize.Browser()
  #br_mech.set_handle_robots(False)
  br_spy = spynner.Browser()
  br_spy.set_cookies('career.kaist.ac.kr\tTRUE\t/\tFALSE\t9294967295\tci_session\t'+ci_session)

  get_career_session()

  for school in schools:
  #for school in ['postech']:
    print "[#] " + school.upper()

    if school == 'career_kaist':
      response = urllib2.urlopen("http://career.kaist.ac.kr/sub0101/recrute/index","search=Y&division=&region=&occupational=IT%2C%EC%A0%95%EB%B3%B4%ED%86%B5%EC%8B%A0%2C%EC%A0%84%EC%82%B0&keyword=&x=44&y=11")
    else:
      response = urllib2.urlopen(job_url[school]['list'])

    r = response.read()
    soup = BeautifulSoup(r)

    if school == 'kaist':
      tds = soup.find_all('td','aL')
    elif school == 'career_kaist':
      tds = soup.find_all('td','title')
    elif school == 'snu':
      tds = soup.find_all('td','views-field views-field-title')
    elif school == 'postech':
      tds = soup.find_all('td','title')

    boards = [ job_url[school]['base'] + td.find('a')['href'] for td in tds ]

    for b_index, b in enumerate(boards):
      print" [*] link : " + b

      if school == 'kaist':
        no = b[b.find('no=') + 3:]
        no = no[:no.find('&')]
      elif school == 'career_kaist':
        no = b[b.find('/id/')+4:]
      elif school == 'snu':
        no = b[b.find('node/') + 5:]
      elif school == 'postech':
        no = b[b.find('boardSeq=') + 9:]
        no = no[:no.find('&')]

      file_name = school + '_' + no + '.png'
      files = [f for f in os.listdir('.') if os.path.isfile(f)]
      new = True

      for f in files:
        if f.find(file_name) is not -1:
          new = False
          break

      if new:
        if school == 'career_kaist':
          br_spy= spynner.Browser()
          br_spy.set_cookies('career.kaist.ac.kr\tTRUE\t/\tFALSE\t4294967295\tci_session\t'+ci_session)
          br_spy.load(b)
          br_spy.snapshot().save(file_name)
          print "FILE SAVE SUCCESS : " + file_name

        else:
          browser = webdriver.Firefox()
          browser.get(b)
          browser.save_screenshot(file_name)

        if school == 'career_kaist':
          print "FILE LOAD AGAIN : " + file_name
          img = Image.open(file_name)
          width, height = img.size
          #bbox = (0, 110, width, height-249)
          bbox = (150, 160, width, height-189)
          working_slice = img.crop(bbox)
          working_slice.save(file_name)
          #sys.exit(1)
        if school == 'snu':
          img = Image.open(file_name)
          width, height = img.size
          bbox = (0, 185, width-240, height-269)
          working_slice = img.crop(bbox)
          working_slice.save(file_name)
        if school == 'postech':
          img = Image.open(file_name)
          width, height = img.size
          bbox = (0, 22, width, height-135)
          #bbox = (200, 285, width-350, height-169)
          working_slice = img.crop(bbox)
          working_slice.save(file_name)

        print" [*] Image : " +  file_name

        if school == 'career_kaist':
          html = br_spy.html
        else:
          html = browser.page_source

        try:
          browser.close()
        except:
          z=123
        soup = BeautifulSoup(html)

        #title = soup.find('th').text

        title = tds[b_index].text
        title = title.strip().encode('utf-8')

        print"  [=] Title : " +  file_name

        img=Image.open(file_name)
        width, height = img.size

        slice_num=1
        sliced=False

        if height > 1000:
          slice_num=2
          sliced=True
        if height > 2000:
          slice_num=3
          sliced=True
        if height > 2800:
          slice_num=4
          sliced=True
        if height > 3600:
          slice_num=5
          sliced=True

        facebook_app_link='https://www.facebook.com/dialog/oauth?scope=manage_pages,publish_stream&redirect_uri=http://carpedm20.blogspot.kr&response_type=token&client_id=641444019231608'

        br_mech = mechanize.Browser()
        br_mech.set_handle_robots(False)

        br_mech.open(facebook_app_link)

        br_mech.form = list(br_mech.forms())[0]
        control = br_mech.form.find_control("email")
        control.value=fb_email
        control = br_mech.form.find_control("pass")
        control.value=fb_pass

        br_mech.submit()

        page_id = '512098305554140' # https://www.facebook.com/cumgong.job
        account_app_access = br_mech.geturl().split('token=')[1].split('&expires')[0]
        page_app_access_url = "https://graph.facebook.com/me/accounts?access_token=" + account_app_access
        j = urllib2.urlopen(page_app_access_url)
        j = json.loads(j.read())

        for d in j['data']:
          if d['id'] == '512098305554140':
            app_access = d['access_token']
            break

        graph = facebook.GraphAPI(app_access)
        # graph.put_photo(open('kaist_1211.png'),message="test",album_id="512098305554140")

        print "  [=] upload : " + file_name

        content = "[ " + school.upper() + " ]" + "\r\n\r\n" + title + "\r\n\r\n링크 : " + b
        print "   [$] content : " + content

        tail = '\r\n\r\n제작자 : 김태훈(carpedm20)'
        tail = ''

        if sliced is True:
          long_slice(file_name, file_name[:-4], os.getcwd(), slice_num)

          for nums in range(1, slice_num+1):
             nums=slice_num-nums+1

             graph.put_photo( open(file_name[:-4] + '_' + str(nums) + '.png'), content + ' ['+str(nums)+'/'+str(slice_num)+']' + tail, "")

        else:
          graph.put_photo( open(file_name), content + tail, "")
          send_mail(title, file_name)

  time.sleep(10)
