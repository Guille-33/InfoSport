from getpass import getpass
from dotenv import load_dotenv
from google import genai
import os
load_dotenv()
# def create_client(i:int)->genai.Client:
#     keyName=f'GEMINI_API_KEY_{i}'
#     if not os.getenv(keyName):
#         os.environ[keyName]=getpass(f'{keyName}: ')
#     api_key_value = os.getenv(keyName)
#     return genai.Client(api_key=api_key_value)

def create_client()->genai.Client:
    if not os.getenv('GCP_PROJECT_ID'):
        os.environ['GCP_PROJECT_ID']=getpass(f'GCP_PROJECT_ID: ')
    project_id = os.getenv("GCP_PROJECT_ID")
    return genai.Client(vertexai=True,project=project_id)