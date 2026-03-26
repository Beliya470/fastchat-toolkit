# 🚀 FastChat — Beginner's Toolkit: FastAPI + Claude API

---

## 1. 🎯 Title & Objective

**Project name:** FastChat — AI Chatbot API

**Technology stack:**
- **Backend framework:** FastAPI (Python)
- **AI model:** Anthropic Claude API (`claude-sonnet-4-5`)
- **Runtime:** Uvicorn (ASGI server)
- **Data validation:** Pydantic v2
- **Config management:** python-dotenv

**Why I chose this stack:**

I chose FastAPI because it's one of the fastest-growing Python backend frameworks right now and it's used in real production systems — not just tutorials. I'd heard about it from senior developers who said it was easier to learn than Flask but more powerful for building APIs. I also wanted to work with a real AI API rather than a fake mock, so combining FastAPI with Anthropic's Claude API felt like the perfect challenge.

**End goal:**

A fully working chatbot REST API with a browser-based chat UI. When a user types a message in the browser, it travels to my FastAPI backend, gets forwarded to Claude, and the AI's response comes back and displays in the chat window — all in real time. I also wanted multi-turn conversations so Claude remembers what was said earlier in the session.

---

## 2. 📖 Quick Summary of the Technology

### What is FastAPI?

FastAPI is a modern Python web framework for building APIs. It's built on top of Starlette (for the web layer) and Pydantic (for data validation), which makes it very fast and very safe at the same time.

**Where it's used:**

FastAPI shows up in production at companies like Microsoft, Netflix, and Uber for ML model serving, microservices, and internal tooling. It's especially popular in data science and AI teams because Python developers can build a production-quality API without learning a completely different language or framework.

**One real-world example:**

Hugging Face, the AI model hosting platform, uses FastAPI to serve the API endpoints that developers call to run inference on their hosted models. If you've ever used the Hugging Face Inference API in a project, there's a good chance FastAPI was handling your request on the other side.

---

### What is the Claude API (Anthropic SDK)?

The Claude API is Anthropic's service for accessing their Claude family of AI language models programmatically. The Anthropic Python SDK (`anthropic`) wraps the REST API into a clean Python interface so you can send messages and receive replies with just a few lines of code.

**Where it's used:**

The Claude API is used in AI coding assistants, customer support chatbots, document summarization tools, educational tutors, and internal knowledge-base query tools. Companies integrate it whenever they need a capable, safe AI that can follow instructions reliably.

**One real-world example:**

Notion AI — the writing and productivity assistant built into Notion — is powered by language models accessed through APIs similar to this one. When you ask Notion AI to summarise a document or draft an email, it's making an API call to an LLM in the background, exactly the way FastChat calls Claude.

---

## 3. 💻 System Requirements

| Requirement | Details |
|---|---|
| **Operating System** | Windows 10/11, macOS 12+, or any modern Linux distro |
| **Python** | 3.8 or higher (3.11+ recommended) |
| **Package manager** | pip (comes with Python) |
| **Code editor** | VS Code (recommended — great Python extension) |
| **Terminal** | Windows Terminal, PowerShell, macOS Terminal, or bash |
| **API key** | An Anthropic API key — get one free at https://console.anthropic.com |
| **Internet connection** | Required to call the Claude API |

**Checking your Python version:**

```bash
python --version
# or, on some systems:
python3 --version
```

You should see something like `Python 3.11.4`. If Python isn't installed, download it from https://python.org/downloads.

---

## 4. ⚙️ Installation & Setup Instructions

Follow these steps exactly, in order. I'll show commands for both Windows and macOS/Linux where they differ.

---

### Step 1 — Clone the repository

```bash
git clone https://github.com/your-username/fastchat-toolkit.git
cd fastchat-toolkit
```

> If you don't have the repo on GitHub yet, just `cd` into the folder you already created.

---

### Step 2 — Create and activate a virtual environment

A virtual environment keeps this project's packages separate from other Python projects on your machine. Always use one.

**Create the environment:**

```bash
python -m venv venv
```

**Activate it:**

```bash
# Windows (Command Prompt or PowerShell):
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

After activation you should see `(venv)` at the start of your terminal prompt. That means it worked.

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, the Anthropic SDK, python-dotenv, and Pydantic all at once. It may take a minute or two on a slow connection.

---

### Step 4 — Configure your API key

```bash
# Windows:
copy .env.example .env

