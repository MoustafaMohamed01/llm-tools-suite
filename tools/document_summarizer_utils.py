from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from pypdf import PdfReader, errors as pypdf_errors
from docx import Document
from langchain_community.vectorstores import FAISS
import os
from api_key import GEMINI_API_KEY

os.environ['GOOGLE_API_KEY'] = GEMINI_API_KEY

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

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    KnowledgeBase = FAISS.from_texts(chunks, embeddings)
    return KnowledgeBase

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF file.

    Args:
        pdf_file (streamlit.runtime.uploaded_file_manager.UploadedFile): The uploaded PDF file object.

    Returns:
        str: The extracted text.
    """
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() or ''
        return text
    except pypdf_errors.PdfStreamError:
        return "ERROR: Could not read PDF. The file might be corrupted or malformed."
    except Exception as e:
        return f"ERROR: An unexpected error occurred while processing the PDF: {e}"


def extract_text_from_docx(docx_file):
    """
    Extracts text from a DOCX (Word) file.

    Args:
        docx_file (streamlit.runtime.uploaded_file_manager.UploadedFile): The uploaded DOCX file object.

    Returns:
        str: The extracted text.
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
        str: The summarized text of the document, or an error message.
    """
    if doc_file is None:
        return "No document file uploaded."

    file_extension = os.path.splitext(doc_file.name)[1].lower()
    text = ''

    if file_extension == '.pdf':
        text = extract_text_from_pdf(doc_file)
    elif file_extension == '.docx':
        text = extract_text_from_docx(doc_file)
    else:
        return "Unsupported file type. Please upload a PDF or DOCX document."

    if text.startswith("ERROR:"):
        return text

    if not text.strip():
        return "Could not extract any meaningful text from the provided document. It might be an image-based file, empty, or encrypted."

    KnowledgeBase = process_text(text)
    query = 'summarize the content of the uploaded document in approximately 3-5 sentences'

    if query:
        docs = KnowledgeBase.similarity_search(query)

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)

        chain = load_qa_chain(llm, chain_type='stuff')

        try:
            response = chain.run(input_documents=docs, question=query)
            return response
        except Exception as e:
            return f"ERROR: An error occurred during summarization with the LLM: {e}"
    else:
        return "Summarization query is empty."
