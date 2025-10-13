import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import json
from app.google_sheets import gsheets_config as gsc

def is_streamlit_cloud() -> bool:
    """Detect Streamlit Cloud by checking if st.secrets has Streamlit-managed credentials."""
    try:
        _ = st.secrets["gcp_service_account"]
        return True
    except Exception:
        return False

def load_key_file_data():
    """
    Loads Google Service Account credentials.
    Handles both local and Streamlit Cloud environments safely.
    """
    try:
        if is_streamlit_cloud():
            print("🌐 STREAMLIT_RUNTIME detected — loading from Streamlit secrets...")
            key_data = json.loads(st.secrets["gcp_service_account"])
        else:
            print("💻 LOCAL_RUNTIME detected — loading from local JSON file...")
            with open(gsc.LOCAL_KEY_PATH, "r") as file:
                key_data = json.load(file)
        
        print("✅ Successfully loaded GCP key data.")
        return key_data

    except FileNotFoundError as e:
        print(f"❌ Local key file not found: {e}")
        st.error("Local service account key file missing.")
        return None

    except KeyError as e:
        print(f"❌ Missing key in Streamlit secrets: {e}")
        st.error("Missing 'gcp_service_account' entry in Streamlit secrets.")
        return None

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        st.error("Service account file contains invalid JSON.")
        return None

    except Exception as e:
        print(f"⚠️ Unexpected error while loading key data: {e}")
        st.error(f"Unexpected error: {e}")
        return None
    
def  run():

    gsc.KEY_FILE_DATA = load_key_file_data()

    if 'page_status' not in st.session_state:
        st.session_state['page_status'] = 'home'

    if st.session_state['page_status'] == 'home':
        st.switch_page("pages/home.py")


if __name__ == "__main__":

    run()