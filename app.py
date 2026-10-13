"""
app.py — Nutrition Agentic AI Backend
IBM Granite LLM powered nutrition planning agent with Flask web server.

Agentic AI SDLC Phase 3: Core Agent Implementation
- IBM Granite model via Watsonx.ai SDK
- Multi-turn conversation support
- Nutrition plan generation
- Query answering agent
- Markdown plan export
"""

import os
import re
import json
import logging
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# IBM Watsonx.ai SDK
try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False

from guardrails import (
    validate_user_input,
    check_harmful_content,
    flag_high_risk_conditions,
    sanitize_llm_response,
    build_system_prompt,
)
from disclaimer import get_medical_disclaimer, get_query_disclaimer

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "nutrition-ai-secret-2024")
CORS(app)

PLANS_DIR = Path("plans")
PLANS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# IBM Granite Model Initialization
# ---------------------------------------------------------------------------
def get_granite_model():
    """Initialize IBM Granite model via Watsonx.ai."""
    api_key = os.getenv("WATSONX_API_KEY", "")
    project_id = os.getenv("WATSONX_PROJECT_ID", "")
    url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    if not api_key or api_key == "your_ibm_watsonx_api_key_here":
        logger.warning("IBM Watsonx API key not configured — running in demo mode.")
        return None

    if not WATSONX_AVAILABLE:
        logger.warning("ibm-watsonx-ai package not installed — running in demo mode.")
        return None

    try:
        credentials = Credentials(url=url, api_key=api_key)
        client = APIClient(credentials)
        model = ModelInference(
            model_id="ibm/granite-3-3-8b-instruct",
            api_client=client,
            project_id=project_id,
            params={
                GenParams.MAX_NEW_TOKENS: 2048,
                GenParams.MIN_NEW_TOKENS: 100,
                GenParams.TEMPERATURE: 0.7,
                GenParams.TOP_P: 0.9,
                GenParams.TOP_K: 50,
                GenParams.REPETITION_PENALTY: 1.1,
                GenParams.STOP_SEQUENCES: ["<|endoftext|>", "###"],
            }
        )
        logger.info("IBM Granite model initialized successfully.")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize IBM Granite model: {e}")
        return None


granite_model = get_granite_model()


# ---------------------------------------------------------------------------
# Agent: Nutrition Plan Generator
# ---------------------------------------------------------------------------
def generate_nutrition_plan(user_profile: dict) -> dict:
    """
    Core agentic function: generates a personalized nutrition plan.
    Uses IBM Granite LLM or falls back to a structured demo plan.
    """
    flagged = flag_high_risk_conditions(user_profile.get("medical_history", ""))
    system_prompt = build_system_prompt(user_profile, flagged)
    disclaimer = get_medical_disclaimer(user_profile.get("name", "User"), flagged)

    if granite_model:
        try:
            # Build the full prompt for IBM Granite (instruct format)
            full_prompt = (
                f"<|system|>\n{system_prompt}\n"
                f"<|user|>\nPlease generate my personalized 7-day nutrition plan.\n"
                f"<|assistant|>\n"
            )
            response = granite_model.generate_text(prompt=full_prompt)
            plan_content = sanitize_llm_response(response)
            plan_content += disclaimer
            source = "IBM Granite 3.3 8B Instruct (Watsonx.ai)"
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            plan_content = _demo_nutrition_plan(user_profile) + disclaimer
            source = "Demo Mode (LLM unavailable)"
    else:
        plan_content = _demo_nutrition_plan(user_profile) + disclaimer
        source = "Demo Mode (Configure WATSONX_API_KEY to use IBM Granite)"

    return {
        "plan": plan_content,
        "flagged_conditions": flagged,
        "source": source,
        "generated_at": datetime.now().isoformat(),
    }


