
import os
from google import genai

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Explain photosynthesis in simple words for a school student."
)

print(response.text)
