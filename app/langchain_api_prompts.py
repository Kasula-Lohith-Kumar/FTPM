import os
import re
import json
import base64
# import faiss
import tempfile
import zipfile
import config
import streamlit as st
from pathlib import Path
import streamlit_secrets
from openai import OpenAI
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
import document_processor as dp


# --- Initialize buffer ---
if "buffer" not in st.session_state:
    st.session_state.buffer = []

# --- Initialize model ---
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    api_key=streamlit_secrets.get_openai_key(),
    temperature=0.7  # adjust as needed
    )

llm_embd = OpenAIEmbeddings(
    model="text-embedding-3-large",    # recommended
    api_key=streamlit_secrets.get_openai_key()
)


client = OpenAI(api_key=streamlit_secrets.get_openai_key())



def learning_material():
    # Prepare the prompt dynamically
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
    
def add_to_buffer(role, content):
    st.session_state.buffer.append({"role": role, "content": content})
    if len(st.session_state.buffer) > 10:
        st.session_state.buffer = st.session_state.buffer[-10:]   

def chat_bot():
    """
    Chat-based assistant using LangChain's ChatOpenAI.
    Uses Streamlit session_state for context memory.
    """

    # 🔹 Prepare the system prompt dynamically
    system_prompt = f"""
    You are a helpful assistant who is an expert in finance. 
    Help the user clarify their doubts.
    Politely ignore queries that are unrelated to finance — say something like 
    "Please stay on our current learning topic."
    Always respond in {st.session_state.language}, unless the user explicitly asks for another language.
    """

    # 🔹 Convert session_state.buffer → LangChain message objects
    messages = [SystemMessage(content=system_prompt)]
    for msg in st.session_state.buffer:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    # 🔹 Get the model's reply
    response = llm.invoke(messages)

    # 🔹 Extract content and update buffer
    reply = response.content
    add_to_buffer("assistant", reply)

    return reply

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

    response = llm_embd.invoke(messages)
    return response.content


def process_text_data(combined_text):

    with open(r'temp.txt', "w", encoding="utf-8") as f:
        f.write(combined_text)

    loader = TextLoader(r'temp.txt', encoding="utf-8")

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
    """
    Creates and returns a Chroma vector store from documents using OpenAI embeddings.
    
    Args:
        splits: A list of Document objects (from langchain or similar) to embed and store.
        
    Returns:
        A Chroma vector store object.
    """
    # Assuming 'secrets.get_openai_key()' is available and returns the key
    # In a typical setup, the key might be read from an environment variable automatically
    # by OpenAIEmbeddings, but we pass it explicitly here for consistency.
    # Note: Using 'from langchain_openai import OpenAIEmbeddings' is the modern approach.

    # Chroma.from_documents is the direct equivalent of FAISS.from_documents

    embd_path = os.path.join(tempfile.gettempdir(), config.PERSISTANT_PATH)

    if not os.path.exists(embd_path):
        os.makedirs(embd_path)

    db = Chroma.from_documents(
        documents = splits, 
        embedding_function = llm_embd,
        persist_directory = embd_path
    )

    try:
        db.persist()
        st.success("✅ Embeddings generated successfully!")
        st.info("✅ Chroma DB persisted successfully.")
        st.session_state.embeddings_generated = True
    
    except Exception as e:
        st.info(f"❌ Error while persisting Chroma DB: {e}")

    st.session_state.temp_embedding_path = embd_path
    
    return db

def text_retraivalQA(database, query):

    # Step 1: Split text (your existing helper)
    # text_splits = process_text_data(combined_text)

    # Step 2: Build vector DB
    # database = chroma_db(text_splits)
    # if save_chroma_embd(database):
    #     st.session_state.embeddings_generated = True
    #     st.success("✅ Embeddings generated successfully!")
    retriever = database.as_retriever()

    # Step 3: Prompt template
    template = """Use the following pieces of context to answer the question at the end.
                If you don't know the answer and don't find it in the given context,
                just say that you don't know. Don't try to make up an answer.

                {context}

                Question: {question}

                Helpful Answer:
                """
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    # Step 4: Build RetrievalQA manually using Runnable syntax
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | QA_CHAIN_PROMPT
        | llm
    )

    # Step 5: Invoke chain
    result = chain.invoke(query)

    return result

