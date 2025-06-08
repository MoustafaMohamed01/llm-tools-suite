import streamlit as st
import os # Import the os module
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
# --- REMOVE THIS LINE: from api_key import GEMINI_API_KEY ---

def configure_gemini():
    # --- Get API key from environment variables ---
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error(
            "**ERROR:** Gemini API key not found for Website Summarizer."
            " Please set it as an environment variable named `GEMINI_API_KEY` "
            "(e.g., in Streamlit Cloud secrets, Heroku config vars, or your local shell)."
        )
        return None
    # Basic validation, Gemini API keys usually start with 'AIzaSy'
    if not api_key.startswith("AIzaSy"):
        st.warning("Invalid API key format. Gemini API keys usually start with 'AIzaSy'. Please check your environment variable setting.")
    # No need to check for strip() if it's from env var unless manually set with spaces
    
    genai.configure(api_key=api_key)
    try:
        # Test if the API key is valid by trying to list models
        list(genai.list_models())
        return genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        st.error(f"Failed to connect to Gemini API in Website Summarizer. Please check your API key environment variable and internet connection. Error: {e}")
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
            response = requests.get(self.url, headers=headers, timeout=10) # Added timeout and User-Agent
            response.raise_for_status() # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.content, "html.parser")
            self.title = soup.title.string if soup.title else self.title
            
            # Remove irrelevant tags more robustly
            for irrelevant in soup.find_all(["script", "style", "img", "input", "nav", "footer", "header", "aside"]):
                irrelevant.decompose()
            
            # Get text from body or common content containers
            content_div = soup.find('div', class_=['content', 'main-content', 'article-body']) # Common content classes
            if content_div:
                self.text = content_div.get_text(separator="\n", strip=True)
            elif soup.body:
                self.text = soup.body.get_text(separator="\n", strip=True)
            else:
                self.text = "" # Fallback if no body or specific content div

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
    # Ensure model is initialized before proceeding
    if model is None: # Changed from 'not model' to 'model is None' for clarity after configure_gemini could return None
        st.warning("Gemini API model is not configured. Cannot summarize.")
        return "Gemini API model is not configured. Please ensure your API key environment variable is set correctly."
    
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

# Streamlit app function for this tool
def website_summarizer_app():
    st.subheader("Enter Website URL")
    url = st.text_input("URL:", placeholder="e.g., https://www.example.com")

    # Use a session state variable to store the summary so it persists for the download button
    if 'website_summary_output' not in st.session_state:
        st.session_state.website_summary_output = ""

    if st.button("Summarize Website"):
        if url:
            with st.spinner("Summarizing website..."):
                summary = summarize_website_content(url)
                # Only update and display if summary generation was successful
                if summary and "Failed to generate summary" not in summary and "Gemini API model is not configured" not in summary:
                    st.session_state.website_summary_output = summary # Store in session state
                    st.markdown("### Summary")
                    st.markdown(summary)
                else:
                    # If an error message was returned, display it and clear session state
                    st.session_state.website_summary_output = ""
                    # The error is already shown by summarize_website_content, no need to show again
        else:
            st.warning("Please enter a URL to summarize.")

    # Show download button only if a summary has been generated
    if st.session_state.website_summary_output:
        st.download_button(
            label="Download Summary as Markdown",
            data=st.session_state.website_summary_output,
            file_name="website_summary.md",
            mime="text/markdown",
            help="Click to download the generated summary as a Markdown file."
        )
