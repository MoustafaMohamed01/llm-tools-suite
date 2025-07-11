import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

def data_analyzer_app():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        st.error(
            "**ERROR:** Gemini API key not found for AI CSV Analyzer. "
            "Please set it as an environment variable named `GEMINI_API_KEY` "
            "(e.g., in Streamlit Cloud secrets, Heroku config vars, or your local shell)."
        )
        st.stop()
    genai.configure(api_key=gemini_api_key)

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
    except Exception as e:
        st.error(f"Failed to initialize Gemini model for AI CSV Analyzer: {e}. Please check your API key and try again.")
        st.stop()


    st.write("Upload your CSV and ask questions about it.")
    st.markdown("---")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], key="data_analyzer_uploader")

    if "chat_history_data_analyzer" not in st.session_state:
        st.session_state.chat_history_data_analyzer = []
    if "data_analyzer_df" not in st.session_state:
        st.session_state.data_analyzer_df = None

    if uploaded_file is not None and st.session_state.data_analyzer_df is None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.data_analyzer_df = df
            st.success("CSV file uploaded and loaded successfully!")
        except Exception as e:
            st.error(f"Error reading CSV file: {e}. Please ensure it's a valid CSV.")
            st.session_state.data_analyzer_df = None
            st.session_state.chat_history_data_analyzer = []
            uploaded_file = None

    df = st.session_state.data_analyzer_df

    if df is not None:
        st.subheader("Data Preview")
        st.dataframe(df.head())
        st.write(f"**Shape:** {df.shape[0]} rows, {df.shape[1]} columns")

        column_names = ", ".join(df.columns)

        st.markdown("---")
        st.subheader("Ask a Question")

        if st.session_state.chat_history_data_analyzer:
            for i, (q, a) in enumerate(st.session_state.chat_history_data_analyzer):
                with st.chat_message("user"):
                    st.markdown(q)
                with st.chat_message("assistant"):
                    st.markdown(a)

        user_query = st.chat_input("E.g., What are the average sales per region? Which column has the most missing values?", key="data_analyzer_query")

        if user_query:
            st.session_state.chat_history_data_analyzer.append((user_query, "")) # Add user query to history

            with st.chat_message("user"):
                st.markdown(user_query)

            with st.spinner("Analyzing data and generating answer..."):
                csv_sample = df.to_csv(index=False)[:5000]

                prompt = (
                    f"You are an expert data analysis assistant. "
                    f"The user has provided a CSV dataset. "
                    f"The dataset has the following columns: **{column_names}**.\n"
                    f"Here is a small sample of the CSV data:\n```csv\n{csv_sample}\n```\n"
                    f"Please answer the following question about the data professionally, concisely, "
                    f"and provide actionable insights or relevant statistics if applicable. "
                    f"If a specific column is mentioned, assume it exists. If you need to perform calculations, briefly describe them.\n\n"
                    f"**Question:** {user_query}"
                )
                try:
                    response = model.generate_content(prompt)
                    answer_text = response.text
                    with st.chat_message("assistant"):
                        st.markdown(answer_text)
                    st.session_state.chat_history_data_analyzer[-1] = (user_query, answer_text)

                except Exception as e:
                    st.error(f"An error occurred while generating the answer: {str(e)}. Please try rephrasing your question or check the data.")
                    st.session_state.chat_history_data_analyzer[-1] = (user_query, f"Error: {str(e)}")

        st.markdown("---")
        if st.button("Clear Data & Chat", key="clear_data_chat"):
            st.session_state.data_analyzer_df = None
            st.session_state.chat_history_data_analyzer = []
            st.success("CSV data and chat history cleared!")
            st.rerun()
    else:
        st.info("Please upload a CSV file to start analyzing your data.")
