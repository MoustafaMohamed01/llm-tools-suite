import streamlit as st
from .document_summarizer_utils import summerizer

def document_summarizer_app():
    st.write('Summarize your PDF or Word files efficiently.')
    st.markdown("---")

    doc_file = st.file_uploader('Upload your PDF or Word Document...', type=['pdf', 'docx'], key="doc_summarizer_uploader")
    
    if 'doc_summary_output' not in st.session_state:
        st.session_state.doc_summary_output = ""

    submit = st.button('Generate Summary', type="primary")

    if submit:
        if doc_file is not None:
            with st.spinner("Analyzing document and generating summary... This might take a moment."):
                response = summerizer(doc_file)
            
            if response:
                st.subheader('Generated Summary:')
                st.info(response)
                st.session_state.doc_summary_output = response
            else:
                st.warning("Could not generate a summary. Please check the document content or try again.")
                st.session_state.doc_summary_output = ""
        else:
            st.warning("Please upload a PDF or Word document to begin summarization.")

    if st.session_state.doc_summary_output:
        st.download_button(
            label="Download Summary as Text",
            data=st.session_state.doc_summary_output,
            file_name="document_summary.txt",
            mime="text/plain",
            help="Click to download the generated summary as a plain text file."
        )
