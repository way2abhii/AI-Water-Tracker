# 💧 AI Water Tracker

> A personalised hydration tracking app powered by AI — built with Streamlit, SQLite, and OpenRouter LLMs.

![Python](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red?style=flat-square&logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightblue?style=flat-square&logo=sqlite)
![LLM](https://img.shields.io/badge/LLM-Llama%203.3%2070B-purple?style=flat-square)

---

## ✨ Features

- 🔐 **User Auth** — Signup & Login with hashed passwords, auto-assigned User ID
- 💧 **Water Logging** — Quick-log buttons (150ml–1000ml) or custom amounts with notes
- 📊 **Dashboard** — Daily progress bar, 7-day bar chart, metric cards
- 🤖 **AI Analysis** — Personalised hydration tips from Llama 3.3 70B via OpenRouter
- 📋 **History** — Per-day totals and full intake log table
- 👤 **Profile** — Edit name, weight, activity level; auto-recalculates daily goal
- 🌗 **Dark UI** — Glassmorphism design with gradient backgrounds

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/way2abhii/AI-Water-Tracker.git
cd AI-Water-Tracker
```

### 2. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the project root:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```
> Get a free API key at [openrouter.ai](https://openrouter.ai)

### 5. Run the app
```bash
streamlit run scr/dashboard.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🗂️ Project Structure

```
water_intake/
├── scr/
│   ├── dashboard.py     # Streamlit UI (Signup, Login, Dashboard)
│   ├── database.py      # SQLite DB — users, water intake, auth
│   ├── agent.py         # AI agent (OpenRouter / Llama 3.3 70B)
│   ├── api.py           # FastAPI REST endpoints
│   └── logger.py        # Logging utility
├── main.py              # Entry point
├── migrate_db.py        # DB migration helper
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project config
└── .env                 # API keys (not committed)
```

---

## 🧠 How the AI Works

The `WaterIntakeAgent` sends a personalised prompt to **Llama 3.3 70B** (via OpenRouter) with:
- User's weight and activity level
- Today's intake vs. daily goal
- Calculated percentage progress

It returns a motivational, personalised hydration tip tailored to that user.

---

## 📐 Daily Goal Formula

```
daily_goal_ml = weight_kg × 35 × activity_multiplier
```

| Activity Level | Multiplier |
|---|---|
| Sedentary | 0.9× |
| Light | 1.0× |
| Moderate | 1.1× |
| Active | 1.2× |
| Very Active | 1.35× |

---

## 🛡️ Security Notes

- Passwords are hashed with **SHA-256** before storage
- `.env` is in `.gitignore` — never commit API keys
- Each user gets a unique `USR-XXXXXXXX` ID on signup

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| Database | SQLite |
| AI / LLM | OpenRouter → Llama 3.3 70B |
| Auth | SHA-256 + UUID |
| Package Manager | uv / pip |

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---
