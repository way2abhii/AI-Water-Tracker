from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


class WaterIntakeAgent:
    def __init__(self):
        self.history = []

    def analyze_intake(self, intake_ml: int, daily_goal_ml: int = 2500,
                       weight_kg: float = 70.0, activity_level: str = "moderate") -> str:
        """Generate a personalised hydration analysis."""
        pct = round((intake_ml / daily_goal_ml) * 100, 1)
        prompt = f"""
You are a friendly, motivational health assistant specialised in hydration.

User stats:
- Weight: {weight_kg} kg
- Activity level: {activity_level}
- Daily water goal: {daily_goal_ml} ml
- Water consumed today: {intake_ml} ml  ({pct}% of goal)

Give a short (3-4 sentence) personalised hydration tip.
Be encouraging. If they're behind, suggest catching up gently.
If they've hit the goal, congratulate them warmly.
"""
        try:
            response = client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Could not fetch AI analysis: {e}"

    def get_motivational_quote(self) -> str:
        """Return a short water / wellness motivation quote."""
        prompt = "Give me one short (1–2 sentence) motivational quote about hydration or healthy habits. No extra commentary."
        try:
            response = client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "💧 Every drop counts. Stay hydrated!"


if __name__ == "__main__":
    agent = WaterIntakeAgent()
    feedback = agent.analyze_intake(1500, daily_goal_ml=2500)
    print(f"Hydration Analysis:\n{feedback}")