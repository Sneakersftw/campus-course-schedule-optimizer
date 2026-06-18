import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"


def parse_preferences_with_ai(user_message: str) -> dict:
    """
    Converts a natural-language scheduling request into structured JSON.
    Retries up to 3 times if the AI provider is temporarily unavailable.
    """
    system_prompt = """You convert student scheduling requests into structured JSON.

Respond ONLY with valid JSON, no preamble, no markdown formatting, no explanation.

The JSON must have this exact shape:
{
  "target_credit_hours": <int or null>,
  "unavailable_times": [{"days": ["Monday", ...], "start_time": "HH:MM", "end_time": "HH:MM"}],
  "earliest_class_time": "HH:MM or null",
  "latest_class_time": "HH:MM or null",
  "avoid_days": ["Monday", ...]
}

If the user doesn't mention a field, use null or an empty list. Use 24-hour time format.
Do not invent constraints the user did not mention."""

    response = None
    last_error = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=f"{system_prompt}\n\nStudent request: {user_message}",
            )
            break
        except Exception as e:
            last_error = e
            time.sleep(3)

    if response is None:
        return {
            "error": "AI service is temporarily unavailable. Please try again shortly.",
            "details": str(last_error),
        }

    raw_text = response.text.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:].strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "error": "Gemini returned invalid JSON",
            "raw_response": raw_text,
        }


def explain_schedule_with_ai(schedule_summary: dict, preferences: dict = None) -> str:
    """
    Given a backend-generated schedule and student preferences,
    asks the AI model to explain in plain English why this schedule fits.
    The AI does NOT regenerate or alter the schedule — only explains it.
    """
    system_prompt = """You explain student course schedules in plain, friendly English.
You are given a schedule that has ALREADY been validated and ranked by a backend system.
Do not suggest changes, do not invent courses, do not claim there are conflicts.
Just explain in 2-4 sentences why this schedule fits the student's stated preferences."""

    user_content = f"""Schedule: {json.dumps(schedule_summary)}
Student preferences: {json.dumps(preferences or {})}"""

    response = client.models.generate_content(
        model=MODEL,
        contents=f"{system_prompt}\n\n{user_content}",
    )

    return response.text.strip()