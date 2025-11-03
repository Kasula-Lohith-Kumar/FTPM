import os
import re
import json
import tempfile
import streamlit as st
from app import secrets
from langchain_openai import OpenAIWhisperParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.tools import OpenAITextToSpeech


# --- Initialize buffer ---
if "buffer" not in st.session_state:
    st.session_state.buffer = []

# --- Initialize model ---
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    api_key=secrets.get_openai_key(),
    temperature=0.7  # adjust as needed
    )



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
    Generate text-to-speech audio for the given text using LangChain.
    Returns raw audio bytes.
    """
    try:
        # Initialize the TTS tool from LangChain
        tts = OpenAITextToSpeech(
            model="gpt-4o-mini-tts",
            voice="alloy"
        )

        # Generate the audio bytes
        audio_bytes = tts.invoke(text)

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
        # Initialize LangChain LLM wrapper
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)

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

    # 🔹 Initialize the model
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)

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