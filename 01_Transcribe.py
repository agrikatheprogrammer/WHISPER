# To run:
# streamlit run 01_Transcribe.py

import streamlit as st
from transcriber import Transcription

st.set_page_config(
    page_title="Transcription System",
    page_icon="📄",
    layout="wide",
)

input_option = st.sidebar.selectbox("Input Type", ["YouTube", "Link", "File"])

with st.sidebar.form("input_form"):
    if input_option == "YouTube":
        youtube_link = st.text_input("URL (video works fine)")
    elif input_option == "Link":
        link_url = st.text_input("URL (video works fine)")
    elif input_option == "File":
        uploaded_file = st.file_uploader("Please upload a valid video file", type=["mp4", "avi", "mov", "mkv", "mp3", "wav"])

    media_name = st.text_input("Audio/Video Name", "some_name")

    start_time = st.number_input("Start time for the media (sec)", min_value=0.0, step=1.0)
    media_duration = st.number_input("Duration (sec) - negative implies till the end", min_value=-1.0, step=1.0)

    whisper_model_choice = st.selectbox("Whisper model (accuracy)", options=["tiny", "base", "small", "medium", "large"], index=1)
    submit_transcription = st.form_submit_button(label="Transcribe!")

if submit_transcription:
    if not media_name:
        st.error("Please enter a name for the audio/video")
    if input_option == "YouTube":
        if youtube_link and youtube_link.startswith("http"):
            st.session_state.transcription = Transcription(media_name, youtube_link, "youtube", start_time, media_duration)
        else:
            st.error("Please enter a valid YouTube URL")
    elif input_option == "Link":
        if link_url and link_url.startswith("http"):
            st.session_state.transcription = Transcription(media_name, link_url, "link", start_time, media_duration)
        else:
            st.error("Please enter a valid URL")
    elif input_option == "File":
        if uploaded_file:
            st.session_state.transcription = Transcription(media_name, uploaded_file, "file", start_time, media_duration)
        else:
            st.error("Please upload a file")

    # Perform transcription and store it in session state
    st.session_state.transcription.transcribe()

if "transcription" in st.session_state:
    transcription_col, media_col = st.columns(2, gap="large")

    transcription_col.markdown("#### Trimmed Audio")
    with open(st.session_state.transcription.audio_path, "rb") as f:
        transcription_col.audio(f.read())
    transcription_col.markdown("---")
    transcription_col.markdown(f"#### Transcription (Whisper Model - `{whisper_model_choice}`)")

    raw_output_expander = transcription_col.expander("Raw Output")
    raw_output_expander.write(st.session_state.transcription.raw_output)

    transcription_col.markdown(f"##### Language: `{st.session_state.transcription.language}`")

    for segment in st.session_state.transcription.segments:
        transcription_col.markdown(
            f"""[{round(segment["start"], 1)} - {round(segment["end"], 1)}] - {segment["text"]}"""
        )

    media_col.markdown("#### Original Audio")
    with open(st.session_state.transcription.og_audio_path, "rb") as f:
        media_col.audio(f.read())
    if input_option == "YouTube":
        media_col.markdown("---")
        media_col.markdown("#### Original YouTube Video")
        media_col.video(st.session_state.transcription.source)
else:
    with open("About.md", "r") as f:
        st.write(f.read())
