"""
Psychology-Based Copywriting Hooks
===================================
Based on deep research into wealth aspiration psychology.

Key insights:
- Target audience is cognitively taxed - keep messaging SIMPLE
- Lead with transformation, not features
- Use identity-based language
- Validate pain without exploiting it
- Be specific (numbers, timeframes, realistic outcomes)
"""

import random

# =============================================================================
# PSYCHOLOGICAL HOOK TEMPLATES
# =============================================================================

# Pain-to-aspiration hooks (validated struggle + promised transformation)
PAIN_TO_ASPIRATION_HOOKS = [
    "I was trading hours for $15... now I charge $80",
    "Broke and burned out. Then I found this.",
    "From paycheck-to-paycheck to $2,500 weeks",
    "I almost gave up. Here's what changed.",
    "Tired of working hard with nothing to show?",
    "What if you could finally breathe?",
    "Stop surviving. Start building.",
    "The freedom you've been looking for",
]

# Identity-based hooks (who they want to become)
IDENTITY_HOOKS = [
    "For people who refuse to settle",
    "You're not lazy. You just need the right tools.",
    "This is for the ones still trying",
    "Builders only. Not for complainers.",
    "For future millionaires who started with nothing",
    "You're one decision away from a different life",
    "Some people watch. You build.",
    "Not everyone will get this. But you will.",
]

# Curiosity + specificity hooks
CURIOSITY_HOOKS = [
    "The $78/hour math nobody teaches you",
    "Why 85% of creators use this (but won't admit it)",
    "The tool that replaced my 4-hour workday",
    "How I went from $500/month to $500/week",
    "The difference between $20/hour and $200/hour",
    "What successful creators know that you don't",
    "I reverse-engineered their success. Here it is.",
    "The boring truth about making money online",
]

# Social proof + FOMO hooks
SOCIAL_PROOF_HOOKS = [
    "Everyone's using this. You're just late.",
    "Your competitor already knows about this",
    "This is why they're winning and you're not",
    "The open secret of the creator economy",
    "What I wish someone told me 2 years ago",
    "They're not smarter. They're just using this.",
    "54% of Americans started a side hustle. Where are you?",
]

# Story-based hooks (relatable origin)
STORY_HOOKS = [
    "I was exactly where you are right now",
    "Last year I couldn't pay rent. This year...",
    "My friends thought I was crazy. Then they saw the results.",
    "I tried 47 things before this worked",
    "The day everything changed for me",
    "I didn't believe it either. Watch.",
    "Here's the truth nobody wants to tell you",
]

# Transformation hooks (before/after)
TRANSFORMATION_HOOKS = [
    "Monday: Struggling. Friday: $2,500 richer.",
    "Before vs After discovering this",
    "30 days ago I was you. Look at me now.",
    "Same me. Different bank account.",
    "From 'I can't afford it' to 'how many do you want?'",
    "Watch me go from zero to paid in 3 minutes",
]

# =============================================================================
# PAIN POINTS (Use to validate, not exploit)
# =============================================================================

PAIN_POINTS = [
    "working 60 hours and still broke",
    "watching others succeed while you struggle",
    "saying 'I can't afford it' one more time",
    "feeling stuck in the same place for years",
    "knowing you're meant for more than this",
    "dreading Monday mornings",
    "missing out on opportunities because of money",
    "calculating if you can afford groceries",
    "pretending everything's fine when it's not",
    "working hard with nothing to show for it",
]

# =============================================================================
# ASPIRATIONAL OUTCOMES (What they dream of)
# =============================================================================

ASPIRATIONS = [
    "wake up without an alarm",
    "check your bank account and smile",
    "say 'yes' without checking the price",
    "work from anywhere in the world",
    "provide for your family properly",
    "prove the doubters wrong",
    "finally breathe",
    "buy what you want, not what you can afford",
    "quit the job that's killing you",
    "build something that's actually yours",
    "stop trading time for money",
    "create generational wealth",
]

# =============================================================================
# BELIEVABLE OUTCOMES (Specific, realistic)
# =============================================================================

