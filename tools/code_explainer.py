import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def code_explainer_app():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        st.error(
            "**ERROR:** Gemini API key not found for Code Explainer. "
            "Please set it as an environment variable named `GEMINI_API_KEY` "
            "(e.g., in .env file, Streamlit secrets, or your shell environment)."
        )
        st.stop()

    genai.configure(api_key=gemini_api_key)

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        st.error(f"Failed to initialize Gemini model: {e}")
        st.stop()

    st.markdown("""
        <div style='text-align: center;'>
            <h3>Code Explainer</h3>
            <p>Get the full code snippet printed, plus a detailed overview and line-by-line explanation.</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

    language = st.selectbox("Select Code Language", ["Python", "JavaScript", "C++", "Java", "Other"])
    code_input = st.text_area("Paste your code here:", height=300)

    if st.button("Explain Code", type="primary"):
        if not code_input.strip():
            st.warning("Please paste some code to get an explanation.")
            return

        with st.spinner("Analyzing your code..."):
            try:
                prompt = f"""
                          You are a senior software engineer and code reviewer.

                          1. First, **print the entire {language} code snippet exactly as provided**, clearly labeled as 'Full Code:'.

                          2. Then provide a **comprehensive overview explanation** of what the entire code does.

                          3. Finally, give a **detailed, line-by-line explanation** of the code. For each line:
                             - Explain what the line does.
                             - Explain each key word, function, or syntax element.
                             - Use bullet points or markdown formatting for clarity.
                             - Explain context if part of a block (function, loop, condition).
                             - Write lines in code bar.

                          Here is the code:
                          ```

                          {code_input}

                          ```


                          Start with the full code, then overview, then line-by-line explanation.
                """

                response = model.generate_content(prompt)
                explanation = response.text.strip()

                st.subheader("Code Explanation:")
                st.markdown(explanation)

                st.download_button(
                    label="Download Explanation",
                    data=explanation,
                    file_name="code_explanation.md",
                    mime="text/markdown",
                    help="Download the full code explanation."
                )

            except Exception as e:
                st.error(f"An error occurred while explaining the code: {e}")