# ---------------------------------------------------------------------------
# Agent: Q&A Query Handler
# ---------------------------------------------------------------------------
def answer_nutrition_query(query: str, user_profile: dict) -> str:
    """
    Agentic Q&A: answers user nutrition questions in context of their profile.
    """
    is_harmful, reason = check_harmful_content(query)
    if is_harmful:
        return reason

    flagged = flag_high_risk_conditions(user_profile.get("medical_history", ""))

    qa_system = f"""You are NutriGuide, an ethical AI nutrition assistant powered by IBM Granite.
Answer the user's nutrition question accurately, helpfully, and in a respectful tone.
Base your answer on established nutrition science and guidelines.

User Profile Context:
- Age: {user_profile.get('age', 'unknown')} years
- Diet: {user_profile.get('diet_preference', 'not specified')}
- Medical History: {user_profile.get('medical_history', 'none')}
- Location: {user_profile.get('location_city', '')}, {user_profile.get('location_country', '')}

GUARDRAILS:
- Do not diagnose or prescribe medications.
- If the question requires specialist medical advice, say so clearly.
- Keep response concise (under 300 words).
- End with a brief note to consult a healthcare professional if relevant.
"""

    if granite_model:
        try:
            full_prompt = (
                f"<|system|>\n{qa_system}\n"
                f"<|user|>\n{query}\n"
                f"<|assistant|>\n"
            )
            response = granite_model.generate_text(prompt=full_prompt)
            answer = sanitize_llm_response(response)
        except Exception as e:
            logger.error(f"QA generation error: {e}")
            answer = _demo_qa_answer(query, user_profile)
    else:
        answer = _demo_qa_answer(query, user_profile)

    answer += get_query_disclaimer()
    return answer


