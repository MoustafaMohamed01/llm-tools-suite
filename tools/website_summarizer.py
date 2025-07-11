import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

def website_summarizer_app():
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        st.error(
            "**ERROR:** Gemini API key not found for Website Summarizer. "
            "Please set it as an environment variable named `GEMINI_API_KEY` "
            "(e.g., in Streamlit Cloud secrets, Heroku config vars, or your local shell)."
        )
        return

    genai.configure(api_key=gemini_api_key)

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        st.error(f"Failed to initialize Gemini model for Website Summarizer: {e}. Please check your API key and try again.")
        return

    class Website:
        def __init__(self, url: str):
            self.url = url
            self.title = "No title found"
            self.text = ""
            self._scrape_website()

        def _scrape_website(self):
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = requests.get(self.url, headers=headers, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                self.title = soup.title.string if soup.title and soup.title.string else self.title

                for irrelevant in soup.find_all(["script", "style", "img", "input", "nav", "footer", "header", "aside", "form", "button", "link", "meta", "svg"]):
                    irrelevant.decompose()

                content_tags = ['main', 'article', 'div']
                possible_content_divs = []
                for tag in content_tags:
                    possible_content_divs.extend(soup.find_all(tag, class_=['content', 'main-content', 'article-body', 'post-content', 'entry-content', 'body', 'text-body']))

                extracted_text = ""
                if possible_content_divs:
                    for div in possible_content_divs:
                        extracted_text += div.get_text(separator="\n", strip=True) + "\n"
                elif soup.body:
                    extracted_text = soup.body.get_text(separator="\n", strip=True)

                self.text = "\n".join(filter(None, [line.strip() for line in extracted_text.splitlines()]))
                self.text = ' '.join(self.text.split())
                self.text = self.text[:15000]

            except requests.exceptions.MissingSchema:
                st.error(f"Invalid URL format. Please ensure it starts with 'http://' or 'https://'.")
                self.text = ""
            except requests.exceptions.ConnectionError:
                st.error(f"Could not connect to the website. Please check the URL and your internet connection.")
                self.text = ""
            except requests.exceptions.Timeout:
                st.error(f"The request to the website timed out after 15 seconds.")
                self.text = ""
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to retrieve the website content: {e}. Status code: {response.status_code if 'response' in locals() else 'N/A'}")
                self.text = ""
            except Exception as e:
                st.error(f"An unexpected error occurred while parsing the website: {e}")
                self.text = ""

    SYSTEM_PROMPT = "You are an assistant that summarizes website content, focusing on key information and ignoring navigation elements. Respond in markdown format. Provide a concise summary, ideally in 3-5 bullet points or a short paragraph."

    def generate_user_prompt(website_title, website_text):
        user_prompt = f"Summarize the following website content professionally and concisely. "
        user_prompt += f"The website is titled '{website_title}'.\n\n"
        user_prompt += f"Content:\n\n{website_text}\n\n"
        user_prompt += "Provide a summary in 3-5 bullet points or a short paragraph, focusing on the main message, key facts, and important announcements. Avoid introductory or concluding phrases like 'Here is a summary' or 'In conclusion'."
        return user_prompt

    def summarize_website_content(url, current_model):
        if current_model is None:
            return "Gemini API model is not configured. Cannot summarize."

        website = Website(url)

        if not website.text:
            return "Could not extract sufficient content from the provided URL, or an error occurred during scraping. Please try a different URL."

        user_prompt = generate_user_prompt(website.title, website.text)

        try:
            # Using the model passed from the main function
            response = current_model.generate_content(user_prompt)
            return response.text
        except Exception as e:
            st.error(f"An error occurred while generating the summary: {e}. This might be due to content length or API issues. Please try again.")
            return "Failed to generate summary. Please try again or provide a different URL."

    st.subheader("Enter Website URL")
    url = st.text_input("URL:", placeholder="e.g., https://www.google.com/docs/gemini/summarization-example")

    if 'website_summary_output' not in st.session_state:
        st.session_state.website_summary_output = ""

    if st.button("Summarize Website", type="primary"):
        if url:
            with st.spinner("Fetching and summarizing website content... This may take a moment."):
                summary = summarize_website_content(url, model)
                if summary and not summary.startswith("Gemini API model is not configured"):
                    st.session_state.website_summary_output = summary
                    st.markdown("### Summary")
                    st.markdown(summary)
                else:
                    st.session_state.website_summary_output = ""
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
