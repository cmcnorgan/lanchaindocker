import PyPDF2
from docx import Document

def extract_text(uploaded_file):
    """
    Given Streamlit UploadedFile (.pdf or .docx) object,
    determine filetype 
    then call docx or pypdf2 methods to
    return full plaintext contents
    """
    fulltext = ""
    ispdf=False
    isdocx=False

    if uploaded_file is None:
        #No file, so return empty full text string
        return fulltext
    #sort out what kind of document we're working with
    else:
        fname=uploaded_file.name
        docxtypestring = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        pdftypestring = "application/pdf"
        ispdf=uploaded_file.type == pdftypestring
        isdocx=uploaded_file.type == docxtypestring
        
    #use extraction methods appropriate for document type
    if ispdf:
        file_reader = PyPDF2.PdfReader(uploaded_file)
        for p in range(len(file_reader.pages)):
            fulltext += file_reader.pages[p].extract_text()
    
    if isdocx:
        doc = Document(uploaded_file)
        for paragraph in doc.paragraphs:
            fulltext += paragraph.text + "\n"

    return fulltext
