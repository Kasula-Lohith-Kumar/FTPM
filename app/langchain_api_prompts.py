import os
import re
import json
import tempfile
import tiktoken
import streamlit as st
from app import secrets
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
from langchain_community.vectorstores import FAISS


# --- Initialize buffer ---
if "buffer" not in st.session_state:
    st.session_state.buffer = []

# --- Initialize model ---
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    api_key=secrets.get_openai_key(),
    temperature=0.7  # adjust as needed
    )

client = OpenAI(api_key=secrets.get_openai_key())



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

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0
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

    response = llm.invoke(messages)
    return response.content


def process_text_data(file_path):

    loader = TextLoader(file_path, encoding="utf-8")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=60,
        separators=["\n\n", "\n"]
    )

    splits = text_splitter.split_documents(loader.load())
    return splits


def faiss_db(splits):

    embedding = OpenAIEmbeddings(api_key=secrets.get_openai_key())

    db = FAISS.from_documents(splits, embedding)
    return db

def text_retraivalQA(combined_text, query):

    # Step 1: Split text (your existing helper)
    text_splits = process_text_data(combined_text)

    # Step 2: Build vector DB
    database = faiss_db(text_splits)
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