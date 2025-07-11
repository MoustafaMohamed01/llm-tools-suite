import streamlit as st

def tool_header(title, description=None, icon="🔧"):
    st.title(f"{icon} {title}")
    if description:
        st.markdown(f"**{description}**")
    st.markdown("---")
