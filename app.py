import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Setup (Load API Key)
load_dotenv(override=True)
api_key = os.environ.get("GEMINI_API_KEY")

st.set_page_config(page_title="Gemini Search Bot", page_icon="🤖")
st.title("🤖 Gemini Web Search Chat")

# 2. Initialize Client (Cached so it doesn't reload on every click)
@st.cache_resource
def get_client():
    return genai.Client(api_key=api_key)

client = get_client()

# 3. Session State (Memory)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.markdown(f"- {source}")

# 5. Handle New Messages
if prompt := st.chat_input("Ask me anything..."):
    # Show User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate Response
    with st.chat_message("model"):
        with st.spinner("Searching & Thinking..."):
            try:
                # A. Prepare History for Gemini
                gemini_history = []
                for msg in st.session_state.messages[:-1]: # Skip the last one we just added
                    gemini_history.append(
                        types.Content(
                            role=msg["role"],
                            parts=[types.Part(text=msg["content"])]
                        )
                    )
                
                # B. Add current prompt
                gemini_history.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(text=prompt)]
                    )
                )

                # C. Configure Search Tool
                tool_config = types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    response_modalities=["TEXT"],
                    temperature=0.7
                )

                # D. Call Gemini (Synchronous is fine here)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=gemini_history,
                    config=tool_config
                )

                # E. Extract Text & Sources
                bot_text = response.text if response.text else "No response generated."
                
                sources = []
                if (response.candidates and 
                    response.candidates[0].grounding_metadata and 
                    response.candidates[0].grounding_metadata.grounding_chunks):
                    for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                        if chunk.web and chunk.web.uri:
                            sources.append(f"{chunk.web.title}: {chunk.web.uri}")

                # F. Display & Save
                st.markdown(bot_text)
                if sources:
                    with st.expander("📚 Sources"):
                        for source in sources:
                            st.markdown(f"- {source}")
                
                st.session_state.messages.append({
                    "role": "model", 
                    "content": bot_text, 
                    "sources": sources
                })

            except Exception as e:
                st.error(f"An error occurred: {e}")