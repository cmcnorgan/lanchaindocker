from bs4 import BeautifulSoup as bs
import requests
import re
import streamlit as st

def scrape_linkedin(url):
    plaintext=""
    #map the url to the format:
    #https://www.linkedin.com/jobs/view/JOBID
    #where JOBID is 10-digits
    baseurl="https://www.linkedin.com/jobs/view/"
    jobid_match=re.search(r'\d+', url)
    jobid=jobid_match.group()
    URL=baseurl + jobid

    #the info we need is in div with class show-more-less-html__markup--clamp-after-5
    div_class="show-more-less-html__markup--clamp-after-5"
    page=requests.get(URL)
    soup = bs(page.content, "html.parser")
    jobdiv=soup.find("div", class_=div_class)
    plaintext=jobdiv.get_text(separator=' ')
    return plaintext
    