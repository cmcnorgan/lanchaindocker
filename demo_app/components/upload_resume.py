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
import chromadb
import hashlib
import pathlib
import re
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings

def extract_emails(text):
    import re
    emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text)
    return emails

def _upload_resume():
    uploaded_resume = st.file_uploader("Upload a Resume file (PDF or DOCX).", 
                                   type=['pdf', 'docx'])

    
    full_resume_text=""

    if uploaded_resume is None:
        pass
    else:
        full_resume_text = extract_text(uploaded_resume)
        emails=extract_emails(full_resume_text)
        email=emails[0].lower()
        st.sidebar.header(email)
        seconds=str(time.time())
        #actually, we will want the hash to use a timestamp so that 
        #bad actors can't replace a parsed resume just by knowing your email address
        _dir=hashlib.sha256(seconds.encode('utf-8')).hexdigest()[:8]
        _dir=str(_dir).upper()
        basedir='chromadb/'
        persistdirectory=basedir+_dir
        st.sidebar.subheader("Your resume ID is " + _dir)

        rdocsearch, sections = _extract_sections(full_resume_text, str(persistdirectory))
        embeddings=OpenAIEmbeddings()
        vectordb = Chroma(persist_directory=persistdirectory, embedding_function=embeddings)
        retriever = vectordb.as_retriever()
        qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=retriever)

        st.write("Your resume has been uploaded and parsed.")
        st.write("Make note of your resume ID. You will need to include it to allow others to chat with your parsed resume.")