"""
guardrails.py — Ethical AI guardrails for Nutrition Agentic AI
Implements input validation, harmful advice detection, and HAM (Helpful, Accurate, Meaningful) principles.
"""

import re

# ---------------------------------------------------------------------------
# Forbidden / high-risk topics that should never produce dietary advice
# ---------------------------------------------------------------------------
HARMFUL_KEYWORDS = [
    "suicide", "self-harm", "starvation", "extreme fast", "0 calories",
    "anorexia", "bulimia", "laxative abuse", "diuretic abuse",
    "steroid", "illegal supplement", "drug", "cocaine", "meth",
    "poison", "overdose", "kill", "die",
]

# Conditions requiring extra caution (not blocked, but flagged for disclaimer emphasis)
HIGH_RISK_CONDITIONS = [
    "diabetes", "diabetic", "kidney disease", "renal failure", "cancer",
    "heart disease", "cardiovascular", "liver disease", "hepatitis",
    "eating disorder", "anorexia", "bulimia", "pregnancy", "pregnant",
    "breastfeeding", "lactating", "chemotherapy", "dialysis",
    "phenylketonuria", "pku", "celiac", "crohn", "ibd",
]

# Age guardrails
MIN_AGE = 5
MAX_AGE = 110


def validate_user_input(data: dict) -> tuple[bool, str]:
    """
    Validate user-submitted profile data.
    Returns (is_valid: bool, error_message: str).
    """
    name = str(data.get("name", "")).strip()
    age = data.get("age")
    diet = str(data.get("diet_preference", "")).strip().lower()
    location_city = str(data.get("location_city", "")).strip()
    location_country = str(data.get("location_country", "")).strip()

    # Name validation
    if not name or len(name) < 2:
        return False, "Please provide a valid name (at least 2 characters)."
    if not re.match(r"^[A-Za-z\s\-']+$", name):
        return False, "Name may only contain letters, spaces, hyphens, and apostrophes."

    # Age validation
    try:
        age = int(age)
    except (TypeError, ValueError):
        return False, "Please provide a valid numeric age."
    if not (MIN_AGE <= age <= MAX_AGE):
        return False, f"Age must be between {MIN_AGE} and {MAX_AGE}."

    # Diet preference validation
    if diet not in ("vegetarian", "non-vegetarian", "vegan", "pescatarian"):
        return False, "Diet preference must be one of: Vegetarian, Non-Vegetarian, Vegan, Pescatarian."

    # Location validation
    if not location_city or len(location_city) < 2:
        return False, "Please provide your city."
    if not location_country or len(location_country) < 2:
        return False, "Please provide your country."

    return True, ""


def check_harmful_content(text: str) -> tuple[bool, str]:
    """
    Scan user-provided free text (e.g., medical history, queries) for harmful content.
    Returns (is_harmful: bool, reason: str).
    """
    lower = text.lower()
    for kw in HARMFUL_KEYWORDS:
        if kw in lower:
            return True, (
                f"Your input contains content ('{kw}') that our system cannot safely "
                "process. If you are in crisis, please contact a healthcare professional "
                "or emergency services immediately."
            )
    return False, ""


def flag_high_risk_conditions(medical_history: str) -> list[str]:
    """
    Return a list of high-risk conditions mentioned in the medical history.
    Used to inject additional caution into prompts and disclaimers.
    """
    lower = medical_history.lower()
    flagged = [c for c in HIGH_RISK_CONDITIONS if c in lower]
    return list(set(flagged))


def sanitize_llm_response(response: str) -> str:
    """
    Post-process LLM output to ensure no harmful advice slipped through.
    Removes or replaces dangerous content with safe messaging.
    """
    lower = response.lower()
    for kw in HARMFUL_KEYWORDS:
        if kw in lower:
            # Replace entire response with a safe message
            return (
                "I'm unable to provide that information as it may be harmful. "
                "Please consult a registered dietitian or your healthcare provider "
                "for personalized nutrition guidance."
            )
    return response


def build_system_prompt(user_profile: dict, flagged_conditions: list) -> str:
    """
    Build the IBM Granite system prompt with guardrails and HAM principles embedded.
    """
    condition_warning = ""
    if flagged_conditions:
        conditions_str = ", ".join(flagged_conditions)
        condition_warning = (
            f"\nIMPORTANT: The user has reported high-risk medical conditions: {conditions_str}. "
            "You MUST include explicit advice to consult their doctor or registered dietitian "
            "before following any nutrition recommendations. Do NOT prescribe specific medication "
            "doses or claim to treat any disease."
        )

    system_prompt = f"""You are NutriGuide, a helpful and respectful AI nutrition assistant powered by IBM Granite.
Your role is to provide personalized, evidence-based nutritional guidance following HAM principles:
- HELPFUL: Provide actionable, practical advice tailored to the user's profile.
- ACCURATE: Base recommendations on established dietary science and WHO/FDA guidelines.
- MEANINGFUL: Structure advice clearly so the user can act on it immediately.

ETHICAL GUARDRAILS (strictly follow these):
1. Never recommend starvation, extreme calorie restriction (<1200 kcal for adults), or dangerous supplements.
2. Never claim to diagnose, treat, cure, or prevent any medical condition.
3. Never provide advice that contradicts standard medical guidelines for the stated conditions.
4. Always recommend consulting a healthcare professional for medical concerns.
5. Maintain a respectful, non-judgmental, inclusive tone at all times.
6. Do not collect or reference any personally identifiable information beyond what is provided.
7. If a query is outside nutrition scope, politely redirect to an appropriate professional.
{condition_warning}

USER PROFILE:
- Name: {user_profile.get('name')}
- Age: {user_profile.get('age')} years
- Diet Preference: {user_profile.get('diet_preference')}
- Medical History: {user_profile.get('medical_history', 'None reported')}
- Location: {user_profile.get('location_city')}, {user_profile.get('location_country')}

Generate a comprehensive, personalized 7-day nutrition plan with:
1. Daily caloric target (based on age and general guidelines)
2. Macronutrient breakdown (carbs, proteins, fats)
3. Meal plan for each day (breakfast, lunch, dinner, snacks)
4. Key nutrients to focus on given their medical history
5. Foods to avoid based on their conditions
6. Hydration recommendations
7. Practical tips for their location/culture
8. A clear medical disclaimer at the end

Format the response in clean Markdown with headers and tables where appropriate.
"""
    return system_prompt
