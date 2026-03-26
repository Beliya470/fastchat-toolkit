# ============================================================
# FastChat — AI Chatbot API built with FastAPI + Gemini API
# ============================================================
# This file is the heart of the application. It defines all
# the API routes, connects to the Google Gemini AI service, and
# manages per-session conversation history.
# ============================================================

# --- Imports ------------------------------------------------
# FastAPI is the web framework that handles HTTP requests
from fastapi import FastAPI, HTTPException

# StaticFiles lets us serve files from a folder (our HTML UI)
# FileResponse sends a specific file back to the browser
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Uvicorn is the server that actually runs FastAPI
import uvicorn

# The official Google Generative AI Python SDK — used to call Gemini
import google.generativeai as genai

# google.api_core.exceptions gives us specific error classes to catch
import google.api_core.exceptions

# os lets us read environment variables (like our API key)
import os

# datetime is used to generate a timestamp for the /health route
from datetime import datetime, timezone

# load_dotenv reads our .env file and puts values into os.environ
from dotenv import load_dotenv

# BaseModel is used to define the shape (schema) of request/response data
from pydantic import BaseModel

# --- Load environment variables ------------------------------
# This reads the .env file in the project root.
# After this call, os.getenv("GEMINI_API_KEY") will return
# whatever value you put in your .env file.
load_dotenv()

# Fetch the API key from the environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# If the key is missing or still the placeholder, raise an error
# immediately so the developer sees a helpful message right away
# instead of a confusing crash later.
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    raise RuntimeError(
        "\n\n❌  GEMINI_API_KEY is missing or not set!\n"
        "To fix this:\n"
        "  1. Copy .env.example to .env\n"
        "     Windows:  copy .env.example .env\n"
        "     Mac/Linux: cp .env.example .env\n"
        "  2. Open .env and replace 'your_gemini_api_key_here' with your real key\n"
        "     Get a free key at: https://aistudio.google.com/apikey\n"
        "  3. Restart the server.\n"
    )

# --- Configure the Gemini client ----------------------------
# genai.configure() registers your API key globally so every
# subsequent call to the SDK uses it automatically.
genai.configure(api_key=GEMINI_API_KEY)

# --- Initialize the Gemini model ----------------------------
# GenerativeModel selects which Gemini model to use and sets
# the system_instruction — a hidden prompt that shapes the AI's
# personality and behaviour for every conversation.
# "gemini-1.5-flash" is fast, capable, and free-tier friendly.
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction=(
        "You are a friendly assistant helping beginners learn "
        "FastAPI and Python. Keep answers clear and encouraging."
    ),
)

# --- Initialize the FastAPI application ---------------------
# title and description appear in the auto-generated API docs
# (visit http://localhost:8000/docs to see them)
app = FastAPI(
    title="FastChat API",
    description=(
        "A beginner-friendly chatbot API powered by FastAPI and the "
        "Google Gemini API. Supports multi-turn conversations with "
        "per-session history. Visit /ui for the browser chat interface."
    ),
    version="1.0.0",
)

# --- Mount the static files folder --------------------------
# This tells FastAPI: "any request to /static/... should serve
# the matching file from the ./static/ folder on disk."
# Our index.html lives at static/index.html.
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Conversation history store -----------------------------
# A plain Python dictionary that maps session_id → list of messages.
# Each message is stored in our own format for consistency:
#   {"role": "user" or "assistant", "content": "the text"}
#
# When we call Gemini, we convert this list into Gemini's expected
# format on the fly (see the /chat endpoint below).
#
# NOTE: This is an in-memory store — it resets when the server restarts.
# For a production app you'd use a database instead.
conversation_history: dict = {}

# --- Pydantic models ----------------------------------------
# Pydantic models define the exact shape of data we expect to
# receive (request body) or send back (response body).
# FastAPI uses these to automatically validate and document the API.

class ChatRequest(BaseModel):
    """Data the client must send when posting a message."""
    # The text message the user wants to send to Gemini
    message: str
    # A unique ID that groups messages into a conversation.
    # Defaults to "default" so simple clients don't need to set it.
    session_id: str = "default"


class ChatResponse(BaseModel):
    """Data FastAPI sends back after getting Gemini's reply."""
    # The text reply generated by Gemini
    reply: str
    # Echo back the session_id so the client can track conversations
    session_id: str


# === ROUTES =================================================

