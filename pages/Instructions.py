import streamlit as st

st.set_page_config(
    page_title="Transcription System",
    page_icon="🧐",
    layout="wide",
)

with open("About.md", "r") as f:
    st.write(f.read())
