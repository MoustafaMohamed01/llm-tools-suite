import streamlit as st
import pandas as pd
import google.generativeai as genai
import os # Import the os module

def data_analyzer_app():
    # Get the API key from environment variables
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        st.error(
            "**ERROR:** Gemini API key not found for AI CSV Analyzer."
            " Please set it as an environment variable named `GEMINI_API_KEY` "
            "(e.g., in Streamlit Cloud secrets, Heroku config vars, or your local shell)."
        )
        st.stop() # Stop the app if the API key is not set

    genai.configure(api_key=gemini_api_key)
    
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
    except Exception as e:
        st.error(f"Failed to initialize Gemini model for AI CSV Analyzer: {e}. Please check your API key and try again.")
        st.stop()


    st.write("Upload your CSV and ask questions about it.")
    st.markdown("---")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.subheader("Data Preview")
            st.dataframe(df.head())

            column_names = ", ".join(df.columns)

            if "chat_history_data_analyzer" not in st.session_state:
                st.session_state.chat_history_data_analyzer = []

            # --- Display chat history ---
            if st.session_state.chat_history_data_analyzer:
                st.subheader("Previous Q&A")
                for i, (q, a) in enumerate(st.session_state.chat_history_data_analyzer):
                    st.markdown(f"**Q{i+1}:** {q}")
                    st.info(a) # Use st.info for answers for better visibility
                    st.markdown("---")

            user_query = st.text_input("Ask a question about your data", key="data_analyzer_query")

            if user_query:
                with st.spinner("Analyzing data..."):
                    # For larger CSVs, consider sending only head or a more concise schema + sample
                    # Sending entire CSV as text can hit token limits for large files
                    csv_sample = df.to_csv(index=False) 
                    
                    prompt = (
                        f"You are a data analysis assistant. "
                        f"The user has uploaded a CSV dataset. "
                        f"The dataset has the following columns: {column_names}.\n"
                        f"Here is a sample of the CSV data:\n```csv\n{csv_sample[:2000]}\n```\n" # Limiting sample to avoid token issues
                        f"Based on this data, please answer the following question professionally and concisely: {user_query}"
                    )
                    try:
                        response = model.generate_content(prompt)
                        answer_text = response.text
                        st.subheader("Answer")
                        st.write(answer_text)

                        st.session_state.chat_history_data_analyzer.append((user_query, answer_text))
                    except Exception as e:
                        st.error(f"An error occurred while generating the answer: {str(e)}. Please try rephrasing your question or check the data.")
            
        except Exception as e:
            st.error(f"Error reading CSV file: {e}. Please ensure it's a valid CSV.")
    else:
        st.info("Please upload a CSV file to start analyzing your data.")
