import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Setup (Load API Key)
load_dotenv(override=True)
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found in environment variables.")
    st.stop()

st.set_page_config(page_title="Gemini Search Bot", page_icon="🤖")
st.title("🤖 Gemini Web Search Chat")

st.sidebar.header("⚙️ Settings")

MODEL_OPTIONS = {
    "Fast (Flash)": "gemini-2.5-flash",
    "Accurate (Pro)": "gemini-2.5-pro"
}

selected_model_label = st.sidebar.radio(
    "Choose Model",
    options=list(MODEL_OPTIONS.keys()),
    index=0
)

selected_model = MODEL_OPTIONS[selected_model_label]

# 2. Initialize Client (Cached so it doesn't reload on every click)
@st.cache_resource
def get_client():
    return genai.Client(api_key=api_key)

client = get_client()

def render_scrollable_markdown_list(items, max_height=220):
    if not items:
        return

    st.markdown(
        f"""
        <div style="
            max-height: {max_height}px;
            overflow-y: auto;
            padding-right: 6px;
            word-break: break-word;
            overflow-wrap: anywhere;
            font-size: 0.9rem;
        ">
        """,
        unsafe_allow_html=True
    )

    for item in items:
        st.markdown(f"- {item}", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def truncate(text, n=70):
    return text if len(text) <= n else text[:n] + "…"


# 3. Session State (Memory)
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "model",
        "content": "💡 Type your question and press **Enter** to search the web."
    })

# 4. Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.markdown(f"- {source}")

# 5. Handle New Messages
if prompt := st.chat_input(
    placeholder="best coffee in India"
):
    # Show User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate Response
    with st.chat_message("model"):
        with st.spinner("Searching & Thinking..."):
            try:
                # A. Prepare History for Gemini (Sliding Window)
                gemini_history = []
                
                # SLICING: Only take the last 10 messages from session state
                # This prevents Token Limit Exceeded errors on long chats
                MAX_TURNS = 10 
                recent_messages = st.session_state.messages[-(MAX_TURNS*2)::] 

                for msg in recent_messages:
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

                # D. Call Gemini (STREAMING)
                # Use generate_content_stream instead of generate_content
                response_stream = client.models.generate_content_stream(
                    model=selected_model,
                    contents=gemini_history,
                    config=tool_config
                )

                # E. Process Stream & Display
                # Create a placeholder for the text to update in real-time
                text_placeholder = st.empty()
                full_text = ""
                unique_sources = {}

                # Iterate through the stream
                for chunk in response_stream:
                    # 1. Collect Text
                    if chunk.text:
                        full_text += chunk.text
                        text_placeholder.markdown(full_text + "▌") # Add a cursor effect

                    # 2. Collect Sources (Grounding Metadata usually comes in chunks too)
                    if (chunk.candidates and 
                        chunk.candidates[0].grounding_metadata and 
                        chunk.candidates[0].grounding_metadata.grounding_chunks):
                        
                        for g_chunk in chunk.candidates[0].grounding_metadata.grounding_chunks:
                            if g_chunk.web and g_chunk.web.uri and g_chunk.web.title:
                                unique_sources[g_chunk.web.uri] = g_chunk.web.title

                # Remove cursor and show final text
                text_placeholder.markdown(full_text)

                # Format Sources
                formatted_sources = [
                f"[{truncate(title)}]({uri})"
                for uri, title in unique_sources.items()
            ]

                # F. Display Sources & Save History
                if formatted_sources:
                    with st.expander("📚 Sources"):
                        render_scrollable_markdown_list(formatted_sources)
                
                st.session_state.messages.append({
                    "role": "model", 
                    "content": full_text, 
                    "sources": formatted_sources
                })

            except Exception as e:
                st.error(f"An error occurred: {e}")