def save_embd(db, dst_file):
    os.makedirs(dst_file, exist_ok=True)
    temp_path = os.path.join(dst_file, 'data.faiss')
    faiss.write_index(db.index, temp_path) 


    

# def load_chroma_from_zip(zip_file):
#     # Create a temp folder
#     temp_dir = tempfile.mkdtemp()

#     # Extract ZIP
#     with zipfile.ZipFile(zip_file, "r") as z:
#         z.extractall(temp_dir)

#     # Find extracted folder (first subdir)
#     subdirs = [os.path.join(temp_dir, d) for d in os.listdir(temp_dir)]
#     persist_dir =  Path(subdirs[0])     # the actual chroma folder
#     # Load the Chroma DB
#     st.info(f'persist_dir : {str(persist_dir)}')
#     db_file = dp.list_dir_content(persist_dir)

#     # if file:
#     #     st.info(f"Found file : {file}, Loading....")
#     #     try:
#     #         with open(os.path.join(str(persist_dir),file), "rb") as f:
#     #             combined_text = base64.b64encode(f.read()).decode("utf-8")
#     #             st.success(f"✅ File : {file} Loaded Successfully!")
#     #     except Exception as e:
#     #         st.error(f"❌Failed to load file : {file} with exception {e}")

#     # st.session_state.temp_embedding_path = str(persist_dir)
#     # st.success(f"✅ Embeddings '{persist_dir.name}' uploaded successfully!")
#     # st.info("📄 Document upload disabled since embeddings are provided directly.")
    
#     return db_file

def load_chroma_from_zip(zip_file):

    # Create temporary directory
    temp_dir = tempfile.mkdtemp()

    # Extract ZIP
    with zipfile.ZipFile(zip_file, "r") as z:
        z.extractall(temp_dir)
    
    st.write("DEBUG: Extracted root:", temp_dir)
    for root, dirs, files in os.walk(temp_dir):
        st.write("DIR:", root)
        st.write("  Subdirs:", dirs)
        st.write("  Files:", files)

    # Scan all subdirectories
    dirs = [
        os.path.join(temp_dir, d)
        for d in os.listdir(temp_dir)
        if os.path.isdir(os.path.join(temp_dir, d))
    ]

    st.session_state.temp_embedding_path = None

    # Look for ANY file ending with .sqlite3
    for d in dirs:
        contents = os.listdir(d)
        sqlite_files = [f for f in contents if f.endswith(".sqlite3")]

        if sqlite_files:
            # Check Chroma required structure
            has_index = os.path.isdir(os.path.join(d, "index"))
            has_collections = os.path.isdir(os.path.join(d, "collections"))

            if has_index and has_collections:
                st.session_state.temp_embedding_path = d
                break

    if st.session_state.temp_embedding_path is None:
        raise FileNotFoundError(
            "No valid Chroma persist directory found (.sqlite3 + index + collections)."
        )

    st.info(f"Using persist_dir: {st.session_state.temp_embedding_path}")

    # Load embeddings
    embeddings = OpenAIEmbeddings(api_key=streamlit_secrets.get_openai_key())

    # Load Chroma DB
    db = Chroma(
        persist_directory=st.session_state.temp_embedding_path,
        embedding_function=embeddings
    )

    combined_text = None
    return combined_text, db

def zip_chroma_db(persist_dir, output_zip_path):
    persist_dir = Path(persist_dir)

    if not persist_dir.exists():
        raise FileNotFoundError(f"Persist directory not found: {persist_dir}")

    # Validate Chroma structure
    sqlite_files = [f for f in os.listdir(persist_dir) if f.endswith(".sqlite3")]
    index_dir = (persist_dir / "index").exists()
    collections_dir = (persist_dir / "collections").exists()

    if not sqlite_files:
        raise FileNotFoundError("No .sqlite3 file found in persist directory.")

    if not index_dir or not collections_dir:
        raise FileNotFoundError(
            "Chroma directory incomplete. It must include:\n"
            "- .sqlite3 file\n"
            "- index/\n"
            "- collections/"
        )

    # Create ZIP
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(persist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, persist_dir)
                zipf.write(file_path, arcname)

    print(f"Successfully created ZIP: {output_zip_path}")

    return output_zip_path