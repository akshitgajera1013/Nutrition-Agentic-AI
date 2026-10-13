"""
disclaimer.py — Medical disclaimer generator for Nutrition Agentic AI
"""


def get_medical_disclaimer(user_name: str = "User", flagged_conditions: list = None) -> str:
    """
    Generate a contextual medical disclaimer.
    Emphasises extra caution when high-risk conditions are flagged.
    """
    flagged_conditions = flagged_conditions or []

    base_disclaimer = f"""
---

## ⚕️ Medical Disclaimer

**Important — Please Read Carefully**

Dear {user_name},

The nutrition plan and information provided by **NutriGuide (Nutrition Agentic AI)** is intended for **general informational and educational purposes only**.

This content:
- ❌ Does **NOT** constitute medical advice, diagnosis, or treatment
- ❌ Does **NOT** replace consultation with a qualified physician, registered dietitian, or other licensed healthcare professional
- ❌ Should **NOT** be used as the sole basis for health or dietary decisions

Before making any significant changes to your diet, especially if you have existing medical conditions, please consult:
- 🩺 Your **primary care physician**
- 🥗 A **registered dietitian (RD)** or **registered dietitian nutritionist (RDN)**
- 💊 Your **specialist** for any condition-specific guidance

**Individual nutritional needs vary** based on many factors including genetics, activity level, medications, and evolving health status. The recommendations provided are general guidelines only.

In case of a medical emergency, call your local emergency services immediately.

*NutriGuide AI — Powered by IBM Granite | Following WHO & FDA Nutritional Guidelines*
"""

    if flagged_conditions:
        conditions_str = ", ".join(c.title() for c in flagged_conditions)
        condition_extra = f"""
> ⚠️ **Additional Notice**: Your profile indicates you may have the following condition(s): **{conditions_str}**.
> These conditions require **specialist medical supervision** for any dietary changes.
> The nutrition plan above is a **general starting point only** — please work with your healthcare team to adapt it safely.
"""
        return base_disclaimer.replace(
            "*NutriGuide AI",
            condition_extra + "\n*NutriGuide AI"
        )

    return base_disclaimer


def get_query_disclaimer() -> str:
    """Short disclaimer appended to Q&A responses."""
    return (
        "\n\n---\n"
        "*⚕️ This response is for informational purposes only and does not constitute "
        "medical advice. Consult a healthcare professional for personal guidance.*"
    )
