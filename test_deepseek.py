
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv('backend/.env')

api_key = os.environ.get('DEEPSEEK_API_KEY')
if not api_key:
    # Fallback to checking if it's named something else or ask user
    print("Warning: DEEPSEEK_API_KEY not found in environment variables.")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        stream=False
    )
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
