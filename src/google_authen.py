from getpass import getpass
from dotenv import load_dotenv
from google import genai
import os

def create_client()->genai.Client:
    if not os.getenv('GCP_PROJECT_ID'):
        os.environ['GCP_PROJECT_ID']=getpass(f'GCP_PROJECT_ID: ')
    project_id = os.getenv("GCP_PROJECT_ID")
    return genai.Client(vertexai=True,project=project_id)