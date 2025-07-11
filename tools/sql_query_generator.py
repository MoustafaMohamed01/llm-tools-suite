import streamlit as st
import google.generativeai as genai
import os

def sql_query_generator_app():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        st.error(
            "**ERROR:** Gemini API key not found for SQL Query Generator. "
            "Please set it as an environment variable named `GEMINI_API_KEY` "
            "(e.g., in Streamlit Cloud secrets, Heroku config vars, or your local shell)."
        )
        st.stop()
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
    st.markdown("---")

    with st.container(border=True):
        st.subheader("Query Details")
        text_input = st.text_area(
            'Describe the SQL query you need (e.g., "Select all users from the '
            'users table who registered after 2023-01-01 and order by registration date").',
            key="sql_desc_input", height=100
        )
        database_context = st.text_area(
            'Optional: Provide database schema or context (e.g., table names, columns, relationships). '
            'This helps generate more accurate queries. Example: "Tables: users (id, name, email, registration_date), products (id, name, price, category)"',
            key="sql_db_context", height=100
        )
        dialect = st.selectbox(
            'Optional: Specify SQL dialect',
            ['Generic SQL', 'PostgreSQL', 'MySQL', 'SQLite', 'SQL Server', 'Oracle'],
            key="sql_dialect_select"
        )

        submit = st.button('Generate SQL Query', type="primary")

    if submit:
        if not text_input:
            st.warning("Please enter a **query description** to generate the SQL query.")
            return

        with st.spinner('Generating SQL Query...'):
            try:
                sql_template = f"""
                Generate a {dialect} SQL query based on the following description:
                Description: ```{text_input}```
                {'Database Context: ' + database_context if database_context else ''}
                Provide only the SQL query as a raw string, without any additional explanations, markdown code block delimiters, or introductory/concluding remarks.
                """
                sql_response = model.generate_content(sql_template)
                sql_query = sql_response.text.strip()

                if sql_query.startswith("```sql"):
                    sql_query = sql_query[len("```sql"):].strip()
                if sql_query.endswith("```"):
                    sql_query = sql_query[:-len("```")].strip()
                elif sql_query.startswith("```"):
                    sql_query = sql_query[len("```"):].strip()
                if sql_query.endswith("```"):
                    sql_query = sql_query[:-len("```")].strip()

                expected_output_prompt = f"""
                Given the following SQL Query:
                ```sql
                {sql_query}
                ```
                What would be a plausible sample tabular response?
                Provide a concise sample tabular response formatted as a Markdown table, with no additional explanation or introductory text.
                If the query is for DDL/DML (e.g., CREATE, INSERT, UPDATE, DELETE), state "No direct tabular output for this type of query."
                """
                output_response = model.generate_content(expected_output_prompt)
                output = output_response.text.strip()

                explanation_prompt = f"""
                Explain the following SQL Query concisely and professionally:
                ```sql
                {sql_query}
                ```
                Focus on what the query does and its purpose.
                """
                explanation_response = model.generate_content(explanation_prompt)
                explanation = explanation_response.text.strip()

                st.markdown("---")
                with st.container(border=True):
                    st.success('SQL Query Generated Successfully!')
                    st.subheader('Generated SQL Query:')
                    st.code(sql_query, language='sql')

                    st.subheader('Expected Output:')
                    st.markdown(output)

                    st.subheader('Explanation:')
                    st.markdown(explanation)

                full_output_for_download = (
                    f"### Generated SQL Query:\n```sql\n{sql_query}\n```\n\n"
                    f"### Expected Output:\n{output}\n\n"
                    f"### Explanation:\n{explanation}"
                )
                st.download_button(
                    label="Download SQL Details",
                    data=full_output_for_download,
                    file_name="sql_query_details.md",
                    mime="text/markdown",
                    help="Download the generated SQL query, its expected output, and explanation in Markdown format."
                )

            except Exception as e:
                st.error(f"An error occurred during SQL query generation: {e}. Please try again.")
