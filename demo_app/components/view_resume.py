import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_chat import message
import io
from io import StringIO
import os
import glob
import time
from components.generate_response import generate_response
from components.extract_text import extract_text
from components.extract_sections import _extract_sections
from components._scrape_linkedin import scrape_linkedin
import chromadb
import hashlib
import pathlib
import re

def _scrape_ad(url):
    full_ad_text=""
    #LinkedIn ad as https://www.linkedin.com/jobs/search/?currentJobId=3661112522
    
    if url is None or url == '':
        uploaded_ad = st.file_uploader("No URL provided. Upload a text description of the role (PDF or DOCX).", 
                                   type=['pdf', 'docx'])
        if uploaded_ad is None:
            pass
        else:
            full_ad_text = extract_text(uploaded_ad)

    else:
        st.write("A url was provided. We'll try our best to extract the job description from it. Currently only linkedin job board posts are officially supported")
        if "linkedin.com" in url.lower():
            jobid_match=re.search(r'\d+', url)
            jobid=jobid_match.group()
            baseurl="https://www.linkedin.com/jobs/view/"
            URL=baseurl+jobid
            full_ad_text=scrape_linkedin(url)
    return full_ad_text