import streamlit as st
from tools import blog_assistant
from tools import data_analyzer
from tools import sql_query_generator
from tools import document_summarizer

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

TOOLS = {
    "Overview": {
        "icon": "🏠",
        "name": "Overview",
        "function": None,
        "description": "Explore the various AI tools available in this suite."
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
}

with st.sidebar:
    st.title("LLM Tools Suite")
    st.markdown("---")

    tool_options = [f"{tool_info['icon']} {tool_name}" for tool_name, tool_info in TOOLS.items()]
    selected_tool_display = st.radio("Select a Tool:", tool_options, index=0)

    st.markdown("---")
    st.info("Choose a tool from the list above to get started!")


selected_tool_name = selected_tool_display.split(' ', 1)[1]

selected_tool_info = TOOLS[selected_tool_name]
selected_tool_function = selected_tool_info["function"]
selected_tool_description = selected_tool_info["description"]

with st.container():
    if selected_tool_name == "Overview":
        st.markdown(f"<h1 style='text-align: center; color: #4A90E2;'>Welcome to the LLM Tools Suite</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 1.2em;'>Your go to collection of AI-powered tools.</p>", unsafe_allow_html=True)
        st.markdown("---")

        st.subheader("What's Inside:")
        st.write("This suite brings together several AI-powered tools designed to help you with common tasks, all in one convenient place.")

        st.subheader("Explore Our Tools:")
        tool_items = [tool_info for tool_name, tool_info in TOOLS.items() if tool_name != "Overview"]

        cols = st.columns(2)

        for i, tool_info in enumerate(tool_items):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"**{tool_info['icon']} {tool_info['name']}**")
                    st.write(tool_info['description'])
                    st.markdown(f"_(Select '{tool_info['icon']} {tool_info['name']}' in the sidebar to use this tool.)_")

        st.markdown("---")
        st.subheader("How to Use:")
        st.markdown("""
        1.  **Select a Tool:** Choose the function you need from the sidebar.
        2.  **Provide Input:** Follow the on-screen instructions to enter your data or query.
        3.  **Get Results:** The AI will process your request and display the output.
        """)

    else:
        st.title(f"{selected_tool_info['icon']} {selected_tool_name}")
        st.markdown(f"**{selected_tool_description}**")
        st.markdown("---")

        selected_tool_function()
