# FastChat — AI Chatbot API with FastAPI + Claude

> A beginner-friendly chatbot backend built with FastAPI and the Anthropic Claude API

---

## What This Is

FastChat is a Python web application that exposes a REST API for multi-turn AI conversations powered by Anthropic's Claude model. It includes a built-in browser chat UI so you can start talking to the AI immediately — no separate frontend setup required. The project is designed to be a clear, well-commented learning example for anyone new to FastAPI and AI APIs.

---

## Prerequisites

- **Python 3.8+** — download from https://python.org/downloads
- **pip** — comes bundled with Python
- **An Anthropic API key** — get one free at https://console.anthropic.com

---

## Quickstart

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd fastchat-toolkit
```

### 2. Create and activate a virtual environment

```bash
# Create the environment (run once)
python -m venv venv

# Activate it:
# Windows (Command Prompt / PowerShell):
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal prompt.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

```bash
# Windows:
copy .env.example .env

# macOS / Linux:
cp .env.example .env
```

Open `.env` in a text editor and replace `your_api_key_here` with your real Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-api03-your-real-key-here
```

> **Important:** Never commit the `.env` file to Git. It is already listed in `.gitignore`.

### 5. Start the server

```bash
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 6. Open the chat UI

```
http://localhost:8000/ui
```

Type a message and press **Enter** or click **Send**. That's it!

> Bonus: visit `http://localhost:8000/docs` for the interactive API documentation.

---

## API Endpoints

| Method | Endpoint  | Description                              |
|--------|-----------|------------------------------------------|
| GET    | `/`       | Welcome message — confirms the API is up |
| GET    | `/health` | Health check with UTC timestamp          |
| GET    | `/ui`     | Browser-based chat interface             |
| POST   | `/chat`   | Send a message and receive an AI reply   |

---

## Example curl

**Send a message to the chatbot:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is FastAPI and why should I learn it?", "session_id": "demo01"}'
```

**Expected JSON response:**

```json
{
  "reply": "FastAPI is a modern, high-performance Python web framework for building APIs. You should learn it because it's incredibly fast to develop with — it gives you automatic data validation, interactive docs at /docs, and async support out of the box. It's a great choice for building AI-powered backends exactly like this one!",
  "session_id": "demo01"
}
```

---

## Project Structure

```
fastchat-toolkit/
├── main.py              # FastAPI application — all routes and Claude API logic
├── requirements.txt     # Python package dependencies
├── .env.example         # Template for environment variables (copy to .env)
├── .gitignore           # Files that should never be committed to Git
├── static/
│   └── index.html       # Single-page browser chat UI (pure HTML/CSS/JS)
├── docs/
│   └── TOOLKIT.md       # Beginner's toolkit — full walkthrough and reference
└── README.md            # This file
```

---

## How Conversations Work

Each browser session generates a random `session_id`. Every message sent to `/chat` includes this ID. The server stores the full message history in memory for each session, so Claude always has the context of the entire conversation. Sessions reset when the server restarts.

---

## License

MIT — free to use, modify, and distribute.
