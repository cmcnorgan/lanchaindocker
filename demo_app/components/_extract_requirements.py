import streamlit as st
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.output_parsers import CommaSeparatedListOutputParser
from components.generate_response import generate_response


@st.cache_resource(experimental_allow_widgets=True)
def _extract_requirements(_full_ad_text): 
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(_full_ad_text)
    embeddings = OpenAIEmbeddings()
    jdocsearch = Chroma.from_texts(texts, 
                                   embeddings, 
                                   metadatas=[{"source": str(i)} for i in range(len(texts))]).as_retriever()
    
    query = "Identify keywords for each individual job requirement for the position described in this job ad. Ignore items that appear to be job benefits. Return the requirement keywords as a python list."
    docs = jdocsearch.get_relevant_documents(query)

    #query = "Identify and generate a 5-word summary of each individual specific requirement mentioned in this job ad, append the summary to a python list, and return the list."
    #docs = jdocsearch.get_relevant_documents(query)

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
    
    return requirements


def _query_requirement(requirement, _state, _response_container, _vectordb):
    input_text = "Does the applicant fulfill " + ''.join(c for c in requirement if c.isalpha() or c.isspace() or c.isnumeric() or c.isnumeric() or c=="-") + "?"
    with _response_container:
        if input_text:
            response = generate_response(input_text, _vectordb)
            _state.past.append(input_text)
            _state.generated.append(response)