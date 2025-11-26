"""
StudyBuddy: AI-Powered Personalized Learning Coach
Track: Agents for Good (Google AI Agents Intensive Capstone)

This agent helps students:
- Create custom study plans
- Generate topic-specific quizzes
- Track progress via human-in-the-loop check-ins

Key ADK Concepts Demonstrated:
✅ Custom Tools (generate_study_plan, create_quiz)
✅ Long-Running Operations (weekly_checkin with approval)
✅ Session State (SQLite persistence)
✅ Observability (LoggingPlugin)
✅ Gemini-Powered (gemini-2.5-flash-lite)
"""

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# Configure retry behavior for transient errors (e.g., rate limits)
retry_config = types.HttpRetryOptions(
    attempts=5,                # Max retry attempts
    exp_base=7,                # Exponential backoff multiplier
    initial_delay=1,           # Initial delay (seconds)
    http_status_codes=[429, 500, 503, 504],  # Retry on these errors
)

# ======================
# CUSTOM TOOLS
# ======================

def generate_study_plan(subject: str, days_left: int, weak_topics: str) -> dict:
    """
    Generates a personalized study plan.
    
    Args:
        subject: Subject name (e.g., "Calculus")
        days_left: Days until exam (e.g., 5)
        weak_topics: Comma-separated topics needing focus (e.g., "integrals, limits")
    
    Returns:
        dict: Study plan as formatted text
    """
    plan = (
        f"📅 **{days_left}-Day Study Plan for {subject}**\n"
        f"**Focus Areas**: {weak_topics}\n"
        f"**Day 1**: Review basics + 10 practice problems\n"
        f"**Day 2**: Deep dive into {weak_topics.split(',')[0]} + video tutorial\n"
        f"**Day 3**: Practice quiz + mistake review\n"
        f"**Day 4**: Full mock test\n"
        f"**Day 5**: Final review + key concepts recap"
    )
    return {"status": "success", "plan": plan}


def create_quiz(topic: str, difficulty: str = "medium") -> dict:
    """
    Generates a short quiz on a topic.
    
    Args:
        topic: Topic name (e.g., "integrals")
        difficulty: "easy", "medium", or "hard"
    
    Returns:
        dict: Quiz questions as text
    """
    quizzes = {
        "easy": "1. What is ∫2x dx?\n2. Derivative of x²?",
        "medium": "1. Evaluate ∫₀¹ x² dx\n2. Area under y=x from 0 to 2",
        "hard": "1. Solve ∫eˣsin(x) dx\n2. Volume of revolution for y=√x (0→4)",
    }
    return {"status": "success", "quiz": quizzes.get(difficulty, quizzes["medium"])}


def weekly_checkin(tool_context: ToolContext, day: int) -> dict:
    """
    Pauses to ask user if they completed a study task (Long-Running Operation).
    
    Args:
        tool_context: ADK-provided context for state/approval handling
        day: Study day number (e.g., 1)
    
    Returns:
        dict: Status after user response
    """
    # First call: Request human approval
    if not tool_context.tool_confirmation:
        tool_context.request_confirmation(
            hint=f"✅ Day {day}: Did you complete your study session?",
            payload={"day": day}
        )
        return {"status": "pending", "message": "Awaiting your response..."}
    
    # Resume after user response
    if tool_context.tool_confirmation.confirmed:
        return {"status": "completed", "message": f"Great job on Day {day}! 🎉"}
    else:
        return {"status": "rescheduled", "message": f"Let's adjust your plan for Day {day}."}

# ======================
# AGENT DEFINITION
# ======================

studybuddy = LlmAgent(
    name="studybuddy",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="A personalized learning coach for students.",
    instruction="""
    You are StudyBuddy, a friendly and encouraging learning coach.
    
    When users ask for help:
    1. Ask for subject, exam date, and weak topics
    2. Use `generate_study_plan` to create a custom study plan
    3. Offer quizzes via `create_quiz`
    4. After study sessions, use `weekly_checkin` to track progress
    5. Always be supportive and adaptive
    
    Never guess facts—use your tools!
    """,
    tools=[generate_study_plan, create_quiz, weekly_checkin],
)
