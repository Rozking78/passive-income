"""
Content Engine - Generate content ideas and templates for affiliate marketing
Works without paid APIs - uses templates and formulas
"""

import random
from datetime import datetime
from typing import List, Dict


class ContentGenerator:
    """Generate high-converting content ideas and templates"""

    def __init__(self):
        self.year = datetime.now().year

    # ==================== HOOKS / TITLES ====================

    def generate_hooks(self, product: str, niche: str) -> List[str]:
        """Generate attention-grabbing hooks for videos/posts"""

        hooks = [
            # Curiosity hooks
            f"I found a {product} secret that nobody talks about...",
            f"Why 99% of people fail with {niche} (and how to fix it)",
            f"The truth about {product} they don't want you to know",
            f"I tested {product} for 30 days - here's what happened",

            # Result hooks
            f"How I went from $0 to $5K/month using {product}",
            f"This {niche} strategy made me ${random.randint(500, 2000)} last week",
            f"The exact {niche} system I use to make passive income",

            # Controversy hooks
            f"Stop wasting money on {niche} - do this instead",
            f"Why {product} is NOT for everyone (honest review)",
            f"I was wrong about {niche}...",

            # Urgency hooks
            f"Best {niche} tools in {self.year} (before they change)",
            f"{product} just updated - here's what's new",

            # Social proof hooks
            f"How beginners are using {product} to quit their jobs",
            f"Why millionaires use {product} (and you should too)",

            # Question hooks
            f"Is {product} actually worth it in {self.year}?",
            f"What's the best {niche} for beginners?",
            f"Can you really make money with {product}?",
        ]

        return hooks

    def generate_video_scripts(self, product: str, product_type: str = "saas") -> Dict:
        """Generate video script templates for YouTube/TikTok"""

        if product_type == "saas":
            script = {
                "type": "SaaS Review",
                "duration": "8-12 minutes",
                "structure": {
                    "hook": f"[0:00-0:30] Today I'm revealing why {product} changed everything for my business...",
                    "intro": f"[0:30-1:30] Quick intro - who this video is for, what you'll learn",
                    "problem": f"[1:30-3:00] The problem {product} solves - pain points your audience has",
                    "solution": f"[3:00-6:00] Walk through {product} - show the interface, key features",
                    "results": f"[6:00-8:00] Show your results/case study using {product}",
                    "comparison": f"[8:00-9:00] Brief comparison to alternatives",
                    "cta": f"[9:00-10:00] Call to action - link in description, special offer",
                    "outro": f"[10:00-end] Ask for likes/subs, tease next video",
                },
                "cta_examples": [
                    f"Link to {product} is in the description - use my link for a special discount",
                    f"Click the first link below to try {product} free for 14 days",
                    f"I negotiated an exclusive deal for my audience - link below",
                ]
            }
        else:
            script = {
                "type": "General Affiliate",
                "duration": "5-8 minutes",
                "structure": {
                    "hook": f"[0:00-0:20] Attention-grabbing statement about {product}",
                    "context": f"[0:20-1:00] Why you're making this video",
                    "content": f"[1:00-5:00] Main value - tips, tutorial, or review",
                    "cta": f"[5:00-6:00] Call to action with affiliate link",
                    "outro": f"[6:00-end] Engagement ask",
                }
            }

        return script

    def generate_tiktok_scripts(self, product: str) -> List[Dict]:
        """Generate short-form video scripts for TikTok/Reels"""

        scripts = [
            {
                "format": "POV Style",
                "duration": "15-30 sec",
                "script": f"""
POV: You just discovered {product}

[Show screen recording of the tool]

This is the tool that's making people $XXX/month

Step 1: [Quick action]
Step 2: [Quick action]
Step 3: Profit

Link in bio to try it free
""",
            },
            {
                "format": "Storytime",
                "duration": "30-60 sec",
                "script": f"""
[Face to camera, casual vibe]

So I've been using {product} for 3 months now and I have to be honest...

[Pause for effect]

It actually works.

Here's what happened:
- Week 1: [Result]
- Week 4: [Better result]
- Month 3: [Best result]

If you want to try it, link is in my bio. Not sponsored, just sharing what works.
""",
            },
            {
                "format": "Listicle",
                "duration": "15-30 sec",
                "script": f"""
3 reasons {product} is blowing up right now:

1. [Benefit 1] - quick explanation
2. [Benefit 2] - quick explanation
3. [Benefit 3] - quick explanation

Try it free - link in bio
""",
            },
            {
                "format": "Reaction/Duet",
                "duration": "15-30 sec",
                "script": f"""
[React to someone asking about {product} or the niche]

"Wait, you're not using {product} yet?"

[Show quick demo]

This is literally how I [result]. Link in bio.
""",
            },
        ]

        return scripts

    # ==================== BLOG/ARTICLE TEMPLATES ====================

    def generate_blog_outline(self, product: str, article_type: str = "review") -> Dict:
        """Generate SEO-optimized blog post outlines"""

        outlines = {
            "review": {
                "title": f"{product} Review {self.year}: Is It Worth It? (Honest Take)",
                "meta_description": f"Detailed {product} review covering features, pricing, pros & cons. See if {product} is right for you + exclusive discount inside.",
                "outline": [
                    "## Quick Verdict (TL;DR)",
                    "## What is {product}?",
                    "## Who is {product} For?",
                    "## Key Features",
                    "### Feature 1",
                    "### Feature 2",
                    "### Feature 3",
                    "## {product} Pricing",
                    "## Pros and Cons",
                    "## {product} vs Alternatives",
                    "## My Personal Experience",
                    "## Is {product} Worth It?",
                    "## How to Get Started",
                    "## FAQ",
                    "## Final Verdict",
                ],
            },
            "comparison": {
                "title": f"{product} vs [Competitor]: Which One Wins in {self.year}?",
                "meta_description": f"Detailed comparison of {product} vs alternatives. See features, pricing, and which is best for your needs.",
                "outline": [
                    "## Quick Comparison Table",
                    "## Overview: {product}",
                    "## Overview: [Competitor]",
                    "## Features Comparison",
                    "## Pricing Comparison",
                    "## Ease of Use",
                    "## Customer Support",
                    "## Who Should Choose {product}",
                    "## Who Should Choose [Competitor]",
                    "## Our Recommendation",
                ],
            },
            "tutorial": {
                "title": f"How to Use {product} (Step-by-Step Guide {self.year})",
                "meta_description": f"Complete {product} tutorial for beginners. Learn how to set up and use {product} to [achieve result].",
                "outline": [
                    "## What You'll Learn",
                    "## Prerequisites",
                    "## Step 1: Getting Started",
                    "## Step 2: [Core Action]",
                    "## Step 3: [Core Action]",
                    "## Step 4: [Core Action]",
                    "## Pro Tips",
                    "## Common Mistakes to Avoid",
                    "## Next Steps",
                    "## FAQ",
                ],
            },
            "listicle": {
                "title": f"Best {product} Alternatives in {self.year} (Free & Paid)",
                "meta_description": f"Looking for {product} alternatives? Compare the top options with features, pricing, and honest reviews.",
                "outline": [
                    "## Quick Comparison Table",
                    "## 1. [Alternative 1] - Best Overall",
                    "## 2. [Alternative 2] - Best for [Use Case]",
                    "## 3. [Alternative 3] - Best Budget Option",
                    "## 4. [Alternative 4] - Best for [Use Case]",
                    "## 5. [Alternative 5] - Best Free Option",
                    "## How We Tested",
                    "## How to Choose",
                    "## FAQ",
                ],
            },
        }

        return outlines.get(article_type, outlines["review"])

    # ==================== EMAIL TEMPLATES ====================

    def generate_email_sequence(self, product: str) -> List[Dict]:
        """Generate email sequence for affiliate promotion"""

        sequence = [
            {
                "day": 0,
                "subject": f"About that {product} thing...",
                "purpose": "Introduction/curiosity",
                "body": f"""Hey {{name}},

I've been getting a lot of questions about {product} lately, so I wanted to share my honest thoughts.

Short version: It's not for everyone. But if you're [target audience], it might be exactly what you need.

I'll break down everything tomorrow - the good, the bad, and whether it's worth your money.

Talk soon,
{{your_name}}

P.S. If you're impatient, here's the link: [AFFILIATE_LINK]
""",
            },
            {
                "day": 1,
                "subject": f"The truth about {product}",
                "purpose": "Value + soft pitch",
                "body": f"""Hey {{name}},

Yesterday I promised to tell you about {product}. Here's my honest breakdown:

**What it does:**
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

**What I like:**
- [Pro 1]
- [Pro 2]

**What I don't like:**
- [Con 1]
- [Con 2]

**Who it's for:**
- [Ideal user 1]
- [Ideal user 2]

**Who should skip it:**
- [Not ideal user]

If you want to try it, here's my link: [AFFILIATE_LINK]

They're offering [special offer] right now, which won't last forever.

{{your_name}}
""",
            },
            {
                "day": 3,
                "subject": f"Quick question about {product}",
                "purpose": "Engagement + social proof",
                "body": f"""Hey {{name}},

Got a few replies about {product} - people are asking:

"Does it actually work for [specific use case]?"

Short answer: Yes, if you [condition].

I've seen people [result 1] and [result 2] using this tool.

Here's a quick case study: [Brief story]

If you missed my link: [AFFILIATE_LINK]

Any questions? Just reply to this email.

{{your_name}}
""",
            },
            {
                "day": 5,
                "subject": f"Last chance: {product} deal ending",
                "purpose": "Urgency + final pitch",
                "body": f"""Hey {{name}},

Quick heads up - the {product} offer I mentioned is ending [timeframe].

If you've been on the fence, now's the time to decide.

Here's the deal:
- [Offer details]
- [Bonus if applicable]

After [deadline], it goes back to regular price.

Grab it here while you can: [AFFILIATE_LINK]

{{your_name}}

P.S. No pressure. Only sign up if it makes sense for you. But don't say I didn't warn you about the deadline!
""",
            },
        ]

        return sequence

    # ==================== SOCIAL MEDIA TEMPLATES ====================

    def generate_social_posts(self, product: str, platform: str = "twitter") -> List[str]:
        """Generate social media post templates"""

        templates = {
            "twitter": [
                f"Unpopular opinion: {product} is overhyped.\n\nJust kidding. It literally [result].\n\nHere's my honest review after using it for 3 months:\n\n[Thread]",
                f"Tools I can't live without:\n\n1. {product} - [reason]\n2. [Tool 2]\n3. [Tool 3]\n4. [Tool 4]\n\nWhich ones am I missing?",
                f"The difference between {product} and free alternatives?\n\n$[time saved] of your time back.\n\nSometimes free costs more.",
                f"If you're not using {product}, you're working too hard.\n\nI automated [task] in 10 minutes.\n\nLink in bio.",
                f"[Screenshot of results]\n\nThis is what happens when you use {product} the right way.\n\nFull breakdown in the replies:",
            ],
            "linkedin": [
                f"I was skeptical about {product}.\n\nAnother tool? Really?\n\nBut after [timeframe], here's what I learned:\n\n1. [Insight 1]\n2. [Insight 2]\n3. [Insight 3]\n\nThe ROI has been [result].\n\nAnyone else using this?",
                f"Hot take: Most people overcomplicate [niche].\n\nHere's my simple stack:\n\n• {product} for [task]\n• [Tool 2] for [task]\n• [Tool 3] for [task]\n\nTotal cost: $X/month\nTotal revenue generated: $XX,XXX\n\nSimplicity wins.",
            ],
            "instagram": [
                f"POV: You just found the tool that changes everything 👀\n\n{product} did [result] for my [business/life].\n\nSave this post and thank me later.\n\nLink in bio.",
                f"📱 Tool of the day: {product}\n\n✅ [Benefit 1]\n✅ [Benefit 2]\n✅ [Benefit 3]\n\nWho else uses this? Drop a 🙋 below",
            ],
        }

        return templates.get(platform, templates["twitter"])


def main():
    """Demo the content generator"""
    generator = ContentGenerator()

    product = "ConvertKit"
    niche = "email marketing"

    print("=" * 60)
    print("CONTENT ENGINE - Affiliate Marketing Templates")
    print("=" * 60)

    print("\n📹 VIDEO HOOKS:")
    for hook in generator.generate_hooks(product, niche)[:5]:
        print(f"  • {hook}")

    print("\n📱 TIKTOK SCRIPTS:")
    scripts = generator.generate_tiktok_scripts(product)
    for script in scripts[:2]:
        print(f"\n  [{script['format']}]")
        print(f"  {script['script'][:200]}...")

    print("\n📧 EMAIL SEQUENCE:")
    emails = generator.generate_email_sequence(product)
    for email in emails[:2]:
        print(f"  Day {email['day']}: {email['subject']}")

    print("\n🐦 SOCIAL POSTS:")
    posts = generator.generate_social_posts(product, "twitter")
    for post in posts[:3]:
        print(f"  • {post[:100]}...")


if __name__ == "__main__":
    main()
