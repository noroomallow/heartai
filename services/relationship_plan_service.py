import json
from services.ai_service import AIService


class PlanGeneratorService:
    """Creates a practical 30-day relationship bonding plan."""

    @staticmethod
    def generate_fallback_plan(scores, partner_name):
        weakest = min(
            ((k, float(v)) for k, v in scores.items() if k not in {"overall_score", "category"}),
            key=lambda item: item[1],
            default=("communication", 50),
        )[0]

        focus = {
            "communication": "Use calm, honest conversations and active listening.",
            "personality": "Learn each other's preferences, emotional needs and boundaries.",
            "interests": "Discover shared interests and create enjoyable memories together.",
            "values": "Discuss expectations, priorities and what a healthy relationship means to both of you.",
            "lifestyle": "Build enjoyable routines while respecting each person's independence.",
            "preference": "Talk about how each of you prefers to give and receive care.",
            "chat": "Improve digital communication through clearer, warmer and less reactive messages.",
        }.get(weakest, "Strengthen communication, trust and quality time together.")

        activities = [
            (1, 1, "Relationship Reset Coffee", f"Spend 20 minutes together without phones. Share one thing you appreciate about {partner_name} and one thing you want to improve together. {focus}"),
            (2, 1, "Favorite Things Night", "Each person lists five favorite things—food, music, places, hobbies or small comforts—and compare the lists."),
            (3, 1, "Memory Lane", "Look through old photos or messages and talk about three memories that still make you both smile."),
            (4, 1, "Walk & Talk Date", "Take a relaxed evening walk and ask each other three open-ended questions about the week."),
            (5, 1, "Love Language Exchange", "Each person chooses one small way they would like to receive care today, then do it willingly and respectfully."),
            (6, 1, "Movie Night", "Choose a movie together, prepare a simple snack, put phones away and discuss your favorite scene afterward."),
            (7, 1, "Weekly Check-In", "Rate the week from 1–10 for communication, quality time and emotional connection. Discuss one small improvement."),
            (8, 2, "Compliment Challenge", "Give each other three specific compliments—one about character, one about effort and one about a recent action."),
            (9, 2, "Style Refresh", "Go shopping together or browse online and choose one new clothing item or accessory for each person within a comfortable budget."),
            (10, 2, "No-Phone Dinner", "Have dinner together with notifications off. Take turns talking for five minutes while the other listens without interrupting."),
            (11, 2, "Conflict Practice", "Pick a small, non-sensitive disagreement and practice using 'I feel… when… because…' rather than blame."),
            (12, 2, "Playlist Exchange", "Create a five-song playlist that reminds you of your relationship and explain why you chose each song."),
            (13, 2, "Mini Surprise", "Give your partner a small thoughtful surprise such as a handwritten note, favorite snack or encouraging message."),
            (14, 2, "Date Night", "Plan a simple date together—cafe, park, bookstore, beach, museum or another place you both enjoy."),
            (15, 3, "Cook Together", "Choose an easy recipe and prepare it together. Divide the work and keep the goal fun rather than perfect."),
            (16, 3, "Dream Day", "Design an ideal day together from morning to night. Compare what overlaps and choose one idea to actually do."),
            (17, 3, "Shared Hobby Hour", "Try a hobby one partner enjoys and let the other teach it. Switch roles if time allows."),
            (18, 3, "Gratitude Messages", "Send each other a short message naming one moment from the relationship you are genuinely grateful for."),
            (19, 3, "Dress-Up Evening", "Wear an outfit you both feel good in and go out for dessert, coffee or a relaxed evening date."),
            (20, 3, "Photo Walk", "Take a short walk and capture five photos representing your relationship today. Share the stories behind them."),
            (21, 3, "Digital Detox Date", "Spend at least 90 minutes together without social media. Choose a board game, cards, walk or conversation instead."),
            (22, 4, "Future Goals", "Discuss three personal goals and three shared goals for the next year. Pick one realistic step you can support each other with."),
            (23, 4, "Budget-Friendly Date", "Have a low-cost date using a fixed budget. The challenge is to create a good memory without focusing on spending."),
            (24, 4, "Support Day", "Ask, 'What would make today easier for you?' and offer one practical, voluntary act of support."),
            (25, 4, "Favorite Food Date", "Visit a favorite food place or recreate a favorite meal at home. Talk about the first time you discovered it together."),
            (26, 4, "Relationship Boundaries", "Discuss personal space, communication expectations and boundaries. Agree on respectful habits that work for both people."),
            (27, 4, "Recreate a First Date", "Recreate a memorable early-date activity or adapt it into a simple version that fits your current life."),
            (28, 4, "Appreciation Letter", "Write a short private letter about what you value in the relationship and read it to each other if comfortable."),
            (29, 4, "Favorite Date Vote", "Each person proposes two date ideas. Pick one together and schedule it for the next few weeks."),
            (30, 4, "30-Day Celebration", "Celebrate completing the plan. Review your favorite activities, note what helped most, and choose three habits to continue."),
        ]
        return [
            {"day": day, "week": week, "title": title, "description": description}
            for day, week, title, description in activities
        ]

    @classmethod
    def build_30_day_plan(cls, scores, partner_name):
        fallback = cls.generate_fallback_plan(scores, partner_name)
        weakest = min(
            ((k, float(v)) for k, v in scores.items() if k not in {"overall_score", "category"}),
            key=lambda item: item[1],
            default=("communication", 50),
        )[0]
        prompt = f"""
Create exactly 30 practical relationship-bonding activities for a couple.
Partner name: {partner_name}
Weakest assessment dimension: {weakest} ({scores.get(weakest, 50)}%).
Overall score: {scores.get('overall_score', 50)}%.

The plan must be safe, mutual, realistic and focused on strengthening the bond.
Include a healthy mix of:
- meaningful conversations and active listening
- dating and quality time
- movie night
- cooking together
- a walk or outdoor activity
- a small surprise/note
- buying or choosing a new clothing item together within a reasonable budget
- dress-up/date night
- shared hobby
- photos/memory activity
- future goals and relationship check-in
- low-cost date ideas
- appreciation and gratitude
- boundaries and respectful communication

Do not make every day a serious conversation. Keep it enjoyable and progressive.
Week 1 = Understanding, Week 2 = Communication, Week 3 = Connection, Week 4 = Growth.
Return ONLY a JSON array of exactly 30 objects with keys: day, week, title, description.
"""
        try:
            result = AIService.generate_json_response(prompt)
            if isinstance(result, dict):
                result = result.get("thirty_day_plan") or result.get("plan")
            if isinstance(result, list) and len(result) == 30:
                normalized = []
                for index, item in enumerate(result, 1):
                    if not isinstance(item, dict):
                        raise ValueError("Invalid plan item")
                    normalized.append({
                        "day": index,
                        "week": int(item.get("week") or ((index - 1) // 7 + 1)),
                        "title": str(item.get("title") or fallback[index - 1]["title"]),
                        "description": str(item.get("description") or fallback[index - 1]["description"]),
                    })
                return normalized
        except Exception as exc:
            print("30-day AI plan fallback:", type(exc).__name__, str(exc))
        return fallback