# ---------------------------------------------------------------------------
# Demo Fallback Content (when LLM not configured)
# ---------------------------------------------------------------------------
def _demo_nutrition_plan(profile: dict) -> str:
    name = profile.get("name", "User")
    age = profile.get("age", 30)
    diet = profile.get("diet_preference", "Vegetarian")
    medical = profile.get("medical_history", "None")
    city = profile.get("location_city", "Your City")
    country = profile.get("location_country", "Your Country")

    # Simple age-based calorie estimate (Mifflin-St Jeor approximation)
    try:
        age_int = int(age)
        if age_int < 18:
            calories = 1800
        elif age_int < 40:
            calories = 2000
        elif age_int < 60:
            calories = 1800
        else:
            calories = 1600
    except Exception:
        calories = 2000

    is_diabetic = "diabet" in str(medical).lower()
    is_bp = "blood pressure" in str(medical).lower() or "hypertension" in str(medical).lower()

    avoid_note = ""
    if is_diabetic:
        avoid_note += "\n- ⚠️ **Diabetes Management**: Limit refined sugars, white bread, and high-GI foods. Prefer complex carbohydrates."
    if is_bp:
        avoid_note += "\n- ⚠️ **Blood Pressure**: Reduce sodium intake. Follow DASH diet principles. Limit processed foods."

    veg_icon = "🥗" if "veg" in diet.lower() else "🍗"

    return f"""# 🥗 Personalized 7-Day Nutrition Plan for {name}

**Generated by NutriGuide AI** | {datetime.now().strftime("%B %d, %Y")}
**Location**: {city}, {country} | **Diet**: {diet} {veg_icon} | **Age**: {age}

---

## 📊 Daily Nutritional Targets

| Nutrient | Daily Target |
|----------|-------------|
| **Calories** | ~{calories} kcal |
| **Protein** | {int(calories * 0.20 / 4)}g (20% of calories) |
| **Carbohydrates** | {int(calories * 0.50 / 4)}g (50% of calories) |
| **Healthy Fats** | {int(calories * 0.30 / 9)}g (30% of calories) |
| **Fiber** | 25–38g |
| **Water** | 8–10 glasses/day |

---

## ⚠️ Personalized Dietary Notes
{avoid_note if avoid_note else "- No specific restrictions flagged. Maintain a balanced, whole-foods diet."}

---

## 🗓️ 7-Day Meal Plan

### Day 1 — Monday

| Meal | Food | Approx. Calories |
|------|------|-----------------|
| 🌅 Breakfast | Oatmeal with banana, nuts & low-fat milk | ~350 kcal |
| 🌞 Lunch | Lentil soup + whole wheat roti + mixed salad | ~500 kcal |
| 🍎 Snack | Apple + a handful of almonds | ~200 kcal |
| 🌙 Dinner | Grilled vegetables + brown rice + dal | ~550 kcal |

### Day 2 — Tuesday

| Meal | Food | Approx. Calories |
|------|------|-----------------|
| 🌅 Breakfast | Whole wheat toast + avocado + boiled egg (if non-veg) or tofu | ~320 kcal |
| 🌞 Lunch | Chickpea curry + quinoa + cucumber raita | ~520 kcal |
| 🍎 Snack | Greek yogurt + mixed berries | ~180 kcal |
| 🌙 Dinner | Stir-fried tofu/chicken + steamed broccoli + brown rice | ~560 kcal |

### Day 3 — Wednesday

| Meal | Food | Approx. Calories |
|------|------|-----------------|
| 🌅 Breakfast | Smoothie: spinach, banana, almond milk, chia seeds | ~280 kcal |
| 🌞 Lunch | Vegetable biryani + cooling mint chutney + side salad | ~510 kcal |
| 🍎 Snack | Hummus + carrot sticks + whole grain crackers | ~210 kcal |
| 🌙 Dinner | Paneer/tofu tikka + sautéed spinach + multigrain roti | ~540 kcal |

### Day 4 — Thursday

| Meal | Food | Approx. Calories |
|------|------|-----------------|
| 🌅 Breakfast | Poha (flattened rice) with vegetables and sprouts | ~300 kcal |
| 🌞 Lunch | Rajma (kidney beans) curry + brown rice + salad | ~530 kcal |
| 🍎 Snack | Orange + walnuts | ~190 kcal |
| 🌙 Dinner | Mixed vegetable stew + whole wheat bread | ~520 kcal |

### Day 5 — Friday

| Meal | Food | Approx. Calories |
|------|------|-----------------|
| 🌅 Breakfast | Upma with vegetables + coconut chutney | ~310 kcal |
| 🌞 Lunch | Black bean tacos / wraps + guacamole + salsa | ~490 kcal |
| 🍎 Snack | Banana + peanut butter (1 tbsp) | ~200 kcal |
| 🌙 Dinner | Baked sweet potato + steamed green beans + lentil patties | ~530 kcal |

### Day 6 — Saturday

| Meal | Food | Approx. Calories |
|------|------|-----------------|
| 🌅 Breakfast | Whole grain pancakes + fresh fruit + maple syrup (small) | ~370 kcal |
| 🌞 Lunch | Minestrone soup + crusty whole grain bread | ~460 kcal |
| 🍎 Snack | Mixed fruit bowl + chia pudding | ~220 kcal |
| 🌙 Dinner | Mushroom + vegetable curry + basmati rice | ~550 kcal |

### Day 7 — Sunday

| Meal | Food | Approx. Calories |
|------|------|-----------------|
| 🌅 Breakfast | Vegetable omelette / tofu scramble + whole wheat toast | ~340 kcal |
| 🌞 Lunch | Palak paneer / spinach dal + roti + salad | ~510 kcal |
| 🍎 Snack | Trail mix (nuts, seeds, dried fruit) | ~230 kcal |
| 🌙 Dinner | Vegetable stir fry with noodles/rice + miso soup | ~540 kcal |

---

## 💧 Hydration Guidelines

- Drink **8–10 glasses (2–2.5 litres)** of water daily
- Start each morning with a glass of warm water with lemon
- Avoid sugary drinks, excessive tea/coffee (max 2 cups/day)
- Coconut water is an excellent natural electrolyte option

---

## 🌿 Key Nutrients to Focus On

| Nutrient | Why Important | Best Sources |
|----------|--------------|-------------|
| **Iron** | Energy, blood health | Lentils, spinach, fortified cereals |
| **Calcium** | Bone strength | Dairy/plant milk, tofu, sesame seeds |
| **Vitamin B12** | Nerve function | Fortified foods, dairy (supplement if vegan) |
| **Omega-3** | Heart & brain health | Flaxseeds, walnuts, chia seeds |
| **Vitamin D** | Immunity, bone health | Sunlight, fortified milk, mushrooms |
| **Zinc** | Immune function | Legumes, nuts, seeds |

---

## 🏃 Lifestyle Tips for {city}, {country}

- Include **local seasonal vegetables** for maximum nutrition and cost efficiency
- Visit your local **farmer's market** for fresh produce
- Practice **mindful eating** — eat slowly and without screens
- Aim for **30 minutes of moderate exercise** daily (walking, yoga, cycling)
- Maintain a **consistent meal schedule** to regulate metabolism

---

## 🛒 Weekly Grocery List Highlights

**Grains & Legumes**: Oats, brown rice, quinoa, lentils, chickpeas, kidney beans
**Vegetables**: Spinach, broccoli, sweet potato, tomatoes, carrots, bell peppers
**Fruits**: Banana, apple, berries, orange, mango (seasonal)
**Proteins**: Tofu, paneer, eggs (if applicable), Greek yogurt
**Nuts & Seeds**: Almonds, walnuts, flaxseeds, chia seeds, pumpkin seeds
**Others**: Olive oil, whole wheat bread/roti, low-fat milk/plant milk

---
"""


