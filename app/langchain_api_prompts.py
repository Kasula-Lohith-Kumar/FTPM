import os
import re
import json
import base64
# import faiss
import shutil
import tempfile
import zipfile
import config
import streamlit as st
from pathlib import Path
import streamlit_secrets
from openai import OpenAI
from utils import buffer_u
from langchain_openai import ChatOpenAI
# from langchain_openai import OpenAITextToSpeech
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.document_loaders.parsers import OpenAIWhisperParser
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Chroma
from utils import document_processor as dp


# --- Initialize buffer ---
if "buffer" not in st.session_state:
    st.session_state.buffer = []


def learning_material():
    # Prepare the prompt dynamically
    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        api_key=streamlit_secrets.get_openai_key(),
        temperature=0.7  # adjust as needed
        )
    prompt = f"""
    You are a financial guide/teacher who provides detailed information 
    on the subtopic '{st.session_state.selected_topic[2]}' 
    of the main topic '{st.session_state.selected_topic[0]}' 
    in {st.session_state.language}, using layman terms.
    
    Write at least one page of content, starting directly with the explanation 
    (avoid phrases like "Here is" or "Certainly").  
    Use structured formatting (bullet points, tables, etc.) and keep it professional.
    """
    # Create the message and get the response
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def voice(text):
    """
    Generate text-to-speech audio for the given text and return raw audio bytes.
    """
    try:
        client = OpenAI(api_key=streamlit_secrets.get_openai_key())

        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text
        )

        # ✅ Extract raw audio bytes from the binary response
        audio_bytes = response.read()

        return audio_bytes

    except Exception as e:
        print(f"❌ Error generating voice: {e}")
        return None
    

def generate_quiz():
    """
    Generate a Python dictionary containing 5 MCQs on the selected subtopic,
    using LangChain's ChatOpenAI interface.
    """
    prompt = f"""
    Generate a Python dictionary containing 5 multiple-choice questions on the subtopic \
    '{st.session_state.selected_topic[2]}' of the main topic '{st.session_state.selected_topic[0]}' in '{st.session_state.language}'.
    
    Each question should have:
    - a 'question' key with the question text
    - an 'options' key containing a list of 4 possible answers
    - an 'answer' key containing the correct answer text (must match one of the options exactly)

    Return ONLY the valid JSON/Python dictionary. 
    Do NOT wrap it in a code block or include any explanations or extra text.
    """

    try:
        llm = ChatOpenAI(
            model="gpt-4.1-mini",
            api_key=streamlit_secrets.get_openai_key(),
            temperature=0.7  # adjust as needed
            )
        # Send the prompt
        response = llm.invoke([HumanMessage(content=prompt)])

        # Extract raw content
        raw_content = response.content

        # --- Clean Markdown fences ---
        clean_content = re.sub(
            r'^\s*```(?:python|json)?\s*|\s*```\s*$',
            '',
            raw_content,
            flags=re.MULTILINE
        ).strip()

        # --- Try to parse JSON ---
        try:
            quiz_data = json.loads(clean_content)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}. Attempting eval as fallback.")
            quiz_data = eval(clean_content)

        return quiz_data

    except Exception as e:
        print(f"❌ Error generating quiz: {e}")
        return None 

# def chat_bot():
#     """
#     Chat-based assistant using LangChain's ChatOpenAI.
#     Uses Streamlit session_state for context memory.
#     """

#     # 🔹 Prepare the system prompt dynamically
#     system_prompt = f"""
#     You are a helpful assistant who is an expert in finance. 
#     Help the user clarify their doubts.
#     Politely ignore queries that are unrelated to finance — say something like 
#     "Please stay on our current learning topic."
#     Always respond in {st.session_state.language}, unless the user explicitly asks for another language.
#     """

#     llm = ChatOpenAI(
#     model="gpt-4.1-mini",
#     api_key=streamlit_secrets.get_openai_key(),
#     temperature=0.7  # adjust as needed
#     )

