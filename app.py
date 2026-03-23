import streamlit as st
from groq import Groq

# Page setup - minimalist style
st.set_page_config(page_title="whisperfleet", page_icon="🎙️")
st.title("🎙️ whisperfleet")

# Grab the key from secrets
api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("Missing GROQ_API_KEY in Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# The Russian-labeled uploader
uploaded_file = st.file_uploader(
    "Кидай файл сюда или нажми для выбора на диске", 
    type=["mp3", "wav", "m4a", "flac"]
)

if uploaded_file:
    # Check file size (Groq hard limit)
    file_size_mb = uploaded_file.size / (1024 * 1024)
    
    if file_size_mb > 25:
        st.error(f"Файл слишком большой ({file_size_mb:.1f}MB). Лимит — 25MB.")
    else:
        # Only transcribe if we haven't already processed this specific file
        # This saves tokens and time
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        
        if "last_file_id" not in st.session_state or st.session_state.last_file_id != file_id:
            with st.spinner("Распознаю голос..."):
                try:
                    transcription = client.audio.transcriptions.create(
                        file=(uploaded_file.name, uploaded_file.read()),
                        model="whisper-large-v3",
                        language="ru",
                        response_format="text"
                    )
                    st.session_state.transcript = transcription
                    st.session_state.last_file_id = file_id
                except Exception as e:
                    st.error(f"Ошибка: {e}")
                    st.stop()

        # Display result
        st.success("Готово")
        st.text_area("Текст:", value=st.session_state.transcript, height=400)
        
        st.download_button(
            label="Скачать .txt",
            data=st.session_state.transcript,
            file_name=f"{uploaded_file.name}.txt",
            mime="text/plain"
        )