# macOS / Linux:
cp .env.example .env
```

Now open the new `.env` file in VS Code (or any text editor) and replace `your_api_key_here` with your real Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx
```

Save the file. **Do not commit `.env` to Git** — it's already listed in `.gitignore`.

---

### Step 5 — Start the development server

```bash
uvicorn main:app --reload
```

The `--reload` flag means the server automatically restarts whenever you save a change to `main.py`. You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Step 6 — Open the chat UI

Open your browser and go to:

```
http://localhost:8000/ui
```

You should see the FastChat interface. Type a message and press Enter or click Send. If Claude replies, everything is working correctly.

**Bonus:** Visit `http://localhost:8000/docs` for the auto-generated interactive API documentation that FastAPI creates for free.

---

## 5. 🧪 Minimal Working Example

### What the project does (plain English)

FastChat is a web application with two parts:

1. **A backend (main.py):** A FastAPI server that receives chat messages from the browser, forwards them to the Claude AI API along with the conversation history, gets a reply, and sends it back to the browser.

2. **A frontend (static/index.html):** A single HTML page that provides a chat interface — bubbles for messages, a text input, and a Send button.

The two parts communicate using a standard HTTP POST request to the `/chat` endpoint.

---

### Walking through main.py

**Part 1 — Loading the environment and initialising the client:**

```python
from dotenv import load_dotenv
import os
import anthropic

load_dotenv()  # Reads .env file and puts values into os.environ

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Guard clause: fail early with a helpful message if the key is missing
if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your_api_key_here":
    raise RuntimeError("ANTHROPIC_API_KEY is missing! Copy .env.example to .env and add your key.")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
```

This runs when the server starts. If the key is missing the server refuses to start and tells you exactly how to fix it — much better than a mysterious crash later.

---

**Part 2 — Creating the FastAPI app and conversation store:**

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="FastChat API")

# Mount the static folder so /static/index.html is served automatically
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory conversation history: session_id → list of messages
conversation_history: dict = {}
```

`conversation_history` is just a Python dictionary. Each key is a session ID (a random string generated by the browser), and each value is a list of message dicts. This is how Claude "remembers" previous messages.

---

**Part 3 — Pydantic models:**

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    reply: str
    session_id: str
```

These models do two things at once: they validate incoming data (FastAPI returns a 422 error automatically if `message` is missing) and they document the API shape in `/docs`.

---

**Part 4 — The /chat endpoint:**

```python
from fastapi import HTTPException

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Get or create the history for this session
    history = conversation_history.setdefault(request.session_id, [])

    # Add the user's message to the history
    history.append({"role": "user", "content": request.message})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            system="You are a friendly assistant helping beginners learn FastAPI and Python.",
            messages=history,
            max_tokens=1024,
        )
        assistant_reply = response.content[0].text

    except anthropic.AuthenticationError:
        raise HTTPException(status_code=401, detail={"error_message": "Invalid API key."})

    # Save Claude's reply so future messages have full context
    history.append({"role": "assistant", "content": assistant_reply})

    return ChatResponse(reply=assistant_reply, session_id=request.session_id)
```

The key insight here is passing the full `history` list to every Claude API call. This is how you get multi-turn conversations — Claude sees everything that was said before.

---

### /chat endpoint — request and response format

**Request (POST /chat):**

```json
{
  "message": "What is FastAPI?",
  "session_id": "abc123xyz"
}
```

**Response:**

```json
{
  "reply": "FastAPI is a modern Python web framework for building APIs...",
  "session_id": "abc123xyz"
}
```

---

### curl examples

**Check that the server is running (GET /health):**

```bash
curl http://localhost:8000/health
```

**Expected output:**

```json
{
  "status": "ok",
  "timestamp": "2026-03-26T07:30:00.123456+00:00",
  "service": "FastChat API"
}
```

---

