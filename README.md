# 🤖 Gemini Web Search Chatbot

```markdown
A powerful, single-file AI chatbot built with Python and Streamlit. 
It uses the Gemini 2.0 Flash model with built-in Google Search Grounding, allowing it to answer questions about current events, news, and real-time data with citation links.
```

## ✨ Features
* **Real-time Web Search**: Automatically searches Google when asked about current events.
* **Source Citations**: Provides clickable links to the websites used to generate answers.
* **Chat History**: Remembers the conversation context within the current session.
* **Streamlit UI**: Clean, responsive web interface.

## 🛠️ Prerequisites
* Python 3.10 or higher.
* A Google Gemini API Key (Get it for free at [Google AI Studio](https://aistudio.google.com/)).

## 📦 Installation

1.  **Clone or Download this repository**
    ```bash
    git clone <repository-url>
    cd chat_bot
    ```

2.  **Set up a Virtual Environment (Recommended)**
    * *Using standard Python:*
        ```bash
        python -m venv .venv
        # Windows:
        .venv\Scripts\activate
        # Mac/Linux:
        source .venv/bin/activate
        ```

3.  **Install Dependencies**
    You need Streamlit, the Google GenAI SDK, and python-dotenv.
    ```bash
    pip install streamlit google-genai python-dotenv
    ```

## 🔑 Configuration

1.  Create a file named `.env` in the same folder as `app.py`.
2.  Open it and add your API key like this:

    ```text
    GEMINI_API_KEY=AIzaSyYourActualApiKeyHere...
    ```

## 🚀 How to Run

Run the application using Streamlit:

```bash
streamlit run app.py

```

### ⚠️ Troubleshooting (Windows)

If you see an error like `'streamlit' is not recognized` even after installing, try running it via Python directly:

```bash
python -m streamlit run app.py

```

## 📂 Project Structure

```text
chat_bot/
├── app.py           # The main application (Frontend + Backend)
├── .env             # Your API Key (Do not share this file!)
└── README.md        # This documentation

```

## 🧠 How it Works

1. **Input**: You type a query (e.g., "What is the stock price of Apple?").
2. **Decision**: The Gemini model analyzes if it needs external information.
3. **Search**: If needed, it uses the `GoogleSearch` tool to query the live web.
4. **Synthesis**: It reads the search results and generates a natural language answer.
5. **Citations**: It extracts the source URLs (`grounding_metadata`) and displays them below the answer.
