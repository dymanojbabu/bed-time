import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).parent.parent / ".env")

key = os.environ.get("GEMINI_API_KEY")
print("Key found:", bool(key))
if key:
    print("Key preview:", key[:8] + "...")

client = genai.Client(api_key=key)

print("\nHere are the models available to your API key:")
for model in client.models.list():
    print(f"- {model.name}")
