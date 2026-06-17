# Campus Course-Schedule Optimizer with AI Planning Assistant

## Project Overview

Campus Course-Schedule Optimizer is a full-stack web application that helps students generate valid semester schedules based on completed courses, prerequisites, class times, credit-hour goals, and personal preferences.

The app uses a deterministic backend scheduling engine to validate prerequisites, detect class-time conflicts, filter by credit hours, and rank possible schedules. Claude AI is planned for natural-language preference parsing and schedule explanations, but the backend remains the source of truth for all scheduling rules.

## Problem Being Solved

College students often struggle to choose classes even with the help of advisors because they must balance prerequisites, required courses, class availability, work schedules, preferred times, and credit-hour limits. This project solves that problem by automatically generating valid schedule options and ranking them based on student preferences.

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

### Planned AI Integration

- Claude API
- Anthropic Python SDK

## Current Status

Week 1 progress:

- Project repository created
- FastAPI backend initialized
- `/health` endpoint added
- React frontend initialized with Vite
- Basic homepage created

## Planned Core Features

- Course database
- Course prerequisite relationships
- Course section data
- Completed-course selection
- Prerequisite validation
- Time-conflict detection
- Credit-hour filtering
- Schedule generation
- Schedule ranking
- Claude-powered natural-language preference parsing
- Schedule explanation assistant
- Automated tests
- Live deployment

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

Health check:

```text
http://127.0.0.1:8000/health
```

API docs:

```text
http://127.0.0.1:8000/docs
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

## Development Roadmap

1. Backend setup
2. Database setup
3. Prerequisite validation
4. Conflict detection
5. Schedule generation
6. Schedule ranking
7. Frontend interface
8. Claude integration
9. Testing
10. Deployment and demo polish