#     # 🔹 Convert session_state.buffer → LangChain message objects
#     messages = [SystemMessage(content=system_prompt)]
#     for msg in st.session_state.buffer:
#         if msg["role"] == "user":
#             messages.append(HumanMessage(content=msg["content"]))
#         elif msg["role"] == "assistant":
#             messages.append(AIMessage(content=msg["content"]))

#     # 🔹 Get the model's reply
#     response = llm.invoke(messages)

#     # 🔹 Extract content and update buffer
#     reply = response.content
#     buffer_u.add_to_buffer("assistant", reply)

#     return reply

def chat_bot(user_input):
    system_prompt = f"""
    You are a helpful assistant who is an expert in finance. 
    Respond only to finance questions. Otherwise say: 'Please stay on the topic.'
    Always respond in {st.session_state.language}.
    """

    llm = ChatOpenAI(model="gpt-4.1-mini",
                     api_key=streamlit_secrets.get_openai_key(),
                     temperature=0.6)

    messages = [SystemMessage(content=system_prompt)]

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    if user_input:
        messages.append(HumanMessage(content=user_input))

    response = llm.invoke(messages)
    return response.content


def audio_transcription(audio_file):
    """
    Transcribes an uploaded/recorded audio file using LangChain's OpenAIWhisperParser.
    """

    # 🔹 1. Validate file
    if audio_file is None or audio_file.size == 0:
        raise ValueError("Empty or invalid audio input")

    # 🔹 2. Save uploaded file temporarily
    file_ext = os.path.splitext(audio_file.name)[-1] or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        temp_file.write(audio_file.read())
        temp_path = temp_file.name

    # 🔹 3. Double-check file size
    if os.path.getsize(temp_path) == 0:
        raise ValueError("Recorded file is empty")

    # 🔹 4. Initialize LangChain Whisper parser
    whisper = OpenAIWhisperParser(model="gpt-4o-mini-transcribe")  # or "whisper-1"

    # 🔹 5. Perform transcription using LangChain Runnable
    with open(temp_path, "rb") as f:
        transcription_text = whisper.invoke(f)

    # 🔹 6. Clean up
    os.remove(temp_path)

    return transcription_text


def describe_image(base64_image: str):
    """
    Uses OpenAI GPT-4o with LangChain to extract text from an image
    and return the extracted text plus a summary.
    """
    vision_model = ChatOpenAI(
        model="gpt-4o",
        api_key=streamlit_secrets.get_openai_key()
    )

    # Prepare messages
    messages = [
        SystemMessage(
            content=(
                "Your job is to extract all the information from the images, including the text. "
                "Extract all the text from the image without changing the order or structure of the information. "
                "Recheck if all the text has been extracted correctly and return in the same presentation "
                "and structure as present in the original image."
            )
        ),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": (
                        "extract ALL the text from the image in the same structure as present in the image. "
                        "and then after it summarise everything in brief, do not miss anything."
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    },
                },
            ]
        )
    ]

    response = vision_model.invoke(messages)
    return response.content


def process_text_data(combined_text):
    
    text_file = os.path.join(st.session_state.upload_temp_path, 
                 config.COMBINED_TEXT_FILE)

    with open(text_file, "w", encoding="utf-8") as f:
        f.write(combined_text)

    loader = TextLoader(text_file, encoding="utf-8")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=60,
        separators=["\n\n", "\n"]
    )

    splits = text_splitter.split_documents(loader.load())
    return splits


def faiss_db(splits):


    db = FAISS.from_documents(splits, llm_embd)
    return db



