import streamlit as st
import os
import json
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Invoice Extractor", layout="wide")

def extract_text_from_pdfs(uploaded_files):
    import tempfile
    from app.pdf_processor import PDFProcessor
    from app.ocr_processor import OCRProcessor
    
    full_text = ""
    pdf_processor = None
    ocr_processor = None
    
    for uploaded_file in uploaded_files:
        # First try normal text extraction
        pdf_reader = PdfReader(uploaded_file)
        file_text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                file_text += page_text + "\n"
                
        # If the PDF is scanned (no text), seamlessly fall back to your existing OCR engine!
        if not file_text.strip() or len(file_text.strip()) < 50:
            if not pdf_processor:
                pdf_processor = PDFProcessor()
                ocr_processor = OCRProcessor()
                
            with tempfile.TemporaryDirectory() as temp_dir:
                pdf_path = os.path.join(temp_dir, uploaded_file.name)
                uploaded_file.seek(0)
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_file.read())
                
                image_paths = pdf_processor.pdf_to_images(pdf_path, temp_dir)
                for img_path in image_paths:
                    file_text += ocr_processor.extract_text_from_image(img_path) + "\n"
                    
        full_text += file_text + "\n"
        
    return full_text

def create_vector_store(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    
    embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = FAISS.from_texts(chunks, embedding_model)
    vector_store.save_local("faiss_index")
    return vector_store

def extract_invoice_data(vector_store):
    query = "invoice number date vendor recipient total amount tax currency line items"
    docs = vector_store.similarity_search(query, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    prompt = PromptTemplate(
        template="""
You are an invoice data extraction assistant.
Extract all relevant invoice information from the context below.
Return ONLY a raw JSON object. No explanation. No markdown. No code blocks.

Use exactly this JSON structure:
{{
  "invoice_number": "",
  "date": "",
  "vendor": "",
  "recipient": "",
  "total_amount": 0.0,
  "tax": 0.0,
  "currency": "",
  "line_items": [
    {{
      "description": "",
      "quantity": 0,
      "unit_price": 0.0,
      "total": 0.0
    }}
  ]
}}

Context:
{context}
""",
        input_variables=["context"]
    )
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({"context": context})
    
    try:
        # Extra step to strip markdown if the LLM ignores instructions
        cleaned_response = response.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:-3].strip()
        elif cleaned_response.startswith('```'):
            cleaned_response = cleaned_response[3:-3].strip()
            
        result = json.loads(cleaned_response)
        return result
    except json.JSONDecodeError:
        return response

st.title("📄 Invoice to JSON Extractor")

st.sidebar.header("Upload Invoices")
uploaded_files = st.sidebar.file_uploader("Upload PDF Invoices", accept_multiple_files=True, type=["pdf"])

if st.sidebar.button("📥 Build Vector Store"):
    if uploaded_files:
        with st.spinner("Extracting text and building vector store..."):
            text = extract_text_from_pdfs(uploaded_files)
            if text:
                vector_store = create_vector_store(text)
                st.session_state["vector_store"] = vector_store
                st.sidebar.success("Vector store created!")
            else:
                st.sidebar.error("Warning: Could not extract any text from the provided PDFs.")
    else:
        st.sidebar.warning("Please upload at least one PDF file first.")

if st.button("🔍 Extract Invoice Data"):
    if "vector_store" in st.session_state:
        with st.spinner("Extracting intelligent invoice data via Gemini AI..."):
            result = extract_invoice_data(st.session_state["vector_store"])
            st.session_state["extracted_data"] = result
            
            if isinstance(result, dict):
                st.json(result)
            else:
                st.text(result)
    else:
        st.warning("Vector store hasn't been created yet. Please upload files and click 'Build Vector Store' in the sidebar.")
elif "extracted_data" in st.session_state:
    # Display previous result if it exists in session state
    result = st.session_state["extracted_data"]
    if isinstance(result, dict):
        st.json(result)
    else:
        st.text(result)
