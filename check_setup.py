import os
from dotenv import load_dotenv

load_dotenv()  
key = os.getenv("AISSTREAM_API_KEY")

if key:
    print(f"Key loaded ({len(key)} characters)")
else:
    print("No key found - check your .env file")