"""
Auto Content Generator - Creates ready-to-post content automatically
Generates TikTok scripts, tweets, blog posts, and emails

Works without API keys using smart templates.
Optional: Add OpenAI API key for AI-powered generation.
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path


class AutoContentGenerator:
    """Automatically generate affiliate marketing content"""

    def __init__(self, niche: str = "ai writing tools", api_key: str = None):
        self.niche = niche
        self.api_key = api_key  # Optional OpenAI key
        self.year = datetime.now().year

        # Product database for the niche
        self.products = {
            "ai writing tools": [
                {"name": "Jasper", "price": "$49/mo", "benefit": "writes content 10x faster", "trial": "7-day free trial"},
                {"name": "Copy.ai", "price": "$36/mo", "benefit": "creates marketing copy in seconds", "trial": "free plan available"},
                {"name": "Writesonic", "price": "$19/mo", "benefit": "generates blogs and ads instantly", "trial": "free trial"},
                {"name": "Rytr", "price": "$9/mo", "benefit": "affordable AI writing assistant", "trial": "free plan"},
            ],
            "email marketing": [
                {"name": "ConvertKit", "price": "$29/mo", "benefit": "built for creators", "trial": "free plan"},
                {"name": "Beehiiv", "price": "$0-99/mo", "benefit": "newsletter growth machine", "trial": "free plan"},
                {"name": "Mailchimp", "price": "$13/mo", "benefit": "all-in-one marketing", "trial": "free plan"},
            ],
            "web hosting": [
                {"name": "Bluehost", "price": "$2.95/mo", "benefit": "easiest WordPress setup", "trial": "30-day guarantee"},
                {"name": "Hostinger", "price": "$1.99/mo", "benefit": "cheapest quality hosting", "trial": "30-day guarantee"},
                {"name": "SiteGround", "price": "$2.99/mo", "benefit": "best customer support", "trial": "30-day guarantee"},
            ],
        }

        # Get products for current niche
        self.niche_products = self.products.get(niche, self.products["ai writing tools"])

    # ==================== TIKTOK SCRIPTS ====================

    def generate_tiktok_script(self, style: str = "random") -> Dict:
        """Generate a complete TikTok script"""

        product = random.choice(self.niche_products)

        styles = {
            "hook": self._tiktok_hook_style,
            "tutorial": self._tiktok_tutorial_style,
            "storytime": self._tiktok_storytime_style,
            "comparison": self._tiktok_comparison_style,
            "results": self._tiktok_results_style,
            "controversy": self._tiktok_controversy_style,
            "challenge": self._tiktok_challenge_style,
        }

        if style == "random":
            style = random.choice(list(styles.keys()))

        generator = styles.get(style, self._tiktok_hook_style)
        script = generator(product)

        return {
            "style": style,
            "product": product["name"],
            "duration": script["duration"],
            "script": script["script"],
            "hook": script["hook"],
            "cta": script["cta"],
            "caption": script["caption"],
            "hashtags": self._generate_hashtags(),
        }

    def _tiktok_hook_style(self, product: Dict) -> Dict:
        hooks = [
            f"This AI tool is breaking the internet right now",
            f"POV: You just found the tool that changes everything",
            f"I can't believe this actually works",
            f"Stop scrolling - you need to see this",
            f"The tool they don't want you to know about",
            f"Wait... did that just happen in 3 seconds?",
            f"This is why I quit writing my own content",
        ]

        results = [
            f"made $500 extra last week",
            f"saved 10 hours this week",
            f"grew my account 3x faster",
            f"finally stopped burning out",
            f"doubled my content output",
        ]

        hook = random.choice(hooks)
        result = random.choice(results)

        script = f"""[HOOK - 0:00]
"{hook}"

[SHOW - 0:02]
*Open {product['name']} on screen*
*Type a simple prompt*

[REVEAL - 0:08]
*Show AI generating content instantly*

"This thing {product['benefit']}.
I {result} because of this.
It's called {product['name']}."

