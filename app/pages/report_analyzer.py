import os
import uuid
import config
import cv2
import streamlit as st
from utils import chatbot
from utils import buffer_u
from pages import fl_config
import langchain_api_prompts as lap
from utils import document_processor as dp

def run():
    # --- HIDE DEFAULT SIDEBAR ---
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
            section[data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
            .block-container {
                padding-left: 10rem;
                padding-right: 10rem;
                padding-top: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- PAGE SETUP ---
    st.set_page_config(page_title="Report Analyzer", page_icon="📊", layout="wide")

    # --- USERNAME HANDLING ---
    username = st.session_state.get("username", "Unknown User")

    st.markdown(f"""
        <h2 style="text-align:center;">📊 Welcome, <span style="color:#22c55e;">{username}</span>!</h2>
        <p style="text-align:center; font-size:17px;">Upload your company reports or embeddings below to begin analysis.</p>
        <hr style="margin:20px 0;">
    """, unsafe_allow_html=True)

    # --- SIDEBAR INFO ---
    st.sidebar.header("Navigation")
    st.sidebar.info("Use this page to upload your documents or vector embeddings for analysis.")

    # --- SESSION STATE INITIALIZATION ---
    st.session_state.setdefault("upload_mode", "📄 Upload Document")
    st.session_state.setdefault("embeddings_generated", False)
    st.session_state.setdefault("temp_embedding_path", None)
    st.session_state.setdefault("start_analysis", False)
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("language", "English")
    st.session_state.setdefault("upload_temp_path", None)

    # Center title
    st.markdown("<h4 style='text-align:center;'>Choose Upload Mode</h4>", unsafe_allow_html=True)

    # Create empty columns and place radio in the middle one
    col1, col2, col3 = st.columns([1,0.8,1])
    with col2:
        upload_mode = st.radio(
        "",
        ("📄 Upload Document", "🧠 Upload Embeddings"),
        horizontal=True
        )

    if st.session_state.upload_mode != upload_mode:
        st.session_state.start_analysis = False
        st.session_state.embeddings_generated = False
        st.session_state.chat_history = []
        st.session_state.combined_text = ''
        st.session_state.db_file_path = None
        st.session_state.chroma_database = None
        st.session_state.messages = []

    st.session_state.upload_mode = upload_mode

    if st.session_state.upload_temp_path == None:
        st.session_state.upload_temp_path = os.path.join(config.WORKING_DIR, str(uuid.uuid4()))

    # --- FILE UPLOAD SECTION ---
    if upload_mode == "📄 Upload Document":
        st.write("### Upload Your Document")
        uploaded_doc = st.file_uploader("Upload a PDF, DOCX, or TXT file", type=["pdf", "docx", "txt"])

        if uploaded_doc:
            if not os.path.exists(st.session_state.upload_temp_path):
                os.makedirs(st.session_state.upload_temp_path)
            temp_doc_path = os.path.join(st.session_state.upload_temp_path, uploaded_doc.name)
            print(f'temp_doc_path: {temp_doc_path}')
            with open(temp_doc_path, "wb") as f:
                f.write(uploaded_doc.getbuffer())
            st.success(f"✅ Document '{uploaded_doc.name}' uploaded successfully!")

            # Generate embeddings button
            if st.button("⚙️ Generate Embeddings"):
                # --- PLACE YOUR EMBEDDING LOGIC HERE ---
                st.session_state.combined_text = \
                    dp.extract_images_and_text_from_pdf(temp_doc_path)
                splits = lap.process_text_data(st.session_state.combined_text)
                st.session_state.chroma_database = lap.chroma_db(splits)
                st.session_state.embeddings_generated = True
                

        # --- If embeddings are generated ---
        if st.session_state.embeddings_generated:
            st.info(f"✅ Using generated embeddings: `{st.session_state.temp_embedding_path}`")
            zip_file = lap.zip_chroma_db(working_dir=st.session_state.upload_temp_path,
                              output_zip_path='chroma_db_export.zip')
            # Download embeddings button
            with open(zip_file, "rb") as file:
                st.download_button(
                    label="💾 Download Embeddings",
                    data=file,
                    file_name=zip_file,
                    mime="application/octet-stream"
                )

            # Start analysis button
            if st.button("🚀 Start Analysis"):
                st.session_state.start_analysis = True

    else:
        # --- Upload embeddings directly ---
        st.write("### Upload Your Embeddings")
        uploaded_embeddings = st.file_uploader("Upload your Chroma DB (.zip)", type=["zip"])
        if uploaded_embeddings:
            st.session_state.chroma_database = lap.load_chroma_from_zip(uploaded_embeddings)

            if st.button("🚀 Start Analysis"):
                st.session_state.start_analysis = True


    if st.session_state.start_analysis:
        # ---------- Render chat history (always run) ----------
        for msg in st.session_state.buffer:
            with st.chat_message(msg["role"]):
                if msg["type"] == "text":
                    st.markdown(msg["content"])
                elif msg["type"] == "image":
                    print(f'msg["type"] : {msg["type"]}')
                    if os.path.exists(msg["content"]):
                        img = cv2.imread(msg["content"])
                        if img is None:
                            st.warning(f"Unable to read image: {msg['content']}")
                        else:
                            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            st.image(img_rgb, use_container_width=True)
                    else:
                        st.warning(f"⚠️ Missing image: {msg['content']}")


        # ---------- Chat input (always last so it's at the bottom) ----------
        assistant = "💬 Interactive Report Analysis"
        lang_eng = fl_config.translations['English']  # your existing config
        user_input = chatbot.chat_buttons(lang_eng['chatbot_input'], assistant)

        if user_input:
            # get reply and optional image path from your pipeline
            response = lap.text_retraivalQA(st.session_state.chroma_database, user_input)
            print(f"response for test : {response}")
            # reply_text = response.get("answer", "")
            reply_text = response["source_documents"][0]
            print(f'reply_text : {reply_text}')
            dp.display_content(reply_text)
            
            # image_path = response.get("image")  # set this in text_retraivalQA if applicable

            # to debug, you can force an image path like:
            # image_path = "/mnt/data/046748b2-f144-4227-82fe-c1a812e37d80.png"

            # store in correct order and rerun
            # buffer_u.to_buffer_rag(user_input, reply_text, image_path)

    # --- FOOTER BUTTONS ---
    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])

    with col1:
        if st.button("🏠 Return to Dashboard"):
            st.session_state['page_status'] = 'welcome'
            del st.session_state.selected_option
            buffer_u.force_clear_buffer()
            st.switch_page("pages/welcome.py")

    with col2:
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.clear()
            st.success("You have been logged out.")
            st.session_state['page_status'] = 'login'
            buffer_u.force_clear_buffer()
            st.switch_page("pages/login.py")

# --- INITIALIZATION HANDLING ---
if 'page_status' not in st.session_state:
    st.session_state['page_status'] = 'login'
    st.switch_page("pages/login.py")

if 'username' not in st.session_state:
    st.session_state['username'] = None

if st.session_state.get('page_status') == 'report_analyzer':
    print(f"page state : {st.session_state['page_status']}")
    run()
