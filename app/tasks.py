import requests
from bs4 import BeautifulSoup

BASE = "http://rocketpun.ch/"
get_soup = lambda url: BeautifulSoup(requests.get(url).text)

def main_task():
    for recruit in get_list():
        pass

def get_list():
    url = BASE + "recruit/list/"
    soup = get_soup(url)

    job_elems = soup.select(".hr_list .hr_text_job")
    company_elems = soup.select(".hr_list .hr_text_company")
    content_elems = soup.select(".hr_list .hr_text_2")
    href_elems = soup.select(".hr_list .hr_hover_bg a")

    zipped = zip(job_elems, company_elems, content_elems, href_elems)

    for (job, company, content, a_link) in zipped:
        yield [job.text,
               company.text,
               content.text,
               a_link['href'].split('/')[-2]]