[CTA - 0:20]
"Link in bio if you want to try it.
{product['trial']}."
"""

        caption = f"{hook} 🤯 This changed everything for me. Link in bio to try {product['name']} free."

        return {
            "duration": "15-25 seconds",
            "script": script,
            "hook": hook,
            "cta": f"Link in bio - {product['trial']}",
            "caption": caption,
        }

    def _tiktok_tutorial_style(self, product: Dict) -> Dict:
        hook = f"How to create a week of content in 10 minutes"

        script = f"""[HOOK - 0:00]
"{hook}"
*Text on screen: SAVE THIS*

[STEP 1 - 0:03]
"First, go to {product['name']}"
*Show opening the tool*

[STEP 2 - 0:08]
"Click new document and pick your content type"
*Show clicking through*

[STEP 3 - 0:13]
"Type what you want - I'm doing Instagram captions"
*Show typing: "5 productivity tips for entrepreneurs"*

[STEP 4 - 0:18]
"Hit generate and watch"
*Show AI writing multiple pieces*

[STEP 5 - 0:25]
"Copy, schedule, done.
That's Monday through Friday in 2 minutes."

[CTA - 0:30]
"{product['trial']} - link in bio.
Save this for later."
"""

        caption = f"How I create a week of content in 10 minutes ⏱️ Save this! Link in bio for {product['trial'].lower()}."

        return {
            "duration": "30-45 seconds",
            "script": script,
            "hook": hook,
            "cta": f"Save this - {product['trial']}",
            "caption": caption,
        }

    def _tiktok_storytime_style(self, product: Dict) -> Dict:
        hook = "I almost quit creating content last month"

        script = f"""[HOOK - 0:00]
"{hook}"
*Serious face to camera*

[STORY - 0:03]
"I was spending 4-5 hours every single day
just writing posts, emails, captions.

I had no time for anything else.
I was completely burned out.

Then someone in my DMs told me about {product['name']}."

[TURN - 0:15]
"I didn't believe it at first.
But I tried it anyway.

*Show quick screen recording*

First week, I got 15 hours of my life back.
My content actually got BETTER.
And I stopped dreading posting."

[LESSON - 0:28]
"Using tools isn't cheating.
It's being smart.

You don't have to do everything the hard way."

[CTA - 0:35]
"If you're burning out, try it.
{product['trial']} - link in bio."
"""

        caption = f"Storytime: How {product['name']} saved me from quitting 😅 Link in bio if you're burning out too."

        return {
            "duration": "35-45 seconds",
            "script": script,
            "hook": hook,
            "cta": f"Link in bio - {product['trial']}",
            "caption": caption,
        }

    def _tiktok_comparison_style(self, product: Dict) -> Dict:
        hook = "Me writing content before vs after AI"

        script = f"""[HOOK - 0:00]
"{hook}"

[BEFORE - Left side]
*Show stressed, typing slowly*
*Clock fast-forwarding*
*Text: "3 hours later..."*
*Exhausted face*

[AFTER - Right side]
*Show relaxed, typing one line*
*{product['name']} generating content*
*Text: "3 minutes"*
*Happy face*

[VOICEOVER - 0:12]
"What used to take me half a day
now takes less than my coffee break.

Same quality. 10x faster.
I use {product['name']} - {product['benefit']}."

[CTA - 0:20]
"Stop working harder than you need to.
Link in bio."
"""

        caption = f"The difference is insane 😳 Before vs after using {product['name']}. Link in bio!"

        return {
            "duration": "20-30 seconds",
            "script": script,
            "hook": hook,
            "cta": "Link in bio",
            "caption": caption,
        }

    def _tiktok_results_style(self, product: Dict) -> Dict:
        days = random.choice([7, 14, 30])
        posts = days * random.randint(2, 4)
        growth = random.randint(20, 80)

        hook = f"What happened after {days} days of using AI for content"

        script = f"""[HOOK - 0:00]
"{hook}"
*Show calendar or stats*

[RESULT 1 - 0:04]
"I went from posting 3x a week to {posts // days}x a day.
Because it takes 10 minutes now, not 3 hours."
*Show posting frequency*