def _demo_qa_answer(query: str, profile: dict) -> str:
    query_lower = query.lower()

    if "protein" in query_lower:
        return (
            f"**Protein Needs** 💪\n\n"
            f"For a {profile.get('age', 'adult')}-year-old following a {profile.get('diet_preference', 'balanced')} diet, "
            f"the general recommendation is **0.8–1.2g of protein per kg of body weight** per day.\n\n"
            f"**Great {profile.get('diet_preference', '')} protein sources include:**\n"
            f"- Lentils & legumes (18g per cup)\n"
            f"- Greek yogurt (17g per cup)\n"
            f"- Tofu (20g per 100g)\n"
            f"- Quinoa (8g per cup)\n"
            f"- Chickpeas (15g per cup)\n\n"
            f"Spread protein intake across all meals for optimal absorption."
        )
    elif "vitamin" in query_lower or "supplement" in query_lower:
        return (
            "**Vitamins & Supplements Guidance** 🌿\n\n"
            "For a balanced diet, focus on getting nutrients from whole foods first.\n\n"
            "**Commonly recommended supplements for vegetarians/vegans:**\n"
            "- **Vitamin B12** — essential if avoiding animal products\n"
            "- **Vitamin D3** — especially in low-sunlight regions\n"
            "- **Iron** — if feeling fatigued (get tested first)\n"
            "- **Omega-3 (algae-based)** — for brain and heart health\n\n"
            "Always consult your doctor before starting any supplement regimen."
        )
    elif "weight" in query_lower or "lose" in query_lower or "gain" in query_lower:
        return (
            "**Weight Management Basics** ⚖️\n\n"
            "Sustainable weight management focuses on **lifestyle changes**, not crash diets:\n\n"
            "**For weight loss:**\n"
            "- Create a moderate calorie deficit (300–500 kcal/day)\n"
            "- Prioritise whole foods, fibre, and protein\n"
            "- Stay hydrated and exercise regularly\n\n"
            "**For weight gain:**\n"
            "- Eat calorie-dense, nutrient-rich foods\n"
            "- Add healthy fats (nuts, avocado, olive oil)\n"
            "- Include strength training\n\n"
            "Avoid extreme approaches — gradual change is sustainable and safe."
        )
    elif "water" in query_lower or "hydrat" in query_lower:
        return (
            "**Hydration Guidelines** 💧\n\n"
            "The general recommendation is **8–10 glasses (2–2.5 litres)** of water per day.\n\n"
            "**Tips to stay hydrated:**\n"
            "- Start your morning with a glass of water\n"
            "- Eat water-rich foods (cucumber, watermelon, oranges)\n"
            "- Drink water before each meal\n"
            "- Carry a reusable water bottle\n"
            "- Coconut water is great for electrolytes\n\n"
            "Needs increase with exercise, hot weather, and illness."
        )
    else:
        return (
            f"**Nutrition Guidance** 🥗\n\n"
            f"Thank you for your question about: *\"{query}\"*\n\n"
            f"Based on your profile ({profile.get('diet_preference', 'balanced')} diet, age {profile.get('age', 'adult')}), "
            f"here are some general evidence-based guidelines:\n\n"
            f"- Focus on **whole, minimally processed foods**\n"
            f"- Eat a **rainbow of vegetables** daily for micronutrients\n"
            f"- Balance your **macronutrients**: carbs (50%), protein (20%), healthy fats (30%)\n"
            f"- Limit **added sugars, saturated fats, and sodium**\n"
            f"- Practice **mindful eating** and regular meal timing\n\n"
            f"For more specific guidance related to your question, please consult a registered dietitian."
        )