# --- GET / --------------------------------------------------
# The root route. Returns a friendly JSON welcome message.
# Useful for quickly checking that the server is running.
@app.get("/")
def root():
    """Welcome endpoint — confirms the API is alive."""
    return {
        "api": "FastChat API",
        "status": "running",
        "message": (
            "Welcome to FastChat! Send a POST request to /chat "
            "to start a conversation, or open /ui for the browser interface."
        ),
        "docs": "/docs",
    }


# --- GET /health --------------------------------------------
# Health-check endpoint. Monitoring tools and load balancers
# often call this to confirm the service is healthy.
@app.get("/health")
def health_check():
    """Returns the current health status and a UTC timestamp."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "FastChat API",
    }


# --- GET /ui ------------------------------------------------
# Returns the HTML file that provides the browser-based chat UI.
# FileResponse streams the file directly to the browser.
@app.get("/ui")
def chat_ui():
    """Serves the single-page chat interface."""
    return FileResponse("static/index.html")


# --- POST /chat ---------------------------------------------
# This is the main endpoint. The client sends a message and
# gets back a reply from Gemini, with full conversation context.
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Accepts a user message and session_id, calls the Gemini API
    with the full conversation history, and returns the AI reply.
    """

    # Step 1: Retrieve (or create) the history for this session.
    # If this is the first message for this session_id, we start
    # with an empty list. setdefault does both checks in one call.
    history = conversation_history.setdefault(request.session_id, [])

    # Step 2: Convert our stored history into Gemini's expected format.
    # Our format:  {"role": "user"/"assistant", "content": "text"}
    # Gemini format: {"role": "user"/"model",   "parts": ["text"]}
    #
    # Key differences:
    #   - Gemini uses "parts" (a list) instead of "content" (a string)
    #   - Gemini uses the role name "model" where we store "assistant"
    gemini_history = []
    for msg in history:
        gemini_role = "model" if msg["role"] == "assistant" else "user"
        gemini_history.append({
            "role": gemini_role,
            "parts": [msg["content"]],
        })

    # Step 3: Call the Gemini API inside a try/except block.
    # We catch specific Google API errors so we can return clear
    # error messages instead of a generic 500 crash.
    try:
        # start_chat() creates a stateful chat session.
        # We pass in the converted history so Gemini has full context
        # of everything said earlier in this session.
        chat_session = model.start_chat(history=gemini_history)

        # send_message() sends the latest user message to Gemini.
        # The SDK automatically appends it to the chat history internally.
        response = chat_session.send_message(request.message)

        # Extract the plain text from the response object
        reply_text = response.text

    except google.api_core.exceptions.PermissionDenied:
        # Raised when the API key is invalid, missing, or does not have
        # permission to use the requested model.
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Authentication failed",
                "error_message": (
                    "Your GEMINI_API_KEY is invalid or does not have permission. "
                    "Check your .env file and make sure the key is correct. "
                    "Get a free key at https://aistudio.google.com/apikey"
                ),
            },
        )

    except google.api_core.exceptions.InvalidArgument:
        # Raised when the request is malformed — e.g. an empty message
        # or an unsupported model name.
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid request",
                "error_message": (
                    "The request sent to Gemini was invalid. "
                    "Make sure your message is not empty and the model name is correct."
                ),
            },
        )

    except google.api_core.exceptions.ResourceExhausted:
        # Raised when you've exceeded your free-tier quota or rate limit
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit / quota exceeded",
                "error_message": (
                    "You've hit the Gemini API rate limit or free-tier quota. "
                    "Wait a moment and try again. Check your quota at "
                    "https://aistudio.google.com/apikey"
                ),
            },
        )

    except Exception as e:
        # Catch-all for any other unexpected errors
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unexpected server error",
                "error_message": (
                    f"Something went wrong on the server: {str(e)}. "
                    "Check the server logs for more details."
                ),
            },
        )

    # Step 4: Save both the user message and Gemini's reply to our history
    # in our own format so future messages in this session have full context.
    history.append({
        "role": "user",
        "content": request.message,
    })
    history.append({
        "role": "assistant",
        "content": reply_text,
    })

    # Step 5: Return the structured response
    return ChatResponse(reply=reply_text, session_id=request.session_id)


# --- Run the app directly (optional) ------------------------
# This block lets you run the app with: python main.py
# For development, prefer: uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