REALISTIC_OUTCOMES = [
    "$500 extra this month",
    "$2,500 in the next 30 days",
    "15 hours back every week",
    "your first paying client this week",
    "doubled your output without more work",
    "$80/hour instead of $15",
    "3 new income streams",
    "quit your job in 6 months",
    "financial breathing room",
]

# =============================================================================
# CALL TO ACTION PATTERNS
# =============================================================================

CTAS = [
    "Link in bio if you're ready",
    "Save this. You'll need it.",
    "Comment 'INFO' and I'll send it",
    "Link in bio - but only if you're serious",
    "Try it free. What do you have to lose?",
    "Your future self will thank you",
    "This is the sign you've been waiting for",
    "Stop scrolling. Start building. Link in bio.",
]

# =============================================================================
# OBJECTION HANDLERS
# =============================================================================

OBJECTION_HANDLERS = {
    "scam": "I know you've seen 100 fake promises. This is different. Here's proof.",
    "expensive": "You can't afford NOT to try this. Calculate your wasted hours.",
    "no_time": "You have time to scroll. You have time to change your life.",
    "too_good": "It sounds too good because you've been doing it the hard way.",
    "not_for_me": "I thought that too. I was wrong. So are you.",
    "later": "Later becomes never. Start today, even if it's small.",
}

# =============================================================================
# VIRAL VIDEO TEXT PATTERNS
# =============================================================================

def get_viral_text_sequence(product_name: str, benefit: str) -> list:
    """Get a sequence of text for viral video overlays"""

    patterns = [
        # Pain → Discovery → Transformation → CTA
        [
            random.choice(PAIN_TO_ASPIRATION_HOOKS),
            f"Then I found {product_name}",
            f"Now I {random.choice(ASPIRATIONS)}",
            random.choice(CTAS),
        ],
        # Curiosity → Reveal → Proof → CTA
        [
            random.choice(CURIOSITY_HOOKS),
            f"It's called {product_name}",
            f"It {benefit}",
            f"Result: {random.choice(REALISTIC_OUTCOMES)}",
            random.choice(CTAS),
        ],
        # Identity → Challenge → Solution → CTA
        [
            random.choice(IDENTITY_HOOKS),
            f"Tired of {random.choice(PAIN_POINTS)}?",
            f"{product_name} changed everything",
            random.choice(CTAS),
        ],
        # Story → Struggle → Discovery → Outcome
        [
            random.choice(STORY_HOOKS),
            f"I was {random.choice(PAIN_POINTS)}",
            f"Then {product_name} happened",
            f"Now: {random.choice(REALISTIC_OUTCOMES)}",
            random.choice(CTAS),
        ],
        # Social Proof → Gap → Bridge → CTA
        [
            random.choice(SOCIAL_PROOF_HOOKS),
            f"They use {product_name}",
            f"You could {random.choice(ASPIRATIONS)}",
            random.choice(CTAS),
        ],
    ]

    return random.choice(patterns)


def get_psychological_hook() -> str:
    """Get a random psychological hook"""
    all_hooks = (
        PAIN_TO_ASPIRATION_HOOKS +
        IDENTITY_HOOKS +
        CURIOSITY_HOOKS +
        SOCIAL_PROOF_HOOKS +
        STORY_HOOKS +
        TRANSFORMATION_HOOKS
    )
    return random.choice(all_hooks)


def get_caption_with_psychology(product_name: str, hook: str) -> str:
    """Generate a psychologically-optimized caption"""

    templates = [
        f"{hook} 🔥 I was skeptical too. Then I tried {product_name}. Link in bio.",
        f"{hook} This isn't another empty promise. Try it free. Link in bio.",
        f"{hook} ⬇️ {product_name} changed everything. Your turn.",
        f"{hook} If you're tired of struggling, link in bio.",
        f"POV: You finally found {product_name} 🎯 Link in bio if you're ready.",
    ]

    return random.choice(templates)


# =============================================================================
# ETHICAL GUIDELINES
# =============================================================================

ETHICAL_RULES = """
ETHICAL COPYWRITING RULES:
1. Validate pain, don't create it
2. Be specific and realistic about outcomes
3. Acknowledge skepticism honestly
4. Show the work required, not just results
5. Disqualify people who aren't a good fit
6. Never promise guaranteed income
7. Use social proof from real people only
8. Make the path visible, not just the destination
"""
