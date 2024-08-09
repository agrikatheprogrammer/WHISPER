import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Transcription System",
    page_icon="📄",
    layout="wide",
)

if "transcription" in st.session_state:
    with st.sidebar.form("summary_form"):
        model = st.text_input("Huggingface model name", "facebook/bart-large-cnn")
        min_length = st.number_input("Minimum length", min_value=25, max_value=250, value=50)
        max_length = st.number_input("Max length", min_value=100, max_value=5000, value=500, step=100)
        do_sample = st.checkbox("Sample", value=False)
        summarize = st.form_submit_button(label="Summarize!")

    if summarize:
        st.session_state.transcription.summarize()

    st.write("## Original Text")
    st.write(st.session_state.transcription.text)
    st.write("---")

    if st.session_state.transcription.summarized:
        st.write("## Summary")
        st.write(st.session_state.transcription.summary)
else:
    st.error("Please upload an audio file to get started")
