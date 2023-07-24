##imports

import streamlit as st
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import io
from io import StringIO
import os
import glob
import PyPDF2
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import time
import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from hugchat import hugchat
from langchain.chains import RetrievalQA
from streamlit_card import card



def generate_response(query, docsearch):
    
    retriever = docsearch
    qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=retriever)
 
    return qa.run(query)
  

st.set_page_config(page_title="Resume Query: Converse with an Uploaded Resume")
sidebar = st.sidebar


with sidebar:
    st.title('📄 Query a Resume')
    st.markdown('''
                After uploading a Resume, ask questions to more quickly access the information you need about the applicant.''')
    add_vertical_space(4)
    
uploaded_resume = st.file_uploader("Upload a Resume PDF file.")
uploaded_ad = st.file_uploader("Upload a Job Ad PDF file.")


if 'generated' not in st.session_state:
    st.session_state['generated'] = ["No, the applicant does not have a master's degree; they have a B.S. in Mechanical Engineering from San Jose State University."]

if 'past' not in st.session_state:
    st.session_state['past'] = ["e.g. Does the applicant have a Master's degree?"]
    
@st.cache_resource
def extract_sections(full_resume_text): 
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(full_resume_text)
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_texts(texts, embeddings, metadatas=[{"source": str(i)} for i in range(len(texts))]).as_retriever()
    query = "Return the sections of this resume as a python list."
    docs = docsearch.get_relevant_documents(query)
    
    refine_prompt_template = (
    "The original question is as follows: {question}\n"
    "We have provided an existing answer: {existing_answer}\n"
    "We have the opportunity to refine the existing answer"
    "(only if needed) with some more context below.\n"
    "------------\n"
    "{context_str}\n"
    "------------\n"
    "Given the new context, refine the original answer to better "
    "answer the question. "
    "If the context isn't useful, return the original answer."
    )
    refine_prompt = PromptTemplate(
    input_variables=["question", "existing_answer", "context_str"],
    template=refine_prompt_template,
    )
    
    initial_qa_template = (
    "Context information is below. \n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the question: {question}\n"
    )
    initial_qa_prompt = PromptTemplate(
    input_variables=["context_str", "question"], template=initial_qa_template
    )
    chain = load_qa_chain(OpenAI(temperature=0), chain_type="refine", return_refine_steps=True,
                     question_prompt=initial_qa_prompt, refine_prompt=refine_prompt)
    output = chain({"input_documents": docs, "question": query}, return_only_outputs=True)
    output_parser = CommaSeparatedListOutputParser()
    sections = (output_parser.parse(output['output_text']))
    
    sectionDict = {}
    with st.sidebar:
        st.header("Identified Resume Sections:")
        
    for section in sections:
        with st.sidebar:
            st.write("📌 **" + ''.join(c for c in section if c.isalpha()  or c.isspace() or c=="-") +"**")

        sectionDict[section] = ""
        query = "Begin all returned text with: 'This is a section of a resume.' Return the heading " + section + " and the text under the " + section + "section of the resume."
        docs = docsearch.get_relevant_documents(query)
    
        refine_prompt_template = (
        "The original question is as follows: {question}\n"
        "We have provided an existing answer: {existing_answer}\n"
        "We have the opportunity to refine the existing answer"
        "(only if needed) with some more context below.\n"
        "------------\n"
        "{context_str}\n"
        "------------\n"
        "Given the new context, refine the original answer to better "
        "answer the question. "
        "If the context isn't useful, return the original answer."
        )
        refine_prompt = PromptTemplate(
        input_variables=["question", "existing_answer", "context_str"],
        template=refine_prompt_template,
        )
    
    
        initial_qa_template = (
        "Context information is below. \n"
        "---------------------\n"
        "{context_str}"
        "\n---------------------\n"
        "Given the context information and not prior knowledge, "
        "answer the question: {question}\n"
        )
        initial_qa_prompt = PromptTemplate(
        input_variables=["context_str", "question"], template=initial_qa_template
        )
        chain = load_qa_chain(OpenAI(temperature=0), chain_type="refine", return_refine_steps=True,
                         question_prompt=initial_qa_prompt, refine_prompt=refine_prompt)
        output = chain({"input_documents": docs, "question": query}, return_only_outputs=True)
        sectionDict[section] = output["output_text"]
        
    docsearch2 = Chroma.from_texts(list(sectionDict.values()), embeddings, metadatas=[{"source": str(i)} for i in range(len(list(sectionDict.values())))]).as_retriever()
    
    return docsearch2, sections