[RESULT 2 - 0:12]
"Engagement went UP {growth}%.
Because I had time to actually reply to comments."
*Show engagement metrics*

[RESULT 3 - 0:18]
"I landed 2 new clients.
From content the AI helped me write."
*Show DMs or testimonials*

[SUMMARY - 0:24]
"More content. Less time. Better results.
This isn't a hack - it's just using the right tools."

[CTA - 0:30]
"{product['name']} - link in bio.
{product['trial']}."
"""

        caption = f"My {days}-day {product['name']} results 📈 Link in bio to try it yourself!"

        return {
            "duration": "30-40 seconds",
            "script": script,
            "hook": hook,
            "cta": f"Link in bio - {product['trial']}",
            "caption": caption,
        }

    def _tiktok_controversy_style(self, product: Dict) -> Dict:
        hook = "Half the viral posts you see are written by AI"

        script = f"""[HOOK - 0:00]
*Whispered, secretive tone*
"{hook}"

[REVEAL - 0:04]
"That influencer with perfect captions every day?
AI.

That blog ranking #1 on Google?
AI helped write it.

Those Twitter threads going viral?
AI.

[PIVOT - 0:14]
The difference between creators who struggle
and creators who succeed?

Successful ones use tools like {product['name']}.

[NORMALIZE - 0:20]
It's not cheating.
It's being smart.
Everyone's doing it - they just don't tell you."

[CTA - 0:26]
"Link in bio if you want to stop working
10x harder than everyone else."
"""

        caption = f"The secret no one talks about 🤫 Link in bio."

        return {
            "duration": "25-35 seconds",
            "script": script,
            "hook": hook,
            "cta": "Link in bio",
            "caption": caption,
        }

    def _tiktok_challenge_style(self, product: Dict) -> Dict:
        hook = "I bet AI can write your caption faster than you can"

        script = f"""[HOOK - 0:00]
*Energetic*
"{hook}

Let's race. Go."

[CHALLENGE - 0:04]
*Split screen*
*Timer starts*

*Left: You typing manually*
*Right: {product['name']} generating*

[RESULT - 0:15]
*AI finishes in ~8 seconds*
*Timer shows comparison*

"8 seconds.
And honestly? It's better than what I would've written."

