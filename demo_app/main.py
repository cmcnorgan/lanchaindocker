import streamlit as st
from components.upload_resume import _upload_resume
from components.view_resume import _scrape_ad
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import VectorDBQA
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from components._extract_requirements import _extract_requirements
from components.generate_response import generate_response
from streamlit_chat import message

#Possible actions: upload resume (up) and view resume (vw)
#View requires an id and a url
args = {
    "action": ["up"],
    "id": [""],
    "url": [""],
    "adid": [""]
}
_args=st.experimental_get_query_params()
#update defaults with any passed parameters
for key, value in _args.items():
    args[key]=value

st.title("Resume-AI")
st.header("Your NLP-powered HR Assistant")
st.write("Resume-AI leverages NLP to help HR professionals identify talent and \
         expertise among applicants without requiring niche expertise in all possible jobs.")

match args["action"][0].lower():
    case "up":
        _upload_resume()
    case "vw":
        url=args["url"][0].lower()
        ad_text=(_scrape_ad(url))
        resumeid=args["id"][0].upper()
        #st.write(ad_text)
        st.write("Extracting details from resume " + resumeid)
        basedir='chromadb/'
        persistdirectory=basedir+resumeid

        embeddings=OpenAIEmbeddings()
        vectordb = Chroma(persist_directory=persistdirectory, embedding_function=embeddings)
        
        if 'generated' not in st.session_state:
            st.session_state['generated'] = ["No, SUNY Oswego does not have any PhD programs."]
        if 'past' not in st.session_state:
            st.session_state['past'] = ["Did the applicant obtain a PhD from SUNY Oswego?"]
        
        state = st.session_state
        response_container = st.container()
        
        requirements = _extract_requirements(ad_text)
        st.sidebar.header("Identifying Job Duties and Requirements")
        for i, requirement in enumerate(requirements):
            #string together a query
            input_text = "Does the resume document mention skills or achievements associated with " + ''.join(c for c in requirement if c.isalpha() or c.isspace() or c.isnumeric() or c.isnumeric() or c=="-") + "?"
            with response_container:
                if input_text:
                    response = generate_response(input_text, vectordb)
                    state.past.append(input_text)
                    state.generated.append(response)
        if state['generated']:
            for i in range(len(st.session_state['generated'])):
                message(state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                message(state["generated"][i], key=str(i), avatar_style="bottts")
#            st.sidebar.write("🏷️ **" + ''.join(c for c in requirement if c.isalpha()  or c.isspace() or c.isnumeric() or c=="-") +"**")