import streamlit as st
import google.generativeai as genai
from api_key import GEMINI_API_KEY

def sql_query_generator_app():
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')

    st.markdown(
        """
        <div style='text-align: center;'>
            <h3>I can generate SQL queries for you!</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    text_input = st.text_area('Enter your Query description here...', key="sql_desc_input")
    database_context = st.text_area('Optional: Provide database schema or context (e.g., table names, columns)...', key="sql_db_context")
    dialect = st.selectbox('Optional: Specify SQL dialect', ['Generic SQL', 'PostgreSQL', 'MySQL', 'SQLite'], key="sql_dialect_select")

    submit = st.button('Generate SQL Query', type="primary")

    if submit:
        if not text_input:
            st.warning("Please enter a query description.")
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
                    I just want the SQL query.
                    """
                response = model.generate_content(template)
                sql_query = response.text
                sql_query = sql_query.strip().lstrip('```sql').rstrip('```')

                expected_output_prompt = f"""
                    What would be the expected response of this SQL Query snippet:
                    ```sql
                    {sql_query}
                    ```
                    Provide a sample tabular response formatted as a Markdown table, with no additional explanation.
                    """
                output_response = model.generate_content(expected_output_prompt)
                output = output_response.text

                explanation_prompt = f"""
                    Explain this SQL Query:
                    ```sql
                    {sql_query}
                    ```
                    Please provide a concise explanation.
                    """
                explanation_response = model.generate_content(explanation_prompt)
                explanation = explanation_response.text

                with st.container():
                    st.success('SQL Query Generated Successfully! Here is your Query Below:')
                    st.code(sql_query, language='sql')

                    st.success('Expected Output of this SQL Query will be:')
                    st.markdown(f"```\n{output}\n```")

                    st.success('Explanation of this SQL Query:')
                    st.markdown(explanation)

            except Exception as e:
                st.error(f"An error occurred: {e}")