[CTA - 0:22]
"Try to beat that.
{product['trial']} - link in bio."
"""

        caption = f"Can you beat 8 seconds? 🏃‍♂️ Link in bio to try {product['name']} free."

        return {
            "duration": "20-30 seconds",
            "script": script,
            "hook": hook,
            "cta": f"Link in bio - {product['trial']}",
            "caption": caption,
        }

    def _generate_hashtags(self) -> List[str]:
        """Generate relevant hashtags"""
        base_tags = [
            "#contentcreator", "#sidehustle", "#makemoneyonline",
            "#passiveincome", "#entrepreneur", "#smallbusiness",
            "#digitalmarketing", "#onlinebusiness", "#workfromhome",
        ]

        niche_tags = {
            "ai writing tools": ["#aitools", "#jasperai", "#copywriting", "#contentmarketing", "#writingtips"],
            "email marketing": ["#emailmarketing", "#convertkit", "#newsletter", "#emaillist", "#creators"],
            "web hosting": ["#webhosting", "#wordpress", "#blogging", "#website", "#onlinebusiness"],
        }

        tags = base_tags + niche_tags.get(self.niche, [])
        return random.sample(tags, min(8, len(tags)))

    # ==================== TWITTER/X THREADS ====================

    def generate_twitter_thread(self, topic: str = None) -> Dict:
        """Generate a Twitter/X thread"""

        product = random.choice(self.niche_products)

        if not topic:
            topics = [
                f"How I use {product['name']} to 10x my content",
                f"The truth about AI content tools",
                f"Why I stopped writing my own content",
                f"My content creation workflow (takes 30 min/day)",
                f"Tools that actually make money (not just cost money)",
            ]
            topic = random.choice(topics)

        thread = self._build_thread(topic, product)

        return {
            "topic": topic,
            "product": product["name"],
            "tweets": thread,
            "total_tweets": len(thread),
        }

    def _build_thread(self, topic: str, product: Dict) -> List[str]:
        """Build a Twitter thread"""

        hooks = [
            f"🧵 {topic}\n\n(Bookmark this - you'll want it later)",
            f"I've been doing this wrong for years.\n\n{topic}\n\n🧵 Thread:",
            f"This changed everything for me.\n\n{topic}\n\n↓",
        ]

        thread = [random.choice(hooks)]

        # Middle tweets
        middle_tweets = [
            f"1/ First, the problem:\n\nI was spending 3-4 hours/day on content.\nThat's 20+ hours/week.\nJust to stay visible.\n\nIt wasn't sustainable.",

            f"2/ Then I discovered {product['name']}.\n\nSkeptical at first (another tool, really?)\n\nBut I tried the {product['trial'].lower()}.\n\nEverything changed.",

            f"3/ Here's what it actually does:\n\n• {product['benefit']}\n• Learns your voice/style\n• Creates drafts in seconds\n\nYou edit → you post → done.",

            f"4/ My results after 30 days:\n\n→ Content time: 4hrs → 45min/day\n→ Posting: 3x/week → daily\n→ Engagement: Up 40%\n\nSame quality. 10x faster.",

            f"5/ The secret most people miss:\n\nAI isn't a replacement.\nIt's a first draft.\n\nYou still add:\n• Your personality\n• Your examples\n• Your voice\n\nThat's what makes it work.",

            f"6/ Common objection:\n\n\"But AI sounds robotic\"\n\nOnly if you use it raw.\n\nSpend 2 min editing.\nAdd your style.\nNo one can tell.",

            f"7/ Who this is for:\n\n✓ Creators burned out on content\n✓ Business owners with no time\n✓ Anyone posting less than they should\n\nWho it's NOT for:\n✗ People who enjoy writing 4hrs/day",
        ]

        thread.extend(middle_tweets)

        # CTA tweet
        cta = f"8/ If you want to try it:\n\n{product['name']} has a {product['trial'].lower()}.\n\nLink: [your affiliate link]\n\nNo pressure. Just sharing what works for me.\n\nIf this helped, RT the first tweet 🙏"
        thread.append(cta)

        return thread

    # ==================== BLOG POSTS ====================

    def generate_blog_post(self, post_type: str = "review") -> Dict:
        """Generate a complete blog post"""

        product = random.choice(self.niche_products)

        if post_type == "review":
            return self._generate_review_post(product)
        elif post_type == "comparison":
            return self._generate_comparison_post()
        elif post_type == "tutorial":
            return self._generate_tutorial_post(product)
        elif post_type == "listicle":
            return self._generate_listicle_post()
        else:
            return self._generate_review_post(product)

    def _generate_review_post(self, product: Dict) -> Dict:
        """Generate a product review blog post"""

        title = f"{product['name']} Review {self.year}: Is It Worth It? (Honest Take)"

        content = f"""# {title}

*Last updated: {datetime.now().strftime('%B %Y')}*

**Quick verdict:** {product['name']} is one of the best tools for {self.niche}. At {product['price']}, it {product['benefit']}. {product['trial']} available.

**Rating: 4.5/5** ⭐⭐⭐⭐½

[Try {product['name']} Free →](YOUR_AFFILIATE_LINK)

---

## What is {product['name']}?

{product['name']} is an AI-powered tool that {product['benefit']}. It's designed for creators, marketers, and business owners who want to create more content in less time.

In this review, I'll cover:
- Key features
- Pricing
- Pros and cons
- Who it's best for
- My honest experience

Let's dive in.

---

## Key Features

### 1. AI Content Generation
The core feature - type what you need, get content in seconds. Works for:
- Blog posts
- Social media captions
- Email copy
- Ad copy
- And more

### 2. Templates
Pre-built templates for common content types. Just fill in the blanks and generate.

