import streamlit as st
from groq import Groq
import streamlit.components.v1 as components

st.set_page_config(page_title="whisperfleet", page_icon="🎙️")

# CSS для глубокой кастомизации интерфейса
st.markdown("""
    <style>
    /* 1. Прячем стандартный текст и кнопку внутри загрузчика */
    [data-testid="stFileUploader"] section button { display: none; }
    [data-testid="stFileUploader"] section div[data-testid="stMarkdownContainer"] { display: none; }
    
    /* 2. Вставляем твой текст (1) вместо (2) прямо внутрь рамки */
    [data-testid="stFileUploader"] section::before {
        content: "Кидай файл сюда или нажми для выбора на диске";
        display: block;
        text-align: center;
        color: #E0E0E0;
        font-size: 1.1rem;
        padding: 40px 20px;
        cursor: pointer;
    }

    /* 3. Убираем лишние отступы у заголовка и инфо-текста */
    .stApp { background-color: #0E1117; }
    .small-info {
        font-size: 0.8rem;
        color: #666;
        margin-bottom: 20px;
    }
    
    /* Убираем заголовок "Текст:" у поля */
    [data-testid="stTextArea"] label { display: none; }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ whisperfleet")
st.markdown('<p class="small-info">mp3, wav, m4a, flac до 25MB</p>', unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Загрузчик без внешнего лейбла (он теперь внутри через CSS)
uploaded_file = st.file_uploader("", type=["mp3", "wav", "m4a", "flac"])

if uploaded_file:
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    if "last_file_id" not in st.session_state or st.session_state.last_file_id != file_id:
        with st.spinner(" "):
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

    if "transcript" in st.session_state:
        # Кнопка копирования через JavaScript
        copy_code = f"""
        <script>
        function copyToClipboard() {{
            const text = `{st.session_state.transcript}`;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.getElementById("copyBtn");
                btn.innerText = "Скопировано!";
                btn.style.backgroundColor = "#28a745";
            }});
        }}
        </script>
        <button id="copyBtn" onclick="copyToClipboard()" style="
            width: 100%;
            background-color: #ff4b4b;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            margin-bottom: 10px;
        ">В буфер</button>
        """
        components.html(copy_code, height=50)

        # Поле с текстом (без подписи "Текст:")
        st.text_area("", value=st.session_state.transcript, height=350)
        
        # Скромная кнопка скачивания внизу
        st.download_button("Скачать .txt", st.session_state.transcript, file_name="text.txt")
