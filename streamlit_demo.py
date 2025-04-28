import streamlit as st
st.title("Streamlit Demo")
st.markdown("This is a simple Streamlit app to demonstrate the use of Streamlit with")
code = """
def hello_world():
    return "Hello, World!"

    """
st.code(code, language='python')
st.write("You can use Streamlit to create interactive web applications easily.")