### 3. Tone Adjustment
Make content sound professional, casual, funny, or match your brand voice.

### 4. Multiple Languages
Works in 25+ languages for international businesses.

---

## Pricing

{product['name']} offers several plans:

| Plan | Price | Best For |
|------|-------|----------|
| Free/Trial | {product['trial']} | Testing it out |
| Starter | ~$29/mo | Individual creators |
| Pro | ~$59/mo | Serious marketers |
| Business | ~$99+/mo | Teams |

**My take:** Start with the {product['trial'].lower()} to see if it fits your workflow. The paid plans pay for themselves if you value your time.

---

## Pros and Cons

### ✅ Pros
- Saves hours every week
- Easy to use interface
- Quality output that needs minimal editing
- Good template variety
- Responsive support

### ❌ Cons
- Learning curve for best results
- Monthly cost adds up
- Still needs human editing
- Not perfect for highly technical content

---

## Who Should Use {product['name']}?

**Great for:**
- Content creators posting regularly
- Marketers managing multiple accounts
- Business owners wearing many hats
- Freelancers scaling their output

**Not ideal for:**
- Hobbyists who enjoy writing
- Those with unlimited time
- Very technical/specialized fields

---

## My Experience

I've been using {product['name']} for 3 months now. Here's what happened:

**Before:** 3-4 hours daily on content
**After:** 45 minutes daily

That's 15+ hours per week back in my life.

The content quality? Honestly better than what I was writing myself (with some editing).

The ROI is clear: {product['price']} vs. 15 hours of my time? Easy decision.

---

## Verdict: Is {product['name']} Worth It?

**Yes, if:**
- You create content regularly
- You value your time
- You're willing to spend 5 min learning it

**No, if:**
- You post once a month
- You genuinely enjoy writing everything yourself
- You need 100% original human-written content

For most creators and business owners, {product['name']} pays for itself within the first week.

---

## Get Started

Ready to try it?

👉 **[Get {product['name']} ({product['trial']}) →](YOUR_AFFILIATE_LINK)**

Use my link above and you'll get access to the full {product['trial'].lower()}.

---

## FAQ

**Is AI content considered cheating?**
No. It's a tool, like spell-check or Grammarly. You still add your ideas, voice, and edits.

**Will Google penalize AI content?**
Google cares about quality and helpfulness, not how content was created. Good AI content ranks fine.

**How much time will I actually save?**
Most users report 50-80% time savings on content creation.

---

*Disclosure: This post contains affiliate links. If you purchase through my link, I earn a commission at no extra cost to you. I only recommend tools I actually use.*
"""

        return {
            "type": "review",
            "title": title,
            "product": product["name"],
            "word_count": len(content.split()),
            "content": content,
            "meta_description": f"Honest {product['name']} review for {self.year}. See features, pricing, pros & cons. Is it worth {product['price']}? Find out + get {product['trial'].lower()}.",
            "keywords": [f"{product['name']} review", f"{product['name']} {self.year}", f"is {product['name']} worth it", f"{product['name']} pricing"],
        }

    def _generate_comparison_post(self) -> Dict:
        """Generate a comparison blog post"""

        if len(self.niche_products) < 2:
            return self._generate_review_post(self.niche_products[0])

        products = random.sample(self.niche_products, 2)
        p1, p2 = products[0], products[1]

        title = f"{p1['name']} vs {p2['name']}: Which Is Better in {self.year}?"

        content = f"""# {title}

Trying to choose between {p1['name']} and {p2['name']}? This comparison breaks down everything you need to know.

**Quick answer:** Choose **{p1['name']}** if you want {p1['benefit']}. Choose **{p2['name']}** if you prefer {p2['benefit']}.

---

## Quick Comparison

| Feature | {p1['name']} | {p2['name']} |
|---------|--------------|--------------|
| Price | {p1['price']} | {p2['price']} |
| Best For | {p1['benefit']} | {p2['benefit']} |
| Free Trial | {p1['trial']} | {p2['trial']} |

---

