import os
from dotenv import load_dotenv
from openai import OpenAI

# Load the API key from your .env file
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ Error: OPENAI_API_KEY not found in .env file.")
else:
    print("✅ Found API Key. Attempting to connect to OpenAI...")
    try:
        # Initialize the OpenAI client
        client = OpenAI(api_key=api_key)

        # Make a simple, low-cost API call to list models
        models = client.models.list()

        print("\n🎉 Success! Your OpenAI API key is working.")
        print(f"Successfully fetched {len(models.data)} available models.")

    except Exception as e:
        print("\n❌ Error: Failed to connect to OpenAI.")
        print("   Please check the following:")
        print("   1. Is your API key correct in the .env file?")
        print("   2. Is your OpenAI account active and does it have credits?")
        print(f"\n   Error details: {e}")