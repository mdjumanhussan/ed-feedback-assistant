# make_data.py
# Makes 200 SYNTHETIC (made-up) emergency department patient comments.
# No real patient data is used. Safe to share in a demo.
# Run it with:  python make_data.py

import csv
import random
from datetime import date, timedelta

random.seed(42)  # same "random" result every time, so your demo is repeatable

# Who came in and when. These set the scene.
SCENES = [
    "I came in on a Saturday night with chest pain.",
    "I brought my son in after a fall at school.",
    "My mother was sent in by her GP on a weekday morning.",
    "I arrived by ambulance late in the evening.",
    "I walked in with a bad cut on my hand.",
    "I took my daughter in with a high fever at 2 am.",
    "My husband had trouble breathing, so we went straight in.",
    "I came in after a car accident on a Monday afternoon.",
    "My father is elderly and had a dizzy spell.",
    "I went in with severe stomach pain on a public holiday.",
]

# Each theme has positive and negative things a patient might say.
THEMES = {
    "Waiting time": {
        "positive": [
            "I was seen within twenty minutes, much faster than I expected.",
            "The wait was short and the screen showed how long was left.",
            "They moved me through quickly even though it looked busy.",
        ],
        "negative": [
            "I waited more than five hours before a doctor saw me.",
            "Nobody told us how long the wait would be.",
            "The waiting room was full and people who came later went in first.",
            "We sat for hours with no update at all.",
        ],
    },
    "Staff communication": {
        "positive": [
            "The doctor explained everything in plain words.",
            "The nurse kept checking in and told us what would happen next.",
            "They listened to my questions and did not rush me.",
        ],
        "negative": [
            "Nobody explained what the tests were for.",
            "Different staff told me different things.",
            "The doctor used medical words I did not understand.",
            "I had to keep asking before anyone gave me an answer.",
        ],
    },
    "Pain management": {
        "positive": [
            "I was given pain relief soon after I arrived.",
            "The nurse asked about my pain often and adjusted the medicine.",
            "They took my pain seriously from the start.",
        ],
        "negative": [
            "I waited three hours in pain before getting any relief.",
            "I asked for pain relief twice and nothing happened.",
            "Nobody asked how bad the pain was.",
        ],
    },
    "Triage process": {
        "positive": [
            "The triage nurse saw me straight away and was very thorough.",
            "Triage was quick and they explained why others might go first.",
            "The triage nurse noticed how unwell I was and acted fast.",
        ],
        "negative": [
            "The triage questions felt rushed and I forgot to mention things.",
            "I did not understand why I was given a low priority.",
            "There was a long queue just to speak to the triage nurse.",
        ],
    },
    "Cleanliness and facilities": {
        "positive": [
            "The department was clean and the bed area was tidy.",
            "The toilets were clean and there was a water station.",
            "The children's area was bright and well kept.",
        ],
        "negative": [
            "The waiting room chairs were hard and there were not enough of them.",
            "The toilets were dirty and had no soap.",
            "It was very cold and noisy in the waiting area.",
        ],
    },
    "Discharge information": {
        "positive": [
            "I got clear written instructions before I went home.",
            "They explained my medicine and when to see my GP.",
            "The nurse made sure I knew the warning signs to watch for.",
        ],
        "negative": [
            "I was sent home without knowing what to do next.",
            "The discharge was rushed and nobody explained my medicine.",
            "I never received the letter for my GP.",
        ],
    },
    "Staff kindness": {
        "positive": [
            "Every staff member was kind and patient with us.",
            "A nurse brought my mother a blanket and a cup of tea.",
            "The staff treated us with respect even though they were busy.",
        ],
        "negative": [
            "The front desk staff seemed annoyed when I asked a question.",
            "I felt like a number, not a person.",
            "One staff member was quite short with my elderly father.",
        ],
    },
    "Parking and access": {
        "positive": [
            "Parking was close and easy to find.",
            "The signs made it easy to find the emergency entrance.",
            "There was a drop-off bay right at the door, which helped a lot.",
        ],
        "negative": [
            "Parking was expensive and the car park was full.",
            "The signs were confusing and we went to the wrong entrance.",
            "It was a long walk from the car park for someone in pain.",
        ],
    },
}

# How the comment ends.
ENDINGS = {
    "positive": [
        "Thank you to the team.",
        "I felt well looked after.",
        "I would recommend this hospital.",
        "It made a stressful day much easier.",
    ],
    "negative": [
        "It was a very stressful experience.",
        "I hope this can be improved.",
        "I left feeling frustrated.",
        "This needs to change.",
    ],
}

TOTAL = 200
start = date(2025, 7, 1)

comments = set()
rows = []
while len(rows) < TOTAL:
    theme = random.choice(list(THEMES))
    sentiment = random.choice(["positive", "negative", "negative"])  # complaints are more common
    text = " ".join([
        random.choice(SCENES),
        random.choice(THEMES[theme][sentiment]),
        random.choice(ENDINGS[sentiment]),
    ])
    if text in comments:      # skip repeats, so all 200 are different
        continue
    comments.add(text)
    day = start + timedelta(days=random.randint(0, 364))
    rows.append([len(rows) + 1, text, theme, sentiment, day.isoformat()])

with open("ed_feedback.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "comment", "theme", "sentiment", "date"])
    writer.writerows(rows)

print(f"Saved {len(rows)} comments to ed_feedback.csv")
for theme in THEMES:
    print(f"  {theme}: {sum(1 for r in rows if r[2] == theme)}")
