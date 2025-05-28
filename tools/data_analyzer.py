import streamlit as st
import pandas as pd
import google.generativeai as genai
from api_key import GEMINI_API_KEY

def data_analyzer_app():
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    st.write("Upload your CSV and ask questions about it.")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.subheader("Data Preview")
        st.dataframe(df.head())

        column_names = ", ".join(df.columns)

        if "chat_history_data_analyzer" not in st.session_state:
            st.session_state.chat_history_data_analyzer = []

        if st.session_state.chat_history_data_analyzer:
            st.subheader("Previous Q&A")
            for i, (q, a) in enumerate(st.session_state.chat_history_data_analyzer):
                st.markdown(f"**Q{i+1}:** {q}")
                st.markdown(f"**A{i+1}:** {a}")
                st.markdown("---")

        user_query = st.text_input("Ask a question about your data", key="data_analyzer_query")

        if user_query:
            with st.spinner("Thinking..."):
                csv_sample = df.to_csv(index=False)
                prompt = (
                    f"The dataset has the following columns: {column_names}.\n"
                    f"Here are the rows:\n{csv_sample}\n"
                    f"Now answer this question: {user_query}"
                )
                try:
                    response = model.generate_content(prompt)
                    answer_text = response.text
                    st.subheader("Answer")
                    st.write(answer_text)

                    st.session_state.chat_history_data_analyzer.append((user_query, answer_text))
                except Exception as e:
                    st.error(f"Model error: {str(e)}")

