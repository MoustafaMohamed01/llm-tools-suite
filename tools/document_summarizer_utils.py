from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from pypdf import PdfReader, errors as pypdf_errors
from docx import Document
from langchain_community.vectorstores import FAISS
import os
import streamlit as st

def process_text(text):
    """
    Processes the input text by splitting it into chunks and creating a FAISS knowledge base.

    Args:
        text (str): The raw text extracted from the PDF or Word document.

    Returns:
        FAISS: A FAISS vector store containing the text chunks and their embeddings.
    """
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    os.environ['GOOGLE_API_KEY'] = gemini_api_key

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    KnowledgeBase = FAISS.from_texts(chunks, embeddings)
    return KnowledgeBase

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF file.

    Args:
        pdf_file (streamlit.runtime.uploaded_file_manager.UploadedFile): The uploaded PDF file object.

    Returns:
        str: The extracted text, or an error message prefixed with "ERROR:".
    """
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() or ''
        return text
    except pypdf_errors.PdfStreamError:
        return "ERROR: Could not read PDF. The file might be corrupted, malformed, or encrypted."
    except Exception as e:
        return f"ERROR: An unexpected error occurred while processing the PDF: {e}"


def extract_text_from_docx(docx_file):
    """
    Extracts text from a DOCX (Word) file.

    Args:
        docx_file (streamlit.runtime.uploaded_file_manager.UploadedFile): The uploaded DOCX file object.

    Returns:
        str: The extracted text, or an error message prefixed with "ERROR:".
    """
    try:
        document = Document(docx_file)
        text = ''
        for paragraph in document.paragraphs:
            text += paragraph.text + '\n'
        return text
    except Exception as e:
        return f"ERROR: An error occurred while processing the Word document: {e}"


def summerizer(doc_file):
    """
    Summarizes the content of an uploaded PDF or Word document using the Gemini API.

    Args:
        doc_file (streamlit.runtime.uploaded_file_manager.UploadedFile): The uploaded document file object (PDF or DOCX).

    Returns:
        str: The summarized text of the document, or an error message prefixed with "ERROR:".
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        return (
            "ERROR: Gemini API key not found for Document Summarizer. "
            "Please set it as an environment variable named `GEMINI_API_KEY` "
            "(e.g., in Streamlit Cloud secrets, Heroku config vars, or your local shell)."
        )
    os.environ['GOOGLE_API_KEY'] = gemini_api_key

    if doc_file is None:
        return "ERROR: No document file uploaded."

    file_extension = os.path.splitext(doc_file.name)[1].lower()
    text = ''

    if file_extension == '.pdf':
        text = extract_text_from_pdf(doc_file)
    elif file_extension == '.docx':
        text = extract_text_from_docx(doc_file)
    else:
        return "ERROR: Unsupported file type. Please upload a PDF or DOCX document."

    if text.startswith("ERROR:"):
        return text

    if not text.strip():
        return "ERROR: Could not extract any meaningful text from the provided document. It might be an image-based file, empty, or encrypted."

    try:
        KnowledgeBase = process_text(text)
    except Exception as e:
        return f"ERROR: Failed to create knowledge base from document due to embedding or API configuration issue. Ensure your `GEMINI_API_KEY` is correct and has access to embedding models. Details: {e}"

    query = 'summarize the entire content of the uploaded document concisely in 3-5 sentences, capturing the main points and key takeaways.'

    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)
    except Exception as e:
        return f"ERROR: Failed to initialize Gemini LLM. Ensure your `GEMINI_API_KEY` is correct and has access to Gemini 1.5 Flash. Details: {e}"

    chain = load_qa_chain(llm, chain_type='stuff')

    try:
        docs = KnowledgeBase.similarity_search(query, k=5)

        response = chain.run(input_documents=docs, question=query)
        return response
    except Exception as e:
        return f"ERROR: An error occurred during summarization with the LLM. This might be due to token limits for very large documents, or an API issue. Details: {e}"
