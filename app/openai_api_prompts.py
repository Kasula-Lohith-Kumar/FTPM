from app import app_config
from openai import OpenAI
import streamlit as st
import re
import json

client = OpenAI(api_key=app_config.key)

if "buffer" not in st.session_state:
    st.session_state.buffer = []

def learning_material():

    response = client.responses.create(model = 'gpt-4.1-mini', input=f"You are a financal guide/teacher \
                                                who Provides the detailed information on subtopic '{st.session_state.selected_topic[2]}' \
                                                of the main topic {st.session_state.selected_topic[0]} in {st.session_state.language} \
                                                in layman terms, provide atleast a page of content. \
                                                Start directly with the explanation — do not include phrases like ‘Here is’ or ‘Certainly’. \
                                                Provide topic conent in a nice structured manner by using the bullet points, tables etc if needed in a \
                                                professional manner")
    return response.output_text 


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
    # ... (Prompt definition remains the same)
    prompt = f"""
    Generate a Python dictionary containing 5 multiple-choice questions on the on subtopic \
    '{st.session_state.selected_topic[2]}' of the main topic '{st.session_state.selected_topic[0]}' in '{st.session_state.language}'.
    
    Each question should have:
    - a 'question' key with the question text
    - an 'options' key containing a list of 4 possible answers
    - an 'answer' key containing the correct answer text (must match one of the options exactly)

    Return ONLY the valid JSON/Python dictionary. Do NOT wrap it in a code block or include any explanations or extra text.
    """

    # Call the model
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    # Get the raw string content
    raw_content = response.choices[0].message.content
    
    # 1. Clean the string by removing Markdown code fences (```python or ```json)
    # This regex is robust for removing fences at the beginning and end of the content.
    clean_content = re.sub(r'^\s*```(?:python|json)?\s*|\s*```\s*$', '', raw_content, flags=re.MULTILINE).strip()
    
    # 2. Use the safer json.loads() instead of eval()
    try:
        quiz_data = json.loads(clean_content)
    except json.JSONDecodeError as e:
        # Fallback in case the output isn't perfect JSON but is valid Python
        print(f"JSON Decode Error: {e}. Attempting eval as fallback.")
        quiz_data = eval(clean_content)

    return quiz_data

def add_to_buffer(role, content):
    st.session_state.buffer.append({"role": role, "content": content})
    if len(st.session_state.buffer) > 10:
        st.session_state.buffer = st.session_state.buffer[-10:]


def chat_bot():
    response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": "You are a helpful assistant who is expert in finance and you help "
            "the user by clarifying their doubt, politely ignore if the topic is not related to finance something like "
            f"'please on our current leaning' like that. Reply only in {st.session_state.language} \
            unless user ask you to give response in differnt language"}, 
            *st.session_state.buffer],
    )
    reply = response.choices[0].message.content
    add_to_buffer("assistant", reply)
    return reply


def audio_transcription(audio_bytes):

    with open("temp.wav", "wb") as f:
        f.write(audio_bytes.getbuffer())

    with open("temp.wav", "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )

        return transcription.text