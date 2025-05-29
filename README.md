# LLM Tools Suite

An integrated collection of AI-powered tools designed to enhance productivity and streamline various tasks using advanced Large Language Models. This suite offers a unified interface to access powerful features for content generation, data analysis, query creation, and document summarization.

---

## Features
The LLM Tools Suite brings together several specialized modules in one convenient Streamlit application:

- **🏠 Overview**  
  A welcoming home screen providing an introduction to the suite and a quick overview of all available tools.

- **📝 Blog AI Assistan**  
  Generate high-quality blog content using AI based on a title, keywords, and desired word count.

- **📊 AI CSV Analyzer**  
  Upload your CSV files and analyze them intelligently using LLM-powered queries.

- **💻 SQL Query Generator**  
  Transform plain English into SQL queries with the help of AI.

- **📄 Document Summarizer**  
  Upload a PDF or Word document and get a concise summary in seconds.

---

## Screenshots

### 🏠 Overview
![Overview](images/overview.png)

### 📝 Blog AI Assistant
![Blog Assistant](images/blog_assistant.png)

### 📊 AI CSV Analyzer
![CSV Analyzer](images/data_analyzer.png)

### 💻 SQL Query Generator
![SQL Generator](images/sql_generator.png)

### 📄 Document Summarizer
![Document Summarizer](images/document_summarizer.png)

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
│   └── document_summarizer\_utils.py
│
├── app.py                          # Main Streamlit app interface
├── README.md                       # Project documentation
├── requirements.txt                # Required Python packages
├── images/                         # Screenshots
└── api_key.py                      # (Not pushed) API key file for Gemini

````

---

## Installation

1. **Clone the Repository**

```bash
git clone https://github.com/MoustafaMohamed01/llm-tools-suite.git
cd llm-tools-suite
````

2. **Install Requirements**

```bash
pip install -r requirements.txt
```

3. **Add Your API Key**

Create a file named `api_key.py` in the root folder and add:

```python
GEMINI_API_KEY = "your-gemini-api-key"
```

---

## Run the App

```bash
streamlit run app.py
```

The app will open in your browser. You can interact with the tools from the sidebar.

---

## Built With

* **Streamlit** – For building the web UI
* **LangChain** – Managing LLM chains and document processing
* **Google Gemini API** – Large Language Model (LLM) backend
* **FAISS** – Vector search for summarization
* **pypdf / python-docx** – Document parsing libraries

---

## To-Do

* [ ] Add support for DOC files
* [ ] Enable chat-based interaction for CSV analysis
* [ ] Save/export summaries and outputs
* [ ] Add user authentication for secure access

---

## Acknowledgements

Thanks to the open-source community and developers of [Streamlit](https://streamlit.io), [LangChain](https://www.langchain.com/), and [Google AI](https://ai.google/).

---

## About Me

**Moustafa Mohamed**  
Aspiring AI Developer with a focus on **Machine Learning, Deep Learning**, and **LLM Engineering**.

* **GitHub**: [MoustafaMohamed01](https://github.com/MoustafaMohamed01)
* **Linkedin**: [Moustafa Mohamed](https://www.linkedin.com/in/moustafamohamed01/)
* **Kaggle**: [moustafamohamed01](https://www.kaggle.com/moustafamohamed01)
* **Portfolio**: [moustafamohamed](https://moustafamohamed.netlify.app/)

---
