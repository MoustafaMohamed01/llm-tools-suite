import streamlit as st
import google.generativeai as genai
import os # Import the os module

def sql_query_generator_app():
    # Get the API key from environment variables
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        st.error(
            "**ERROR:** Gemini API key not found for SQL Query Generator."
            " Please set it as an environment variable named `GEMINI_API_KEY` "
            "(e.g., in Streamlit Cloud secrets, Heroku config vars, or your local shell)."
        )
        st.stop() # Stop the app if the API key is not set

    genai.configure(api_key=gemini_api_key)
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        st.error(f"Failed to initialize Gemini model for SQL Query Generator: {e}. Please check your API key and try again.")
        st.stop()


    st.markdown(
        """
        <div style='text-align: center;'>
            <h3>I can generate SQL queries for you!</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---") # Add a separator for better visual structure

    text_input = st.text_area('Enter your Query description here...', key="sql_desc_input")
    database_context = st.text_area('Optional: Provide database schema or context (e.g., table names, columns)...', key="sql_db_context")
    dialect = st.selectbox('Optional: Specify SQL dialect', ['Generic SQL', 'PostgreSQL', 'MySQL', 'SQLite'], key="sql_dialect_select")

    submit = st.button('Generate SQL Query', type="primary")

    if submit:
        if not text_input:
            st.warning("Please enter a query description to generate the SQL query.")
            return

        with st.spinner('Generating SQL Query...'):
            try:
                template = f"""
                    Create a SQL query snippet based on the following description:
                    ```
                    {text_input}
                    ```
                    {'considering the following database context: ' + database_context if database_context else ''}
                    {'Ensure the query is compatible with ' + dialect + '.' if dialect != 'Generic SQL' else ''}
                    Provide only the SQL query, without any additional explanations or markdown code block delimiters.
                    """
                response = model.generate_content(template)
                sql_query = response.text.strip() # Removed specific stripping, let model handle it
                
                # It's better to tell the model to not include code blocks if you only want the code.
                # But if it does, ensure it's removed:
                if sql_query.startswith("```sql"):
                    sql_query = sql_query.lstrip("```sql").rstrip("```").strip()
                elif sql_query.startswith("```"): # For generic code blocks
                    sql_query = sql_query.lstrip("```").rstrip("```").strip()


                expected_output_prompt = f"""
                    What would be a plausible sample tabular response for this SQL Query snippet:
                    ```sql
                    {sql_query}
                    ```
                    Provide a concise sample tabular response formatted as a Markdown table, with no additional explanation or introductory text.
                    """
                output_response = model.generate_content(expected_output_prompt)
                output = output_response.text.strip()

                explanation_prompt = f"""
                    Explain this SQL Query in a concise manner:
                    ```sql
                    {sql_query}
                    ```
                    """
                explanation_response = model.generate_content(explanation_prompt)
                explanation = explanation_response.text.strip()

                with st.container():
                    st.success('SQL Query Generated Successfully!')
                    st.subheader('Generated SQL Query:')
                    st.code(sql_query, language='sql')

                    st.subheader('Expected Output:')
                    st.markdown(output) # No need for triple backticks if output is already markdown table

                    st.subheader('Explanation:')
                    st.markdown(explanation)
                
                # Download button
                full_output_for_download = (
                    f"SQL Query:\n```sql\n{sql_query}\n```\n\n"
                    f"Expected Output:\n{output}\n\n"
                    f"Explanation:\n{explanation}"
                )
                st.download_button(
                    label="Download SQL & Explanation",
                    data=full_output_for_download,
                    file_name="sql_query_details.md",
                    mime="text/markdown",
                    help="Download the generated SQL query, its expected output, and explanation."
                )


            except Exception as e:
                st.error(f"An error occurred during SQL query generation: {e}. Please try again.")
