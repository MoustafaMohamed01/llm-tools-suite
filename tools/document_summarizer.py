import streamlit as st
from .document_summarizer_utils import summerizer

def document_summarizer_app():
    st.write('Summarize your PDF or Word files efficiently.')
    st.markdown("---")

    doc_file = st.file_uploader('Upload your PDF or Word Document (Max 20MB for optimal performance):', type=['pdf', 'docx'], key="doc_summarizer_uploader")

    if 'doc_summary_output' not in st.session_state:
        st.session_state.doc_summary_output = ""

    submit = st.button('Generate Summary', type="primary")

    if submit:
        if doc_file is not None:
            if doc_file.size > 20 * 1024 * 1024:
                st.warning("File size exceeds 20MB. Processing large documents might be slow or hit API limits.")

            with st.spinner("Analyzing document and generating summary... This might take a moment based on document size."):
                response = summerizer(doc_file)

            if response and not response.startswith("ERROR:"):
                st.subheader('Generated Summary:')
                st.info(response)
                st.session_state.doc_summary_output = response
            else:
                st.error(response if response.startswith("ERROR:") else "Could not generate a summary. Please check the document content or try again.")
                st.session_state.doc_summary_output = ""
        else:
            st.warning("Please upload a **PDF** or **Word document** to begin summarization.")

    if st.session_state.doc_summary_output:
        st.download_button(
            label="Download Summary as Text",
            data=st.session_state.doc_summary_output,
            file_name="document_summary.txt",
            mime="text/plain",
            help="Click to download the generated summary as a plain text file."
        )