## {p1['name']} Overview

{p1['name']} {p1['benefit']}. It's priced at {p1['price']} and offers a {p1['trial'].lower()}.

**Best for:** Creators who want speed and simplicity.

[Try {p1['name']} Free →](YOUR_AFFILIATE_LINK_1)

---

## {p2['name']} Overview

{p2['name']} {p2['benefit']}. Starting at {p2['price']} with {p2['trial'].lower()}.

**Best for:** Users who want flexibility and value.

[Try {p2['name']} Free →](YOUR_AFFILIATE_LINK_2)

---

## The Verdict

**Choose {p1['name']} if:**
- You want the most popular option
- Speed is your priority
- You don't mind paying a bit more

**Choose {p2['name']} if:**
- Budget is a concern
- You want more customization
- You prefer the underdog

Both are excellent tools. You can't go wrong either way.

My recommendation? Try both free trials and see which clicks for you.

---

*Disclosure: This post contains affiliate links.*
"""

        return {
            "type": "comparison",
            "title": title,
            "products": [p1["name"], p2["name"]],
            "word_count": len(content.split()),
            "content": content,
            "meta_description": f"{p1['name']} vs {p2['name']} comparison for {self.year}. See pricing, features, and which is better for your needs.",
            "keywords": [f"{p1['name']} vs {p2['name']}", f"{p1['name']} alternative", f"{p2['name']} alternative"],
        }

    def _generate_tutorial_post(self, product: Dict) -> Dict:
        """Generate a tutorial blog post"""

        title = f"How to Use {product['name']}: Complete Beginner's Guide ({self.year})"

        content = f"""# {title}

Want to learn how to use {product['name']}? This step-by-step guide will have you creating content in under 10 minutes.

[Get {product['name']} ({product['trial']}) →](YOUR_AFFILIATE_LINK)

---

## What You'll Learn

1. How to set up your account
2. Creating your first content
3. Pro tips for better results
4. Common mistakes to avoid

Let's get started.

---

## Step 1: Create Your Account

1. Go to {product['name']}'s website
2. Click "Start Free Trial" or "Sign Up"
3. Enter your email and create a password
4. Verify your email

Done! You're in.

---

## Step 2: Navigate the Dashboard

When you log in, you'll see:
- **New Document** - Start creating
- **Templates** - Pre-built content types
- **History** - Your past content
- **Settings** - Account options

---

## Step 3: Create Your First Content

1. Click "New Document"
2. Choose a template (try "Blog Post Intro")
3. Enter your topic
4. Click "Generate"
5. Edit the output to match your voice

That's it. You just created content in under 60 seconds.

---

## Pro Tips

- **Be specific in prompts** - "Write about dogs" → "Write 3 tips for training a golden retriever puppy"
- **Use the tone setting** - Match your brand voice
- **Generate multiple options** - Pick the best one
- **Always edit** - AI is the first draft, you're the editor

---

## Common Mistakes

❌ Using AI content without editing
❌ Being too vague in prompts
❌ Expecting perfection on first try
❌ Not experimenting with templates

---

## Next Steps

Now that you know the basics:
1. Try 3 different templates today
2. Create a week's worth of content
3. Develop your prompt style

[Start Your {product['trial']} →](YOUR_AFFILIATE_LINK)

---

*Questions? Drop them in the comments below.*
"""

        return {
            "type": "tutorial",
            "title": title,
            "product": product["name"],
            "word_count": len(content.split()),
            "content": content,
            "meta_description": f"Learn how to use {product['name']} with this beginner's guide. Step-by-step tutorial with pro tips and common mistakes to avoid.",
            "keywords": [f"how to use {product['name']}", f"{product['name']} tutorial", f"{product['name']} guide"],
        }

    def _generate_listicle_post(self) -> Dict:
        """Generate a listicle blog post"""

        title = f"Best {self.niche.title()} in {self.year} (Tested & Ranked)"

        content = f"""# {title}

Looking for the best {self.niche}? I tested the top options and ranked them.

---

## Quick Picks

