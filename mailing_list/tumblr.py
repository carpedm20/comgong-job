import urllib, urllib2

TUMBLR = "https://www.tumblr.com/login"

src = 'fullscreen_post_image" src="'
bg = []
for i in range(100):
  r=urllib2.urlopen(TUMBLR)
  t=r.read()

  tt=t[t.find(src)+len(src):]
  ttt=tt[:tt.find('"')]

  bg.append(ttt)
  print ttt

bg = list(set(bg))
print str(bg)
