import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app import secrets
import os


# --- Initialize buffer ---
if "buffer" not in st.session_state:
    st.session_state.buffer = []

# --- Initialize model ---
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    api_key=os.getenv("OPENAI_API_KEY").strip().replace('"', ''),
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