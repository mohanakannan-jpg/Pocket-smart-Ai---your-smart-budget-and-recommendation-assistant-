"""Optional, bounded Gemini enrichment. Budget arithmetic never passes through here."""
import json, os
from pydantic import BaseModel, Field, ValidationError

class AIAdvice(BaseModel):
    title: str = Field(max_length=100)
    reason: str = Field(max_length=500)

def get_advice(planner_type: str, preferences: dict, remaining_minor: int, over_budget_minor: int) -> AIAdvice | None:
    key = os.getenv("GEMINI_API_KEY")
    if not key: return None
    try:
        # google-genai is the current SDK. JSON is validated before returning it.
        from google import genai
        client = genai.Client(api_key=key)
        prompt = (
            "You are a cautious budgeting assistant. Return JSON only with title and reason. "
            "Do not state or invent products, merchants, prices, links, availability, material quality, "
            "or arithmetic. Offer one practical trade-off based only on the supplied facts. "
            f"Planner: {planner_type}. Preferences: {json.dumps(preferences)[:1000]}. "
            f"Remaining minor units: {remaining_minor}. Over-budget minor units: {over_budget_minor}."
        )
        response = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"), contents=prompt,
            config={"response_mime_type":"application/json", "response_json_schema": AIAdvice.model_json_schema(), "temperature":0.2})
        return AIAdvice.model_validate_json(response.text or "")
    except (Exception, ValidationError):
        # A provider failure is intentionally indistinguishable from no AI advice to callers.
        return None
