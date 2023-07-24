##imports
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
from components._extract_requirements import _extract_requirements
from components.lc_utils import _extract_sections

st.set_page_config(page_title="Resum-AI: The Virtual Hiring Manager Assistant")
sidebar = st.sidebar


with sidebar:
    st.title('📄 Interview With the Resume')
    st.markdown('''
                Pair up an applicant's resume with a job, then ask questions to quickly learn about their qualifications for the role.''')
    add_vertical_space(4)
    
uploaded_resume = st.file_uploader("Upload a Resume PDF file.")
uploaded_ad = st.file_uploader("Upload a Job Ad PDF file.")


if 'generated' not in st.session_state:
    st.session_state['generated'] = ["No, Dutchess Community College does not have a PhD program."]

if 'past' not in st.session_state:
    st.session_state['past'] = ["e.g. Did the applicant get a PhD from SUNY Poughkeepsie?"]
    
full_ad_text=""
full_resume_text=""

if uploaded_resume is None:
    if uploaded_ad is None:
        pass
elif uploaded_ad is None:
    if uploaded_resume is None:
        pass
else:
    full_resume_text = extract_text(uploaded_resume)
    full_ad_text = extract_text(uploaded_ad)


    rdocsearch, sections = _extract_sections(full_resume_text)
    
    colored_header(label='', description='', color_name='blue-30')
    response_container = st.container()
    input_container = st.container()
    state = st.session_state
    

    requirements = _extract_requirements(full_ad_text, 
                                         state,
                                         response_container,
                                         rdocsearch)
    


    input_text = st.text_input("You: ", "", key="input", placeholder="Ask a question here!")

    
    with response_container:
        if input_text:
            response = generate_response(input_text, rdocsearch)
            state.past.append(input_text)
            state.generated.append(response)
        
    if state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
            message(state["generated"][i], key=str(i), avatar_style="bottts")
