import streamlit as st
from groq import Groq

# Конфиг страницы
st.set_page_config(page_title="whisperfleet", page_icon="🎙️")

# CSS для кастомизации: прячем кнопку и стилизуем зону загрузки
st.markdown("""
    <style>
    /* Прячем стандартную кнопку 'Browse files' */
    section[data-testid="stFileUploader"] button {
        display: none;
    }
    /* Делаем текст внутри зоны чуть больше и центрируем */
    section[data-testid="stFileUploader"] label {
        font-size: 1.2rem;
        margin-bottom: 10px;
        color: #ff4b4b; /* Цвет можно поменять */
    }
    /* Инструкция про форматы и вес */
    .file-info {
        font-size: 0.85rem;
        color: #888;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ whisperfleet")

# API Key
api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("Missing GROQ_API_KEY in Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# Основной интерфейс
st.markdown('<p class="file-info">Поддерживаются mp3, wav, m4a, flac до 25MB</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Кидай файл сюда или нажми для выбора на диске", 
    type=["mp3", "wav", "m4a", "flac"],
    label_visibility="visible"
)

if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    
    if file_size_mb > 25:
        st.error(f"Файл слишком тяжелый ({file_size_mb:.1f}MB). Лимит — 25MB.")
    else:
        # Логика транскрибации с защитой от повторных запусков
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        
        if "last_file_id" not in st.session_state or st.session_state.last_file_id != file_id:
            with st.spinner("Слушаю..."):
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
                    st.error(f"Ошибка API: {e}")
                    st.stop()

        # Результат
        st.success("Готово")
        st.text_area("Текст:", value=st.session_state.transcript, height=400)
        
        st.download_button(
            label="Скачать .txt",
            data=st.session_state.transcript,
            file_name=f"{uploaded_file.name}.txt",
            mime="text/plain"
        )
