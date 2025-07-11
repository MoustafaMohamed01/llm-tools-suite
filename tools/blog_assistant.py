import streamlit as st
import os
import google.generativeai as genai

def blog_assistant_app():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        st.error(
            "**ERROR:** Gemini API key not found for Blog Assistant. "
            "Please set it as an environment variable named `GEMINI_API_KEY` "
            "(e.g., in Streamlit Cloud secrets, Heroku config vars, or your local shell)."
        )
        st.stop()
    genai.configure(api_key=gemini_api_key)

    generation_config = {
        'temperature': 0.9,
        'top_p': 1,
        'top_k': 1,
        'max_output_tokens': 2048,
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    try:
        model = genai.GenerativeModel(model_name='gemini-2.0-flash',
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)
    except Exception as e:
        st.error(f"Failed to initialize Gemini model for Blog Assistant: {e}. Please check your API key and try again.")
        st.stop()


    st.subheader('Now you can craft perfect blogs with the help of AI')
    st.markdown("---")

    with st.container(border=True):
        st.subheader('Blog Configuration')
        st.write('Enter details of the blog you want to generate')

        blog_title = st.text_input('Blog Title', placeholder="e.g., The Future of AI in Healthcare", key="blog_title_input")
        keywords = st.text_input('Keywords (comma-separated)', placeholder="e.g., AI, healthcare, innovation, technology", key="keywords_input")
        num_words = st.slider('Number of words', min_value=200, max_value=2500, step=250, value=750, key="num_words_slider")

        prompt_parts = [f"""
        Generate a comprehensive, well-structured, and engaging blog post.
        **Title:** "{blog_title}"
        **Keywords:** "{keywords}" (Integrate these naturally throughout the content)
        **Tone:** Professional yet accessible, suitable for a broad audience.
        **Structure:** Include a captivating introduction, informative body paragraphs with clear headings/subheadings, and a concise conclusion (with a call to action if appropriate).
        **Word Count:** Approximately {num_words} words.
        """
        ]

        submit_button = st.button('Generate Blog', type="primary")

    if submit_button:
        if not blog_title or not keywords:
            st.warning("Please provide a **Blog Title** and **Keywords** to generate the blog.")
            return

        with st.spinner('Generating blog post...'):
            try:
                response = model.generate_content(prompt_parts)
                generated_text = response.text
                st.subheader("Generated Blog Post:")
                st.markdown(generated_text)

                if generated_text:
                    st.download_button(
                        label="Download as Markdown",
                        data=generated_text,
                        file_name=f"{blog_title.replace(' ', '_').strip() or 'generated_blog'}.md",
                        mime="text/markdown",
                    )
            except Exception as e:
                st.error(f"An error occurred during blog post generation: {e}. Please try again.")
