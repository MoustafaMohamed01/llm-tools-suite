import streamlit as st
import os
import google.generativeai as genai
from tools import blog_assistant
from tools import data_analyzer
from tools import sql_query_generator
from tools import document_summarizer
from tools import website_summarizer 

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    st.error(
        "**ERROR:** Gemini API key not found."
        " Please set it as an environment variable named `GEMINI_API_KEY` "
        "(e.g., in Streamlit Cloud secrets, Heroku config vars, or your local shell)."
    )
    st.stop()

genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel('gemini-2.0-flash')

professional_persona_instruction = """
You are an AI assistant designed to provide professional, and accurate information.
Your responses should be:
- **Formal and Respectful:** Maintain a polite and courteous tone at all times.
- **Objective and Factual:** Focus on verifiable information and avoid personal opinions or emotional language.
- **Grammatically Correct:** Ensure flawless grammar, spelling, and punctuation.
- **Solution-Oriented:** When appropriate, offer practical advice or solutions based on the query.
- **Avoid Ambiguity:** Provide definitive answers where possible. If uncertainty exists, state it clearly.
- **Maintain Confidentiality:** Do not ask for or provide sensitive personal information.
- **Neutral and Unbiased:** Present information without prejudice or favoritism.
"""

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[
        {"role": "user", "parts": [professional_persona_instruction]},
        {"role": "model", "parts": ["Understood. I will adhere to these guidelines for all interactions. How may I assist you?"]}
    ])
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Hello! I am an AI assistant designed to provide professional, concise, and accurate information. How may I assist you today?"})


TOOLS = {
    "AI Assistant": {
        "icon": "🧠",
        "name": "AI Assistant",
        "function": None,
        "description": "Engage in a professional conversation with an AI assistant."
    },

    "Blog AI Assistant": {
        "icon": "📝",
        "name": "Blog AI Assistant",
        "function": blog_assistant.blog_assistant_app,
        "description": "Generate engaging blog posts with AI assistance."
    },

    "AI CSV Analyzer": {
        "icon": "📊",
        "name": "AI CSV Analyzer",
        "function": data_analyzer.data_analyzer_app,
        "description": "Upload and analyze your CSV data using AI."
    },

    "SQL Query Generator": {
        "icon": "💻",
        "name": "SQL Query Generator",
        "function": sql_query_generator.sql_query_generator_app,
        "description": "Generate SQL queries from natural language descriptions."
    },

    "Document Summarizer": {
        "icon": "📄",
        "name": "Document Summarizer",
        "function": document_summarizer.document_summarizer_app,
        "description": "Summarize PDF and Word documents instantly."
    },

    "Website Summarizer": {
        "icon": "🌐",
        "name": "Website Summarizer",
        "function": website_summarizer.website_summarizer_app,
        "description": "Summarize web pages by providing a URL."
    },
}

st.set_page_config(
    page_title="LLM Tools Suite",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.google.com/search?q=llm+tools+suite+help',
        'Report a bug': "https://www.google.com/search?q=llm+tools+suite+bug+report",
        'About': "# **LLM Tools Suite**\n_A collection of AI-powered tools for everyday tasks._",
    }
)

with st.sidebar:
    st.title("LLM Tools Suite")
    st.markdown("---")

    tool_options = [f"{tool_info['icon']} {tool_name}" for tool_name, tool_info in TOOLS.items()]
    selected_tool_display = st.radio("Select a Tool:", tool_options, index=0)

    st.markdown("---")
    st.info("Choose a tool from the list above to get started!")

selected_tool_name = selected_tool_display.split(' ', 1)[1]

if selected_tool_name == "AI Assistant":
    st.title('AI Assistant')
    st.markdown("""
        I'm here to provide you with professional and accurate information.
        Please feel free to ask your questions.
    """)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask a professional question...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Processing request..."):
            try:
                response_chunks = st.session_state.chat_session.send_message(user_input, stream=True)
                
                full_response = ""
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    for chunk in response_chunks:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌") 
                    message_placeholder.markdown(full_response) 

                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"An error occurred: {e}. Please try again.")

    def get_chat_history_as_text():
        history_text = ""
        for message in st.session_state.messages:
            role = "You" if message["role"] == "user" else "Assistant"
            history_text += f"{role}: {message['content']}\n\n"
        return history_text

    if st.session_state.messages:
        st.download_button(
            label="Download Conversation",
            data=get_chat_history_as_text(),
            file_name="chatbot_conversation.txt",
            mime="text/plain",
            help="Click to download the current conversation history."
        )

else:
    selected_tool_info = TOOLS[selected_tool_name]
    selected_tool_function = selected_tool_info["function"]
    selected_tool_description = selected_tool_info["description"]

    st.title(f"{selected_tool_info['icon']} {selected_tool_name}")
    st.markdown(f"**{selected_tool_description}**")
    st.markdown("---")

    selected_tool_function()