| Rank | Tool | Best For | Price |
|------|------|----------|-------|
"""

        for i, product in enumerate(self.niche_products, 1):
            content += f"| #{i} | {product['name']} | {product['benefit']} | {product['price']} |\n"

        content += "\n---\n\n"

        for i, product in enumerate(self.niche_products, 1):
            content += f"""## #{i} {product['name']}

**Best for:** {product['benefit']}
**Price:** {product['price']}
**Trial:** {product['trial']}

{product['name']} {product['benefit']}. At {product['price']}, it's a solid choice for most users.

[Try {product['name']} →](YOUR_AFFILIATE_LINK_{i})

---

"""

        content += """## How I Tested

I used each tool for at least 2 weeks, creating real content for my business. I evaluated:
- Ease of use
- Output quality
- Price vs value
- Customer support

---

## Final Thoughts

All of these tools are good. The "best" one depends on your specific needs and budget.

My recommendation: Start with the free trials and see which feels right for you.

---

*Disclosure: This post contains affiliate links.*
"""

        return {
            "type": "listicle",
            "title": title,
            "products": [p["name"] for p in self.niche_products],
            "word_count": len(content.split()),
            "content": content,
            "meta_description": f"Best {self.niche} for {self.year}, tested and ranked. Compare features, pricing, and find the right tool for you.",
            "keywords": [f"best {self.niche}", f"{self.niche} {self.year}", f"top {self.niche}"],
        }

    # ==================== BATCH GENERATION ====================

    def generate_content_batch(self, count: int = 7) -> Dict:
        """Generate a batch of mixed content for a week"""

        batch = {
            "generated_at": datetime.now().isoformat(),
            "niche": self.niche,
            "tiktoks": [],
            "tweets": [],
            "blog_ideas": [],
        }

        # Generate TikTok scripts
        styles = ["hook", "tutorial", "storytime", "comparison", "results", "controversy", "challenge"]
        for i in range(min(count, len(styles))):
            script = self.generate_tiktok_script(styles[i])
            batch["tiktoks"].append(script)

        # Generate Twitter thread
        batch["tweets"].append(self.generate_twitter_thread())

        # Generate blog post ideas
        for post_type in ["review", "comparison", "tutorial", "listicle"]:
            post = self.generate_blog_post(post_type)
            batch["blog_ideas"].append({
                "type": post["type"],
                "title": post["title"],
                "keywords": post.get("keywords", []),
            })

        return batch

    def save_content(self, content: Dict, filename: str = None) -> str:
        """Save generated content to file"""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"content_{timestamp}.json"

        output_dir = Path("content/generated")
        output_dir.mkdir(parents=True, exist_ok=True)

        filepath = output_dir / filename
        with open(filepath, "w") as f:
            json.dump(content, f, indent=2)

        return str(filepath)


def main():
    """Demo the auto content generator"""

    generator = AutoContentGenerator(niche="ai writing tools")

    print("=" * 70)
    print("AUTO CONTENT GENERATOR")
    print("=" * 70)

    # Generate a TikTok script
    print("\n📱 TIKTOK SCRIPT:")
    print("-" * 50)
    script = generator.generate_tiktok_script()
    print(f"Style: {script['style']}")
    print(f"Product: {script['product']}")
    print(f"Duration: {script['duration']}")
    print(f"\n{script['script']}")
    print(f"\nCaption: {script['caption']}")
    print(f"Hashtags: {' '.join(script['hashtags'])}")

    # Generate a week of content
    print("\n" + "=" * 70)
    print("📅 WEEKLY CONTENT BATCH:")
    print("-" * 50)
    batch = generator.generate_content_batch(7)
    print(f"Generated {len(batch['tiktoks'])} TikTok scripts")
    print(f"Generated {len(batch['tweets'])} Twitter threads")
    print(f"Generated {len(batch['blog_ideas'])} blog post ideas")

    # Save to file
    filepath = generator.save_content(batch)
    print(f"\nSaved to: {filepath}")


if __name__ == "__main__":
    main()
