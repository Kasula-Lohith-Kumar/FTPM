import io
import streamlit as st    
from gtts import gTTS
import langchain_api_prompts as lap

# --- Text-to-Speech helpers ---
def get_tts_lang(language):
        mapping = {
            "English": "en",
            "తెలుగు (Telugu)": "te",
            "हिंदी (Hindi)": "hi",
            "தமிழ் (Tamil)": "ta",
            "ಕನ್ನಡ (Kannada)": "kn",
        }
        return mapping.get(language, "en")

def speak_text(text, language):
        lang_code = get_tts_lang(language)
        try:
            tts = gTTS(text=text, lang=lang_code)
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            st.audio(audio_bytes, format="audio/mp3")
        except Exception as e:
            st.error(f"Error generating audio: {e}")

def speak_text(text):
        """
        Wrapper around voice() to produce Streamlit-safe audio bytes.
        """
        audio_bytes = lap.voice(text)
        if audio_bytes:
            return audio_bytes
        return None


def safe_speak(text, fallback_text):
        too_many_rqsts ="Too Many Requests"
        tmr_warning = f"⚠️ {too_many_rqsts} — playing fallback audio."
        ega_error = "⚠️ Error generating audio — playing fallback audio."
        try:
            # Try primary text
            audio = speak_text(text)
            return audio

        except Exception as e:
            msg = str(e)

            # Handle 429 rate limits
            if "429" in msg or too_many_rqsts in msg:
                st.error(tmr_warning)
                try:
                    return speak_text(fallback_text)
                except:
                    return None

            # Other errors → fallback audio
            st.error(ega_error)
            try:
                return speak_text(fallback_text)
            except:
                return None
            

    # Process input or voice
    # if audio_input:
    #     st.info("⏳ Transcribing...")
    #     try:
    #         text = oap.audio_transcription(audio_input)
    #         st.success("✅ Transcribed Text:")
    #         st.write(text)
    #     except Exception as e:
    #         st.error(f"❌ Transcription failed: {e}")