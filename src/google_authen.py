from getpass import getpass
from dotenv import load_dotenv
from google import genai
import os

def create_client()->genai.Client:
    load_dotenv()
    if not os.getenv('GEMINI_API_KEY'):
        os.environ['GEMINI_API_KEY']=getpass('GEMINI_API_KEY: ')
    return genai.Client()