# ---------------------------------------------------------------------------
# Save Plan to Markdown File
# ---------------------------------------------------------------------------
def save_plan_to_markdown(user_profile: dict, plan_content: str) -> str:
    """Save the nutrition plan as a .md file and return the filename."""
    safe_name = re.sub(r"[^A-Za-z0-9_-]", "_", user_profile.get("name", "user"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{timestamp}_nutrition_plan.md"
    filepath = PLANS_DIR / filename

    header = f"""---
title: "Nutrition Plan for {user_profile.get('name', 'User')}"
generated: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
model: "IBM Granite 3.3 8B Instruct (ibm/granite-3-3-8b-instruct)"
app: "NutriGuide Agentic AI"
---

"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header + plan_content)

    logger.info(f"Plan saved: {filepath}")
    return filename


# ---------------------------------------------------------------------------
# Flask Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate-plan", methods=["POST"])
def api_generate_plan():
    """Generate a personalized nutrition plan."""
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Guardrail: Input validation
        is_valid, error_msg = validate_user_input(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 422

        # Guardrail: Check medical history for harmful content
        medical = data.get("medical_history", "")
        if medical:
            is_harmful, harm_reason = check_harmful_content(medical)
            if is_harmful:
                return jsonify({"error": harm_reason}), 422

        user_profile = {
            "name": data.get("name", "").strip(),
            "age": int(data.get("age")),
            "diet_preference": data.get("diet_preference", "").strip(),
            "medical_history": data.get("medical_history", "None").strip(),
            "location_city": data.get("location_city", "").strip(),
            "location_country": data.get("location_country", "").strip(),
        }

        result = generate_nutrition_plan(user_profile)

        # Auto-save plan
        filename = save_plan_to_markdown(user_profile, result["plan"])
        result["saved_file"] = filename

        logger.info(f"Plan generated for user: {user_profile['name']}")
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in /api/generate-plan: {e}")
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


@app.route("/api/ask", methods=["POST"])
def api_ask():
    """Answer a nutrition query in context of user profile."""
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No data provided"}), 400

        query = str(data.get("query", "")).strip()
        if not query or len(query) < 3:
            return jsonify({"error": "Please enter a valid question."}), 422
        if len(query) > 500:
            return jsonify({"error": "Query too long. Please limit to 500 characters."}), 422

        # Guardrail: Check query for harmful content
        is_harmful, harm_reason = check_harmful_content(query)
        if is_harmful:
            return jsonify({"error": harm_reason}), 422

        user_profile = {
            "name": data.get("name", "User"),
            "age": data.get("age", 30),
            "diet_preference": data.get("diet_preference", ""),
            "medical_history": data.get("medical_history", ""),
            "location_city": data.get("location_city", ""),
            "location_country": data.get("location_country", ""),
        }

        answer = answer_nutrition_query(query, user_profile)
        return jsonify({"answer": answer}), 200

    except Exception as e:
        logger.error(f"Error in /api/ask: {e}")
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


@app.route("/api/download-plan/<filename>")
def download_plan(filename):
    """Download a saved nutrition plan as .md file."""
    # Guardrail: prevent directory traversal
    safe_name = re.sub(r"[^A-Za-z0-9_.\-]", "", filename)
    filepath = PLANS_DIR / safe_name
    if not filepath.exists():
        return jsonify({"error": "Plan file not found."}), 404
    return send_file(filepath, as_attachment=True, download_name=safe_name)


@app.route("/api/health")
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "app": "NutriGuide Agentic AI",
        "model": "IBM Granite 3.3 8B Instruct",
        "llm_connected": granite_model is not None,
        "timestamp": datetime.now().isoformat(),
    })


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    logger.info(f"🥗 NutriGuide Agentic AI starting on http://localhost:{port}")
    logger.info(f"🤖 IBM Granite model: {'Connected' if granite_model else 'Demo Mode'}")
    app.run(host="0.0.0.0", port=port, debug=debug)
