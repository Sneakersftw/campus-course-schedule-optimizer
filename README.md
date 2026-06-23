# Campus Course-Schedule Optimizer with AI Planning Assistant

## Project Overview

Campus Course-Schedule Optimizer is a full-stack web application that helps students generate valid semester schedules based on completed courses, prerequisites, class times, credit-hour goals, and personal preferences.

The app uses a deterministic backend scheduling engine to validate prerequisites, detect class-time conflicts, filter by credit hours, and rank possible schedules. Natural-language preferences (e.g. "I want 15 credit hours, no Friday classes, nothing before 10am") are parsed into structured constraints using Google's Gemini API, but the backend remains the source of truth for all scheduling rules — the AI never invents courses, decides conflicts, or generates schedules directly.

## Problem Being Solved

College students often struggle to choose classes because they must balance prerequisites, required courses, class availability, work schedules, preferred times, and credit-hour limits. This project solves that problem by automatically generating valid schedule options and ranking them based on student preferences.

## Tech Stack

### Frontend
- React
- Vite
- TypeScript
- Tailwind CSS

### Backend
- Python
- FastAPI
- SQLAlchemy
- PyMySQL
- Pytest

### Database
- MySQL

### AI Integration
- Google Gemini API (`google-genai` SDK)

> **Note on AI provider:** The original project plan specified Anthropic's Claude API. This was swapped to Google's Gemini API during development, since Gemini offers a no-credit-card-required free tier, while Claude's API requires billing setup even for minimal usage. The integration architecture (a dedicated `ai.py` module with `parse_preferences_with_ai` and `explain_schedule_with_ai` functions) is provider-agnostic by design, so swapping providers required no changes to the scheduling engine, routes, or frontend.

## Current Status

- FastAPI backend with `/health` and root routes
- React + Vite + TypeScript + Tailwind frontend
- MySQL database with `courses`, `course_prerequisites`, `course_sections`, and `completed_courses` tables
- Seed script with 10 sample CS/Math courses, prerequisite relationships, and course sections
- Prerequisite validation engine (`check_prerequisites`, `get_eligible_courses`)
- Time-conflict detection (`sections_overlap`, `schedule_has_conflicts`)
- Credit-hour calculation and filtering
- Schedule generation via backtracking with early conflict pruning (`generate_valid_schedules`)
- Schedule scoring and ranking based on gaps, time preferences, and day avoidance (`score_schedule`, `rank_schedules`)
- REST API endpoints: `GET /schedules/{student_id}` and `POST /schedules/{student_id}/with-preferences`
- Gemini API integration for natural-language preference parsing, with retry logic for upstream outages
- Frontend UI: credit-hour inputs, natural-language preference textarea, and live schedule results displayed as ranked cards
- CORS configured for local development
- 25 automated Pytest tests covering prerequisites, conflicts, scheduling, ranking, and AI integration edge cases

## Known Limitations

- **Gemini free-tier rate limit:** The free tier used for AI preference parsing is capped at 20 requests per day per model. Once exceeded, the app returns a clean error message rather than crashing (see retry/error handling in `app/ai.py`), but repeated testing or demoing within the same day can exhaust this quota. A production version would need a paid tier or a caching/rate-limiting layer.
- **Sample data scope:** The seed dataset includes 10 courses rather than the originally planned 15–25, focused on a single sample student (`student_id=1`) with a believable prerequisite chain. This was a deliberate scope reduction to prioritize finishing core scheduling logic over breadth of sample data.
- **Brute-force schedule generation:** `generate_valid_schedules` uses exhaustive backtracking with early conflict pruning. This is appropriate at the current data scale (10 courses, 1–2 sections each) but would need a more efficient algorithm (e.g. constraint propagation or pruning by credit budget) at a much larger course catalog size.
- **Soft vs. hard preferences:** Day avoidance and time preferences affect schedule *ranking* (lower score) but are not currently hard exclusion filters — a schedule that includes an avoided day can still appear, just ranked lower. This matches the original plan's distinction between hard constraints (prerequisites, conflicts, credit range) and soft preferences (day/time preference).
- **No user accounts or persistence of preferences:** Preferences are submitted per-request and not saved between sessions, consistent with the planned MVP scope.

## Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at:
```text
http://127.0.0.1:8000
```

Health check: `http://127.0.0.1:8000/health`
API docs: `http://127.0.0.1:8000/docs`

You'll need a `.env` file inside `backend/` (see `.env.example`) with:
```text
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/course_optimizer
GEMINI_API_KEY=your_gemini_api_key_here
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:
```text
http://localhost:5173
```

## How the Scheduling Algorithm Works

1. **Eligibility check** — `get_eligible_courses` filters the full course list down to courses the student hasn't completed and has satisfied all prerequisites for.
2. **Generation** — `generate_valid_schedules` recursively explores combinations of course sections (including skipping a course entirely), rejecting any combination with a time conflict, and pruning early as soon as a conflict is detected.
3. **Filtering** — only combinations whose total credit hours fall within the requested range are kept.
4. **Ranking** — `score_schedule` assigns a score starting at 100, then applies penalties for time gaps between classes, classes before the preferred start time, and classes on avoided days. `rank_schedules` sorts all valid schedules by this score.

## How AI Preference Parsing Works

1. The user types a natural-language request (e.g. "15 credit hours, no Fridays, nothing before 10am") into the frontend.
2. The request is sent to `POST /ai/parse-preferences`, which calls `parse_preferences_with_ai` in `app/ai.py`.
3. Gemini is prompted to return *only* structured JSON matching a fixed schema (credit hours, unavailable times, earliest/latest class time, avoided days) — it does not see the course catalog and cannot invent constraints beyond what the user stated.
4. These structured preferences are passed to `POST /schedules/{student_id}/with-preferences`, which converts them into a scoring dictionary used by the existing `rank_schedules` function — the same deterministic ranking logic used everywhere else in the app.

## Development Roadmap / Future Improvements

- Expand sample data to 15–25 courses across multiple eligible students
- Add `explain_schedule_with_ai` to the frontend, so each schedule shows a plain-English explanation of why it was recommended
- Treat hard-avoid preferences (e.g. "I cannot take classes on Friday, no exceptions") as exclusion filters rather than scoring penalties
- Add a basic rate-limit-aware queue or caching layer for AI requests
- User accounts and saved schedules
- Deployment (Vercel for frontend, Render/Railway for backend, hosted MySQL)
- `.ics` calendar export