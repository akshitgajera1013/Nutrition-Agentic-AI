<div align="center">

# 🥗 NutriGuide — Nutrition Agentic AI

### Powered by IBM Granite 3.3 · Watsonx.ai · Flask

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![IBM Granite](https://img.shields.io/badge/IBM%20Granite-3.3%208B%20Instruct-0f62fe?logo=ibm&logoColor=white)](https://www.ibm.com/products/watsonx-ai)
[![Watsonx.ai](https://img.shields.io/badge/Watsonx.ai-Enabled-6929c4?logo=ibm&logoColor=white)](https://www.ibm.com/watsonx)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Ethical AI](https://img.shields.io/badge/Ethical%20AI-HAM%20Principles-24a148)](https://www.ibm.com/artificial-intelligence/ethics)

**A full-stack Agentic AI web application that generates personalized 7-day nutrition plans using IBM Granite LLM, with built-in ethical guardrails, HAM principles, and medical safety disclaimers.**

[🚀 Quick Start](#-quick-start) · [✨ Features](#-features) · [🏗️ Architecture](#️-architecture) · [📸 Screenshots](#-screenshots) · [⚙️ Configuration](#️-configuration) · [📁 Project Structure](#-project-structure)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **IBM Granite LLM** | Uses `ibm/granite-3-3-8b-instruct` via Watsonx.ai for intelligent plan generation |
| 👤 **User Profiling** | Collects name, age, diet preference, medical history, and location |
| 📋 **7-Day Meal Plans** | Detailed breakfast, lunch, dinner & snack recommendations per day |
| 📊 **Macro Targets** | Personalised calorie, protein, carb, fat and fibre targets |
| 💬 **Q&A Agent** | Multi-turn nutrition question answering in context of user profile |
| 🛡️ **Ethical Guardrails** | Input validation, harmful content detection, LLM output sanitisation |
| ⚕️ **Medical Disclaimers** | Auto-generated, condition-specific medical safety disclaimers |
| 🌿 **HAM Principles** | Helpful, Accurate & Meaningful AI responses throughout |
| 📥 **Markdown Export** | Download personalised plan as a `.md` file |
| 🌐 **Web UI** | Responsive single-page application with dark-header design |
| 🎯 **Demo Mode** | Runs fully without an API key using structured demo responses |

---

## 🚀 Quick Start

### Option A — Windows One-Click Launch (Recommended)

```bat
git clone https://github.com/akshitgajera1013/Nutrition-Agentic-AI.git
cd Nutrition-Agentic-AI
run.bat
```

The `run.bat` launcher will:
1. ✅ Verify Python 3.9+ is installed
2. ✅ Create a Python virtual environment (`venv/`)
3. ✅ Install all dependencies from `requirements.txt`
4. ✅ Prompt for optional IBM Watsonx API credentials
5. ✅ Start the Flask server at **http://localhost:5000**
6. ✅ Auto-open the browser

---

### Option B — Manual Setup (All Platforms)

#### 1. Clone the repository
```bash
git clone https://github.com/akshitgajera1013/Nutrition-Agentic-AI.git
cd Nutrition-Agentic-AI
```

#### 2. Create and activate virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure environment variables
```bash
cp .env.example .env
# Open .env and fill in your IBM Watsonx credentials (optional — see below)
```

#### 5. Run the application
```bash
python app.py
```

#### 6. Open the app
Navigate to **http://localhost:5000** in your browser.

---

## ⚙️ Configuration

### IBM Watsonx.ai Credentials (Optional)

The app runs in **Demo Mode** without credentials. To enable live IBM Granite responses:

1. Sign up at [IBM Watsonx.ai](https://www.ibm.com/products/watsonx-ai)
2. Create a project and generate an API key
3. Edit your `.env` file:

```env
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
FLASK_SECRET_KEY=your_random_secret_key
FLASK_PORT=5000
FLASK_DEBUG=False
```

> 💡 **Never commit your `.env` file** — it is already listed in `.gitignore`.

### IBM Granite Model

| Setting | Value |
|---------|-------|
| Model ID | `ibm/granite-3-3-8b-instruct` |
| Platform | IBM Watsonx.ai |
| Max Tokens | 2048 |
| Temperature | 0.7 |
| SDK | `ibm-watsonx-ai` |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (Web UI)                        │
│              HTML + CSS + Vanilla JavaScript                 │
│         Form → Fetch API → Marked.js (MD render)            │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────▼─────────────────────────────────┐
│                   Flask Backend (app.py)                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Guardrails  │  │  Plan Agent  │  │   Q&A Agent       │  │
│  │ (guardrails  │  │  (generate_  │  │ (answer_nutrition_ │  │
│  │  .py)        │  │  nutrition_  │  │  query)            │  │
│  │  - Validate  │  │  plan)       │  │  - Context-aware  │  │
│  │  - HAM check │  │  - Prompt    │  │  - Guardrailed    │  │
│  │  - Sanitise  │  │    building  │  │  - Disclaimered   │  │
│  └──────────────┘  └──────┬───────┘  └────────┬──────────┘  │
│                           │                   │              │
│  ┌────────────────────────▼───────────────────▼───────────┐ │
│  │           IBM Watsonx.ai SDK (ibm-watsonx-ai)          │ │
│  │           Model: ibm/granite-3-3-8b-instruct           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────┐   ┌─────────────────────────────┐  │
│  │  disclaimer.py      │   │   plans/ (.md file export)  │  │
│  │  Medical disclaimers│   │   Auto-saved per request    │  │
│  └─────────────────────┘   └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────▼──────────────┐
              │     IBM Watsonx.ai Cloud   │
              │   granite-3-3-8b-instruct  │
              └────────────────────────────┘
```

### Agentic AI SDLC Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 1. Requirements | User profiles, LLM selection, ethics framework | ✅ |
| 2. Architecture | Flask + IBM Granite + REST API design | ✅ |
| 3. Agent Design | Multi-turn Q&A, tool use, guardrails pipeline | ✅ |
| 4. Development | Backend agent, frontend SPA, markdown export | ✅ |
| 5. Guardrails | Input validation, harmful content detection, disclaimers | ✅ |
| 6. Testing | Edge cases, ethical red-teaming, demo mode | ✅ |
| 7. Deployment | Local server with `.bat` launcher | ✅ |
| 8. Monitoring | Request logging, plan export audit trail | ✅ |

---

## 📁 Project Structure

```
Nutrition-Agentic-AI/
│
├── app.py                  # 🐍 Flask backend — IBM Granite agent logic
├── guardrails.py           # 🛡️  Ethics & safety guardrails module
├── disclaimer.py           # ⚕️  Medical disclaimer generator
├── requirements.txt        # 📦 Python dependencies
├── .env.example            # 🔑 Environment variable template (safe to commit)
├── run.bat                 # 🚀 One-click Windows launcher
├── README.md               # 📖 This file
├── .gitignore              # 🚫 Git ignore rules
│
├── templates/
│   └── index.html          # 🌐 Single-page web application (Jinja2)
│
├── static/
│   ├── style.css           # 🎨 Application styles (IBM design language)
│   └── app.js              # ⚡ Frontend JavaScript (Fetch API + Marked.js)
│
└── plans/                  # 📂 Auto-saved nutrition plan .md files
    └── sample_nutrition_plan.md
```

---

## 🛡️ Ethical AI & Guardrails

This application follows IBM's Responsible AI principles:

### Input Guardrails
- ✅ Full form validation (name, age 5–110, valid diet types, location)
- ✅ Harmful keyword detection (25+ dangerous terms blocked)
- ✅ High-risk condition flagging (15+ conditions trigger enhanced disclaimers)
- ✅ Query length limits (500 char max) to prevent prompt injection

### LLM Output Guardrails
- ✅ Post-generation harmful content scan on all LLM responses
- ✅ System prompt embeds HAM principles and ethical constraints
- ✅ Explicit blocks: no diagnoses, no medication dosing, no extreme diets
- ✅ Automatic fallback to safe message if harmful output detected

### HAM Principles Applied
| Principle | Implementation |
|-----------|---------------|
| **Helpful** | Actionable meal plans, grocery lists, local food suggestions |
| **Accurate** | WHO/FDA guidelines embedded in system prompt |
| **Meaningful** | Structured markdown output, tables, clear sections |

### Medical Safety
- Every plan ends with a full medical disclaimer
- High-risk conditions (diabetes, kidney disease, cancer, etc.) trigger enhanced warnings
- Q&A responses append a short disclaimer
- No medication advice is ever generated

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serve the web application |
| `POST` | `/api/generate-plan` | Generate personalised nutrition plan |
| `POST` | `/api/ask` | Answer a nutrition question (Q&A agent) |
| `GET` | `/api/download-plan/<filename>` | Download saved `.md` plan |
| `GET` | `/api/health` | Health check — LLM connection status |

### POST `/api/generate-plan` — Request Body
```json
{
  "name": "Priya Sharma",
  "age": 35,
  "diet_preference": "Vegetarian",
  "medical_history": "Type 2 diabetes",
  "location_city": "Mumbai",
  "location_country": "India"
}
```

### POST `/api/ask` — Request Body
```json
{
  "query": "What are the best protein sources for a vegetarian?",
  "name": "Priya Sharma",
  "age": 35,
  "diet_preference": "Vegetarian",
  "medical_history": "Type 2 diabetes",
  "location_city": "Mumbai",
  "location_country": "India"
}
```

---

## 📋 Requirements

| Requirement | Minimum Version |
|-------------|----------------|
| Python | 3.9+ |
| Flask | 3.0.3 |
| ibm-watsonx-ai | 1.1.2 |
| flask-cors | 4.0.1 |
| python-dotenv | 1.0.1 |
| markdown | 3.6 |
| requests | 2.32.3 |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## ⚕️ Medical Disclaimer

> **NutriGuide provides general nutritional information only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider (physician, registered dietitian) before making significant dietary changes — especially if you have existing medical conditions.**

---

<div align="center">

**NutriGuide Agentic AI** · Built with ❤️ using IBM Granite & Watsonx.ai

*Following Ethical AI · HAM Principles · WHO & FDA Nutritional Guidelines*

</div>
