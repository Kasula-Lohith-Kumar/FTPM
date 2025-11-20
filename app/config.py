import os 
import tempfile

IMAGE_FOLDER_PATH = 'images'
PERSISTANT_PATH = 'embeddings'
WORKING_DIR = os.path.join(tempfile.gettempdir(), 'working_dir')
EMBBED_EXRT_PATH = os.path.join(WORKING_DIR, PERSISTANT_PATH)
COMBINED_TEXT_FILE = r'temp.txt'