**Send a chat message (POST /chat):**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain what a Pydantic model does", "session_id": "test01"}'
```

**Expected output:**

```json
{
  "reply": "A Pydantic model is a Python class that inherits from BaseModel...",
  "session_id": "test01"
}
```

---

## 6. 🤖 AI Prompt Journal

These are the actual prompts I used while building this project with Claude Code. Looking back, some were great on the first try and some needed a couple of attempts before I got what I needed.

---

**Prompt #1: Setting up FastAPI from scratch**

- **Prompt used:** "I'm a beginner and I want to build a REST API in Python using FastAPI. Can you show me the minimal code to create an app with one GET endpoint that returns a JSON welcome message, and explain each line?"
- **AI response summary:** Claude gave me a clean 15-line example with the imports, `app = FastAPI()`, and a single `@app.get("/")` route. It explained what `@app.get` means as a decorator and why we return a dict (FastAPI auto-converts it to JSON).
- **My evaluation:** Very helpful on the first try. The explanation of decorators was exactly what I needed since I hadn't used them much before. I used this code almost exactly as the base for my `/` route.

---

**Prompt #2: Understanding Pydantic models**

- **Prompt used:** "What is a Pydantic BaseModel and why do I need it in FastAPI? Can you show me a before/after example — once without validation and once using a Pydantic model for a POST endpoint body?"
- **AI response summary:** Claude showed a side-by-side comparison. Without Pydantic: manually calling `request.json()` and hoping the keys exist. With Pydantic: declare a class, FastAPI handles parsing and validation automatically, and you get a 422 error with a clear message if data is missing.
- **My evaluation:** The before/after format was brilliant — it made the value of Pydantic immediately obvious. I refined my prompt once because my first version just asked "what is Pydantic?" and got too much theory. Adding "show me before/after" made it practical.

---

**Prompt #3: Connecting the Anthropic SDK to FastAPI**

- **Prompt used:** "How do I use the Anthropic Python SDK inside a FastAPI endpoint? I want to send a user's message to Claude and return the text reply. Show me the minimal working code, including how to load the API key from an .env file."
- **AI response summary:** Claude showed the exact pattern: `load_dotenv()`, `anthropic.Anthropic(api_key=...)`, then `client.messages.create(model=..., messages=[...], max_tokens=...)` inside the route. It also explained the `messages` format — the list of dicts with `"role"` and `"content"` keys.
- **My evaluation:** Extremely helpful. The trickiest part was understanding the message format Claude expects — the list of dicts with specific keys. Claude's explanation of why this format enables multi-turn conversation was the lightbulb moment for this whole project.

---

**Prompt #4: Handling API errors with HTTPException**

- **Prompt used:** "What specific exceptions does the Anthropic Python SDK raise, and how do I catch them in a FastAPI endpoint and return appropriate HTTP error responses using HTTPException?"
- **AI response summary:** Claude listed the main exceptions: `AuthenticationError` (bad key), `APIConnectionError` (network issue), `RateLimitError` (too many requests), and the generic `Exception` fallback. It showed the try/except structure and how to map each error to the right HTTP status code (401, 503, 429, 500).
- **My evaluation:** Perfect answer. I wouldn't have known the specific exception class names without this. I did have to ask a follow-up — "can you show me how to include a helpful message in the HTTPException detail field?" — before I had the final code I wanted.

---

**Prompt #5: Building the HTML chat UI with fetch()**

- **Prompt used:** "Help me build a single-file HTML chat UI with no frameworks. It should use fetch() to POST to /chat, show user and bot messages as bubbles, disable the input while waiting, and show a typing indicator. Pure HTML/CSS/JS only."
- **AI response summary:** Claude provided a complete HTML file with flexbox bubble layout, a send-on-Enter handler, the fetch() call with error handling, a CSS animated dots indicator, and auto-scroll. It also included the session_id pattern using `Math.random()`.
- **My evaluation:** This was the most impressive response I got from Claude during the project. It produced a complete, working file on the first attempt. I made cosmetic changes (colours, fonts) but the structure was solid. The auto-scroll and empty-input guard were things I hadn't thought to ask for but Claude added them anyway.

---

**Prompt #6: Debugging a 422 Unprocessable Entity error**

- **Prompt used:** "I'm getting a 422 Unprocessable Entity error when I POST to /chat. My request body is `{\"text\": \"hello\"}`. My Pydantic model has a field called `message`. What's going wrong and how do I fix it?"
- **AI response summary:** Claude immediately spotted the mismatch: my request body used `"text"` as the key but my Pydantic model expected `"message"`. It explained that FastAPI returns 422 when the request body doesn't match the model's required fields, and showed how to read the `detail` array in the 422 response body to find the exact field that failed validation.
- **My evaluation:** Solved in one prompt. I had stared at this for 20 minutes before asking Claude. The key lesson I took from this: always check the `detail` field in 422 responses — FastAPI puts a precise error message there that points exactly to the problem.

---

## 7. 🐛 Common Issues & Fixes

---

**Issue: Missing or wrong ANTHROPIC_API_KEY**

**What happened:** The server starts but every chat request returns a 401 Unauthorized error, or the server refuses to start with a RuntimeError about the missing key.

**Why it happened:** Either the `.env` file doesn't exist (the `.env.example` file was never copied), the key value is still `your_api_key_here`, or there's a typo in the key.

**How I fixed it:**

```bash
# Copy the example file to create .env (run once)
# Windows:
copy .env.example .env

# macOS / Linux:
cp .env.example .env
```

Then open `.env` and paste your real key:

```
ANTHROPIC_API_KEY=sk-ant-api03-your-real-key-here
```

Get a key from https://console.anthropic.com. Restart the server after editing `.env`.

---

**Issue: ModuleNotFoundError: No module named 'fastapi'**

**What happened:** Running `python main.py` or `uvicorn main:app` crashes immediately with `ModuleNotFoundError: No module named 'fastapi'` (or `anthropic`, or `dotenv`).

**Why it happened:** The dependencies haven't been installed, OR the virtual environment isn't activated, so Python is looking in the wrong place.

**How I fixed it:**

First, make sure the virtual environment is activated (you should see `(venv)` in your terminal prompt). Then install dependencies:

```bash
# Activate venv first:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Then install:
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:

```bash
pip install fastapi uvicorn[standard] anthropic python-dotenv pydantic
```

---

**Issue: uvicorn: command not found**

**What happened:** After installing everything, running `uvicorn main:app --reload` gave `command not found` or `'uvicorn' is not recognized`.

**Why it happened:** Uvicorn's executable isn't on the system PATH, usually because the virtual environment isn't activated or the `[standard]` extras weren't installed.

**How I fixed it:**

```bash
# Option 1: Run via Python module (always works)
python -m uvicorn main:app --reload

# Option 2: Make sure venv is activated first, then try again
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

uvicorn main:app --reload
```

Running via `python -m uvicorn` bypasses PATH issues entirely.

---

**Issue: 422 Unprocessable Entity on POST /chat**

**What happened:** Sending a POST request to `/chat` returns HTTP 422 with a response body containing a `detail` array.

**Why it happened:** The JSON body sent in the request doesn't match what the `ChatRequest` Pydantic model expects. The most common cause is a wrong field name (e.g., sending `"text"` instead of `"message"`) or a missing required field.

**How I fixed it:**

Read the `detail` array in the 422 response — FastAPI populates it with exactly which field failed and why. For example:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "message"],
      "msg": "Field required"
    }
  ]
}
```

This tells you the `message` field is missing. Make sure your request body matches the model exactly:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'
```

Also double-check that you're sending `Content-Type: application/json` — omitting this header is another common cause of 422 errors.

---

**Issue: CORS error when testing from a different origin**

**What happened:** When trying to call the API from a different frontend (or a different port), the browser console showed: `Access to fetch at 'http://localhost:8000/chat' from origin 'http://localhost:3000' has been blocked by CORS policy`.

**Why it happened:** By default, FastAPI doesn't allow requests from a different origin (different domain or port). Browsers enforce this security rule automatically.

**How I fixed it:**

Add the `CORSMiddleware` to `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production, replace * with your real frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Add this block right after `app = FastAPI(...)` and before any routes. For production, replace `"*"` with a specific list of allowed origins like `["https://myfrontend.com"]`.

---

## 8. 📚 References

| Resource | URL |
|---|---|
| FastAPI official documentation | https://fastapi.tiangolo.com |
| Anthropic Python SDK documentation | https://docs.anthropic.com |
| Uvicorn documentation | https://www.uvicorn.org |
| Pydantic v2 documentation | https://docs.pydantic.dev |
| FastAPI on PyPI | https://pypi.org/project/fastapi/ |
| Anthropic Console (get API key) | https://console.anthropic.com |

---

*Built as a student capstone project — FastAPI + Anthropic Claude API.*
