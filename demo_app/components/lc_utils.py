import streamlit as st
import PyPDF2
from docx import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from hugchat import hugchat
from langchain.chains import RetrievalQA


    
@st.cache_resource
def _extract_sections(full_resume_text): 
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(full_resume_text)
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_texts(texts, embeddings, metadatas=[{"source": str(i)} for i in range(len(texts))]).as_retriever()
    query = "Return the sections of this resume as a python list."
    docs = docsearch.get_relevant_documents(query)
    #sidebar=st.sidebar

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
    chain = load_qa_chain(OpenAI(temperature=0), 
                          chain_type="refine", return_refine_steps=True,
                          question_prompt=initial_qa_prompt, 
                          refine_prompt=refine_prompt)
    output = chain(
        {"input_documents": docs, "question": query}, 
        return_only_outputs=True)
    output_parser = CommaSeparatedListOutputParser()
    sections = (output_parser.parse(output['output_text']))
    
    sectionDict = {}
    
    st.sidebar.header("Identified Resume Sections:")
        
    for section in sections:
        st.sidebar.write("📌 **" + ''.join(c for c in section if c.isalpha()  or c.isspace() or c=="-") +"**")

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



