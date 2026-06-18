from fastapi import APIRouter
from pydantic import BaseModel
from app.ai import parse_preferences_with_ai

router = APIRouter()


class PreferenceRequest(BaseModel):
    message: str


@router.post("/ai/parse-preferences")
def parse_preferences(request: PreferenceRequest):
    parsed = parse_preferences_with_ai(request.message)
    return parsed