@st.cache_resource(experimental_allow_widgets=True)
def extract_requirements(full_ad_text, sections): 
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(full_ad_text)
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_texts(texts, embeddings, metadatas=[{"source": str(i)} for i in range(len(texts))]).as_retriever()
    query = "Return each individual specific requirement mentioned in this job ad as a python list."
    docs = docsearch.get_relevant_documents(query)
    
    refine_prompt_template = (
    "The original question is as follows: {question}\n"
    "We have provided an existing answer: {existing_answer}\n"
    "We have the opportunity to refine the existing answer"
    "(only if needed) with some more context below.\n"
    "------------\n"
    "{context_str}\n"
    "------------\n"
    "Given the new context, refine the original answer to better "
    "answer the question. "
    "If the context isn't useful, return the original answer."
    )
    refine_prompt = PromptTemplate(
    input_variables=["question", "existing_answer", "context_str"],
    template=refine_prompt_template,
    )
    
    initial_qa_template = (
    "Context information is below. \n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the question: {question}\n"
    )
    initial_qa_prompt = PromptTemplate(
    input_variables=["context_str", "question"], template=initial_qa_template
    )
    chain = load_qa_chain(OpenAI(temperature=0), chain_type="refine", return_refine_steps=True,
                     question_prompt=initial_qa_prompt, refine_prompt=refine_prompt)
    output = chain({"input_documents": docs, "question": query}, return_only_outputs=True)
    output_parser = CommaSeparatedListOutputParser()
    requirements = (output_parser.parse(output['output_text']))
    
    with sidebar:
        st.header("Job Requirements")
    
    for i, requirement in enumerate(requirements):
        with sidebar:
            st.write("🏷️ **" + ''.join(c for c in requirement if c.isalpha()  or c.isspace() or c.isnumeric() or c=="-") +"**")
            query_requirement(requirement, state)
   
    return requirements


def query_requirement(requirement, state):
    input_text = "Does the applicant fulfill " + ''.join(c for c in requirement if c.isalpha() or c.isspace() or c.isnumeric() or c.isnumeric() or c=="-") + "?"
    
    with response_container:
        if input_text:
            response = generate_response(input_text, docsearch2)
            state.past.append(input_text)
            state.generated.append(response)
        
    # if state['generated']:
    #     for i in range(len(st.session_state['generated'])):
    #         message(state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
    #         message(state["generated"][i], key=str(i), avatar_style="bottts")
            

full_resume_text = ""
full_ad_text = ""
if uploaded_resume is None:
    if uploaded_ad is None:
        pass
elif uploaded_ad is None:
    if uploaded_resume is None:
        pass
else:
    ad_reader = PyPDF2.PdfReader(uploaded_ad)
    resume_reader = PyPDF2.PdfReader(uploaded_resume)
    
    for x in range(len(resume_reader.pages)):
        full_resume_text += resume_reader.pages[x].extract_text()
        
    for y in range(len(ad_reader.pages)):
        full_ad_text += ad_reader.pages[y].extract_text()
        
    docsearch2, sections = extract_sections(full_resume_text)
    
    colored_header(label='', description='', color_name='blue-30')
    response_container = st.container()
    input_container = st.container()
    state = st.session_state
    

    requirements = extract_requirements(full_ad_text, sections)
    


    input_text = st.text_input("You: ", "", key="input", placeholder="Ask a question here!")

    
    with response_container:
        if input_text:
            response = generate_response(input_text, docsearch2)
            state.past.append(input_text)
            state.generated.append(response)
        
    if state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
            message(state["generated"][i], key=str(i), avatar_style="bottts")
