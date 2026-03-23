import streamlit as st
from groq import Groq
import os

# Page setup
st.set_page_config(page_title="Russian Transcriber", page_icon="🎙️")
st.title("🎙️ Russian Audio Transcriber")
st.markdown("Upload an audio file (up to 25MB) to get a Russian transcript.")

# Initialize Groq Client (using Secrets later)
api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("Please add your GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

uploaded_file = st.file_uploader("Upload Audio", type=["mp3", "wav", "m4a", "flac"])

if uploaded_file:
    # Check file size (Groq limit is 25MB)
    file_size_mb = uploaded_file.size / (1024 * 1024)
    
    if file_size_mb > 25:
        st.error(f"File too large ({file_size_mb:.1f}MB). Please upload a file under 25MB.")
    else:
        if st.button("Transcribe Now"):
            with st.spinner("Transcribing... (usually takes 5-10 seconds)"):
                try:
                    # Specific call for Russian
                    transcription = client.audio.transcriptions.create(
                        file=(uploaded_file.name, uploaded_file.read()),
                        model="whisper-large-v3",
                        language="ru",  # Forces Russian for better accuracy
                        response_format="text"
                    )
                    
                    st.success("Done!")
                    st.text_area("Transcript:", value=transcription, height=300)
                    
                    # Download button
                    st.download_button("Download Text", transcription, file_name="transcript.txt")
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")