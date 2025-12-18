import os
from google import genai
from google.genai import types
#--load the environment variables
from dotenv import load_dotenv
load_dotenv(override=True)
#--load from environment variables
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("❌ API Key not found! Please set GEMINI_API_KEY environment variable or paste it directly.")
else:
    print("✅ API Key found.")

    try:
        # 2. Initialize Client
        client = genai.Client(api_key=api_key)

        # 3. Simple Generation Test
        print("Sending request to Gemini...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Hello! Are you working? Reply with a short funny quote."
        )

        # 4. Print Result
        print("\n--- Response from Gemini ---")
        print(response.text)
        print("----------------------------")
        print("✅ SUCCESS: Gemini is working!")

    except Exception as e:
        print("\n❌ ERROR: Something went wrong.")
        print(e)