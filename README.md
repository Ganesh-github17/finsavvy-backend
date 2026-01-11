# Finsavvy Backend

FastAPI backend for Finsavvy AI-Based Financial Application.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On Linux/Mac

pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file:

```
GEMINI_API_KEY=your_actual_api_key_here
PYTHON_ENV=development
DEBUG=True
```

## Development

```bash
uvicorn app:app --reload --port 5000
```

## Deploy to Render

1. Push this backend folder to GitHub
2. Create a new Web Service on Render
3. Connect your repository
4. Set build settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `PYTHON_ENV`: `production`
