import os
import time
from dotenv import load_dotenv
from google import genai

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
models = [
    os.getenv("GEMINI_MODEL", "gemini-3.7-flash"),
    *[x.strip() for x in os.getenv(
        "GEMINI_FALLBACK_MODELS",
        "gemini-3.6-flash,gemini-3.5-flash-lite"
    ).split(",") if x.strip()]
]
models = list(dict.fromkeys(models))

print("================================")
print("HeartAI Gemini Test")
print("================================")

if not api_key or not api_key.strip():
    print("ERROR: Gemini API key not found.")
    raise SystemExit(1)

print("API key detected.")
print("Models to test:", ", ".join(models))

client = genai.Client(api_key=api_key.strip())
last_error = None

for model in models:
    for attempt in range(3):
        try:
            print(f"\nTesting {model} (attempt {attempt + 1}/3)...")
            response = client.models.generate_content(
                model=model,
                contents="Reply with exactly: HeartAI Gemini Test Successful"
            )
            print("\nGEMINI RESPONSE:")
            print(response.text)
            print("\nSUCCESS")
            print("Working model:", model)
            print("================================")
            raise SystemExit(0)
        except Exception as exc:
            last_error = exc
            print(type(exc).__name__, str(exc))
            text = f"{type(exc).__name__} {exc}".lower()
            retryable = any(x in text for x in ("503", "unavailable", "429", "500", "502", "504", "high demand"))
            if retryable and attempt < 2:
                delay = 1.5 * (2 ** attempt)
                print(f"Temporary Gemini error. Retrying in {delay:.1f}s...")
                time.sleep(delay)
            else:
                break

print("\nGEMINI ERROR")
print("All configured models were unavailable.")
print(type(last_error).__name__ if last_error else "UnknownError")
print(str(last_error) if last_error else "No response")
print("\nThis is a Gemini service/availability problem, not a missing API-key problem.")
print("Try again later or check Google AI Studio usage/quota.")
print("================================")
