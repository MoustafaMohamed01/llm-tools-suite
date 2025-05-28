import streamlit as st
from .document_summarizer_utils import summerizer

def document_summarizer_app():
    st.write('Summarize your PDF or Word files in just a few seconds...')
    st.divider()

    doc_file = st.file_uploader('Upload your PDF or Word Document...', type=['pdf', 'docx'], key="doc_summarizer_uploader")
    submit = st.button('Generate Summary', type="primary")

    if submit:
        if doc_file is not None:
            with st.spinner("Generating summary... This might take a moment."):
                response = summerizer(doc_file)

            st.subheader('Summary of file:')
            st.write(response)
        else:
            st.warning("Please upload a PDF or Word document first.")
