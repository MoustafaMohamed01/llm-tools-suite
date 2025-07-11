import streamlit as st
import os
import google.generativeai as genai
from tools import (
    blog_assistant,
    data_analyzer,
    sql_query_generator,
    document_summarizer,
    website_summarizer,
    code_explainer,
)
from tools.ui_helpers import tool_header

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    st.error(
        "**ERROR:** Gemini API key not found."
        " Please set it as an environment variable named `GEMINI_API_KEY`."
    )
    st.stop()

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

instruction = """
You are an AI assistant designed to provide professional, accurate information.
Your responses should be:
- Formal, concise, and helpful
- Free from bias and ambiguity
- Always grammatically correct
"""

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[
        {"role": "user", "parts": [instruction]},
        {"role": "model", "parts": ["Understood. I'm ready to assist you."]},
    ])
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I'm your AI assistant. How can I help you today?"
    })

TOOLS = {
    "AI Assistant": {
        "icon": "🧠",
        "name": "AI Assistant",
        "function": None,
        "description": "Chat with a professional AI assistant."
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
    "Code Explainer": {
        "icon": "🔍",
        "name": "Code Explainer",
        "function": code_explainer.code_explainer_app,
        "description": "Understand code with AI-powered step-by-step explanations."
    }
}

st.set_page_config(
    page_title="LLM Tools Suite",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# LLM Tools Suite\nA collection of AI-powered tools for productivity.",
        'Report a Bug': "https://www.google.com/search?q=llm+tools+suite+bug",
        'Get Help': "https://www.google.com/search?q=llm+tools+suite+help"
    }
)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("🛠️ LLM Tools Suite")
    st.markdown("---")

    tool_options = [f"{v['icon']} {k}" for k, v in TOOLS.items()]
    selected_tool_display = st.radio("Select a Tool:", tool_options, index=0)

    st.markdown("---")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    app_url = "/"
    st.markdown(f"""
        <a href="{app_url}" target="_blank" style="
            display: inline-block;
            background-color: #f39c12;
            color: white;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            margin-top: 10px;">
            Start New Chat
        </a>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("Choose a tool from the list above to get started!")

# --- Tool Selection ---
selected_tool_name = selected_tool_display.split(" ", 1)[1]
selected_tool = TOOLS[selected_tool_name]

if selected_tool_name == "AI Assistant":
    st.title("🧠 AI Assistant")
    st.markdown("I'm here to assist you professionally. Ask your question below.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Thinking..."):
            try:
                chunks = st.session_state.chat_session.send_message(user_input, stream=True)
                full_response = ""
                with st.chat_message("assistant"):
                    msg_placeholder = st.empty()
                    for chunk in chunks:
                        full_response += chunk.text
                        msg_placeholder.markdown(full_response + "▌")
                    msg_placeholder.markdown(full_response)

                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"An error occurred: {e}")

    if st.session_state.messages:
        def chat_history_text():
            return "\n\n".join(
                f"{'You' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                for m in st.session_state.messages
            )

        st.download_button(
            label="Download Chat",
            data=chat_history_text(),
            file_name="chat_history.txt",
            mime="text/plain"
        )
else:
    tool_header(selected_tool_name, selected_tool["description"], selected_tool["icon"])
    selected_tool["function"]()
