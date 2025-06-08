import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from api_key import GEMINI_API_KEY

def configure_gemini():
    api_key = GEMINI_API_KEY

    if not api_key:
        st.error("Gemini API key is missing. Please ensure 'GEMINI_API_KEY' is set in 'api_key.py'.")
        return None
    if not api_key.startswith("AIzaSy"):
        st.warning("Invalid API key format. Gemini API keys usually start with 'AIzaSy'. Please check 'api_key.py'.")
    if api_key.strip() != api_key:
        st.warning("Extra spaces detected around your API key in 'api_key.py'. Please remove them.")
    
    genai.configure(api_key=api_key)
    try:
        list(genai.list_models())
        return genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        st.error(f"Failed to connect to Gemini API in Website Summarizer. Please check your API key in 'api_key.py' and internet connection. Error: {e}")
        return None

model = configure_gemini()

class Website:
    def __init__(self, url: str):
        self.url = url
        self.title = "No title found"
        self.text = ""
        self._scrape_website()

    def _scrape_website(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status() 
            soup = BeautifulSoup(response.content, "html.parser")
            self.title = soup.title.string if soup.title else self.title
            
            for irrelevant in soup.find_all(["script", "style", "img", "input", "nav", "footer", "header", "aside"]):
                irrelevant.decompose()
            
            content_div = soup.find('div', class_=['content', 'main-content', 'article-body'])
            if content_div:
                self.text = content_div.get_text(separator="\n", strip=True)
            elif soup.body:
                self.text = soup.body.get_text(separator="\n", strip=True)
            else:
                self.text = ""

        except requests.exceptions.MissingSchema:
            st.error(f"Invalid URL format. Please ensure it starts with 'http://' or 'https://'.")
            self.text = ""
        except requests.exceptions.ConnectionError:
            st.error(f"Could not connect to the website. Please check the URL and your internet connection.")
            self.text = ""
        except requests.exceptions.Timeout:
            st.error(f"The request to the website timed out.")
            self.text = ""
        except requests.RequestException as e:
            st.error(f"Failed to retrieve the website: {e}")
            self.text = ""
        except Exception as e:
            st.error(f"An error occurred while parsing the website: {e}")
            self.text = ""

SYSTEM_PROMPT = "You are an assistant that summarizes website content, focusing on key information and ignoring navigation elements. Respond in markdown format. Provide a concise summary, ideally in 3-5 bullet points or a short paragraph."

def generate_user_prompt(website_title, website_text):
    user_prompt = f"You are looking at this website titled: {website_title}\n\n"
    user_prompt += "The contents of this website are as follows. Please provide a short, concise summary in markdown format. "
    user_prompt += "If it includes news or announcements, summarize these too.\n\n"
    user_prompt += f"{website_text}"
    return user_prompt

def summarize_website_content(url):
    if not model:
        st.warning("Gemini API is not configured. Cannot summarize.")
        return "Gemini API is not configured. Please ensure your API key is set correctly in 'api_key.py'."
    
    website = Website(url)
    
    if not website.text:
        return "Could not extract content from the provided URL or an error occurred during scraping."

    user_prompt = generate_user_prompt(website.title, website.text)
    
    try:
        response = model.generate_content(user_prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred while generating the summary: {e}")
        return "Failed to generate summary. Please try again."

def website_summarizer_app():
    st.subheader("Enter Website URL")
    url = st.text_input("URL:", placeholder="e.g., https://www.example.com")

    if 'website_summary_output' not in st.session_state:
        st.session_state.website_summary_output = ""

    if st.button("Summarize Website"):
        if url:
            with st.spinner("Summarizing website..."):
                summary = summarize_website_content(url)
                st.session_state.website_summary_output = summary
                st.markdown("### Summary")
                st.markdown(summary)
        else:
            st.warning("Please enter a URL to summarize.")

    if st.session_state.website_summary_output:
        st.download_button(
            label="Download Summary as Markdown",
            data=st.session_state.website_summary_output,
            file_name="website_summary.md",
            mime="text/markdown",
            help="Click to download the generated summary as a Markdown file."
        )
