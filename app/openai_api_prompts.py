from app import app_config
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=app_config.key)

def learning_material():

    response = client.responses.create(model = 'gpt-4.1-mini', input=f"You are a financal guide/teacher \
                                                who Provides the detailed information about the subtopic '{st.session_state.selected_topic[2]}' \
                                                of the main topic {st.session_state.selected_topic[0]} in {st.session_state.language} \
                                                in layman terms, provide atleast a page of content. \
                                                Start directly with the explanation — do not include phrases like ‘Here is’ or ‘Certainly’. \
                                                Provide topic conent in a nice structured manner by using the bullet points, tables etc if needed in a \
                                                professional manner")
    return response.output_text 