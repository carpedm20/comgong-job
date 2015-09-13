import requests
from bs4 import BeautifulSoup

BASE = "http://rocketpun.ch/"
get_soup = lambda url: BeautifulSoup(requests.get(url, verify=False).text)

def main_task(Recruit, db_session):
    for recruit in get_list():
        instance = Recruit.query.filter_by(id=recruit[3]).first()
        if instance:
            print "[@] %s already exists" % instance
            pass
        else:
            recruit = Recruit(recruit[0],
                              recruit[1],
                              recruit[2],
                              recruit[3])

            db_session.add(recruit)
            db_session.commit()

def get_list():
    url = BASE + "recruit/list/"
    soup = get_soup(url)

    job_elems = soup.select(".hr_list .hr_text_job")
    company_elems = soup.select(".hr_list .hr_text_company")
    content_elems = soup.select(".hr_list .hr_text_2")
    href_elems = soup.select(".hr_list .hr_hover_bg a")

    zipped = zip(job_elems, company_elems, content_elems, href_elems)

    zipped.reverse()

    for (job, company, content, a_link) in zipped:
        job_soup = get_soup(BASE + a_link['href'])
        quote = job_soup.select("blockquote div")[0]
        job_content = quote.decode_contents(formatter="html").replace("<br/>","\r\n")

        yield [job.text,
               company.text,
               job_content,
               int(a_link['href'].split('/')[-2])]
