"""
Authentication and Onboarding Router.
Multi-user session management, persona selection, and profile configuration.
"""
from fastapi import APIRouter, HTTPException
from apps.api.schemas.api_schemas import UserProfile, OnboardingRequest

router = APIRouter(prefix="/auth", tags=["auth"])

CURRENT_USER = UserProfile(
    user_id="usr-reviewer-01",
    persona_key="ai_engineer",
    display_name="Alex Morgan",
    headline="Senior AI/ML & LLM Systems Engineer",
    hourly_rate=65.0,
    min_budget=500.0,
    weekly_connects_budget=80,
    marketplace_mode="gigsim"
)

@router.get("/me", response_model=UserProfile)
def get_current_user():
    return CURRENT_USER

@router.post("/onboarding", response_model=UserProfile)
def onboard_user(req: OnboardingRequest):
    global CURRENT_USER
    CURRENT_USER = UserProfile(
        user_id="usr-reviewer-01",
        persona_key=req.persona_key,
        display_name=req.display_name,
        headline=f"Specialist in {req.persona_key.replace('_', ' ').title()}",
        hourly_rate=req.hourly_rate,
        min_budget=req.min_budget,
        weekly_connects_budget=req.weekly_connects_budget,
        marketplace_mode=req.marketplace_mode
    )
    return CURRENT_USER

@router.post("/switch_persona/{persona_key}", response_model=UserProfile)
def switch_persona(persona_key: str):
    global CURRENT_USER
    personas = {
        "ai_engineer": ("Alex Morgan", "Senior AI/ML & LLM Systems Engineer", 65.0, 500.0),
        "fullstack_dev": ("Marcus Vance", "Principal Full-Stack Web Engineer", 60.0, 400.0),
        "data_analyst": ("Elena Rostova", "Lead Analytics & BI Engineer", 50.0, 350.0)
    }
    if persona_key not in personas:
        raise HTTPException(status_code=400, detail=f"Unknown persona: {persona_key}")
    name, title, rate, floor = personas[persona_key]
    CURRENT_USER.persona_key = persona_key
    CURRENT_USER.display_name = name
    CURRENT_USER.headline = title
    CURRENT_USER.hourly_rate = rate
    CURRENT_USER.min_budget = floor
    return CURRENT_USER

