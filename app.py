import streamlit as st
from groq import Groq
import streamlit.components.v1 as components
import json
import os

st.set_page_config(page_title="whisperfleet", page_icon="🎙️")

st.markdown("""
    <style>
    [data-testid="stFileUploader"] section button { display: none; }
    [data-testid="stFileUploader"] section div[data-testid="stMarkdownContainer"] { display: none; }
    
    [data-testid="stFileUploader"] section::before {
        content: "Кидай файл сюда или нажми для выбора на диске";
        display: block;
        text-align: center;
        color: #E0E0E0;
        font-size: 1.1rem;
        padding: 40px 20px;
        cursor: pointer;
    }

    .stApp { background-color: #0E1117; }
    .small-info {
        font-size: 0.8rem;
        color: #666;
        margin-bottom: 20px;
    }
    
    [data-testid="stTextArea"] label { display: none; }
    
    /* Slight adjustment to make the textarea blend better */
    .stTextArea textarea {
        font-size: 1rem;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ whisperfleet")
st.markdown('<p class="small-info">mp3, wav, m4a, flac до 25MB</p>', unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

uploaded_file = st.file_uploader("", type=["mp3", "wav", "m4a", "flac"])

if uploaded_file:
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    # Check if this is a new file drop
    if "last_file_id" not in st.session_state or st.session_state.last_file_id != file_id:
        # Clear the old transcript immediately so the UI doesn't look stalled
        st.session_state.pop("transcript", None) 
        st.session_state.last_file_id = file_id
        
        # An empty spinner feels broken. Added minimal text.
        with st.spinner("Расшифровываю..."):
            try:
                transcription = client.audio.transcriptions.create(
                    file=(uploaded_file.name, uploaded_file.read()),
                    model="whisper-large-v3",
                    language="ru",
                    response_format="text"
                )
                st.session_state.transcript = transcription
                st.rerun() # Force UI refresh to show text immediately
            except Exception as e:
                st.error(f"Ошибка: {e}")
                st.stop()

# Render text and actions if we have a transcript
if "transcript" in st.session_state:
    
    # Capture any edits the user makes in the text area
    edited_text = st.text_area("", value=st.session_state.transcript, height=350)
    
    # Group the actions horizontally to save vertical space
    col1, col2 = st.columns(2)
    
    with col1:
        # I'm always a bit conflicted about using JS inside Streamlit iframes for clipboard 
        # actions because strict browser security policies sometimes block it. But since it 
        # was working for you, I kept it. I used json.dumps to safely pass the multiline 
        # edited text into the JS without breaking the script with rogue quotes or newlines.
        safe_text = json.dumps(edited_text)
        
        copy_code = f"""
        <script>
        function copyToClipboard() {{
            const text = {safe_text};
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.getElementById("copyBtn");
                btn.innerText = "✓ Скопировано";
                btn.style.backgroundColor = "#28a745";
                btn.style.borderColor = "#28a745";
                btn.style.color = "white";
                
                setTimeout(() => {{
                    btn.innerText = "В буфер";
                    btn.style.backgroundColor = "transparent";
                    btn.style.borderColor = "#ff4b4b";
                    btn.style.color = "#ff4b4b";
                }}, 2000);
            }});
        }}
        </script>
        <button id="copyBtn" onclick="copyToClipboard()" style="
            width: 100%;
            background-color: transparent;
            color: #ff4b4b;
            border: 1px solid #ff4b4b;
            padding: 0.5rem 0.75rem;
            border-radius: 0.5rem;
            cursor: pointer;
            font-weight: 400;
            font-family: 'Source Sans Pro', sans-serif;
            font-size: 1rem;
            transition: all 0.2s;
        ">В буфер</button>
        """
        components.html(copy_code, height=60)

    with col2:
        # Dynamic filename so it doesn't overwrite a folder full of "text.txt"
        base_name = os.path.splitext(uploaded_file.name)[0]
        st.download_button(
            label="Скачать .txt", 
            data=edited_text, 
            file_name=f"{base_name}_transcript.txt",
            use_container_width=True
        )