def chroma_db(splits):

    # -----------------------
    # 1. Create a fresh folder
    # -----------------------
    unique_folder = f"chroma_{next(tempfile._get_candidate_names())}"
    embd_path = os.path.join(st.session_state.upload_temp_path, unique_folder)

    # -----------------------
    # 2. Create embed model
    # -----------------------
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=streamlit_secrets.get_openai_key()
    )

    # -----------------------
    # 3. Build new DB
    # -----------------------
    db = Chroma.from_documents(
        documents=splits,
        embedding=embedding_model,
        persist_directory=embd_path
    )

    # -----------------------
    # 4. Persist safely
    # -----------------------
    try:
        db.persist()
        st.success(f"✅ Chroma DB created at {embd_path}")
    except Exception as e:
        st.error(f"❌ Error while persisting Chroma DB: {e}")

    # -----------------------
    # 5. Save references
    # -----------------------
    st.session_state.temp_embedding_path = embd_path
    st.session_state.chroma_database = db
    st.session_state.embeddings_generated = True

    return db


def text_retraivalQA(database, query):

    retriever = database.as_retriever()

    llm = ChatOpenAI(model="gpt-4o", temperature=0,
                     api_key=streamlit_secrets.get_openai_key())

    template = """Use the following pieces of context to answer the question at the end.
    If you don't know the answer, say you don't know.

    {context}

    Question: {question}

    Helpful Answer:"""

    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    # FIX: Include return of source documents
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | QA_CHAIN_PROMPT
        | llm
    )

    # Call the retriever separately
    docs = retriever.invoke(query)

    answer = chain.invoke(query)

    return {
        "answer": answer.content,
        "source_documents": docs
    }

def save_embd(db, dst_file):
    os.makedirs(dst_file, exist_ok=True)
    temp_path = os.path.join(dst_file, 'data.faiss')
    faiss.write_index(db.index, temp_path) 


def load_chroma_from_zip(zip_file):

    extract_path = config.EMBBED_EXRT_PATH
    # extract_path = temp_dir.name

    # Extract the zip
    with zipfile.ZipFile(zip_file, "r") as z:
        z.extractall(extract_path)

    st.write("DEBUG: Extracted:", extract_path)

    # ---- show directory structure to debug ----
    import subprocess
    tree_output = subprocess.getoutput(f"find {extract_path} -maxdepth 5 | sed 's|{extract_path}||'")
    st.code(tree_output, language="bash")

    # ---- Find chroma.sqlite3 anywhere ----
    sqlite_paths = []
    for root, dirs, files in os.walk(extract_path):
        if "chroma.sqlite3" in files:
            sqlite_paths.append(root)

    if not sqlite_paths:
        raise FileNotFoundError(
            "No chroma.sqlite3 found anywhere in the ZIP.\n"
            "This means your export does NOT contain a valid Chroma DB."
        )

    # Pick the folder that contains chroma.sqlite3
    persist_dir = sqlite_paths[0]
    st.success(f"Found chroma.sqlite3 at:\n{persist_dir}")

    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=streamlit_secrets.get_openai_key()
    )

    # ---- Load Chroma ----
    try:
        db = Chroma(
            persist_directory=persist_dir,
            embedding_function=embedding_model
        )
        st.success("Chroma DB loaded successfully!")
        return db

    except Exception as e:
        st.error("Chroma load failed")
        st.exception(e)
        return None

def zip_chroma_db(working_dir, output_zip_path):
    persist_dir = Path(st.session_state.temp_embedding_path)
    zip_folder_path = Path(working_dir)

    if not persist_dir.exists():
        raise FileNotFoundError(f"Persist directory not found: {persist_dir}")

    # --- List contents ---
    files = [f for f in os.listdir(persist_dir) if f.endswith(".sqlite3")]
    print(f'files : {files}')
    dirs = [d for d in os.listdir(persist_dir) if (persist_dir / d).is_dir()]
    print(f'dirs : {dirs}')

    # --- Validate ---
    if not files:
        raise FileNotFoundError("❌ No .sqlite3 database found in persist directory.")

    if len(dirs) == 0:
        raise FileNotFoundError(
            "❌ Chroma directory incomplete — expected at least one collection folder."
        )

    # --- Create ZIP ---
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _dirs, file_list in os.walk(zip_folder_path):
            for file in file_list:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, zip_folder_path)
                zipf.write(file_path, arcname)

    return output_zip_path