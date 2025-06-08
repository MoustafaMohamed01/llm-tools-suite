# LLM Tools Suite

An integrated collection of AI-powered tools designed to enhance productivity and streamline various tasks using advanced Large Language Models. This suite offers a unified interface to access powerful features for content generation, data analysis, query creation, document summarization, and more.

-----

## Features

The LLM Tools Suite brings together several specialized modules in one convenient Streamlit application:

  - **🧠 AI Assistant**
    Engage in a professional conversation with an AI assistant for quick, accurate information. This is now the default landing page.

  - **📝 Blog AI Assistant**
    Generate high-quality blog content using AI based on a title, keywords, and desired word count.

  - **📊 AI CSV Analyzer**
    Upload your CSV files and analyze them intelligently using LLM-powered queries.

  - **💻 SQL Query Generator**
    Transform plain English into SQL queries with the help of AI.

  - **📄 Document Summarizer**
    Upload a PDF or Word document and get a concise summary in seconds, with the option to download the output.

  - **🌐 Website Summarizer**
    Provide a URL and get a concise summary of the web page content, with a convenient download option for the summary.

-----

## Screenshots

### 🧠 AI Assistant

 \#\#\# 📝 Blog AI Assistant

### 📊 AI CSV Analyzer

### 💻 SQL Query Generator

### 📄 Document Summarizer

### 🌐 Website Summarizer

 ---

## Project Structure

```
llm-tools-suite/
│
├── tools/
│   ├── blog_assistant.py
│   ├── data_analyzer.py
│   ├── sql_query_generator.py
│   ├── document_summarizer.py
│   ├── document_summarizer_utils.py
│   └── website_summarizer.py     # New tool for website summarization
│
├── app.py                      # Main Streamlit app interface
├── README.md                   # Project documentation
├── requirements.txt            # Required Python packages
├── images/                     # Screenshots
└── api_key.py                  # (Not pushed) API key file for Gemini

```

-----

## Installation

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/MoustafaMohamed01/llm-tools-suite.git
    cd llm-tools-suite
    ```

2.  **Install Requirements**

    ```bash
    pip install -r requirements.txt
    ```

    *Self-correction: You might need to add `requests`, `beautifulsoup4`, and `python-dotenv` to your `requirements.txt` if they aren't already there, especially if you're using `python-dotenv` for other parts or if your `document_summarizer_utils.py` relies on it.*

3.  **Add Your API Key**

    Create a file named `api_key.py` in the root folder and add:

    ```python
    GEMINI_API_KEY = "your-gemini-api-key"
    ```

    *Ensure your API key is correctly set in `api_key.py` as both the main app and the new `website_summarizer` tool directly import from it.*

-----

## Run the App

```bash
streamlit run app.py
```

The app will open in your browser, defaulting to the **AI Assistant** page. You can switch between tools using the sidebar.

-----

## Built With

  * **Streamlit** – For building the web UI
  * **LangChain** – Managing LLM chains and document processing
  * **Google Gemini API** – Large Language Model (LLM) backend
  * **FAISS** – Vector search for summarization
  * **pypdf / python-docx** – Document parsing libraries
  * **Requests & Beautiful Soup 4 (BS4)** – For web scraping functionality in the Website Summarizer

-----

## To-Do

  * Add support for DOC files (if not already covered by `python-docx`)
  * Enable chat-based interaction for CSV analysis
  * Add user authentication for secure access
  * **Enhance summary download options (e.g., specific file types like PDF for summarizers)**

-----

## Acknowledgements

Thanks to the open-source community and developers of [Streamlit](https://streamlit.io), [LangChain](https://www.langchain.com/), and [Google AI](https://ai.google/).

-----

## About Me

**Moustafa Mohamed**
Aspiring AI Developer with a focus on **Machine Learning, Deep Learning**, and **LLM Engineering**.

  * **GitHub**: [MoustafaMohamed01](https://github.com/MoustafaMohamed01)
  * **Linkedin**: [Moustafa Mohamed](https://www.linkedin.com/in/moustafamohamed01/)
  * **Kaggle**: [moustafamohamed01](https://www.kaggle.com/moustafamohamed01)
  * **Portfolio**: [moustafamohamed](https://moustafamohamed.netlify.app/)

-----
